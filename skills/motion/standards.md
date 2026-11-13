# Motion Standards

The bar every animation is measured against. Quote these values in a review; don't approximate them. Two schools of motion design run through this file. The web-craft view is design-engineering practice for web UI. The gesture-first view is Apple's approach to fluid, touch-driven interfaces, carried over to the web. They agree far more often than not; where they don't, the section gives both positions.

## 1. Should it animate at all?

Settle this before you write any code.

| Frequency | Decision |
| --- | --- |
| 100+ times/day (keyboard shortcuts, command palette, core nav) | No animation. Ever. |
| Tens of times/day (hover, list navigation, frequent toggles) | Remove, or near-imperceptible only |
| Occasional (modals, drawers, toasts, settings) | Standard animation |
| Rare / first-time (onboarding, empty states, success, celebration) | The delight budget goes here |

**Never animate actions started from the keyboard.** Users repeat them hundreds of times a day, and motion makes them feel slow and detached. Raycast opens and closes with no animation, and that's the right call.

## 2. What's the purpose?

Name the purpose with one of these, or leave it still:

- **Feedback.** Shows the interface registered the input (hold-to-confirm fill, press scale)
- **Spatial consistency.** Shows where something came from or where it went
- **State indication.** Makes a change readable
- **Preventing a jarring change.** Stops content from teleporting
- **Explanation.** Teaches what a feature does (marketing and onboarding only)
- **Delight.** The rare / first-time tier only

'It looks cool' doesn't qualify.

## 3. Easing

Pick in this order:

- Entering or exiting → `ease-out` (fast start, responsive feel)
- Movement or morphing within the screen → `ease-in-out`
- Hover and colour changes → `ease`
- Continuous motion (marquee, progress) → `linear`
- Anything else → `ease-out`

**`ease-in` never goes on UI, not even on exits.** Its slow start holds back the moment the user watches hardest. At the same 200ms, `ease-out` *feels* faster than `ease-in`.

The easings CSS ships with are too weak. Use strong custom curves:

```css
:root {
  --curve-enter: cubic-bezier(0.23, 1, 0.32, 1);   /* anything arriving or leaving */
  --curve-move:  cubic-bezier(0.77, 0, 0.175, 1);  /* anything crossing the screen */
  --curve-sheet: cubic-bezier(0.32, 0.72, 0, 1);   /* drawers that settle like an iOS sheet */
}
```

Don't hand-roll a curve. Pick one from [easing.dev](https://easing.dev/) or [easings.co](https://easings.co/).

**The gesture-first view disagrees on scope.** For anything the user can touch, it drops easing curves and uses a spring (§5). Curves stay for motion the user watches without touching.

## 4. Duration

| Element | Duration |
| --- | --- |
| Button press feedback | 100-160ms |
| Tooltips, small popovers | 125-200ms |
| Dropdowns, selects | 150-250ms |
| Modals, drawers | 200-500ms |
| Marketing / explanatory | Can be longer |

**Keep UI animations under 300ms. Four exceptions: the 2s hold-to-confirm fill, slow on purpose (§14), toast entrances at 400ms (§6), staggered section entrances at 400ms (§12), and modals and drawers, which go up to 500ms per the table.** A dropdown at 180ms feels more responsive than one at 400ms. A faster spinner makes loading feel faster with the load time unchanged. Show every tooltip after the first instantly, with no delay and no animation, and the whole toolbar feels quicker.

## 5. Springs

A spring has no fixed duration. Its parameters decide when it settles, which is why you can always interrupt it.

**Use for:** drag with momentum, interruptible gestures, decorative mouse-tracking and elements meant to feel alive.

The gesture-first view swaps the physics triplet for two parameters a designer can reason about:

- **Damping ratio.** Sets the overshoot. `1.0` is critically damped, with no bounce. Under `1.0` it overshoots, and the lower it goes the more it bounces.
- **Response.** The speed at which it reaches the target, in seconds. It isn't a duration; the settle time follows from the parameters.

