# Frontend Engineer Skill

## Overview
Builds Next.js frontend pages and components, integrates APIs, and handles JWT tokens for secure user interfaces.

## Description
The Frontend Engineer skill is responsible for implementing modern, responsive, and accessible user interfaces using Next.js and React. It creates reusable components, integrates with backend APIs, manages authentication state, handles JWT tokens securely, and follows frontend best practices for performance, accessibility, and maintainability.

## Components

### 1. Task List Page
**Main Task Management Interface**:
- Display all user tasks in a list view
- Show task details (title, description, completion status)
- Real-time updates when tasks change
- Empty state when no tasks exist
- Loading states during data fetch
- Error states with retry functionality
- Responsive design (mobile, tablet, desktop)
- Accessibility compliance (ARIA labels, keyboard navigation)

**Features**:
- Filter tasks by completion status (all/active/completed)
- Sort tasks (by date, title, completion)
- Search tasks by title/description
- Pagination or infinite scroll for large lists
- Optimistic UI updates
- Skeleton loaders during initial load

**Page Structure** (`app/tasks/page.tsx`):
```typescript
- Header with user info and logout
- Task creation form/button
- Filters and search bar
- Task list component
- Empty state component
- Loading state
- Error boundary
```

### 2. Create, Edit, Delete, Toggle Complete Tasks
**Task Creation**:
- Form to create new tasks
- Input validation (title required, max length)
- Submit button with loading state
- Error handling and display
- Success feedback (toast/notification)
- Clear form after successful creation
- Optimistic UI update

**Task Editing**:
- Inline editing or modal form
- Pre-populate existing task data
- Validation before update
- Cancel button to discard changes
- Loading state during update
- Success/error feedback
- Optimistic UI update

**Task Deletion**:
- Confirmation dialog before delete
- Loading state during deletion
- Success feedback
- Remove from UI immediately
- Undo option (optional)
- Error handling with rollback

**Toggle Completion**:
- Checkbox or button to toggle status
- Visual feedback (strikethrough, color change)
- Instant UI update (optimistic)
- Loading indicator (subtle)
- Error handling with revert
- Accessibility support

**CRUD Operations Flow**:
```typescript
Create: Form → Validate → API Call → Update State → Show Success
Read: Mount → API Call → Update State → Render List
Update: Edit Form → Validate → API Call → Update State → Show Success
Delete: Confirm → API Call → Remove from State → Show Success
Toggle: Click → API Call → Update State → Visual Feedback
```

### 3. Attach JWT Token to API Calls
**Authentication Setup**:
- Store JWT token securely (httpOnly cookie preferred)
- Retrieve token for API requests
- Attach token to Authorization header
- Handle token expiration
- Refresh token mechanism
- Logout on authentication failure

**API Client Configuration**:
- Axios or Fetch wrapper with interceptors
- Automatic token injection
- Request/response interceptors
- Error handling
- Retry logic
- Timeout configuration

**Token Management**:
```typescript
- Get token from storage/cookie
- Attach to request headers: Authorization: Bearer <token>
- Handle 401 responses (redirect to login)
- Refresh token before expiration
- Clear token on logout
- Validate token on app load
```

**Protected Routes**:
- Check authentication on route access
- Redirect to login if not authenticated
- Preserve intended destination
- Handle session expiration gracefully

### 4. Clean Component Structure
**Component Organization**:
```
frontend/
├── app/                          # Next.js App Router
│   ├── layout.tsx               # Root layout
│   ├── page.tsx                 # Home page
│   ├── login/
│   │   └── page.tsx            # Login page
│   ├── register/
│   │   └── page.tsx            # Register page
│   └── tasks/
│       └── page.tsx            # Task list page
├── components/                   # Reusable components
│   ├── ui/                      # Base UI components
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Modal.tsx
│   │   ├── Checkbox.tsx
│   │   └── Card.tsx
│   ├── layout/                  # Layout components
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   └── Sidebar.tsx
│   ├── auth/                    # Auth components
│   │   ├── LoginForm.tsx
│   │   ├── RegisterForm.tsx
│   │   └── ProtectedRoute.tsx
│   └── tasks/                   # Task-specific components
│       ├── TaskList.tsx
│       ├── TaskItem.tsx
│       ├── TaskForm.tsx
│       ├── TaskFilters.tsx
│       └── EmptyState.tsx
├── lib/                         # Utilities and libraries
│   ├── api-client.ts           # API client with auth
│   ├── auth.ts                 # Better Auth setup
│   ├── config.ts               # Environment config
│   └── utils.ts                # Helper functions
├── hooks/                       # Custom React hooks
│   ├── useAuth.ts              # Authentication hook
│   ├── useTasks.ts             # Tasks data hook
│   └── useToast.ts             # Toast notifications
├── types/                       # TypeScript types
│   ├── task.ts
│   ├── user.ts
│   └── api.ts
├── contexts/                    # React contexts
│   ├── AuthContext.tsx
│   └── ToastContext.tsx
└── styles/                      # Global styles
    └── globals.css
```

