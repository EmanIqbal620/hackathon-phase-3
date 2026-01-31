"""
Performance Optimizer Service
This module provides business logic for optimizing application performance and managing caching.
"""
from typing import Dict, Any, Optional
from sqlmodel import Session, select
from datetime import datetime, timedelta
from ..models import Task
from ..models.performance import PerformanceMetrics
from ..database import sync_engine
import logging
from functools import wraps
import time


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceOptimizerService:
    """Service class for handling performance optimization and caching."""

    @staticmethod
    def cache_response(cache_duration: int = 300):
        """
        Decorator to cache API responses for performance optimization.

        Args:
            cache_duration: Duration to cache responses in seconds (default: 300 = 5 minutes)
        """
        def decorator(func):
            cache = {}

            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Create cache key based on function name and arguments
                cache_key = f"{func.__name__}:{str(args)}:{str(sorted(kwargs.items()))}"

                # Check if result is in cache and not expired
                if cache_key in cache:
                    result, timestamp = cache[cache_key]
                    if time.time() - timestamp < cache_duration:
                        logger.info(f"Cache hit for {cache_key}")
                        return result
                    else:
                        # Remove expired cache entry
                        del cache[cache_key]

                # Execute function and cache result
                result = await func(*args, **kwargs)
                cache[cache_key] = (result, time.time())
                logger.info(f"Cached response for {cache_key}")
                return result

            return wrapper
        return decorator

    @staticmethod
    async def optimize_task_queries(user_id: str, filters: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Optimize database queries for task retrieval operations.

        Args:
            user_id: ID of the user to get tasks for
            filters: Optional filters for task query

        Returns:
            Dictionary with optimized query results and performance metrics
        """
        start_time = time.time()

        with Session(sync_engine) as session:
            # Build optimized query with proper indexing
            query = select(Task).where(Task.user_id == user_id)

            # Apply filters if provided
            if filters:
                if "status" in filters:
                    if filters["status"] == "completed":
                        query = query.where(Task.is_completed == True)
                    elif filters["status"] == "pending":
                        query = query.where(Task.is_completed == False)

                if "priority" in filters:
                    query = query.where(Task.priority == filters["priority"])

                if "due_date_start" in filters:
                    query = query.where(Task.due_date >= filters["due_date_start"])

                if "due_date_end" in filters:
                    query = query.where(Task.due_date <= filters["due_date_end"])

            # Execute query with proper ordering
            tasks = session.exec(query.order_by(Task.created_at.desc())).all()

            # Calculate performance metrics
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds

            # Record performance metric
            from .analytics_service import AnalyticsService
            AnalyticsService.record_query_performance(
                user_id=user_id,
                query_type="optimized_task_query",
                execution_time_ms=execution_time,
                result_count=len(tasks)
            )

            logger.info(f"Optimized task query executed in {execution_time:.2f}ms for user {user_id}")

            return {
                "tasks": tasks,
                "execution_time_ms": execution_time,
                "result_count": len(tasks),
                "optimized": True
            }

    @staticmethod
    def get_cached_analytics(user_id: str, time_range: str = "week") -> Optional[Dict[str, Any]]:
        """
        Get cached analytics if available and not expired.

        Args:
            user_id: ID of the user to get analytics for
            time_range: Time range for analytics

        Returns:
            Cached analytics data if available, None otherwise
        """
        # In a real implementation, this would check a cache like Redis
        # For now, we'll simulate with a simple in-memory cache
        # This is a simplified version - in production, use Redis or similar
        return None

    @staticmethod
    def cache_analytics(user_id: str, time_range: str, data: Dict[str, Any]) -> bool:
        """
        Cache analytics data for future requests.

        Args:
            user_id: ID of the user
            time_range: Time range for analytics
            data: Analytics data to cache

        Returns:
            True if successfully cached, False otherwise
        """
        # In a real implementation, this would store in Redis or similar
        # For now, we'll just return True to simulate caching
        logger.info(f"Cached analytics for user {user_id}, time_range {time_range}")
        return True

    @staticmethod
    async def optimize_analytics_calculation(user_id: str, time_range: str = "week") -> Dict[str, Any]:
        """
        Optimize analytics calculation with caching and efficient querying.

        Args:
            user_id: ID of the user to calculate analytics for
            time_range: Time range for analytics calculation

        Returns:
            Optimized analytics data
        """
        start_time = time.time()

        # Try to get from cache first
        cached_result = PerformanceOptimizerService.get_cached_analytics(user_id, time_range)
        if cached_result:
            logger.info(f"Analytics served from cache for user {user_id}")
            return cached_result

        # Calculate analytics (this would use the AnalyticsService)
        from .analytics_service import AnalyticsService
        analytics_result = AnalyticsService.calculate_user_analytics(user_id, time_range)

        # Calculate performance metrics
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to milliseconds

        # Record performance metric
        PerformanceOptimizerService.record_performance_metric(
            user_id=user_id,
            metric_type="analytics_calculation",
            value=execution_time,
            unit="milliseconds",
            metadata={
                "time_range": time_range,
                "result_size": len(str(analytics_result))
            }
        )

        # Cache the result for future requests
        PerformanceOptimizerService.cache_analytics(user_id, time_range, analytics_result)

        logger.info(f"Optimized analytics calculation completed in {execution_time:.2f}ms for user {user_id}")

        return {
            "analytics": analytics_result,
            "execution_time_ms": execution_time,
            "cached": True
        }

    @staticmethod
    def record_performance_metric(
        user_id: str,
        metric_type: str,
        value: float,
        unit: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record a performance metric to the database.

        Args:
            user_id: ID of the user associated with the metric
            metric_type: Type of performance metric
            value: Measured value
            unit: Unit of measurement
            metadata: Additional metadata about the metric

        Returns:
            True if successfully recorded, False otherwise
        """
        try:
            with Session(sync_engine) as session:
                # Create performance metric record
                performance_metric = PerformanceMetrics(
                    user_id=user_id,
                    metric_type=metric_type,
                    value=value,
                    unit=unit,
                    page_route="n/a",
                    api_endpoint="n/a",
                    device_info="n/a",
                    network_condition="n/a",
                    metadata=metadata
                )

                # Add to session and commit
                session.add(performance_metric)
                session.commit()

                logger.info(f"Performance metric recorded: {metric_type} = {value}{unit} for user {user_id}")
                return True

        except Exception as e:
            logger.error(f"Error recording performance metric: {str(e)}")
            return False

    @staticmethod
    def get_performance_summary(user_id: str, time_range: str = "week") -> Dict[str, Any]:
        """
        Get performance summary for a user.

        Args:
            user_id: ID of the user to get performance summary for
            time_range: Time range for performance metrics

        Returns:
            Performance summary with averages and trends
        """
        with Session(sync_engine) as session:
            # Calculate date range based on time_range
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

            # Query performance metrics
            query = select(PerformanceMetrics).where(
                PerformanceMetrics.user_id == user_id,
                PerformanceMetrics.created_at >= start_date
            )
            metrics = session.exec(query).all()

            if not metrics:
                return {
                    "user_id": user_id,
                    "time_range": time_range,
                    "summary": {
                        "total_metrics": 0,
                        "avg_response_time_ms": 0,
                        "p95_response_time_ms": 0,
                        "p99_response_time_ms": 0
                    }
                }

            # Calculate summary statistics
            values = [m.value for m in metrics if m.unit == "milliseconds"]
            if not values:
                # If no millisecond metrics, return zeros
                return {
                    "user_id": user_id,
                    "time_range": time_range,
                    "summary": {
                        "total_metrics": len(metrics),
                        "avg_response_time_ms": 0,
                        "p95_response_time_ms": 0,
                        "p99_response_time_ms": 0
                    }
                }

            # Calculate statistics
            avg_response_time = sum(values) / len(values)
            sorted_values = sorted(values)

            # Calculate percentiles
            p95_idx = int(len(sorted_values) * 0.95)
            p99_idx = int(len(sorted_values) * 0.99)

            p95_response_time = sorted_values[min(p95_idx, len(sorted_values) - 1)]
            p99_response_time = sorted_values[min(p99_idx, len(sorted_values) - 1)]

            # Group metrics by type
            metrics_by_type = {}
            for metric in metrics:
                if metric.metric_type in metrics_by_type:
                    metrics_by_type[metric.metric_type].append(metric.value)
                else:
                    metrics_by_type[metric.metric_type] = [metric.value]

            return {
                "user_id": user_id,
                "time_range": time_range,
                "summary": {
                    "total_metrics": len(metrics),
                    "avg_response_time_ms": round(avg_response_time, 2),
                    "p95_response_time_ms": round(p95_response_time, 2),
                    "p99_response_time_ms": round(p99_response_time, 2)
                },
                "breakdown_by_type": {
                    metric_type: {
                        "count": len(values),
                        "avg_value": round(sum(values) / len(values), 2),
                        "min_value": min(values),
                        "max_value": max(values)
                    }
                    for metric_type, values in metrics_by_type.items()
                }
            }

    @staticmethod
    def should_refresh_cache(user_id: str, time_range: str) -> bool:
        """
        Determine if cached analytics should be refreshed based on usage patterns.

        Args:
            user_id: ID of the user
            time_range: Time range for analytics

        Returns:
            True if cache should be refreshed, False otherwise
        """
        # Get recent task activity for the user
        with Session(sync_engine) as session:
            # Find tasks created in the last hour
            recent_threshold = datetime.utcnow() - timedelta(hours=1)
            recent_tasks = session.exec(
                select(Task).where(
                    Task.user_id == user_id,
                    Task.created_at >= recent_threshold
                )
            ).all()

            # If user has been active recently, refresh cache
            return len(recent_tasks) > 0

    @staticmethod
    async def optimize_response_time(response_func, *args, **kwargs) -> Dict[str, Any]:
        """
        Wrapper to measure and optimize response time for any function.

        Args:
            response_func: Function to wrap and measure
            *args, **kwargs: Arguments to pass to the function

        Returns:
            Function result with performance metrics
        """
        start_time = time.time()

        try:
            # Execute the function
            result = await response_func(*args, **kwargs)

            # Calculate execution time
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000  # Convert to milliseconds

            # Log performance if it exceeded threshold
            if execution_time > 500:  # Log if response took more than 500ms
                logger.warning(f"Slow response detected: {execution_time:.2f}ms")

            return {
                "result": result,
                "response_time_ms": execution_time,
                "optimized": True
            }

        except Exception as e:
            end_time = time.time()
            execution_time = (end_time - start_time) * 1000

            logger.error(f"Error in optimized function execution: {str(e)}, response time: {execution_time:.2f}ms")
            raise e