"""
Performance Monitoring Middleware
This module provides middleware for tracking and monitoring API performance metrics.
"""
import time
import logging
from typing import Callable, Awaitable
from fastapi import Request, Response
from fastapi.routing import APIRoute
import uuid
from datetime import datetime
from ..models.performance import PerformanceMetrics, PerformanceMetricsCreate
from ..database import sync_engine
from sqlmodel import Session, select


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware:
    """Middleware to monitor and log performance metrics for API requests."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        start_time = time.time()

        # Capture the response to measure processing time
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                process_time = time.time() - start_time
                response_status = message["status"]

                # Log performance metrics
                await self.record_performance_metric(
                    request=request,
                    process_time=process_time,
                    response_status=response_status
                )

            await send(message)

        await self.app(scope, receive, send_wrapper)

    async def record_performance_metric(
        self,
        request: Request,
        process_time: float,
        response_status: int
    ):
        """Record performance metrics to the database."""
        try:
            # Extract user information if available
            user_id = getattr(request.state, "user_id", "anonymous")

            # Determine the metric type based on the endpoint
            path = request.url.path
            if "/analytics" in path:
                metric_type = "analytics_api_response"
            elif "/chat" in path:
                metric_type = "chat_api_response"
            elif "/tasks" in path:
                metric_type = "task_api_response"
            else:
                metric_type = "general_api_response"

            # Create performance metrics record
            performance_data = PerformanceMetricsCreate(
                user_id=user_id,
                metric_type=metric_type,
                value=process_time * 1000,  # Convert to milliseconds
                unit="milliseconds",
                page_route=path,
                api_endpoint=request.method + " " + path,
                device_info=self._get_device_info(request),
                network_condition=self._get_network_condition(request)
            )

            # Save to database
            with Session(sync_engine) as session:
                performance_record = PerformanceMetrics.model_validate(performance_data)
                session.add(performance_record)
                session.commit()

            # Log for debugging
            logger.info(
                f"Performance metric recorded: {metric_type} took {process_time * 1000:.2f}ms "
                f"for user {user_id}, status {response_status}"
            )

        except Exception as e:
            logger.error(f"Error recording performance metric: {str(e)}")

    def _get_device_info(self, request: Request) -> str:
        """Extract device information from request headers."""
        user_agent = request.headers.get("user-agent", "unknown")

        # Simplified device detection
        if "mobile" in user_agent.lower() or "android" in user_agent.lower() or "iphone" in user_agent.lower():
            device_type = "mobile"
        elif "tablet" in user_agent.lower():
            device_type = "tablet"
        else:
            device_type = "desktop"

        return f"{device_type} ({user_agent[:50]}...)"

    def _get_network_condition(self, request: Request) -> str:
        """Estimate network condition based on request characteristics."""
        # This is a simplified estimation - in a real app, you might use more sophisticated detection
        # based on request size, response time, etc.
        return "unknown"


class PerformanceRoute(APIRoute):
    """Custom API route class that adds performance tracking to each endpoint."""

    def get_route_handler(self) -> Callable[[Request], Awaitable[Response]]:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
            start_time = time.time()

            try:
                response = await original_route_handler(request)

                # Calculate processing time
                process_time = time.time() - start_time

                # Record performance metric
                await self._record_endpoint_performance(
                    request=request,
                    endpoint_path=self.path,
                    process_time=process_time,
                    response=response
                )

                return response
            except Exception as e:
                # Calculate processing time even for errors
                process_time = time.time() - start_time

                # Record performance metric for error case
                await self._record_endpoint_performance(
                    request=request,
                    endpoint_path=self.path,
                    process_time=process_time,
                    response=None,
                    error=e
                )

                raise

        return custom_route_handler

    async def _record_endpoint_performance(
        self,
        request: Request,
        endpoint_path: str,
        process_time: float,
        response: Response = None,
        error: Exception = None
    ):
        """Record performance metrics for a specific endpoint."""
        try:
            # Extract user ID from request if available
            user_id = getattr(request.state, "user_id", "anonymous")

            # Determine metric type based on endpoint
            if "/analytics" in endpoint_path:
                metric_type = "analytics_api_response"
            elif "/chat" in endpoint_path:
                metric_type = "chat_api_response"
            elif "/tasks" in endpoint_path:
                metric_type = "task_api_response"
            elif "/suggestions" in endpoint_path:
                metric_type = "suggestions_api_response"
            elif "/reminders" in endpoint_path:
                metric_type = "reminders_api_response"
            else:
                metric_type = "general_api_response"

            # Create performance metrics record
            performance_data = PerformanceMetricsCreate(
                user_id=user_id,
                metric_type=metric_type,
                value=process_time * 1000,  # Convert to milliseconds
                unit="milliseconds",
                page_route=endpoint_path,
                api_endpoint=request.method + " " + endpoint_path,
                device_info=self._get_device_info(request),
                network_condition=self._get_network_condition(request)
            )

            # Save to database
            with Session(sync_engine) as session:
                performance_record = PerformanceMetrics.model_validate(performance_data)
                session.add(performance_record)
                session.commit()

            # Log performance data
            status = "ERROR" if error else (response.status_code if response else "UNKNOWN")
            logger.info(
                f"Endpoint performance: {endpoint_path} took {process_time * 1000:.2f}ms "
                f"for user {user_id}, status {status}"
            )

        except Exception as e:
            logger.error(f"Error recording endpoint performance: {str(e)}")

    def _get_device_info(self, request: Request) -> str:
        """Extract device information from request headers."""
        user_agent = request.headers.get("user-agent", "unknown")

        # Simplified device detection
        if "mobile" in user_agent.lower() or "android" in user_agent.lower() or "iphone" in user_agent.lower():
            device_type = "mobile"
        elif "tablet" in user_agent.lower():
            device_type = "tablet"
        else:
            device_type = "desktop"

        return f"{device_type} ({user_agent[:50]}...)"

    def _get_network_condition(self, request: Request) -> str:
        """Estimate network condition based on request characteristics."""
        # This is a simplified estimation - in a real app, you might use more sophisticated detection
        return "unknown"


def get_performance_summary(user_id: str, time_range: str = "week") -> dict:
    """
    Get performance summary for a user.

    Args:
        user_id: ID of the user to get performance summary for
        time_range: Time range for summary ('day', 'week', 'month', 'quarter')

    Returns:
        Dictionary with performance summary metrics
    """
    with Session(sync_engine) as session:
        # Calculate date range based on time_range
        from datetime import datetime, timedelta
        now = datetime.utcnow()

        if time_range == "day":
            start_date = now - timedelta(days=1)
        elif time_range == "week":
            start_date = now - timedelta(weeks=1)
        elif time_range == "month":
            start_date = now - timedelta(days=30)
        elif time_range == "quarter":
            start_date = now - timedelta(days=90)
        else:  # default to week
            start_date = now - timedelta(weeks=1)

        # Query performance metrics for the time range
        query = select(PerformanceMetrics).where(
            PerformanceMetrics.user_id == user_id,
            PerformanceMetrics.created_at >= start_date
        )
        all_metrics = session.exec(query).all()

        # Calculate summary metrics
        total_requests = len(all_metrics)
        if total_requests == 0:
            return {
                "user_id": user_id,
                "time_range": time_range,
                "total_requests": 0,
                "avg_response_time_ms": 0,
                "p95_response_time_ms": 0,
                "p99_response_time_ms": 0,
                "requests_by_type": {},
                "performance_trend": []
            }

        # Calculate average response time
        total_response_time = sum(metric.value for metric in all_metrics)
        avg_response_time = total_response_time / total_requests

        # Calculate percentiles (simplified)
        sorted_values = sorted([metric.value for metric in all_metrics])
        p95_index = int(len(sorted_values) * 0.95)
        p99_index = int(len(sorted_values) * 0.99)

        p95_response_time = sorted_values[min(p95_index, len(sorted_values) - 1)] if sorted_values else 0
        p99_response_time = sorted_values[min(p99_index, len(sorted_values) - 1)] if sorted_values else 0

        # Count requests by type
        requests_by_type = {}
        for metric in all_metrics:
            metric_type = metric.metric_type
            if metric_type in requests_by_type:
                requests_by_type[metric_type] += 1
            else:
                requests_by_type[metric_type] = 1

        # Calculate performance trend (simplified - just basic trend)
        performance_trend = []
        for i in range(min(7, len(all_metrics))):
            # Sample some metrics to show trend
            if i < len(all_metrics):
                metric = all_metrics[i]
                performance_trend.append({
                    "date": metric.created_at.date().isoformat(),
                    "avg_response_time": metric.value
                })

        return {
            "user_id": user_id,
            "time_range": time_range,
            "total_requests": total_requests,
            "avg_response_time_ms": round(avg_response_time, 2),
            "p95_response_time_ms": round(p95_response_time, 2),
            "p99_response_time_ms": round(p99_response_time, 2),
            "requests_by_type": requests_by_type,
            "performance_trend": performance_trend
        }


def log_performance_event(user_id: str, event_name: str, duration_ms: float, metadata: dict = None):
    """
    Log a specific performance event to the database.

    Args:
        user_id: ID of the user associated with the event
        event_name: Name of the performance event
        duration_ms: Duration of the event in milliseconds
        metadata: Additional metadata about the event
    """
    try:
        with Session(sync_engine) as session:
            performance_data = PerformanceMetricsCreate(
                user_id=user_id,
                metric_type=event_name,
                value=duration_ms,
                unit="milliseconds",
                page_route="n/a",  # Not an API route
                api_endpoint="n/a",  # Not an API endpoint
                device_info="n/a",  # Not an API request
                network_condition="n/a"  # Not an API request
            )

            performance_record = PerformanceMetrics.model_validate(performance_data)
            session.add(performance_record)
            session.commit()

            logger.info(f"Performance event logged: {event_name} took {duration_ms}ms for user {user_id}")

    except Exception as e:
        logger.error(f"Error logging performance event: {str(e)}")