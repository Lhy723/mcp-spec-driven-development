"""Tests for the comprehensive error handling system."""

import logging
from typing import List
from unittest.mock import Mock, patch

import pytest

from src.mcp_spec_driven_development.error_handler import ErrorHandler
from src.mcp_spec_driven_development.exceptions import (
    ContentAccessError,
    ErrorSeverity,
    RecoverySuggestion,
    SpecDrivenDevelopmentError,
    StateError,
    TaskExecutionError,
    ValidationError,
    WorkflowError,
)
from src.mcp_spec_driven_development.workflow.models import (
    PhaseType,
    ValidationLocation,
    ValidationResult,
)


class TestCustomExceptions:
    """Test custom exception classes."""

    def test_base_exception_creation(self):
        """Test creating base SpecDrivenDevelopmentError."""
        error = SpecDrivenDevelopmentError(
            message="Test error", severity=ErrorSeverity.HIGH, context={"test": "value"}
        )

        assert error.message == "Test error"
        assert error.severity == ErrorSeverity.HIGH
        assert error.context == {"test": "value"}
        assert error.recovery_suggestions == []

    def test_recovery_suggestion_management(self):
        """Test adding and sorting recovery suggestions."""
        error = SpecDrivenDevelopmentError("Test error")

        suggestion1 = RecoverySuggestion("Action 1", "Description 1", 3)
        suggestion2 = RecoverySuggestion("Action 2", "Description 2", 1)
        suggestion3 = RecoverySuggestion("Action 3", "Description 3", 2)

        error.add_recovery_suggestion(suggestion1)
        error.add_recovery_suggestion(suggestion2)
        error.add_recovery_suggestion(suggestion3)

        # Should be sorted by priority (lower numbers first)
        assert error.recovery_suggestions[0].action == "Action 2"
        assert error.recovery_suggestions[1].action == "Action 3"
        assert error.recovery_suggestions[2].action == "Action 1"

    def test_formatted_message(self):
        """Test formatted error message with recovery suggestions."""
        error = SpecDrivenDevelopmentError(
            message="Test error", severity=ErrorSeverity.CRITICAL
        )

        error.add_recovery_suggestion(RecoverySuggestion("Fix it", "Try this fix", 1))
        error.add_recovery_suggestion(
            RecoverySuggestion("Alternative", "Or try this", 2)
        )

        formatted = error.get_formatted_message()

        assert "[CRITICAL] Test error" in formatted
        assert "Recovery suggestions:" in formatted
        assert "1. Fix it: Try this fix" in formatted
        assert "2. Alternative: Or try this" in formatted

    def test_validation_error_defaults(self):
        """Test ValidationError with default recovery suggestions."""
        error = ValidationError(
            message="Validation failed", document_type="requirements"
        )

        # Should have default suggestions for requirements
        assert len(error.recovery_suggestions) > 0
        assert any("EARS format" in s.action for s in error.recovery_suggestions)

    def test_workflow_error_defaults(self):
        """Test WorkflowError with default recovery suggestions."""
        error = WorkflowError(
            message="Phase transition failed",
            current_phase=PhaseType.REQUIREMENTS,
            attempted_action="phase_transition",
        )

        # Should have default suggestions for phase transitions
        assert len(error.recovery_suggestions) > 0
        assert any(
            "phase status" in s.action.lower() for s in error.recovery_suggestions
        )

    def test_content_access_error_defaults(self):
        """Test ContentAccessError with default recovery suggestions."""
        error = ContentAccessError(
            message="Template not found",
            content_type="template",
            requested_item="requirements",
        )

        # Should have default suggestions for content access
        assert len(error.recovery_suggestions) > 0
        assert any(
            "content type" in s.action.lower() for s in error.recovery_suggestions
        )


