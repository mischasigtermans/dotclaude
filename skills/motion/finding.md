# Finding Animation Opportunities

Go through an interface looking for moments that motion would improve, and throw out the rest. Rejecting is half the job, and most candidates should fail. A short list you'd defend beats a long one you wouldn't.

This pass reads and reports. It proposes recipes with exact values and leaves building them to a later ask.

## The gate

A candidate has to clear all four questions, asked in this order. Write the answers down; the report needs them.

**1. Frequency.** Place it in the table in `standards.md` §1. Anything in the 100+/day tier, and anything started from the keyboard, fails outright, with no judgment call.

**2. Purpose.** Pick its purpose from the list in `standards.md` §2. If none fits, reject it.

**3. Speed.** It must work within the durations in `standards.md` §4. A moment that only lands as a slow, showy animation fails.

**4. Function.** On functional, information-dense UI, decoration gets in the way. A mouse-tracking effect suits a marketing page. A chart in a banking app is better with no animation at all. Data the user reads or acts on never moves for style alone.

## Where to hunt

Each class below reliably turns up real opportunities.

**Feedback gaps**
- Anything pressable that lacks an `:active` state → `scale(0.96)`, `150ms ease-out`
- Destructive actions that fire on a single click, where holding to confirm would catch mistakes → `clip-path` overlay, 2s linear while pressed, 200ms ease-out snap-back

**Teleporting state**
- Views that swap, mount or unmount content in a single frame → scale up and fade in from `scale(0.95)` + `opacity: 0`, `ease-out`, never `scale(0)`; `@starting-style` handles entry without JS
- Collapsible sections and accordions that open in one jump → height + opacity transition
- Lists whose items appear or disappear with nothing between the states → enter/exit transitions built with CSS transitions, not keyframes

**Missing spatial story**
- Menus, panels and popovers that appear unconnected to their trigger → grow from a `transform-origin` set at the trigger; modals exempt
- Sheets and toasts that leave by a different route than they came in → symmetric paths, percentage translates

**Group entrances**
- A list or grid that appears in one go, on a surface the user sees occasionally → 30-80ms stagger that never blocks interaction

**Gesture seams**
- Swipeable or draggable elements that snap without physics → springs, dismissal by velocity, rubber-banding at the edges

**The delight budget**
- Rare moments with emotional weight that play flat today, such as first run, empty states, success and completion. Bounce, a generous stagger or a longer beat belong here and nowhere else.

Sweeps that find these: click handlers on elements that lack `:active`, conditional renders that skip a transition (`{isOpen &&`, `display: none` toggles), drag handlers, `details` and accordion markup, `.map(` renders of lists that gain items, and components for empty states and success.

## Workflow

1. **Recon.** Note the stack, the motion libraries, the easing and duration tokens already in place, and the personality of the product. Suggest less, and more quietly, for a crisp dashboard than for a playful consumer app. Sketch how often each surface gets used.
2. **Sweep** the hunt list. You're done when every class has either produced candidates with `file:line` evidence or been cleared on purpose.
3. **Gate** every candidate, without mercy.
4. **Report.** When no candidate survives, report that. An empty list is a good outcome.

## Output

**Part 1: Opportunities.** One row per candidate that survived, highest impact first. At most 5-7 rows for a whole app; a single view gets fewer.

| # | Location | Today | Purpose | Frequency | Suggested motion |
| --- | --- | --- | --- | --- | --- |
| 1 | `Toast.tsx:41` | Appears instantly | Preventing a jarring change | Occasional | `@starting-style`: `opacity 0`, `translateY(100%)` → settled, `400ms ease`, exits the same edge |

Fill every suggested-motion cell with exact values taken from the repo's own tokens. Animate `transform` and `opacity` unless `standards.md` §20 lists an exception. Add reduced-motion handling and a hover gate where they apply.

**Part 2: Rejected candidates.** Required, because the rejections separate a finding pass from a wishlist. List 2-5 places you looked at and chose not to suggest, each with the gate question that ruled it out.

- `CommandMenu.tsx:12`: palette open/close. Rejected: keyboard-initiated, 100+/day.
- `Chart.tsx:88`: animated line draw. Rejected: functional data the user is reading.

**Part 3: Verdict.** One paragraph. Say how much motion the interface needs, whether it's nearly there already, and which one suggestion would help most.
