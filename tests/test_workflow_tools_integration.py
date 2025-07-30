"""Integration tests for workflow management tools."""

import pytest
from mcp.types import TextContent

from src.mcp_spec_driven_development.tools.workflow_tools import WorkflowManagementTools
from src.mcp_spec_driven_development.workflow.models import PhaseStatus, PhaseType


class TestWorkflowManagementToolsIntegration:
    """Integration tests for workflow management tools."""

    @pytest.fixture
    def workflow_tools(self):
        """Create workflow management tools instance."""
        return WorkflowManagementTools()

    @pytest.mark.asyncio
    async def test_create_workflow(self, workflow_tools):
        """Test creating a new workflow."""
        arguments = {"feature_name": "user-authentication"}
        result = await workflow_tools.handle_create_workflow(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check workflow creation response
        assert "Workflow Created: user-authentication" in content
        assert "**Current Phase**: requirements" in content
        assert "Requirements" in content
        assert "Design" in content
        assert "Tasks" in content

    @pytest.mark.asyncio
    async def test_create_workflow_missing_name(self, workflow_tools):
        """Test creating workflow without feature name."""
        arguments = {}
        result = await workflow_tools.handle_create_workflow(arguments)

        assert len(result) == 1
        assert "Error:" in result[0].text
        assert "feature_name is required" in result[0].text

    @pytest.mark.asyncio
    async def test_get_workflow_status_new_workflow(self, workflow_tools):
        """Test getting status of newly created workflow."""
        # Create workflow first
        await workflow_tools.handle_create_workflow({"feature_name": "test-feature"})

        # Get status
        arguments = {"feature_name": "test-feature"}
        result = await workflow_tools.handle_get_workflow_status(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check status content
        assert "Workflow Status: test-feature" in content
        assert "**Current Phase**: requirements" in content
        assert "**Completion**: 0.0%" in content
        assert "**Requirements**: ⏸️ Not Started" in content
        assert "**Design**: ⏸️ Not Started" in content
        assert "**Tasks**: ⏸️ Not Started" in content

    @pytest.mark.asyncio
    async def test_get_workflow_status_nonexistent(self, workflow_tools):
        """Test getting status of nonexistent workflow."""
        arguments = {"feature_name": "nonexistent"}
        result = await workflow_tools.handle_get_workflow_status(arguments)

        assert len(result) == 1
        assert "No workflow found" in result[0].text

    @pytest.mark.asyncio
    async def test_transition_phase_start_requirements(self, workflow_tools):
        """Test starting requirements phase."""
        # Create workflow first
        await workflow_tools.handle_create_workflow({"feature_name": "test-feature"})

        # Start requirements phase
        arguments = {
            "feature_name": "test-feature",
            "action": "start",
            "phase": "requirements",
        }
        result = await workflow_tools.handle_transition_phase(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check transition response
        assert "Phase Transition: test-feature" in content
        assert "Start requirements phase" in content
        assert "**New Status**: in_progress" in content

    @pytest.mark.asyncio
    async def test_transition_phase_complete_requirements(self, workflow_tools):
        """Test completing requirements phase."""
        # Create and start workflow
        await workflow_tools.handle_create_workflow({"feature_name": "test-feature"})
        await workflow_tools.handle_transition_phase(
            {"feature_name": "test-feature", "action": "start", "phase": "requirements"}
        )

        # Complete requirements phase
        arguments = {
            "feature_name": "test-feature",
            "action": "complete",
            "phase": "requirements",
        }
        result = await workflow_tools.handle_transition_phase(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check completion response
        assert "Complete requirements phase" in content
        assert "**New Status**: review" in content
        assert "ready for review" in content

    @pytest.mark.asyncio
    async def test_transition_phase_approve_requirements(self, workflow_tools):
        """Test approving requirements phase."""
        # Create, start, and complete workflow
        await workflow_tools.handle_create_workflow({"feature_name": "test-feature"})
        await workflow_tools.handle_transition_phase(
            {"feature_name": "test-feature", "action": "start", "phase": "requirements"}
        )
        await workflow_tools.handle_transition_phase(
            {
                "feature_name": "test-feature",
                "action": "complete",
                "phase": "requirements",
            }
        )

        # Approve requirements phase
        arguments = {
            "feature_name": "test-feature",
            "action": "approve",
            "phase": "requirements",
        }
        result = await workflow_tools.handle_transition_phase(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check approval response
        assert "Approve requirements phase" in content
        assert "**Current Phase**: design" in content
        assert "Ready to start" in content

    @pytest.mark.asyncio
    async def test_transition_phase_invalid_action(self, workflow_tools):
        """Test transition with invalid action."""
        await workflow_tools.handle_create_workflow({"feature_name": "test-feature"})

        arguments = {"feature_name": "test-feature", "action": "invalid_action"}
        result = await workflow_tools.handle_transition_phase(arguments)

        assert len(result) == 1
        assert "Invalid action" in result[0].text

    @pytest.mark.asyncio
    async def test_transition_phase_invalid_sequence(self, workflow_tools):
        """Test invalid phase transition sequence."""
        await workflow_tools.handle_create_workflow({"feature_name": "test-feature"})

        # Try to start design without completing requirements
        arguments = {
            "feature_name": "test-feature",
            "action": "start",
            "phase": "design",
        }
        result = await workflow_tools.handle_transition_phase(arguments)

        assert len(result) == 1
        assert "Invalid phase transition:" in result[0].text

    @pytest.mark.asyncio
    async def test_navigate_backward_to_requirements(self, workflow_tools):
        """Test navigating backward to requirements phase."""
        # Create workflow and progress to design
        await workflow_tools.handle_create_workflow({"feature_name": "test-feature"})
        await workflow_tools.handle_transition_phase(
            {"feature_name": "test-feature", "action": "start", "phase": "requirements"}
        )
        await workflow_tools.handle_transition_phase(
            {
                "feature_name": "test-feature",
                "action": "complete",
                "phase": "requirements",
            }
        )
        await workflow_tools.handle_transition_phase(
            {
                "feature_name": "test-feature",
                "action": "approve",
                "phase": "requirements",
            }
        )

        # Navigate backward to requirements
        arguments = {"feature_name": "test-feature", "target_phase": "requirements"}
        result = await workflow_tools.handle_navigate_backward(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check backward navigation response
        assert "Backward Navigation: test-feature" in content
        assert "**Target Phase**: requirements" in content
        assert "**Current Phase**: requirements" in content
        assert "in_progress" in content

    @pytest.mark.asyncio
    async def test_navigate_backward_invalid(self, workflow_tools):
        """Test invalid backward navigation."""
        await workflow_tools.handle_create_workflow({"feature_name": "test-feature"})

        # Try to navigate backward to design from requirements (invalid)
        arguments = {"feature_name": "test-feature", "target_phase": "design"}
        result = await workflow_tools.handle_navigate_backward(arguments)

        assert len(result) == 1
        assert "Cannot navigate backward" in result[0].text

    @pytest.mark.asyncio
    async def test_check_transition_requirements_design(self, workflow_tools):
        """Test checking transition requirements for design phase."""
        await workflow_tools.handle_create_workflow({"feature_name": "test-feature"})

        arguments = {"feature_name": "test-feature", "target_phase": "design"}
        result = await workflow_tools.handle_check_transition_requirements(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check transition requirements response
        assert "Transition Requirements Check: test-feature" in content
        assert "Target Phase: design" in content
        assert "**Can Transition**: No" in content
        assert "Requirements phase must be approved" in content

    @pytest.mark.asyncio
    async def test_check_transition_requirements_after_approval(self, workflow_tools):
        """Test checking transition requirements after approval."""
        # Create and approve requirements
        await workflow_tools.handle_create_workflow({"feature_name": "test-feature"})
        await workflow_tools.handle_transition_phase(
            {"feature_name": "test-feature", "action": "start", "phase": "requirements"}
        )
        await workflow_tools.handle_transition_phase(
            {
                "feature_name": "test-feature",
                "action": "complete",
                "phase": "requirements",
            }
        )
        await workflow_tools.handle_transition_phase(
            {
                "feature_name": "test-feature",
                "action": "approve",
                "phase": "requirements",
            }
        )

        arguments = {"feature_name": "test-feature", "target_phase": "design"}
        result = await workflow_tools.handle_check_transition_requirements(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check that transition is now allowed
        assert "**Can Transition**: Yes" in content
        assert "✅ Requirements approved" in content

    @pytest.mark.asyncio
    async def test_get_approval_guidance_not_started(self, workflow_tools):
        """Test getting approval guidance for not started phase."""
        await workflow_tools.handle_create_workflow({"feature_name": "test-feature"})

        arguments = {"feature_name": "test-feature"}
        result = await workflow_tools.handle_get_approval_guidance(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check approval guidance
        assert "Approval Guidance: test-feature" in content
        assert "Current Phase: requirements" in content
        assert "Phase Not Started" in content
        assert "Start working on the phase first" in content

    @pytest.mark.asyncio
    async def test_get_approval_guidance_ready_for_approval(self, workflow_tools):
        """Test getting approval guidance when ready for approval."""
        # Create, start, and complete requirements
        await workflow_tools.handle_create_workflow({"feature_name": "test-feature"})
        await workflow_tools.handle_transition_phase(
            {"feature_name": "test-feature", "action": "start", "phase": "requirements"}
        )
        await workflow_tools.handle_transition_phase(
            {
                "feature_name": "test-feature",
                "action": "complete",
                "phase": "requirements",
            }
        )

        arguments = {"feature_name": "test-feature"}
        result = await workflow_tools.handle_get_approval_guidance(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check approval guidance for review phase
        assert "Ready for Approval" in content
        assert "Do the requirements look good?" in content
        assert "What Counts as Approval" in content
        assert "What Doesn't Count as Approval" in content

    @pytest.mark.asyncio
    async def test_full_workflow_cycle(self, workflow_tools):
        """Test complete workflow cycle through all phases."""
        feature_name = "full-cycle-test"

        # Create workflow
        await workflow_tools.handle_create_workflow({"feature_name": feature_name})

        # Requirements phase
        await workflow_tools.handle_transition_phase(
            {"feature_name": feature_name, "action": "start", "phase": "requirements"}
        )
        await workflow_tools.handle_transition_phase(
            {
                "feature_name": feature_name,
                "action": "complete",
                "phase": "requirements",
            }
        )
        await workflow_tools.handle_transition_phase(
            {"feature_name": feature_name, "action": "approve", "phase": "requirements"}
        )

        # Design phase
        await workflow_tools.handle_transition_phase(
            {"feature_name": feature_name, "action": "start", "phase": "design"}
        )
        await workflow_tools.handle_transition_phase(
            {"feature_name": feature_name, "action": "complete", "phase": "design"}
        )
        await workflow_tools.handle_transition_phase(
            {"feature_name": feature_name, "action": "approve", "phase": "design"}
        )

        # Tasks phase
        await workflow_tools.handle_transition_phase(
            {"feature_name": feature_name, "action": "start", "phase": "tasks"}
        )
        await workflow_tools.handle_transition_phase(
            {"feature_name": feature_name, "action": "complete", "phase": "tasks"}
        )
        await workflow_tools.handle_transition_phase(
            {"feature_name": feature_name, "action": "approve", "phase": "tasks"}
        )

        # Check final status
        result = await workflow_tools.handle_get_workflow_status(
            {"feature_name": feature_name}
        )
        content = result[0].text

        assert "**Completion**: 100.0%" in content
        assert "**Workflow Complete**: Yes" in content
        assert "**Requirements**: ✅ Approved" in content
        assert "**Design**: ✅ Approved" in content
        assert "**Tasks**: ✅ Approved" in content

    def test_tool_definitions(self, workflow_tools):
        """Test that tool definitions are properly structured."""
        tools = workflow_tools.get_tool_definitions()

        assert len(tools) == 6

        tool_names = [tool.name for tool in tools]
        expected_names = [
            "create_workflow",
            "get_workflow_status",
            "transition_phase",
            "navigate_backward",
            "check_transition_requirements",
            "get_approval_guidance",
        ]

        for name in expected_names:
            assert name in tool_names

        # Check that all tools have required properties
        for tool in tools:
            assert tool.name
            assert tool.description
            assert tool.inputSchema
            assert "type" in tool.inputSchema
            assert "properties" in tool.inputSchema
            assert "required" in tool.inputSchema

    @pytest.mark.asyncio
    async def test_handle_unknown_tool(self, workflow_tools):
        """Test handling unknown tool call."""
        result = await workflow_tools.handle_tool_call("unknown_tool", {})

        assert len(result) == 1
        assert "Unknown tool" in result[0].text