class TestErrorHandler:
    """Test the ErrorHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.logger = Mock(spec=logging.Logger)
        self.error_handler = ErrorHandler(self.logger)

    def test_initialization(self):
        """Test ErrorHandler initialization."""
        assert self.error_handler.logger == self.logger
        assert self.error_handler._error_history == []
        assert self.error_handler._fallback_handlers == {}

    def test_register_fallback_handler(self):
        """Test registering fallback handlers."""
        handler = Mock()
        self.error_handler.register_fallback_handler("test_type", handler)

        assert self.error_handler._fallback_handlers["test_type"] == handler

    def test_handle_validation_error(self):
        """Test handling validation errors."""
        validation_results = [
            ValidationResult(
                type="error",
                message="EARS format violation",
                location=ValidationLocation(section="Requirement 1"),
            )
        ]

        error = self.error_handler.handle_validation_error(
            message="Validation failed",
            validation_results=validation_results,
            document_type="requirements",
        )

        assert isinstance(error, ValidationError)
        assert error.message == "Validation failed"
        assert error.validation_results == validation_results
        assert error.document_type == "requirements"
        assert error.severity == ErrorSeverity.HIGH

        # Should be logged and added to history
        self.logger.log.assert_called()
        assert error in self.error_handler._error_history

    def test_handle_workflow_error(self):
        """Test handling workflow errors."""
        error = self.error_handler.handle_workflow_error(
            message="Phase transition failed",
            current_phase="requirements",
            attempted_action="phase_transition",
        )

        assert isinstance(error, WorkflowError)
        assert error.message == "Phase transition failed"
        assert error.current_phase == PhaseType.REQUIREMENTS
        assert error.attempted_action == "phase_transition"
        assert error.severity == ErrorSeverity.MEDIUM

        # Should be logged and added to history
        self.logger.log.assert_called()
        assert error in self.error_handler._error_history

    def test_handle_content_access_error_with_fallback(self):
        """Test handling content access errors with fallback."""
        fallback_handler = Mock(return_value="fallback content")
        self.error_handler.register_fallback_handler(
            "content_template", fallback_handler
        )

        error = self.error_handler.handle_content_access_error(
            message="Template not found",
            content_type="template",
            requested_item="requirements",
        )

        assert isinstance(error, ContentAccessError)
        assert error.context["fallback_available"] is True
        assert error.context["fallback_result"] == "fallback content"

        # Should have called fallback handler
        fallback_handler.assert_called_once_with("requirements")

    def test_handle_content_access_error_fallback_failure(self):
        """Test handling content access errors when fallback fails."""
        fallback_handler = Mock(side_effect=Exception("Fallback failed"))
        self.error_handler.register_fallback_handler(
            "content_template", fallback_handler
        )

        error = self.error_handler.handle_content_access_error(
            message="Template not found",
            content_type="template",
            requested_item="requirements",
        )

        assert isinstance(error, ContentAccessError)
        assert "fallback_error" in error.context
        assert error.context["fallback_error"] == "Fallback failed"

    def test_handle_state_error(self):
        """Test handling state errors."""
        error = self.error_handler.handle_state_error(
            message="Invalid state",
            feature_name="test-feature",
            state_operation="transition",
        )

        assert isinstance(error, StateError)
        assert error.message == "Invalid state"
        assert error.feature_name == "test-feature"
        assert error.state_operation == "transition"
        assert error.severity == ErrorSeverity.HIGH

    def test_handle_task_execution_error(self):
        """Test handling task execution errors."""
        execution_context = {"task_details": "test details"}

        error = self.error_handler.handle_task_execution_error(
            message="Task failed", task_id="1.1", execution_context=execution_context
        )

        assert isinstance(error, TaskExecutionError)
        assert error.message == "Task failed"
        assert error.task_id == "1.1"
        assert error.execution_context == execution_context
        assert error.severity == ErrorSeverity.MEDIUM

    def test_error_history_management(self):
        """Test error history management."""
        error1 = self.error_handler.handle_generic_error("Error 1")
        error2 = self.error_handler.handle_generic_error("Error 2")

        history = self.error_handler.get_error_history()
        assert len(history) == 2
        assert error1 in history
        assert error2 in history

        self.error_handler.clear_error_history()
        assert len(self.error_handler.get_error_history()) == 0

    def test_context_specific_recovery_suggestions(self):
        """Test getting context-specific recovery suggestions."""
        context = {"document_type": "requirements"}
        suggestions = self.error_handler.get_recovery_suggestions_for_context(
            "validation", context
        )

        assert len(suggestions) > 0
        assert any("EARS" in s.action for s in suggestions)

        context = {"attempted_action": "phase_transition"}
        suggestions = self.error_handler.get_recovery_suggestions_for_context(
            "workflow", context
        )

        assert len(suggestions) > 0
        assert any("phase" in s.action.lower() for s in suggestions)

    def test_error_context_manager_success(self):
        """Test error context manager with successful operation."""
        with self.error_handler.error_context("test_operation", param="value"):
            result = "success"

        assert result == "success"
        # No errors should be logged for successful operations
        assert len(self.error_handler._error_history) == 0

    def test_error_context_manager_custom_exception(self):
        """Test error context manager with custom exception."""
        custom_error = ValidationError("Custom validation error")

        with pytest.raises(ValidationError):
            with self.error_handler.error_context("test_operation"):
                raise custom_error

        # Custom exceptions should be re-raised as-is
        assert len(self.error_handler._error_history) == 0

    def test_error_context_manager_generic_exception(self):
        """Test error context manager with generic exception."""
        with pytest.raises(SpecDrivenDevelopmentError) as exc_info:
            with self.error_handler.error_context("test_operation", param="value"):
                raise ValueError("Generic error")

        error = exc_info.value
        assert "Unexpected error during test_operation" in error.message
        assert error.context["operation"] == "test_operation"
        assert error.context["param"] == "value"
        assert "Generic error" in error.context["original_exception"]

    def test_validation_specific_suggestions(self):
        """Test adding validation-specific recovery suggestions."""
        validation_results = [
            ValidationResult(
                type="error",
                message="EARS format violation in acceptance criteria",
                location=ValidationLocation(section="Requirement 1"),
            ),
            ValidationResult(
                type="error",
                message="User story format is incorrect",
                location=ValidationLocation(section="Requirement 2"),
            ),
            ValidationResult(
                type="error",
                message="Missing requirement reference in task",
                location=ValidationLocation(section="Task 1.1"),
            ),
        ]

        error = ValidationError(
            message="Multiple validation errors",
            validation_results=validation_results,
            document_type="requirements",
        )

        self.error_handler._add_validation_specific_suggestions(
            error, validation_results
        )

        # Should have suggestions for EARS format, user story, and requirement references
        suggestions = [s.action for s in error.recovery_suggestions]
        assert any("EARS format" in s for s in suggestions)
        assert any("user story" in s for s in suggestions)
        assert any("requirement references" in s for s in suggestions)


class TestErrorHandlerIntegration:
    """Test error handler integration with other components."""

    def test_content_loader_error_handling(self):
        """Test error handling in content loader."""
        from src.mcp_spec_driven_development.content.content_loader import ContentLoader

        # Mock file system to simulate missing files
        with patch("pathlib.Path.exists", return_value=False):
            loader = ContentLoader()

            # Should use fallback content when primary content is missing
            content = loader.get_methodology_content("workflow")
            assert content is not None
            assert "spec-driven development" in content.lower()

    def test_validation_error_handling(self):
        """Test error handling in validation components."""
        from src.mcp_spec_driven_development.validation.requirements_validator import (
            RequirementsValidator,
        )

        validator = RequirementsValidator()

        # Test with empty content
        with pytest.raises(ValidationError) as exc_info:
            validator.validate("")

        error = exc_info.value
        assert "empty" in error.message.lower()
        assert error.document_type == "requirements"
        assert len(error.recovery_suggestions) > 0

    def test_workflow_tools_error_handling(self):
        """Test error handling in workflow tools."""
        from src.mcp_spec_driven_development.tools.workflow_tools import (
            WorkflowManagementTools,
        )

        tools = WorkflowManagementTools()

        # Test with invalid feature name
        import asyncio

        result = asyncio.run(tools.handle_get_workflow_status({"feature_name": ""}))

        assert len(result) == 1
        assert "required" in result[0].text.lower()


class TestFallbackContent:
    """Test fallback content provider."""

    def test_fallback_content_provider(self):
        """Test fallback content provider functionality."""
        from src.mcp_spec_driven_development.fallback_content import (
            FallbackContentProvider,
        )

        provider = FallbackContentProvider()

        # Test fallback templates
        requirements_template = provider.get_fallback_template("requirements")
        assert requirements_template is not None
        assert "Requirements Document" in requirements_template
        assert "EARS format" in requirements_template or "WHEN" in requirements_template

        design_template = provider.get_fallback_template("design")
        assert design_template is not None
        assert "Design Document" in design_template
        assert "Architecture" in design_template

        tasks_template = provider.get_fallback_template("tasks")
        assert tasks_template is not None
        assert "Implementation Plan" in tasks_template
        assert "Requirements:" in tasks_template

        # Test fallback methodology
        workflow_content = provider.get_fallback_methodology("workflow")
        assert workflow_content is not None
        assert "three" in workflow_content.lower()
        assert "requirements" in workflow_content.lower()

        # Test fallback examples
        requirements_example = provider.get_fallback_example("requirements")
        assert requirements_example is not None
        assert "WHEN" in requirements_example or "IF" in requirements_example

        # Test error guidance
        validation_guidance = provider.get_generic_error_guidance("validation")
        assert validation_guidance is not None
        assert "validation" in validation_guidance.lower()

        # Test recovery steps
        recovery_steps = provider.get_recovery_steps({"error_type": "validation"})
        assert len(recovery_steps) > 0
        assert all(
            step.startswith(("1.", "2.", "3.", "4.", "5.")) for step in recovery_steps
        )

        # Test alternative approaches
        alternatives = provider.get_alternative_approaches("template_access")
        assert len(alternatives) > 0
        assert any("fallback" in alt.lower() for alt in alternatives)


if __name__ == "__main__":
    pytest.main([__file__])
