# DevOps Environment Management Skill

## Overview
Manages environment variables and secrets for secure deployment and runtime configuration across development, staging, and production environments.

## Description
The DevOps Environment Management skill is responsible for configuring, securing, and managing environment variables and secrets throughout the application lifecycle. It ensures proper separation of configuration from code, implements secure secret storage, provides environment-specific configurations, and follows the twelve-factor app methodology for configuration management.

## Components

### 1. Configure DB_URL, JWT_SECRET, BETTER_AUTH_SECRET
**Database Configuration (DB_URL)**:
- PostgreSQL connection string
- Includes host, port, database name, credentials
- Environment-specific (dev, staging, prod)
- Connection pooling parameters
- SSL mode for production

**Format**:
```bash
# Development
DATABASE_URL=postgresql://user:password@localhost:5432/todo_dev

# Production
DATABASE_URL=postgresql://user:password@db.example.com:5432/todo_prod?sslmode=require

# With connection pooling
DATABASE_URL=postgresql://user:password@localhost:5432/todo_dev?pool_size=20&max_overflow=0
```

**JWT Secret (JWT_SECRET)**:
- Secret key for signing JWT tokens
- Minimum 32 characters, cryptographically random
- Different per environment
- Never committed to version control
- Rotated periodically (security best practice)

**Generation**:
```bash
# Generate secure JWT secret (256-bit)
openssl rand -hex 32

# Or using Python
python -c "import secrets; print(secrets.token_hex(32))"

# Example output
JWT_SECRET=a7f9d8e6c4b2a1e3f5d7c9b8a6e4d2c0f8e6d4c2a0e8f6d4c2a0e8f6d4c2a0e8
```

**Better Auth Secret (BETTER_AUTH_SECRET)**:
- Secret key for Better Auth session management
- Minimum 32 characters, cryptographically random
- Used for encrypting session cookies
- Different per environment
- Rotated periodically

**Generation**:
```bash
# Generate secure Better Auth secret
openssl rand -base64 32

# Example output
BETTER_AUTH_SECRET=xK8vN2mP9qR5tY7uW3eZ6aB4cD1fG8hJ0lM2nO5pQ7rS9tU1vW3xY5zA7bC9dE1f
```

**Additional Configuration Variables**:
- `FRONTEND_URL`: Frontend application URL for CORS
- `BACKEND_URL`: Backend API URL
- `ACCESS_TOKEN_EXPIRE_MINUTES`: JWT token expiration
- `REFRESH_TOKEN_EXPIRE_DAYS`: Refresh token expiration
- `CORS_ORIGINS`: Allowed CORS origins
- `ENVIRONMENT`: Environment name (dev, staging, prod)
- `LOG_LEVEL`: Logging verbosity (DEBUG, INFO, WARNING, ERROR)
- `RATE_LIMIT_PER_MINUTE`: API rate limiting

### 2. Ensure Secure Storage of Secrets
**Never Commit Secrets**:
- Add `.env` to `.gitignore`
- Never commit secrets to version control
- Use `.env.example` for template
- Document required variables without values
- Use secrets scanning tools (git-secrets, truffleHog)

**Environment-Specific Files**:
```
.env.local           # Local development (gitignored)
.env.development     # Development environment (gitignored)
.env.staging         # Staging environment (gitignored)
.env.production      # Production environment (gitignored)
.env.example         # Template with no real values (committed)
.env.test            # Test environment (can be committed with test values)
```

**Secure Storage Solutions**:

**Development**:
- Local `.env` files (gitignored)
- Team shared secrets via secure channels (1Password, LastPass)
- Development-specific dummy values where possible

**Staging/Production**:
- **Cloud Secret Managers**:
  - AWS Secrets Manager
  - Google Cloud Secret Manager
  - Azure Key Vault
  - HashiCorp Vault

- **Environment Variables in Hosting Platform**:
  - Vercel Environment Variables
  - Heroku Config Vars
  - Railway Environment Variables
  - Render Environment Variables
  - Docker secrets

- **CI/CD Secret Management**:
  - GitHub Secrets
  - GitLab CI/CD Variables
  - CircleCI Environment Variables
  - Jenkins Credentials

