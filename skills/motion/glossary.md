# Motion Glossary

Works backwards: the user describes an effect and you give its name. Match what the effect does, whatever words the user picked. When two entries come close, offer both and say what separates them.

Give the user the term so they can use it precisely from then on, and point them to `standards.md` for exact numbers.

## Glossary

### Entrances & Exits: how things arrive and leave
- **Fade in / Fade out.** Opacity carries the element onto or off the screen.
- **Slide in.** The element travels in from beyond one edge of the screen, whether top, bottom, left or right.
- **Scale in.** The element grows to full size as it arrives, usually with a fade.
- **Pop in.** The element arrives with a small overshoot and settles, as if it bounced.
- **Reveal.** The content is uncovered bit by bit, typically by animating a clip-path or a mask.
- **Enter / Exit.** The animation an element runs on joining or leaving the screen.

### Sequencing & Timing: lining up several elements or moments
- **Keyframes.** Fixed points in an animation, such as 0%, 50% and 100%, with the browser filling in between.
- **Interpolation / Tween.** Computing every frame between a start value and an end value so the motion runs without gaps.
- **Stagger.** Starting a set of items one after the other, a short delay apart, so they cascade.
- **Orchestration.** Timing several animations on purpose so they read as one movement.
- **Delay.** The wait before an animation begins.
- **Duration.** How long an animation runs.
- **Fill mode.** Whether an element holds the styles of its first frame before the animation starts, or of its last frame once it has finished (e.g. forwards).
- **Stepped animation.** Motion that advances in separate jumps, the way a countdown timer ticks.

### Movement & Transforms: changing position, size or angle
- **Translate.** Shifting an element along X or Y.
- **Scale.** Making an element larger or smaller.
- **Rotate.** Turning an element around a point.
- **Skew.** Slanting an element along X or Y, so its rectangle shears.
- **3D tilt / Flip.** Rotating in 3D (rotateX / rotateY) for a sense of depth.
- **Perspective.** The strength of the 3D effect. A lower value exaggerates depth, as if the viewer stood closer.
- **Transform origin.** The point a scale grows from or a rotation turns around.
- **Origin-aware animation.** The element animates out of whatever triggered it, such as a popover growing from its button. CSS grows it from its own center unless told otherwise.

### Transitions Between States: linking one state, view or element to the next
- **Crossfade.** Two elements share a spot; one fades out while the other fades in.
- **Continuity transition.** A change that visibly links before and after so the user stays oriented, such as one rectangle growing and shrinking.
- **Morph.** One shape flows into another, as on the Dynamic Island.
- **Shared element transition.** An element moves and reshapes from one place into another, such as a thumbnail opening into a card.
- **Layout animation.** An element whose size or position changes animates to its new place rather than jumping there.
- **Accordion / Collapse.** A section animates its height open and closed to show or hide its content.
- **Direction-aware transition.** Content moves one way when going forward and the other way when going back, so navigation has direction.

### Scroll: motion linked to scrolling or moving between views
- **Scroll reveal.** As elements come into the viewport, they fade or slide into position.
- **Scroll-driven animation.** Animation progress bound directly to the scroll position.
- **Parallax.** Background and foreground scroll at different speeds, which suggests depth.
- **Page transition.** Motion that plays as the user navigates between pages or routes.
- **View transition.** A browser-made morph between two states or pages that links the elements they share.

### Feedback & Interaction: answering what the user does
- **Hover effect.** A visual change while the cursor is over an element.
- **Press / Tap feedback.** A small scale-down on click so the element feels physical.
- **Hold to confirm.** A progress fill that grows while the user keeps a button pressed.
- **Drag.** Grabbing an element and moving it, often with momentum on release.
- **Drag to reorder.** Dragging list items into a new order while the rest move aside.
- **Swipe to dismiss.** Closing an element, such as a drawer or a toast, by dragging it off the screen.
- **Rubber-banding.** Pull past a boundary meets resistance, then springs back, like overscroll on iOS.
- **Shake / Wiggle.** A short side-to-side jitter that signals an error or a rejected input.
- **Ripple.** From the point of the tap, a circle spreads outward to confirm the press.

