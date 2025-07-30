"""Centralized error handling system for the MCP spec-driven development tool."""

import logging
import traceback
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Union

from .exceptions import (
    ContentAccessError,
    ErrorSeverity,
    RecoverySuggestion,
    SpecDrivenDevelopmentError,
    StateError,
    TaskExecutionError,
    ValidationError,
    WorkflowError,
)
from .workflow.models import ValidationResult


class ErrorHandler:
    """Centralized error handling system with recovery suggestions and fallback options."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize error handler with optional logger."""
        self.logger = logger or logging.getLogger(__name__)
        self._error_history: List[SpecDrivenDevelopmentError] = []
        self._fallback_handlers: Dict[str, Callable] = {}

    def register_fallback_handler(self, error_type: str, handler: Callable) -> None:
        """Register a fallback handler for a specific error type."""
        self._fallback_handlers[error_type] = handler

    def handle_validation_error(
        self,
        message: str,
        validation_results: Optional[List[ValidationResult]] = None,
        document_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationError:
        """Handle validation errors with specific feedback."""
        error = ValidationError(
            message=message,
            validation_results=validation_results,
            document_type=document_type,
            severity=ErrorSeverity.HIGH,
            context=context,
        )

        # Add specific recovery suggestions based on validation results
        if validation_results:
            self._add_validation_specific_suggestions(error, validation_results)

        self._log_error(error)
        self._error_history.append(error)
        return error

    def handle_workflow_error(
        self,
        message: str,
        current_phase: Optional[str] = None,
        attempted_action: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> WorkflowError:
        """Handle workflow errors with recovery suggestions."""
        from .workflow.models import PhaseType

        phase_enum = None
        if current_phase:
            try:
                phase_enum = PhaseType(current_phase)
            except ValueError:
                pass

        error = WorkflowError(
            message=message,
            current_phase=phase_enum,
            attempted_action=attempted_action,
            severity=ErrorSeverity.MEDIUM,
            context=context,
        )

        self._log_error(error)
        self._error_history.append(error)
        return error

    def handle_content_access_error(
        self,
        message: str,
        content_type: Optional[str] = None,
        requested_item: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> ContentAccessError:
        """Handle content access errors with fallback options."""
        error = ContentAccessError(
            message=message,
            content_type=content_type,
            requested_item=requested_item,
            severity=ErrorSeverity.LOW,
            context=context,
        )

        # Try fallback handler if available
        fallback_key = f"content_{content_type}"
        if fallback_key in self._fallback_handlers:
            try:
                fallback_result = self._fallback_handlers[fallback_key](requested_item)
                error.context["fallback_available"] = True
                error.context["fallback_result"] = fallback_result
                error.add_recovery_suggestion(
                    RecoverySuggestion(
                        "Use fallback content",
                        "Fallback content is available and has been provided",
                        1,
                    )
                )
            except Exception as fallback_error:
                error.context["fallback_error"] = str(fallback_error)

        self._log_error(error)
        self._error_history.append(error)
        return error

    def handle_state_error(
        self,
        message: str,
        feature_name: Optional[str] = None,
        state_operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> StateError:
        """Handle state management errors."""
        error = StateError(
            message=message,
            feature_name=feature_name,
            state_operation=state_operation,
            severity=ErrorSeverity.HIGH,
            context=context,
        )

        self._log_error(error)
        self._error_history.append(error)
        return error

    def handle_task_execution_error(
        self,
        message: str,
        task_id: Optional[str] = None,
        execution_context: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> TaskExecutionError:
        """Handle task execution errors."""
        error = TaskExecutionError(
            message=message,
            task_id=task_id,
            execution_context=execution_context,
            severity=ErrorSeverity.MEDIUM,
            context=context,
        )

        self._log_error(error)
        self._error_history.append(error)
        return error

    def handle_generic_error(
        self,
        message: str,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recovery_suggestions: Optional[List[RecoverySuggestion]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> SpecDrivenDevelopmentError:
        """Handle generic errors."""
        error = SpecDrivenDevelopmentError(
            message=message,
            severity=severity,
            recovery_suggestions=recovery_suggestions,
            context=context,
        )

        self._log_error(error)
        self._error_history.append(error)
        return error

    def get_error_history(self) -> List[SpecDrivenDevelopmentError]:
        """Get the history of handled errors."""
        return self._error_history.copy()

    def clear_error_history(self) -> None:
        """Clear the error history."""
        self._error_history.clear()

    def get_recovery_suggestions_for_context(
        self, error_type: str, context: Dict[str, Any]
    ) -> List[RecoverySuggestion]:
        """Get context-specific recovery suggestions."""
        suggestions = []

        if error_type == "validation":
            if context.get("document_type") == "requirements":
                suggestions.extend(
                    [
                        RecoverySuggestion(
                            "Use EARS template",
                            "Apply the EARS format template to structure acceptance criteria",
                            1,
                        ),
                        RecoverySuggestion(
                            "Check user story format",
                            "Ensure user stories follow 'As a...I want...so that' pattern",
                            2,
                        ),
                    ]
                )
            elif context.get("document_type") == "design":
                suggestions.extend(
                    [
                        RecoverySuggestion(
                            "Use design template",
                            "Apply the design document template to ensure all sections are present",
                            1,
                        ),
                        RecoverySuggestion(
                            "Add missing sections",
                            "Include any missing required sections from the design template",
                            2,
                        ),
                    ]
                )

        elif error_type == "workflow":
            if context.get("attempted_action") == "phase_transition":
                suggestions.extend(
                    [
                        RecoverySuggestion(
                            "Complete current phase",
                            "Ensure the current phase is fully completed before transitioning",
                            1,
                        ),
                        RecoverySuggestion(
                            "Get approval",
                            "Obtain explicit user approval for the current phase",
                            2,
                        ),
                    ]
                )

        return suggestions

    def _add_validation_specific_suggestions(
        self, error: ValidationError, validation_results: List[ValidationResult]
    ) -> None:
        """Add specific recovery suggestions based on validation results."""
        error_types = {result.type for result in validation_results}

        if "error" in error_types:
            error.add_recovery_suggestion(
                RecoverySuggestion(
                    "Fix validation errors",
                    "Address all validation errors before proceeding",
                    1,
                )
            )

        # Look for specific validation patterns
        for result in validation_results:
            if "EARS format" in result.message:
                error.add_recovery_suggestion(
                    RecoverySuggestion(
                        "Apply EARS format",
                        "Use WHEN/IF/WHILE/WHERE...THEN...SHALL structure for acceptance criteria",
                        2,
                    )
                )
            elif "user story" in result.message.lower():
                error.add_recovery_suggestion(
                    RecoverySuggestion(
                        "Fix user story format",
                        "Use 'As a [role], I want [feature], so that [benefit]' format",
                        2,
                    )
                )
            elif (
                "requirement" in result.message.lower()
                and "reference" in result.message.lower()
            ):
                error.add_recovery_suggestion(
                    RecoverySuggestion(
                        "Add requirement references",
                        "Include _Requirements: X.X_ references in task descriptions",
                        2,
                    )
                )

    def _log_error(self, error: SpecDrivenDevelopmentError) -> None:
        """Log an error with appropriate level."""
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL,
        }.get(error.severity, logging.WARNING)

        self.logger.log(log_level, f"{error.__class__.__name__}: {error.message}")

        if error.context:
            self.logger.debug(f"Error context: {error.context}")

    @contextmanager
    def error_context(self, operation: str, **context_data):
        """Context manager for handling errors in a specific operation."""
        try:
            yield
        except SpecDrivenDevelopmentError:
            # Re-raise our custom errors
            raise
        except Exception as e:
            # Convert generic exceptions to our custom errors
            error = self.handle_generic_error(
                message=f"Unexpected error during {operation}: {str(e)}",
                severity=ErrorSeverity.HIGH,
                context={
                    "operation": operation,
                    "original_exception": str(e),
                    "traceback": traceback.format_exc(),
                    **context_data,
                },
            )
            raise error from e


def error_handler_decorator(error_handler: ErrorHandler, operation: str):
    """Decorator for automatic error handling in methods."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            with error_handler.error_context(operation, function=func.__name__):
                return func(*args, **kwargs)

        return wrapper

    return decorator


# Global error handler instance
_global_error_handler = ErrorHandler()


def get_error_handler() -> ErrorHandler:
    """Get the global error handler instance."""
    return _global_error_handler


def set_error_handler(handler: ErrorHandler) -> None:
    """Set the global error handler instance."""
    global _global_error_handler
    _global_error_handler = handler
