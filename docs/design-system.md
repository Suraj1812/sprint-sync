# SprintSync Design System

## Philosophy

The design system is the single visual source of truth for SprintSync. Every component, layout, and interaction derives from shared tokens. No page hardcodes colors, spacing, typography, shadows, or radius values.

It is built on:

- **Radix UI** for accessible, keyboard-navigable primitives.
- **Tailwind CSS** with design-token variables.
- **Framer Motion** for purposeful, reduced-motion-safe animation.
- **next-themes** for light, dark, and system-aware theming.

## Tokens

CSS variables in `packages/ui/styles/theme.css` define the visual language. They automatically change when `.dark` is applied to the `<html>` element.

Key token categories:

- **Background/surface:** `background`, `card`, `popover`, `surface`, `overlay`.
- **Interactive:** `primary`, `secondary`, `accent`, `muted`.
- **Semantic:** `success`, `warning`, `info`, `destructive`.
- **Border and input:** `border`, `input`, `ring`.
- **Radii:** `radius`.

These map to Tailwind utilities: `bg-primary`, `text-muted-foreground`, `border-destructive`, `shadow-card`, etc.

## Typography

- **Primary font:** Inter via `next/font/google` (`--font-sans`). Chosen for high legibility and a neutral, modern feel across dashboards and forms.
- **Code font:** JetBrains Mono via `next/font/google` (`--font-mono`). Clear distinction for code and data.
- **Scale:** Custom `fontSize` tokens: `display`, `hero`, `h1-h6`, `body`, `body-sm`, `caption`, `overline`. All tokens use tight tracking for headings and relaxed leading for body text.

## Spacing, grid, and radius

- **8px logical grid:** Tailwind spacing is based on `0.25rem` (4px), so `p-2` is 8px, `p-4` is 16px, and so on.
- **Container sizes:** Centered container with `1400px` max width.
- **Breakpoints:** `xs` 320px, `sm` 375px, `md` 768px, `lg` 1024px, `xl` 1440px, `2xl` 1920px, `uw` 2560px.
- **Radius tokens:** `sm`, `md`, `lg`, `xl`, `2xl`, `pill`, `circle`.

## Elevation

Shadows are tokenized: `shadow-surface`, `shadow-card`, `shadow-dropdown`, `shadow-modal`, `shadow-floating`. They use subtle black alphas and are the same in light and dark mode so hierarchy is preserved.

## Components

Components live in `packages/ui/src/components/` and are exported from `packages/ui/src/index.ts`.

Implemented primitives include:

- Form: `Button`, `Input`, `Textarea`, `Label`, `Checkbox`, `Switch`, `RadioGroup`, `Select`.
- Surface: `Card`, `CardHeader`, `CardTitle`, `CardDescription`, `CardContent`, `CardFooter`.
- Feedback: `Alert`, `Badge`, `Skeleton`, `Spinner`.
- Overlay: `Dialog`, `Sheet`, `Popover`, `Tooltip`, `DropdownMenu`.
- Navigation: `Tabs`, `Accordion`, `Breadcrumb`, `Separator`.
- Media: `Avatar`.

Each component uses the shared `cn` utility and the Tailwind token classes. They support `cva` variants for `variant`, `size`, and `className` overrides.

## Usage example

```tsx
import { Button, Input, Card, CardHeader, CardTitle, CardContent } from "@sprint-sync/ui"

export default function Example() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Welcome</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <Input placeholder="Email" />
        <Button variant="default" size="lg">Continue</Button>
      </CardContent>
    </Card>
  )
}
```

## Theming

The `ThemeProvider` in `apps/web/app/providers.tsx` handles `light`, `dark`, and `system`. Tailwind `darkMode: "class"` causes `.dark` to toggle the token values. Theme preference is stored client-side and transitions are smooth.

## Accessibility

- All Radix primitives manage focus, ARIA attributes, and keyboard navigation.
- Every interactive element has a visible focus ring (`ring-ring`).
- Colors are chosen for WCAG AA contrast in both themes.
- Motion is gated by `prefers-reduced-motion` in the animation utilities.
