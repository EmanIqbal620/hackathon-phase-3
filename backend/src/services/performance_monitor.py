"""
Performance Monitoring Service
This module provides functionality for tracking and analyzing application performance metrics.
"""
from typing import Dict, List, Optional, Union
from sqlmodel import Session, select
from datetime import datetime, timedelta
from enum import Enum
import time
import logging
from functools import wraps
from ..models.performance import PerformanceMetrics, PerformanceMetricsCreate
from ..database import sync_engine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MetricType(str, Enum):
    """Enumeration of supported performance metric types"""
    PAGE_LOAD = "page_load"
    API_RESPONSE = "api_response"
    ANIMATION_FRAME = "animation_frame"
    INTERACTION_RESPONSE = "interaction_response"
    DATABASE_QUERY = "database_query"
    CACHE_HIT = "cache_hit"
    CACHE_MISS = "cache_miss"
    FILE_UPLOAD = "file_upload"
    FILE_DOWNLOAD = "file_download"


class PerformanceMonitor:
    """Service class for monitoring and analyzing application performance."""

    @staticmethod
    def record_metric(
        user_id: str,
        metric_type: MetricType,
        value: float,
        unit: str,
        page_route: Optional[str] = None,
        api_endpoint: Optional[str] = None,
        device_info: Optional[str] = None,
        network_condition: Optional[str] = None,
        additional_metadata: Optional[Dict] = None
    ) -> PerformanceMetrics:
        """
        Record a performance metric.

        Args:
            user_id: ID of the user associated with the metric
            metric_type: Type of performance metric being recorded
            value: Measured value of the metric
            unit: Unit of measurement (e.g., milliseconds, seconds, frames_per_second)
            page_route: Page or route associated with the metric
            api_endpoint: API endpoint associated with the metric
            device_info: Information about the user's device
            network_condition: Network condition during measurement
            additional_metadata: Additional metadata to store with the metric

        Returns:
            Created PerformanceMetrics object
        """
        with Session(sync_engine) as session:
            metric_data = PerformanceMetricsCreate(
                user_id=user_id,
                metric_type=metric_type,
                value=value,
                unit=unit,
                page_route=page_route,
                api_endpoint=api_endpoint,
                device_info=device_info,
                network_condition=network_condition,
                additional_metadata=additional_metadata or {}
            )

            new_metric = PerformanceMetrics.model_validate(metric_data)
            session.add(new_metric)
            session.commit()
            session.refresh(new_metric)

            logger.debug(f"Recorded performance metric: {metric_type.value} = {value}{unit} for user {user_id}")
            return new_metric

    @staticmethod
    def get_user_metrics(
        user_id: str,
        metric_type: Optional[MetricType] = None,
        time_range_hours: int = 24,
        limit: int = 100
    ) -> List[PerformanceMetrics]:
        """
        Get performance metrics for a specific user.

        Args:
            user_id: ID of the user to get metrics for
            metric_type: Optional filter by metric type
            time_range_hours: Time range in hours to fetch metrics for (default 24)
            limit: Maximum number of metrics to return (default 100)

        Returns:
            List of PerformanceMetrics objects
        """
        with Session(sync_engine) as session:
            # Calculate time threshold
            time_threshold = datetime.utcnow() - timedelta(hours=time_range_hours)

            query = select(PerformanceMetrics).where(
                PerformanceMetrics.user_id == user_id,
                PerformanceMetrics.timestamp >= time_threshold
            )

            if metric_type:
                query = query.where(PerformanceMetrics.metric_type == metric_type)

            # Order by timestamp descending and limit results
            query = query.order_by(PerformanceMetrics.timestamp.desc()).limit(limit)

            metrics = session.exec(query).all()
            logger.debug(f"Retrieved {len(metrics)} metrics for user {user_id}")
            return metrics

    @staticmethod
    def get_aggregated_metrics(
        user_id: str,
        metric_type: MetricType,
        time_range_hours: int = 24
    ) -> Dict[str, Union[float, int]]:
        """
        Get aggregated performance metrics for a user.

        Args:
            user_id: ID of the user to get metrics for
            metric_type: Type of metric to aggregate
            time_range_hours: Time range in hours to aggregate metrics for

        Returns:
            Dictionary with aggregated metrics (avg, min, max, count)
        """
        with Session(sync_engine) as session:
            time_threshold = datetime.utcnow() - timedelta(hours=time_range_hours)

            query = select(PerformanceMetrics).where(
                PerformanceMetrics.user_id == user_id,
                PerformanceMetrics.metric_type == metric_type,
                PerformanceMetrics.timestamp >= time_threshold
            )

            metrics = session.exec(query).all()

            if not metrics:
                return {
                    "average": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "count": 0,
                    "time_range_hours": time_range_hours
                }

            values = [m.value for m in metrics]
            avg_value = sum(values) / len(values)
            min_value = min(values)
            max_value = max(values)

            result = {
                "average": avg_value,
                "min": min_value,
                "max": max_value,
                "count": len(values),
                "time_range_hours": time_range_hours,
                "unit": metrics[0].unit if metrics else "unknown"
            }

            logger.debug(f"Aggregated metrics for user {user_id}, type {metric_type.value}: {result}")
            return result

    @staticmethod
    def get_system_wide_metrics(
        metric_type: MetricType,
        time_range_hours: int = 24,
        limit_users: int = 1000
    ) -> Dict[str, Union[float, int, List[Dict]]]:
        """
        Get system-wide performance metrics across all users.

        Args:
            metric_type: Type of metric to aggregate
            time_range_hours: Time range in hours to aggregate metrics for
            limit_users: Maximum number of users to include in calculation

        Returns:
            Dictionary with system-wide aggregated metrics
        """
        with Session(sync_engine) as session:
            time_threshold = datetime.utcnow() - timedelta(hours=time_range_hours)

            # Get a sample of users to avoid performance issues with large datasets
            user_query = select(PerformanceMetrics.user_id).distinct().limit(limit_users)
            user_ids = [row for row in session.exec(user_query)]

            # Get metrics for these users
            query = select(PerformanceMetrics).where(
                PerformanceMetrics.metric_type == metric_type,
                PerformanceMetrics.timestamp >= time_threshold,
                PerformanceMetrics.user_id.in_(user_ids)
            )

            metrics = session.exec(query).all()

            if not metrics:
                return {
                    "average": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "count": 0,
                    "unique_users": 0,
                    "time_range_hours": time_range_hours
                }

            values = [m.value for m in metrics]
            avg_value = sum(values) / len(values) if values else 0.0
            min_value = min(values) if values else 0.0
            max_value = max(values) if values else 0.0
            unique_users = len(set(m.user_id for m in metrics))

            result = {
                "average": avg_value,
                "min": min_value,
                "max": max_value,
                "count": len(values),
                "unique_users": unique_users,
                "time_range_hours": time_range_hours,
                "unit": metrics[0].unit if metrics else "unknown"
            }

            logger.info(f"System-wide metrics for {metric_type.value}: {result}")
            return result

    @staticmethod
    def get_performance_trends(
        user_id: str,
        metric_type: MetricType,
        days: int = 7
    ) -> List[Dict[str, Union[str, float]]]:
        """
        Get performance trends over time for a user.

        Args:
            user_id: ID of the user to get trends for
            metric_type: Type of metric to get trends for
            days: Number of days to include in trend analysis

        Returns:
            List of daily average metrics
        """
        with Session(sync_engine) as session:
            from sqlalchemy import func
            from datetime import date

            # Calculate date threshold
            date_threshold = datetime.utcnow() - timedelta(days=days)

            # Group metrics by date and calculate averages
            subquery = select(
                PerformanceMetrics,
                func.date(PerformanceMetrics.timestamp).label('date_only')
            ).where(
                PerformanceMetrics.user_id == user_id,
                PerformanceMetrics.metric_type == metric_type,
                PerformanceMetrics.timestamp >= date_threshold
            ).subquery()

            query = select(
                func.avg(subquery.c.value).label('avg_value'),
                func.min(subquery.c.value).label('min_value'),
                func.max(subquery.c.value).label('max_value'),
                func.count(subquery.c.value).label('count'),
                subquery.c.date_only.label('date')
            ).group_by(subquery.c.date_only).order_by(subquery.c.date_only)

            results = session.exec(query).all()

            trends = []
            for result in results:
                trends.append({
                    "date": result.date.isoformat() if hasattr(result.date, 'isoformat') else str(result.date),
                    "average": float(result.avg_value) if result.avg_value else 0.0,
                    "min": float(result.min_value) if result.min_value else 0.0,
                    "max": float(result.max_value) if result.max_value else 0.0,
                    "count": int(result.count) if result.count else 0
                })

            logger.debug(f"Retrieved {len(trends)} trend data points for user {user_id}, type {metric_type.value}")
            return trends

    @staticmethod
    def get_slow_endpoints(time_range_hours: int = 24, threshold_ms: float = 1000.0) -> List[Dict[str, Union[str, float]]]:
        """
        Identify slow-performing API endpoints.

        Args:
            time_range_hours: Time range in hours to analyze
            threshold_ms: Threshold in milliseconds for considering an endpoint "slow"

        Returns:
            List of slow endpoints with performance data
        """
        with Session(sync_engine) as session:
            time_threshold = datetime.utcnow() - timedelta(hours=time_range_hours)

            query = select(PerformanceMetrics).where(
                PerformanceMetrics.metric_type == MetricType.API_RESPONSE,
                PerformanceMetrics.timestamp >= time_threshold,
                PerformanceMetrics.value >= threshold_ms
            ).order_by(PerformanceMetrics.value.desc())

            slow_metrics = session.exec(query).all()

            # Group by endpoint and calculate averages
            endpoint_stats = {}
            for metric in slow_metrics:
                if not metric.api_endpoint:
                    continue

                if metric.api_endpoint not in endpoint_stats:
                    endpoint_stats[metric.api_endpoint] = {
                        "endpoint": metric.api_endpoint,
                        "count": 0,
                        "total_time": 0.0,
                        "min_time": float('inf'),
                        "max_time": 0.0,
                        "samples": []
                    }

                stats = endpoint_stats[metric.api_endpoint]
                stats["count"] += 1
                stats["total_time"] += metric.value
                stats["min_time"] = min(stats["min_time"], metric.value)
                stats["max_time"] = max(stats["max_time"], metric.value)
                stats["samples"].append(metric.value)

            # Calculate averages and format results
            slow_endpoints = []
            for endpoint, stats in endpoint_stats.items():
                avg_time = stats["total_time"] / stats["count"] if stats["count"] > 0 else 0
                slow_endpoints.append({
                    "endpoint": endpoint,
                    "average_response_time_ms": avg_time,
                    "max_response_time_ms": stats["max_time"],
                    "min_response_time_ms": stats["min_time"] if stats["min_time"] != float('inf') else 0,
                    "request_count": stats["count"],
                    "p95_response_time_ms": PerformanceMonitor._calculate_percentile(stats["samples"], 95) if stats["samples"] else 0
                })

            # Sort by average response time
            slow_endpoints.sort(key=lambda x: x["average_response_time_ms"], reverse=True)

            logger.info(f"Identified {len(slow_endpoints)} slow endpoints")
            return slow_endpoints

    @staticmethod
    def _calculate_percentile(data: List[float], percentile: float) -> float:
        """
        Calculate percentile of a dataset.

        Args:
            data: List of numeric values
            percentile: Percentile to calculate (0-100)

        Returns:
            Calculated percentile value
        """
        if not data:
            return 0.0

        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_data) - 1)

        if lower_index == upper_index:
            return sorted_data[lower_index]

        # Interpolate between the two values
        fraction = index - lower_index
        return sorted_data[lower_index] + fraction * (sorted_data[upper_index] - sorted_data[lower_index])

    @staticmethod
    def get_performance_summary(user_id: str, time_range_hours: int = 24) -> Dict[str, Union[float, int, str]]:
        """
        Get a comprehensive performance summary for a user.

        Args:
            user_id: ID of the user to get summary for
            time_range_hours: Time range in hours to analyze

        Returns:
            Dictionary with performance summary
        """
        summary = {
            "user_id": user_id,
            "time_range_hours": time_range_hours,
            "generated_at": datetime.utcnow().isoformat(),
            "metrics": {}
        }

        # Get metrics for different types
        for metric_type in MetricType:
            try:
                agg_metrics = PerformanceMonitor.get_aggregated_metrics(
                    user_id, metric_type, time_range_hours
                )
                summary["metrics"][metric_type.value] = agg_metrics
            except Exception as e:
                logger.warning(f"Could not get metrics for {metric_type.value}: {str(e)}")
                summary["metrics"][metric_type.value] = {
                    "average": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "count": 0,
                    "time_range_hours": time_range_hours
                }

        # Add trend information
        try:
            page_load_trends = PerformanceMonitor.get_performance_trends(
                user_id, MetricType.PAGE_LOAD, 7
            )
            summary["trends"] = {
                "page_load_improving": len(page_load_trends) > 1 and page_load_trends[-1]["average"] < page_load_trends[0]["average"],
                "recent_days_data_points": len(page_load_trends)
            }
        except Exception as e:
            logger.warning(f"Could not get trends: {str(e)}")
            summary["trends"] = {}

        logger.info(f"Generated performance summary for user {user_id}")
        return summary


