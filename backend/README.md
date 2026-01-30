---
title: Todo App API
emoji: 📝
colorFrom: blue
colorTo: indigo
sdk: docker
runtime: huggingface_hub
---

# Todo App API

This is a FastAPI-based Todo application backend with JWT authentication and PostgreSQL database integration.

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /docs` - Interactive API documentation
- `GET /redoc` - Alternative API documentation
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Authenticate user and return JWT
- `POST /api/auth/logout` - Logout user
- `GET /api/user/profile` - Get authenticated user's profile
- `GET /api/user/{user_id}/validate` - Validate JWT and return user info
- `PUT /api/user/profile` - Update user profile
- `GET /api/tasks` - Get user's tasks
- `POST /api/tasks` - Create a new task
- `GET /api/tasks/{task_id}` - Get a specific task
- `PUT /api/tasks/{task_id}` - Update a task
- `DELETE /api/tasks/{task_id}` - Delete a task

## Environment Variables

This application requires the following environment variables to be set:

- `JWT_SECRET`: Secret key for JWT signing (default: randomly generated)
- `DATABASE_URL`: PostgreSQL database connection string
- `JWT_ALGORITHM`: Algorithm for JWT signing (default: HS256)
- `JWT_EXPIRATION_HOURS`: JWT expiration time in hours (default: 24)

## About

Built with FastAPI, SQLModel, and PostgreSQL for a secure and scalable todo application with user authentication.