**Secret Rotation**:
- Rotate secrets regularly (quarterly recommended)
- Implement zero-downtime rotation
- Document rotation procedures
- Alert on rotation failures
- Maintain audit logs

**Access Control**:
- Limit who can view/modify secrets
- Use role-based access control (RBAC)
- Audit access to secrets
- Require MFA for secret access
- Use least privilege principle

### 3. Provide Environment Variables to Backend and Frontend
**Backend Environment Variables (FastAPI)**:

**Configuration File** (`backend/app/config.py`):
```python
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "ToDo API"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Better Auth
    BETTER_AUTH_SECRET: str

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]

    # API
    API_V1_PREFIX: str = "/api"
    RATE_LIMIT_PER_MINUTE: int = 60

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
```

**Usage in Application**:
```python
from app.config import settings

# Access configuration
print(f"Database: {settings.DATABASE_URL}")
print(f"Environment: {settings.ENVIRONMENT}")

# Use in FastAPI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_CREDENTIALS,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)
```

**Frontend Environment Variables (Next.js)**:

**Environment Files**:
```bash
# .env.local (development)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_ENVIRONMENT=development
BETTER_AUTH_SECRET=your-secret-here

# .env.production (production)
NEXT_PUBLIC_API_URL=https://api.todoapp.com
NEXT_PUBLIC_ENVIRONMENT=production
BETTER_AUTH_SECRET=your-production-secret-here
```

**Configuration File** (`frontend/lib/config.ts`):
```typescript
export const config = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  environment: process.env.NEXT_PUBLIC_ENVIRONMENT || "development",
  betterAuthSecret: process.env.BETTER_AUTH_SECRET || "",
  isDevelopment: process.env.NODE_ENV === "development",
  isProduction: process.env.NODE_ENV === "production",
} as const

// Validate required environment variables
const requiredEnvVars = {
  NEXT_PUBLIC_API_URL: config.apiUrl,
  BETTER_AUTH_SECRET: config.betterAuthSecret,
}

Object.entries(requiredEnvVars).forEach(([key, value]) => {
  if (!value) {
    throw new Error(`Missing required environment variable: ${key}`)
  }
})

export default config
```

**Next.js Important Notes**:
- `NEXT_PUBLIC_*` prefix for client-side variables
- Non-prefixed variables only available server-side
- Never expose secrets in `NEXT_PUBLIC_*` variables
- Use server-side API routes for sensitive operations

## Reusability
**Yes** - This skill can be reused across projects requiring:
- Secure environment variable management
- Multi-environment configuration
- Secret storage and rotation
- Twelve-factor app compliance
- Database and API configuration

## Usage

### Called By
- Main Agent (for environment setup)
- DevOps Sub-Agent (for deployment configuration)
- Backend Engineer (for accessing configuration)
- Frontend Engineer (for accessing configuration)

### When to Invoke
1. **Project Initialization**: Setting up environment configuration
2. **New Environment**: Adding staging/production environments
3. **Secret Rotation**: Updating secrets periodically
4. **Deployment**: Configuring deployment environments
5. **Security Audit**: Reviewing secret management

### Example Invocations
```bash
# Setup environment configuration
/devops-env setup

# Generate secrets
/devops-env generate-secrets

# Validate environment variables
/devops-env validate

# Configure specific environment
/devops-env configure --env production

# Rotate secrets
/devops-env rotate-secrets

# Audit secret storage
/devops-env audit
```

## Outputs

### Primary Artifacts
1. `.env.example` - Environment variable template (committed)
2. `.env.local` - Local development environment (gitignored)
3. `backend/app/config.py` - Backend configuration loader
4. `frontend/lib/config.ts` - Frontend configuration loader
5. Environment setup documentation

### Secondary Outputs
- Secret rotation procedures
- Environment-specific deployment configs
- CI/CD pipeline configurations
- Secret scanning configurations
- Access control policies

## Environment Variable Template