| Interaction | Damping | Response |
| --- | --- | --- |
| Move / reposition | `1.0` | `0.4` |
| Rotation | `0.8` | `0.4` |
| Drawer / sheet | `0.8` | `0.3` |

Start at damping `1.0`. Add bounce (~`0.8`) only when the gesture carried momentum of its own, such as a flick, a throw or a drag release. A menu that faded in shouldn't overshoot. A card the user flicked should.

```js
// settling into place with no gesture behind it: no overshoot
animate(card, { x: 0 }, { type: 'spring', duration: 0.4, bounce: 0 });

// released after a flick: a little overshoot is earned
animate(card, { x: snapX }, { type: 'spring', duration: 0.4, bounce: 0.2 });
```

The web-craft view also finds the Apple-style API easier to reason about, and keeps bounce at `0.1-0.3` whenever it uses bounce. For finer control, use the physics form (`mass`, `stiffness`, `damping`).

For mouse-tracking, run the value through a spring instead of tying it straight to the pointer position. A direct binding has no momentum and feels artificial. Reserve this for decorative motion; a functional graph in a banking app is better with no animation.

## 6. Interruptibility

**The gesture-first view ranks this above every other principle.** Users think and gesture at the same time, so they must be able to catch a moving element mid-flight and send it back without waiting.

- **Never block input during a transition.**
- **Always start from the presentation value, the one on screen, and never from the target.** On an interrupt, read the transform currently on screen and animate from there. Starting from the logical value makes the element jump.
- **When a gesture reverses, blend the velocity instead of cutting it.** Swapping one animation for another at the turn breaks the velocity, and the element feels like it hit a wall.
- **Split 2D motion into separate X and Y springs.** A single spring on the 2D distance falls out of sync when the axes move at different speeds.

In CSS, transitions retarget mid-flight and keyframes start again from zero.

| | CSS transitions | Keyframes |
| --- | --- | --- |
| Behaviour | Interpolate toward latest state | Fixed timeline |
| Interruptible | Yes, retargets | No, restarts |
| Use for | Interactive state changes | One-shot sequences |
| Duration | Adapts to remaining distance | Fixed |

Use transitions for anything that fires in quick succession, such as toasts and toggles.

```css
.notice {
  transform: translateY(0);
  opacity: 1;
  transition: transform 400ms ease, opacity 400ms ease;

  @starting-style {
    transform: translateY(100%);
    opacity: 0;
  }
}
```

`@starting-style` covers entry without JS. For older browsers, set a `data-mounted` attribute after the first render.

## 7. Velocity handoff

When the gesture ends, the animation carries on at the finger's exact velocity, so dragging and animating join without a seam. Of all the details here, this one does most to turn 'fine' into 'fluid'.

Feed the release velocity into the spring as its starting velocity. When the API expects relative velocity, divide by the distance left:

```
springVelocity = fingerVelocity / (destination − position)
```

Example: the element sits at `y=50`, the target is `y=150` and the finger moves at 50px/s, so the initial velocity is `0.5`. Motion and Framer Motion accept absolute px/s as is, through `velocity`.

## 8. Momentum projection

Don't snap to whichever boundary sits nearest the release point. Work out where the gesture is *heading*, then snap to whichever target lies closest to that projected point. Projection makes a flick behave like a throw.

```js
// rate 0.998 feels like ordinary scrolling; 0.99 comes to rest sooner
const projectDistance = (velocity, rate = 0.998) =>
  (velocity / 1000) * rate / (1 - rate);

const landing = offset + projectDistance(releaseVelocity);
springTo(closestSnap(landing), { velocity: releaseVelocity });
```

Apple doesn't ship the textbook `v²/(2·decel)`. Use the exponential-decay form, as Vaul and Embla do.

