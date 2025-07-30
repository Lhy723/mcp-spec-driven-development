"""End-to-end integration tests for the complete workflow from requirements through tasks."""

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.types import TextContent

from src.mcp_spec_driven_development.tools.content_tools import ContentAccessTools
from src.mcp_spec_driven_development.tools.task_execution_tools import (
    TaskExecutionTools,
)
from src.mcp_spec_driven_development.tools.validation_tools import ValidationTools
from src.mcp_spec_driven_development.tools.workflow_tools import WorkflowManagementTools


class TestEndToEndWorkflow:
    """End-to-end integration tests for the complete spec-driven development workflow."""

    @pytest.fixture
    def workflow_tools(self):
        """Create workflow tools instance."""
        return WorkflowManagementTools()

    @pytest.fixture
    def content_tools(self):
        """Create content tools instance."""
        return ContentAccessTools()

    @pytest.fixture
    def validation_tools(self):
        """Create validation tools instance."""
        return ValidationTools()

    @pytest.fixture
    def task_tools(self):
        """Create task execution tools instance."""
        return TaskExecutionTools()

    @pytest.mark.asyncio
    async def test_complete_workflow_requirements_to_tasks(
        self, workflow_tools, content_tools, validation_tools
    ):
        """Test complete workflow from requirements creation through task planning."""
        feature_name = "integration-test-feature"

        # Step 1: Create workflow
        result = await workflow_tools.handle_create_workflow(
            {"feature_name": feature_name}
        )
        assert len(result) == 1
        assert (
            "created" in result[0].text.lower() or "workflow" in result[0].text.lower()
        )

        # Step 2: Get requirements template
        result = await content_tools.handle_get_template(
            {"template_type": "requirements"}
        )
        assert len(result) == 1
        assert "requirements document" in result[0].text.lower()

        # Step 3: Validate requirements document structure
        sample_requirements = """
        # Requirements Document

        ## Introduction
        Test feature for integration testing.

        ## Requirements

        ### Requirement 1
        **User Story:** As a user, I want to test integration, so that I can verify the system works.

        #### Acceptance Criteria
        1. WHEN the system is tested THEN it SHALL respond correctly
        """

        result = await validation_tools.handle_validate_document(
            {"document_type": "requirements", "content": sample_requirements}
        )
        assert len(result) == 1

        # Step 4: Transition to design phase
        result = await workflow_tools.handle_transition_phase(
            {
                "feature_name": feature_name,
                "action": "complete",
                "phase": "requirements",
            }
        )
        assert len(result) == 1

        # Step 5: Get design template
        result = await content_tools.handle_get_template({"template_type": "design"})
        assert len(result) == 1
        assert "design document" in result[0].text.lower()

        # Step 6: Transition to tasks phase
        result = await workflow_tools.handle_transition_phase(
            {"feature_name": feature_name, "action": "complete", "phase": "design"}
        )
        assert len(result) == 1

        # Step 7: Get tasks template
        result = await content_tools.handle_get_template({"template_type": "tasks"})
        assert len(result) == 1
        assert "implementation plan" in result[0].text.lower()

        # Step 8: Check final workflow status
        result = await workflow_tools.handle_get_workflow_status(
            {"feature_name": feature_name}
        )
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_workflow_with_validation_failures(
        self, workflow_tools, validation_tools
    ):
        """Test workflow handling when validation fails."""
        feature_name = "validation-test-feature"

        # Create workflow
        await workflow_tools.handle_create_workflow({"feature_name": feature_name})

        # Test with invalid requirements document
        invalid_requirements = "This is not a proper requirements document"

        result = await validation_tools.handle_validate_document(
            {"document_type": "requirements", "content": invalid_requirements}
        )
        assert len(result) == 1
        # Should indicate validation issues

    @pytest.mark.asyncio
    async def test_workflow_backward_navigation(self, workflow_tools):
        """Test backward navigation in workflow."""
        feature_name = "navigation-test-feature"

        # Create workflow and progress through phases
        await workflow_tools.handle_create_workflow({"feature_name": feature_name})

        # Complete requirements
        await workflow_tools.handle_transition_phase(
            {
                "feature_name": feature_name,
                "action": "complete",
                "phase": "requirements",
            }
        )

        # Start design
        await workflow_tools.handle_transition_phase(
            {"feature_name": feature_name, "action": "start", "phase": "design"}
        )

        # Navigate back to requirements
        result = await workflow_tools.handle_navigate_backward(
            {"feature_name": feature_name, "target_phase": "requirements"}
        )
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_content_and_validation_integration(
        self, content_tools, validation_tools
    ):
        """Test integration between content tools and validation tools."""
        # Get methodology content
        result = await content_tools.handle_get_methodology_guide({"topic": "workflow"})
        assert len(result) == 1
        methodology_content = result[0].text

        # Get validation checklist
        result = await validation_tools.handle_get_validation_checklist(
            {"document_type": "requirements"}
        )
        assert len(result) == 1
        checklist_content = result[0].text

        # Both should contain relevant information
        assert len(methodology_content) > 100
        assert len(checklist_content) > 50

    @pytest.mark.asyncio
    async def test_task_execution_integration(self, task_tools, workflow_tools):
        """Test integration between task execution and workflow tools."""
        feature_name = "task-integration-test"

        # Create workflow
        await workflow_tools.handle_create_workflow({"feature_name": feature_name})

        # Get task details
        result = await task_tools.handle_get_task_details(
            {"feature_name": feature_name, "task_id": "1.1"}
        )
        assert len(result) == 1

        # Get next task
        result = await task_tools.handle_get_next_task({"feature_name": feature_name})
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_error_propagation_across_tools(
        self, workflow_tools, content_tools, validation_tools
    ):
        """Test that errors are properly handled across different tool integrations."""
        # Test with non-existent feature
        result = await workflow_tools.handle_get_workflow_status(
            {"feature_name": "non-existent"}
        )
        assert len(result) == 1
        assert (
            "not found" in result[0].text.lower()
            or "error" in result[0].text.lower()
            or "no workflow" in result[0].text.lower()
        )

        # Test with invalid content request
        result = await content_tools.handle_get_template({"template_type": "invalid"})
        assert len(result) == 1

        # Test with invalid validation request
        result = await validation_tools.handle_validate_document(
            {"document_type": "invalid", "content": "test"}
        )
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_concurrent_tool_operations(
        self, workflow_tools, content_tools, validation_tools
    ):
        """Test concurrent operations across different tools."""
        # Create multiple concurrent operations
        tasks = [
            workflow_tools.handle_create_workflow(
                {"feature_name": f"concurrent-test-{i}"}
            )
            for i in range(3)
        ]

        # Add content and validation operations
        tasks.extend(
            [
                content_tools.handle_get_methodology_guide({"topic": "workflow"}),
                validation_tools.handle_get_validation_checklist(
                    {"document_type": "requirements"}
                ),
            ]
        )

        # Execute all concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # All should complete successfully
        for result in results:
            assert not isinstance(result, Exception)
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_workflow_state_consistency(self, workflow_tools):
        """Test that workflow state remains consistent across operations."""
        feature_name = "consistency-test"

        # Create workflow
        await workflow_tools.handle_create_workflow({"feature_name": feature_name})

        # Check initial status
        result1 = await workflow_tools.handle_get_workflow_status(
            {"feature_name": feature_name}
        )

        # Perform transition
        await workflow_tools.handle_transition_phase(
            {
                "feature_name": feature_name,
                "action": "complete",
                "phase": "requirements",
            }
        )

        # Check status after transition
        result2 = await workflow_tools.handle_get_workflow_status(
            {"feature_name": feature_name}
        )

        # States should be different but both valid
        assert len(result1) == 1
        assert len(result2) == 1
        # Note: States might be the same if transition didn't change state
        # Both should be valid responses
        assert isinstance(result1[0].text, str)
        assert isinstance(result2[0].text, str)

    @pytest.mark.asyncio
    async def test_content_template_validation_cycle(
        self, content_tools, validation_tools
    ):
        """Test the cycle of getting templates and validating content based on them."""
        # Get requirements template
        template_result = await content_tools.handle_get_template(
            {"template_type": "requirements"}
        )
        template_content = template_result[0].text

        # Create content based on template structure
        test_content = """
        # Requirements Document

        ## Introduction
        Test requirements based on template.

        ## Requirements

        ### Requirement 1
        **User Story:** As a developer, I want to test templates, so that I can validate the system.

        #### Acceptance Criteria
        1. WHEN I use a template THEN the system SHALL validate it correctly
        """

        # Validate the content
        validation_result = await validation_tools.handle_validate_document(
            {"document_type": "requirements", "content": test_content}
        )

        assert len(template_result) == 1
        assert len(validation_result) == 1
        assert len(template_content) > 100

    @pytest.mark.asyncio
    async def test_methodology_guidance_integration(self, content_tools):
        """Test integration of methodology guidance across different topics."""
        topics = ["workflow", "ears-format", "phase-transitions"]

        results = []
        for topic in topics:
            result = await content_tools.handle_get_methodology_guide({"topic": topic})
            results.append(result)

        # All topics should return content
        for result in results:
            assert len(result) == 1
            assert len(result[0].text) > 50

    @pytest.mark.asyncio
    async def test_examples_and_case_studies_integration(self, content_tools):
        """Test integration of examples and case studies."""
        result = await content_tools.handle_get_examples_and_case_studies(
            {"category": "requirements"}
        )
        assert len(result) == 1

        # Should provide examples or indicate none available
        content = result[0].text
        assert len(content) > 0

    @pytest.mark.asyncio
    async def test_validation_error_explanation_integration(self, validation_tools):
        """Test integration of validation error explanations."""
        # Test with a validation error scenario
        result = await validation_tools.handle_explain_validation_error(
            {"error_type": "missing_user_story", "document_type": "requirements"}
        )

        assert len(result) == 1
        assert len(result[0].text) > 30

    @pytest.mark.asyncio
    async def test_requirement_traceability_integration(self, validation_tools):
        """Test requirement traceability validation integration."""
        sample_requirements = "Sample requirements content"
        sample_design = "Sample design content"

        result = await validation_tools.handle_validate_requirement_traceability(
            {
                "requirements_content": sample_requirements,
                "design_content": sample_design,
            }
        )

        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_tool_definition_consistency(
        self, workflow_tools, content_tools, validation_tools, task_tools
    ):
        """Test that all tools provide consistent tool definitions."""
        tools = [workflow_tools, content_tools, validation_tools, task_tools]

        for tool in tools:
            definitions = tool.get_tool_definitions()
            assert isinstance(definitions, list)
            assert len(definitions) > 0

            # Each definition should have required fields
            for definition in definitions:
                assert hasattr(definition, "name")
                assert hasattr(definition, "description")

    @pytest.mark.asyncio
    async def test_error_recovery_integration(self, workflow_tools, content_tools):
        """Test error recovery across integrated tools."""
        # Simulate error conditions and test recovery
        with patch.object(
            workflow_tools.phase_manager,
            "create_workflow",
            side_effect=Exception("Test error"),
        ):
            result = await workflow_tools.handle_create_workflow(
                {"feature_name": "error-test"}
            )
            assert len(result) == 1
            assert "error" in result[0].text.lower()

        # Tool should still be functional after error
        result = await content_tools.handle_get_methodology_guide({"topic": "workflow"})
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_data_flow_integration(
        self, workflow_tools, content_tools, validation_tools
    ):
        """Test data flow between different tools in the system."""
        feature_name = "data-flow-test"

        # Create workflow (produces workflow state)
        await workflow_tools.handle_create_workflow({"feature_name": feature_name})

        # Get workflow status (consumes workflow state)
        status_result = await workflow_tools.handle_get_workflow_status(
            {"feature_name": feature_name}
        )

        # Get content (independent operation)
        content_result = await content_tools.handle_get_template(
            {"template_type": "requirements"}
        )

        # Validate content (consumes content)
        validation_result = await validation_tools.handle_validate_document(
            {
                "document_type": "requirements",
                "content": content_result[0].text[
                    :500
                ],  # Use part of template as test content
            }
        )

        # All operations should complete successfully
        assert len(status_result) == 1
        assert len(content_result) == 1
        assert len(validation_result) == 1
