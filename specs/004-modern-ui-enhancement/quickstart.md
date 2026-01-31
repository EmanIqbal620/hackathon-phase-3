# Quickstart Guide: Modern UI & UX Enhancement for Todo Web Application

## Prerequisites

- Node.js (v18 or higher)
- npm or yarn package manager
- Python 3.8+
- Git
- Access to backend API (FastAPI server running on port 8000)

## Environment Setup

### 1. Clone and Navigate
```bash
git clone [repository-url]
cd todo-app
```

### 2. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Install Frontend Dependencies
```bash
cd ../frontend
npm install
```

### 4. Set Up Environment Variables

Create `.env.local` in the frontend directory:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:3000
```

## Running the Application

### 1. Start Backend Server
```bash
cd backend
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Start Frontend Development Server
```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:3000`

## Key Technologies & Libraries

### UI Styling
- **Tailwind CSS**: Utility-first CSS framework for rapid styling
- **Headless UI**: Completely unstyled, fully accessible UI components
- **Framer Motion**: Production-ready motion library for animations

### State Management
- **React Context API**: For theme and UI state management
- **Zustand**: Lightweight state management for complex UI states

### UI Components Structure
```
frontend/src/components/
├── ui/                 # Reusable UI primitives (buttons, modals, etc.)
├── layout/            # Layout components (navbar, sidebar, footer)
├── auth/              # Authentication forms and flows
├── dashboard/         # Dashboard-specific components
├── tasks/             # Task-related components (cards, forms, lists)
├── theme/             # Theme toggle and providers
└── common/            # Shared components across the app
```

## Development Workflow

### 1. Creating New UI Components
1. Place reusable components in `frontend/src/components/ui/`
2. Place feature-specific components in respective folders
3. Follow the naming convention: `ComponentName.tsx`
4. Use Tailwind classes for styling (avoid inline styles)

### 2. Adding Animations
1. Use Framer Motion for complex animations (hero sections, modals)
2. Use Tailwind classes for simple transitions (hover, focus states)
3. Keep animations under 300ms for micro-interactions

### 3. Implementing Dark/Light Theme
1. Define CSS custom properties in `frontend/src/styles/theme.css`
2. Use React Context to manage theme state in `frontend/src/contexts/ThemeContext.tsx`
3. Apply theme classes using Tailwind's dark: prefix

### 4. Responsive Design
1. Use Tailwind's responsive prefixes (sm:, md:, lg:, xl:)
2. Follow mobile-first approach (styles apply from smallest to largest screens)
3. Test components on different screen sizes

## Key UI Patterns Implemented

### 1. Modal Forms
- Create and edit tasks in modal overlays
- Use proper focus management and accessibility attributes
- Implement proper closing mechanisms (ESC key, backdrop click)

### 2. Loading States
- Implement skeleton loaders for content placeholders
- Show loading indicators during API calls
- Use proper aria attributes for accessibility

### 3. Toast Notifications
- Implement toast system for user feedback
- Auto-dismiss notifications after duration
- Support different types (success, error, warning, info)

### 4. Interactive Elements
- Hover and focus states for all interactive elements
- Proper cursor indicators (pointer, not-allowed)
- Smooth transitions between states

## Testing UI Components

### Unit Testing
```bash
npm test
```

### Component Testing
- Test component rendering with different props
- Verify event handlers work correctly
- Ensure accessibility attributes are applied

### Visual Testing
- Test on different screen sizes (mobile, tablet, desktop)
- Verify theme switching works properly
- Check animations perform smoothly

## Common Tailwind Classes Used

### Colors
- Primary: `bg-indigo-600`, `text-indigo-600`
- Success: `bg-green-500`, `text-green-500`
- Error: `bg-red-500`, `text-red-500`
- Neutral: `bg-gray-100`, `text-gray-700`

### Spacing
- Padding: `p-4`, `px-6`, `py-3`
- Margin: `m-2`, `mx-auto`, `my-4`
- Gap: `gap-4`, `space-y-4`

### Typography
- Font sizes: `text-sm`, `text-base`, `text-lg`, `text-xl`
- Font weights: `font-normal`, `font-medium`, `font-semibold`
- Text alignment: `text-left`, `text-center`, `text-right`

### Layout
- Flexbox: `flex`, `flex-col`, `items-center`, `justify-between`
- Grid: `grid`, `grid-cols-1`, `md:grid-cols-3`
- Display: `hidden`, `block`, `inline-block`

## Troubleshooting

### UI Components Not Rendering
- Check if Tailwind is properly configured in `tailwind.config.js`
- Verify component imports are correct
- Ensure all dependencies are installed

### Theme Switching Not Working
- Verify ThemeContext is properly wrapped around the app
- Check CSS custom properties are defined
- Confirm dark: prefixes are used correctly in Tailwind classes

### Animations Not Performing Well
- Reduce animation complexity if performance is poor
- Use `transform` and `opacity` properties for better performance
- Consider disabling animations for users who prefer reduced motion