**Component Design Principles**:
- Single Responsibility Principle
- Composition over inheritance
- Props interface for type safety
- Default props where appropriate
- Prop drilling avoided (use context)
- Reusable and modular
- Self-contained with clear API
- Well-documented with JSDoc

## Reusability
**Yes** - This skill can be reused across Next.js projects requiring:
- Modern React component architecture
- API integration with authentication
- CRUD operations with optimistic updates
- JWT token management
- Responsive and accessible UI
- TypeScript type safety

## Usage

### Called By
- Main Agent (for frontend implementation)
- Frontend Engineer Sub-Agent (for feature development)
- Auth Security Agent (for authentication integration)

### When to Invoke
1. **New Feature Development**: Building new UI features
2. **Component Creation**: Creating reusable components
3. **API Integration**: Connecting frontend to backend
4. **Authentication Setup**: Implementing login/protected routes
5. **UI Refactoring**: Improving component structure

### Example Invocations
```bash
# Build complete task management UI
/frontend-engineer tasks-ui

# Create specific component
/frontend-engineer component --name TaskForm

# Integrate API endpoints
/frontend-engineer api-integration --resource tasks

# Setup authentication flow
/frontend-engineer auth-flow

# Create protected route
/frontend-engineer protected-route --path /tasks

# Review component structure
/frontend-engineer review
```

## Outputs

### Primary Artifacts
1. Next.js pages and layouts
2. Reusable React components
3. API client with authentication
4. Custom React hooks
5. TypeScript type definitions
6. Component tests

### Secondary Outputs
- Storybook stories (if using)
- Component documentation
- Accessibility tests
- E2E tests (Playwright/Cypress)
- Performance optimizations

## Implementation Guide

### 1. API Client with JWT (`lib/api-client.ts`)
```typescript
import axios, { AxiosInstance, AxiosError } from "axios"
import { authClient } from "./auth"
import config from "./config"

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: config.apiUrl,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000,
})

// Request interceptor - attach JWT token
apiClient.interceptors.request.use(
  async (config) => {
    const session = await authClient.getSession()

    if (session?.accessToken) {
      config.headers.Authorization = `Bearer ${session.accessToken}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor - handle errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    // Handle 401 Unauthorized
    if (error.response?.status === 401) {
      // Clear session and redirect to login
      await authClient.signOut()
      window.location.href = "/login"
    }

    // Handle 403 Forbidden
    if (error.response?.status === 403) {
      console.error("Access forbidden:", error.response.data)
    }

    // Handle 422 Validation Error
    if (error.response?.status === 422) {
      console.error("Validation error:", error.response.data)
    }

    return Promise.reject(error)
  }
)

export default apiClient
```

### 2. Task API Service (`lib/api/tasks.ts`)
```typescript
import apiClient from "../api-client"
import { Task, TaskCreate, TaskUpdate } from "@/types/task"

