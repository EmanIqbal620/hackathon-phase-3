# UI/UX Design Skill

## Overview
Designs responsive and user-friendly UI for applications with focus on accessibility, usability, and visual consistency.

## Description
The UI/UX Design skill is responsible for creating intuitive, accessible, and visually appealing user interfaces that provide excellent user experiences across all devices. It defines design systems, component patterns, responsive layouts, accessibility standards, and ensures consistency with project design principles and Spec 0 Constitution rules.

## Components

### 1. Responsive Layout for Desktop and Mobile
**Responsive Design Strategy**:
- Mobile-first approach (design for mobile, enhance for desktop)
- Fluid layouts with flexible grids
- Breakpoints for different screen sizes
- Touch-friendly targets (minimum 44x44px)
- Adaptive images and media
- Progressive enhancement

**Breakpoint System**:
```css
/* Mobile First Breakpoints */
/* Mobile: 320px - 639px (default) */
/* Tablet: 640px - 1023px */
@media (min-width: 640px) { /* sm */ }

/* Desktop: 1024px - 1279px */
@media (min-width: 1024px) { /* md */ }

/* Large Desktop: 1280px - 1535px */
@media (min-width: 1280px) { /* lg */ }

/* Extra Large: 1536px+ */
@media (min-width: 1536px) { /* xl */ }
```

**Layout Patterns**:

**Mobile Layout** (< 640px):
```
┌─────────────────┐
│     Header      │
├─────────────────┤
│                 │
│   Task Form     │
│   (Stacked)     │
│                 │
├─────────────────┤
│   Task Item 1   │
├─────────────────┤
│   Task Item 2   │
├─────────────────┤
│   Task Item 3   │
└─────────────────┘
```

**Tablet Layout** (640px - 1023px):
```
┌───────────────────────────┐
│         Header            │
├───────────────────────────┤
│                           │
│   Task Form (2 columns)   │
│                           │
├───────────────────────────┤
│   Task Item 1             │
├───────────────────────────┤
│   Task Item 2             │
└───────────────────────────┘
```

**Desktop Layout** (1024px+):
```
┌─────────────────────────────────────┐
│            Header                   │
├──────────────┬──────────────────────┤
│   Sidebar    │   Task Form          │
│   (Filters)  │                      │
│              ├──────────────────────┤
│              │   Task Grid          │
│              │   [Item] [Item]      │
│              │   [Item] [Item]      │
└──────────────┴──────────────────────┘
```

**Responsive Techniques**:
- CSS Grid and Flexbox for layouts
- Relative units (rem, em, %, vw, vh)
- Container queries for component-level responsiveness
- CSS clamp() for fluid typography
- Media queries for breakpoint-specific styles
- Viewport meta tag for mobile optimization

### 2. Clean and Accessible Component Design
**Accessibility Standards (WCAG 2.1 Level AA)**:

**Visual Accessibility**:
- Color contrast ratio ≥ 4.5:1 for normal text
- Color contrast ratio ≥ 3:1 for large text (18px+)
- Don't rely on color alone to convey information
- Clear focus indicators (outline, border, shadow)
- Sufficient font sizes (16px minimum for body text)
- Line height 1.5+ for readability
- Adequate white space and padding

**Semantic HTML**:
```html
<!-- Good: Semantic and accessible -->
<header>
  <nav aria-label="Main navigation">
    <ul>
      <li><a href="/tasks">Tasks</a></li>
    </ul>
  </nav>
</header>

<main>
  <h1>My Tasks</h1>
  <form aria-label="Create new task">
    <label for="task-title">Task Title</label>
    <input id="task-title" type="text" required />
    <button type="submit">Create Task</button>
  </form>

  <section aria-label="Task list">
    <article>
      <h2>Buy groceries</h2>
      <p>Milk, eggs, bread</p>
    </article>
  </section>
</main>

<!-- Bad: Non-semantic -->
<div class="header">
  <div class="nav">
    <div class="link">Tasks</div>
  </div>
</div>
```

**ARIA Labels and Roles**:
```html
<!-- Form controls -->
<input
  type="text"
  id="task-title"
  aria-label="Task title"
  aria-required="true"
  aria-invalid="false"
  aria-describedby="title-error"
/>
<span id="title-error" role="alert" aria-live="polite">
  Title is required
</span>

<!-- Interactive elements -->
<button
  aria-label="Delete task"
  aria-describedby="delete-tooltip"
>
  <TrashIcon aria-hidden="true" />
</button>

<!-- Status updates -->
<div role="status" aria-live="polite" aria-atomic="true">
  Task created successfully
</div>

<!-- Loading state -->
<div role="progressbar" aria-label="Loading tasks" aria-busy="true">
  <span className="sr-only">Loading...</span>
</div>
```

