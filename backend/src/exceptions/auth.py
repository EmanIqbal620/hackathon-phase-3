from fastapi import HTTPException, status

class AuthException(HTTPException):
    """Base exception class for authentication-related errors."""

    def __init__(self, detail: str, status_code: int = status.HTTP_401_UNAUTHORIZED):
        super().__init__(status_code=status_code, detail=detail)


class InvalidCredentialsException(AuthException):
    """Raised when provided credentials are invalid."""

    def __init__(self, detail: str = "Invalid credentials"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class TokenExpiredException(AuthException):
    """Raised when a JWT token has expired."""

    def __init__(self, detail: str = "Token has expired"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class TokenValidationException(AuthException):
    """Raised when a JWT token cannot be validated."""

    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class InsufficientPermissionsException(AuthException):
    """Raised when a user lacks sufficient permissions for an action."""

    def __init__(self, detail: str = "Insufficient permissions"):
        super().__init__(detail=detail, status_code=status.HTTP_403_FORBIDDEN)


class UserNotFoundException(AuthException):
    """Raised when a user is not found in the system."""

    def __init__(self, detail: str = "User not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class UserInactiveException(AuthException):
    """Raised when a user account is inactive."""

    def __init__(self, detail: str = "User account is inactive"):
        super().__init__(detail=detail, status_code=status.HTTP_401_UNAUTHORIZED)


class DuplicateUserException(AuthException):
    """Raised when attempting to create a user with credentials that already exist."""

    def __init__(self, detail: str = "User already exists"):
        super().__init__(detail=detail, status_code=status.HTTP_409_CONFLICT)