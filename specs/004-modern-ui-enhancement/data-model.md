# Data Model: Modern UI & UX Enhancement for Todo Web Application

## UI State Entities

### ThemeState
Represents the current theme preference for the application
- **Fields**:
  - theme: "light" | "dark" (required)
  - updatedAt: timestamp (required)
- **Validation**:
  - theme must be one of the allowed values
  - updatedAt must be a valid timestamp
- **Relationships**: Associated with user preferences

### UserPreferences
Represents user-specific UI preferences and settings
- **Fields**:
  - userId: string (required, foreign key to User)
  - theme: "light" | "dark" (optional, default: "light")
  - taskView: "list" | "grid" | "kanban" (optional, default: "list")
  - notificationsEnabled: boolean (optional, default: true)
  - createdAt: timestamp (required)
  - updatedAt: timestamp (required)
- **Validation**:
  - userId must be a valid user ID
  - theme must be one of allowed values
  - taskView must be one of allowed values
- **Relationships**: Belongs to a User entity

### TaskViewState
Represents the current view state for task lists and filters
- **Fields**:
  - userId: string (required, foreign key to User)
  - filter: "all" | "active" | "completed" (optional, default: "all")
  - sort: "dateCreated" | "dueDate" | "priority" | "title" (optional, default: "dateCreated")
  - searchTerm: string (optional)
  - lastViewed: timestamp (required)
- **Validation**:
  - userId must be a valid user ID
  - filter must be one of allowed values
  - sort must be one of allowed values
- **Relationships**: Associated with user's task view preferences

### ToastNotification
Represents temporary UI notifications for user feedback
- **Fields**:
  - id: string (required, unique identifier)
  - message: string (required, max 255 characters)
  - type: "success" | "error" | "warning" | "info" (required)
  - duration: number (optional, default: 3000ms)
  - position: "top-right" | "bottom-right" | "top-center" | "bottom-center" (optional, default: "top-right")
  - createdAt: timestamp (required)
- **Validation**:
  - message must not exceed 255 characters
  - type must be one of allowed values
  - duration must be between 1000-10000ms
- **Relationships**: Standalone UI entity

### LoadingState
Represents application loading states during API operations
- **Fields**:
  - id: string (required, unique identifier)
  - type: "apiCall" | "component" | "page" (required)
  - isActive: boolean (required)
  - message: string (optional)
  - progress: number (optional, 0-100 for determinate loaders)
  - createdAt: timestamp (required)
- **Validation**:
  - type must be one of allowed values
  - progress must be between 0-100 if provided
- **Relationships**: Standalone UI entity

## UI Component Specifications

### TaskCard Component
Visual representation of a task with interactive elements
- **Props**:
  - task: Task object (required)
  - onToggle: function (required)
  - onEdit: function (required)
  - onDelete: function (required)
  - showPriorityIndicator: boolean (optional, default: true)
  - showDueDate: boolean (optional, default: true)

### TaskFilterBar Component
UI controls for filtering and sorting tasks
- **Props**:
  - currentFilter: string (required)
  - currentSort: string (required)
  - searchTerm: string (optional)
  - onFilterChange: function (required)
  - onSortChange: function (required)
  - onSearchChange: function (required)

### ThemeToggle Component
UI control for switching between light/dark themes
- **Props**:
  - currentTheme: "light" | "dark" (required)
  - onToggle: function (required)
  - showLabel: boolean (optional, default: true)

### SkeletonLoader Component
Placeholder UI for content loading states
- **Props**:
  - type: "card" | "text" | "avatar" | "image" (required)
  - width: string | number (optional)
  - height: string | number (optional)
  - count: number (optional, default: 1)

## State Transitions

### Theme Transition
- **From**: light theme
- **Action**: User toggles theme
- **To**: dark theme
- **Side effect**: Updates ThemeState and applies CSS custom properties

### Loading State Transition
- **From**: idle state
- **Action**: API call initiated
- **To**: loading state
- **Side effect**: Shows loading indicator, potentially disables interactive elements

### Notification Lifecycle
- **From**: no notification
- **Action**: Event occurs (task created, error, etc.)
- **To**: notification visible
- **Action**: Duration elapses or user dismisses
- **To**: notification dismissed