**Keyboard Navigation**:
- All interactive elements accessible via Tab key
- Enter/Space to activate buttons
- Escape to close modals/dropdowns
- Arrow keys for lists and menus
- Tab order follows visual order
- Skip links for main content
- Focus trap in modals

**Screen Reader Support**:
- Descriptive alt text for images
- ARIA labels for icon buttons
- Status messages with aria-live
- Hidden labels with sr-only class
- Proper heading hierarchy (h1 → h2 → h3)
- Landmark regions (header, nav, main, footer)

**Component Accessibility Checklist**:
- [ ] Semantic HTML elements used
- [ ] ARIA labels where needed
- [ ] Keyboard accessible
- [ ] Focus indicators visible
- [ ] Color contrast meets WCAG AA
- [ ] Screen reader tested
- [ ] Touch targets ≥ 44x44px
- [ ] Form labels associated with inputs
- [ ] Error messages announced to screen readers
- [ ] Loading states announced

### 3. Consistent UI with Spec 0 Rules
**Design System Principles**:

**Color Palette**:
```css
/* Primary Colors */
--color-primary-50: #eff6ff;
--color-primary-100: #dbeafe;
--color-primary-500: #3b82f6;  /* Primary blue */
--color-primary-600: #2563eb;
--color-primary-700: #1d4ed8;

/* Neutral Colors */
--color-gray-50: #f9fafb;
--color-gray-100: #f3f4f6;
--color-gray-500: #6b7280;
--color-gray-700: #374151;
--color-gray-900: #111827;

/* Semantic Colors */
--color-success: #10b981;  /* Green */
--color-warning: #f59e0b;  /* Amber */
--color-error: #ef4444;    /* Red */
--color-info: #3b82f6;     /* Blue */

/* Background & Text */
--color-bg-primary: #ffffff;
--color-bg-secondary: #f9fafb;
--color-text-primary: #111827;
--color-text-secondary: #6b7280;
```

**Typography Scale**:
```css
/* Font Families */
--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'Fira Code', Consolas, Monaco, monospace;

/* Font Sizes (using fluid typography) */
--text-xs: clamp(0.75rem, 0.7rem + 0.25vw, 0.875rem);    /* 12-14px */
--text-sm: clamp(0.875rem, 0.8rem + 0.375vw, 1rem);       /* 14-16px */
--text-base: clamp(1rem, 0.95rem + 0.25vw, 1.125rem);     /* 16-18px */
--text-lg: clamp(1.125rem, 1.05rem + 0.375vw, 1.25rem);   /* 18-20px */
--text-xl: clamp(1.25rem, 1.15rem + 0.5vw, 1.5rem);       /* 20-24px */
--text-2xl: clamp(1.5rem, 1.35rem + 0.75vw, 1.875rem);    /* 24-30px */
--text-3xl: clamp(1.875rem, 1.65rem + 1.125vw, 2.25rem);  /* 30-36px */

/* Font Weights */
--font-normal: 400;
--font-medium: 500;
--font-semibold: 600;
--font-bold: 700;

/* Line Heights */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.75;
```

**Spacing Scale** (based on 4px grid):
```css
--space-0: 0;
--space-1: 0.25rem;  /* 4px */
--space-2: 0.5rem;   /* 8px */
--space-3: 0.75rem;  /* 12px */
--space-4: 1rem;     /* 16px */
--space-5: 1.25rem;  /* 20px */
--space-6: 1.5rem;   /* 24px */
--space-8: 2rem;     /* 32px */
--space-10: 2.5rem;  /* 40px */
--space-12: 3rem;    /* 48px */
--space-16: 4rem;    /* 64px */
--space-20: 5rem;    /* 80px */
```

**Border Radius**:
```css
--radius-none: 0;
--radius-sm: 0.125rem;   /* 2px */
--radius-base: 0.25rem;  /* 4px */
--radius-md: 0.375rem;   /* 6px */
--radius-lg: 0.5rem;     /* 8px */
--radius-xl: 0.75rem;    /* 12px */
--radius-2xl: 1rem;      /* 16px */
--radius-full: 9999px;   /* Pill shape */
```

