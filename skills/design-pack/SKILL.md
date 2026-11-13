---
name: design-pack
description: "Design and build UI with the ui.sh design guidelines, fetched through its MCP server. Use for new pages, sections and components when the user's UI rules ask for design guidelines, for UI ideas or variants to pick from in the browser, and when the user names ui.sh or the design pack. Requires a ui.sh account with its MCP server connected. Triggers on 'a few ideas for this section', 'show me three hero layouts', 'ideeën voor deze sectie', 'use the design guidelines'. Craft and review belong to ui, animation to motion."
allowed-tools:
  - Bash(npx @tailwindcss/cli:*)
---

# Design pack

[ui.sh](https://ui.sh) sells design skills and guidelines for agents and serves them through its MCP server. This skill holds none of that text. It fetches what the task needs and adds how to work with it.

## What it needs

The ui.sh MCP server, connected with the user's own account. Its fetch tool is `uidotsh_fetch`; Claude Code lists it as `mcp__uidotsh__uidotsh_fetch`.

Without that tool, say that the design guidelines aren't available in this session and carry on with `ui` alone. Never write the guidelines from memory.

## Load first

1. Fetch `uidotsh://ui` and follow its routing. It names the subskills and where each one lives; `design` is the fallback. Its line that it only runs on an explicit `/ui` doesn't apply here.
2. Fetch the matched subskill and every guideline it points to before you write code. New UI starts at `uidotsh://ui/design-guidelines`, which is an index and holds no rules. From it, fetch every topic that applies: always `responsive-design`, plus the section's own topic such as `testimonials` or `pricing-cards`. Pass the URIs you already know in one call, as `uris`.
3. Load `ui` as well. Its craft files cover surfaces, typography, feel and library picks, and its sections on how to work, review and verify apply to everything built here. Where a guideline and a craft file disagree (shadows, heading leading, the font), the craft file wins.

## On top of the guidelines

- **A request that conflicts with a guideline:** flag it once, with what the guideline recommends and why, then build what was asked. Never override silently in either direction.
- **Ideas:** the `question` tool the subskill asks for is AskUserQuestion in Claude Code. In a Laravel project without `resources/views/layouts/app.blade.php`, inject the picker script once in the shared layout the app does use (a Flux layout, for example), right before `</body>`. At final cleanup the script tag goes with the variants that weren't picked.
- **Dark-mode images:** the subskill hands raster work to an `imagegen` skill. Generating a dark variant needs an image tool in the session; without one, stop and say so. Never fake it with CSS filters.
- **Componentize and finalize:** reuse the project's components (Flux, Blade components, the existing `components/` directory) before creating one. Scope is the files named or the feature built in this session, never the whole app, and the UI renders the same before and after.
- **Canonicalize:** pass `--css <entry>` when the project's Tailwind entry isn't the default, and run it over every class list you touched, including new components.
- **Placeholder images:** the guidelines load images from ui.sh's asset server. If that server stops answering, use the project's own images or a neutral placeholder, and say so.