export const tasksApi = {
  // Get all tasks for user
  getTasks: async (userId: number, params?: {
    is_completed?: boolean
    limit?: number
    offset?: number
    sort_by?: string
    order?: string
  }): Promise<Task[]> => {
    const response = await apiClient.get(`/api/${userId}/tasks`, { params })
    return response.data
  },

  // Create new task
  createTask: async (userId: number, data: TaskCreate): Promise<Task> => {
    const response = await apiClient.post(`/api/${userId}/tasks`, data)
    return response.data
  },

  // Get single task
  getTask: async (userId: number, taskId: number): Promise<Task> => {
    const response = await apiClient.get(`/api/${userId}/tasks/${taskId}`)
    return response.data
  },

  // Update task
  updateTask: async (
    userId: number,
    taskId: number,
    data: TaskUpdate
  ): Promise<Task> => {
    const response = await apiClient.put(`/api/${userId}/tasks/${taskId}`, data)
    return response.data
  },

  // Delete task
  deleteTask: async (userId: number, taskId: number): Promise<void> => {
    await apiClient.delete(`/api/${userId}/tasks/${taskId}`)
  },

  // Toggle task completion
  toggleComplete: async (userId: number, taskId: number): Promise<Task> => {
    const response = await apiClient.patch(
      `/api/${userId}/tasks/${taskId}/complete`
    )
    return response.data
  },
}
```

### 3. Tasks Hook (`hooks/useTasks.ts`)
```typescript
import { useState, useEffect, useCallback } from "react"
import { tasksApi } from "@/lib/api/tasks"
import { Task, TaskCreate, TaskUpdate } from "@/types/task"
import { useAuth } from "./useAuth"
import { useToast } from "./useToast"

export function useTasks() {
  const { user } = useAuth()
  const { showToast } = useToast()
  const [tasks, setTasks] = useState<Task[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Fetch tasks
  const fetchTasks = useCallback(async () => {
    if (!user?.id) return

    setIsLoading(true)
    setError(null)

    try {
      const data = await tasksApi.getTasks(user.id)
      setTasks(data)
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to fetch tasks"
      setError(message)
      showToast(message, "error")
    } finally {
      setIsLoading(false)
    }
  }, [user?.id, showToast])

  // Create task
  const createTask = async (data: TaskCreate) => {
    if (!user?.id) return

    try {
      // Optimistic update
      const tempTask: Task = {
        id: Date.now(), // Temporary ID
        user_id: user.id,
        title: data.title,
        description: data.description || null,
        is_completed: false,
        completed_at: null,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      setTasks((prev) => [tempTask, ...prev])

      // API call
      const newTask = await tasksApi.createTask(user.id, data)

      // Replace temp task with real task
      setTasks((prev) =>
        prev.map((t) => (t.id === tempTask.id ? newTask : t))
      )

      showToast("Task created successfully", "success")
      return newTask
    } catch (err) {
      // Rollback optimistic update
      setTasks((prev) => prev.filter((t) => t.id !== Date.now()))

      const message = err instanceof Error ? err.message : "Failed to create task"
      showToast(message, "error")
      throw err
    }
  }

  // Update task
  const updateTask = async (taskId: number, data: TaskUpdate) => {
    if (!user?.id) return

    try {
      // Optimistic update
      setTasks((prev) =>
        prev.map((t) =>
          t.id === taskId
            ? { ...t, ...data, updated_at: new Date().toISOString() }
            : t
        )
      )

      // API call
      const updatedTask = await tasksApi.updateTask(user.id, taskId, data)

      // Update with real data
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? updatedTask : t))
      )

      showToast("Task updated successfully", "success")
      return updatedTask
    } catch (err) {
      // Rollback on error
      await fetchTasks()

      const message = err instanceof Error ? err.message : "Failed to update task"
      showToast(message, "error")
      throw err
    }
  }

  // Delete task
  const deleteTask = async (taskId: number) => {
    if (!user?.id) return

    try {
      // Optimistic update
      const taskToDelete = tasks.find((t) => t.id === taskId)
      setTasks((prev) => prev.filter((t) => t.id !== taskId))

      // API call
      await tasksApi.deleteTask(user.id, taskId)

      showToast("Task deleted successfully", "success")
    } catch (err) {
      // Rollback on error
      await fetchTasks()

      const message = err instanceof Error ? err.message : "Failed to delete task"
      showToast(message, "error")
      throw err
    }
  }

  // Toggle completion
  const toggleComplete = async (taskId: number) => {
    if (!user?.id) return

    try {
      // Optimistic update
      setTasks((prev) =>
        prev.map((t) =>
          t.id === taskId
            ? {
                ...t,
                is_completed: !t.is_completed,
                completed_at: !t.is_completed ? new Date().toISOString() : null,
              }
            : t
        )
      )

      // API call
      const updatedTask = await tasksApi.toggleComplete(user.id, taskId)

      // Update with real data
      setTasks((prev) =>
        prev.map((t) => (t.id === taskId ? updatedTask : t))
      )
    } catch (err) {
      // Rollback on error
      await fetchTasks()

      const message = err instanceof Error ? err.message : "Failed to toggle task"
      showToast(message, "error")
      throw err
    }
  }

  // Load tasks on mount
  useEffect(() => {
    fetchTasks()
  }, [fetchTasks])

  return {
    tasks,
    isLoading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
  }
}
```

### 4. Task List Component (`components/tasks/TaskList.tsx`)
```typescript
"use client"

