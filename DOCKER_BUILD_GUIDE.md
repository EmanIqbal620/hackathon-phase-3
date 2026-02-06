# Docker Build Instructions

## Prerequisites

Before building the Docker images, ensure you have:
- Docker installed and running
- Access to the internet to download dependencies

## Building Images

### Backend Image

To build the backend image:

```bash
cd backend
docker build -t todo-backend .
```

### Frontend Image

To build the frontend image:

```bash
cd frontend
docker build -t todo-frontend .
```

## Common Issues and Solutions

### Issue: "No module named 'psycopg2'"
**Solution**: This occurs when the psycopg2-binary package is not properly installed. The Dockerfile has been updated to include the necessary system dependencies for psycopg2:
- gcc
- g++
- postgresql-dev
- libpq-dev

If you still encounter this issue, rebuild the backend image:
```bash
cd backend
docker build --no-cache -t todo-backend .
```

### Issue: "Image not found" when running containers
**Solution**: Make sure you have built the images first:
```bash
# Build backend
cd backend && docker build -t todo-backend . && cd ..

# Build frontend  
cd frontend && docker build -t todo-frontend . && cd ..
```

### Issue: Build fails due to missing dependencies
**Solution**: Clear Docker build cache and rebuild:
```bash
docker builder prune -a
# Then rebuild your images
```

## Running the Containers

### Backend Container

After building the backend image, run it with:

```bash
# With environment variables from .env file
docker run --env-file .env -p 7860:7860 todo-backend

# Or with specific environment variables
docker run -e DATABASE_URL="your-database-url" -e SECRET_KEY="your-secret-key" -p 7860:7860 todo-backend
```

### Frontend Container

After building the frontend image, run it with:

```bash
docker run -p 3000:7860 todo-frontend
```

## Environment Variables

### Backend

The backend expects the following environment variables:
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time

### Frontend

The frontend can use:
- `NEXT_PUBLIC_API_URL`: Backend API URL (passed during build or runtime)

## Troubleshooting Tips

1. **Check Docker daemon**: Ensure Docker is running before building images
2. **Disk space**: Ensure sufficient disk space for Docker images and build cache
3. **Network connectivity**: Ensure internet access to download dependencies
4. **Build context**: Make sure you're in the correct directory when running docker build
5. **Port conflicts**: Ensure ports 7860 and 3000 are not already in use

## Verifying Successful Build

After building, verify the images exist:

```bash
docker images | grep todo-
```

You should see both `todo-backend` and `todo-frontend` images listed.