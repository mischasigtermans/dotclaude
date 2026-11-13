# Feel

What makes an interface feel right, and the details that get it there. All of it is judgment. Push back where it doesn't fit the work.

Motion lives in `motion`, including tooltip delays and fitting an animation to a component's personality.

## Why it matters

**Taste is a trained skill, separate from personal preference.** It sees past the obvious answer and spots what makes something better. Train it on great work: study what you admire, ask why it feels good, and take apart the interactions you'd want to have built.

**Details add up unseen.** Users never consciously notice most of them, and they shouldn't. When something behaves the way they expected, they carry on without a thought. Together, hundreds of these small calls are what make a product feel exceptional.

**Beauty wins users.** People choose a tool for how the whole of it feels, more than for its feature list. Good defaults and good motion set a product apart, and few products bother with beauty.

## Eight principles

Use these names to argue a contested call.

1. **Purpose.** Build on purpose and choose what to leave out. Each feature costs the user time, attention and trust.
2. **Agency.** The user stays in control. Give them choices and forgive mistakes. A slip gets an easy undo. A confirmation dialog is for destructive actions that can't be reversed, nothing else: show it too often and people learn to click through it.
3. **Responsibility.** Work in the user's interest. Ask for a permission when it's needed, and only for what's needed. Expect misuse, above all with AI. Drop a feature when its risk outweighs what it gives.
4. **Familiarity.** Start from what people already know. Pick a metaphor that is neither too literal nor too abstract, and respect its physics. What looks alike acts alike and sits in the same place. Keep a familiar pattern unless you can show a new one is better, and test the new one.
5. **Flexibility.** Plan for other contexts, devices and abilities. Where one layout can't serve everyone, let people adjust it.
6. **Simplicity.** Cut what isn't needed until the core purpose shows. Minimal is a different thing: everything buried in one place looks minimal and isn't simple. Extra context sometimes makes a screen simpler. Put the common path first and the advanced one a level down.
7. **Craft.** Make every spacing, timing and alignment value a choice you can defend. Jittery scrolling, icons out of line and layouts that break on rotation tell the user nobody cared.
8. **Delight.** It comes from getting the other seven right and can't be added as confetti afterwards. Pick the emotion you want and back it up everywhere.

## Feedback and wayfinding

- **Feedback comes in four kinds:** status, completion, warning and error. Confirm actions that matter, show status while work runs, warn before a problem lands, and validate inline instead of on submit.
- **Wayfinding.** Each screen tells the user where they are, where they can go, what's there and how to leave. No dead ends.
- **Grouping and mapping.** Things placed close together look related. Put a control next to what it changes and lay controls out the way their targets are laid out. A control that needs a label to explain it is mapped badly.
- **Name nav items for what they hold.** 'Progress' and 'Library' tell the user what's behind them; 'Home' doesn't. Specific labels make the interface predictable.

## Materials and depth

A translucent layer floats above the content and gives the screen structure while the content keeps the attention. On the web, build it with `backdrop-filter`.

- **Nav bars, toolbars and sheets are translucent layers** with content scrolling beneath them. An opaque bar eats a fixed strip of the screen.
- **Weight shows hierarchy.** Dark, heavy material marks structural regions such as a sidebar. Light material pulls the eye to interactive elements. **Never put a light translucent surface on top of another**; the text on it becomes unreadable.
- **A larger surface reads as thicker.** Give it more blur and a deeper shadow than a small chip. Think about shadow that responds to context, heavier over busy content.
- **Dim for focus, offset for flow.** A modal task gets a scrim (a dimming layer behind the surface) that pushes the background back. A panel that runs alongside the page without blocking it gets translucency and an offset, and no scrim. Sheets stacked on sheets dim each parent a step further.
- **Vibrancy keeps text legible over changing backgrounds.** Flat grey text on a translucent surface fails. Raise the contrast, add some weight and open the letter-spacing slightly. Colour goes on a solid layer, never on the translucent foreground.
- **Fade at scroll edges.** Skip the 1px border under a sticky header. Where content runs under floating chrome, fade it with a small blur or a gradient mask, and only where the two overlap.
- **Glass arrives as a material.** On enter and exit, animate the blur radius and the scale together. An opacity fade on its own falls short.

```css
.app-header {
  backdrop-filter: saturate(160%) blur(24px);
  background: rgba(255, 255, 255, 0.65);
  border-top: 1px solid rgba(255, 255, 255, 0.5); /* a bright top edge, like light on glass */
}
```

## Motion, sound and haptics together

1. **Causality.** The user can tell what caused the feedback. Fire it on the event that caused it, and give it a character that fits how physical the action is.
2. **Harmony.** Picture, sound and haptic land on **the same frame**. Any lag between them breaks the effect.
3. **Utility.** Save it for moments that matter: success, error, commit, snap. Feedback on everything teaches users to tune all of it out.

## Components people love

These hold for any component:

1. **The developer experience is the product.** Adoption should need zero hooks, zero context and zero setup. One element dropped in, one function called from anywhere. The less friction, the more people adopt it.
2. **Defaults beat options.** Make it look good out of the box. Most users never change a setting, so the default easing, timing and visuals carry the whole thing.
3. **A name gives it identity.** 'Sonner' beats 'react-toast'. Trade discoverability for a name people remember when the trade pays off.
4. **Edge cases get handled out of sight.** Pause timers while the tab is hidden. Fill the gaps between stacked items so hover holds. Capture pointer events during a drag. Nobody notices, and that's correct.
5. **Ship a proper docs site.** People should be able to try it and understand it before they commit. Interactive examples with snippets to copy make starting easy.

## Process

- **Prototype interactively.** One interactive demo beats any number of static mockups. You find the interface by building it and trying it out. A prototype that works also sets a bar the final build has to clear.
- **Design the interaction and the visuals as one.** The seam between them shouldn't show. Motion belongs in the design from the start, never as a coat painted on after the pixels.
- **Put it in front of real people, in their real setting**, then look again with fresh eyes the next day.