def performance_monitor_decorator(metric_type: MetricType, unit: str = "milliseconds"):
    """
    Decorator to automatically monitor the performance of functions.

    Args:
        metric_type: Type of performance metric to record
        unit: Unit of measurement for the metric

    Returns:
        Decorated function that records performance metrics
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            # Try to extract user_id from arguments (common patterns)
            user_id = "unknown"
            if args:
                # Check if first arg has user_id attribute (like TokenData)
                if hasattr(args[0], 'user_id'):
                    user_id = getattr(args[0], 'user_id', 'unknown')
                elif isinstance(args[0], dict) and 'user_id' in args[0]:
                    user_id = args[0]['user_id']

            try:
                result = func(*args, **kwargs)
                end_time = time.time()

                # Calculate duration in the appropriate unit
                if unit == "milliseconds":
                    duration = (end_time - start_time) * 1000
                elif unit == "seconds":
                    duration = end_time - start_time
                else:
                    duration = end_time - start_time  # default to seconds

                # Record the metric
                try:
                    PerformanceMonitor.record_metric(
                        user_id=user_id,
                        metric_type=metric_type,
                        value=duration,
                        unit=unit,
                        api_endpoint=f"/api/{func.__name__}" if func.__name__ else "unknown"
                    )
                except Exception as e:
                    logger.error(f"Failed to record performance metric: {str(e)}")

                return result
            except Exception as e:
                end_time = time.time()

                # Record the duration even if the function failed
                if unit == "milliseconds":
                    duration = (end_time - start_time) * 1000
                elif unit == "seconds":
                    duration = end_time - start_time
                else:
                    duration = end_time - start_time  # default to seconds

                try:
                    PerformanceMonitor.record_metric(
                        user_id=user_id,
                        metric_type=metric_type,
                        value=duration,
                        unit=unit,
                        api_endpoint=f"/api/{func.__name__}" if func.__name__ else "unknown",
                        additional_metadata={"error": str(e)}
                    )
                except Exception as record_error:
                    logger.error(f"Failed to record error performance metric: {str(record_error)}")

                raise e

        return wrapper
    return decorator


# Example usage of the decorator
@performance_monitor_decorator(MetricType.API_RESPONSE, "milliseconds")
def example_monitored_function(user_id: str):
    """
    Example function demonstrating how to use the performance monitor decorator.

    Args:
        user_id: ID of the user performing the action
    """
    # Simulate some work
    time.sleep(0.1)
    return {"status": "completed", "user_id": user_id}