**Shadows**:
```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
```

**Component Consistency Rules**:
1. **Buttons**: Same padding, border-radius, hover states
2. **Inputs**: Consistent height, border, focus states
3. **Cards**: Uniform padding, shadows, borders
4. **Spacing**: Follow 4px grid system
5. **Icons**: Same size within context (16px, 20px, 24px)
6. **Typography**: Limited to defined scale
7. **Colors**: Use design tokens, not hardcoded values

## Reusability
**Yes** - This skill can be reused across frontend projects requiring:
- Responsive web design
- Accessible user interfaces
- Design system implementation
- Component library development
- Multi-device support

## Usage

### Called By
- Main Agent (for UI/UX planning)
- Frontend Engineer Sub-Agent (for implementation)
- Product Designer (for design specifications)

### When to Invoke
1. **Project Initialization**: Establishing design system
2. **Feature Design**: Creating UI mockups and specifications
3. **Component Development**: Implementing reusable components
4. **Accessibility Audit**: Reviewing WCAG compliance
5. **Responsive Testing**: Ensuring multi-device support

### Example Invocations
```bash
# Create design system
/ui-ux design-system

# Design specific component
/ui-ux component --name TaskCard

# Generate responsive layout
/ui-ux layout --page tasks

# Audit accessibility
/ui-ux a11y-audit

# Create style guide
/ui-ux style-guide
```

## Outputs

### Primary Artifacts
1. Design system documentation
2. Component specifications
3. Style guide (colors, typography, spacing)
4. Responsive layout designs
5. Accessibility guidelines

### Secondary Outputs
- Figma/design mockups (if applicable)
- CSS/Tailwind configuration
- Component Storybook stories
- Accessibility test results
- Responsive breakpoint documentation

## Design System Implementation

### Global CSS Variables (`styles/design-tokens.css`)
```css
:root {
  /* Colors */
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-primary-active: #1d4ed8;

  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
  --color-info: #3b82f6;

  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f9fafb;
  --color-bg-tertiary: #f3f4f6;

  --color-text-primary: #111827;
  --color-text-secondary: #6b7280;
  --color-text-tertiary: #9ca3af;

  --color-border: #e5e7eb;
  --color-border-focus: #3b82f6;

  /* Typography */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'Fira Code', monospace;

  --text-xs: 0.75rem;      /* 12px */
  --text-sm: 0.875rem;     /* 14px */
  --text-base: 1rem;       /* 16px */
  --text-lg: 1.125rem;     /* 18px */
  --text-xl: 1.25rem;      /* 20px */
  --text-2xl: 1.5rem;      /* 24px */
  --text-3xl: 1.875rem;    /* 30px */
  --text-4xl: 2.25rem;     /* 36px */

  --font-normal: 400;
  --font-medium: 500;
  --font-semibold: 600;
  --font-bold: 700;

  --leading-tight: 1.25;
  --leading-normal: 1.5;
  --leading-relaxed: 1.75;

  /* Spacing (4px grid) */
  --space-1: 0.25rem;   /* 4px */
  --space-2: 0.5rem;    /* 8px */
  --space-3: 0.75rem;   /* 12px */
  --space-4: 1rem;      /* 16px */
  --space-5: 1.25rem;   /* 20px */
  --space-6: 1.5rem;    /* 24px */
  --space-8: 2rem;      /* 32px */
  --space-10: 2.5rem;   /* 40px */
  --space-12: 3rem;     /* 48px */
  --space-16: 4rem;     /* 64px */

  /* Border Radius */
  --radius-sm: 0.125rem;  /* 2px */
  --radius-base: 0.25rem; /* 4px */
  --radius-md: 0.375rem;  /* 6px */
  --radius-lg: 0.5rem;    /* 8px */
  --radius-xl: 0.75rem;   /* 12px */
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);

  /* Transitions */
  --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-base: 200ms cubic-bezier(0.4, 0, 0.2, 1);
  --transition-slow: 300ms cubic-bezier(0.4, 0, 0.2, 1);

  /* Z-index scale */
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-popover: 1060;
  --z-tooltip: 1070;
}

/* Dark mode (optional) */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-primary: #111827;
    --color-bg-secondary: #1f2937;
    --color-bg-tertiary: #374151;

    --color-text-primary: #f9fafb;
    --color-text-secondary: #d1d5db;
    --color-text-tertiary: #9ca3af;

    --color-border: #374151;
  }
}
```