### `.env.example` (Committed to Git)
```bash
# =============================================================================
# ToDo App Environment Variables Template
# =============================================================================
# Copy this file to .env.local and fill in the actual values
# NEVER commit .env.local or any file with real secrets to version control
# =============================================================================

# -----------------------------------------------------------------------------
# Application Settings
# -----------------------------------------------------------------------------
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# -----------------------------------------------------------------------------
# Database Configuration
# -----------------------------------------------------------------------------
# PostgreSQL connection string
# Format: postgresql://username:password@host:port/database
DATABASE_URL=postgresql://user:password@localhost:5432/todo_dev

# -----------------------------------------------------------------------------
# JWT Configuration
# -----------------------------------------------------------------------------
# Secret key for signing JWT tokens (generate with: openssl rand -hex 32)
JWT_SECRET_KEY=your-secret-key-here-min-32-chars

# JWT algorithm (HS256 recommended)
JWT_ALGORITHM=HS256

# Access token expiration in minutes (15-60 recommended)
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Refresh token expiration in days
REFRESH_TOKEN_EXPIRE_DAYS=7

# -----------------------------------------------------------------------------
# Better Auth Configuration
# -----------------------------------------------------------------------------
# Secret for Better Auth session encryption (generate with: openssl rand -base64 32)
BETTER_AUTH_SECRET=your-better-auth-secret-here

# -----------------------------------------------------------------------------
# CORS Configuration
# -----------------------------------------------------------------------------
# Comma-separated list of allowed origins
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Frontend URL for redirects
FRONTEND_URL=http://localhost:3000

# -----------------------------------------------------------------------------
# API Configuration
# -----------------------------------------------------------------------------
# API URL for frontend to connect to backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# Rate limiting (requests per minute per user)
RATE_LIMIT_PER_MINUTE=60

# -----------------------------------------------------------------------------
# Optional: External Services
# -----------------------------------------------------------------------------
# Email service (if implementing email notifications)
# SMTP_HOST=smtp.gmail.com
# SMTP_PORT=587
# SMTP_USER=your-email@gmail.com
# SMTP_PASSWORD=your-app-password

# Monitoring/Analytics (if implementing)
# SENTRY_DSN=https://your-sentry-dsn
# ANALYTICS_ID=your-analytics-id

# -----------------------------------------------------------------------------
# Development Tools
# -----------------------------------------------------------------------------
# Enable SQL query logging in development
# SQL_ECHO=true

# Enable detailed error messages
# SHOW_DETAILED_ERRORS=true
```

### `.gitignore` Configuration
```bash
# Environment variables
.env
.env.local
.env.development
.env.staging
.env.production
.env.*.local

# Keep example file
!.env.example
!.env.test

# Secrets
secrets/
*.key
*.pem
*.crt

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
```

## Security Best Practices

### Secret Generation
- **Use cryptographically secure random generators**
  ```bash
  # Good
  openssl rand -hex 32
  python -c "import secrets; print(secrets.token_hex(32))"

  # Bad
  echo "mysecret123"  # Too predictable
  date +%s | sha256sum  # Not random enough
  ```

- **Minimum Secret Length**:
  - JWT secrets: 32 bytes (256 bits)
  - Better Auth secrets: 32 bytes (256 bits)
  - API keys: 32+ bytes
  - Passwords: 12+ characters

### Secret Storage
- **Never in Version Control**:
  - Add `.env*` to `.gitignore` (except `.env.example`)
  - Use git-secrets or gitleaks to scan commits
  - Remove secrets from git history if accidentally committed

- **Never in Code**:
  ```python
  # Bad
  JWT_SECRET = "hardcoded-secret-123"

  # Good
  JWT_SECRET = os.getenv("JWT_SECRET_KEY")
  if not JWT_SECRET:
      raise ValueError("JWT_SECRET_KEY must be set")
  ```

- **Never in Logs**:
  ```python
  # Bad
  logger.info(f"Using JWT secret: {settings.JWT_SECRET_KEY}")

  # Good
  logger.info("JWT authentication initialized")
  ```

- **Never in Client-Side Code**:
  ```javascript
  // Bad (Next.js)
  const JWT_SECRET = process.env.NEXT_PUBLIC_JWT_SECRET  // Exposed to browser!

  // Good
  const JWT_SECRET = process.env.JWT_SECRET  // Server-side only
  ```

