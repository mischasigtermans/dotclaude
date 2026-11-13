# Typography

How text wraps, renders and scales in an interface.

## Wrapping

Pick the `text-wrap` value by length.

| Text | Value |
| --- | --- |
| Headings and titles that need lines of equal length | `text-wrap: balance` |
| UI copy, captions, descriptions and paragraphs, short to medium | `text-wrap: pretty` |
| Long text (10+ lines), pre-formatted text, code blocks | Neither, leave the default |

### `text-wrap: balance`

Evens out line lengths so a heading or other short block doesn't end on one stray word. Browsers only run it on short blocks, because the algorithm is costly: 6 lines or fewer in Chromium, 10 or fewer in Firefox. On anything longer it does nothing. Tailwind: `text-balance`.

```css
/* Good: titles break into lines of even length */
.page-title,
.section-title {
  text-wrap: balance;
}
```

```css
/* Bad: default wrapping gives "Pricing for every
   team", with "team" stranded on line two */
.hero-heading {
  text-wrap: wrap;
}
```

```css
/* Bad: body paragraphs run past the line limit, so the browser skips it */
.post-content p {
  text-wrap: balance;
}
```

### `text-wrap: pretty`

Moves line breaks across the whole paragraph so the last line never holds a single word. It leaves line lengths uneven and only guards the ending. No line limit applies. Tailwind: `text-pretty`.

Make it the default for short and medium text, such as list items, captions, card copy, descriptions and paragraphs. At 10 lines or more, use neither `pretty` nor `balance`. Default wrapping looks fine at that length and costs less layout work.

```css
/* Good: card copy, captions, list items, paragraphs */
.card-body,
figcaption,
li,
p {
  text-wrap: pretty;
}
```

```tsx
// Tailwind
<figcaption className="text-pretty">
  The team at the March offsite, after the last session of the day.
</figcaption>
```

## Font smoothing on macOS

macOS draws text heavier than the design intends. Set antialiased smoothing once, on the root, and every piece of text comes out crisper and lighter.

```css
:root {
  -moz-osx-font-smoothing: grayscale;
  -webkit-font-smoothing: antialiased;
}
```

```tsx
// Tailwind: on the root element
<html lang="en" className="antialiased">
```

Set it per element and every element you miss renders heavier than the rest.

```css
/* Good: set once, on the root */
:root {
  -webkit-font-smoothing: antialiased;
}

/* Bad: set on the title alone, so the intro renders heavier */
.page-title {
  -webkit-font-smoothing: antialiased;
}
.page-intro {
  font-size: 1.125rem;
}
```

Only macOS reads these properties. Other platforms ignore them, so they do no harm anywhere.

## Tabular numbers

Give numbers that change in place (timers, prices, counters, numeric table columns) `tabular-nums`. Every digit then takes the same width, so the layout stops shifting as the value changes.

```css
.price,
.timer {
  font-variant-numeric: tabular-nums;
}
```

```tsx
// Tailwind
<td className="tabular-nums">{row.total}</td>
```

| Tabular | Leave proportional |
| --- | --- |
| Timers, counters | Numbers that never change on screen |
| Live prices | Big decorative figures |
| Numeric columns in a table | Zip codes, phone numbers |
| Numbers that animate from one value to the next | Version numbers (v2.1.0) |
| Dashboards, scoreboards | |

Some fonts redraw numerals under this property. In Inter, the `1` gets wider and sits centred. That's expected and usually helps alignment, but check the result in the font you're using.

```css
/* Inter, before and after tabular-nums:
   proportional  1170  → the "1" is narrow
   tabular       1170  → every digit equal width, the "1" centred */
```

## Optical size, tracking, leading

Set type differently at each size instead of scaling one style up. Tracking is the space between letters; leading is the space between lines.

- **Tracking depends on size, so no single value fits every size.** Big display type needs negative tracking, since its letters look spaced out. Small type needs a little positive tracking to stay legible. One fixed `letter-spacing` is wrong at some size. Tighten headings and keep body text near `0`.
- **Leading moves against size.** Large headings get tight leading, body copy gets more. Open it up when a script has tall ascenders and descenders. Close it for dense, data-heavy UI.
- **Combine weight, size and leading for hierarchy.** Size alone is thin. Weight gives presence and costs no room.
- **Scale with the user's text setting.** Set spacing in `rem` or `em` so the layout grows with the type. Fixed px breaks when the user scales text up.
- **Start from the system font.** It ships with tracking tables, optical sizing and legibility tuning built in. Swap it out only for a reason.

```css
html {
  font-family: system-ui, sans-serif;
  font-size: 100%;
  line-height: 1.5;
}

.hero-title {
  font-optical-sizing: auto;
  font-size: clamp(2.25rem, 6vw, 4.5rem);
  line-height: 1.1;          /* large type, tight leading */
  letter-spacing: -0.025em;  /* large type, negative tracking */
}
```
