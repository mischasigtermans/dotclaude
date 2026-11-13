---
name: ui
description: "Build and refine UI against a craft bar. Use for: new pages, sections and components; add or fix dark mode; componentize or extract components (optimaliseer componenten); improve the UI or review the frontend (verbeter de UI); picking a component, chart or animation library; and craft: shadows, radius, optical alignment, hit areas, typography, hover states, 'this feels off', 'why does this look cheap'. Anything that moves belongs to motion."
---

# UI

The user's own UI rules set the bar. This skill adds the craft under it: how to get surfaces, type and feel right, which library to reach for, and how to work on an interface without breaking it.

## Load

| For | Read |
| --- | --- |
| Radius, shadows, optical alignment, hit areas, image outlines | [surfaces.md](./surfaces.md) |
| Wrapping, font smoothing, tabular numbers, tracking, leading | [typography.md](./typography.md) |
| 'Feels off', a general craft review | [feel.md](./feel.md) |
| A component library, chart, animation, state or styling dependency | [libraries.md](./libraries.md) |

A full pass on a page is feel.md, surfaces.md and typography.md.

## Per kind of work

- **Centering nav links or a logo on the page**, not between the side items: three flex sections. Left `flex flex-1 items-center`, the centred group at its natural width, right `flex flex-1 items-center justify-end`. The matching `flex-1` gutters put the group on the true page centre.
- **A request that conflicts with a rule in these files**: flag it once, with what the file recommends and why, then build what was asked. Never override silently in either direction.
- **Dark-mode images:** a dark variant of a raster image needs an image tool in the session; without one, stop and say so. Never fake it with CSS filters.
- **Componentize:** reuse the project's components (Flux, Blade components, the existing `components/` directory) before creating one. Scope is the files named or the feature just built, never the whole app, and the UI renders the same before and after.

## How to work

1. Read the surrounding code first. Match the project's tokens, spacing scale, component patterns and naming. Never introduce a parallel vocabulary.
2. Change only what the ask covers. Handle an unrelated bug the way the user's own instructions say; without any, name it in the report and leave it. Something that works but looks wrong is named and left.
3. Say what changed and why. A diff of magic numbers with no reasoning is not a refinement.

## Reviewing rather than fixing

When asked to review instead of change, report in a table, one row per issue:

| Before | After | Why |
| --- | --- | --- |

Say plainly when something is weak and when it's already fine. Don't manufacture findings.

## Verify

- The project's formatter, lint, typecheck or tests pass.
- The change holds in both colour schemes, at every breakpoint and in every interaction state it touches.
- Refining and componentizing never alter what the UI does.
- Name the page, breakpoint and state to look at, and what should be visible there.