The web-craft view reaches the same result by a shorter route. Never make dismissal depend on crossing a distance threshold. Compute `Math.abs(distance) / elapsedMs` and dismiss above ~`0.11`, so a flick is enough on its own.

## 9. Boundaries: rubber-band, never hard-stop

Raise the resistance the further the user drags past an edge. A hard stop looks frozen. Rising resistance shows the interface is responding and there's nothing more to see. Both views agree.

```js
// how far the finger went past the edge in, how far the element moves out
function resist(past, size, c = 0.55) {
  return (past * size * c) / (size + c * Math.abs(past));
}
```

Let the user drag past the edge against growing friction instead of meeting an invisible wall.

## 10. Spatial consistency

- **Leave the way you came.** A panel that enters from the right side leaves to the right. Arriving from the right and leaving through the bottom breaks the link between the two.
- **Anchor to the source.** A menu, popover or sheet grows out of the element that opened it. Set `transform-origin` to the trigger.
- **On reversible transitions, mirror the easing**, with the cubic-bézier control points inverted.
- **Lean toward the destination.** The in-between frames should show where the motion ends up, rather than interpolate toward it blindly. Control Center modules grow up and outward, toward the finger.

## 11. Physicality

- **Never `scale(0)`.** Start at `scale(0.9-0.97)` with `opacity: 0`. Real objects don't materialise out of nothing.
- **Origin-aware popovers.** Base UI exposes this as `transform-origin: var(--transform-origin)`. Modals are the exception and open in the centre, where they stay.
- **Press feedback.** `transform: scale(0.96-0.97)` on `:active`, with `transition: transform 150-160ms ease-out`. Stay inside `0.95-0.98`; below `0.95` looks exaggerated. Some buttons shouldn't have it, so offer a `static` prop that switches it off where the motion would get in the way.

```css
.pressable {
  transition: transform 150ms ease-out;
}

.pressable:active {
  transform: scale(0.96);
}
```

## 12. Enter animations: split and stagger

Break the entrance into semantic chunks and animate each one, instead of moving one large container as a block.

1. Divide the content into logical groups (title, description, buttons)
2. Space the groups ~100ms apart
3. Consider a per-word split for titles, at ~80ms
4. Combine `opacity`, `blur` and `translateY`

```css
@keyframes rise-in {
  to { filter: blur(0); transform: translateY(0); opacity: 1; }
}

.hero > * {
  filter: blur(4px);
  transform: translateY(10px);
  opacity: 0;
  animation: rise-in 400ms ease-out forwards;
}

.hero > :nth-child(2) { animation-delay: 100ms; }
.hero > :nth-child(3) { animation-delay: 200ms; }
```

Between list items, as opposed to page sections, tighten the stagger to 30-80ms. Anything longer drags. Stagger only decorates, so it must never block interaction.

## 13. Exit animations

Make exits softer and shorter than entrances. The user's attention has already moved on; don't compete for it.

- A small fixed `translateY` (around `-12px`), never the full height of the container
- Keep some movement in one direction, so the element seems to go somewhere
- Exit faster than enter: 150ms against 300ms
- Always keep an exit; a vanish through `display: none` loses context

```css
.row[data-leaving] {
  transform: translateY(-12px);
  opacity: 0;
  transition: transform 150ms ease-out, opacity 150ms ease-out;
}
```

## 14. Asymmetric timing

Go slow where the user decides and fast where the system answers.

```css
/* letting go: the fill snaps back quickly */
.hold-fill {
  transition: clip-path 200ms ease-out;
}

/* holding down: the fill takes its time */
.hold-button:active .hold-fill {
  transition: clip-path 2s linear;
}
```

## 15. Contextual icon animations

When an icon changes on hover or with state, animate the swap instead of toggling visibility. Use these values and no others:

- `scale`: `0.25` → `1` (not `0.5`, not `0.6`)
- `opacity`: `0` → `1`
- `filter`: `blur(4px)` → `blur(0px)`
- `transition`: `{ type: 'spring', duration: 0.3, bounce: 0 }`, bounce always `0`

