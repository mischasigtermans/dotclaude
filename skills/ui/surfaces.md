# Surfaces

Radius on nested elements, optical alignment, shadows, image outlines and hit areas.

## Concentric radius

When one rounded element sits inside another, add the padding between them to the inner radius to get the outer one:

```
outerRadius = innerRadius + padding
```

Same radius on both reads wrong. Nested radii that don't match are among the commonest reasons an interface feels off, so do the sum every time.

The rule earns its keep when the two surfaces sit close. Past `24px` of padding they stop reading as one object: pick each radius on its own and skip the maths.

```css
/* Good: 10 + 6 = 16 */
.panel {
  padding: 6px;
  border-radius: 16px;
}
.panel-media {
  border-radius: 10px;
}

/* Bad: 10px outside and in, so the gap bulges at the corners */
.panel {
  padding: 6px;
  border-radius: 10px;
}
.panel-media {
  border-radius: 10px;
}
```

In Tailwind:

```tsx
// Good: 12px outside = 8px inside + 4px padding
<section className="rounded-xl p-1">
  <img className="rounded-lg" src={cover} alt="" />
</section>

// Bad: 8px on both, so the outer corner looks too tight
<section className="rounded-lg p-1">
  <img className="rounded-lg" src={cover} alt="" />
</section>
```

## Optical alignment

Geometric centre and visual centre aren't always the same point. When the maths is right and it still looks off, trust the eye.

### Text and icon in one button

Give the icon side 2px less padding than the text side: `icon-side padding = text-side padding - 2px`. With equal padding the icon looks pushed too far right.

```css
/* Good: text on the left at 20px, icon on the right at 18px */
.btn-next {
  padding-inline: 20px 18px;
}

/* Bad: 20px on both sides drifts the icon right */
.btn-next {
  padding-inline: 20px;
}
```

```tsx
// Tailwind: 12px on the text side, 10px on the icon side
<button className="inline-flex items-center gap-1.5 pl-3 pr-2.5">
  <span>Next step</span>
  <ChevronRightIcon />
</button>
```

### Play triangles

A triangle's geometric centre isn't where it looks centred. Nudge the icon right.

```css
/* Good: nudged right until it looks centred */
.video-play > svg {
  margin-left: 2px;
}

/* Bad: centred by the box, off-centre to the eye */
.video-play > svg {
  margin-left: 0;
}
```

### Lopsided icons: stars, arrows, carets

Fix the weight in the SVG itself, so the component needs no extra margin or padding. Use a margin only when you can't touch the SVG.

```tsx
// Best: correct the path or the viewBox in the SVG file

// Fallback: nudge the wrapper by 1px
<span className="inline-flex ml-px">
  <CaretIcon />
</span>
```

## Shadows over borders

Where a border gives a button, card or container its depth or elevation, replace it with a light `box-shadow`. A shadow is transparent, so it sits right on any background. A solid border colour only works on the background it was picked for, which rules it out over images or several colours.

Leave dividers alone. `border-b`, `border-t`, side borders and any border that separates layout rather than lifting an element stay borders.

| Shadow | Border |
| --- | --- |
| Cards and containers that need depth | Lines between items in a list |
| Button styles that would carry a border | Edges of table cells |
| Raised elements, such as dropdowns and modals | Outlines on form inputs, kept for accessibility |
| Anything on a mixed or changing background | Hairlines in dense UI |
| Lift on hover or focus | |

### Light mode

Three layers. The first is a 1px ring that does the border's job, the second gives a little lift, the third adds ambient depth.

```css
:root {
  --edge-shadow:
    0 0 0 1px rgba(0, 0, 0, 0.06),
    0 1px 2px -1px rgba(0, 0, 0, 0.06),
    0 2px 4px 0 rgba(0, 0, 0, 0.04);
  --edge-shadow-hover:
    0 0 0 1px rgba(0, 0, 0, 0.08),
    0 1px 2px -1px rgba(0, 0, 0, 0.08),
    0 2px 4px 0 rgba(0, 0, 0, 0.06);
}
```

### Dark mode

One white ring. Depth layers vanish on a dark background, so drop them.

```css
/* Swap the media query for the project's own dark-mode hook, such as a class or a data attribute */
@media (prefers-color-scheme: dark) {
  :root {
    --edge-shadow: 0 0 0 1px rgba(255, 255, 255, 0.08);
    --edge-shadow-hover: 0 0 0 1px rgba(255, 255, 255, 0.13);
  }
}
```

### Hover

Set the variable and transition `box-shadow` alone (`transition-[box-shadow]` in Tailwind):

```css
.tile {
  transition: box-shadow 150ms ease-out;
  box-shadow: var(--edge-shadow);
}

.tile:hover {
  box-shadow: var(--edge-shadow-hover);
}
```

## Image outlines

Give images a `1px` outline at low opacity. It gives them the same edge as everything else, which matters most in a design system where other elements carry borders or shadows.

The colours are fixed. Don't adapt them:

- **Light:** pure black, `rgba(0, 0, 0, 0.1)`. R=0, G=0, B=0.
- **Dark:** pure white, `rgba(255, 255, 255, 0.1)`. R=255, G=255, B=255.
- No palette near-black or near-white: not slate-900, zinc-900, `#0a0a0a`, `#111827` or `#f5f5f7`. A tinted outline takes on the colour of the surface behind it and looks like dirt on the edge of the image.
- No accent or ink colour either. The outline separates; it carries no theme.

```css
img {
  outline: 1px solid rgba(0, 0, 0, 0.1);
  outline-offset: -1px; /* drawn inside the image, so the layout stays put */
}

@media (prefers-color-scheme: dark) {
  img {
    outline-color: rgba(255, 255, 255, 0.1);
  }
}
```

In Tailwind, both modes:

```tsx
<img
  src={photo.url}
  alt={photo.caption}
  className="outline outline-1 -outline-offset-1 outline-black/10 dark:outline-white/10"
/>
```

Write `outline-black/10` and `outline-white/10`. Never `outline-slate-*`, `outline-zinc-*`, `outline-neutral-*` or another tinted scale.

Use `outline`, not `border`. An outline adds no width or height, and `outline-offset: -1px` pulls it inside so the image keeps its size.

## Hit areas

Every interactive element gets at least 48×48px to hit. When what the user sees is smaller, such as a 16×16 checkbox, grow the target with a pseudo-element.

```css
/* A 16px checkbox with a 48px target: 16 + 2 × 16 = 48 */
.checkbox {
  position: relative;
  width: 16px;
  height: 16px;
}

.checkbox::before {
  content: "";
  position: absolute;
  inset: -16px;
}
```

In Tailwind:

```tsx
<button className="relative size-4 before:absolute before:-inset-4" aria-label="Select row">
  <CheckIcon />
</button>
```

Two hit areas never overlap. When the pseudo-element would run into a neighbouring control, shrink it until it clears, and no further.
