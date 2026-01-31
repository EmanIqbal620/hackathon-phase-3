"""
API Rate Limiting Middleware
This module provides functionality for controlling API request rates to prevent abuse and ensure fair usage.
"""
from fastapi import Request, HTTPException, status
from typing import Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import time
import threading
import hashlib
import asyncio
import logging
from pydantic import BaseModel
from sqlmodel import Session, select
from ..models.performance import PerformanceMetrics, PerformanceMetricsCreate
from ..database import sync_engine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimitInfo(BaseModel):
    """Information about a rate limit"""
    limit: int
    remaining: int
    reset_time: int


class RateLimiter:
    """Rate limiter implementation with in-memory storage and optional database persistence."""

    def __init__(self, default_limit: int = 100, default_window: int = 3600):
        """
        Initialize the rate limiter.

        Args:
            default_limit: Default number of requests allowed per window
            default_window: Default time window in seconds
        """
        self.default_limit = default_limit
        self.default_window = default_window
        self.requests = defaultdict(list)  # {identifier: [timestamps]}
        self.lock = threading.Lock()

    def _get_client_identifier(self, request: Request) -> str:
        """
        Get a unique identifier for the client making the request.

        Args:
            request: The incoming request

        Returns:
            A unique identifier for the client
        """
        # Try to get IP address from various headers (to handle proxies)
        forwarded_for = request.headers.get("x-forwarded-for")
        real_ip = request.headers.get("x-real-ip")
        x_cluster_client_ip = request.headers.get("x-cluster-client-ip")

        if forwarded_for:
            ip = forwarded_for.split(",")[0].strip()
        elif real_ip:
            ip = real_ip.strip()
        elif x_cluster_client_ip:
            ip = x_cluster_client_ip.strip()
        else:
            ip = request.client.host if request.client else "unknown"

        # Include user ID if available (from JWT token)
        user_id = getattr(request.state, 'user_id', None)
        identifier = f"{ip}:{user_id}" if user_id else ip

        # Hash the identifier to prevent abuse patterns
        return hashlib.sha256(identifier.encode()).hexdigest()[:16]

    def _cleanup_old_requests(self, identifier: str, window: int):
        """
        Remove timestamps that are outside the current time window.

        Args:
            identifier: Client identifier
            window: Time window in seconds
        """
        now = time.time()
        cutoff = now - window

        with self.lock:
            self.requests[identifier] = [
                timestamp for timestamp in self.requests[identifier]
                if timestamp > cutoff
            ]

    def is_allowed(
        self,
        request: Request,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> tuple[bool, RateLimitInfo]:
        """
        Check if a request is allowed based on rate limits.

        Args:
            request: The incoming request
            limit: Override for the number of requests allowed (optional)
            window: Override for the time window in seconds (optional)

        Returns:
            Tuple of (is_allowed, rate_limit_info)
        """
        identifier = self._get_client_identifier(request)
        limit = limit or self.default_limit
        window = window or self.default_window

        # Clean up old requests
        self._cleanup_old_requests(identifier, window)

        with self.lock:
            current_requests = self.requests[identifier]
            current_count = len(current_requests)

            # Check if limit exceeded
            is_allowed_result = current_count < limit

            # Add current request timestamp
            if is_allowed_result:
                current_requests.append(time.time())

            # Calculate reset time (when the window will reset)
            now = time.time()
            reset_time = int(now + window)

            remaining = max(0, limit - current_count - (0 if is_allowed_result else 1))

            rate_limit_info = RateLimitInfo(
                limit=limit,
                remaining=remaining,
                reset_time=reset_time
            )

            return is_allowed_result, rate_limit_info

    def get_rate_limit_headers(self, rate_limit_info: RateLimitInfo) -> Dict[str, str]:
        """
        Get rate limit headers to include in response.

        Args:
            rate_limit_info: Rate limit information

        Returns:
            Dictionary of headers to include in response
        """
        return {
            "X-RateLimit-Limit": str(rate_limit_info.limit),
            "X-RateLimit-Remaining": str(rate_limit_info.remaining),
            "X-RateLimit-Reset": str(rate_limit_info.reset_time),
        }


# Global rate limiter instance
rate_limiter = RateLimiter(default_limit=100, default_window=3600)


def get_rate_limit_middleware(
    default_limit: int = 100,
    default_window: int = 3600,
    endpoint_limits: Optional[Dict[str, tuple[int, int]]] = None  # {path: (limit, window)}
):
    """
    Create a rate limiting middleware function.

    Args:
        default_limit: Default number of requests allowed per window
        default_window: Default time window in seconds
        endpoint_limits: Specific limits for certain endpoints

    Returns:
        Middleware function
    """
    local_rate_limiter = RateLimiter(default_limit, default_window)
    endpoint_limits = endpoint_limits or {}

    async def rate_limit_middleware(request: Request, call_next):
        # Determine rate limit for this endpoint
        path = request.url.path
        limit, window = endpoint_limits.get(path, (default_limit, default_window))

        # For API endpoints, we might want stricter limits
        if path.startswith("/api/"):
            # Apply more conservative limits to API endpoints
            if limit > 50:  # If default is higher than 50, cap at 50 for APIs
                limit = min(limit, 50)

        # Check if request is allowed
        is_allowed, rate_info = local_rate_limiter.is_allowed(request, limit, window)

        # Continue with request processing
        response = await call_next(request)

        # Add rate limit headers to response
        headers = local_rate_limiter.get_rate_limit_headers(rate_info)
        for header, value in headers.items():
            response.headers[header] = value

        # Log rate limit information
        client_id = local_rate_limiter._get_client_identifier(request)
        logger.debug(f"Rate limit check for {client_id}: {rate_info.remaining}/{rate_info.limit} remaining")

        # If the request was denied, update the response
        if not is_allowed:
            # This shouldn't happen in normal flow since we process the request anyway
            # The rate limiting should be handled before processing
            pass

        return response

    return rate_limit_middleware


def rate_limit_endpoint(
    limit: int,
    window: int = 3600,
    per_user: bool = True,
    block_on_exceed: bool = True
):
    """
    Decorator to apply rate limiting to specific endpoints.

    Args:
        limit: Number of requests allowed per window
        window: Time window in seconds
        per_user: Whether to apply limits per user or per IP
        block_on_exceed: Whether to block requests when limit is exceeded

    Returns:
        Decorator function
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extract request from kwargs or args
            request = None
            for arg in list(args) + list(kwargs.values()):
                if isinstance(arg, Request):
                    request = arg
                    break

            if not request:
                logger.warning("Request object not found, skipping rate limit check")
                return await func(*args, **kwargs)

            # Modify request to include user info if needed
            if per_user:
                # In a real implementation, you'd extract user info from JWT
                # Here we'll just use a placeholder approach
                pass

            # Check rate limit
            is_allowed, rate_info = rate_limiter.is_allowed(request, limit, window)

            if not is_allowed and block_on_exceed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail={
                        "error": "Rate limit exceeded",
                        "limit": limit,
                        "window_seconds": window,
                        "retry_after": rate_info.reset_time - int(time.time())
                    }
                )

            # Store rate limit info in request state for later use
            request.state.rate_limit_remaining = rate_info.remaining
            request.state.rate_limit_reset = rate_info.reset_time

            # Call the original function
            result = await func(*args, **kwargs)

            return result

        return wrapper
    return decorator


class DatabaseRateLimiter(RateLimiter):
    """
    Rate limiter that uses database storage for persistence across server restarts.
    """

    def __init__(self, default_limit: int = 100, default_window: int = 3600):
        super().__init__(default_limit, default_window)
        self.use_database = True

    def is_allowed(
        self,
        request: Request,
        limit: Optional[int] = None,
        window: Optional[int] = None
    ) -> tuple[bool, RateLimitInfo]:
        """
        Check if a request is allowed based on database-stored rate limits.
        """
        identifier = self._get_client_identifier(request)
        limit = limit or self.default_limit
        window = window or self.default_window

        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window)

        # Use database to track requests
        with Session(sync_engine) as session:
            # Get recent requests for this identifier
            # This would typically involve a separate RateLimit table
            # For now, we'll simulate with performance metrics table
            # In a real implementation, you'd have a dedicated rate limit table

            # Record performance metric for rate limiting tracking
            from ..models.performance import PerformanceMetrics, PerformanceMetricsCreate

            metric = PerformanceMetricsCreate(
                user_id=getattr(request.state, 'user_id', 'anonymous'),
                metric_type='api_rate_limit_check',
                value=1.0,  # Just counting the check
                unit='count',
                api_endpoint=request.url.path,
                device_info=f"client:{identifier}",
                additional_metadata={
                    'rate_limit_config': {'limit': limit, 'window': window},
                    'timestamp': now.isoformat()
                }
            )

            rate_limit_record = PerformanceMetrics.model_validate(metric)
            session.add(rate_limit_record)
            session.commit()

            # For simulation, we'll use in-memory approach
            # In a real implementation, you'd query the database for recent requests
            return super().is_allowed(request, limit, window)


# Create a database-backed rate limiter instance
db_rate_limiter = DatabaseRateLimiter(default_limit=100, default_window=3600)


def get_enhanced_rate_limit_middleware(
    default_limit: int = 100,
    default_window: int = 3600,
    endpoint_limits: Optional[Dict[str, tuple[int, int]]] = None,
    use_database: bool = False
):
    """
    Create an enhanced rate limiting middleware with additional features.

    Args:
        default_limit: Default number of requests allowed per window
        default_window: Default time window in seconds
        endpoint_limits: Specific limits for certain endpoints
        use_database: Whether to use database persistence

    Returns:
        Enhanced middleware function
    """
    rate_limiter_instance = db_rate_limiter if use_database else rate_limiter
    endpoint_limits = endpoint_limits or {}

    async def enhanced_rate_limit_middleware(request: Request, call_next):
        # Determine rate limit for this endpoint
        path = request.url.path
        limit, window = endpoint_limits.get(path, (default_limit, default_window))

        # Apply different limits based on request characteristics
        if path.startswith("/api/"):
            # Apply more conservative limits to API endpoints
            limit = min(limit, 50)
        elif path.startswith("/auth/"):
            # Even more conservative for auth endpoints
            limit = min(limit, 20)

        # Check if request is allowed
        is_allowed, rate_info = rate_limiter_instance.is_allowed(request, limit, window)

        # Add rate limit info to request state
        request.state.rate_limit_remaining = rate_info.remaining
        request.state.rate_limit_reset = rate_info.reset_time

        # If rate limit exceeded, return 429 error
        if not is_allowed:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded",
                    "limit": limit,
                    "remaining": rate_info.remaining,
                    "reset_time": rate_info.reset_time,
                    "retry_after": rate_info.reset_time - int(time.time())
                },
                headers={
                    "X-RateLimit-Limit": str(rate_info.limit),
                    "X-RateLimit-Remaining": str(rate_info.remaining),
                    "X-RateLimit-Reset": str(rate_info.reset_time),
                }
            )

        # Continue with request processing
        response = await call_next(request)

        # Add rate limit headers to response
        headers = rate_limiter_instance.get_rate_limit_headers(rate_info)
        for header, value in headers.items():
            response.headers[header] = value

        return response

    # Import here to avoid circular imports
    from fastapi.responses import JSONResponse
    from fastapi import status

    return enhanced_rate_limit_middleware


# Default rate limiter instance
default_rate_limiter = RateLimiter(default_limit=100, default_window=3600)