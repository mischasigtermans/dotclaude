---
paths:
  - "**/*.blade.php"
  - "**/*.{html,tsx,jsx,vue,svelte,css}"
---

# UI

Every UI change meets this bar, whether I asked for it or not.

- Mobile-first. Base classes are the phone layout, `sm:`, `md:` and `lg:` add the larger ones. Nothing wider than the viewport: no fixed widths, tables scroll horizontally, shrinking flex children get `min-w-0`, icons and avatars get `shrink-0`. Body copy stays at `text-base` on mobile. Touch targets are at least 48px.
- A project that uses `dark:` anywhere gets a dark variant on every element you add.
- Reuse the project's components, tokens and spacing scale before adding anything new. Check the project's catalogue and Flux Pro for a component before building one.
- A new page, section or component loads the ui.sh guidelines first: `uidotsh://ui/design-guidelines` for the index, then every topic that applies (always `responsive-design`, plus the section's own topic such as `testimonials` or `pricing-cards`) in one `uidotsh_fetch` call with `uris`. The index alone holds no rules. The tool is deferred: `ToolSearch select:mcp__uidotsh__uidotsh_fetch`.
- In a Flux project every control is Flux's own, never the browser's: `flux:date-picker`, `flux:time-picker`, `flux:select variant="listbox"` or `combobox` (the default `flux:select` renders a native `<select>`), `flux:checkbox`, `flux:radio`, `flux:switch`.
- Build the assets before you tell me to look. A page served from a stale build renders unstyled and wastes the look.
- One visual change, then I look, then the next. Don't stack guesses I haven't seen.
