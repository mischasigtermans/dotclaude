---
name: ui
description: "Local licensed design-pack workflows: UI variants and the browser picker, responsive layouts, dark-mode conversion and Tailwind canonicalization. Load when rules/ui.md requests the design guidelines, or when the user asks for the pack or its workflows. General UI review, component extraction and craft belong to development:ui; animation to development:motion."
allowed-tools:
  - Bash(npx @tailwindcss/cli:*)
---

# UI

A licensed design pack, kept local and never published: the routing, the subskills, the design guidelines and the picker script are files in this directory.

## Load first

1. Read [routing.md](./routing.md) and follow it: design (the fallback), ideas, finalize, componentize, canonicalize-tailwind, add-dark-mode, dark-mode-image, make-responsive. Read the matched subskill and every guideline it points to before writing code. Its line that it only runs on an explicit `/ui` doesn't apply here.
2. New UI reads [design-guidelines.md](./design-guidelines.md) for the index, then every topic that applies: always `responsive-design`, plus the section's own topic such as `testimonials` or `pricing-cards`. The index alone holds no rules.
3. Load `development:ui` as well. Its craft files cover surfaces, typography, feel and library picks, and its sections on how to work, review and verify apply to everything built here. Where a guideline here and a craft file there disagree (shadows, heading leading, the font), the craft file wins.

## On top of the pack

- **A request that conflicts with a guideline**: flag it once, with what the guideline recommends and why, then build what was asked. Never override silently in either direction.
- **Ideas:** the pack's `question` tool is AskUserQuestion here. The picker script is [ui-picker.js](./ui-picker.js) in this directory: copy it into the project's public directory and load it as `/ui-picker.js`. At final cleanup the copy goes with the script tag. In a Laravel project without `resources/views/layouts/app.blade.php`, inject the script once in the shared layout the app does use (a Flux layout, for example), right before `</body>`.
- **Dark-mode images:** the pack hands raster work to an `imagegen` skill that isn't installed here. Generating a dark variant needs an image tool in the session; without one, stop and say so. Never fake it with CSS filters.
- **Componentize and finalize:** reuse the project's components (Flux, Blade components, the existing `components/` directory) before creating one. Scope is the files named or the feature just built, never the whole app, and the UI renders the same before and after.
- **Canonicalize:** pass `--css <entry>` when the project's Tailwind entry isn't the default, and run it over every class list you touched, including new components.
- **Placeholder images:** `placeholder-content.md` and `assets-api.md` load images from the pack's own asset server. If that server stops answering, use the project's own images or a neutral placeholder, and say so.
