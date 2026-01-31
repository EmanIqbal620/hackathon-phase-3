from fastapi import HTTPException, status, Request
from collections import defaultdict
import time
from typing import Dict
import threading

# Global storage for rate limiting (in production, use Redis)
# Format: {user_id: [(request_time, count)]}
request_times: Dict[str, list] = defaultdict(list)
lock = threading.Lock()

def rate_limit(max_requests: int = 10, window_seconds: int = 60):
    """
    Rate limiting middleware decorator

    Args:
        max_requests: Maximum number of requests allowed per window
        window_seconds: Time window in seconds
    """
    def rate_limit_middleware(request: Request):
        user_id = request.path_params.get("user_id")  # Extract user_id from path
        if not user_id:
            # Try to extract from token if available
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                # In a real implementation, you'd decode the JWT to get user_id
                # For now, we'll use a placeholder
                user_id = "unknown_user"
            else:
                user_id = "anonymous"

        current_time = time.time()

        with lock:
            # Clean old requests outside the window
            request_times[user_id] = [
                req_time for req_time in request_times[user_id]
                if current_time - req_time < window_seconds
            ]

            # Check if user has exceeded the limit
            if len(request_times[user_id]) >= max_requests:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded: {max_requests} requests per {window_seconds} seconds"
                )

            # Add current request time
            request_times[user_id].append(current_time)

    return rate_limit_middleware


# Alternative implementation using in-memory storage with automatic cleanup
class InMemoryRateLimiter:
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()

    def is_allowed(self, user_id: str) -> bool:
        """
        Check if a request from user_id is allowed

        Args:
            user_id: The ID of the user making the request

        Returns:
            True if request is allowed, False otherwise
        """
        current_time = time.time()

        with self.lock:
            # Clean old requests outside the window
            self.requests[user_id] = [
                req_time for req_time in self.requests[user_id]
                if current_time - req_time < self.window_seconds
            ]

            # Check if user has exceeded the limit
            if len(self.requests[user_id]) >= self.max_requests:
                return False

            # Add current request time
            self.requests[user_id].append(current_time)
            return True

    def get_reset_time(self, user_id: str) -> float:
        """
        Get the time when the rate limit will reset for the user

        Args:
            user_id: The ID of the user

        Returns:
            Unix timestamp when the rate limit will reset
        """
        with self.lock:
            if user_id in self.requests and self.requests[user_id]:
                oldest_request = min(self.requests[user_id])
                return oldest_request + self.window_seconds
            return time.time()


# Create a global rate limiter instance
rate_limiter = InMemoryRateLimiter(max_requests=10, window_seconds=60)


async def check_rate_limit(user_id: str):
    """
    Async function to check rate limit for a user

    Args:
        user_id: The ID of the user making the request

    Raises:
        HTTPException: If rate limit is exceeded
    """
    if not rate_limiter.is_allowed(user_id):
        reset_time = rate_limiter.get_reset_time(user_id)
        retry_after = int(reset_time - time.time())

        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": "Rate limit exceeded",
                "message": f"You have exceeded the rate limit of 10 requests per minute",
                "retry_after_seconds": max(1, retry_after)
            }
        )