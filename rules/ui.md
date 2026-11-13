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
- A new page, section or component loads `development:design-pack` first. It fetches the design guidelines index from ui.sh, then every topic that applies (always `responsive-design`, plus the section's own topic such as `testimonials` or `pricing-cards`). The index alone holds no rules.
- In a Flux project every control is Flux's own, never the browser's: `flux:date-picker`, `flux:time-picker`, `flux:select variant="listbox"` or `combobox` (the default `flux:select` renders a native `<select>`), `flux:checkbox`, `flux:radio`, `flux:switch`. That holds for the pages already there: the change that brings Flux into a project converts every native control in its views, `<details>` to `flux:accordion` included, and a grep for `<input`, `<select`, `<textarea`, `<button` and `<details` comes back empty.
- In a Flux project, read the component's page in the Flux docs before styling it: the documented composition beats a class. A link in text is `flux:link` inside `flux:text`, which gives it the text's size and colour; a size class on the link is the wrong fix.
- A Flux project's `app.css` holds `@custom-variant dark (&:where(.dark, .dark *));`, Flux's install step: without it Flux's `dark:` follows the system while `@fluxAppearance` and the project's tokens follow the chosen appearance, and the two fight. Check dark mode with the system and the chosen appearance set opposite, both ways, never only with both dark.
- Build the assets before you tell me to look. A page served from a stale build renders unstyled and wastes the look.
- A page is done when it holds up as a page, not when it renders: a run of sections in the same shape (heading, lede, list) is unfinished, and so is a hero carrying a paragraph. Every page gets rhythm (bands, figures, splits, a scene or artwork where the project has them) and a hero of one title, one short lede and its actions.
- An interactive component is checked in every state it has, not on its happy path: each branch (found, not found, ineligible, empty, error), each long option text, opened and closed. Zoomed in, fields in one row share a baseline, nothing overlaps a close button, a label fits its control.
- Before you tell me to look, screenshot every screen the change reaches, full page, at 390px and at desktop width, and read each one as a designer: edges and baselines line up, a list or table inside a card runs to the card's edges with no inset of its own, the last row has no bottom border, and an alert is never a coloured left border on a tint. A shared component's change reaches every screen that uses it, not only the one you were working on. Screenshot in WebKit as well as Chromium (Playwright's `webkit`, browsers installed under the scratchpad via `PLAYWRIGHT_BROWSERS_PATH`): Safari and every iOS browser are WebKit, and it differs where Chrome looks right, such as an `aspect-ratio` box with `overflow: hidden` that WebKit widens to fit its content.
- One visual change, then I look, then the next. Don't stack guesses I haven't seen.
- A button's label is the act. Only the page's primary call to action may carry a trailing arrow; a secondary or ghost button carries none, and an icon on a button names what it does (download, add), never decorates it.
- A block says each thing once. No label stacked over a title that names the same thing, no badges restating its copy, a column's label once at its head and never on every row, and no icon set in a decorative circle or square. A block that needs a label, a title and badges to be understood has the wrong layout: change the layout, not the labels.
- Copy handed over as one long paragraph gets a layout, never a heading of its own: a headline, a lede and the lists inside it as facets, all in the giver's words. A 50-word sentence set as the h1 reads as a wall.