import { useTasks } from "@/hooks/useTasks"
import TaskItem from "./TaskItem"
import TaskForm from "./TaskForm"
import EmptyState from "./EmptyState"
import { Loader2 } from "lucide-react"

export default function TaskList() {
  const {
    tasks,
    isLoading,
    error,
    createTask,
    updateTask,
    deleteTask,
    toggleComplete,
  } = useTasks()

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" />
        <span className="ml-2 text-gray-600">Loading tasks...</span>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Retry
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      {/* Task Creation Form */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-4">Create New Task</h2>
        <TaskForm onSubmit={createTask} />
      </div>

      {/* Task List */}
      <div>
        <h2 className="text-2xl font-bold mb-4">
          Your Tasks ({tasks.length})
        </h2>

        {tasks.length === 0 ? (
          <EmptyState />
        ) : (
          <div className="space-y-3">
            {tasks.map((task) => (
              <TaskItem
                key={task.id}
                task={task}
                onUpdate={updateTask}
                onDelete={deleteTask}
                onToggleComplete={toggleComplete}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
```

### 5. Task Item Component (`components/tasks/TaskItem.tsx`)
```typescript
"use client"

import { useState } from "react"
import { Task, TaskUpdate } from "@/types/task"
import { Trash2, Edit2, Check, X } from "lucide-react"

interface TaskItemProps {
  task: Task
  onUpdate: (taskId: number, data: TaskUpdate) => Promise<void>
  onDelete: (taskId: number) => Promise<void>
  onToggleComplete: (taskId: number) => Promise<void>
}

export default function TaskItem({
  task,
  onUpdate,
  onDelete,
  onToggleComplete,
}: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editTitle, setEditTitle] = useState(task.title)
  const [editDescription, setEditDescription] = useState(task.description || "")
  const [isDeleting, setIsDeleting] = useState(false)

  const handleUpdate = async () => {
    if (!editTitle.trim()) return

    await onUpdate(task.id, {
      title: editTitle,
      description: editDescription || null,
      is_completed: task.is_completed,
    })
    setIsEditing(false)
  }

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this task?")) return

    setIsDeleting(true)
    try {
      await onDelete(task.id)
    } finally {
      setIsDeleting(false)
    }
  }

  if (isEditing) {
    return (
      <div className="border rounded-lg p-4 bg-white shadow-sm">
        <input
          type="text"
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          className="w-full px-3 py-2 border rounded mb-2"
          placeholder="Task title"
          autoFocus
        />
        <textarea
          value={editDescription}
          onChange={(e) => setEditDescription(e.target.value)}
          className="w-full px-3 py-2 border rounded mb-2"
          placeholder="Task description (optional)"
          rows={3}
        />
        <div className="flex gap-2">
          <button
            onClick={handleUpdate}
            className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700 flex items-center gap-1"
          >
            <Check className="h-4 w-4" />
            Save
          </button>
          <button
            onClick={() => {
              setIsEditing(false)
              setEditTitle(task.title)
              setEditDescription(task.description || "")
            }}
            className="px-3 py-1 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 flex items-center gap-1"
          >
            <X className="h-4 w-4" />
            Cancel
          </button>
        </div>
      </div>
    )
  }

  return (
    <div
      className={`border rounded-lg p-4 bg-white shadow-sm transition-opacity ${
        isDeleting ? "opacity-50" : ""
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Checkbox */}
        <input
          type="checkbox"
          checked={task.is_completed}
          onChange={() => onToggleComplete(task.id)}
          className="mt-1 h-5 w-5 cursor-pointer"
          disabled={isDeleting}
        />

        {/* Task Content */}
        <div className="flex-1">
          <h3
            className={`font-semibold ${
              task.is_completed ? "line-through text-gray-500" : ""
            }`}
          >
            {task.title}
          </h3>
          {task.description && (
            <p className="text-gray-600 text-sm mt-1">{task.description}</p>
          )}
          <p className="text-xs text-gray-400 mt-2">
            Created: {new Date(task.created_at).toLocaleDateString()}
          </p>
        </div>

        {/* Actions */}
        <div className="flex gap-2">
          <button
            onClick={() => setIsEditing(true)}
            className="p-2 text-blue-600 hover:bg-blue-50 rounded"
            disabled={isDeleting}
            aria-label="Edit task"
          >
            <Edit2 className="h-4 w-4" />
          </button>
          <button
            onClick={handleDelete}
            className="p-2 text-red-600 hover:bg-red-50 rounded"
            disabled={isDeleting}
            aria-label="Delete task"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      </div>
    </div>
  )
}
```

### 6. Task Form Component (`components/tasks/TaskForm.tsx`)
```typescript
"use client"

import { useState, FormEvent } from "react"
import { TaskCreate } from "@/types/task"
import { Plus } from "lucide-react"

interface TaskFormProps {
  onSubmit: (data: TaskCreate) => Promise<void>
}

export default function TaskForm({ onSubmit }: TaskFormProps) {
  const [title, setTitle] = useState("")
  const [description, setDescription] = useState("")
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError(null)

    // Validation
    if (!title.trim()) {
      setError("Task title is required")
      return
    }

    if (title.length > 255) {
      setError("Task title cannot exceed 255 characters")
      return
    }

    if (description.length > 2000) {
      setError("Task description cannot exceed 2000 characters")
      return
    }

    setIsSubmitting(true)

    try {
      await onSubmit({
        title: title.trim(),
        description: description.trim() || undefined,
      })

      // Clear form on success
      setTitle("")
      setDescription("")
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to create task")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {/* Title Input */}
      <div>
        <label htmlFor="title" className="block text-sm font-medium mb-1">
          Task Title *
        </label>
        <input
          id="title"
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter task title"
          maxLength={255}
          disabled={isSubmitting}
          required
        />
        <p className="text-xs text-gray-500 mt-1">
          {title.length}/255 characters
        </p>
      </div>

      {/* Description Input */}
      <div>
        <label htmlFor="description" className="block text-sm font-medium mb-1">
          Description (optional)
        </label>
        <textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="w-full px-3 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="Enter task description"
          rows={3}
          maxLength={2000}
          disabled={isSubmitting}
        />
        <p className="text-xs text-gray-500 mt-1">
          {description.length}/2000 characters
        </p>
      </div>

      {/* Error Message */}
      {error && (
        <div className="text-red-600 text-sm bg-red-50 p-3 rounded">
          {error}
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        disabled={isSubmitting || !title.trim()}
        className="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
      >
        {isSubmitting ? (
          <>
            <span className="animate-spin">⏳</span>
            Creating...
          </>
        ) : (
          <>
            <Plus className="h-4 w-4" />
            Create Task
          </>
        )}
      </button>
    </form>
  )
}
```

### 7. Protected Route Component (`components/auth/ProtectedRoute.tsx`)
```typescript
"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import { authClient } from "@/lib/auth"
import { Loader2 } from "lucide-react"

export default function ProtectedRoute({
  children,
}: {
  children: React.ReactNode
}) {
  const router = useRouter()
  const [isAuthenticated, setIsAuthenticated] = useState<boolean | null>(null)

  useEffect(() => {
    const checkAuth = async () => {
      const session = await authClient.getSession()

      if (!session) {
        // Store intended destination
        sessionStorage.setItem("redirectAfterLogin", window.location.pathname)
        router.push("/login")
      } else {
        setIsAuthenticated(true)
      }
    }

    checkAuth()
  }, [router])

  if (isAuthenticated === null) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return <>{children}</>
}
```

### 8. TypeScript Types (`types/task.ts`)
```typescript
export interface Task {
  id: number
  user_id: number
  title: string
  description: string | null
  is_completed: boolean
  completed_at: string | null
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  title: string
  description?: string
}

export interface TaskUpdate {
  title: string
  description: string | null
  is_completed: boolean
}

export interface TaskFilters {
  is_completed?: boolean
  limit?: number
  offset?: number
  sort_by?: "created_at" | "updated_at" | "title" | "is_completed"
  order?: "asc" | "desc"
}
```

## Frontend Best Practices

### 1. Component Design
- **Single Responsibility**: Each component has one clear purpose
- **Composition**: Build complex UIs from simple components
- **Props Interface**: Use TypeScript for type safety
- **Default Props**: Provide sensible defaults
- **Prop Validation**: Validate props at runtime if needed

### 2. State Management
- **Local State**: Use useState for component-specific state
- **Global State**: Use Context API for app-wide state
- **Server State**: Use hooks for API data
- **Derived State**: Compute from existing state, don't duplicate
- **Optimistic Updates**: Update UI immediately, rollback on error

### 3. Performance
- **Code Splitting**: Dynamic imports for large components
- **Lazy Loading**: Load components/images on demand
- **Memoization**: Use React.memo, useMemo, useCallback
- **Virtualization**: For long lists (react-window)
- **Debouncing**: For search and input handlers
- **Image Optimization**: Use Next.js Image component

### 4. Accessibility
- **Semantic HTML**: Use proper HTML elements
- **ARIA Labels**: Add labels for screen readers
- **Keyboard Navigation**: Support tab, enter, escape
- **Focus Management**: Proper focus indicators
- **Color Contrast**: WCAG AA compliance
- **Alt Text**: Descriptive text for images

### 5. Error Handling
- **Error Boundaries**: Catch React errors gracefully
- **Loading States**: Show feedback during async operations
- **Error Messages**: Clear, actionable error messages
- **Retry Logic**: Allow users to retry failed operations
- **Offline Support**: Handle network errors gracefully

### 6. Security
- **XSS Prevention**: Sanitize user input
- **CSRF Protection**: Use tokens for mutations
- **JWT Storage**: httpOnly cookies, not localStorage
- **Input Validation**: Validate on client and server
- **Content Security Policy**: Set proper CSP headers

## Testing Strategy

### Unit Tests (Jest + React Testing Library)
```typescript
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import TaskForm from "@/components/tasks/TaskForm"

describe("TaskForm", () => {
  it("renders form fields", () => {
    const onSubmit = jest.fn()
    render(<TaskForm onSubmit={onSubmit} />)

    expect(screen.getByLabelText(/task title/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument()
  })

  it("validates required title", async () => {
    const onSubmit = jest.fn()
    render(<TaskForm onSubmit={onSubmit} />)

    const submitButton = screen.getByRole("button", { name: /create task/i })
    fireEvent.click(submitButton)

    expect(onSubmit).not.toHaveBeenCalled()
    expect(screen.getByText(/title is required/i)).toBeInTheDocument()
  })

  it("submits form with valid data", async () => {
    const onSubmit = jest.fn().mockResolvedValue(undefined)
    render(<TaskForm onSubmit={onSubmit} />)

    fireEvent.change(screen.getByLabelText(/task title/i), {
      target: { value: "Test Task" },
    })

    fireEvent.click(screen.getByRole("button", { name: /create task/i }))

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        title: "Test Task",
        description: undefined,
      })
    })
  })
})
```

### Integration Tests (Playwright)
```typescript
import { test, expect } from "@playwright/test"

test.describe("Task Management", () => {
  test.beforeEach(async ({ page }) => {
    // Login first
    await page.goto("/login")
    await page.fill('input[name="email"]', "test@example.com")
    await page.fill('input[name="password"]', "password123")
    await page.click('button[type="submit"]')
    await page.waitForURL("/tasks")
  })

  test("creates a new task", async ({ page }) => {
    await page.fill('input[placeholder="Enter task title"]', "Buy groceries")
    await page.fill('textarea[placeholder*="description"]', "Milk, eggs, bread")
    await page.click('button:has-text("Create Task")')

    await expect(page.locator("text=Buy groceries")).toBeVisible()
    await expect(page.locator("text=Milk, eggs, bread")).toBeVisible()
  })

  test("toggles task completion", async ({ page }) => {
    // Create task first
    await page.fill('input[placeholder="Enter task title"]', "Test Task")
    await page.click('button:has-text("Create Task")')

    // Toggle completion
    const checkbox = page.locator('input[type="checkbox"]').first()
    await checkbox.check()

    await expect(page.locator("text=Test Task")).toHaveClass(/line-through/)
  })

  test("deletes a task", async ({ page }) => {
    // Create task
    await page.fill('input[placeholder="Enter task title"]', "Task to Delete")
    await page.click('button:has-text("Create Task")')

    // Delete task
    page.on("dialog", (dialog) => dialog.accept())
    await page.click('button[aria-label="Delete task"]')

    await expect(page.locator("text=Task to Delete")).not.toBeVisible()
  })
})
```

## Performance Optimization

### Code Splitting
```typescript
// Dynamic import for heavy components
import dynamic from "next/dynamic"

const TaskAnalytics = dynamic(() => import("@/components/tasks/TaskAnalytics"), {
  loading: () => <p>Loading analytics...</p>,
  ssr: false,
})
```

### Image Optimization
```typescript
import Image from "next/image"

<Image
  src="/hero.jpg"
  alt="Hero image"
  width={1200}
  height={600}
  priority
  placeholder="blur"
/>
```

### Debouncing
```typescript
import { useState, useEffect } from "react"
import { debounce } from "lodash"

const [searchTerm, setSearchTerm] = useState("")
const [debouncedTerm, setDebouncedTerm] = useState("")

useEffect(() => {
  const handler = debounce(() => {
    setDebouncedTerm(searchTerm)
  }, 300)

  handler()

  return () => handler.cancel()
}, [searchTerm])
```

## Integration with SDD Workflow

### Workflow Steps
1. **Read Requirements**: Parse feature specifications
2. **Design Components**: Plan component hierarchy
3. **Setup TypeScript Types**: Define interfaces
4. **Create API Client**: Setup axios with JWT
5. **Build Custom Hooks**: Implement data fetching hooks
6. **Implement Components**: Build UI components
7. **Add Protected Routes**: Implement authentication guards
8. **Style Components**: Apply responsive design
9. **Write Tests**: Unit and integration tests
10. **Optimize Performance**: Code splitting, lazy loading
11. **Accessibility Audit**: WCAG compliance check

## Responsibilities

### What This Skill Does
✅ Build Next.js pages and layouts
✅ Create reusable React components
✅ Integrate backend APIs with JWT authentication
✅ Implement CRUD operations with optimistic updates
✅ Handle loading, error, and empty states
✅ Create custom hooks for data management
✅ Write TypeScript types and interfaces
✅ Implement responsive and accessible UI
✅ Write component tests
✅ Optimize performance

### What This Skill Does NOT Do
❌ Design the API endpoints (use API Design skill)
❌ Implement backend logic (use Backend Engineer skill)
❌ Configure deployment infrastructure
❌ Design the authentication system (follows auth spec)
❌ Make business requirement decisions
❌ Manage database schemas
❌ Configure CI/CD pipelines

## UI/UX Checklist

Before completing frontend work:
- [ ] All pages are responsive (mobile, tablet, desktop)
- [ ] Loading states implemented for all async operations
- [ ] Error states with retry functionality
- [ ] Empty states with helpful messaging
- [ ] Form validation with clear error messages
- [ ] Optimistic UI updates for better UX
- [ ] Accessibility labels and keyboard navigation
- [ ] Color contrast meets WCAG AA standards
- [ ] Focus indicators visible
- [ ] Images optimized with Next.js Image
- [ ] Code split for large components
- [ ] Protected routes redirect to login
- [ ] JWT tokens attached to all API calls
- [ ] 401 responses trigger logout
- [ ] Success feedback for user actions
- [ ] Confirmation dialogs for destructive actions
- [ ] Component tests written
- [ ] E2E tests for critical flows
- [ ] Performance optimized (Lighthouse score > 90)

## Version History
- **v1.0**: Initial frontend-engineer skill definition for Next.js with JWT integration