If the project has no motion library, crossfade the icons in CSS with both left in the DOM. Position one absolutely on top of the other; the one that isn't absolute sets the layout size. Neither unmounts, so the swap animates in both directions.

```html
<button type="button" class="relative" aria-label="Copied">
  <!-- visible: absolutely positioned on top -->
  <svg class="absolute inset-0 m-auto size-4 opacity-100 blur-0 scale-100
              transition-[opacity,filter,scale] duration-300"><!-- check --></svg>
  <!-- hidden: stays in the flow and gives the button its size -->
  <svg class="size-4 opacity-0 blur-[4px] scale-[0.25]
              transition-[opacity,filter,scale] duration-300"><!-- copy --></svg>
</button>
```

Look in `package.json` for `motion` or `framer-motion` before you pick a library. Never add a dependency for icon transitions.

Animate: loading and success indicators, toolbar icons that depend on context, icons revealed on hover, and icons that show state (play → pause). Leave still: text labels, static nav icons, decorative icons and icons that are always visible.

## 16. Skip animation on first paint

An element that loads in its default state shouldn't animate in; animate its later changes. `initial={false}` on `AnimatePresence` covers this for toggles, tabs, segmented controls and icon swaps.

It goes wrong when the component depends on `initial` for a real first entrance, such as a staggered hero. Check with a full refresh before you apply it.

## 17. Transforms and clip-path

- **`translate` percentages** are measured against the element's own size, so `translateY(100%)` moves it by its own height whatever its dimensions. Sonner and Vaul place toasts and drawers this way. Prefer it to hardcoded pixels.
- **`scale()` scales the children too**, font size and icons included. For press feedback, that's what you want.
- **3D**: `rotateX/Y` with `transform-style: preserve-3d` gives depth, orbit and flip without JS.
- **`clip-path: inset(t r b l)`** ranks among the strongest animation tools in CSS. Each value cuts in from its own side. Use it to reveal on scroll (`inset(0 0 100% 0)` → `inset(0 0 0 0)`), for hold-to-delete overlays, for seamless tab colour changes (duplicate the list and clip the active copy) and for comparison sliders without adding DOM nodes.

## 18. Gestures and drag

- **1:1 tracking.** The element sticks to the finger and keeps the offset from where the user grabbed it. Snapping its centre to the finger on grab ruins the illusion at once.
- **Pointer capture** from the moment dragging starts, so tracking carries on outside the element.
- **Keep a short history of positions and timestamps**, not only the current point. Release needs the velocity.
- **Movement threshold**: wait for ~10px of travel before committing to a direction.
- **Run every plausible gesture recogniser side by side** from the first movement, and cancel the losers once the intent is clear. Skip recognisers that report only a final state; they discard the continuous tracking that feedback depends on.
- **Multi-touch protection**: ignore extra touch points once the drag starts, or a change of finger mid-drag makes the element jump.
- **Tap**: pointer-*down* highlights, pointer-*up* commits. Pad the hit area by ~10px, and let the user cancel by dragging off the target and back.

## 19. Response and feedback

**React on pointer-down rather than on release.** As soon as lag shows, the feeling of direct control collapses. Check the input path for debounces, artificial timers and waits on transitions.

Keep feedback continuous *during* the interaction, not only at its end. Update a drag, slider or drawer 1:1 from start to finish.

## 20. Performance

