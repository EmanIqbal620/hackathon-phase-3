# Quickstart Guide: Final Optimization, Performance, and UX Enhancements

## Overview
This guide provides setup and usage instructions for the optimized Todo App with enhanced performance, accessibility features, and UX improvements. The guide covers how to use the new optimization features and verify that all performance and accessibility requirements are met.

## Prerequisites
- Node.js 18+ and npm/yarn
- Python 3.11+
- PostgreSQL database (or Neon for cloud)
- OpenAI API key
- MCP tools framework

## Setup Instructions

### 1. Environment Configuration
```bash
# Copy the environment template
cp .env.example .env

# Update with your configuration:
OPENAI_API_KEY=your_openai_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/todo_app
NEON_DATABASE_URL=your_neon_database_url
```

### 2. Backend Installation
```bash
cd backend
pip install -r requirements.txt

# Run database migrations
python -m src.database.migrate

# Start the backend server
uvicorn src.main:app --reload
```

### 3. Frontend Installation
```bash
cd frontend
npm install

# Start the frontend development server
npm run dev
```

## Performance Optimization Features

### 1. Using Performance Metrics
The application now tracks performance metrics for:
- Page load times
- API response times
- Animation frame rates
- User interaction response times

Access performance data through:
```javascript
// Get user's performance metrics
fetch('/api/performance/{user_id}/metrics?time_range=week', {
  headers: {
    'Authorization': 'Bearer your_token_here',
    'Content-Type': 'application/json'
  }
});
```

### 2. Accessibility Features
The app now includes WCAG 2.1 AA compliance with:
- Proper color contrast ratios (4.5:1 minimum for normal text)
- Full keyboard navigation support
- ARIA labels for screen readers
- Reduced motion support for users with motion sensitivity
- Semantic HTML structure

Access and modify accessibility settings:
```javascript
// Get current accessibility settings
fetch('/api/accessibility/{user_id}/settings', {
  headers: {
    'Authorization': 'Bearer your_token_here',
    'Content-Type': 'application/json'
  }
});

// Update accessibility settings
fetch('/api/accessibility/{user_id}/settings', {
  method: 'PUT',
  headers: {
    'Authorization': 'Bearer your_token_here',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    'high_contrast_enabled': true,
    'reduced_motion_enabled': true,
    'font_size_preference': 'large'
  })
});
```

### 3. Micro-Features
The application includes optional micro-features to improve user efficiency:

#### Keyboard Shortcuts
- `n` or `N`: Create new task
- `s` or `S`: Open search
- `q` or `Q`: Quick-add task
- `t` or `T`: Toggle theme
- `Escape`: Close modals/dialogs

#### Quick-Add Functionality
Press `q` to open a quick-add input that allows rapid task creation without navigating to the full form.

#### Enhanced Drag-and-Drop
Tasks can now be reordered with smooth animations and visual feedback.

## Verification Steps

### 1. Performance Verification
1. Check initial page load time: Should be <2 seconds
2. Verify user interactions respond within 300ms
3. Confirm animations maintain 60fps (use browser dev tools)
4. Test with a large number of tasks (1000+ if available)

### 2. Accessibility Verification
1. Run accessibility audit using browser tools (axe-core)
2. Test keyboard navigation (Tab/Shift+Tab, Enter/Space for activation)
3. Verify screen reader compatibility
4. Check high contrast mode functionality
5. Test with reduced motion settings enabled

### 3. UX Enhancement Verification
1. Confirm all hover effects work smoothly
2. Verify theme switching completes in <200ms
3. Test all new micro-features
4. Verify consistent spacing and typography
5. Check responsive design on different devices

### 4. Console Verification
1. Open browser developer tools
2. Check Console tab for any errors or warnings
3. Verify no console errors appear during normal usage
4. Check Network tab for failed requests

## API Usage Examples

### Recording Performance Metrics
```javascript
// Record a page load performance metric
fetch('/api/performance/{user_id}/record', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer your_token_here',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    'metric_type': 'page_load',
    'value': 1.8,  // in seconds
    'unit': 'seconds',
    'page_route': '/dashboard',
    'device_info': 'Desktop Chrome',
    'network_condition': 'fast_3g'
  })
});
```

### Managing Micro-Feature Preferences
```javascript
// Get user's micro-feature preferences
fetch('/api/micro-features/user/{user_id}/preferences', {
  headers: {
    'Authorization': 'Bearer your_token_here',
    'Content-Type': 'application/json'
  }
});

// Update a specific micro-feature preference
fetch('/api/micro-features/user/{user_id}/preferences/{feature_id}', {
  method: 'PATCH',
  headers: {
    'Authorization': 'Bearer your_token_here',
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    'is_enabled': true,
    'custom_settings': {
      'shortcut_mappings': {
        'n': 'new_task',
        's': 'search',
        'd': 'delete_task'
      }
    }
  })
});
```

## Troubleshooting

### Common Performance Issues
1. **Slow Page Load**: Check network tab for large bundle sizes or slow API calls
2. **Janky Animations**: Enable "reduce motion" in accessibility settings
3. **High API Response Times**: Verify database indexing and query optimization
4. **Memory Leaks**: Check browser memory usage during extended sessions

### Accessibility Issues
1. **Low Contrast**: Enable high contrast mode in accessibility settings
2. **Keyboard Navigation**: Ensure all interactive elements have proper focus management
3. **Screen Reader Problems**: Check for missing ARIA labels or semantic HTML issues
4. **Motion Sensitivity**: Enable reduced motion mode in settings

### Micro-Feature Issues
1. **Keyboard Shortcuts Not Working**: Check if focus is on input fields that might intercept shortcuts
2. **Quick-Add Not Appearing**: Verify the feature is enabled in preferences
3. **Drag-and-Drop Not Responsive**: Check for browser compatibility issues

## Production Verification Checklist

Before deploying to production, verify:
- [ ] Initial page load <2 seconds on standard broadband
- [ ] All API responses <300ms for simple operations
- [ ] Zero console errors during normal usage
- [ ] WCAG 2.1 AA compliance verified with automated tools
- [ ] All animations maintain 60fps performance
- [ ] Theme switching <200ms with smooth transitions
- [ ] All micro-features work as expected
- [ ] Keyboard navigation works for all interactive elements
- [ ] Responsive design works on all target devices
- [ ] Performance metrics are being collected properly