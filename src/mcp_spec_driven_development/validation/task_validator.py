"""Task document validator for format validation and requirements traceability."""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple

from ..workflow.models import ValidationLocation, ValidationResult


@dataclass
class TaskItem:
    """Represents a parsed task item."""

    number: str
    title: str
    details: List[str]
    requirements_refs: List[str]
    line_start: int
    line_end: int
    is_subtask: bool
    parent_task: Optional[str] = None


class TaskValidator:
    """Validates task documents for format compliance and requirements traceability."""

    # Task item pattern (checkbox with number and title)
    TASK_PATTERN = r"^-\s*\[\s*[x\s-]\s*\]\s*(\d+(?:\.\d+)*)\.?\s+(.+)$"

    # Requirements reference pattern (captures everything between the underscores)
    REQUIREMENTS_REF_PATTERN = r"_Requirements?:\s*([^_]+)_"

    # Non-coding task indicators (things to avoid)
    NON_CODING_INDICATORS = [
        "user testing",
        "user acceptance",
        "deployment",
        "production",
        "performance metrics",
        "user training",
        "documentation creation",
        "business process",
        "marketing",
        "communication",
        "user feedback",
        "analyze usage",
        "gather metrics",
        "deploy to",
        "user interview",
    ]

    # Vague language indicators
    VAGUE_INDICATORS = [
        "set up the system",
        "make it work",
        "implement properly",
        "add security",
        "create responsive design",
        "user management",
        "handle errors",
        "optimize performance",
        "improve user experience",
    ]

    # Actionable coding verbs
    CODING_VERBS = [
        "implement",
        "create",
        "write",
        "build",
        "add",
        "develop",
        "code",
        "program",
        "construct",
        "design",
        "integrate",
        "test",
        "validate",
        "configure",
        "setup",
        "initialize",
    ]

    def __init__(self):
        """Initialize the task validator."""
        self.task_regex = re.compile(self.TASK_PATTERN)
        self.requirements_ref_regex = re.compile(self.REQUIREMENTS_REF_PATTERN)

    def validate(
        self, content: str, requirements_content: Optional[str] = None
    ) -> List[ValidationResult]:
        """
        Validate a task document.

        Args:
            content: The task document content
            requirements_content: Optional requirements document for traceability checking

        Returns:
            List of validation results
        """
        results = []
        lines = content.split("\n")

        # Check document structure
        results.extend(self._validate_document_structure(lines))

        # Parse task items
        tasks = self._parse_tasks(lines)

        # Validate each task
        for task in tasks:
            results.extend(self._validate_task(task, lines))

        # Validate task numbering and hierarchy
        results.extend(self._validate_task_numbering(tasks))

        # Validate task dependencies and sequencing
        results.extend(self._validate_task_sequencing(tasks))

        # Validate requirements traceability if requirements provided
        if requirements_content:
            results.extend(
                self._validate_requirements_traceability(tasks, requirements_content)
            )

        return results

    def _validate_document_structure(self, lines: List[str]) -> List[ValidationResult]:
        """Validate the overall document structure."""
        results = []

        # Check for title
        has_title = any(line.strip().startswith("# ") for line in lines)
        if not has_title:
            results.append(
                ValidationResult(
                    type="error",
                    message="Document must have a title (# Implementation Plan)",
                    location=ValidationLocation(section="document"),
                    suggestion="Add a title at the beginning: # Implementation Plan",
                )
            )

        # Check for at least one task
        has_tasks = any(self.task_regex.match(line.strip()) for line in lines)
        if not has_tasks:
            results.append(
                ValidationResult(
                    type="error",
                    message="Document must contain at least one task",
                    location=ValidationLocation(section="document"),
                    suggestion="Add tasks using format: - [ ] 1. Task title",
                )
            )

        return results

    def _parse_tasks(self, lines: List[str]) -> List[TaskItem]:
        """Parse task items from the document."""
        tasks = []
        current_task = None

        for i, line in enumerate(lines):
            line_num = i + 1
            stripped_line = line.strip()

            # Check for task item
            match = self.task_regex.match(stripped_line)
            if match:
                # Save previous task
                if current_task:
                    current_task["line_end"] = line_num - 1
                    tasks.append(self._create_task_item(current_task))

                # Start new task
                task_number = match.group(1)
                task_title = match.group(2).strip()

                current_task = {
                    "number": task_number,
                    "title": task_title,
                    "details": [],
                    "requirements_refs": [],
                    "line_start": line_num,
                    "line_end": line_num,
                    "is_subtask": "." in task_number,
                }
            elif current_task and stripped_line:
                # Add details to current task or check for requirements
                if stripped_line.startswith("-") and not self.task_regex.match(
                    stripped_line
                ):
                    # This is a detail line
                    detail = stripped_line[1:].strip()
                    current_task["details"].append(detail)

                # Always check for requirements reference in any line under a task
                req_match = self.requirements_ref_regex.search(stripped_line)
                if req_match:
                    refs = [ref.strip() for ref in req_match.group(1).split(",")]
                    current_task["requirements_refs"].extend(refs)

        # Don't forget the last task
        if current_task:
            current_task["line_end"] = len(lines)
            tasks.append(self._create_task_item(current_task))

        return tasks

    def _create_task_item(self, task_data: Dict) -> TaskItem:
        """Create a TaskItem from parsed data."""
        parent_task = None
        if task_data["is_subtask"]:
            # Extract parent task number (e.g., "2.1" -> "2")
            parent_task = task_data["number"].split(".")[0]

        return TaskItem(
            number=task_data["number"],
            title=task_data["title"],
            details=task_data["details"],
            requirements_refs=task_data["requirements_refs"],
            line_start=task_data["line_start"],
            line_end=task_data["line_end"],
            is_subtask=task_data["is_subtask"],
            parent_task=parent_task,
        )

    def _validate_task(
        self, task: TaskItem, lines: List[str]
    ) -> List[ValidationResult]:
        """Validate a single task item."""
        results = []
        section_name = f"Task {task.number}"

        # Validate task actionability
        results.extend(self._validate_task_actionability(task, section_name))

        # Validate requirements references
        results.extend(self._validate_task_requirements(task, section_name))

        # Validate task specificity
        results.extend(self._validate_task_specificity(task, section_name))

        return results

    def _validate_task_actionability(
        self, task: TaskItem, section_name: str
    ) -> List[ValidationResult]:
        """Validate that task is actionable and coding-focused."""
        results = []

        full_text = f"{task.title} {' '.join(task.details)}".lower()

        # Check for non-coding activities
        for indicator in self.NON_CODING_INDICATORS:
            if indicator in full_text:
                results.append(
                    ValidationResult(
                        type="error",
                        message=f'{section_name} contains non-coding activity: "{indicator}"',
                        location=ValidationLocation(
                            section=section_name, line=task.line_start
                        ),
                        suggestion="Focus on coding activities like implementing, writing, or testing code",
                    )
                )

        # Check for actionable verbs
        has_coding_verb = any(verb in full_text for verb in self.CODING_VERBS)
        if not has_coding_verb:
            results.append(
                ValidationResult(
                    type="warning",
                    message=f"{section_name} lacks actionable coding verbs",
                    location=ValidationLocation(
                        section=section_name, line=task.line_start
                    ),
                    suggestion="Use action verbs like implement, create, write, build, test",
                )
            )

        # Check for vague language
        for indicator in self.VAGUE_INDICATORS:
            if indicator in full_text:
                results.append(
                    ValidationResult(
                        type="warning",
                        message=f'{section_name} contains vague language: "{indicator}"',
                        location=ValidationLocation(
                            section=section_name, line=task.line_start
                        ),
                        suggestion="Be specific about what code to write or modify",
                    )
                )

        return results

    def _validate_task_requirements(
        self, task: TaskItem, section_name: str
    ) -> List[ValidationResult]:
        """Validate task requirements references."""
        results = []

        if not task.requirements_refs:
            results.append(
                ValidationResult(
                    type="error",
                    message=f"{section_name} missing requirements reference",
                    location=ValidationLocation(
                        section=section_name, line=task.line_start
                    ),
                    suggestion="Add _Requirements: X.X_ reference to link task to specific requirements",
                )
            )
        else:
            # Validate requirement reference format
            for ref in task.requirements_refs:
                if not re.match(r"^\d+(\.\d+)*$", ref.strip()):
                    results.append(
                        ValidationResult(
                            type="error",
                            message=f'{section_name} has invalid requirement reference format: "{ref}"',
                            location=ValidationLocation(
                                section=section_name, line=task.line_start
                            ),
                            suggestion="Use format like 1.1, 2.3, etc. for requirement references",
                        )
                    )

        return results

    def _validate_task_specificity(
        self, task: TaskItem, section_name: str
    ) -> List[ValidationResult]:
        """Validate task specificity and implementation details."""
        results = []

        # Check if task has implementation details (excluding requirements references)
        implementation_details = [
            detail
            for detail in task.details
            if not self.requirements_ref_regex.search(detail)
        ]
        if not implementation_details:
            results.append(
                ValidationResult(
                    type="warning",
                    message=f"{section_name} lacks implementation details",
                    location=ValidationLocation(
                        section=section_name, line=task.line_start
                    ),
                    suggestion="Add bullet points with specific implementation steps",
                )
            )

        # Check task title length (too short might be vague)
        if len(task.title.split()) < 3:
            results.append(
                ValidationResult(
                    type="warning",
                    message=f"{section_name} title may be too brief",
                    location=ValidationLocation(
                        section=section_name, line=task.line_start
                    ),
                    suggestion="Provide more descriptive task titles with specific objectives",
                )
            )

        # Check for specific file/component mentions
        full_text = f"{task.title} {' '.join(task.details)}".lower()
        has_specifics = any(
            keyword in full_text
            for keyword in [
                "class",
                "method",
                "function",
                "file",
                "component",
                "module",
                "interface",
                "api",
                "endpoint",
                "database",
                "table",
                "model",
            ]
        )

        if not has_specifics:
            results.append(
                ValidationResult(
                    type="info",
                    message=f"{section_name} could be more specific about implementation targets",
                    location=ValidationLocation(
                        section=section_name, line=task.line_start
                    ),
                    suggestion="Mention specific files, classes, methods, or components to implement",
                )
            )

        return results

    def _validate_task_numbering(self, tasks: List[TaskItem]) -> List[ValidationResult]:
        """Validate task numbering and hierarchy."""
        results = []

        if not tasks:
            return results

        # Group tasks by parent
        main_tasks = [t for t in tasks if not t.is_subtask]
        subtasks_by_parent = {}

        for task in tasks:
            if task.is_subtask:
                parent = task.parent_task
                if parent not in subtasks_by_parent:
                    subtasks_by_parent[parent] = []
                subtasks_by_parent[parent].append(task)

        # Validate main task numbering
        expected_main = 1
        for task in main_tasks:
            if task.number != str(expected_main):
                results.append(
                    ValidationResult(
                        type="error",
                        message=f"Task numbering error: expected {expected_main}, found {task.number}",
                        location=ValidationLocation(
                            section=f"Task {task.number}", line=task.line_start
                        ),
                        suggestion=f"Renumber this task to {expected_main}",
                    )
                )
            expected_main += 1

        # Validate subtask numbering
        for parent_num, subtasks in subtasks_by_parent.items():
            # Sort subtasks by their actual number for proper validation
            sorted_subtasks = sorted(
                subtasks,
                key=lambda t: float(t.number.split(".")[1]) if "." in t.number else 0,
            )
            expected_sub = 1
            for subtask in sorted_subtasks:
                expected_number = f"{parent_num}.{expected_sub}"
                if subtask.number != expected_number:
                    results.append(
                        ValidationResult(
                            type="error",
                            message=f"Subtask numbering error: expected {expected_number}, found {subtask.number}",
                            location=ValidationLocation(
                                section=f"Task {subtask.number}",
                                line=subtask.line_start,
                            ),
                            suggestion=f"Renumber this subtask to {expected_number}",
                        )
                    )
                expected_sub += 1

        # Check for orphaned subtasks
        main_task_numbers = {t.number for t in main_tasks}
        for task in tasks:
            if task.is_subtask and task.parent_task not in main_task_numbers:
                results.append(
                    ValidationResult(
                        type="error",
                        message=f"Subtask {task.number} has no corresponding parent task {task.parent_task}",
                        location=ValidationLocation(
                            section=f"Task {task.number}", line=task.line_start
                        ),
                        suggestion=f"Add parent task {task.parent_task} or renumber this subtask",
                    )
                )

        return results

    def _validate_task_sequencing(
        self, tasks: List[TaskItem]
    ) -> List[ValidationResult]:
        """Validate logical task sequencing and dependencies."""
        results = []

        # Check for proper incremental development
        # This is a basic check - could be enhanced with more sophisticated dependency analysis

        # Look for setup/foundation tasks early
        setup_keywords = [
            "setup",
            "initialize",
            "create structure",
            "foundation",
            "configure",
        ]
        has_early_setup = False

        if tasks:
            first_few_tasks = tasks[:3]  # Check first 3 tasks
            for task in first_few_tasks:
                full_text = f"{task.title} {' '.join(task.details)}".lower()
                if any(keyword in full_text for keyword in setup_keywords):
                    has_early_setup = True
                    break

            if not has_early_setup:
                results.append(
                    ValidationResult(
                        type="info",
                        message="Consider starting with setup/foundation tasks",
                        location=ValidationLocation(section="document"),
                        suggestion="Begin with tasks that set up project structure or core interfaces",
                    )
                )

        # Check for testing integration throughout
        test_keywords = ["test", "testing", "unit test", "integration test"]
        testing_tasks = []

        for task in tasks:
            full_text = f"{task.title} {' '.join(task.details)}".lower()
            if any(keyword in full_text for keyword in test_keywords):
                testing_tasks.append(task)

        if len(testing_tasks) == 0:
            results.append(
                ValidationResult(
                    type="warning",
                    message="Implementation plan lacks testing tasks",
                    location=ValidationLocation(section="document"),
                    suggestion="Include unit testing and integration testing tasks throughout",
                )
            )
        elif len(testing_tasks) < len(tasks) // 3:  # Less than 1/3 are testing tasks
            results.append(
                ValidationResult(
                    type="info",
                    message="Consider adding more testing tasks throughout implementation",
                    location=ValidationLocation(section="document"),
                    suggestion="Include testing tasks after major implementation milestones",
                )
            )

        return results

    def _validate_requirements_traceability(
        self, tasks: List[TaskItem], requirements_content: str
    ) -> List[ValidationResult]:
        """Validate that tasks trace back to requirements."""
        results = []

        # Extract requirement numbers from requirements document
        req_numbers = self._extract_requirement_numbers(requirements_content)

        # Extract requirement references from tasks
        task_refs = set()
        for task in tasks:
            task_refs.update(task.requirements_refs)

        # Check for requirements not covered by tasks
        uncovered_reqs = req_numbers - task_refs
        for req_num in uncovered_reqs:
            results.append(
                ValidationResult(
                    type="warning",
                    message=f"Requirement {req_num} not covered by any task",
                    location=ValidationLocation(section="document"),
                    suggestion=f"Add tasks that implement requirement {req_num}",
                )
            )

        # Check for invalid requirement references
        invalid_refs = task_refs - req_numbers
        for ref in invalid_refs:
            results.append(
                ValidationResult(
                    type="error",
                    message=f"Tasks reference non-existent requirement {ref}",
                    location=ValidationLocation(section="document"),
                    suggestion=f"Remove reference to requirement {ref} or verify requirement exists",
                )
            )

        return results

    def _extract_requirement_numbers(self, requirements_content: str) -> Set[str]:
        """Extract requirement numbers from requirements document."""
        req_numbers = set()

        # Look for requirement headers like "### Requirement 1"
        req_header_pattern = r"###\s+Requirement\s+(\d+(?:\.\d+)*)"
        matches = re.findall(req_header_pattern, requirements_content)
        req_numbers.update(matches)

        return req_numbers
