# Finding Animation Opportunities

Sweep an interface for moments that would genuinely benefit from motion, and reject everything else. This is a filter as much as a finder. Expect to reject most candidates. A short list of high-conviction opportunities beats a long wishlist.

Read-only. It proposes recipes with exact values; it does not implement them.

## The gate

Every candidate survives all four questions, in order. Record the answers, they go in the report.

**1. Frequency.** Use the table in `standards.md` §1. The 100+/day tier and anything keyboard-initiated are disqualifiers, not judgment calls.

**2. Purpose.** Name it in one of the words from `standards.md` §2. If you can't, reject.

**3. Speed.** It has to work inside the budgets in `standards.md` §4. If the moment only works as a slow, showy animation, it fails.

**4. Function.** Decoration on functional, information-dense UI hinders. A mouse-tracking effect is fine on a marketing page. On a banking app's chart, no animation is better. Data the user is reading or acting on doesn't move for style.

## Where to hunt

Each of these is a known class of genuine opportunity.

**Feedback gaps**
- Pressable elements with no `:active` state → `scale(0.96)`, `150ms ease-out`
- Destructive actions on a plain click where a hold-to-confirm would prevent slips → `clip-path` overlay, 2s linear on press, 200ms ease-out snap-back

**Teleporting state**
- Content that swaps, appears or vanishes instantly → fade and scale from `scale(0.95)` + `opacity: 0`, `ease-out`, never `scale(0)`; `@starting-style` for entry without JS
- Accordions and collapses that snap open → height + opacity transition
- List items added or removed with no bridge → enter/exit transitions, CSS transitions not keyframes

**Missing spatial story**
- Panels, popovers and menus appearing with no connection to their trigger → scale from `transform-origin` at the trigger; modals exempt
- Toasts and sheets that exit a different way than they entered → symmetric paths, percentage translates

**Group entrances**
- A grid or list that pops in all at once, on a surface seen occasionally → 30-80ms stagger, never blocking interaction

**Gesture seams**
- Draggable or swipeable elements that snap with no physics → springs, velocity-based dismissal, rubber-banding at boundaries

**The delight budget**
- Rare high-emotion moments rendered flat: first run, empty states, success, completion. The only places bounce, generous stagger, or a longer beat are welcome.

Useful sweeps: conditional renders with no transition (`{isOpen &&`, `display: none` toggles), click handlers on elements with no `:active`, `details` and accordion markup, drag handlers, `.map(` renders of entering lists, empty-state and success components.

## Workflow

1. **Recon.** Stack, motion libraries, existing easing and duration tokens, and the product's personality. A crisp dashboard earns fewer and subtler suggestions than a playful consumer app. Build a rough frequency map.
2. **Sweep** the hunt list. Done when every class has either yielded candidates with `file:line` evidence or been explicitly cleared.
3. **Gate** every candidate. Be ruthless.
4. **Report.** If nothing survives, say so. That's a good result, not a failure.

## Output

**Part 1: Opportunities.** One row per survivor, ordered by leverage. Cap at 5-7 for a whole app, fewer for one view.

| # | Location | Today | Purpose | Frequency | Suggested motion |
| --- | --- | --- | --- | --- | --- |
| 1 | `Toast.tsx:41` | Appears instantly | Preventing a jarring change | Occasional | `@starting-style`: `opacity 0`, `translateY(100%)` → settled, `400ms ease`, exits the same edge |

Every suggested-motion cell carries exact values pulled from the repo's own tokens. Animate `transform` and `opacity` only. Include reduced-motion handling and hover gating where relevant.

**Part 2: Rejected candidates.** Required. 2-5 places you considered and deliberately did not suggest, each with the gate question that killed it.

- `CommandMenu.tsx:12`: palette open/close. Rejected: keyboard-initiated, 100+/day.
- `Chart.tsx:88`: animated line draw. Rejected: functional data the user is reading.

This section is the whole difference between a finding pass and a wishlist.

**Part 3: Verdict.** One paragraph: how much motion this interface actually needs, whether it's already close, and which single suggestion has the highest leverage.
