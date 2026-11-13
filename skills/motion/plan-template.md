# Plan Template

Write every motion plan in this shape. Assume the agent that runs it is a weaker model with no context and no taste, and put everything it needs in the plan, exactly. Never point at 'the audit above' or 'the easing we discussed'.

```markdown
# NNN: <Title, phrased as a short command>

- **Status**: TODO
- **Commit**: <`git rev-parse --short HEAD` at the time you write the plan>
- **Severity**: HIGH | MEDIUM | LOW
- **Category**: <category from the audit>
- **Estimated scope**: <file count and approximate size>

## Problem

What's wrong, where it lives and how it hurts the feel of the product. Give
each location as `path/to/file.tsx:123` and quote today's code as it stands:

​```css
/* src/ui/context-menu.css:27, current */
.context-menu {
  transform-origin: center;
  transition: all 350ms ease-in;
}
​```

## Target

The end state, exactly. Write out each value, from curves and durations to
spring configs and media queries. 'Use a nicer easing' is not a target:

​```css
/* target state */
.context-menu {
  transform-origin: var(--transform-origin);
  transition: opacity 180ms var(--curve-enter), transform 180ms var(--curve-enter);
}
​```

## Repo conventions to follow

The way this codebase does it today, plus one exemplar for the executor to
copy (token names, where files go, prop patterns):

- Easing tokens sit in `src/styles/motion.css`; put new curves there too, e.g. `--curve-enter: cubic-bezier(0.23, 1, 0.32, 1);`
- <exemplar file:line that already gets this right>

## Steps

1. <One concrete edit per step: the file, the change, the code it produces.>
2. …

## Boundaries

- Do NOT edit <files or components outside this plan>.
- Do NOT alter markup or structure. Change motion properties alone, except where a step says so.
- Do NOT add a dependency.
- If the code has drifted since the commit stamp and a step no longer fits, STOP and report. Don't improvise.

## Verification

- **Mechanical**: <exact commands (typecheck, lint, build) and the result each should give>.
- **Feel check**: open the UI, perform <interaction> and check that:
  - <something you can see, e.g. 'the context menu grows out of the spot that was clicked, not its center'>
  - <e.g. 'hammering the toggle never sends the animation back to zero'>
  - Set playback to 10% in the DevTools Animations panel and confirm <detail>.
  - Turn on `prefers-reduced-motion` in the Rendering panel and confirm the movement is gone while the opacity feedback stays.
- **Done when**: <completion criteria a machine or an eye can check>.
```

## Notes for the plan author

- Write one plan per finding. Two findings may share a plan when they touch exactly the same files and need the same fix pattern (e.g. one easing token swapped across components).
- Copy every value out of [standards.md](./standards.md). Don't fill one in from memory.
- Always include the feel check. Motion that passes every mechanical check can still feel wrong, so give the executor, or the human reviewing its diff, specific things to look for in slow motion.
- Once the plans exist, create or update `plans/README.md`. It lists every plan in a table (number, title, severity, status), then gives the order to run them in and the dependencies between them.