### Tailwind Configuration (`tailwind.config.js`)
```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['Fira Code', 'monospace'],
      },
      fontSize: {
        xs: ['0.75rem', { lineHeight: '1rem' }],
        sm: ['0.875rem', { lineHeight: '1.25rem' }],
        base: ['1rem', { lineHeight: '1.5rem' }],
        lg: ['1.125rem', { lineHeight: '1.75rem' }],
        xl: ['1.25rem', { lineHeight: '1.75rem' }],
        '2xl': ['1.5rem', { lineHeight: '2rem' }],
        '3xl': ['1.875rem', { lineHeight: '2.25rem' }],
        '4xl': ['2.25rem', { lineHeight: '2.5rem' }],
      },
      spacing: {
        '18': '4.5rem',
        '88': '22rem',
        '128': '32rem',
      },
      animation: {
        'fade-in': 'fadeIn 200ms ease-in',
        'fade-out': 'fadeOut 200ms ease-out',
        'slide-in': 'slideIn 200ms ease-out',
        'slide-out': 'slideOut 200ms ease-in',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        fadeOut: {
          '0%': { opacity: '1' },
          '100%': { opacity: '0' },
        },
        slideIn: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideOut: {
          '0%': { transform: 'translateY(0)', opacity: '1' },
          '100%': { transform: 'translateY(-10px)', opacity: '0' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
```

### Base Component Styles (`components/ui/Button.tsx`)
```typescript
import { ButtonHTMLAttributes, forwardRef } from 'react'
import { cva, type VariantProps } from 'class-variance-authority'

const buttonVariants = cva(
  // Base styles
  'inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50',
  {
    variants: {
      variant: {
        primary: 'bg-primary-600 text-white hover:bg-primary-700 focus-visible:ring-primary-600',
        secondary: 'bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-500',
        outline: 'border border-gray-300 bg-white hover:bg-gray-50 focus-visible:ring-gray-500',
        ghost: 'hover:bg-gray-100 hover:text-gray-900 focus-visible:ring-gray-500',
        danger: 'bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-600',
      },
      size: {
        sm: 'h-9 px-3 text-sm',
        md: 'h-10 px-4 text-base',
        lg: 'h-11 px-6 text-lg',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'primary',
      size: 'md',
    },
  }
)

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, isLoading, children, disabled, ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={buttonVariants({ variant, size, className })}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <>
            <span className="mr-2 h-4 w-4 animate-spin rounded-full border-2 border-current border-t-transparent" />
            Loading...
          </>
        ) : (
          children
        )}
      </button>
    )
  }
)

Button.displayName = 'Button'

export { Button, buttonVariants }
```

### Responsive Layout Example (`app/tasks/page.tsx`)
```typescript
export default function TasksPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header - Full width on all devices */}
      <header className="sticky top-0 z-10 bg-white border-b border-gray-200">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <h1 className="text-xl sm:text-2xl font-bold">My Tasks</h1>
            <button className="md:hidden">Menu</button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 sm:px-6 lg:px-8 py-6 lg:py-8">
        {/* Mobile: Single column */}
        {/* Tablet: Single column with more padding */}
        {/* Desktop: Sidebar + Content */}
        <div className="grid grid-cols-1 lg:grid-cols-[280px_1fr] gap-6 lg:gap-8">
          {/* Sidebar - Hidden on mobile, visible on desktop */}
          <aside className="hidden lg:block">
            <div className="sticky top-24 space-y-4">
              <TaskFilters />
              <TaskStats />
            </div>
          </aside>

          {/* Content Area */}
          <div className="space-y-6">
            {/* Task Form - Full width on mobile, constrained on desktop */}
            <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6">
              <h2 className="text-lg sm:text-xl font-semibold mb-4">
                Create New Task
              </h2>
              <TaskForm />
            </div>

            {/* Task List - Responsive grid */}
            <div className="space-y-3">
              <h2 className="text-lg sm:text-xl font-semibold">
                Your Tasks
              </h2>
              {/* Mobile: 1 column, Tablet: 1 column, Desktop: 1-2 columns */}
              <div className="grid grid-cols-1 xl:grid-cols-2 gap-3">
                {tasks.map((task) => (
                  <TaskCard key={task.id} task={task} />
                ))}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
```

## UI/UX Best Practices