### Environment Isolation
- **Separate Secrets Per Environment**:
  - Development: Safe to use dummy/test values
  - Staging: Production-like but separate secrets
  - Production: Highly secure, rotated regularly

- **Never Share Secrets Between Environments**:
  ```bash
  # Bad
  JWT_SECRET=same-secret-for-all-envs

  # Good
  # Development
  JWT_SECRET=dev-secret-abc123...

  # Production
  JWT_SECRET=prod-secret-xyz789...
  ```

### Access Control
- **Limit Access**:
  - Only DevOps/senior engineers access production secrets
  - Use RBAC in secret management systems
  - Audit all secret access
  - Require MFA for production secret access

- **Principle of Least Privilege**:
  - Applications only access secrets they need
  - Read-only access when possible
  - Temporary credentials when possible

### Secret Rotation
- **Regular Rotation Schedule**:
  - JWT secrets: Quarterly
  - Database passwords: Quarterly
  - API keys: As needed or annually
  - Document rotation in calendar

- **Zero-Downtime Rotation**:
  ```python
  # Support multiple valid secrets during rotation
  JWT_SECRETS = [
      os.getenv("JWT_SECRET_KEY"),  # Current
      os.getenv("JWT_SECRET_KEY_OLD"),  # Previous (grace period)
  ]

  def verify_token(token):
      for secret in JWT_SECRETS:
          try:
              return jwt.decode(token, secret, algorithms=["HS256"])
          except:
              continue
      raise InvalidTokenError()
  ```

### Monitoring and Auditing
- **Log Secret Access** (but never the secret values):
  ```python
  logger.info("JWT secret loaded successfully")
  logger.warning("Failed to load database URL")
  ```

- **Alert on Failures**:
  - Missing required environment variables
  - Failed secret rotation
  - Unauthorized secret access attempts

- **Regular Audits**:
  - Review who has access to secrets
  - Check for secrets in code/logs
  - Verify rotation compliance
  - Scan for leaked secrets

## Validation and Testing

### Environment Validation Script
```python
# scripts/validate_env.py
import os
import sys
from typing import List, Tuple

def validate_environment() -> Tuple[bool, List[str]]:
    """Validate required environment variables are set."""
    required_vars = [
        "DATABASE_URL",
        "JWT_SECRET_KEY",
        "BETTER_AUTH_SECRET",
    ]

    optional_vars = [
        "CORS_ORIGINS",
        "FRONTEND_URL",
        "LOG_LEVEL",
    ]

    errors = []
    warnings = []

    # Check required variables
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            errors.append(f"Missing required environment variable: {var}")
        elif var.endswith("SECRET") and len(value) < 32:
            errors.append(f"{var} must be at least 32 characters")

    # Check optional variables
    for var in optional_vars:
        if not os.getenv(var):
            warnings.append(f"Optional environment variable not set: {var}")

    # Print results
    if errors:
        print("❌ Environment Validation Failed:")
        for error in errors:
            print(f"  - {error}")

    if warnings:
        print("⚠️  Warnings:")
        for warning in warnings:
            print(f"  - {warning}")

    if not errors and not warnings:
        print("✅ Environment validation passed!")

    return len(errors) == 0, errors

if __name__ == "__main__":
    success, _ = validate_environment()
    sys.exit(0 if success else 1)
```

### Testing with Environment Variables
```python
# tests/conftest.py
import pytest
import os

@pytest.fixture(scope="session")
def test_env():
    """Set up test environment variables."""
    test_vars = {
        "DATABASE_URL": "postgresql://test:test@localhost:5432/test_db",
        "JWT_SECRET_KEY": "test-secret-key-for-testing-only-min-32-chars-long",
        "BETTER_AUTH_SECRET": "test-better-auth-secret-min-32-chars",
        "ENVIRONMENT": "test",
        "DEBUG": "false",
    }

    # Store original values
    original_values = {key: os.getenv(key) for key in test_vars}

    # Set test values
    for key, value in test_vars.items():
        os.environ[key] = value

    yield test_vars

    # Restore original values
    for key, value in original_values.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
```

## Deployment Configurations

