# Motion Standards

The bar animations get measured against. Cite these values in reviews instead of approximating.

Two sources, marked inline where they differ. **(EK)** is Emil Kowalski's design engineering philosophy, focused on web UI craft. **(Apple)** is Apple's WWDC design talks, chiefly *Designing Fluid Interfaces* (2018), translated to the web. They agree on more than they disagree. Where they conflict, both positions are stated.

## 1. Should it animate at all?

Answer this before writing a single line. **(EK)**

| Frequency | Decision |
| --- | --- |
| 100+ times/day (keyboard shortcuts, command palette, core nav) | No animation. Ever. |
| Tens of times/day (hover, list navigation, frequent toggles) | Remove, or near-imperceptible only |
| Occasional (modals, drawers, toasts, settings) | Standard animation |
| Rare / first-time (onboarding, empty states, success, celebration) | The delight budget lives here |

**Never animate keyboard-initiated actions.** They repeat hundreds of times a day, and animation makes them feel slow and disconnected. Raycast has no open/close animation. That's correct.

## 2. What's the purpose?

Name it in one of these words or don't animate:

- **Feedback.** The interface heard the user (press scale, hold-to-confirm fill)
- **Spatial consistency.** Where something came from or went
- **State indication.** Making a change legible
- **Preventing a jarring change.** Content that would teleport
- **Explanation.** Showing how a feature works (marketing and onboarding only)
- **Delight.** Only at the rare / first-time tier

'It looks cool' is not on the list.

## 3. Easing

Decision order **(EK)**:

- Entering or exiting → `ease-out` (starts fast, feels responsive)
- Moving or morphing on screen → `ease-in-out`
- Hover or colour change → `ease`
- Constant motion (marquee, progress) → `linear`
- Default → `ease-out`

**Never `ease-in` on UI.** It starts slow, delaying the exact moment the user is watching most closely. `ease-out` at 200ms *feels* faster than `ease-in` at 200ms.

Built-in CSS easings are too weak. Use strong custom curves:

```css
--ease-out:     cubic-bezier(0.23, 1, 0.32, 1);      /* UI enter/exit */
--ease-in-out:  cubic-bezier(0.77, 0, 0.175, 1);     /* on-screen movement */
--ease-drawer:  cubic-bezier(0.32, 0.72, 0, 1);      /* iOS-like drawer, from Ionic */
```

