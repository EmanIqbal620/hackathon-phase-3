# CORS Configuration Guide for Full-Stack Application

This guide explains how to configure CORS for both local development and production deployment.

## Problem
When deploying the frontend on Vercel, the browser shows CORS errors:
- Request URL: http://localhost:8000/api/auth/register
- Request Method: OPTIONS
- Status Code: 400 Bad Request

This occurs because the frontend (now on a different origin) makes a preflight OPTIONS request to the backend, which rejects it due to CORS policy.

## Solution

### 1. Backend (FastAPI) Configuration

The backend now supports dynamic CORS configuration using environment variables:

#### Environment Variables:
- `CORS_ORIGINS`: Comma-separated list of allowed origins
- `VERCEL_URL`: Automatically set by Vercel during deployment (used to dynamically add the Vercel URL to allowed origins)
- `PRODUCTION_FRONTEND_URL`: Custom domain for production (optional)

#### Current Allowed Origins:
- `http://localhost:3000` - Local frontend development
- `https://emaniqbal-todo-phase2.hf.space` - Hugging Face deployment
- `http://localhost:8000` - Local backend testing
- Dynamic origins from environment variables

### 2. Frontend (Next.js) Configuration

#### Environment Variables:
- `NEXT_PUBLIC_API_URL`: The backend URL used by the frontend

#### For Different Environments:

**Local Development:**
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

**Vercel Production:**
```
NEXT_PUBLIC_API_URL=https://your-vercel-project-name.vercel.app
```

**Hugging Face Spaces:**
```
NEXT_PUBLIC_API_URL=https://emaniqbal-todo-phase2.hf.space
```

## Setup Instructions

### For Local Development:
1. Ensure your backend is running on `http://localhost:8000`
2. Set in frontend `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```
3. Start both frontend and backend normally

### For Vercel Deployment:

#### Option 1: Using Vercel CLI
1. Install Vercel CLI: `npm i -g vercel`
2. Navigate to the frontend directory: `cd frontend`
3. Run `vercel env add NEXT_PUBLIC_API_URL` and set it to your backend URL
4. Deploy: `vercel --prod`

#### Option 2: Using Vercel Dashboard
1. Go to your Vercel dashboard
2. Select your project
3. Go to Settings → Environment Variables
4. Add:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: Your backend URL (e.g., `https://your-backend.onrender.com` or your Hugging Face Space URL)
5. Redeploy your project

### For Backend Deployment:

#### If deploying backend to a custom server:
1. Set the `PRODUCTION_FRONTEND_URL` environment variable to your Vercel frontend URL
2. If deploying to Vercel, the `VERCEL_URL` will be set automatically

#### If using Hugging Face Spaces (current setup):
The CORS configuration already includes the Hugging Face Space URL.

## Troubleshooting

### Common Issues:

1. **Preflight OPTIONS 400 Error**
   - Ensure your backend allows the Vercel domain
   - Check that the origin in the request matches what's configured

2. **Credentials Not Working**
   - Make sure `allow_credentials=True` is set in CORS middleware
   - Verify that both frontend and backend use the same protocol (HTTP/HTTPS)

3. **Environment Variables Not Loading**
   - For frontend: Ensure variables are prefixed with `NEXT_PUBLIC_`
   - For backend: Check that environment variables are set in the deployment environment

### Testing CORS Configuration:
1. Use browser dev tools Network tab to inspect OPTIONS requests
2. Check the "Access-Control-Allow-Origin" header in responses
3. Verify the request origin matches an allowed origin

## Security Considerations

- Never use `"*"` for `allow_origins` in production
- Only add trusted domains to allowed origins
- Regularly review and remove unused origins from configuration
- Use HTTPS in production environments