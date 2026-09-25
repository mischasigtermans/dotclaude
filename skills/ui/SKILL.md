---
name: ui
description: "Build and refine UI with the ui.sh guidelines, fetched live. Use for: new pages, sections, layouts and components; several variants to compare and pick from; make it responsive or fix it on mobile (maak responsive, werkt niet op mobiel); add or fix dark mode; componentize or extract components (optimaliseer componenten); canonicalize or clean up Tailwind classes (ruim de classes op); improve the UI or review the frontend (verbeter de UI); and craft: shadows, radius, optical alignment, hit areas, typography, hover states, 'this feels off', 'why does this look cheap'. Anything that moves is motion."
allowed-tools:
  - mcp__uidotsh__uidotsh_fetch
  - WebFetch
  - Bash(npx @tailwindcss/cli:*)
---

# UI

ui.sh routes the work. This file adds what ui.sh doesn't have.

## Load first

1. `ToolSearch select:mcp__uidotsh__uidotsh_fetch`.
2. Fetch `uidotsh://ui` and follow its routing: design (the fallback), ideas, finalize, componentize, canonicalize-tailwind, add-dark-mode, dark-mode-image, make-responsive. Fetch what the matched subskill points to, in one call with `uris`. Its line that it only runs on an explicit `/ui` doesn't apply here.
3. Craft asks ui.sh doesn't cover load a file from this directory:
   - 'feels off', a general craft review → [feel.md](./feel.md)
   - shadows, radius, optical alignment, hit areas, image outlines → [surfaces.md](./surfaces.md)
   - wrapping, font smoothing, tabular numbers, tracking, leading → [typography.md](./typography.md)

   A full pass on a page is feel, surfaces and typography, then make-responsive.
4. [libraries.md](./libraries.md) when the work needs a component library, chart, animation, state or styling dependency.

If the MCP server isn't connected, say so and stop. Don't build from memory of the guidelines.

## On top of ui.sh

- **Centering nav links or a logo on the page**, not between the side items: three flex sections. Left `flex flex-1 items-center`, the centred group at its natural width, right `flex flex-1 items-center justify-end`. The matching `flex-1` gutters put the group on the true page centre.
- **A request that conflicts with a guideline**: flag it with AskUserQuestion, say what the guideline recommends and why, offer a concrete alternative, and wait. Never override silently in either direction.
- **Ideas:** before coding a new-design option, write its style definition in the reply. Ask for the selection with AskUserQuestion, one question per decision point, labels matching the picker labels, the `(current)` option first. In a Laravel project without a framework script API, inject the picker script once in the shared layout (`resources/views/layouts/app.blade.php` or the Flux layout the app uses), right before `</body>`.
- **Responsive audit order:** page shell and breakpoints, then navigation and pagination, then text, forms and touch targets, then overflow, then component patterns.
- **Dark-mode images:** ui.sh hands raster work to an `imagegen` skill that doesn't exist here. Generating a dark variant needs an image tool in the session; without one, stop and say so. Never fake it with CSS filters.
- **Componentize and finalize:** reuse the project's components (Flux, Blade components, the existing `components/` directory) before creating one. Scope is the files named or the feature just built, never the whole app, and the UI renders the same before and after.
- **Canonicalize:** pass `--css <entry>` when the project's Tailwind entry isn't the default, and run it over every class list you touched, including new components.

## How to work

1. Read the surrounding code first. Match the project's tokens, spacing scale, component patterns and naming. Never introduce a parallel vocabulary.
2. Check `package.json` before adding a dependency. A listed library the project already uses wins. If it uses a competitor, flag the pick but don't churn the dependency unasked.
3. Change only what the ask covers. If you spot something unrelated and broken, mention it and leave it.
4. Say what changed and why. A diff of magic numbers with no reasoning is not a refinement.

## Reviewing rather than fixing

When asked to review instead of change, report in a table, one row per issue:

| Before | After | Why |
| --- | --- | --- |

Say plainly when something is weak and when it's already fine. Don't manufacture findings.

## Verify

- The project's formatter, lint, typecheck or tests pass.
- The change holds in both colour schemes, at every breakpoint and in every interaction state it touches.
- Refining, componentizing and canonicalizing never alter what the UI does.
- Name the page, breakpoint and state to look at, and what should be visible there.
