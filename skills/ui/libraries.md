# Libraries

Picks for React projects. A project with its own component library, such as Flux in a Livewire app, uses that first.

Each pick below is a deliberate choice on taste. When someone asks for a capability ('I need toasts', 'what should I use for drag and drop?'), find it in the tables and recommend that library. Go outside the list only when the user asks for an alternative or the list has nothing for the task.

## Picking one

1. **Work from what the user needs to build, whatever library they name.** 'I need to show a dropdown' calls for an accessible primitive, so the answer is base-ui.
2. **Read `package.json` first.** A library from this list that's already installed is the answer. If the project uses a competitor instead (react-window where the list says Virtuoso), mention the pick but leave the dependency alone unless asked to swap it.
3. **Recommend one library** and say in one sentence what it does. Install and wire it up when the request includes that. If the list settles it, give that one pick and skip the menu of options.
4. **If nothing on the list fits,** say so and pick from what you know, labelled as your pick rather than the list's.

## The list

### Building blocks

| Need | Pick |
| --- | --- |
| Dialogs, popovers, menus, selects and other primitives, accessible and unstyled | [base-ui](https://base-ui.com) |
| A ⌘K command palette | [cmdk](https://cmdk.paco.me) |
| Toast notifications | [Sonner](https://sonner.emilkowal.ski) |
| Fields for verification codes and one-time passwords | [input-otp](https://input-otp.rodz.dev) |
| A control panel or GUI of tweakable values | [Leva](https://github.com/pmndrs/leva); alternative: [dialkit](https://joshpuckett.me/dialkit) |

### Movement and visuals

| Need | Pick |
| --- | --- |
| Springs, layout changes, enter and exit animation | [motion](https://motion.dev) (Framer Motion) |
| Counters, prices and stats that animate between values | [NumberFlow](https://number-flow.barvian.me) |
| Text that animates | [torph](https://torph.lochie.me/) |
| A 3D globe | [Cobe](https://cobe.vercel.app) |
| OG images rendered on the fly, from HTML/CSS to SVG or PNG | [Satori](https://github.com/vercel/satori) |
| Highlighted code | [shiki](https://shiki.style) |

Add motion for springs, layout animations, exit animations or values driven by a gesture. A hover or a fade needs none of that: use a plain CSS transition.

### Charts

| Need | Pick |
| --- | --- |
| A chart fed by streaming, real-time data | [Liveline](https://github.com/benjitaylor/liveline) |
| Any other chart, static or interactive, dashboards included | [recharts](https://recharts.org) |

Data that arrives live and scrolls the chart along with time goes to Liveline. Every other chart is recharts.

### Interaction and speed

| Need | Pick |
| --- | --- |
| Drag and drop | [dnd kit](https://dndkit.com) |
| Long lists and big tables that need virtualization | [Virtuoso](https://virtuoso.dev) |

### State and classes

| Need | Pick |
| --- | --- |
| Shared state across components | [zustand](https://zustand.docs.pmnd.rs) |
| Conditional `className` strings | [clsx](https://github.com/lukeed/clsx) |
| Typed variants for Tailwind styles | [cva](https://cva.style) |
| Dark mode and theme switching, without a flash on load | [next-themes](https://github.com/pacocoursey/next-themes) |

Use clsx for one-off conditional classes. Use cva for a component with real variants (size, intent, state) that earn a typed API. The two work together: cva takes clsx-style inputs under the hood.

## Mismatches to catch

- **Hand-built toasts, or toasts through a modal library** → Sonner.
- **A dropdown or dialog made of `<div>`s with focus handled by hand** → base-ui. It traps focus, dismisses correctly and gets accessibility right.
- **A number animated by re-rendering its text** → NumberFlow, which transitions each digit.
- **A list of 1.000+ rows rendered in full** → Virtuoso, before any pagination workaround.
- **Shared state passed around as a web of `useState` and props** → zustand.
- **`className` built in a template literal from ternaries nested three deep** → clsx, or cva when the shape is variants.
