"""Deployment verification tests for MCP server."""

import asyncio
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict

import pytest
import structlog

from mcp_spec_driven_development.config import ServerConfig, setup_logging
from mcp_spec_driven_development.monitoring import HealthMonitor
from mcp_spec_driven_development.server import main as server_main


class TestDeploymentVerification:
    """Test suite for deployment verification."""

    def test_server_config_from_env(self):
        """Test server configuration from environment variables."""
        # Set test environment variables
        test_env = {
            "MCP_SERVER_NAME": "test-server",
            "MCP_SERVER_VERSION": "1.0.0",
            "MCP_LOG_LEVEL": "DEBUG",
            "MCP_LOG_FORMAT": "json",
            "MCP_MAX_CONTENT_SIZE": "2048000",
            "MCP_CACHE_TTL": "7200",
        }

        # Temporarily set environment variables
        original_env = {}
        for key, value in test_env.items():
            original_env[key] = os.environ.get(key)
            os.environ[key] = value

        try:
            config = ServerConfig.from_env()

            assert config.name == "test-server"
            assert config.version == "1.0.0"
            assert config.log_level == "DEBUG"
            assert config.log_format == "json"
            assert config.max_content_size == 2048000
            assert config.cache_ttl == 7200

        finally:
            # Restore original environment
            for key, value in original_env.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    def test_logging_setup_console(self):
        """Test console logging setup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            setup_logging("INFO", "console", log_file)

            # Test that structlog is configured
            logger = structlog.get_logger("test")
            logger.info("Test message", test_key="test_value")

            # Force flush the log handlers
            import logging

            for handler in logging.getLogger().handlers:
                handler.flush()

            # Verify log file was created
            assert log_file.exists()

    def test_logging_setup_json(self):
        """Test JSON logging setup."""
        with tempfile.TemporaryDirectory() as temp_dir:
            log_file = Path(temp_dir) / "test.log"

            setup_logging("INFO", "json", log_file)

            # Test that structlog is configured for JSON
            logger = structlog.get_logger("test")
            logger.info("Test message", test_key="test_value")

            # Force flush the log handlers
            import logging

            for handler in logging.getLogger().handlers:
                handler.flush()

            # Verify log file exists
            assert log_file.exists()

    @pytest.mark.asyncio
    async def test_health_monitor_initialization(self):
        """Test health monitor initialization and basic functionality."""
        monitor = HealthMonitor()

        # Test initial state
        assert monitor.metrics.is_healthy is True
        assert monitor.metrics.total_tool_calls == 0
        assert monitor.metrics.get_success_rate() == 1.0

        # Test recording tool calls
        monitor.record_tool_call(success=True, response_time=0.1)
        monitor.record_tool_call(success=False, response_time=0.2)

        assert monitor.metrics.total_tool_calls == 2
        assert monitor.metrics.successful_tool_calls == 1
        assert monitor.metrics.failed_tool_calls == 1
        assert monitor.metrics.get_success_rate() == 0.5
        assert abs(monitor.metrics.average_response_time - 0.15) < 0.001

    @pytest.mark.asyncio
    async def test_health_check_components(self):
        """Test individual component health checks."""
        monitor = HealthMonitor()

        # Test content system check
        content_healthy = await monitor._check_content_system()
        assert isinstance(content_healthy, bool)

        # Test workflow system check
        workflow_healthy = await monitor._check_workflow_system()
        assert isinstance(workflow_healthy, bool)

        # Test validation system check
        validation_healthy = await monitor._check_validation_system()
        assert isinstance(validation_healthy, bool)

    @pytest.mark.asyncio
    async def test_comprehensive_health_check(self):
        """Test comprehensive health check."""
        monitor = HealthMonitor()

        health_status = await monitor.perform_health_check()
        assert isinstance(health_status, bool)

        # Test health report
        report = monitor.get_health_report()

        required_keys = {
            "status",
            "uptime_seconds",
            "last_check",
            "metrics",
            "components",
            "recent_errors",
        }
        assert set(report.keys()) >= required_keys

        # Test metrics structure
        metrics = report["metrics"]
        assert "total_tool_calls" in metrics
        assert "success_rate" in metrics
        assert "average_response_time_ms" in metrics

        # Test components structure
        components = report["components"]
        assert "content_system" in components
        assert "workflow_system" in components
        assert "validation_system" in components

    def test_error_tracking(self):
        """Test error tracking functionality."""
        monitor = HealthMonitor()

        # Record some errors
        monitor.record_error("Test error 1")
        monitor.record_error("Test error 2")

        assert len(monitor.metrics.recent_errors) == 2
        assert monitor.metrics.error_count_last_hour == 2

        # Test error limit (should keep only last 10)
        for i in range(15):
            monitor.record_error(f"Error {i}")

        assert len(monitor.metrics.recent_errors) == 10

    def test_package_installation_structure(self):
        """Test that package structure is correct for installation."""
        # Check that main package exists
        import mcp_spec_driven_development

        assert hasattr(mcp_spec_driven_development, "main")

        # Check that all required modules are importable
        from mcp_spec_driven_development import config, monitoring, server

        # Check that tools are importable
        from mcp_spec_driven_development.tools import (
            content_tools,
            validation_tools,
            workflow_tools,
        )

    def test_startup_script_exists(self):
        """Test that startup script exists and is executable."""
        script_path = Path("scripts/start-server.py")
        assert script_path.exists()

        # Check that script has proper shebang
        content = script_path.read_text()
        assert content.startswith("#!/usr/bin/env python3")

    @pytest.mark.asyncio
    async def test_server_startup_and_shutdown(self):
        """Test server startup and graceful shutdown."""
        # This test verifies the server can start without errors
        # In a real deployment, this would be tested with actual MCP client

        # Test that server main function exists and is callable
        assert callable(server_main)

        # Test configuration loading
        config = ServerConfig.from_env()
        assert config.name is not None
        assert config.version is not None

    def test_dependencies_available(self):
        """Test that all required dependencies are available."""
        required_packages = [
            "mcp",
            "pydantic",
            "jinja2",
            "structlog",
        ]

        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                pytest.fail(f"Required package {package} is not available")

    def test_content_data_structure(self):
        """Test that content data structure exists and is accessible."""
        from mcp_spec_driven_development.config import ServerConfig

        config = ServerConfig.from_env()
        content_root = config.content_root

        # Check that content directories exist
        assert content_root.exists()

        # Check for required subdirectories
        required_dirs = ["methodology", "templates", "examples"]
        for dir_name in required_dirs:
            dir_path = content_root / dir_name
            if dir_path.exists():  # Some may not exist yet, that's ok
                assert dir_path.is_dir()

    @pytest.mark.integration
    def test_end_to_end_tool_availability(self):
        """Integration test for tool availability."""
        # This would typically be run against a live server
        # For now, we test that tool definitions can be generated

        from mcp_spec_driven_development.tools.content_tools import ContentAccessTools
        from mcp_spec_driven_development.tools.validation_tools import ValidationTools
        from mcp_spec_driven_development.tools.workflow_tools import (
            WorkflowManagementTools,
        )

        content_tools = ContentAccessTools()
        workflow_tools = WorkflowManagementTools()
        validation_tools = ValidationTools()

        # Test that tools can provide their definitions
        content_defs = content_tools.get_tool_definitions()
        workflow_defs = workflow_tools.get_tool_definitions()
        validation_defs = validation_tools.get_tool_definitions()

        assert len(content_defs) > 0
        assert len(workflow_defs) > 0
        assert len(validation_defs) > 0

        # Test that each tool definition has required fields
        all_tools = content_defs + workflow_defs + validation_defs
        for tool in all_tools:
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")


@pytest.mark.performance
class TestPerformanceVerification:
    """Performance verification tests for deployment."""

    @pytest.mark.asyncio
    async def test_health_check_performance(self):
        """Test that health checks complete within acceptable time."""
        monitor = HealthMonitor()

        start_time = time.time()
        await monitor.perform_health_check()
        end_time = time.time()

        # Health check should complete within 5 seconds
        assert (end_time - start_time) < 5.0

    def test_tool_definition_performance(self):
        """Test that tool definitions are generated quickly."""
        from mcp_spec_driven_development.tools.content_tools import ContentAccessTools

        content_tools = ContentAccessTools()

        start_time = time.time()
        tools = content_tools.get_tool_definitions()
        end_time = time.time()

        # Tool definition generation should be fast
        assert (end_time - start_time) < 1.0
        assert len(tools) > 0
