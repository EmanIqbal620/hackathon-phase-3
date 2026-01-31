# Todo App Phase 2 - Authentication & User Identity

This project implements a secure authentication system using JWT tokens with Better Auth for frontend authentication and FastAPI middleware for backend verification. The system ensures stateless authentication with proper user data isolation and database persistence.

## Architecture

The authentication system consists of:

- **Frontend**: Next.js application with Better Auth integration
- **Backend**: FastAPI service with JWT verification middleware
- **Database**: PostgreSQL with SQLModel ORM
- **Security**: Stateless authentication using JWT tokens

## Features

- User registration and login
- JWT-based authentication
- Secure API access with user data isolation
- Session management with automatic token refresh
- Proper error handling (401/403 responses)
- Database persistence for user data

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Set up environment variables in `.env`:
   ```bash
   cp .env.example .env
   ```
   Then edit the `.env` file with your own values:
   ```env
   JWT_SECRET=your-super-secret-jwt-key-here
   JWT_ALGORITHM=HS256
   JWT_EXPIRATION_HOURS=24
   BETTER_AUTH_SECRET=your-better-auth-secret-here
   DATABASE_URL=postgresql://username:password@localhost:5432/todo_app
   SERVER_HOST=localhost
   SERVER_PORT=8000
   LOG_LEVEL=INFO
   ```

3. Install dependencies and start the application:
   ```bash
   # On Unix/Linux/Mac:
   chmod +x start.sh
   ./start.sh

   # On Windows:
   start.bat
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Set up environment variables in `.env.local`:
   ```env
   NEXT_PUBLIC_BETTER_AUTH_URL=http://localhost:8000
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

4. Run the development server:
   ```bash
   npm run dev
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Authenticate user and return JWT
- `POST /api/auth/logout` - Logout user

### User Management
- `GET /api/user/profile` - Get authenticated user's profile
- `GET /api/user/{user_id}/validate` - Validate JWT and return user info
- `PUT /api/user/profile` - Update user profile

## Security Features

- JWT tokens with configurable expiration
- Automatic token refresh
- Cross-user access prevention
- Proper error responses for authentication failures
- Environment-based secret management
- Password hashing with bcrypt
- Database isolation of user data

## Database Schema

The system uses SQLModel with the following tables:
- `users` table with fields: id, email, password_hash, name, is_active, created_at, updated_at

## Testing

To run the backend tests:

```bash
cd backend
python -m pytest tests/
```

## Files Structure

```
backend/
├── src/
│   ├── config.py           # Configuration and environment variables
│   ├── main.py             # Main FastAPI application
│   ├── database.py         # Database connection and session
│   ├── models/
│   │   ├── __init__.py    # Models package init
│   │   └── user.py        # User model definition
│   ├── dependencies/
│   │   └── auth.py        # JWT verification middleware
│   ├── utils/
│   │   └── jwt_utils.py   # JWT utility functions
│   ├── exceptions/
│   │   └── auth.py        # Authentication exceptions
│   └── api/
│       └── routes/
│           ├── auth.py    # Authentication endpoints
│           └── user.py    # User management endpoints
├── tests/
│   └── test_auth.py       # Authentication tests
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variable template
├── init_db.py            # Database initialization script
├── start.sh              # Startup script for Unix/Linux/Mac
└── start.bat             # Startup script for Windows

frontend/
├── src/
│   ├── lib/
│   │   └── auth.ts        # Better Auth configuration
│   ├── services/
│   │   ├── api-client.ts  # API client with JWT attachment
│   │   ├── auth.ts        # Authentication service
│   │   └── session.ts     # Session management
│   └── components/
│       ├── auth/
│       │   ├── RegisterForm.tsx
│       │   └── LoginForm.tsx
│       └── user/
│           └── ProfilePage.tsx
```

## Implementation Details

The authentication system implements the following security principles:

1. **Stateless Authentication**: No server-side session storage required
2. **JWT Verification**: All requests verified using shared secret
3. **User Isolation**: Cross-user access prevented by comparing JWT user ID with requested resource
4. **Proper Error Handling**: Clear 401/403 responses for unauthorized access
5. **Environment-Based Secrets**: JWT secret stored in environment variables only
6. **Password Security**: Passwords are hashed using bcrypt before storage
7. **Database Security**: SQL injection protection through ORM