### Docker Compose (Development)
```yaml
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: ${DB_USER:-todouser}
      POSTGRES_PASSWORD: ${DB_PASSWORD:-todopass}
      POSTGRES_DB: ${DB_NAME:-todo_dev}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    env_file:
      - .env.local
    environment:
      DATABASE_URL: postgresql://${DB_USER:-todouser}:${DB_PASSWORD:-todopass}@db:5432/${DB_NAME:-todo_dev}
    ports:
      - "8000:8000"
    depends_on:
      - db

  frontend:
    build: ./frontend
    env_file:
      - .env.local
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
```

### Kubernetes (Production)
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: todo-app-config
data:
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  CORS_ORIGINS: "https://todoapp.com"
  FRONTEND_URL: "https://todoapp.com"

---
# k8s/secret.yaml (Apply secrets separately, never commit)
apiVersion: v1
kind: Secret
metadata:
  name: todo-app-secrets
type: Opaque
stringData:
  DATABASE_URL: postgresql://user:pass@db:5432/todo_prod
  JWT_SECRET_KEY: your-production-jwt-secret
  BETTER_AUTH_SECRET: your-production-auth-secret
```

### CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy Backend
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          JWT_SECRET_KEY: ${{ secrets.JWT_SECRET_KEY }}
          BETTER_AUTH_SECRET: ${{ secrets.BETTER_AUTH_SECRET }}
        run: |
          # Deployment commands here
          echo "Deploying with secure environment variables"
```

## Integration with SDD Workflow

### Workflow Steps
1. **Requirements Analysis**: Identify required configuration
2. **Create `.env.example`**: Document all required variables
3. **Setup `.gitignore`**: Ensure secrets not committed
4. **Generate Secrets**: Create secure random secrets
5. **Configure Backend**: Setup Pydantic Settings
6. **Configure Frontend**: Setup Next.js environment
7. **Validation Script**: Create env validation
8. **Documentation**: Document setup procedures
9. **Testing**: Test with different environments
10. **Deployment**: Configure production secrets securely

## Responsibilities

### What This Skill Does
✅ Configure environment variables for all environments
✅ Generate secure secrets (JWT, Better Auth, etc.)
✅ Create `.env.example` template
✅ Setup configuration loaders (backend/frontend)
✅ Implement secret validation
✅ Document environment setup procedures
✅ Configure `.gitignore` for secret protection
✅ Provide deployment configuration examples
✅ Implement secret rotation procedures

### What This Skill Does NOT Do
❌ Deploy applications to production
❌ Manage cloud infrastructure
❌ Implement application features
❌ Design database schemas
❌ Write application code
❌ Configure CI/CD pipelines (provides examples only)
❌ Manage SSL/TLS certificates directly

## Security Checklist

Before deployment:
- [ ] `.env` files in `.gitignore`
- [ ] `.env.example` created and committed
- [ ] All secrets are cryptographically random
- [ ] Secrets are minimum 32 characters
- [ ] No secrets committed to git history
- [ ] No secrets in application code
- [ ] No secrets in logs
- [ ] No secrets exposed to client-side (NEXT_PUBLIC_*)
- [ ] Different secrets per environment
- [ ] Production secrets stored in secret manager
- [ ] Access control configured for secrets
- [ ] Secret rotation schedule established
- [ ] Environment validation script created
- [ ] Required environment variables documented
- [ ] CI/CD secrets configured securely
- [ ] Monitoring for missing environment variables
- [ ] Audit logging for secret access

## Troubleshooting

### Common Issues

**Missing Environment Variables**:
```python
# Error: KeyError or AttributeError
# Solution: Check .env.local exists and is loaded
# Verify variable name matches exactly (case-sensitive)
```

**Invalid Secret Format**:
```python
# Error: Token signing fails
# Solution: Regenerate secret with proper length
openssl rand -hex 32  # For JWT
```

**CORS Issues**:
```python
# Error: CORS policy blocking requests
# Solution: Check CORS_ORIGINS includes frontend URL
CORS_ORIGINS=http://localhost:3000,https://app.example.com
```

**Database Connection Fails**:
```python
# Error: Connection refused
# Solution: Verify DATABASE_URL format
DATABASE_URL=postgresql://user:pass@localhost:5432/dbname
```

## Version History
- **v1.0**: Initial devops-env skill definition for secure environment management
