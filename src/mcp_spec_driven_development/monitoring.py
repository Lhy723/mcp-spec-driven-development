"""Health monitoring and metrics for MCP server."""

import asyncio
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import structlog

from .config import get_health_check_config


@dataclass
class HealthMetrics:
    """Health metrics for the MCP server."""

    # Server status
    start_time: datetime = field(default_factory=datetime.now)
    last_health_check: Optional[datetime] = None
    is_healthy: bool = True

    # Tool call metrics
    total_tool_calls: int = 0
    successful_tool_calls: int = 0
    failed_tool_calls: int = 0
    average_response_time: float = 0.0

    # Component health
    content_system_healthy: bool = True
    workflow_system_healthy: bool = True
    validation_system_healthy: bool = True

    # Error tracking
    recent_errors: List[str] = field(default_factory=list)
    error_count_last_hour: int = 0

    def get_uptime(self) -> timedelta:
        """Get server uptime."""
        return datetime.now() - self.start_time

    def get_success_rate(self) -> float:
        """Get tool call success rate."""
        if self.total_tool_calls == 0:
            return 1.0
        return self.successful_tool_calls / self.total_tool_calls

    def add_error(self, error: str) -> None:
        """Add an error to recent errors list."""
        self.recent_errors.append(f"{datetime.now().isoformat()}: {error}")
        # Keep only last 10 errors
        if len(self.recent_errors) > 10:
            self.recent_errors.pop(0)
        self.error_count_last_hour += 1


class HealthMonitor:
    """Monitors server health and provides metrics."""

    def __init__(self):
        self.logger = structlog.get_logger(__name__)
        self.metrics = HealthMetrics()
        self.config = get_health_check_config()
        self._response_times: List[float] = []

    def record_tool_call(self, success: bool, response_time: float) -> None:
        """Record a tool call for metrics."""
        self.metrics.total_tool_calls += 1

        if success:
            self.metrics.successful_tool_calls += 1
        else:
            self.metrics.failed_tool_calls += 1

        # Update average response time
        self._response_times.append(response_time)
        if len(self._response_times) > 100:  # Keep last 100 calls
            self._response_times.pop(0)

        self.metrics.average_response_time = sum(self._response_times) / len(
            self._response_times
        )

    def record_error(self, error: str) -> None:
        """Record an error for monitoring."""
        self.metrics.add_error(error)
        self.logger.warning("Error recorded", error=error)

    async def perform_health_check(self) -> bool:
        """Perform comprehensive health check."""
        self.logger.debug("Performing health check")

        try:
            # Check content system
            self.metrics.content_system_healthy = await self._check_content_system()

            # Check workflow system
            self.metrics.workflow_system_healthy = await self._check_workflow_system()

            # Check validation system
            self.metrics.validation_system_healthy = (
                await self._check_validation_system()
            )

            # Overall health
            self.metrics.is_healthy = (
                self.metrics.content_system_healthy
                and self.metrics.workflow_system_healthy
                and self.metrics.validation_system_healthy
            )

            self.metrics.last_health_check = datetime.now()

            if self.metrics.is_healthy:
                self.logger.info("Health check passed")
            else:
                self.logger.warning(
                    "Health check failed",
                    content_healthy=self.metrics.content_system_healthy,
                    workflow_healthy=self.metrics.workflow_system_healthy,
                    validation_healthy=self.metrics.validation_system_healthy,
                )

            return self.metrics.is_healthy

        except Exception as e:
            self.logger.error("Health check error", error=str(e), exc_info=True)
            self.metrics.is_healthy = False
            return False

    async def _check_content_system(self) -> bool:
        """Check if content system is healthy."""
        try:
            # Import here to avoid circular imports
            from .content.content_loader import ContentLoader

            loader = ContentLoader()
            # Try to load a basic template
            template = await loader.get_template("requirements")
            return template is not None and len(template) > 0

        except Exception as e:
            self.logger.error("Content system check failed", error=str(e))
            return False

    async def _check_workflow_system(self) -> bool:
        """Check if workflow system is healthy."""
        try:
            # Import here to avoid circular imports
            from .workflow.phase_manager import PhaseManager

            manager = PhaseManager()
            # Try basic workflow operations
            return True  # Basic instantiation check

        except Exception as e:
            self.logger.error("Workflow system check failed", error=str(e))
            return False

    async def _check_validation_system(self) -> bool:
        """Check if validation system is healthy."""
        try:
            # Import here to avoid circular imports
            from .validation.requirements_validator import RequirementsValidator

            validator = RequirementsValidator()
            # Try basic validation
            return True  # Basic instantiation check

        except Exception as e:
            self.logger.error("Validation system check failed", error=str(e))
            return False

    def get_health_report(self) -> Dict:
        """Get comprehensive health report."""
        return {
            "status": "healthy" if self.metrics.is_healthy else "unhealthy",
            "uptime_seconds": self.metrics.get_uptime().total_seconds(),
            "last_check": self.metrics.last_health_check.isoformat()
            if self.metrics.last_health_check
            else None,
            "metrics": {
                "total_tool_calls": self.metrics.total_tool_calls,
                "success_rate": self.metrics.get_success_rate(),
                "average_response_time_ms": self.metrics.average_response_time * 1000,
                "error_count_last_hour": self.metrics.error_count_last_hour,
            },
            "components": {
                "content_system": "healthy"
                if self.metrics.content_system_healthy
                else "unhealthy",
                "workflow_system": "healthy"
                if self.metrics.workflow_system_healthy
                else "unhealthy",
                "validation_system": "healthy"
                if self.metrics.validation_system_healthy
                else "unhealthy",
            },
            "recent_errors": self.metrics.recent_errors[-5:],  # Last 5 errors
        }


# Global health monitor instance
health_monitor = HealthMonitor()
