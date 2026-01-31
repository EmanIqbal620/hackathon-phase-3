"""
Error Handling Middleware with Performance Monitoring
This module provides comprehensive error handling with integrated performance monitoring.
"""
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Callable, Optional
import traceback
import logging
import time
from datetime import datetime
from ..services.performance_monitor import PerformanceMonitor, MetricType
from ..models.performance import PerformanceMetrics
import sys
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    """
    Comprehensive error handling middleware with performance monitoring.
    """

    def __init__(self, app, enable_performance_monitoring: bool = True):
        super().__init__(app)
        self.enable_performance_monitoring = enable_performance_monitoring

    async def dispatch(self, request: Request, call_next: Callable):
        start_time = time.time()
        error_occurred = False
        error_details = None

        try:
            # Add request start time for performance tracking
            request.state.request_start_time = start_time

            # Process the request
            response = await call_next(request)

            # Calculate response time
            response_time = (time.time() - start_time) * 1000  # Convert to milliseconds

            # Log performance metrics if enabled
            if self.enable_performance_monitoring:
                user_id = getattr(request.state, 'user_id', 'anonymous')

                # Record API response time
                PerformanceMonitor.record_metric(
                    user_id=user_id,
                    metric_type=MetricType.API_RESPONSE,
                    value=response_time,
                    unit="milliseconds",
                    api_endpoint=str(request.url.path),
                    device_info=request.headers.get('user-agent', ''),
                    network_condition=self._get_network_condition(request)
                )

            return response

        except HTTPException as e:
            error_occurred = True
            error_details = {
                "type": "HTTPException",
                "status_code": e.status_code,
                "detail": e.detail,
                "headers": getattr(e, 'headers', None)
            }

            response_time = (time.time() - start_time) * 1000
            await self._record_error_metrics(request, response_time, error_details)

            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": "Request failed",
                    "status_code": e.status_code,
                    "message": str(e.detail),
                    "timestamp": datetime.utcnow().isoformat()
                },
                headers=getattr(e, 'headers', {})
            )

        except StarletteHTTPException as e:
            error_occurred = True
            error_details = {
                "type": "StarletteHTTPException",
                "status_code": e.status_code,
                "detail": e.detail
            }

            response_time = (time.time() - start_time) * 1000
            await self._record_error_metrics(request, response_time, error_details)

            return JSONResponse(
                status_code=e.status_code,
                content={
                    "error": "Request failed",
                    "status_code": e.status_code,
                    "message": str(e.detail),
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

        except Exception as e:
            error_occurred = True
            error_details = {
                "type": "UnexpectedError",
                "status_code": 500,
                "error_class": e.__class__.__name__,
                "message": str(e),
                "traceback": traceback.format_exc()
            }

            response_time = (time.time() - start_time) * 1000
            await self._record_error_metrics(request, response_time, error_details)

            # Log the full error with traceback
            logger.error(f"Unexpected error occurred: {str(e)}", exc_info=True)

            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "status_code": 500,
                    "message": "An unexpected error occurred",
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        finally:
            if error_occurred and self.enable_performance_monitoring:
                # Record error-specific metrics
                response_time = (time.time() - start_time) * 1000

                user_id = getattr(request.state, 'user_id', 'anonymous')
                PerformanceMonitor.record_metric(
                    user_id=user_id,
                    metric_type=MetricType.API_RESPONSE,
                    value=response_time,
                    unit="milliseconds",
                    api_endpoint=str(request.url.path),
                    device_info=request.headers.get('user-agent', ''),
                    network_condition=self._get_network_condition(request),
                    additional_metadata={
                        "error": True,
                        "error_type": error_details["type"],
                        "status_code": error_details["status_code"]
                    }
                )

    async def _record_error_metrics(self, request: Request, response_time: float, error_details: dict):
        """
        Record error-specific performance metrics.

        Args:
            request: The incoming request
            response_time: Response time in milliseconds
            error_details: Details about the error that occurred
        """
        if not self.enable_performance_monitoring:
            return

        user_id = getattr(request.state, 'user_id', 'anonymous')

        # Record the error as a performance metric
        PerformanceMonitor.record_metric(
            user_id=user_id,
            metric_type=MetricType.API_RESPONSE,
            value=response_time,
            unit="milliseconds",
            api_endpoint=str(request.url.path),
            device_info=request.headers.get('user-agent', ''),
            network_condition=self._get_network_condition(request),
            additional_metadata={
                "error": True,
                "error_type": error_details["type"],
                "status_code": error_details["status_code"],
                "error_message": error_details.get("message", ""),
                "error_class": error_details.get("error_class", ""),
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        # Log the error for monitoring
        logger.error(
            f"API Error - Endpoint: {request.url.path}, "
            f"Method: {request.method}, "
            f"User: {user_id}, "
            f"Response Time: {response_time:.2f}ms, "
            f"Error: {error_details['type']} - {error_details.get('message', '')}"
        )

    def _get_network_condition(self, request: Request) -> str:
        """
        Determine network condition based on request headers.

        Args:
            request: The incoming request

        Returns:
            String representing network condition
        """
        # Check for common network condition indicators
        connection = request.headers.get('connection', '').lower()
        user_agent = request.headers.get('user-agent', '').lower()

        if 'slow' in connection or '2g' in user_agent or 'edge' in user_agent:
            return 'slow_2g'
        elif '3g' in user_agent:
            return 'slow_3g'
        elif '4g' in user_agent or 'lte' in user_agent:
            return 'fast_3g'
        else:
            return '4g'


def setup_error_handling(app, enable_performance_monitoring: bool = True):
    """
    Set up error handling middleware for the application.

    Args:
        app: FastAPI application instance
        enable_performance_monitoring: Whether to enable performance monitoring
    """
    app.add_middleware(
        ErrorHandlerMiddleware,
        enable_performance_monitoring=enable_performance_monitoring
    )


def log_api_call(user_id: str, endpoint: str, method: str, response_time: float,
                 status_code: int, success: bool = True):
    """
    Log an API call with performance metrics.

    Args:
        user_id: ID of the user making the call
        endpoint: API endpoint that was called
        method: HTTP method used
        response_time: Time taken to process the request in milliseconds
        status_code: HTTP status code returned
        success: Whether the call was successful
    """
    try:
        PerformanceMonitor.record_metric(
            user_id=user_id,
            metric_type=MetricType.API_RESPONSE,
            value=response_time,
            unit="milliseconds",
            api_endpoint=f"{method} {endpoint}",
            additional_metadata={
                "http_method": method,
                "status_code": status_code,
                "success": success,
                "timestamp": datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"Failed to log API call metrics: {str(e)}")


def validate_input_schema(data: dict, schema: dict, endpoint: str = "unknown"):
    """
    Validate input data against a schema and log performance.

    Args:
        data: Input data to validate
        schema: Expected schema
        endpoint: Endpoint name for logging

    Returns:
        Tuple of (is_valid, errors)
    """
    start_time = time.time()

    try:
        # Perform basic validation
        is_valid, errors = _validate_schema(data, schema)

        # Log validation performance
        response_time = (time.time() - start_time) * 1000

        PerformanceMonitor.record_metric(
            user_id="system",  # System-level metric
            metric_type=MetricType.API_RESPONSE,
            value=response_time,
            unit="milliseconds",
            api_endpoint=f"validation_{endpoint}",
            additional_metadata={
                "validation_success": is_valid,
                "error_count": len(errors) if errors else 0,
                "data_size": len(json.dumps(data)) if isinstance(data, dict) else len(str(data))
            }
        )

        return is_valid, errors

    except Exception as e:
        logger.error(f"Schema validation error: {str(e)}")
        return False, [str(e)]


def _validate_schema(data: dict, schema: dict) -> tuple[bool, list[str]]:
    """
    Internal function to validate data against schema.

    Args:
        data: Data to validate
        schema: Schema to validate against

    Returns:
        Tuple of (is_valid, errors)
    """
    errors = []

    # Check required fields
    required_fields = schema.get('required', [])
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")

    # Check field types (basic validation)
    properties = schema.get('properties', {})
    for field, field_spec in properties.items():
        if field in data:
            expected_type = field_spec.get('type')
            actual_value = data[field]

            if expected_type == 'string' and not isinstance(actual_value, str):
                errors.append(f"Field {field} should be string, got {type(actual_value).__name__}")
            elif expected_type == 'integer' and not isinstance(actual_value, int):
                errors.append(f"Field {field} should be integer, got {type(actual_value).__name__}")
            elif expected_type == 'number' and not isinstance(actual_value, (int, float)):
                errors.append(f"Field {field} should be number, got {type(actual_value).__name__}")
            elif expected_type == 'boolean' and not isinstance(actual_value, bool):
                errors.append(f"Field {field} should be boolean, got {type(actual_value).__name__}")
            elif expected_type == 'array' and not isinstance(actual_value, list):
                errors.append(f"Field {field} should be array, got {type(actual_value).__name__}")
            elif expected_type == 'object' and not isinstance(actual_value, dict):
                errors.append(f"Field {field} should be object, got {type(actual_value).__name__}")

    return len(errors) == 0, errors


def safe_execute(func, *args, **kwargs):
    """
    Safely execute a function with error handling and performance monitoring.

    Args:
        func: Function to execute
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        Tuple of (result, error)
    """
    start_time = time.time()
    user_id = kwargs.pop('user_id', 'anonymous')  # Extract user_id if provided

    try:
        result = func(*args, **kwargs)

        # Log successful execution
        response_time = (time.time() - start_time) * 1000
        PerformanceMonitor.record_metric(
            user_id=user_id,
            metric_type=MetricType.API_RESPONSE,
            value=response_time,
            unit="milliseconds",
            api_endpoint=f"function_{func.__name__}",
            additional_metadata={
                "execution_success": True,
                "function_name": func.__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
        )

        return result, None

    except Exception as e:
        # Log failed execution
        response_time = (time.time() - start_time) * 1000
        error_details = {
            "error_type": type(e).__name__,
            "error_message": str(e),
            "function_name": func.__name__,
            "timestamp": datetime.utcnow().isoformat(),
            "traceback": traceback.format_exc()
        }

        PerformanceMonitor.record_metric(
            user_id=user_id,
            metric_type=MetricType.API_RESPONSE,
            value=response_time,
            unit="milliseconds",
            api_endpoint=f"function_{func.__name__}",
            additional_metadata={
                "execution_success": False,
                "error_details": error_details
            }
        )

        logger.error(f"Function execution error in {func.__name__}: {str(e)}", exc_info=True)

        return None, e


# Error handler for specific exception types
def handle_validation_error(exc: Exception, request: Request) -> JSONResponse:
    """
    Handle validation errors specifically.

    Args:
        exc: The validation exception
        request: The incoming request

    Returns:
        JSONResponse with error details
    """
    logger.warning(f"Validation error: {str(exc)}")

    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation failed",
            "status_code": 422,
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


def handle_business_logic_error(exc: Exception, request: Request) -> JSONResponse:
    """
    Handle business logic errors specifically.

    Args:
        exc: The business logic exception
        request: The incoming request

    Returns:
        JSONResponse with error details
    """
    logger.warning(f"Business logic error: {str(exc)}")

    return JSONResponse(
        status_code=400,
        content={
            "error": "Business logic error",
            "status_code": 400,
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )


def handle_resource_not_found(exc: Exception, request: Request) -> JSONResponse:
    """
    Handle resource not found errors specifically.

    Args:
        exc: The not found exception
        request: The incoming request

    Returns:
        JSONResponse with error details
    """
    logger.info(f"Resource not found: {str(exc)}")

    return JSONResponse(
        status_code=404,
        content={
            "error": "Resource not found",
            "status_code": 404,
            "message": str(exc),
            "timestamp": datetime.utcnow().isoformat()
        }
    )