Find curves at [easing.dev](https://easing.dev/) or [easings.co](https://easings.co/). Don't hand-roll from scratch.

**(Apple) disagrees on scope.** For anything a user can touch, skip easing curves entirely and use a spring (§5). Curves are for motion the user only watches.

## 4. Duration

| Element | Duration |
| --- | --- |
| Button press feedback | 100-160ms |
| Tooltips, small popovers | 125-200ms |
| Dropdowns, selects | 150-250ms |
| Modals, drawers | 200-500ms |
| Marketing / explanatory | Can be longer |

**UI animations stay under 300ms. (EK)** A 180ms dropdown feels more responsive than a 400ms one. Faster spinners make loading feel faster at identical actual load time. Instant tooltips after the first one (skip delay, skip animation) make a whole toolbar feel faster.

## 5. Springs

Springs have no fixed duration. They settle based on parameters, which is why they're interruptible by nature.

**Use for:** drag with momentum, elements that should feel alive, interruptible gestures, decorative mouse-tracking.

**(Apple)** replaced the physics triplet with two designer-facing parameters:

- **Damping ratio.** Controls overshoot. `1.0` is critically damped, no bounce. Below `1.0` overshoots. Lower is bouncier.
- **Response.** How fast it reaches the target, in seconds. Not duration; settle time emerges from the parameters.

| Interaction | Damping | Response |
| --- | --- | --- |
| Move / reposition | `1.0` | `0.4` |
| Rotation | `0.8` | `0.4` |
| Drawer / sheet | `0.8` | `0.3` |

Default to damping `1.0`. Add bounce (~`0.8`) **only when the gesture itself carried momentum**: a flick, a throw, a drag release. Overshoot on a menu that faded in is wrong. Overshoot on a card you flicked is right.

```js
animate(el, { y: 0 },      { type: 'spring', bounce: 0,   duration: 0.4 }); // default
animate(el, { y: target }, { type: 'spring', bounce: 0.2, duration: 0.4 }); // after a flick
```

**(EK)** agrees on the Apple-style API being easier to reason about, and puts bounce at `0.1-0.3` when used at all. Traditional physics form (`mass`, `stiffness`, `damping`) when you need finer control.

For mouse-tracking, interpolate through a spring rather than binding the value directly to pointer position. Direct binding feels artificial because it has no momentum. Only do this when the motion is decorative: on a functional graph in a banking app, no animation is better.

## 6. Interruptibility

**(Apple) calls this the single most important principle.** The thought and the gesture happen in parallel, so a user must be able to grab a moving element mid-flight and reverse it without waiting.

- **Never lock out input during a transition.**
- **Always animate from the presentation value, never the target value.** On interrupt, read the live on-screen transform and start from there. Starting from the logical value causes a visible jump.
- **When a gesture reverses, blend velocity, don't hard-cut it.** Replacing one animation with another at a reversal creates a velocity discontinuity that reads as a brick wall.
- **Decompose 2D motion into independent X and Y springs.** One spring on a 2D distance desyncs when the axes have different velocities.

In CSS terms **(EK)**: transitions retarget mid-flight, keyframes restart from zero.

| | CSS transitions | Keyframes |
| --- | --- | --- |
| Behaviour | Interpolate toward latest state | Fixed timeline |
| Interruptible | Yes, retargets | No, restarts |
| Use for | Interactive state changes | One-shot sequences |
| Duration | Adapts to remaining distance | Fixed |

Anything triggered rapidly (toasts, toggles) uses transitions.

```css
.toast {
  opacity: 1; transform: translateY(0);
  transition: opacity 400ms ease, transform 400ms ease;
  @starting-style { opacity: 0; transform: translateY(100%); }
}
```

`@starting-style` handles entry without JS. Legacy fallback is a `data-mounted` attribute set after first render.

## 7. Velocity handoff

When a gesture ends, the animation continues at the finger's exact velocity, so there's no seam between dragging and animating. **(Apple).** This is the detail that most separates 'fluid' from 'fine'.

Pass release velocity as the spring's initial velocity. If the API wants relative velocity, normalize by remaining distance:

```
relativeVelocity = gestureVelocity / (targetValue − currentValue)
```

Element at `y=50`, target `y=150`, finger at 50px/s → initial velocity `0.5`. Motion and Framer Motion take absolute px/s directly via `velocity`.

## 8. Momentum projection

Don't snap to the nearest boundary from the release point. Project where the gesture is *going*, then snap to the target nearest that projection. **(Apple).** This is what makes a flick feel like a throw.

```js
// decelerationRate ≈ 0.998 for normal scroll feel, 0.99 for snappier
function project(initialVelocity, decelerationRate = 0.998) {
  return (initialVelocity / 1000) * decelerationRate / (1 - decelerationRate);
}

const projected = currentPosition + project(releaseVelocity);
animateSpringTo(nearestSnapPoint(projected), { velocity: releaseVelocity });
```

The textbook `v²/(2·decel)` is not what Apple ships. Use the exponential-decay form. Vaul and Embla both do.

**(EK)** reaches the same place from a simpler angle: don't require crossing a distance threshold to dismiss. Compute `Math.abs(distance) / elapsedMs` and dismiss above ~`0.11`. A flick should be enough.

## 9. Boundaries: rubber-band, don't hard-stop

Resist progressively at an edge. A hard stop reads as frozen. Continuous resistance reads as responsive with nothing more to see. Both sources agree.

```js
function rubberband(overshoot, dimension, constant = 0.55) {
  return (overshoot * dimension * constant) / (dimension + constant * Math.abs(overshoot));
}
```

Allow over-drag with rising friction rather than an invisible wall.

## 10. Spatial consistency

- **Enter and exit along the same path. (Apple)** A panel that slides in from the right dismisses to the right. In-from-right, out-the-bottom reads as disconnected.
- **Anchor to the source.** Menus, popovers and sheets originate from the element that triggered them. Set `transform-origin` to the trigger.
- **Mirror the easing on reversible transitions** Using inverse cubic-bézier control points.
- **Hint in the direction of travel.** Intermediate frames should telegraph the outcome, not blindly interpolate toward it. Control Center modules grow up and out toward your finger.

## 11. Physicality

- **Never `scale(0)`. (EK)** Start from `scale(0.9-0.97)` plus `opacity: 0`. Nothing in the real world appears from nothing.
- **Origin-aware popovers.** `transform-origin: var(--transform-origin)` in Base UI. **Modals are exempt**, they appear centred and stay centred.
- **Press feedback.** `transform: scale(0.96-0.97)` on `:active`, `transition: transform 150-160ms ease-out`. Keep it in `0.95-0.98`; below `0.95` reads as exaggerated. Not every button needs it, so expose a `static` prop that disables it where the motion would distract.

```css
.button { transition: transform 150ms ease-out; }
.button:active { transform: scale(0.96); }
```

## 12. Enter animations: split and stagger

Don't animate one large container. Break content into semantic chunks and animate each. **(EK)**

1. Split into logical groups (title, description, buttons)
2. Stagger ~100ms between groups
3. For titles, consider per-word splitting at ~80ms
4. Combine `opacity`, `blur` and `translateY`

```css
.stagger-item {
  opacity: 0; transform: translateY(12px); filter: blur(4px);
  animation: fadeInUp 400ms ease-out forwards;
}
.stagger-item:nth-child(2) { animation-delay: 100ms; }
.stagger-item:nth-child(3) { animation-delay: 200ms; }

@keyframes fadeInUp { to { opacity: 1; transform: translateY(0); filter: blur(0); } }
```

For list items rather than page sections, tighten to 30-80ms between items. Longer feels slow. Stagger is decorative and must never block interaction.

## 13. Exit animations

Softer and shorter than enters. The user's attention is already moving on, so don't fight for it.

- Small fixed `translateY` (around `-12px`), not the full container height
- Keep some directional movement so the element reads as having gone somewhere
- Exit shorter than enter: 150ms against 300ms
- Never remove the exit entirely; a `display: none` vanish loses context

```css
.item-exit {
  opacity: 0;
  transform: translateY(-12px);
  transition: opacity 150ms ease-in, transform 150ms ease-in;
}
```

## 14. Asymmetric timing

Slow where the user is deciding, fast where the system responds.

```css
.overlay              { transition: clip-path 200ms ease-out; }  /* release: fast */
.button:active .overlay { transition: clip-path 2s linear; }     /* press: deliberate */
```

## 15. Contextual icon animations

When icons swap on state change or hover, animate rather than toggling visibility. Use exactly these values, don't deviate:

- `scale`: `0.25` → `1` (not `0.5`, not `0.6`)
- `opacity`: `0` → `1`
- `filter`: `blur(4px)` → `blur(0px)`
- `transition`: `{ type: 'spring', duration: 0.3, bounce: 0 }`, bounce always `0`

Without a motion library, keep both icons in the DOM and cross-fade with CSS. One is absolutely positioned over the other; the non-absolute one defines layout size. Neither unmounts, so both directions animate.

```html
<div class="relative">
  <div class="absolute inset-0 flex items-center justify-center
              transition-[opacity,filter,scale] duration-300
              scale-100 opacity-100 blur-0"><!-- active icon --></div>
  <div class="transition-[opacity,filter,scale] duration-300
              scale-[0.25] opacity-0 blur-[4px]"><!-- inactive icon --></div>
</div>
```

Check `package.json` for `motion` or `framer-motion` before reaching for a library. Don't add a dependency for icon transitions.

Animate: icons appearing on hover, state-change icons (play → pause), contextual toolbar icons, loading and success indicators. Don't animate: static nav icons, decorative icons, always-visible icons, text labels.

## 16. Skip animation on first paint

Elements already in their default state shouldn't animate in on page load, only on subsequent changes. `initial={false}` on `AnimatePresence` handles this for icon swaps, toggles, tabs and segmented controls.

It breaks when the component relies on `initial` for a genuine first-time entrance, like a staggered hero. Verify on a full refresh before applying.

## 17. Transforms and clip-path

- **`translate` percentages** Are relative to the element's own size. `translateY(100%)` moves by its own height regardless of dimensions. This is how Sonner and Vaul position toasts and drawers. Prefer over hardcoded pixels.
- **`scale()` scales children too**, including font size and icons. A feature for press feedback, not a bug.
- **3D**: `rotateX/Y` plus `transform-style: preserve-3d` for depth, orbit and flip without JS.
- **`clip-path: inset(t r b l)`** Is one of the most powerful animation tools in CSS. Each value eats in from that side. Uses: reveal on scroll (`inset(0 0 100% 0)` → `inset(0 0 0 0)`), hold-to-delete overlays, seamless tab colour transitions (duplicate the list, clip the active copy), comparison sliders with no extra DOM.

## 18. Gestures and drag

- **1:1 tracking. (Apple)** The element stays glued to the finger and respects the offset from where it was grabbed. Snapping to centre on grab breaks the illusion instantly.
- **Pointer capture** Once dragging starts, so tracking continues outside the element's bounds.
- **Track a short position and timestamp history**, not just the current point. You need velocity at release.
- **Movement threshold** Of ~10px before committing to a direction.
- **Detect plausible gestures in parallel** From the first move, then cancel the losers once intent is clear. Avoid recognizers that only report a final state; they throw away the continuous tracking you need for feedback.
- **Multi-touch protection**: ignore extra touch points after the drag begins, or switching fingers mid-drag jumps the element.
- **Tap**: highlight on pointer-*down*, commit on pointer-*up*. Add ~10px of hit padding, and allow cancel by dragging away and back.

## 19. Response and feedback

**Respond on pointer-down, not on release. (Apple)** The moment lag appears, directness falls off a cliff. Audit debounces, artificial timers and transition waits on the input path.

Feedback must be continuous *during* the interaction, not only at the end. For a drag, slider or drawer, update 1:1 the whole way through.

## 20. Performance

- **Only animate `transform` and `opacity`.** They skip layout and paint and run on the GPU. `padding`, `margin`, `height`, `width`, `top`, `left` trigger all three.
- **Never `transition: all`.** Name the properties.
- **`will-change` sparingly.** It's a hint, not a fix, and overuse costs memory. Add it where motion is imminent, remove it after.
- **Don't drive child transforms through a CSS variable on the parent.** It recalculates styles for every child. Set `transform` directly on the element.
  ```js
  element.style.setProperty('--swipe-amount', `${d}px`); // recalcs all children
  element.style.transform = `translateY(${d}px)`;        // only this element
  ```
- **Framer Motion shorthands are not hardware-accelerated.** `x`, `y` and `scale` run on the main thread via rAF and drop frames under load. Use the full transform string: `animate={{ transform: 'translateX(100px)' }}`.
- **CSS animations beat JS under load.** They run off the main thread. Use CSS for predetermined motion, JS for dynamic and interruptible.
- **WAAPI** Gives JS control at CSS performance, hardware-accelerated and interruptible with no library.
- **Keep per-frame positional change below the perception threshold** To avoid strobing. **(Apple)** For very fast motion, subtle motion blur or stretch reads better than a hard streak.

## 21. Masking imperfect crossfades

When a crossfade shows two overlapping states despite tuning easing and duration, add `filter: blur(2px)` during the transition. Without it you see two distinct objects; blur blends them into one perceived transformation. Keep blur under 20px, it's expensive in Safari.

## 22. Reduced motion and accessibility

Reduced motion means gentler, not zero. Keep transitions that aid comprehension, remove movement and position changes.

Three independent signals, all worth honouring **(Apple)**:

```css
@media (prefers-reduced-motion: reduce) {
  .sheet { transition: opacity 200ms ease; transform: none !important; }
}
@media (prefers-reduced-transparency: reduce) {
  .toolbar { background: white; backdrop-filter: none; }
}
@media (prefers-contrast: more) {
  .card { background: var(--solid); border: 1px solid var(--edge); }
}
```

Gate hover motion behind `@media (hover: hover) and (pointer: fine)`. Touch devices fire hover on tap.

Also avoid: full-viewport moving backgrounds, slow looping oscillations near 0.2 Hz, and abrupt brightness jumps. Ease theme changes. Make large moving objects semi-transparent while they travel.

## 23. Cohesion

Match motion to the component's personality. A playful component can be bouncier; a professional dashboard should be crisp and fast. **(EK)** Sonner feels right partly because its easing, duration, design and even its name are in harmony: slightly slower than typical, and `ease` rather than `ease-out`, to read as elegant.

Opacity plus height on entering and exiting lists is trial and error. There's no formula. Adjust until it feels right.

## 24. Debugging

- **Slow motion.** Bump duration 2-5×, or use the DevTools animation inspector. Check that colours crossfade cleanly, easing doesn't stop abruptly, `transform-origin` is right, and coordinated properties stay in sync.
- **Frame by frame.** Chrome DevTools Animations panel reveals timing drift between properties.
- **Real devices** For gestures. Connect a phone, hit the dev server by IP, use Safari remote devtools. The simulator is a fallback, not a substitute.
- **Fresh eyes the next day.** Imperfections invisible during development surface later.

## Quick reference

| Need | Technique | Value |
| --- | --- | --- |
| Default UI spring | Critically damped | `damping 1.0`, `response 0.3-0.4` |
| Momentum spring | Slight bounce | `damping ~0.8`, `bounce 0.1-0.3` |
| Gesture → spring | Hand off release velocity | `v / (target − current)` if normalized |
| Flick landing | Project momentum | `current + (v/1000)·d/(1−d)`, `d ≈ 0.998` |
| Clean interrupt | Start from live value | read the on-screen transform |
| Press feedback | Scale down on `:active` | `scale(0.96)`, `150ms ease-out` |
| Entry | Scale + opacity, never from 0 | `scale(0.95)`, `opacity 0` |
| Exit | Shorter and softer than enter | `translateY(-12px)`, `150ms ease-in` |
| Group entrance | Stagger | 100ms sections, 30-80ms list items |
| Icon swap | Fixed values, no bounce | `scale 0.25→1`, `blur 4px→0`, `spring 0.3 bounce 0` |
| Boundary | Rubber-band | progressive resistance |
| Reduced motion | Cross-fade, not slide | `@media (prefers-reduced-motion)` |
