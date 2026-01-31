# Glassmorphism Component Specifications

## Core Glass Components

### GlassCard
**Purpose**: Primary container component with frosted glass effect for content display
- **Props**:
  - `children`: ReactNode (required) - Content to display inside the glass card
  - `className`: string (optional) - Additional CSS classes
  - `variant`: 'default' | 'elevated' | 'floating' | 'heavy' | 'light' (optional, default: 'default')
  - `hoverEffect`: boolean (optional, default: false) - Enable hover animations
  - `onClick`: () => void (optional) - Click handler for interactive cards
- **Styling**:
  - Background: `rgba(255, 255, 255, 0.15)` (light mode) / `rgba(30, 30, 46, 0.2)` (dark mode)
  - Backdrop-filter: `blur(12px)`
  - Border: `1px solid rgba(255, 255, 255, 0.18)` (light) / `rgba(255, 255, 255, 0.12)` (dark)
  - Border-radius: `20px`
  - Shadow: `0 8px 32px rgba(31, 38, 135, 0.37)` (default) with variant-specific adjustments
- **Behaviors**:
  - Hover: Elevate and scale effect when `hoverEffect` is true
  - Responsive: Adapts to different screen sizes
  - Accessible: Proper focus management and ARIA attributes

### GlassButton
**Purpose**: Interactive button component with glassmorphism styling
- **Props**:
  - `children`: ReactNode (required) - Button content
  - `variant`: 'primary' | 'secondary' | 'outline' | 'ghost' (optional, default: 'primary')
  - `size`: 'sm' | 'md' | 'lg' (optional, default: 'md')
  - `className`: string (optional) - Additional CSS classes
  - `disabled`: boolean (optional, default: false) - Disable button state
  - `type`: 'button' | 'submit' | 'reset' (optional, default: 'button')
  - `fullWidth`: boolean (optional, default: false) - Full width button
  - `icon`: ReactNode (optional) - Icon to display
  - `iconPosition`: 'left' | 'right' (optional, default: 'left') - Icon placement
- **Styling**:
  - Background: Glass effect with gradient overlay for visibility
  - Backdrop-filter: `blur(4px)`
  - Border: `1px solid rgba(255, 255, 255, 0.18)`
  - Border-radius: `50px` for pill-shaped buttons
  - Padding: Size-dependent (sm: 0.75rem 1.5rem, md: 1rem 2rem, lg: 1.25rem 2.5rem)
- **Behaviors**:
  - Hover: Brightness increase and subtle scale effect
  - Focus: Clear focus ring respecting accessibility
  - Disabled: Reduced opacity and disabled cursor
  - Loading: Appropriate loading state with spinner option

### GlassInput
**Purpose**: Form input component with glassmorphism styling
- **Props**:
  - `label`: string (optional) - Input label
  - `error`: string (optional) - Error message
  - `helperText`: string (optional) - Helper text below input
  - `variant`: 'default' | 'filled' | 'outlined' (optional, default: 'default')
  - `inputSize`: 'sm' | 'md' | 'lg' (optional, default: 'md')
  - `fullWidth`: boolean (optional, default: false) - Full width input
  - `startAdornment`: ReactNode (optional) - Element before input value
  - `endAdornment`: ReactNode (optional) - Element after input value
  - ...InputHTMLAttributes<HTMLInputElement> - All standard input props
- **Styling**:
  - Background: Glass effect with appropriate transparency
  - Backdrop-filter: `blur(4px)`
  - Border: `1px solid rgba(255, 255, 255, 0.18)`
  - Border-radius: `16px`
  - Padding: Size-dependent (sm: 0.75rem 1rem, md: 1rem 1.25rem, lg: 1.25rem 1.5rem)
- **Behaviors**:
  - Focus: Enhanced border and shadow effect
  - Error: Red border and error message display
  - Disabled: Reduced opacity and disabled cursor
  - Adornments: Proper spacing and alignment

## Layout Components

### GlassNavbar
**Purpose**: Navigation bar with glassmorphism styling
- **Props**:
  - `user`: User object (optional) - Current user information
  - `onLogout`: () => void (optional) - Logout handler
  - `className`: string (optional) - Additional CSS classes
- **Styling**:
  - Background: Glass effect with rounded bottom corners
  - Backdrop-filter: `blur(12px)`
  - Border: Bottom border only
  - Padding: Responsive horizontal padding
- **Behaviors**:
  - Responsive: Collapses to hamburger menu on mobile
  - Sticky: Stays at top of viewport during scroll
  - Theme-aware: Adapts to light/dark mode

### GlassSidebar
**Purpose**: Sidebar navigation with glassmorphism styling
- **Props**:
  - `children`: ReactNode (required) - Sidebar content
  - `isOpen`: boolean (required) - Mobile menu state
  - `onClose`: () => void (required) - Close handler
  - `className`: string (optional) - Additional CSS classes
- **Styling**:
  - Background: Glass effect with appropriate transparency
  - Backdrop-filter: `blur(16px)`
  - Width: Responsive (full on mobile, fixed on desktop)
- **Behaviors**:
  - Mobile: Slides in/out with smooth animation
  - Desktop: Always visible with appropriate width
  - Overlay: Applies glass backdrop to main content when open

## Authentication Components

### GlassLoginForm
**Purpose**: Login form with glassmorphism styling
- **Props**:
  - `onLogin`: (email: string, password: string) => Promise<void> (required) - Login handler
  - `onNavigateToSignup`: () => void (optional) - Navigation to signup
  - `loading`: boolean (optional, default: false) - Loading state
  - `onSuccess`: () => void (optional) - Success callback
  - `onError`: (error: any) => void (optional) - Error callback
- **Styling**:
  - Container: Glass card with appropriate padding
  - Form elements: Glass inputs with proper spacing
  - Buttons: Glass buttons with primary accent