### Visual Design
1. **Whitespace**: Use generous spacing for clarity
2. **Hierarchy**: Clear visual hierarchy with size, weight, color
3. **Contrast**: Ensure readability with proper contrast ratios
4. **Consistency**: Use design system tokens consistently
5. **Feedback**: Provide immediate visual feedback for actions
6. **Progressive Disclosure**: Show only what's needed
7. **Error Prevention**: Design to prevent errors

### Interaction Design
1. **Predictability**: UI behaves as users expect
2. **Affordance**: Visual cues show what's interactive
3. **Feedback**: Immediate response to user actions
4. **Reversibility**: Allow undo for destructive actions
5. **Efficiency**: Minimize steps to complete tasks
6. **Discoverability**: Features are easy to find
7. **Consistency**: Similar actions work the same way

### Responsive Design
1. **Mobile First**: Design for smallest screen first
2. **Touch Targets**: Minimum 44x44px for tap targets
3. **Fluid Typography**: Use clamp() for responsive text
4. **Flexible Images**: Responsive images with srcset
5. **Content Priority**: Show most important content first
6. **Performance**: Optimize for mobile networks
7. **Testing**: Test on real devices, not just simulators

### Accessibility
1. **Keyboard Access**: All features via keyboard
2. **Focus Management**: Clear focus indicators
3. **ARIA Labels**: Descriptive labels for screen readers
4. **Semantic HTML**: Use correct HTML elements
5. **Color Independence**: Don't rely on color alone
6. **Text Alternatives**: Alt text for images
7. **Error Identification**: Clear error messages

## Component Library

### Button Component Variants
```typescript
// Primary button - main actions
<Button variant="primary">Create Task</Button>

// Secondary button - secondary actions
<Button variant="secondary">Cancel</Button>

// Outline button - less prominent actions
<Button variant="outline">More Options</Button>

// Ghost button - minimal visual weight
<Button variant="ghost">Learn More</Button>

// Danger button - destructive actions
<Button variant="danger">Delete Task</Button>

// Loading state
<Button isLoading>Saving...</Button>

// With icon
<Button>
  <PlusIcon className="mr-2 h-4 w-4" />
  Add Task
</Button>

// Icon only
<Button variant="ghost" size="icon" aria-label="Settings">
  <SettingsIcon className="h-5 w-5" />
</Button>
```

### Input Component
```typescript
interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
}

export function Input({ label, error, helperText, ...props }: InputProps) {
  const id = props.id || useId()
  const errorId = `${id}-error`
  const helperId = `${id}-helper`

  return (
    <div className="space-y-1">
      {label && (
        <label
          htmlFor={id}
          className="block text-sm font-medium text-gray-700"
        >
          {label}
          {props.required && (
            <span className="text-red-500 ml-1" aria-label="required">
              *
            </span>
          )}
        </label>
      )}

      <input
        id={id}
        className={`
          w-full px-3 py-2 border rounded-md
          focus:outline-none focus:ring-2 focus:ring-primary-500
          disabled:bg-gray-100 disabled:cursor-not-allowed
          ${error ? 'border-red-500' : 'border-gray-300'}
        `}
        aria-invalid={!!error}
        aria-describedby={
          error ? errorId : helperText ? helperId : undefined
        }
        {...props}
      />

      {error && (
        <p id={errorId} className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      {!error && helperText && (
        <p id={helperId} className="text-sm text-gray-500">
          {helperText}
        </p>
      )}
    </div>
  )
}
```

### Card Component
```typescript
interface CardProps {
  children: React.ReactNode
  className?: string
  variant?: 'default' | 'elevated' | 'outlined'
}

export function Card({ children, className, variant = 'default' }: CardProps) {
  const variants = {
    default: 'bg-white border border-gray-200',
    elevated: 'bg-white shadow-md',
    outlined: 'bg-white border-2 border-gray-300',
  }

  return (
    <div className={`rounded-lg p-4 sm:p-6 ${variants[variant]} ${className}`}>
      {children}
    </div>
  )
}
```

## Testing UI/UX

### Accessibility Testing
```typescript
import { render } from '@testing-library/react'
import { axe, toHaveNoViolations } from 'jest-axe'

expect.extend(toHaveNoViolations)

describe('TaskForm Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<TaskForm onSubmit={jest.fn()} />)
    const results = await axe(container)
    expect(results).toHaveNoViolations()
  })

  it('should have proper ARIA labels', () => {
    const { getByLabelText } = render(<TaskForm onSubmit={jest.fn()} />)
    expect(getByLabelText('Task title')).toBeInTheDocument()
  })

  it('should be keyboard navigable', () => {
    const { getByRole } = render(<TaskForm onSubmit={jest.fn()} />)
    const submitButton = getByRole('button', { name: /create task/i })

    submitButton.focus()
    expect(submitButton).toHaveFocus()
  })
})
```