### Easing: how speed changes through an animation
- **Easing.** The pattern of acceleration and deceleration across an animation.
- **Ease-out.** Fast at the start, slow at the end. The default for most UI and for anything that responds to the user.
- **Ease-in.** Slow at the start, fast at the end. Mostly avoided, since it can feel sluggish.
- **Ease-in-out.** Starts slow, speeds up, then slows again. Suits an on-screen element travelling from A to B.
- **Linear.** One speed throughout. Keep it out of UI; it belongs to spinners and marquees.
- **Cubic-bezier.** An easing curve you write yourself when you need exact control.
- **Asymmetric easing.** A curve that speeds up and slows down at different rates. It feels more alive than a symmetric curve.

### Spring Animations: physics in place of a fixed duration and curve
- **Spring.** Motion governed by physics (tension, mass, damping) instead of a set duration.
- **Stiffness / Tension.** The force pulling the spring toward its target. More stiffness feels snappier.
- **Damping.** How fast the spring comes to rest. With less damping the spring bounces and oscillates more.
- **Mass.** The weight the moving element seems to have. Add mass and it moves slower and more sluggishly.
- **Bounce.** Overshooting the target and settling back, which adds playfulness.
- **Perceptual duration.** The point at which a spring looks finished, even while it keeps settling by tiny amounts.
- **Momentum.** Motion that keeps its velocity, especially after a drag or an interruption.
- **Velocity.** The speed and direction an element moves in. An interrupted spring hands it on to the next animation, so a flicked element doesn't lose speed.
- **Interruptible animation.** Motion that can change course smoothly mid-flight rather than run to the end first.

### Looping & Ambient Motion: animations that run by themselves
- **Marquee.** Text or content scrolling on a continuous loop.
- **Loop.** Repeating an animation a fixed number of times, or without end.
- **Alternate (yoyo).** A loop that runs forward and then backward each time, rather than jumping back to the start.
- **Orbit.** One element travelling a continuous circle around another.
- **Pulse.** A soft, repeating change in scale or opacity that draws the eye.
- **Float.** A slow, endless drift up and down that gives a static element a light, living feel.
- **Idle animation.** Small motion an element plays while it waits for the user.

### Polish & Effects: the small details that finish the work
- **Blur.** A blur filter that softens an element or hides small flaws.
- **Clip-path.** Cropping an element to a shape; reveals, masks and before/after sliders run on it.
- **Mask.** Showing or hiding parts of an element through a shape or gradient. Clip-path with soft edges that can fade.
- **Before / after slider.** A divider the user drags to wipe between two stacked images and compare them.
- **Line drawing.** A path in SVG that traces itself onto the screen, as if drawn by an invisible pen.
- **Text morph.** Text that animates per character when its value changes, pulling the eye to the new value.
- **Skeleton / Shimmer.** A stand-in shape with a sheen sweeping across it while content loads.
- **Number ticker.** Digits that roll or count up to a value.
- **Tabular numbers.** Digits of equal width, so a changing number doesn't shift sideways. Required for tickers, timers and counters.
- **Typewriter.** Text that appears one character at a time, as if someone were typing it.

### Performance: what keeps motion smooth
- **Frame rate (FPS).** How many frames are drawn each second. 60fps is the floor for smooth motion; newer displays run 120fps.
- **Jank.** Visible stutter from the browser dropping frames it can't keep up with.
- **Dropped frame.** A frame the browser didn't draw in time, which shows as a small hitch.
- **Compositing.** The GPU moves or fades an element on its own layer, with no new layout or paint.
- **will-change.** A hint in CSS announcing upcoming animation on an element, so the browser can move it to its own layer early.
- **Layout thrashing.** Animating properties such as width, height, top or left, which make the browser redo layout on every frame and cause jank.

### Principles to Know: ideas for deciding whether and how to animate
- **Purposeful animation.** Every movement does a job, such as orienting, giving feedback or showing relationships, instead of decorating.
- **Anticipation.** A brief wind-up the other way before the main move, signalling what comes next.
- **Follow-through.** Parts of an element keep going and settle a little after the main motion stops, which adds weight.
- **Squash & stretch.** Changing an element's shape while it moves, to show its weight, speed and flexibility.
- **Perceived performance.** A well-chosen animation can make an interface seem quicker than it is.
- **Frequency of use.** An animation the user sees often should be shorter and quieter than one they rarely see.
- **Spatial consistency.** An element keeps its identity and place across states, so the user always knows where things went.
- **Hardware acceleration.** Restricting animation to transform and opacity so the GPU can keep it smooth.
- **Reduced motion.** Honouring the user's prefers-reduced-motion setting by reducing or removing motion.
