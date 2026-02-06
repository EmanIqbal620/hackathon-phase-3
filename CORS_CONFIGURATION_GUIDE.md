# CORS Configuration Guide

This guide explains how to configure Cross-Origin Resource Sharing (CORS) for the Todo App backend.

## Overview

CORS (Cross-Origin Resource Sharing) is a security feature that controls how web pages in one domain can request resources from another domain. Our backend API implements CORS to securely allow requests from trusted origins while preventing unauthorized cross-origin requests.

## Current Configuration

The backend API is configured with the following CORS settings:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Allowed Origins

The application supports the following origins:

- `http://localhost:3000` - Local frontend development
- `https://emaniqbal-todo-phase2.hf.space` - Deployed frontend on Hugging Face
- `http://localhost:8000` - Local backend (for testing)
- `http://127.0.0.1:3000`
- `http://127.0.0.1:8000`
- `http://localhost:3001`
- `http://localhost:3002`
- `http://127.0.0.1:3001`
- `http://127.0.0.1:3002`
- `http://localhost`
- `http://127.0.0.1`

Additionally, the following dynamic origins are supported:

- Vercel deployment URLs (when `VERCEL_URL` environment variable is set)
- Custom production frontend URL (when `PRODUCTION_FRONTEND_URL` environment variable is set)
- Origins specified in the `CORS_ORIGINS` environment variable (comma-separated list)

## Environment Variables

The CORS configuration can be customized using the following environment variables:

- `CORS_ORIGINS`: Comma-separated list of additional origins to allow
- `VERCEL_URL`: URL of the Vercel deployment (automatically added to allowed origins)
- `PRODUCTION_FRONTEND_URL`: Custom production frontend URL

## Docker Configuration

When running the application with Docker, CORS is automatically configured based on the environment variables. The frontend and backend services are configured to communicate properly within the Docker network.

For Docker deployments, the frontend service is configured with:
- `NEXT_PUBLIC_API_URL=http://backend:7860`

This allows the frontend to communicate with the backend service using the internal Docker network name.

## Security Considerations

- The configuration allows credentials to be sent with cross-origin requests (`allow_credentials=True`)
- All HTTP methods and headers are permitted (`allow_methods=["*"]`, `allow_headers=["*"]`)
- Origins are restricted to known, trusted domains
- Dynamic origins from environment variables should be carefully validated in production

## Troubleshooting

### Common CORS Issues

1. **"Access to fetch from origin has been blocked"**: Check that the requesting origin is in the allowed list
2. **Credentials not being sent**: Ensure the origin is properly configured and credentials are enabled
3. **Development vs Production differences**: Verify that the correct origins are configured for each environment

### Testing CORS Configuration

To test CORS configuration during development:
1. Ensure your frontend is running on one of the allowed origins
2. Check browser developer tools for CORS-related errors
3. Verify that the `Origin` header in requests matches an allowed origin

## Best Practices

- Regularly audit the list of allowed origins
- Use environment-specific configurations
- Monitor for unexpected CORS errors in production
- Consider using more restrictive method/header allowances if security requirements demand it