### Responsive Testing
```typescript
describe('TaskList Responsive', () => {
  it('renders mobile layout on small screens', () => {
    window.innerWidth = 375
    const { container } = render(<TaskList />)

    // Check mobile-specific layout
    expect(container.querySelector('.lg\\:grid-cols-2')).not.toBeVisible()
  })

  it('renders desktop layout on large screens', () => {
    window.innerWidth = 1024
    const { container } = render(<TaskList />)

    // Check desktop-specific layout
    expect(container.querySelector('.lg\\:block')).toBeVisible()
  })
})
```

### Visual Regression Testing (Playwright)
```typescript
import { test, expect } from '@playwright/test'

test.describe('Visual Regression', () => {
  test('task card matches screenshot', async ({ page }) => {
    await page.goto('/tasks')

    const taskCard = page.locator('[data-testid="task-card"]').first()
    await expect(taskCard).toHaveScreenshot('task-card.png')
  })

  test('mobile layout matches screenshot', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 })
    await page.goto('/tasks')
    await expect(page).toHaveScreenshot('mobile-tasks.png')
  })

  test('desktop layout matches screenshot', async ({ page }) => {
    await page.setViewportSize({ width: 1920, height: 1080 })
    await page.goto('/tasks')
    await expect(page).toHaveScreenshot('desktop-tasks.png')
  })
})
```

## Integration with SDD Workflow

### Workflow Steps
1. **Requirements Analysis**: Extract UI/UX requirements from specs
2. **Design System**: Define colors, typography, spacing
3. **Component Design**: Design base components
4. **Responsive Layouts**: Plan breakpoints and layouts
5. **Accessibility Review**: Ensure WCAG compliance
6. **Implementation**: Build components with design tokens
7. **Testing**: Accessibility, responsive, visual regression tests
8. **Documentation**: Create style guide and component docs
9. **Review**: Validate against Spec 0 Constitution
10. **Iterate**: Refine based on feedback

## Responsibilities

### What This Skill Does
✅ Define design system (colors, typography, spacing)
✅ Create responsive layouts for all devices
✅ Design accessible UI components
✅ Ensure WCAG 2.1 Level AA compliance
✅ Implement consistent visual design
✅ Create reusable component patterns
✅ Provide Tailwind/CSS configuration
✅ Document UI/UX guidelines
✅ Test accessibility and responsiveness

### What This Skill Does NOT Do
❌ Implement backend logic
❌ Design database schemas
❌ Write API endpoints
❌ Manage authentication
❌ Configure deployment infrastructure
❌ Make business requirement decisions
❌ Create graphic assets (logos, illustrations)

## UI/UX Checklist

Before finalizing UI:
- [ ] Design system tokens defined
- [ ] Color contrast meets WCAG AA (4.5:1)
- [ ] Font sizes readable (16px minimum)
- [ ] Touch targets ≥ 44x44px
- [ ] Responsive on mobile, tablet, desktop
- [ ] Semantic HTML used throughout
- [ ] ARIA labels for interactive elements
- [ ] Keyboard navigation works
- [ ] Focus indicators visible
- [ ] Screen reader tested
- [ ] Loading states implemented
- [ ] Error states with clear messages
- [ ] Empty states with helpful guidance
- [ ] Success feedback for actions
- [ ] Consistent spacing (4px grid)
- [ ] Component library documented
- [ ] Tailwind configuration complete
- [ ] Accessibility tests passing
- [ ] Visual regression tests passing

## Resources

### Tools
- **Design**: Figma, Sketch, Adobe XD
- **Prototyping**: Figma, InVision, Framer
- **Color Contrast**: WebAIM Contrast Checker
- **Accessibility**: axe DevTools, WAVE, Lighthouse
- **Icons**: Lucide, Heroicons, Feather Icons
- **Typography**: Google Fonts, Adobe Fonts

### Documentation
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [MDN Web Docs - Accessibility](https://developer.mozilla.org/en-US/docs/Web/Accessibility)
- [Inclusive Components](https://inclusive-components.design/)
- [A11y Style Guide](https://a11y-style-guide.com/)

## Version History
- **v1.0**: Initial ui-ux skill definition for responsive and accessible design