- **Behaviors**:
  - Validation: Real-time validation with glass error states
  - Submission: Loading state with glass button
  - Feedback: Glass toast notifications

### GlassSignupForm
**Purpose**: Signup form with glassmorphism styling
- **Props**:
  - `onRegister`: (name: string, email: string, password: string) => Promise<void> (required) - Registration handler
  - `onNavigateToLogin`: () => void (optional) - Navigation to login
  - `loading`: boolean (optional, default: false) - Loading state
  - `onSuccess`: () => void (optional) - Success callback
  - `onError`: () => void (optional) - Error callback
- **Styling**:
  - Container: Glass card with appropriate padding
  - Form elements: Glass inputs with proper spacing
  - Buttons: Glass buttons with primary accent
- **Behaviors**:
  - Validation: Real-time validation with glass error states
  - Password strength: Visual indicator with glass styling
  - Terms agreement: Glass-styled checkbox

## Dashboard Components

### GlassStatisticsCards
**Purpose**: Dashboard statistics cards with glassmorphism styling
- **Props**:
  - `totalTasks`: number (required) - Total task count
  - `completedTasks`: number (required) - Completed task count
  - `pendingTasks`: number (required) - Pending task count
  - `overdueTasks`: number (required) - Overdue task count
  - `className`: string (optional) - Additional CSS classes
- **Styling**:
  - Individual cards: Glass cards with appropriate sizing
  - Icons: Gradient icons with glass effect
  - Numbers: Large, readable text with appropriate contrast
- **Behaviors**:
  - Hover: Subtle elevation effect
  - Responsive: Adapts grid layout based on screen size
  - Animations: Count-up animations for numbers

### GlassTaskCard
**Purpose**: Individual task display with glassmorphism styling
- **Props**:
  - `task`: Task object (required) - Task data to display
  - `onToggle`: (taskId: string) => void (required) - Toggle completion
  - `onEdit`: (taskId: string) => void (required) - Edit handler
  - `onDelete`: (taskId: string) => void (required) - Delete handler
  - `showPriorityIndicator`: boolean (optional, default: false) - Show priority
  - `showDueDate`: boolean (optional, default: false) - Show due date
- **Styling**:
  - Container: Glass card with appropriate padding
  - Priority indicators: Colored badges with glass effect
  - Due dates: Subtle text with appropriate styling
- **Behaviors**:
  - Hover: Subtle elevation and scale effect
  - Completion: Visual indication with checkmark animation
  - Priority: Color-coded indicators with appropriate contrast

## Theme Components

### GlassThemeToggle
**Purpose**: Theme switching component with glassmorphism styling
- **Props**:
  - `currentTheme`: 'light' | 'dark' (required) - Current theme
  - `onToggle`: () => void (required) - Theme toggle handler
  - `showLabel`: boolean (optional, default: true) - Show theme label
- **Styling**:
  - Container: Small glass button with theme icon
  - Icons: Sun/moon icons with appropriate styling
  - Animation: Smooth transition between themes
- **Behaviors**:
  - Toggle: Switches between light and dark modes
  - Persistence: Remembers user preference in localStorage
  - Animation: Smooth transition between theme states

### GlassThemeProvider
**Purpose**: Theme context provider for glassmorphism UI
- **Props**:
  - `children`: ReactNode (required) - Child components to wrap
- **Functionality**:
  - Manages theme state (light/dark)
  - Applies theme classes to document
  - Persists theme preference
  - Provides theme context to child components

## Utility Components

### GlassModal
**Purpose**: Modal dialog with glassmorphism styling
- **Props**:
  - `isOpen`: boolean (required) - Modal visibility
  - `children`: ReactNode (required) - Modal content
  - `onClose`: () => void (required) - Close handler
  - `title`: string (optional) - Modal title
  - `size`: 'sm' | 'md' | 'lg' | 'xl' (optional, default: 'md') - Modal size
- **Styling**:
  - Backdrop: Semi-transparent overlay with blur effect
  - Content: Glass card with appropriate sizing
  - Close button: Glass-styled close button
- **Behaviors**:
  - Entrance: Scale and fade animation
  - Exit: Reverse animation
  - Close: Click outside or ESC key
  - Focus: Trap focus within modal

### GlassToast
**Purpose**: Toast notifications with glassmorphism styling
- **Props**:
  - `message`: string (required) - Notification message
  - `type`: 'success' | 'error' | 'warning' | 'info' (required) - Message type
  - `duration`: number (optional, default: 3000) - Display duration
  - `position`: 'top-right' | 'bottom-right' | 'top-center' | 'bottom-center' (optional, default: 'top-right') - Position
- **Styling**:
  - Container: Small glass card with appropriate padding
  - Icon: Type-specific icon with glass styling
  - Text: Readable text with appropriate contrast
- **Behaviors**:
  - Auto-dismiss: Automatically hides after duration
  - Manual dismiss: Close button for immediate dismissal
  - Stacking: Multiple toasts stack appropriately
  - Animation: Slide-in and slide-out animations

## Animation Components

### GlassAnimatedBackground
**Purpose**: Animated background with ambient blobs for glassmorphism depth
- **Props**:
  - `children`: ReactNode (required) - Content to overlay
  - `blobCount`: number (optional, default: 2) - Number of background blobs
  - `blobPositions`: Array of positions (optional) - Specific blob positions
- **Styling**:
  - Background: Gradient background with radial blur effects
  - Blobs: Large, soft, blurred circles in corner positions
  - Animation: Subtle floating animation for depth
- **Behaviors**:
  - Performance: Respects `prefers-reduced-motion` setting
  - Responsiveness: Adapts to different screen sizes
  - Efficiency: Optimized for smooth animation performance