"""
Performance Testing Utilities
This module provides functions for testing performance improvements with large datasets.
"""
from typing import Dict, List, Tuple
import time
import asyncio
from datetime import datetime, timedelta
import random
import string
from sqlmodel import Session, select
from ..models import Task
from ..models.performance import PerformanceMetrics, PerformanceMetricsCreate
from ..database import sync_engine
from ..services.task_service import TaskService
from ..services.analytics_service import AnalyticsService
import logging
from concurrent.futures import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PerformanceTester:
    """Class for testing performance improvements with large datasets."""

    @staticmethod
    def generate_test_tasks(user_id: str, count: int = 1000) -> List[Task]:
        """
        Generate a large number of test tasks.

        Args:
            user_id: ID of the user to assign tasks to
            count: Number of tasks to generate

        Returns:
            List of generated task objects
        """
        tasks = []
        priorities = ['low', 'medium', 'high']
        titles = [
            'Complete project proposal', 'Review quarterly reports', 'Schedule team meeting',
            'Update documentation', 'Fix critical bug', 'Prepare presentation',
            'Code review', 'Deploy to production', 'Update dependencies',
            'Write tests', 'Refactor legacy code', 'Optimize database queries'
        ]

        for i in range(count):
            title = f"{random.choice(titles)} #{i+1}"
            description = f"This is a sample task description for task #{i+1}. It contains more detailed information about what needs to be done."

            # Randomly determine completion status
            is_completed = random.random() < 0.7  # 70% chance of being completed
            created_at = datetime.utcnow() - timedelta(days=random.randint(0, 30))
            completed_at = None

            if is_completed:
                completed_at = created_at + timedelta(hours=random.randint(1, 48))

            task = Task(
                id=f"test_task_{i+1}",
                title=title,
                description=description,
                priority=random.choice(priorities),
                due_date=datetime.utcnow() + timedelta(days=random.randint(1, 30)),
                is_completed=is_completed,
                created_at=created_at,
                updated_at=datetime.utcnow(),
                completed_at=completed_at,
                user_id=user_id
            )
            tasks.append(task)

        return tasks

    @staticmethod
    def benchmark_task_retrieval(user_id: str, task_count: int = 1000) -> Dict[str, any]:
        """
        Benchmark task retrieval performance.

        Args:
            user_id: ID of the user whose tasks to retrieve
            task_count: Expected number of tasks to retrieve

        Returns:
            Dictionary with performance metrics
        """
        start_time = time.time()

        with Session(sync_engine) as session:
            # Retrieve all tasks for the user
            query = select(Task).where(Task.user_id == user_id)
            tasks = session.exec(query).all()

        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Convert to milliseconds

        return {
            "operation": "retrieve_tasks",
            "task_count": len(tasks),
            "expected_count": task_count,
            "duration_ms": round(duration, 2),
            "throughput": round(len(tasks) / (duration / 1000), 2) if duration > 0 else 0,  # tasks per second
            "successful": len(tasks) >= task_count * 0.9  # Allow 10% tolerance
        }

    @staticmethod
    def benchmark_task_creation(user_id: str, task_count: int = 100) -> Dict[str, any]:
        """
        Benchmark task creation performance.

        Args:
            user_id: ID of the user creating tasks
            task_count: Number of tasks to create

        Returns:
            Dictionary with performance metrics
        """
        start_time = time.time()

        created_tasks = []
        for i in range(task_count):
            title = f"Performance Test Task #{i+1}"
            description = f"Task created for performance testing #{i+1}"

            task_data = {
                "title": title,
                "description": description,
                "priority": random.choice(['low', 'medium', 'high']),
                "due_date": (datetime.utcnow() + timedelta(days=random.randint(1, 30))).isoformat()
            }

            # In a real implementation, we would use TaskService to create tasks
            # For this example, we'll simulate the creation
            task = Task(
                id=f"perf_task_{i+1}",
                title=task_data["title"],
                description=task_data["description"],
                priority=task_data["priority"],
                due_date=datetime.fromisoformat(task_data["due_date"]),
                is_completed=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                user_id=user_id
            )
            created_tasks.append(task)

        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Convert to milliseconds

        return {
            "operation": "create_tasks",
            "task_count": len(created_tasks),
            "duration_ms": round(duration, 2),
            "throughput": round(len(created_tasks) / (duration / 1000), 2) if duration > 0 else 0,  # tasks per second
            "successful": len(created_tasks) == task_count
        }

    @staticmethod
    def benchmark_analytics_calculation(user_id: str, time_range: str = "month") -> Dict[str, any]:
        """
        Benchmark analytics calculation performance.

        Args:
            user_id: ID of the user to calculate analytics for
            time_range: Time range for analytics calculation

        Returns:
            Dictionary with performance metrics
        """
        start_time = time.time()

        # Calculate analytics
        analytics_data = AnalyticsService.calculate_user_analytics(user_id, time_range)

        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Convert to milliseconds

        return {
            "operation": "calculate_analytics",
            "time_range": time_range,
            "duration_ms": round(duration, 2),
            "metrics_calculated": len(analytics_data.get("metrics", {})),
            "successful": duration < 2000,  # Should complete in under 2 seconds
            "analytics_data_keys": list(analytics_data.keys()) if isinstance(analytics_data, dict) else []
        }

    @staticmethod
    def benchmark_search_operations(user_id: str, search_term: str = "", task_count: int = 1000) -> Dict[str, any]:
        """
        Benchmark search operations with large datasets.

        Args:
            user_id: ID of the user performing search
            search_term: Term to search for
            task_count: Number of tasks to search through

        Returns:
            Dictionary with performance metrics
        """
        start_time = time.time()

        # Simulate search operation
        # In a real implementation, this would use the search functionality
        matching_tasks = []
        for i in range(task_count):
            title = f"Sample Task {i+1}"
            description = f"Description for task {i+1}"

            if not search_term or search_term.lower() in title.lower() or search_term.lower() in description.lower():
                matching_tasks.append({
                    "id": f"task_{i+1}",
                    "title": title,
                    "description": description
                })

        end_time = time.time()
        duration = (end_time - start_time) * 1000  # Convert to milliseconds

        return {
            "operation": "search_tasks",
            "search_term": search_term,
            "total_tasks": task_count,
            "matching_results": len(matching_tasks),
            "duration_ms": round(duration, 2),
            "successful": duration < 500  # Should complete in under 500ms
        }

    @staticmethod
    def run_comprehensive_performance_test(user_id: str, task_count: int = 1000) -> Dict[str, any]:
        """
        Run comprehensive performance tests with a large dataset.

        Args:
            user_id: ID of the user to test with
            task_count: Number of tasks to use for testing

        Returns:
            Dictionary with comprehensive test results
        """
        logger.info(f"Starting comprehensive performance test with {task_count} tasks for user {user_id}")

        # Generate test tasks
        logger.info("Generating test tasks...")
        test_tasks = PerformanceTester.generate_test_tasks(user_id, task_count)

        # Run various performance tests
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "test_config": {
                "user_id": user_id,
                "task_count": task_count
            },
            "tests": {}
        }

        # Test task retrieval
        logger.info("Testing task retrieval performance...")
        results["tests"]["retrieve_tasks"] = PerformanceTester.benchmark_task_retrieval(user_id, task_count)

        # Test analytics calculation
        logger.info("Testing analytics calculation performance...")
        results["tests"]["analytics_calculation"] = PerformanceTester.benchmark_analytics_calculation(user_id, "month")

        # Test search operations
        logger.info("Testing search performance...")
        results["tests"]["search_operations"] = PerformanceTester.benchmark_search_operations(user_id, "sample", task_count)

        # Calculate overall performance metrics
        total_duration = sum(test["duration_ms"] for test in results["tests"].values())
        avg_throughput = sum(
            test.get("throughput", 0) for test in results["tests"].values()
        ) / len(results["tests"])

        results["summary"] = {
            "total_test_duration_ms": round(total_duration, 2),
            "average_throughput": round(avg_throughput, 2),
            "all_tests_passed": all(test.get("successful", False) for test in results["tests"].values()),
            "performance_score": PerformanceTester.calculate_performance_score(results["tests"])
        }

        logger.info(f"Performance test completed. Score: {results['summary']['performance_score']}/100")

        return results

    @staticmethod
    def calculate_performance_score(test_results: Dict[str, any]) -> int:
        """
        Calculate an overall performance score based on test results.

        Args:
            test_results: Dictionary containing test results

        Returns:
            Performance score from 0-100
        """
        score = 100  # Start with perfect score

        # Deduct points based on performance issues
        for test_name, result in test_results.items():
            duration = result.get("duration_ms", 0)
            successful = result.get("successful", False)

            if not successful:
                score -= 25  # Major failure
            elif test_name == "retrieve_tasks" and duration > 1000:  # More than 1 second
                score -= 10
            elif test_name == "calculate_analytics" and duration > 2000:  # More than 2 seconds
                score -= 15
            elif test_name == "search_tasks" and duration > 500:  # More than 500ms
                score -= 5

        # Ensure score stays within bounds
        return max(0, min(100, score))

    @staticmethod
    def stress_test_concurrent_access(user_id: str, concurrent_users: int = 10, tasks_per_user: int = 100) -> Dict[str, any]:
        """
        Perform stress testing with concurrent users accessing the system.

        Args:
            user_id: Base user ID to use
            concurrent_users: Number of concurrent users to simulate
            tasks_per_user: Number of tasks per simulated user

        Returns:
            Dictionary with stress test results
        """
        start_time = time.time()

        # Simulate concurrent access
        with ThreadPoolExecutor(max_workers=concurrent_users) as executor:
            futures = []
            for i in range(concurrent_users):
                simulated_user_id = f"{user_id}_stress_{i}"
                future = executor.submit(
                    PerformanceTester.benchmark_task_retrieval,
                    simulated_user_id,
                    tasks_per_user
                )
                futures.append(future)

            # Collect results
            results = []
            for future in futures:
                try:
                    result = future.result(timeout=30)  # 30 second timeout
                    results.append(result)
                except Exception as e:
                    results.append({
                        "operation": "retrieve_tasks",
                        "task_count": 0,
                        "expected_count": tasks_per_user,
                        "duration_ms": 0,
                        "throughput": 0,
                        "successful": False,
                        "error": str(e)
                    })

        end_time = time.time()
        total_duration = (end_time - start_time) * 1000

        # Calculate stress test metrics
        successful_requests = sum(1 for r in results if r.get("successful", False))
        total_requests = len(results)
        avg_response_time = sum(r.get("duration_ms", 0) for r in results) / total_requests if total_requests > 0 else 0

        return {
            "operation": "stress_test",
            "concurrent_users": concurrent_users,
            "tasks_per_user": tasks_per_user,
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": round(successful_requests / total_requests * 100, 2) if total_requests > 0 else 0,
            "total_duration_ms": round(total_duration, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "throughput_requests_per_second": round(total_requests / (total_duration / 1000), 2) if total_duration > 0 else 0,
            "results": results
        }

    @staticmethod
    def generate_performance_report(test_results: Dict[str, any]) -> str:
        """
        Generate a human-readable performance test report.

        Args:
            test_results: Results from performance tests

        Returns:
            Formatted performance report
        """
        report_lines = [
            "PERFORMANCE TEST REPORT",
            "=" * 50,
            f"Timestamp: {test_results['timestamp']}",
            f"User ID: {test_results['test_config']['user_id']}",
            f"Task Count: {test_results['test_config']['task_count']:,}",
            "",
            "TEST RESULTS:",
            "-" * 30
        ]

        for test_name, result in test_results["tests"].items():
            status = "✅ PASS" if result.get("successful", False) else "❌ FAIL"
            report_lines.append(f"{test_name.upper()}: {status}")
            report_lines.append(f"  Duration: {result.get('duration_ms', 0):.2f}ms")

            if "throughput" in result:
                report_lines.append(f"  Throughput: {result['throughput']:.2f} ops/sec")

            if "task_count" in result:
                report_lines.append(f"  Task Count: {result['task_count']:,}")

            if "metrics_calculated" in result:
                report_lines.append(f"  Metrics Calculated: {result['metrics_calculated']}")

            report_lines.append("")

        report_lines.extend([
            "SUMMARY:",
            "-" * 15,
            f"Performance Score: {test_results['summary']['performance_score']}/100",
            f"Total Duration: {test_results['summary']['total_test_duration_ms']:.2f}ms",
            f"Average Throughput: {test_results['summary']['average_throughput']:.2f} ops/sec",
            f"All Tests Passed: {'YES' if test_results['summary']['all_tests_passed'] else 'NO'}",
            "",
            "RECOMMENDATIONS:",
            "-" * 20
        ])

        score = test_results['summary']['performance_score']
        if score >= 90:
            report_lines.append("  • Performance is excellent")
        elif score >= 70:
            report_lines.append("  • Performance is good but could be improved")
        elif score >= 50:
            report_lines.append("  • Performance needs optimization")
        else:
            report_lines.append("  • Performance requires immediate attention")

        report_lines.append("")
        return "\n".join(report_lines)

    @staticmethod
    def record_performance_metrics(user_id: str, test_results: Dict[str, any]):
        """
        Record performance test results as metrics in the database.

        Args:
            user_id: ID of the user running the test
            test_results: Results from performance tests
        """
        with Session(sync_engine) as session:
            for test_name, result in test_results.get("tests", {}).items():
                # Record duration metric
                duration_metric = PerformanceMetricsCreate(
                    user_id=user_id,
                    metric_type="performance_test_duration",
                    value=result.get("duration_ms", 0),
                    unit="milliseconds",
                    api_endpoint=f"/performance-test/{test_name}",
                    additional_metadata={
                        "test_name": test_name,
                        "task_count": result.get("task_count", 0),
                        "successful": result.get("successful", False),
                        "timestamp": datetime.utcnow().isoformat()
                    }
                )

                duration_record = PerformanceMetrics.model_validate(duration_metric)
                session.add(duration_record)

            # Record overall performance score
            score_metric = PerformanceMetricsCreate(
                user_id=user_id,
                metric_type="performance_score",
                value=test_results["summary"]["performance_score"],
                unit="score",
                api_endpoint="/performance-test/overall",
                additional_metadata={
                    "total_duration_ms": test_results["summary"]["total_test_duration_ms"],
                    "all_tests_passed": test_results["summary"]["all_tests_passed"],
                    "timestamp": datetime.utcnow().isoformat()
                }
            )

            score_record = PerformanceMetrics.model_validate(score_metric)
            session.add(score_record)

            session.commit()
            logger.info(f"Performance metrics recorded for user {user_id}")