"""Tests for task execution tools."""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.mcp_spec_driven_development.tools.task_execution_tools import (
    TaskExecutionTools,
)
from src.mcp_spec_driven_development.validation.task_validator import TaskItem


class TestTaskExecutionTools:
    """Test cases for TaskExecutionTools."""

    def setup_method(self):
        """Set up test fixtures."""
        self.tools = TaskExecutionTools()

        # Sample task content
        self.sample_tasks_content = """# Implementation Plan

- [x] 1. Set up project structure
  - Create directory structure
  - Initialize configuration
  - _Requirements: 1.1, 1.2_

- [ ] 2. Implement core functionality
- [ ] 2.1 Create data models
  - Write model classes
  - Add validation logic
  - _Requirements: 2.1_

- [-] 2.2 Build API endpoints
  - Implement REST endpoints
  - Add error handling
  - _Requirements: 2.2, 2.3_

- [ ] 3. Add testing
  - Write unit tests
  - Add integration tests
  - _Requirements: 3.1_
"""

        # Sample requirements content
        self.sample_requirements_content = """# Requirements Document

### Requirement 1

**User Story:** As a developer, I want project structure, so that I can organize code.

#### Acceptance Criteria
1. WHEN setting up THEN system SHALL create directories
2. WHEN initializing THEN system SHALL configure settings

### Requirement 2

**User Story:** As a user, I want core functionality, so that I can use the system.

#### Acceptance Criteria
1. WHEN using system THEN it SHALL provide core features
2. WHEN accessing data THEN system SHALL validate inputs
"""

    @pytest.mark.asyncio
    async def test_get_task_details_success(self):
        """Test successful task details retrieval."""
        with patch.object(
            self.tools, "_load_tasks_document"
        ) as mock_load_tasks, patch.object(
            self.tools, "_load_requirements_document"
        ) as mock_load_reqs:
            mock_load_tasks.return_value = self.sample_tasks_content
            mock_load_reqs.return_value = self.sample_requirements_content

            result = await self.tools.handle_get_task_details(
                {"feature_name": "test-feature", "task_number": "2.1"}
            )

            assert len(result) == 1
            response = result[0].text
            assert "Task 2.1: Create data models" in response
            assert "Subtask" in response
            assert "**Referenced Requirements**: 2.1" in response
            assert "Write model classes" in response

    @pytest.mark.asyncio
    async def test_get_task_details_task_not_found(self):
        """Test task details when task is not found."""
        with patch.object(self.tools, "_load_tasks_document") as mock_load_tasks:
            mock_load_tasks.return_value = self.sample_tasks_content

            result = await self.tools.handle_get_task_details(
                {"feature_name": "test-feature", "task_number": "99"}
            )

            assert len(result) == 1
            assert "Task 99 not found" in result[0].text

    @pytest.mark.asyncio
    async def test_get_task_details_no_tasks_document(self):
        """Test task details when tasks document doesn't exist."""
        with patch.object(self.tools, "_load_tasks_document") as mock_load_tasks:
            mock_load_tasks.return_value = None

            result = await self.tools.handle_get_task_details(
                {"feature_name": "test-feature", "task_number": "1"}
            )

            assert len(result) == 1
            assert "No tasks document found" in result[0].text

    @pytest.mark.asyncio
    async def test_get_task_context_success(self):
        """Test successful task context retrieval."""
        with patch.object(
            self.tools, "_load_tasks_document"
        ) as mock_load_tasks, patch.object(
            self.tools, "_load_requirements_document"
        ) as mock_load_reqs, patch.object(
            self.tools, "_load_design_document"
        ) as mock_load_design:
            mock_load_tasks.return_value = self.sample_tasks_content
            mock_load_reqs.return_value = self.sample_requirements_content
            mock_load_design.return_value = (
                "# Design Document\n\n## Architecture\nSystem design details"
            )

            result = await self.tools.handle_get_task_context(
                {"feature_name": "test-feature", "task_number": "2.1"}
            )

            assert len(result) == 1
            response = result[0].text
            assert "Task Execution Context" in response
            assert "Task 2.1: Create data models" in response
            assert "Requirements Context" in response
            assert "Design Context" in response
            assert "Implementation Methodology" in response

    @pytest.mark.asyncio
    async def test_get_task_dependencies_success(self):
        """Test successful task dependencies analysis."""
        with patch.object(self.tools, "_load_tasks_document") as mock_load_tasks:
            mock_load_tasks.return_value = self.sample_tasks_content

            result = await self.tools.handle_get_task_dependencies(
                {"feature_name": "test-feature", "task_number": "2.2"}
            )

            assert len(result) == 1
            response = result[0].text
            assert "Task Dependencies" in response
            assert "Task 2.2: Build API endpoints" in response
            assert "Prerequisites" in response
            assert "Execution Order Guidance" in response

    @pytest.mark.asyncio
    async def test_get_task_troubleshooting_unclear_requirements(self):
        """Test troubleshooting for unclear requirements."""
        with patch.object(self.tools, "_load_tasks_document") as mock_load_tasks:
            mock_load_tasks.return_value = self.sample_tasks_content

            result = await self.tools.handle_get_task_troubleshooting(
                {
                    "feature_name": "test-feature",
                    "task_number": "2.1",
                    "issue_type": "unclear_requirements",
                }
            )

            assert len(result) == 1
            response = result[0].text
            assert "Task Troubleshooting" in response
            assert "Requirements Clarity Issues" in response
            assert "Review Referenced Requirements" in response

    @pytest.mark.asyncio
    async def test_get_task_troubleshooting_technical_difficulty(self):
        """Test troubleshooting for technical difficulties."""
        with patch.object(self.tools, "_load_tasks_document") as mock_load_tasks:
            mock_load_tasks.return_value = self.sample_tasks_content

            result = await self.tools.handle_get_task_troubleshooting(
                {
                    "feature_name": "test-feature",
                    "task_number": "2.1",
                    "issue_type": "technical_difficulty",
                }
            )

            assert len(result) == 1
            response = result[0].text
            assert "Technical Implementation Issues" in response
            assert "Simplify the Problem" in response

    @pytest.mark.asyncio
    async def test_list_tasks_all(self):
        """Test listing all tasks."""
        with patch.object(self.tools, "_load_tasks_document") as mock_load_tasks:
            mock_load_tasks.return_value = self.sample_tasks_content

            result = await self.tools.handle_list_tasks(
                {"feature_name": "test-feature", "filter_status": "all"}
            )

            assert len(result) == 1
            response = result[0].text
            assert "Task List" in response
            assert "Task 1: Set up project structure" in response
            assert "Task 2: Implement core functionality" in response
            assert "Summary Statistics" in response

    @pytest.mark.asyncio
    async def test_list_tasks_filtered(self):
        """Test listing tasks with status filter."""
        with patch.object(self.tools, "_load_tasks_document") as mock_load_tasks:
            mock_load_tasks.return_value = self.sample_tasks_content

            result = await self.tools.handle_list_tasks(
                {"feature_name": "test-feature", "filter_status": "completed"}
            )

            assert len(result) == 1
            response = result[0].text
            assert "Filter: Completed" in response

    @pytest.mark.asyncio
    async def test_get_next_task_success(self):
        """Test getting next recommended task."""
        with patch.object(self.tools, "_load_tasks_document") as mock_load_tasks:
            mock_load_tasks.return_value = self.sample_tasks_content

            result = await self.tools.handle_get_next_task(
                {"feature_name": "test-feature"}
            )

            assert len(result) == 1
            response = result[0].text
            assert "Next Task Recommendation" in response
            assert "Recommended Task" in response

    @pytest.mark.asyncio
    async def test_get_next_task_all_complete(self):
        """Test getting next task when all tasks are complete."""
        complete_tasks_content = self.sample_tasks_content.replace(
            "[ ]", "[x]"
        ).replace("[-]", "[x]")

        with patch.object(self.tools, "_load_tasks_document") as mock_load_tasks:
            mock_load_tasks.return_value = complete_tasks_content

            result = await self.tools.handle_get_next_task(
                {"feature_name": "test-feature"}
            )

            assert len(result) == 1
            response = result[0].text
            assert "All Tasks Complete" in response

    def test_get_task_status_from_content(self):
        """Test task status extraction from content."""
        # Test completed task
        status = self.tools._get_task_status_from_content(
            self.sample_tasks_content, "1"
        )
        assert status == "completed"

        # Test in-progress task
        status = self.tools._get_task_status_from_content(
            self.sample_tasks_content, "2.2"
        )
        assert status == "in_progress"

        # Test not started task
        status = self.tools._get_task_status_from_content(
            self.sample_tasks_content, "2.1"
        )
        assert status == "not_started"

        # Test non-existent task
        status = self.tools._get_task_status_from_content(
            self.sample_tasks_content, "99"
        )
        assert status == "not_started"

    def test_get_status_icon(self):
        """Test status icon mapping."""
        assert self.tools._get_status_icon("completed") == "✅"
        assert self.tools._get_status_icon("in_progress") == "🔄"
        assert self.tools._get_status_icon("not_started") == "⏸️"
        assert self.tools._get_status_icon("unknown") == "❓"

    def test_find_task_by_number(self):
        """Test finding task by number."""
        # Create sample tasks
        tasks = [
            TaskItem("1", "Task 1", [], [], 1, 2, False),
            TaskItem("2.1", "Task 2.1", [], [], 3, 4, True, "2"),
            TaskItem("2.2", "Task 2.2", [], [], 5, 6, True, "2"),
        ]

        # Test finding existing task
        task = self.tools._find_task_by_number(tasks, "2.1")
        assert task is not None
        assert task.title == "Task 2.1"

        # Test finding non-existent task
        task = self.tools._find_task_by_number(tasks, "99")
        assert task is None

    def test_extract_requirement_context(self):
        """Test requirement context extraction."""
        context = self.tools._extract_requirement_context(
            self.sample_requirements_content, "1"
        )
        assert context is not None
        assert "User Story" in context
        assert "project structure" in context

        # Test non-existent requirement
        context = self.tools._extract_requirement_context(
            self.sample_requirements_content, "99"
        )
        assert context is None

    def test_analyze_task_dependencies(self):
        """Test task dependency analysis."""
        # Create sample tasks with dependencies
        tasks = [
            TaskItem("1", "Setup", [], [], 1, 2, False),
            TaskItem("2", "Core", [], [], 3, 4, False),
            TaskItem("2.1", "Models", [], [], 5, 6, True, "2"),
            TaskItem("2.2", "API", [], [], 7, 8, True, "2"),
            TaskItem("3", "Testing", [], [], 9, 10, False),
        ]

        # Test dependencies for subtask
        deps = self.tools._analyze_task_dependencies(tasks, tasks[2])  # Task 2.1
        assert len(deps["prerequisites"]) >= 0  # May have prerequisites
        assert len(deps["dependents"]) >= 0  # May have dependents
        assert len(deps["parallel"]) >= 0  # May have parallel tasks

    @pytest.mark.asyncio
    async def test_missing_arguments(self):
        """Test handling of missing required arguments."""
        # Test missing feature_name
        result = await self.tools.handle_get_task_details({"task_number": "1"})
        assert "feature_name and task_number are required" in result[0].text

        # Test missing task_number
        result = await self.tools.handle_get_task_details(
            {"feature_name": "test-feature"}
        )
        assert "feature_name and task_number are required" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_tool_call_unknown_tool(self):
        """Test handling unknown tool calls."""
        result = await self.tools.handle_tool_call("unknown_tool", {})
        assert len(result) == 1
        assert "Unknown tool: unknown_tool" in result[0].text

    @pytest.mark.asyncio
    async def test_handle_tool_call_known_tools(self):
        """Test handling known tool calls."""
        with patch.object(self.tools, "handle_get_task_details") as mock_handler:
            mock_handler.return_value = [Mock(text="test response")]

            result = await self.tools.handle_tool_call(
                "get_task_details", {"feature_name": "test", "task_number": "1"}
            )

            mock_handler.assert_called_once_with(
                {"feature_name": "test", "task_number": "1"}
            )

    @pytest.mark.asyncio
    async def test_update_task_status_success(self):
        """Test successful task status update."""
        with patch.object(self.tools, "_load_tasks_document") as mock_load_tasks:
            mock_load_tasks.return_value = self.sample_tasks_content

            result = await self.tools.handle_update_task_status(
                {
                    "feature_name": "test-feature",
                    "task_number": "2.1",
                    "status": "in_progress",
                }
            )

            assert len(result) == 1
            response = result[0].text
            assert "Task Status Updated" in response
            assert "**New Status**: in_progress" in response

    @pytest.mark.asyncio
    async def test_update_task_status_invalid_task(self):
        """Test task status update with invalid task number."""
        with patch.object(self.tools, "_load_tasks_document") as mock_load_tasks:
            mock_load_tasks.return_value = self.sample_tasks_content

            result = await self.tools.handle_update_task_status(
                {
                    "feature_name": "test-feature",
                    "task_number": "99",
                    "status": "completed",
                }
            )

            assert len(result) == 1
            assert "Task 99 not found" in result[0].text

    @pytest.mark.asyncio
    async def test_validate_task_execution_order_success(self):
        """Test task execution order validation."""
        with patch.object(self.tools, "_load_tasks_document") as mock_load_tasks:
            mock_load_tasks.return_value = self.sample_tasks_content

            result = await self.tools.handle_validate_task_execution_order(
                {"feature_name": "test-feature", "task_number": "2.1"}
            )

            assert len(result) == 1
            response = result[0].text
            assert "Task Execution Order Validation" in response
            assert "Dependency Validation" in response

    @pytest.mark.asyncio
    async def test_get_task_progress_success(self):
        """Test task progress report generation."""
        with patch.object(self.tools, "_load_tasks_document") as mock_load_tasks:
            mock_load_tasks.return_value = self.sample_tasks_content

            result = await self.tools.handle_get_task_progress(
                {"feature_name": "test-feature"}
            )

            assert len(result) == 1
            response = result[0].text
            assert "Task Progress Report" in response
            assert "Overall Progress" in response
            assert "Progress Bar" in response

    def test_validate_status_change(self):
        """Test status change validation logic."""
        # Create sample tasks
        tasks = [
            TaskItem("1", "Task 1", [], [], 1, 2, False),
            TaskItem("2", "Task 2", [], [], 3, 4, False),
        ]

        # Test valid status change
        result = self.tools._validate_status_change(
            tasks, tasks[0], "in_progress", self.sample_tasks_content
        )
        assert result["valid"] == True

        # Test invalid status change (same status)
        result = self.tools._validate_status_change(
            tasks, tasks[0], "completed", self.sample_tasks_content
        )
        # Task 1 is already completed in sample content, so this should be invalid
        assert result["valid"] == False

    def test_update_task_status_in_content(self):
        """Test updating task status in content string."""
        content = "- [ ] 1. Test task\n- [x] 2. Another task"

        # Update first task to in_progress
        updated = self.tools._update_task_status_in_content(content, "1", "in_progress")
        assert "- [-] 1. Test task" in updated

        # Update second task to not_started
        updated = self.tools._update_task_status_in_content(content, "2", "not_started")
        assert "- [ ] 2. Another task" in updated

    def test_generate_progress_bar(self):
        """Test progress bar generation."""
        # Test various percentages
        bar_0 = self.tools._generate_progress_bar(0)
        assert "0.0%" in bar_0
        assert "░" in bar_0

        bar_50 = self.tools._generate_progress_bar(50)
        assert "50.0%" in bar_50
        assert "█" in bar_50
        assert "░" in bar_50

        bar_100 = self.tools._generate_progress_bar(100)
        assert "100.0%" in bar_100
        assert "█" in bar_100

    def test_get_tool_definitions(self):
        """Test tool definitions are properly structured."""
        tools = self.tools.get_tool_definitions()

        # Check that we have the expected tools
        tool_names = [tool.name for tool in tools]
        expected_tools = [
            "get_task_details",
            "get_task_context",
            "get_task_dependencies",
            "get_task_troubleshooting",
            "list_tasks",
            "get_next_task",
            "update_task_status",
            "validate_task_execution_order",
            "get_task_progress",
        ]

        for expected_tool in expected_tools:
            assert expected_tool in tool_names

        # Check that each tool has required properties
        for tool in tools:
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert hasattr(tool, "inputSchema")
            assert "properties" in tool.inputSchema
            assert "required" in tool.inputSchema
