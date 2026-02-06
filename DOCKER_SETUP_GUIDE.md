# Docker Setup Guide

This guide explains how to build and run the Todo App using standalone Docker containers.

## Prerequisites

- Docker Desktop installed and running

## Building the Application

### Method 1: Using Build Script (Recommended)

Windows:
```bash
build_containers.bat
```

Linux/Mac:
```bash
chmod +x build_containers.sh
./build_containers.sh
```

### Method 2: Manual Build

Backend:
```bash
cd backend
docker build -t todo-backend .
cd ..
```

Frontend:
```bash
cd frontend
docker build -t todo-frontend .
cd ..
```

## Running the Application

### Standalone Containers

1. Start the database:
```bash
docker run -d -p 5432:5432 --name todo-db postgres:15
```

2. Start the backend:
```bash
docker run -d -p 7860:7860 --name todo-backend --link todo-db -e DATABASE_URL=postgresql://postgres:password@todo-db:5432/todoapp todo-backend
```

3. Start the frontend:
```bash
docker run -d -p 3000:7860 --name todo-frontend --link todo-backend -e NEXT_PUBLIC_API_URL=http://localhost:7860 todo-frontend
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:7860
- Database: localhost:5432 (PostgreSQL)

### Using Start Script

Windows:
```bash
start_server.bat
```
This script will display the commands needed to run the containers.

## Container Architecture

The application consists of three standalone containers:

1. **Database**: PostgreSQL 15
   - Internal port: 5432
   - External port: 5432

2. **Backend**: Python/FastAPI application
   - Internal port: 7860
   - External port: 7860

3. **Frontend**: Next.js static site
   - Internal port: 7860 (served by nginx)
   - External port: 3000

## Environment Variables

The services are configured with the following environment variables:

- `DATABASE_URL`: Connection string for PostgreSQL database (used by backend)
- `NEXT_PUBLIC_API_URL`: URL for the backend API (used by frontend)

## Troubleshooting

### Common Issues

1. **Port already in use**: Make sure ports 3000, 7860, and 5432 are free
2. **Build failures**: Check that all required files exist in both frontend and backend directories
3. **Connection issues**: Verify that services are running and can communicate with each other using --link
4. **Container name conflicts**: Make sure container names (todo-db, todo-backend, todo-frontend) are not already in use

### Useful Commands

List running containers:
```bash
docker ps
```

View container logs:
```bash
docker logs [container-name]
```

Stop and remove containers:
```bash
docker stop todo-frontend todo-backend todo-db
docker rm todo-frontend todo-backend todo-db
```

Clean up unused containers and images:
```bash
docker system prune
```

## Development Notes

- The frontend is built as a static site using Next.js export
- The backend uses a PostgreSQL database for persistence
- Containers are linked using Docker's legacy linking feature for communication
- All containers can be managed independently for flexibility