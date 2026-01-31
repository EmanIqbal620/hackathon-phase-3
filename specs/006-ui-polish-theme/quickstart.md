# Quickstart Guide: UI Polish & Theme Enhancement

## Setup

1. Ensure you're on the `006-ui-polish-theme` branch
2. Install dependencies if not already done: `npm install` or `yarn install`

## Theme Configuration

The theme system is configured using Tailwind CSS with custom extensions. The theme configuration is located in `frontend/src/styles/theme.ts`.

```typescript
export const themeConfig = {
  colors: {
    primary: '#0D0E0E', // Primary background
    accent: '#4B0076',  // Accent purple
    // Additional theme colors...
  },
  // Other theme properties...
};
```

## Applying Themes

To apply themes in your components:

1. Use Tailwind classes that reference the theme: `bg-primary`, `text-accent`
2. For dynamic theming, use the `useTheme` hook: `const { theme, toggleTheme } = useTheme();`
3. Wrap your application with the `ThemeProvider` in `app/layout.tsx`

## Adding Animations

Animations are implemented using Framer Motion:

```jsx
import { motion } from 'framer-motion';

<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
  {/* Animated content */}
</motion.div>
```

## Component Styling

All UI components should follow the design system:

- Use matte backgrounds: `bg-surface` instead of transparent/glass
- Apply soft rounded corners: `rounded-lg` or `rounded-xl`
- Use subtle borders: `border border-border-light`
- Implement hover effects with subtle transforms: `hover:scale-[1.02]`

## Background Accents

Partial matrix-style line accents can be added to decorative sections using the `MatrixLines` component:

```jsx
import { MatrixLines } from '@/components/ui/MatrixLines';

<div className="relative">
  <MatrixLines />
  {/* Other content */}
</div>
```

## Testing

- Verify theme switching works: Toggle between light and dark modes
- Check all animations: Ensure they are smooth and subtle
- Validate accessibility: Confirm contrast ratios meet WCAG AA standards
- Test responsive design: Ensure UI looks good on all device sizes