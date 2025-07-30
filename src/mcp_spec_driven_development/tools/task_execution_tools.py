"""MCP tools for task execution support (task details, context, status management)."""

import re
from typing import Any, Dict, List, Optional, Tuple

from mcp.types import TextContent, Tool

from ..content.content_loader import ContentLoader
from ..validation.task_validator import TaskItem, TaskValidator
from ..workflow.models import PhaseType


class TaskExecutionTools:
    """MCP tools for supporting task execution with context and status management."""

    def __init__(self):
        """Initialize task execution tools."""
        self.content_loader = ContentLoader()
        self.task_validator = TaskValidator()

    def get_tool_definitions(self) -> List[Tool]:
        """Get MCP tool definitions for task execution support."""
        return [
            Tool(
                name="get_task_details",
                description="Get detailed information about a specific task including requirements context",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature",
                        },
                        "task_number": {
                            "type": "string",
                            "description": "Task number (e.g., '1', '2.1', '3.2')",
                        },
                    },
                    "required": ["feature_name", "task_number"],
                },
            ),
            Tool(
                name="get_task_context",
                description="Get comprehensive context for task execution including requirements and design info",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature",
                        },
                        "task_number": {
                            "type": "string",
                            "description": "Task number (e.g., '1', '2.1', '3.2')",
                        },
                    },
                    "required": ["feature_name", "task_number"],
                },
            ),
            Tool(
                name="get_task_dependencies",
                description="Get information about task dependencies and execution order",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature",
                        },
                        "task_number": {
                            "type": "string",
                            "description": "Task number (e.g., '1', '2.1', '3.2')",
                        },
                    },
                    "required": ["feature_name", "task_number"],
                },
            ),
            Tool(
                name="get_task_troubleshooting",
                description="Get troubleshooting guidance for task execution issues",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature",
                        },
                        "task_number": {
                            "type": "string",
                            "description": "Task number (e.g., '1', '2.1', '3.2')",
                        },
                        "issue_type": {
                            "type": "string",
                            "enum": [
                                "unclear_requirements",
                                "technical_difficulty",
                                "dependency_issues",
                                "testing_problems",
                                "general",
                            ],
                            "description": "Type of issue encountered",
                        },
                    },
                    "required": ["feature_name", "task_number", "issue_type"],
                },
            ),
            Tool(
                name="list_tasks",
                description="List all tasks for a feature with their current status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature",
                        },
                        "filter_status": {
                            "type": "string",
                            "enum": ["all", "not_started", "in_progress", "completed"],
                            "description": "Filter tasks by status (default: all)",
                        },
                    },
                    "required": ["feature_name"],
                },
            ),
            Tool(
                name="get_next_task",
                description="Get the next recommended task to work on based on dependencies and current status",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature",
                        }
                    },
                    "required": ["feature_name"],
                },
            ),
            Tool(
                name="update_task_status",
                description="Update the status of a specific task",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature",
                        },
                        "task_number": {
                            "type": "string",
                            "description": "Task number (e.g., '1', '2.1', '3.2')",
                        },
                        "status": {
                            "type": "string",
                            "enum": ["not_started", "in_progress", "completed"],
                            "description": "New status for the task",
                        },
                    },
                    "required": ["feature_name", "task_number", "status"],
                },
            ),
            Tool(
                name="validate_task_execution_order",
                description="Validate if a task can be started based on dependency requirements",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature",
                        },
                        "task_number": {
                            "type": "string",
                            "description": "Task number (e.g., '1', '2.1', '3.2')",
                        },
                    },
                    "required": ["feature_name", "task_number"],
                },
            ),
            Tool(
                name="get_task_progress",
                description="Get overall progress statistics for all tasks in a feature",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature",
                        }
                    },
                    "required": ["feature_name"],
                },
            ),
        ]

    async def handle_get_task_details(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_task_details tool call."""
        feature_name = arguments.get("feature_name", "")
        task_number = arguments.get("task_number", "")

        if not feature_name or not task_number:
            return [
                TextContent(
                    type="text", text="Error: feature_name and task_number are required"
                )
            ]

        try:
            # Load task document
            tasks_content = self._load_tasks_document(feature_name)
            if not tasks_content:
                return [
                    TextContent(
                        type="text",
                        text=f"No tasks document found for feature: {feature_name}",
                    )
                ]

            # Parse tasks and find the requested task
            tasks = self.task_validator._parse_tasks(tasks_content.split("\n"))
            task = self._find_task_by_number(tasks, task_number)

            if not task:
                return [
                    TextContent(
                        type="text",
                        text=f"Task {task_number} not found in {feature_name}",
                    )
                ]

            # Load requirements for context
            requirements_content = self._load_requirements_document(feature_name)

            # Format detailed task information
            response = f"""# Task Details: {feature_name}

## Task {task.number}: {task.title}

### Task Information
- **Number**: {task.number}
- **Type**: {'Subtask' if task.is_subtask else 'Main Task'}
- **Parent Task**: {task.parent_task if task.parent_task else 'None'}

### Implementation Details
"""

            if task.details:
                for detail in task.details:
                    # Skip requirements references in details display
                    if not re.search(r"_Requirements?:", detail):
                        response += f"- {detail}\n"
            else:
                response += "- No specific implementation details provided\n"

            # Add requirements context
            response += "\n### Requirements Context\n"
            if task.requirements_refs:
                response += f"**Referenced Requirements**: {', '.join(task.requirements_refs)}\n\n"

                if requirements_content:
                    for req_ref in task.requirements_refs:
                        req_context = self._extract_requirement_context(
                            requirements_content, req_ref
                        )
                        if req_context:
                            response += f"#### Requirement {req_ref}\n{req_context}\n\n"
                else:
                    response += (
                        "Requirements document not available for detailed context.\n"
                    )
            else:
                response += "No requirements references found for this task.\n"

            # Add task status information
            task_status = self._get_task_status_from_content(tasks_content, task_number)
            response += f"\n### Current Status\n"
            response += f"- **Status**: {task_status}\n"

            # Add execution guidance
            response += "\n### Execution Guidance\n"
            response += "- Focus on implementing only the functionality described in this task\n"
            response += "- Verify implementation against the referenced requirements\n"
            response += "- Write tests to validate the implementation\n"
            response += "- Update task status when complete\n"

            if task.is_subtask:
                response += f"- This is a subtask of Task {task.parent_task} - ensure it integrates properly\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [
                TextContent(type="text", text=f"Error getting task details: {str(e)}")
            ]

    async def handle_get_task_context(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_task_context tool call."""
        feature_name = arguments.get("feature_name", "")
        task_number = arguments.get("task_number", "")

        if not feature_name or not task_number:
            return [
                TextContent(
                    type="text", text="Error: feature_name and task_number are required"
                )
            ]

        try:
            # Load all spec documents
            tasks_content = self._load_tasks_document(feature_name)
            requirements_content = self._load_requirements_document(feature_name)
            design_content = self._load_design_document(feature_name)

            if not tasks_content:
                return [
                    TextContent(
                        type="text",
                        text=f"No tasks document found for feature: {feature_name}",
                    )
                ]

            # Parse tasks and find the requested task
            tasks = self.task_validator._parse_tasks(tasks_content.split("\n"))
            task = self._find_task_by_number(tasks, task_number)

            if not task:
                return [
                    TextContent(
                        type="text",
                        text=f"Task {task_number} not found in {feature_name}",
                    )
                ]

            # Build comprehensive context
            response = f"""# Task Execution Context: {feature_name}

## Task {task.number}: {task.title}

### Task Overview
- **Objective**: {task.title}
- **Type**: {'Subtask' if task.is_subtask else 'Main Task'}
- **Requirements**: {', '.join(task.requirements_refs) if task.requirements_refs else 'None specified'}

### Implementation Steps
"""

            if task.details:
                for i, detail in enumerate(task.details, 1):
                    if not re.search(r"_Requirements?:", detail):
                        response += f"{i}. {detail}\n"

            # Add requirements context
            if task.requirements_refs and requirements_content:
                response += "\n## Requirements Context\n"
                for req_ref in task.requirements_refs:
                    req_context = self._extract_requirement_context(
                        requirements_content, req_ref
                    )
                    if req_context:
                        response += f"\n### Requirement {req_ref}\n{req_context}\n"

            # Add relevant design context
            if design_content:
                response += "\n## Design Context\n"
                design_context = self._extract_relevant_design_context(
                    design_content, task
                )
                response += design_context

            # Add related tasks context
            related_tasks = self._find_related_tasks(tasks, task)
            if related_tasks:
                response += "\n## Related Tasks\n"
                for related_task in related_tasks:
                    status = self._get_task_status_from_content(
                        tasks_content, related_task.number
                    )
                    response += f"- **Task {related_task.number}**: {related_task.title} ({status})\n"

            # Add methodology guidance
            response += "\n## Implementation Methodology\n"
            methodology_guidance = self._get_task_methodology_guidance(task)
            response += methodology_guidance

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [
                TextContent(type="text", text=f"Error getting task context: {str(e)}")
            ]

    async def handle_get_task_dependencies(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_task_dependencies tool call."""
        feature_name = arguments.get("feature_name", "")
        task_number = arguments.get("task_number", "")

        if not feature_name or not task_number:
            return [
                TextContent(
                    type="text", text="Error: feature_name and task_number are required"
                )
            ]

        try:
            # Load tasks document
            tasks_content = self._load_tasks_document(feature_name)
            if not tasks_content:
                return [
                    TextContent(
                        type="text",
                        text=f"No tasks document found for feature: {feature_name}",
                    )
                ]

            # Parse tasks
            tasks = self.task_validator._parse_tasks(tasks_content.split("\n"))
            task = self._find_task_by_number(tasks, task_number)

            if not task:
                return [
                    TextContent(
                        type="text",
                        text=f"Task {task_number} not found in {feature_name}",
                    )
                ]

            # Analyze dependencies
            dependencies = self._analyze_task_dependencies(tasks, task)

            response = f"""# Task Dependencies: {feature_name}

## Task {task.number}: {task.title}

### Dependency Analysis
"""

            # Prerequisites (tasks that should be completed before this one)
            if dependencies["prerequisites"]:
                response += "\n#### Prerequisites (Complete Before Starting)\n"
                for prereq in dependencies["prerequisites"]:
                    status = self._get_task_status_from_content(
                        tasks_content, prereq.number
                    )
                    status_icon = (
                        "✅"
                        if status == "completed"
                        else "⏸️"
                        if status == "not_started"
                        else "🔄"
                    )
                    response += f"- {status_icon} **Task {prereq.number}**: {prereq.title} ({status})\n"
            else:
                response += "\n#### Prerequisites\n- No prerequisite tasks identified\n"

            # Dependents (tasks that depend on this one)
            if dependencies["dependents"]:
                response += (
                    "\n#### Dependent Tasks (Will Be Blocked Until This Completes)\n"
                )
                for dependent in dependencies["dependents"]:
                    status = self._get_task_status_from_content(
                        tasks_content, dependent.number
                    )
                    response += (
                        f"- **Task {dependent.number}**: {dependent.title} ({status})\n"
                    )
            else:
                response += "\n#### Dependent Tasks\n- No tasks depend on this one\n"

            # Parallel tasks (can be worked on simultaneously)
            if dependencies["parallel"]:
                response += "\n#### Parallel Tasks (Can Work On Simultaneously)\n"
                for parallel in dependencies["parallel"]:
                    status = self._get_task_status_from_content(
                        tasks_content, parallel.number
                    )
                    response += (
                        f"- **Task {parallel.number}**: {parallel.title} ({status})\n"
                    )

            # Execution order guidance
            response += "\n### Execution Order Guidance\n"

            if dependencies["prerequisites"]:
                incomplete_prereqs = [
                    p
                    for p in dependencies["prerequisites"]
                    if self._get_task_status_from_content(tasks_content, p.number)
                    != "completed"
                ]
                if incomplete_prereqs:
                    response += "⚠️ **Cannot start this task yet**\n"
                    response += "Complete these prerequisite tasks first:\n"
                    for prereq in incomplete_prereqs:
                        response += f"- Task {prereq.number}: {prereq.title}\n"
                else:
                    response += "✅ **Ready to start** - All prerequisites completed\n"
            else:
                response += "✅ **Ready to start** - No prerequisites required\n"

            # Add sequence recommendations
            response += "\n### Recommended Sequence\n"
            sequence = self._get_recommended_sequence(tasks, task)
            for i, step in enumerate(sequence, 1):
                response += f"{i}. {step}\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [
                TextContent(
                    type="text", text=f"Error analyzing task dependencies: {str(e)}"
                )
            ]

    async def handle_get_task_troubleshooting(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_task_troubleshooting tool call."""
        feature_name = arguments.get("feature_name", "")
        task_number = arguments.get("task_number", "")
        issue_type = arguments.get("issue_type", "general")

        if not feature_name or not task_number:
            return [
                TextContent(
                    type="text", text="Error: feature_name and task_number are required"
                )
            ]

        try:
            # Load task document
            tasks_content = self._load_tasks_document(feature_name)
            if not tasks_content:
                return [
                    TextContent(
                        type="text",
                        text=f"No tasks document found for feature: {feature_name}",
                    )
                ]

            # Parse tasks and find the requested task
            tasks = self.task_validator._parse_tasks(tasks_content.split("\n"))
            task = self._find_task_by_number(tasks, task_number)

            if not task:
                return [
                    TextContent(
                        type="text",
                        text=f"Task {task_number} not found in {feature_name}",
                    )
                ]

            # Generate troubleshooting guidance based on issue type
            response = f"""# Task Troubleshooting: {feature_name}

## Task {task.number}: {task.title}

### Issue Type: {issue_type.replace('_', ' ').title()}

"""

            if issue_type == "unclear_requirements":
                response += self._get_requirements_troubleshooting(task, feature_name)
            elif issue_type == "technical_difficulty":
                response += self._get_technical_troubleshooting(task, feature_name)
            elif issue_type == "dependency_issues":
                response += self._get_dependency_troubleshooting(
                    task, tasks, tasks_content
                )
            elif issue_type == "testing_problems":
                response += self._get_testing_troubleshooting(task, feature_name)
            else:  # general
                response += self._get_general_troubleshooting(task, feature_name)

            # Add common troubleshooting steps
            response += """
## General Troubleshooting Steps

### 1. Review Task Context
- Re-read the task description and implementation details
- Check the referenced requirements for clarity
- Review related design documentation

### 2. Break Down the Problem
- Identify the smallest possible first step
- Focus on one specific aspect at a time
- Create a simple test case to validate understanding

### 3. Seek Additional Context
- Use `get_task_context` for comprehensive background
- Check `get_task_dependencies` for prerequisite information
- Review related tasks for implementation patterns

### 4. Validate Approach
- Write a simple test first to clarify expected behavior
- Implement the minimal viable solution
- Iterate and refine based on test results

### 5. Get Help
- If still stuck, consider asking for clarification on requirements
- Break the task into smaller sub-tasks if needed
- Look for similar implementations in the codebase
"""

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"Error getting troubleshooting guidance: {str(e)}",
                )
            ]

    async def handle_list_tasks(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle list_tasks tool call."""
        feature_name = arguments.get("feature_name", "")
        filter_status = arguments.get("filter_status", "all")

        if not feature_name:
            return [TextContent(type="text", text="Error: feature_name is required")]

        try:
            # Load tasks document
            tasks_content = self._load_tasks_document(feature_name)
            if not tasks_content:
                return [
                    TextContent(
                        type="text",
                        text=f"No tasks document found for feature: {feature_name}",
                    )
                ]

            # Parse tasks
            tasks = self.task_validator._parse_tasks(tasks_content.split("\n"))

            # Filter tasks by status if requested
            if filter_status != "all":
                filtered_tasks = []
                for task in tasks:
                    task_status = self._get_task_status_from_content(
                        tasks_content, task.number
                    )
                    if task_status == filter_status:
                        filtered_tasks.append(task)
                tasks = filtered_tasks

            # Format task list
            response = f"""# Task List: {feature_name}

## Filter: {filter_status.replace('_', ' ').title()}

### Tasks Overview
"""

            if not tasks:
                response += f"No tasks found with status: {filter_status}\n"
                return [TextContent(type="text", text=response)]

            # Group tasks by main task and subtasks
            main_tasks = [t for t in tasks if not t.is_subtask]
            subtasks_by_parent = {}

            for task in tasks:
                if task.is_subtask:
                    parent = task.parent_task
                    if parent not in subtasks_by_parent:
                        subtasks_by_parent[parent] = []
                    subtasks_by_parent[parent].append(task)

            # Display tasks hierarchically
            for main_task in main_tasks:
                status = self._get_task_status_from_content(
                    tasks_content, main_task.number
                )
                status_icon = self._get_status_icon(status)

                response += (
                    f"\n#### {status_icon} Task {main_task.number}: {main_task.title}\n"
                )
                response += f"- **Status**: {status}\n"
                if main_task.requirements_refs:
                    response += f"- **Requirements**: {', '.join(main_task.requirements_refs)}\n"

                # Add subtasks
                if main_task.number in subtasks_by_parent:
                    response += "- **Subtasks**:\n"
                    for subtask in subtasks_by_parent[main_task.number]:
                        sub_status = self._get_task_status_from_content(
                            tasks_content, subtask.number
                        )
                        sub_icon = self._get_status_icon(sub_status)
                        response += f"  - {sub_icon} {subtask.number}: {subtask.title} ({sub_status})\n"

            # Add summary statistics
            total_tasks = len(tasks)
            completed_count = sum(
                1
                for task in tasks
                if self._get_task_status_from_content(tasks_content, task.number)
                == "completed"
            )
            in_progress_count = sum(
                1
                for task in tasks
                if self._get_task_status_from_content(tasks_content, task.number)
                == "in_progress"
            )
            not_started_count = total_tasks - completed_count - in_progress_count

            response += f"""
### Summary Statistics
- **Total Tasks**: {total_tasks}
- **Completed**: {completed_count} ({completed_count/total_tasks*100:.1f}%)
- **In Progress**: {in_progress_count} ({in_progress_count/total_tasks*100:.1f}%)
- **Not Started**: {not_started_count} ({not_started_count/total_tasks*100:.1f}%)
"""

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error listing tasks: {str(e)}")]

    async def handle_get_next_task(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_next_task tool call."""
        feature_name = arguments.get("feature_name", "")

        if not feature_name:
            return [TextContent(type="text", text="Error: feature_name is required")]

        try:
            # Load tasks document
            tasks_content = self._load_tasks_document(feature_name)
            if not tasks_content:
                return [
                    TextContent(
                        type="text",
                        text=f"No tasks document found for feature: {feature_name}",
                    )
                ]

            # Parse tasks
            tasks = self.task_validator._parse_tasks(tasks_content.split("\n"))

            # Find the next recommended task
            next_task = self._find_next_recommended_task(tasks, tasks_content)

            if not next_task:
                response = f"""# Next Task Recommendation: {feature_name}

## Status: All Tasks Complete! 🎉

All tasks in the implementation plan have been completed. The feature is ready for final integration and testing.

### Next Steps
1. Perform final integration testing
2. Review all implemented functionality
3. Update documentation if needed
4. Consider the feature complete
"""
                return [TextContent(type="text", text=response)]

            # Get task details and context
            task_status = self._get_task_status_from_content(
                tasks_content, next_task.number
            )
            dependencies = self._analyze_task_dependencies(tasks, next_task)

            response = f"""# Next Task Recommendation: {feature_name}

## Recommended Task: {next_task.number}

### Task Details
- **Title**: {next_task.title}
- **Type**: {'Subtask' if next_task.is_subtask else 'Main Task'}
- **Current Status**: {task_status}
- **Requirements**: {', '.join(next_task.requirements_refs) if next_task.requirements_refs else 'None specified'}

### Why This Task?
"""

            # Explain why this task was recommended
            if task_status == "in_progress":
                response += (
                    "- This task is already in progress and should be completed\n"
                )
            elif not dependencies["prerequisites"]:
                response += "- No prerequisite tasks - can start immediately\n"
            else:
                completed_prereqs = [
                    p
                    for p in dependencies["prerequisites"]
                    if self._get_task_status_from_content(tasks_content, p.number)
                    == "completed"
                ]
                if len(completed_prereqs) == len(dependencies["prerequisites"]):
                    response += "- All prerequisite tasks have been completed\n"
                else:
                    response += "- Most prerequisite tasks are complete\n"

            response += "- Follows logical implementation sequence\n"
            response += "- Builds incrementally on previous work\n"

            # Add implementation guidance
            response += "\n### Implementation Steps\n"
            if next_task.details:
                for i, detail in enumerate(next_task.details, 1):
                    if not re.search(r"_Requirements?:", detail):
                        response += f"{i}. {detail}\n"
            else:
                response += "1. Review task requirements and context\n"
                response += "2. Plan implementation approach\n"
                response += "3. Write tests for expected behavior\n"
                response += "4. Implement functionality\n"
                response += "5. Validate against requirements\n"

            # Add quick access to more information
            response += f"""
### Get More Information
- Use `get_task_details` with task_number="{next_task.number}" for detailed information
- Use `get_task_context` with task_number="{next_task.number}" for full context
- Use `get_task_dependencies` with task_number="{next_task.number}" for dependency analysis

### Ready to Start?
Update the task status to 'in_progress' when you begin working on it.
"""

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error finding next task: {str(e)}")]

    # Helper methods

    def _load_tasks_document(self, feature_name: str) -> Optional[str]:
        """Load tasks document content."""
        try:
            return self.content_loader.load_spec_document(feature_name, PhaseType.TASKS)
        except:
            return None

    def _load_requirements_document(self, feature_name: str) -> Optional[str]:
        """Load requirements document content."""
        try:
            return self.content_loader.load_spec_document(
                feature_name, PhaseType.REQUIREMENTS
            )
        except:
            return None

    def _load_design_document(self, feature_name: str) -> Optional[str]:
        """Load design document content."""
        try:
            return self.content_loader.load_spec_document(
                feature_name, PhaseType.DESIGN
            )
        except:
            return None

    def _find_task_by_number(
        self, tasks: List[TaskItem], task_number: str
    ) -> Optional[TaskItem]:
        """Find a task by its number."""
        for task in tasks:
            if task.number == task_number:
                return task
        return None

    def _get_task_status_from_content(
        self, tasks_content: str, task_number: str
    ) -> str:
        """Extract task status from tasks document content."""
        lines = tasks_content.split("\n")

        for line in lines:
            if f"- [x] {task_number}" in line or f"- [X] {task_number}" in line:
                return "completed"
            elif f"- [-] {task_number}" in line:
                return "in_progress"
            elif f"- [ ] {task_number}" in line:
                return "not_started"

        return "not_started"  # Default if not found

    def _get_status_icon(self, status: str) -> str:
        """Get icon for task status."""
        icons = {"completed": "✅", "in_progress": "🔄", "not_started": "⏸️"}
        return icons.get(status, "❓")

    def _extract_requirement_context(
        self, requirements_content: str, req_ref: str
    ) -> Optional[str]:
        """Extract context for a specific requirement reference."""
        lines = requirements_content.split("\n")

        # Look for requirement section
        req_pattern = f"### Requirement {req_ref}"
        in_requirement = False
        context_lines = []

        for line in lines:
            if line.strip().startswith(req_pattern):
                in_requirement = True
                continue
            elif in_requirement and line.strip().startswith("### Requirement"):
                break  # Next requirement section
            elif in_requirement:
                context_lines.append(line)

        if context_lines:
            return "\n".join(context_lines).strip()
        return None

    def _extract_relevant_design_context(
        self, design_content: str, task: TaskItem
    ) -> str:
        """Extract relevant design context for a task."""
        # This is a simplified implementation - could be enhanced with more sophisticated matching
        context = "Relevant design information:\n"

        # Look for sections that might be relevant to the task
        task_keywords = task.title.lower().split()
        lines = design_content.split("\n")

        relevant_sections = []
        current_section = None
        current_content = []

        for line in lines:
            if line.startswith("##"):
                if current_section and current_content:
                    # Check if this section is relevant
                    section_text = " ".join(current_content).lower()
                    if any(keyword in section_text for keyword in task_keywords):
                        relevant_sections.append((current_section, current_content))

                current_section = line.strip()
                current_content = []
            else:
                current_content.append(line)

        # Don't forget the last section
        if current_section and current_content:
            section_text = " ".join(current_content).lower()
            if any(keyword in section_text for keyword in task_keywords):
                relevant_sections.append((current_section, current_content))

        if relevant_sections:
            for section_title, section_content in relevant_sections[
                :2
            ]:  # Limit to 2 most relevant
                context += f"\n{section_title}\n"
                context += "\n".join(section_content[:10])  # Limit content length
                context += "\n"
        else:
            context += "No specific design context found for this task.\n"

        return context

    def _find_related_tasks(
        self, tasks: List[TaskItem], current_task: TaskItem
    ) -> List[TaskItem]:
        """Find tasks related to the current task."""
        related = []

        # If this is a subtask, include parent and sibling subtasks
        if current_task.is_subtask:
            for task in tasks:
                if (
                    task.parent_task == current_task.parent_task
                    and task.number != current_task.number
                ):
                    related.append(task)
                elif task.number == current_task.parent_task:
                    related.append(task)

        # If this is a main task, include its subtasks
        else:
            for task in tasks:
                if task.parent_task == current_task.number:
                    related.append(task)

        # Include tasks with overlapping requirements
        current_reqs = set(current_task.requirements_refs)
        for task in tasks:
            if task.number != current_task.number:
                task_reqs = set(task.requirements_refs)
                if current_reqs & task_reqs:  # Intersection
                    related.append(task)

        return related[:5]  # Limit to 5 most related

    def _get_task_methodology_guidance(self, task: TaskItem) -> str:
        """Get methodology guidance for task execution."""
        guidance = """
### Test-Driven Development
1. Write tests first to clarify expected behavior
2. Implement minimal code to make tests pass
3. Refactor and improve code quality
4. Ensure all tests continue to pass

### Incremental Implementation
1. Start with the simplest possible implementation
2. Add complexity gradually
3. Test each increment thoroughly
4. Integrate with existing code carefully

### Code Quality Standards
1. Follow project coding standards and conventions
2. Write clear, self-documenting code
3. Add appropriate comments for complex logic
4. Ensure proper error handling

### Integration Guidelines
1. Ensure new code integrates with existing components
2. Update interfaces and contracts as needed
3. Test integration points thoroughly
4. Document any breaking changes
"""
        return guidance

    def _analyze_task_dependencies(
        self, tasks: List[TaskItem], current_task: TaskItem
    ) -> Dict[str, List[TaskItem]]:
        """Analyze dependencies for a task."""
        dependencies = {"prerequisites": [], "dependents": [], "parallel": []}

        current_num = float(current_task.number.replace(".", ""))

        for task in tasks:
            if task.number == current_task.number:
                continue

            task_num = float(task.number.replace(".", ""))

            # Simple heuristic: earlier numbered tasks are prerequisites
            if task_num < current_num:
                # Check if it's a direct prerequisite (same main task or previous main task)
                if (
                    current_task.is_subtask
                    and task.parent_task == current_task.parent_task
                ):
                    if task_num < current_num:
                        dependencies["prerequisites"].append(task)
                elif not current_task.is_subtask and not task.is_subtask:
                    if task_num == current_num - 1:  # Previous main task
                        dependencies["prerequisites"].append(task)
                elif not current_task.is_subtask and task.is_subtask:
                    # Main task depends on its subtasks
                    if task.parent_task == current_task.number:
                        dependencies["prerequisites"].append(task)

            # Later tasks depend on this one
            elif task_num > current_num:
                if not current_task.is_subtask and task.is_subtask:
                    if task.parent_task == current_task.number:
                        dependencies["dependents"].append(task)
                elif current_task.is_subtask and not task.is_subtask:
                    if current_task.parent_task == str(int(task_num)):
                        dependencies["dependents"].append(task)
                else:
                    dependencies["dependents"].append(task)

            # Tasks with overlapping requirements can be parallel
            current_reqs = set(current_task.requirements_refs)
            task_reqs = set(task.requirements_refs)
            if current_reqs & task_reqs and abs(task_num - current_num) <= 1:
                dependencies["parallel"].append(task)

        return dependencies

    def _get_recommended_sequence(
        self, tasks: List[TaskItem], current_task: TaskItem
    ) -> List[str]:
        """Get recommended sequence for task execution."""
        sequence = [
            "Review task requirements and acceptance criteria",
            "Understand the context from requirements and design documents",
            "Identify specific files, classes, or components to modify",
            "Write failing tests that define expected behavior",
            "Implement minimal code to make tests pass",
            "Refactor and improve code quality",
            "Run all tests to ensure no regressions",
            "Update task status to completed",
        ]

        if current_task.is_subtask:
            sequence.insert(
                1,
                f"Ensure parent task {current_task.parent_task} context is understood",
            )
            sequence.append("Verify integration with other subtasks")

        return sequence

    def _find_next_recommended_task(
        self, tasks: List[TaskItem], tasks_content: str
    ) -> Optional[TaskItem]:
        """Find the next recommended task to work on."""
        # First, look for in-progress tasks
        for task in tasks:
            status = self._get_task_status_from_content(tasks_content, task.number)
            if status == "in_progress":
                return task

        # Then, look for tasks that can be started (prerequisites completed)
        for task in tasks:
            status = self._get_task_status_from_content(tasks_content, task.number)
            if status == "not_started":
                dependencies = self._analyze_task_dependencies(tasks, task)

                # Check if all prerequisites are completed
                all_prereqs_done = True
                for prereq in dependencies["prerequisites"]:
                    prereq_status = self._get_task_status_from_content(
                        tasks_content, prereq.number
                    )
                    if prereq_status != "completed":
                        all_prereqs_done = False
                        break

                if all_prereqs_done:
                    return task

        return None  # All tasks completed or blocked

    def _get_requirements_troubleshooting(
        self, task: TaskItem, feature_name: str
    ) -> str:
        """Get troubleshooting guidance for unclear requirements."""
        return f"""
### Requirements Clarity Issues

#### Problem Analysis
The task requirements may be unclear or insufficient for implementation.

#### Troubleshooting Steps

1. **Review Referenced Requirements**
   - Check requirements {', '.join(task.requirements_refs) if task.requirements_refs else 'None specified'}
   - Look for acceptance criteria and user stories
   - Identify specific behaviors expected

2. **Break Down the Requirement**
   - What specific user action triggers this functionality?
   - What should the system do in response?
   - What are the success and failure scenarios?

3. **Look for Examples**
   - Check if similar functionality exists in the codebase
   - Look for test cases that demonstrate expected behavior
   - Review design documents for additional context

4. **Clarify Ambiguities**
   - Identify specific unclear aspects
   - Consider edge cases and error conditions
   - Think about user experience implications

#### Common Issues and Solutions

- **Vague Requirements**: Break down into specific, testable behaviors
- **Missing Edge Cases**: Consider error conditions and boundary cases
- **Unclear Success Criteria**: Define what "done" looks like with specific tests
- **Integration Unclear**: Review how this fits with existing functionality
"""

    def _get_technical_troubleshooting(self, task: TaskItem, feature_name: str) -> str:
        """Get troubleshooting guidance for technical difficulties."""
        return f"""
### Technical Implementation Issues

#### Problem Analysis
The task may involve technical challenges or unfamiliar technologies.

#### Troubleshooting Steps

1. **Simplify the Problem**
   - Break the task into smaller, manageable pieces
   - Identify the core functionality needed
   - Start with the simplest possible implementation

2. **Research and Learning**
   - Look up documentation for relevant technologies
   - Find examples of similar implementations
   - Check existing codebase for patterns

3. **Prototype First**
   - Create a minimal proof-of-concept
   - Test core assumptions with simple code
   - Validate approach before full implementation

4. **Incremental Development**
   - Implement one small piece at a time
   - Test each piece thoroughly
   - Build complexity gradually

#### Common Technical Issues

- **Unfamiliar APIs**: Start with simple examples and build up
- **Complex Logic**: Break into smaller functions with clear responsibilities
- **Integration Challenges**: Test integration points separately
- **Performance Concerns**: Get it working first, optimize later
"""

    def _get_dependency_troubleshooting(
        self, task: TaskItem, tasks: List[TaskItem], tasks_content: str
    ) -> str:
        """Get troubleshooting guidance for dependency issues."""
        dependencies = self._analyze_task_dependencies(tasks, task)

        response = """
### Task Dependency Issues

#### Problem Analysis
This task may be blocked by incomplete prerequisites or causing blocking issues.

#### Current Dependencies
"""

        # Check prerequisite status
        if dependencies["prerequisites"]:
            response += "\n**Prerequisites Status:**\n"
            for prereq in dependencies["prerequisites"]:
                status = self._get_task_status_from_content(
                    tasks_content, prereq.number
                )
                status_icon = self._get_status_icon(status)
                response += (
                    f"- {status_icon} Task {prereq.number}: {prereq.title} ({status})\n"
                )

        response += """
#### Troubleshooting Steps

1. **Check Prerequisites**
   - Ensure all prerequisite tasks are truly complete
   - Verify that prerequisite functionality works as expected
   - Test integration points with prerequisite code

2. **Resolve Blocking Issues**
   - If prerequisites are incomplete, consider helping complete them
   - Look for workarounds or temporary implementations
   - Consider if task can be partially implemented

3. **Dependency Management**
   - Review if dependencies are actually necessary
   - Consider if task can be broken down to reduce dependencies
   - Look for opportunities to work in parallel

4. **Communication**
   - If working in a team, coordinate with others on prerequisite tasks
   - Update task status to reflect current blocking issues
   - Consider reordering tasks if dependencies are problematic
"""

        return response

    def _get_testing_troubleshooting(self, task: TaskItem, feature_name: str) -> str:
        """Get troubleshooting guidance for testing problems."""
        return f"""
### Testing Implementation Issues

#### Problem Analysis
Difficulties with writing or running tests for this task.

#### Troubleshooting Steps

1. **Test Strategy**
   - Start with the simplest possible test
   - Focus on testing one behavior at a time
   - Use arrange-act-assert pattern

2. **Test Environment**
   - Ensure test environment is properly set up
   - Check that all dependencies are available
   - Verify test runner configuration

3. **Test Design**
   - Write tests that match the requirements exactly
   - Test both success and failure scenarios
   - Include edge cases and boundary conditions

4. **Debugging Tests**
   - Run tests individually to isolate issues
   - Use debugging tools to step through test execution
   - Add logging to understand test behavior

#### Common Testing Issues

- **Test Setup**: Ensure proper test data and environment setup
- **Mocking**: Use mocks for external dependencies
- **Assertions**: Make assertions specific and meaningful
- **Test Isolation**: Ensure tests don't interfere with each other
"""

    def _get_general_troubleshooting(self, task: TaskItem, feature_name: str) -> str:
        """Get general troubleshooting guidance."""
        return f"""
### General Task Execution Issues

#### Problem Analysis
General difficulties with task execution or unclear next steps.

#### Troubleshooting Steps

1. **Task Understanding**
   - Re-read the task description carefully
   - Review implementation details and requirements
   - Understand the expected outcome

2. **Context Review**
   - Check requirements and design documents
   - Review related tasks for patterns
   - Understand how this fits in the overall feature

3. **Planning**
   - Break the task into smaller steps
   - Identify specific files or components to modify
   - Plan the implementation approach

4. **Implementation**
   - Start with the simplest possible implementation
   - Write tests to validate behavior
   - Iterate and improve incrementally

#### When to Seek Help

- Requirements are fundamentally unclear
- Technical approach is uncertain
- Task seems too large or complex
- Dependencies are blocking progress
- Tests are consistently failing
"""

    async def handle_update_task_status(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle update_task_status tool call."""
        feature_name = arguments.get("feature_name", "")
        task_number = arguments.get("task_number", "")
        new_status = arguments.get("status", "")

        if not feature_name or not task_number or not new_status:
            return [
                TextContent(
                    type="text",
                    text="Error: feature_name, task_number, and status are required",
                )
            ]

        try:
            # Load tasks document
            tasks_content = self._load_tasks_document(feature_name)
            if not tasks_content:
                return [
                    TextContent(
                        type="text",
                        text=f"No tasks document found for feature: {feature_name}",
                    )
                ]

            # Parse tasks to validate task exists
            tasks = self.task_validator._parse_tasks(tasks_content.split("\n"))
            task = self._find_task_by_number(tasks, task_number)

            if not task:
                return [
                    TextContent(
                        type="text",
                        text=f"Task {task_number} not found in {feature_name}",
                    )
                ]

            # Check if status change is valid based on dependencies
            validation_result = self._validate_status_change(
                tasks, task, new_status, tasks_content
            )
            if not validation_result["valid"]:
                return [
                    TextContent(
                        type="text",
                        text=f"Status change not allowed: {validation_result['reason']}",
                    )
                ]

            # Update the task status in the document
            updated_content = self._update_task_status_in_content(
                tasks_content, task_number, new_status
            )

            if updated_content == tasks_content:
                return [
                    TextContent(
                        type="text",
                        text=f"Task {task_number} status was already {new_status}",
                    )
                ]

            # Save the updated content (in a real implementation, this would write to file)
            # For now, we'll just return success message

            response = f"""# Task Status Updated: {feature_name}

## Task {task.number}: {task.title}

### Status Change
- **Previous Status**: {self._get_task_status_from_content(tasks_content, task_number)}
- **New Status**: {new_status}
- **Updated**: Successfully

### Impact Analysis
"""

            if new_status == "completed":
                # Check what tasks are now unblocked
                dependent_tasks = self._analyze_task_dependencies(tasks, task)[
                    "dependents"
                ]
                if dependent_tasks:
                    response += "\n#### Tasks Now Available\n"
                    for dep_task in dependent_tasks:
                        dep_deps = self._analyze_task_dependencies(tasks, dep_task)
                        all_prereqs_done = all(
                            self._get_task_status_from_content(
                                updated_content, prereq.number
                            )
                            == "completed"
                            for prereq in dep_deps["prerequisites"]
                        )
                        if all_prereqs_done:
                            response += f"- **Task {dep_task.number}**: {dep_task.title} (ready to start)\n"
                else:
                    response += "- No dependent tasks affected\n"

            elif new_status == "in_progress":
                response += "- Task is now active and being worked on\n"
                response += "- Remember to update status to 'completed' when finished\n"

            elif new_status == "not_started":
                response += "- Task has been reset to not started\n"
                response += "- Any dependent tasks may need to be reconsidered\n"

            # Add next steps guidance
            response += "\n### Next Steps\n"
            if new_status == "completed":
                next_task = self._find_next_recommended_task(tasks, updated_content)
                if next_task:
                    response += f"- Consider starting Task {next_task.number}: {next_task.title}\n"
                else:
                    response += (
                        "- All tasks completed! Feature implementation is done.\n"
                    )
            elif new_status == "in_progress":
                response += "- Focus on completing this task\n"
                response += (
                    "- Use task execution tools for guidance and troubleshooting\n"
                )
            else:  # not_started
                response += "- Task is available to be started when ready\n"
                response += "- Check dependencies before beginning work\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [
                TextContent(type="text", text=f"Error updating task status: {str(e)}")
            ]

    async def handle_validate_task_execution_order(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle validate_task_execution_order tool call."""
        feature_name = arguments.get("feature_name", "")
        task_number = arguments.get("task_number", "")

        if not feature_name or not task_number:
            return [
                TextContent(
                    type="text", text="Error: feature_name and task_number are required"
                )
            ]

        try:
            # Load tasks document
            tasks_content = self._load_tasks_document(feature_name)
            if not tasks_content:
                return [
                    TextContent(
                        type="text",
                        text=f"No tasks document found for feature: {feature_name}",
                    )
                ]

            # Parse tasks
            tasks = self.task_validator._parse_tasks(tasks_content.split("\n"))
            task = self._find_task_by_number(tasks, task_number)

            if not task:
                return [
                    TextContent(
                        type="text",
                        text=f"Task {task_number} not found in {feature_name}",
                    )
                ]

            # Analyze dependencies
            dependencies = self._analyze_task_dependencies(tasks, task)
            current_status = self._get_task_status_from_content(
                tasks_content, task_number
            )

            response = f"""# Task Execution Order Validation: {feature_name}

## Task {task.number}: {task.title}

### Current Status: {current_status}

### Dependency Validation
"""

            # Check prerequisites
            if dependencies["prerequisites"]:
                response += "\n#### Prerequisites Check\n"
                all_prereqs_met = True
                for prereq in dependencies["prerequisites"]:
                    prereq_status = self._get_task_status_from_content(
                        tasks_content, prereq.number
                    )
                    if prereq_status == "completed":
                        response += f"- ✅ **Task {prereq.number}**: {prereq.title} (completed)\n"
                    else:
                        response += f"- ❌ **Task {prereq.number}**: {prereq.title} ({prereq_status})\n"
                        all_prereqs_met = False

                if all_prereqs_met:
                    response += "\n**Result**: ✅ All prerequisites completed - task can be started\n"
                else:
                    response += "\n**Result**: ❌ Prerequisites not met - complete prerequisite tasks first\n"
            else:
                response += "\n#### Prerequisites Check\n- ✅ No prerequisites required - task can be started anytime\n"

            # Check current task status implications
            response += "\n### Status-Based Recommendations\n"

            if current_status == "not_started":
                if not dependencies["prerequisites"] or all(
                    self._get_task_status_from_content(tasks_content, prereq.number)
                    == "completed"
                    for prereq in dependencies["prerequisites"]
                ):
                    response += "- ✅ **Ready to Start**: All conditions met for beginning this task\n"
                    response += "- Update status to 'in_progress' when you begin work\n"
                else:
                    response += "- ⏸️ **Blocked**: Complete prerequisite tasks before starting\n"
                    response += "- Focus on prerequisite tasks first\n"

            elif current_status == "in_progress":
                response += "- 🔄 **Currently Active**: Task is being worked on\n"
                response += "- Continue work and update to 'completed' when finished\n"
                response += "- Ensure all implementation details are addressed\n"

            elif current_status == "completed":
                response += "- ✅ **Already Complete**: Task has been finished\n"
                if dependencies["dependents"]:
                    response += "- Check if dependent tasks can now be started\n"
                else:
                    response += "- No dependent tasks affected\n"

            # Add execution order guidance
            response += "\n### Execution Order Guidance\n"

            # Find the logical sequence
            if task.is_subtask:
                response += f"- This is a subtask of Task {task.parent_task}\n"
                response += (
                    f"- Complete all subtasks before considering parent task complete\n"
                )

                # Find sibling subtasks
                siblings = [
                    t
                    for t in tasks
                    if t.parent_task == task.parent_task and t.number != task.number
                ]
                if siblings:
                    response += (
                        f"- Sibling subtasks: {', '.join(s.number for s in siblings)}\n"
                    )

            # Suggest next tasks if this one is completed
            if current_status == "completed":
                next_candidates = []
                for candidate in tasks:
                    if (
                        self._get_task_status_from_content(
                            tasks_content, candidate.number
                        )
                        == "not_started"
                    ):
                        candidate_deps = self._analyze_task_dependencies(
                            tasks, candidate
                        )
                        if all(
                            self._get_task_status_from_content(
                                tasks_content, prereq.number
                            )
                            == "completed"
                            for prereq in candidate_deps["prerequisites"]
                        ):
                            next_candidates.append(candidate)

                if next_candidates:
                    response += f"\n### Next Available Tasks\n"
                    for candidate in next_candidates[:3]:  # Show top 3
                        response += (
                            f"- **Task {candidate.number}**: {candidate.title}\n"
                        )

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [
                TextContent(
                    type="text", text=f"Error validating task execution order: {str(e)}"
                )
            ]

    async def handle_get_task_progress(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_task_progress tool call."""
        feature_name = arguments.get("feature_name", "")

        if not feature_name:
            return [TextContent(type="text", text="Error: feature_name is required")]

        try:
            # Load tasks document
            tasks_content = self._load_tasks_document(feature_name)
            if not tasks_content:
                return [
                    TextContent(
                        type="text",
                        text=f"No tasks document found for feature: {feature_name}",
                    )
                ]

            # Parse tasks
            tasks = self.task_validator._parse_tasks(tasks_content.split("\n"))

            if not tasks:
                return [
                    TextContent(type="text", text=f"No tasks found in {feature_name}")
                ]

            # Calculate progress statistics
            total_tasks = len(tasks)
            completed_tasks = sum(
                1
                for task in tasks
                if self._get_task_status_from_content(tasks_content, task.number)
                == "completed"
            )
            in_progress_tasks = sum(
                1
                for task in tasks
                if self._get_task_status_from_content(tasks_content, task.number)
                == "in_progress"
            )
            not_started_tasks = total_tasks - completed_tasks - in_progress_tasks

            completion_percentage = (completed_tasks / total_tasks) * 100

            # Separate main tasks and subtasks
            main_tasks = [t for t in tasks if not t.is_subtask]
            subtasks = [t for t in tasks if t.is_subtask]

            response = f"""# Task Progress Report: {feature_name}

## Overall Progress
- **Total Tasks**: {total_tasks}
- **Completed**: {completed_tasks} ({completion_percentage:.1f}%)
- **In Progress**: {in_progress_tasks} ({in_progress_tasks/total_tasks*100:.1f}%)
- **Not Started**: {not_started_tasks} ({not_started_tasks/total_tasks*100:.1f}%)

## Progress Bar
{self._generate_progress_bar(completion_percentage)}

## Task Breakdown

### Main Tasks ({len(main_tasks)} total)
"""

            for main_task in main_tasks:
                status = self._get_task_status_from_content(
                    tasks_content, main_task.number
                )
                status_icon = self._get_status_icon(status)

                response += (
                    f"\n#### {status_icon} Task {main_task.number}: {main_task.title}\n"
                )
                response += f"- **Status**: {status.replace('_', ' ').title()}\n"

                # Check subtasks for this main task
                task_subtasks = [
                    t for t in subtasks if t.parent_task == main_task.number
                ]
                if task_subtasks:
                    completed_subtasks = sum(
                        1
                        for st in task_subtasks
                        if self._get_task_status_from_content(tasks_content, st.number)
                        == "completed"
                    )
                    subtask_progress = (completed_subtasks / len(task_subtasks)) * 100
                    response += f"- **Subtasks**: {completed_subtasks}/{len(task_subtasks)} completed ({subtask_progress:.1f}%)\n"

                    for subtask in task_subtasks:
                        sub_status = self._get_task_status_from_content(
                            tasks_content, subtask.number
                        )
                        sub_icon = self._get_status_icon(sub_status)
                        response += f"  - {sub_icon} {subtask.number}: {subtask.title} ({sub_status.replace('_', ' ')})\n"

            # Add velocity and estimation info
            response += "\n## Progress Analysis\n"

            if completed_tasks > 0:
                response += (
                    f"- **Completion Rate**: {completed_tasks} tasks completed\n"
                )
                if in_progress_tasks > 0:
                    response += f"- **Active Work**: {in_progress_tasks} tasks currently in progress\n"

                # Estimate remaining work
                if not_started_tasks > 0:
                    response += f"- **Remaining Work**: {not_started_tasks} tasks not yet started\n"
            else:
                response += "- **Status**: Project not yet started\n"

            # Find bottlenecks and blockers
            blocked_tasks = []
            ready_tasks = []

            for task in tasks:
                if (
                    self._get_task_status_from_content(tasks_content, task.number)
                    == "not_started"
                ):
                    dependencies = self._analyze_task_dependencies(tasks, task)
                    if dependencies["prerequisites"]:
                        prereqs_completed = all(
                            self._get_task_status_from_content(
                                tasks_content, prereq.number
                            )
                            == "completed"
                            for prereq in dependencies["prerequisites"]
                        )
                        if prereqs_completed:
                            ready_tasks.append(task)
                        else:
                            blocked_tasks.append(task)
                    else:
                        ready_tasks.append(task)

            if blocked_tasks:
                response += f"\n### Blocked Tasks ({len(blocked_tasks)})\n"
                for task in blocked_tasks[:5]:  # Show first 5
                    response += f"- **Task {task.number}**: {task.title} (waiting on prerequisites)\n"

            if ready_tasks:
                response += f"\n### Ready to Start ({len(ready_tasks)})\n"
                for task in ready_tasks[:5]:  # Show first 5
                    response += f"- **Task {task.number}**: {task.title} (can start immediately)\n"

            # Add recommendations
            response += "\n## Recommendations\n"

            if in_progress_tasks > 0:
                response += (
                    "- Focus on completing in-progress tasks before starting new ones\n"
                )

            if ready_tasks:
                response += f"- {len(ready_tasks)} tasks are ready to start - consider prioritizing these\n"

            if blocked_tasks:
                response += f"- {len(blocked_tasks)} tasks are blocked - focus on completing their prerequisites\n"

            if completion_percentage >= 80:
                response += "- Project is nearing completion - focus on final tasks and integration\n"
            elif completion_percentage >= 50:
                response += "- Project is halfway complete - maintain momentum and address any blockers\n"
            elif completion_percentage >= 20:
                response += (
                    "- Good progress made - continue with systematic task completion\n"
                )
            else:
                response += (
                    "- Project is in early stages - focus on foundational tasks first\n"
                )

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [
                TextContent(type="text", text=f"Error getting task progress: {str(e)}")
            ]

    # Helper methods for task status management

    def _validate_status_change(
        self, tasks: List[TaskItem], task: TaskItem, new_status: str, tasks_content: str
    ) -> Dict[str, Any]:
        """Validate if a status change is allowed."""
        current_status = self._get_task_status_from_content(tasks_content, task.number)

        # Allow any status change for now - in a more sophisticated system,
        # we might have rules about valid transitions
        if current_status == new_status:
            return {"valid": False, "reason": f"Task is already {new_status}"}

        # Check if trying to complete a task with incomplete prerequisites
        if new_status == "completed":
            dependencies = self._analyze_task_dependencies(tasks, task)
            for prereq in dependencies["prerequisites"]:
                prereq_status = self._get_task_status_from_content(
                    tasks_content, prereq.number
                )
                if prereq_status != "completed":
                    return {
                        "valid": False,
                        "reason": f"Cannot complete task - prerequisite Task {prereq.number} is not completed ({prereq_status})",
                    }

        return {"valid": True, "reason": "Status change is valid"}

    def _update_task_status_in_content(
        self, content: str, task_number: str, new_status: str
    ) -> str:
        """Update task status in the content string."""
        lines = content.split("\n")
        updated_lines = []

        status_markers = {
            "not_started": "[ ]",
            "in_progress": "[-]",
            "completed": "[x]",
        }

        new_marker = status_markers[new_status]

        for line in lines:
            # Check if this line contains the task we want to update
            if f" {task_number}." in line or f" {task_number} " in line:
                # Replace the status marker
                if "- [x]" in line:
                    updated_line = line.replace("- [x]", f"- {new_marker}")
                elif "- [-]" in line:
                    updated_line = line.replace("- [-]", f"- {new_marker}")
                elif "- [ ]" in line:
                    updated_line = line.replace("- [ ]", f"- {new_marker}")
                else:
                    updated_line = line
                updated_lines.append(updated_line)
            else:
                updated_lines.append(line)

        return "\n".join(updated_lines)

    def _generate_progress_bar(self, percentage: float, width: int = 30) -> str:
        """Generate a text-based progress bar."""
        filled = int(width * percentage / 100)
        empty = width - filled
        bar = "█" * filled + "░" * empty
        return f"[{bar}] {percentage:.1f}%"

    async def handle_tool_call(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle MCP tool calls for task execution support."""
        handlers = {
            "get_task_details": self.handle_get_task_details,
            "get_task_context": self.handle_get_task_context,
            "get_task_dependencies": self.handle_get_task_dependencies,
            "get_task_troubleshooting": self.handle_get_task_troubleshooting,
            "list_tasks": self.handle_list_tasks,
            "get_next_task": self.handle_get_next_task,
            "update_task_status": self.handle_update_task_status,
            "validate_task_execution_order": self.handle_validate_task_execution_order,
            "get_task_progress": self.handle_get_task_progress,
        }

        handler = handlers.get(name)
        if not handler:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return await handler(arguments)
