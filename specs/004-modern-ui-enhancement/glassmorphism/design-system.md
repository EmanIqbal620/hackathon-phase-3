# Glassmorphism Design System

## Glassmorphism Variables

### Base Glass Properties
- **Transparency**: `rgba(255, 255, 255, 0.15)` (light mode), `rgba(30, 30, 46, 0.2)` (dark mode)
- **Blur Amount**: `backdrop-filter: blur(12px)` (standard), `blur(16px)` (enhanced)
- **Border**: `1px solid rgba(255, 255, 255, 0.18)` (light), `rgba(255, 255, 255, 0.12)` (dark)
- **Shadow**: `0 8px 32px rgba(31, 38, 135, 0.37)` (standard), `0 12px 32px rgba(31, 38, 135, 0.25)` (lighter)

### Glass Variants
- **Standard Glass**: Default transparency and blur for most components
- **Heavy Glass**: Higher transparency (`0.25`) and more blur (`20px`) for emphasis
- **Light Glass**: Lower transparency (`0.08`) and less blur (`10px`) for subtle effects
- **Floating Glass**: Additional lift effect with hover animations

## Color Palette for Glassmorphism

### Glass-Specific Colors
- **Glass Background Light**: `rgba(255, 255, 255, 0.15)`
- **Glass Background Dark**: `rgba(30, 30, 46, 0.2)`
- **Glass Border Light**: `rgba(255, 255, 255, 0.18)`
- **Glass Border Dark**: `rgba(255, 255, 255, 0.12)`
- **Glass Shadow**: `rgba(31, 38, 135, 0.37)` with varying opacity

### Supporting Colors
- **Text on Glass Light**: `rgba(0, 0, 0, 0.9)` (high contrast)
- **Text on Glass Dark**: `rgba(255, 255, 255, 0.9)` (high contrast)
- **Glass Button Primary**: Gradient overlay on glass background
- **Glass Button Secondary**: Subtle contrast with glass background

## Typography in Glass Context

### Text Readability
- **Minimum Contrast Ratio**: 4.5:1 against glass backgrounds
- **Font Weight**: Medium to semi-bold (500-600) for better readability
- **Font Size**: Maintain standard sizes, ensure legibility over varied backgrounds
- **Line Height**: Slightly increased (1.5-1.6) for better readability

### Text Styling
- **Text Shadows**: Subtle drop shadows on light text over glass for readability
- **Emphasis**: Use background highlights sparingly to avoid competing with glass effect
- **Links**: Maintain clear visual distinction with appropriate underlines or styling

## Layout Principles

### Spacing
- **Padding**: Generous padding (1.5rem standard) to emphasize glass containment
- **Margins**: Consistent margins to establish clear visual hierarchy
- **Gaps**: Appropriate spacing between glass elements to avoid visual clutter

### Hierarchy
- **Depth Levels**: Use different glass intensities to establish visual hierarchy
- **Layering**: Glass components should feel like they exist in 3D space
- **Focus**: Ensure glass elements have clear visual focus states

## Component Specifications

### GlassCard
- **Background**: Standard glass properties
- **Padding**: 1.5rem (24px)
- **Border Radius**: 20px for rounded appearance
- **Shadow**: Subtle drop shadow for depth
- **Hover Effect**: Slight elevation and scale transform
- **Variants**: Standard, elevated, floating, heavy, light

### GlassButton
- **Background**: Glass with gradient overlay for visibility
- **Border**: Subtle border to define shape
- **Padding**: Adequate for touch targets (min 44px)
- **Hover**: Slight brightness increase and scale effect
- **Focus**: Clear focus ring respecting accessibility

### GlassInput
- **Background**: Glass effect with appropriate transparency
- **Border**: Subtle border with focus state
- **Padding**: Comfortable for text input
- **Focus**: Clear indication with glow effect
- **States**: Normal, focus, error, disabled with consistent glass styling

### GlassModal
- **Backdrop**: Semi-transparent overlay with blur effect
- **Content**: Glass card with appropriate sizing
- **Animation**: Smooth entrance/exit with scale and fade
- **Close**: Clear, accessible close mechanism

## Interaction Patterns

### Hover States
- **Subtle**: Gentle brightness increase or scale effect
- **Consistent**: Uniform hover behavior across all glass elements
- **Performance**: Hardware-accelerated transforms for smooth animation

### Focus States
- **Clear**: Visible focus indicators for accessibility
- **Respectful**: Respect `prefers-reduced-motion` setting
- **Accessible**: Meet WCAG 2.1 AA standards for focus visibility

### Loading States
- **Skeleton**: Glass-styled skeleton loaders
- **Progress**: Subtle progress indicators with glass aesthetic
- **Feedback**: Clear loading states without disrupting glass effect

## Responsive Considerations

### Mobile
- **Touch Targets**: Minimum 44px for accessibility
- **Performance**: Potentially reduced glass effects on lower-end devices
- **Spacing**: Increased spacing for touch-friendly interactions

### Tablet
- **Adaptation**: Adjust glass effects for intermediate screen sizes
- **Touch Integration**: Maintain touch-friendly interactions

### Desktop
- **Full Effects**: Full glass effects with performance optimization
- **Mouse Interactions**: Rich hover states and subtle animations

## Accessibility Guidelines

### Color Contrast
- **Minimum Ratio**: 4.5:1 for normal text, 3:1 for large text
- **Testing**: Verify contrast over various background images
- **Fallbacks**: Maintain contrast when glass effect is not supported

### Focus Management
- **Visibility**: Clear focus indicators that work over glass
- **Navigation**: Logical tab order with glass components
- **Announcements**: Proper ARIA labels and announcements

### Motion Sensitivity
- **Respects**: `prefers-reduced-motion` media query
- **Options**: Potentially provide motion reduction settings
- **Performance**: Ensure animations don't cause jank or performance issues

## Performance Guidelines

### Rendering Optimization
- **Layers**: Promote glass elements to separate layers where beneficial
- **Complexity**: Limit nested glass effects to prevent performance issues
- **Animations**: Use hardware-accelerated properties for smooth animations

### Resource Management
- **Images**: Optimize background images to complement glass effects
- **Shadows**: Use efficient shadow implementations
- **Filters**: Monitor performance impact of backdrop filters

### Device Adaptation
- **Detection**: Potentially detect device capabilities and adjust effects
- **Fallbacks**: Provide performance-appropriate alternatives
- **Settings**: Allow users to adjust visual effects based on preference/performance