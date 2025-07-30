"""Custom exceptions for the MCP spec-driven development tool."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from .workflow.models import PhaseType, ValidationResult


class ErrorSeverity(Enum):
    """Severity levels for errors."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class RecoverySuggestion:
    """Represents a recovery suggestion for an error."""

    action: str
    description: str
    priority: int = 1  # Lower numbers = higher priority


class SpecDrivenDevelopmentError(Exception):
    """Base exception for all spec-driven development errors."""

    def __init__(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recovery_suggestions: Optional[List[RecoverySuggestion]] = None,
        context: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.severity = severity
        self.recovery_suggestions = recovery_suggestions or []
        self.context = context or {}

    def add_recovery_suggestion(self, suggestion: RecoverySuggestion) -> None:
        """Add a recovery suggestion to this error."""
        self.recovery_suggestions.append(suggestion)
        # Sort by priority
        self.recovery_suggestions.sort(key=lambda x: x.priority)

    def get_formatted_message(self) -> str:
        """Get a formatted error message with recovery suggestions."""
        message = f"[{self.severity.value.upper()}] {self.message}"

        if self.recovery_suggestions:
            message += "\n\nRecovery suggestions:"
            for i, suggestion in enumerate(self.recovery_suggestions, 1):
                message += f"\n{i}. {suggestion.action}: {suggestion.description}"

        return message


class ValidationError(SpecDrivenDevelopmentError):
    """Error during document validation."""

    def __init__(
        self,
        message: str,
        validation_results: Optional[List[ValidationResult]] = None,
        document_type: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.validation_results = validation_results or []
        self.document_type = document_type

        # Add default recovery suggestions for validation errors
        if not self.recovery_suggestions:
            self._add_default_validation_suggestions()

    def _add_default_validation_suggestions(self) -> None:
        """Add default recovery suggestions for validation errors."""
        if self.document_type == "requirements":
            self.add_recovery_suggestion(
                RecoverySuggestion(
                    "Check EARS format",
                    "Ensure acceptance criteria follow WHEN/IF/WHILE/WHERE...THEN...SHALL format",
                    1,
                )
            )
            self.add_recovery_suggestion(
                RecoverySuggestion(
                    "Verify user stories",
                    "Confirm all requirements have user stories in 'As a...I want...so that' format",
                    2,
                )
            )
        elif self.document_type == "design":
            self.add_recovery_suggestion(
                RecoverySuggestion(
                    "Check required sections",
                    "Ensure all required sections are present: Overview, Architecture, Components, Data Models, Error Handling, Testing Strategy",
                    1,
                )
            )
            self.add_recovery_suggestion(
                RecoverySuggestion(
                    "Verify requirements traceability",
                    "Check that design addresses all requirements from requirements document",
                    2,
                )
            )
        elif self.document_type == "tasks":
            self.add_recovery_suggestion(
                RecoverySuggestion(
                    "Check task format",
                    "Ensure tasks are properly formatted with checkboxes and numbering",
                    1,
                )
            )
            self.add_recovery_suggestion(
                RecoverySuggestion(
                    "Verify requirements references",
                    "Confirm all tasks reference specific requirements using _Requirements: X.X_ format",
                    2,
                )
            )


class WorkflowError(SpecDrivenDevelopmentError):
    """Error during workflow operations."""

    def __init__(
        self,
        message: str,
        current_phase: Optional[PhaseType] = None,
        attempted_action: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.current_phase = current_phase
        self.attempted_action = attempted_action

        # Add default recovery suggestions for workflow errors
        if not self.recovery_suggestions:
            self._add_default_workflow_suggestions()

    def _add_default_workflow_suggestions(self) -> None:
        """Add default recovery suggestions for workflow errors."""
        if self.attempted_action == "phase_transition":
            self.add_recovery_suggestion(
                RecoverySuggestion(
                    "Check phase status",
                    "Verify current phase is complete and approved before transitioning",
                    1,
                )
            )
            self.add_recovery_suggestion(
                RecoverySuggestion(
                    "Review workflow state",
                    "Use workflow status tool to check current state and requirements",
                    2,
                )
            )
        elif self.attempted_action == "approval":
            self.add_recovery_suggestion(
                RecoverySuggestion(
                    "Complete phase first",
                    "Ensure the phase is marked as complete before attempting approval",
                    1,
                )
            )
            self.add_recovery_suggestion(
                RecoverySuggestion(
                    "Validate document",
                    "Run validation on the document to ensure it meets requirements",
                    2,
                )
            )


class ContentAccessError(SpecDrivenDevelopmentError):
    """Error accessing content (templates, methodology, examples)."""

    def __init__(
        self,
        message: str,
        content_type: Optional[str] = None,
        requested_item: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.content_type = content_type
        self.requested_item = requested_item

        # Add default recovery suggestions for content access errors
        if not self.recovery_suggestions:
            self._add_default_content_suggestions()

    def _add_default_content_suggestions(self) -> None:
        """Add default recovery suggestions for content access errors."""
        self.add_recovery_suggestion(
            RecoverySuggestion(
                "Check content type",
                "Verify the requested content type is valid (methodology, template, example)",
                1,
            )
        )
        self.add_recovery_suggestion(
            RecoverySuggestion(
                "Use fallback content",
                "Try using generic templates or methodology if specific content is unavailable",
                2,
            )
        )
        self.add_recovery_suggestion(
            RecoverySuggestion(
                "Check file system",
                "Ensure content files are present in the expected directory structure",
                3,
            )
        )


class StateError(SpecDrivenDevelopmentError):
    """Error with workflow state management."""

    def __init__(
        self,
        message: str,
        feature_name: Optional[str] = None,
        state_operation: Optional[str] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.feature_name = feature_name
        self.state_operation = state_operation

        # Add default recovery suggestions for state errors
        if not self.recovery_suggestions:
            self._add_default_state_suggestions()

    def _add_default_state_suggestions(self) -> None:
        """Add default recovery suggestions for state errors."""
        self.add_recovery_suggestion(
            RecoverySuggestion(
                "Initialize workflow",
                "Create a new workflow if one doesn't exist for this feature",
                1,
            )
        )
        self.add_recovery_suggestion(
            RecoverySuggestion(
                "Reset state",
                "Consider resetting workflow state if it's in an invalid condition",
                2,
            )
        )
        self.add_recovery_suggestion(
            RecoverySuggestion(
                "Check feature name",
                "Verify the feature name is correct and matches existing workflows",
                3,
            )
        )


class TaskExecutionError(SpecDrivenDevelopmentError):
    """Error during task execution."""

    def __init__(
        self,
        message: str,
        task_id: Optional[str] = None,
        execution_context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ):
        super().__init__(message, **kwargs)
        self.task_id = task_id
        self.execution_context = execution_context or {}

        # Add default recovery suggestions for task execution errors
        if not self.recovery_suggestions:
            self._add_default_task_suggestions()

    def _add_default_task_suggestions(self) -> None:
        """Add default recovery suggestions for task execution errors."""
        self.add_recovery_suggestion(
            RecoverySuggestion(
                "Check task dependencies",
                "Ensure all prerequisite tasks are completed before executing this task",
                1,
            )
        )
        self.add_recovery_suggestion(
            RecoverySuggestion(
                "Review task details",
                "Verify task requirements and context are clear and actionable",
                2,
            )
        )
        self.add_recovery_suggestion(
            RecoverySuggestion(
                "Break down task",
                "Consider breaking complex tasks into smaller, more manageable subtasks",
                3,
            )
        )
