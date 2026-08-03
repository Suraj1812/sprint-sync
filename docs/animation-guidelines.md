# Animation Guidelines

## Principles

- **Purposeful:** animations guide attention, confirm actions, or reveal state changes.
- **Fast:** most transitions use 150–300ms to feel responsive.
- **Reduced-motion first:** all helpers check `prefers-reduced-motion` and disable movement when requested.
- **Consistent:** use the same easing and durations across the application.

## Presets

`packages/ui/src/lib/animation.ts` exports:

- `fadeIn` — simple opacity reveal.
- `fadeInUp` / `fadeInDown` — opacity + vertical slide.
- `scaleIn` — opacity + slight scale.
- `slideInFromBottom` — entrance for modals and sheets.
- `staggerContainer` — parent container that staggers children.
- `spring` — spring transition for micro-interactions.
- `hoverScale` / `tapScale` — gesture states.

## Durations

```ts
const duration = {
  fast: 0.15,
  normal: 0.2,
  slow: 0.3,
  slower: 0.4,
}
```

## Usage

```tsx
import { motion } from "framer-motion"
import { fadeInUp, spring } from "@sprint-sync/ui"

<motion.div
  initial="hidden"
  animate="visible"
  variants={fadeInUp}
  transition={spring}
>
  Content
</motion.div>
```

## Component-level animation

- `Dialog`, `Sheet`, and `DropdownMenu` use Radix built-in `animate-in`/`animate-out` helpers combined with the shadow/overlay token.
- `Accordion` uses `data-[state=open]:animate-accordion-down` and `data-[state=closed]:animate-accordion-up`.
- `Skeleton` uses `animate-pulse`.
- `Spinner` uses `animate-spin`.

## Reduced motion

Components must not animate if `prefers-reduced-motion: reduce` is active. Framer Motion `useReducedMotion` or the `getReducedMotion` helper should gate `y`/`scale` transforms.