- **Animate `transform` and `opacity` by default.** They bypass layout and paint and go straight to the GPU. Animating `width`, `height`, `padding`, `margin`, `top` or `left` triggers all three. This file breaks that default on purpose in four places: height plus opacity on accordions and on lists whose items come and go (§23); `clip-path` on reveals and on hold overlays (§14, §17); a small `filter: blur` (under 20px) when entering, swapping icons or crossfading (§12, §15, §21); and colour changes on hover and on theme switches (§3, §22).
- **Never `transition: all`.** Name each property.
- **Use `will-change` sparingly.** It hints and fixes nothing, and too much of it costs memory. Add it where motion is about to start and remove it afterwards.
- **Don't drive child transforms from a CSS variable on the parent.** Every child gets its styles recalculated. Set `transform` on the element itself.
  ```js
  // slow: every descendant resolves the variable again
  sheet.style.setProperty('--drag-y', `${dragY}px`);

  // fast: only the sheet changes
  sheet.style.transform = `translateY(${dragY}px)`;
  ```
- **Framer Motion's shorthands aren't hardware-accelerated.** `x`, `y` and `scale` animate on the main thread through rAF and drop frames under load. Write the full transform string: `animate={{ transform: 'translateX(100px)' }}`.
- **Under load, CSS animations beat JS.** They don't depend on the main thread. Use CSS for motion you can define up front and JS for dynamic, interruptible motion.
- **WAAPI** pairs JS control with CSS performance. It's hardware-accelerated, interruptible and needs no library.
- **Keep the change in position per frame under the threshold of perception**, so motion doesn't strobe. When something moves extremely fast, a subtle motion blur or stretch looks better than a hard-edged streak.

## 21. Masking imperfect crossfades

If a crossfade still shows two overlapping states after you've tuned easing and duration, add `filter: blur(2px)` for the length of the transition. Without it the eye sees two separate objects; with it, one object changing. Blur is expensive in Safari, so keep it under 20px.

## 22. Reduced motion and accessibility

When the user asks for reduced motion, make motion gentler; some of it stays. Keep the transitions that help the user understand a change; remove movement and changes of position.

Three separate signals, and each deserves respect:

```css
@media (prefers-reduced-motion: reduce) {
  .drawer {
    transform: none !important;
    transition: opacity 200ms ease;
  }
}

@media (prefers-reduced-transparency: reduce) {
  .nav-bar {
    backdrop-filter: none;
    background: var(--surface-opaque);
  }
}

@media (prefers-contrast: more) {
  .panel {
    border: 1px solid var(--outline-strong);
    background: var(--surface-solid);
  }
}
```

Put hover motion behind `@media (hover: hover) and (pointer: fine)`, since touch devices fire hover on tap.

Avoid sudden jumps in brightness, slow oscillations that loop at around 0.2 Hz and moving backgrounds that fill the viewport. Ease theme changes. Make large objects semi-transparent while they move.

## 23. Cohesion

Fit the motion to the component's character. A playful component can bounce more; a professional dashboard stays crisp and quick. Part of why Sonner feels right is that its name, design, easing and duration all fit together: a little slower than usual, with `ease` in place of `ease-out`, so it reads as elegant.

Opacity and height on lists that gain and lose items come down to trial and error, with no formula. Keep tuning until the feel is right.

## 24. Debugging

- **Slow motion.** Stretch the duration 2-5×, or open the animation inspector in DevTools. Confirm that colours crossfade cleanly, the easing doesn't end abruptly, `transform-origin` sits in the right place and properties that move together stay in sync.
- **Frame by frame.** The Animations panel in Chrome DevTools shows where properties drift apart in timing.
- **Real devices** for gestures. Plug in a phone, open the dev server by IP and use Safari's remote devtools. Fall back to the simulator only when there's no device; it doesn't replace one.
- **Fresh eyes the next day.** Flaws you couldn't see while building show up later.

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
| Exit | Shorter and softer than enter | `translateY(-12px)`, `150ms ease-out` |
| Group entrance | Stagger | 100ms sections, 30-80ms list items |
| Icon swap | Fixed values, no bounce | `scale 0.25→1`, `blur 4px→0`, `spring 0.3 bounce 0` |
| Boundary | Rubber-band | progressive resistance |
| Reduced motion | Cross-fade, not slide | `@media (prefers-reduced-motion)` |
