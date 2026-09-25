# Feel

Why interfaces feel right, and the details that get them there. Everything here is judgment, not spec. Argue with it.

Two sources, marked inline. **(EK)** is Emil Kowalski's design engineering philosophy. **(Apple)** is Apple's design talks, chiefly *Principles of Great Design* (WWDC 2026) and *Designing Fluid Interfaces* (2018).

For anything that moves, see the `motion` skill.

## The premise

**Taste is trained, not innate. (EK)** It isn't personal preference; it's the learned ability to see past the obvious and recognise what lifts something. You build it by surrounding yourself with great work, thinking about *why* it feels good, and reverse-engineering interactions you admire.

**Unseen details compound.** Most details users never consciously notice. That's the point. When something works exactly as assumed, they move on without a second thought.

Paul Graham put it this way:

> "All those unseen details combine to produce something that's just stunning, like a thousand barely audible voices all singing in tune."

**Beauty is leverage.** People pick tools on the whole experience, not the feature list. Good defaults and good motion are real differentiators, and beauty is underused in software.

## The eight principles (Apple)

Names to reason with when a decision is contested.

1. **Purpose.** Make with intention; decide what *not* to build. Every feature spends the user's time, attention and trust.
2. **Agency.** Keep people in control. Offer choices, back them with forgiveness. Easy undo for slips; a confirmation dialog only for genuinely destructive, irreversible actions. Overusing confirmation trains people to click through it.
3. **Responsibility.** Act in the user's interest. Ask for permissions at the right moment, only for what's needed. Anticipate misuse, especially with AI. Cut a feature whose risk outweighs its value.
4. **Familiarity.** Build on what people know. Metaphors neither too literal nor too abstract, and honour their physics. Things that look the same behave the same and live in the same place. Break a familiar pattern only if you can prove it's better, then test it.
5. **Flexibility.** Design for different contexts, devices and abilities. When no single layout fits everyone, let people personalise.
6. **Simplicity, not minimalism.** Strip the unnecessary so the core purpose shows. Burying everything in one place looks minimal but isn't simple. Sometimes *adding* context simplifies. Common path first, advanced one level deeper.
7. **Craft.** Every spacing, timing and alignment value is a deliberate choice you can defend. Jittery scroll, misaligned icons and layouts that break on rotation read as carelessness.
8. **Delight.** The result of getting the other seven right, not confetti on top. Decide the emotion you want and reinforce it everywhere.

## Feedback and wayfinding (Apple)

- **Four kinds of feedback:** status, completion, warning, error. Confirm meaningful actions, expose ongoing status, warn before problems, validate inline rather than on submit.
- **Wayfinding.** Every screen answers: where am I, where can I go, what's there, how do I get out. Never trap the user.
- **Grouping and mapping.** Proximity implies relationship. Put a control near what it affects, and arrange controls to mirror what they change. If you need a label to explain a control, the mapping is weak.
- **Direct, specific labels beat safe generic ones.** Name nav items for their contents ('Progress', 'Library'), not vague umbrellas ('Home'). Specificity creates predictability.

## Materials and depth (Apple)

Translucency is a floating functional layer that brings structure without stealing focus. On the web, approximate with `backdrop-filter`.

- **Build nav, toolbars and sheets as translucent layers** with content scrolling underneath, not opaque bars consuming a fixed strip.
- **Material weight encodes hierarchy.** Darker, heavier materials separate structural regions like sidebars; lighter ones draw attention to interactive elements. **Never stack a light translucent surface on another**, legibility collapses.
- **Bigger surfaces read as thicker:** stronger blur, deeper shadow than small chips. Consider context-aware shadow, heavier over busy content.
- **Dim to focus, separate to keep flow.** A modal task pairs the surface with a dimming scrim and pushes the background back. A parallel, non-blocking panel uses translucency and offset *without* a scrim. For stacked sheets, progressively dim each parent layer.
- **Vibrancy keeps text legible** over changing backgrounds. Don't use flat gray text on translucent surfaces; raise contrast, add a little weight, bump letter-spacing slightly. Put colour on a solid layer, not the translucent foreground.
- **Scroll edge effects, not hard dividers.** Instead of a 1px border under a sticky header, fade a small blur or gradient mask where content meets floating chrome, and only where they actually overlap.
- **Materialize, don't just fade.** For glass surfaces, animate blur radius and scale together on enter and exit so it reads as a real material arriving.

```css
.toolbar {
  background: rgba(255, 255, 255, 0.6);
  backdrop-filter: blur(20px) saturate(180%);
  border-top: 1px solid rgba(255, 255, 255, 0.4); /* bright edge = light catching the material */
}
```

## Multimodal feedback (Apple)

Three rules for combining motion, sound and haptics:

1. **Causality.** It must be obvious what caused the feedback. Trigger on the actual causal event and match its character to the action's physicality.
2. **Harmony.** Visual, sound and haptic fire on the **same frame**. Latency between them destroys the illusion.
3. **Utility.** Reserve it for meaningful moments: success, error, commit, snap. Over-feedback trains users to ignore all of it.

## Building components people love (EK)

From building Sonner, and applicable to any component:

1. **Developer experience is the product.** No hooks, no context, no setup. Drop one element in, call one function from anywhere. Less friction to adopt means more adoption.
2. **Good defaults matter more than options.** Ship beautiful out of the box. Most users never customise, so the default easing, timing and visual design have to be excellent.
3. **Naming creates identity.** 'Sonner' beats 'react-toast'. Sacrifice discoverability for memorability when it's worth it.
4. **Handle edge cases invisibly.** Pause timers when the tab is hidden. Fill gaps between stacked items so hover doesn't break. Capture pointer events during drag. Users never notice, which is exactly right.
5. **Build a real documentation site.** Let people touch it and understand it before they adopt it. Interactive examples with copyable snippets lower the barrier.

## Small patterns worth stealing

**Tooltips skip their delay on subsequent hovers.** The first tooltip delays to prevent accidental activation. Once one is open, adjacent tooltips open instantly with no animation. The toolbar feels faster without defeating the point of the initial delay.

```css
.tooltip { transition: transform 125ms ease-out, opacity 125ms ease-out; }
.tooltip[data-instant] { transition-duration: 0ms; }
```

**Match motion to personality.** A playful component can be bouncier. A professional dashboard is crisp and fast. Sonner reads as elegant partly because it's slightly slower than typical and uses `ease` rather than `ease-out`. Everything is in harmony, down to the name.

## Process (Apple)

- **Prototype interactively.** An interactive demo is worth a million static designs. You discover the interface by building and playing with it, and a working prototype sets a concrete bar that stops the final implementation being mediocre.
- **Design interaction and visuals together.** You shouldn't be able to tell where one ends and the other begins. Motion is not a layer added after the pixels.
- **Test with real people in real context**, and review with fresh eyes the next day.
