# Data Model: Theme Configuration

## Theme Configuration Entity
Represents the design token system that manages color palettes, typography, and styling properties for both light and dark modes

**Fields**:
- `mode`: string (light | dark) - Current theme mode
- `colors`: object - Color palette containing primary, secondary, background, surface, border, and text colors
- `spacing`: object - Spacing scale for consistent padding and margin
- `typography`: object - Font sizes, weights, and line heights
- `borderRadius`: object - Border radius scale for consistent rounded corners
- `shadows`: object - Shadow definitions for depth and elevation
- `transitions`: object - Animation timing and easing functions

**Validation Rules**:
- `mode` must be either 'light' or 'dark'
- All color values must be valid CSS color formats (hex, rgb, hsl)
- All spacing values must be valid CSS units
- Contrast ratios must meet WCAG AA standards (4.5:1 for normal text)

## UI Component Entity
Represents the visual elements that implement the specified design rules and behaviors

**Fields**:
- `componentType`: string (card, button, modal, form, etc.) - Type of UI component
- `themeStyles`: object - Styles applied based on current theme
- `hoverEffects`: object - Subtle hover animations and transformations
- `animationProps`: object - Animation configurations for entrance and interaction

**Validation Rules**:
- All components must support both light and dark themes
- Hover effects must be subtle and predictable (no harsh transitions)
- Animations must not impact performance (maintain 60fps)

## Animation System Entity
Represents the smooth transition and animation behaviors that enhance user interactions

**Fields**:
- `animationType`: string (fade-up, translate, scale, modal-open, etc.) - Type of animation
- `duration`: number - Duration of animation in milliseconds
- `easing`: string - Easing function for smooth transitions
- `trigger`: string (load, hover, click, etc.) - Event that triggers animation

**Validation Rules**:
- Animation durations must be optimized for performance
- Easing functions must create smooth, natural transitions
- All animations must respect user's reduced motion preferences