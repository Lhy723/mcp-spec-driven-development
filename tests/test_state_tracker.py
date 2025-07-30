"""Tests for state tracking system."""

from datetime import datetime

import pytest

from src.mcp_spec_driven_development.workflow.models import (
    PhaseStatus,
    PhaseType,
    WorkflowState,
)
from src.mcp_spec_driven_development.workflow.state_tracker import StateTracker


class TestStateTracker:
    """Test cases for StateTracker."""

    def setup_method(self):
        """Set up test fixtures."""
        self.state_tracker = StateTracker()
        self.feature_name = "test-feature"
        self.workflow_state = WorkflowState(
            feature_name=self.feature_name,
            current_phase=PhaseType.REQUIREMENTS,
            phase_status={
                PhaseType.REQUIREMENTS: PhaseStatus.NOT_STARTED,
                PhaseType.DESIGN: PhaseStatus.NOT_STARTED,
                PhaseType.TASKS: PhaseStatus.NOT_STARTED,
            },
            can_proceed=False,
            requires_approval=True,
            last_updated=datetime.now(),
        )

    def test_track_workflow(self):
        """Test tracking a workflow state."""
        self.state_tracker.track_workflow(self.workflow_state)

        current_phase = self.state_tracker.get_current_phase(self.feature_name)
        assert current_phase == PhaseType.REQUIREMENTS

    def test_get_current_phase_existing(self):
        """Test getting current phase for existing workflow."""
        self.state_tracker.track_workflow(self.workflow_state)

        current_phase = self.state_tracker.get_current_phase(self.feature_name)
        assert current_phase == PhaseType.REQUIREMENTS

    def test_get_current_phase_nonexistent(self):
        """Test getting current phase for non-existent workflow."""
        current_phase = self.state_tracker.get_current_phase("nonexistent")
        assert current_phase is None

    def test_get_phase_status_existing(self):
        """Test getting phase status for existing workflow."""
        self.state_tracker.track_workflow(self.workflow_state)

        status = self.state_tracker.get_phase_status(
            self.feature_name, PhaseType.REQUIREMENTS
        )
        assert status == PhaseStatus.NOT_STARTED

    def test_get_phase_status_nonexistent(self):
        """Test getting phase status for non-existent workflow."""
        status = self.state_tracker.get_phase_status(
            "nonexistent", PhaseType.REQUIREMENTS
        )
        assert status is None

    def test_get_all_phase_statuses(self):
        """Test getting all phase statuses."""
        self.state_tracker.track_workflow(self.workflow_state)

        statuses = self.state_tracker.get_all_phase_statuses(self.feature_name)
        assert statuses == {
            PhaseType.REQUIREMENTS: PhaseStatus.NOT_STARTED,
            PhaseType.DESIGN: PhaseStatus.NOT_STARTED,
            PhaseType.TASKS: PhaseStatus.NOT_STARTED,
        }

    def test_get_all_phase_statuses_nonexistent(self):
        """Test getting all phase statuses for non-existent workflow."""
        statuses = self.state_tracker.get_all_phase_statuses("nonexistent")
        assert statuses is None

    def test_is_phase_complete_approved(self):
        """Test checking if phase is complete when approved."""
        self.workflow_state.phase_status[PhaseType.REQUIREMENTS] = PhaseStatus.APPROVED
        self.state_tracker.track_workflow(self.workflow_state)

        assert self.state_tracker.is_phase_complete(
            self.feature_name, PhaseType.REQUIREMENTS
        )

    def test_is_phase_complete_not_approved(self):
        """Test checking if phase is complete when not approved."""
        self.state_tracker.track_workflow(self.workflow_state)

        assert not self.state_tracker.is_phase_complete(
            self.feature_name, PhaseType.REQUIREMENTS
        )

    def test_is_phase_complete_nonexistent(self):
        """Test checking if phase is complete for non-existent workflow."""
        assert not self.state_tracker.is_phase_complete(
            "nonexistent", PhaseType.REQUIREMENTS
        )

    def test_get_completion_percentage_none_complete(self):
        """Test completion percentage when no phases complete."""
        self.state_tracker.track_workflow(self.workflow_state)

        percentage = self.state_tracker.get_completion_percentage(self.feature_name)
        assert percentage == 0.0

    def test_get_completion_percentage_partial_complete(self):
        """Test completion percentage when some phases complete."""
        self.workflow_state.phase_status[PhaseType.REQUIREMENTS] = PhaseStatus.APPROVED
        self.state_tracker.track_workflow(self.workflow_state)

        percentage = self.state_tracker.get_completion_percentage(self.feature_name)
        assert percentage == 1.0 / 3.0  # 1 out of 3 phases

    def test_get_completion_percentage_all_complete(self):
        """Test completion percentage when all phases complete."""
        self.workflow_state.phase_status[PhaseType.REQUIREMENTS] = PhaseStatus.APPROVED
        self.workflow_state.phase_status[PhaseType.DESIGN] = PhaseStatus.APPROVED
        self.workflow_state.phase_status[PhaseType.TASKS] = PhaseStatus.APPROVED
        self.state_tracker.track_workflow(self.workflow_state)

        percentage = self.state_tracker.get_completion_percentage(self.feature_name)
        assert percentage == 1.0

    def test_get_completion_percentage_nonexistent(self):
        """Test completion percentage for non-existent workflow."""
        percentage = self.state_tracker.get_completion_percentage("nonexistent")
        assert percentage == 0.0

    def test_requires_user_approval_true(self):
        """Test checking if user approval required when true."""
        self.state_tracker.track_workflow(self.workflow_state)

        assert self.state_tracker.requires_user_approval(self.feature_name)

    def test_requires_user_approval_false(self):
        """Test checking if user approval required when false."""
        self.workflow_state.requires_approval = False
        self.state_tracker.track_workflow(self.workflow_state)

        assert not self.state_tracker.requires_user_approval(self.feature_name)

    def test_requires_user_approval_nonexistent(self):
        """Test checking if user approval required for non-existent workflow."""
        assert not self.state_tracker.requires_user_approval("nonexistent")

    def test_can_proceed_to_next_phase_true(self):
        """Test checking if can proceed when true."""
        self.workflow_state.can_proceed = True
        self.state_tracker.track_workflow(self.workflow_state)

        assert self.state_tracker.can_proceed_to_next_phase(self.feature_name)

    def test_can_proceed_to_next_phase_false(self):
        """Test checking if can proceed when false."""
        self.state_tracker.track_workflow(self.workflow_state)

        assert not self.state_tracker.can_proceed_to_next_phase(self.feature_name)

    def test_can_proceed_to_next_phase_nonexistent(self):
        """Test checking if can proceed for non-existent workflow."""
        assert not self.state_tracker.can_proceed_to_next_phase("nonexistent")

    def test_record_approval(self):
        """Test recording approval."""
        self.state_tracker.track_workflow(self.workflow_state)
        self.state_tracker.record_approval(
            self.feature_name, PhaseType.REQUIREMENTS, True
        )

        history = self.state_tracker.get_approval_history(self.feature_name)
        assert len(history) == 1
        assert history[0][0] == PhaseType.REQUIREMENTS
        assert history[0][2] is True

    def test_record_approval_new_workflow(self):
        """Test recording approval for new workflow."""
        self.state_tracker.record_approval(
            self.feature_name, PhaseType.REQUIREMENTS, True
        )

        history = self.state_tracker.get_approval_history(self.feature_name)
        assert len(history) == 1

    def test_get_approval_history_empty(self):
        """Test getting approval history when empty."""
        history = self.state_tracker.get_approval_history("nonexistent")
        assert history == []

    def test_get_approval_history_multiple(self):
        """Test getting approval history with multiple entries."""
        self.state_tracker.track_workflow(self.workflow_state)
        self.state_tracker.record_approval(
            self.feature_name, PhaseType.REQUIREMENTS, False
        )
        self.state_tracker.record_approval(
            self.feature_name, PhaseType.REQUIREMENTS, True
        )

        history = self.state_tracker.get_approval_history(self.feature_name)
        assert len(history) == 2
        assert history[0][2] is False
        assert history[1][2] is True

    def test_get_last_approval_existing(self):
        """Test getting last approval for existing phase."""
        self.state_tracker.track_workflow(self.workflow_state)
        self.state_tracker.record_approval(
            self.feature_name, PhaseType.REQUIREMENTS, False
        )
        self.state_tracker.record_approval(
            self.feature_name, PhaseType.REQUIREMENTS, True
        )

        last_approval = self.state_tracker.get_last_approval(
            self.feature_name, PhaseType.REQUIREMENTS
        )
        assert last_approval is not None
        assert last_approval[1] is True

    def test_get_last_approval_nonexistent(self):
        """Test getting last approval for non-existent phase."""
        self.state_tracker.track_workflow(self.workflow_state)

        last_approval = self.state_tracker.get_last_approval(
            self.feature_name, PhaseType.REQUIREMENTS
        )
        assert last_approval is None

    def test_can_navigate_backward_to_requirements(self):
        """Test backward navigation to requirements (always allowed)."""
        self.workflow_state.current_phase = PhaseType.DESIGN
        self.state_tracker.track_workflow(self.workflow_state)

        assert self.state_tracker.can_navigate_backward(
            self.feature_name, PhaseType.REQUIREMENTS
        )

    def test_can_navigate_backward_to_design_from_tasks(self):
        """Test backward navigation to design from tasks."""
        self.workflow_state.current_phase = PhaseType.TASKS
        self.state_tracker.track_workflow(self.workflow_state)

        assert self.state_tracker.can_navigate_backward(
            self.feature_name, PhaseType.DESIGN
        )

    def test_can_navigate_backward_to_design_from_requirements(self):
        """Test backward navigation to design from requirements (not allowed)."""
        self.workflow_state.current_phase = PhaseType.REQUIREMENTS
        self.state_tracker.track_workflow(self.workflow_state)

        assert not self.state_tracker.can_navigate_backward(
            self.feature_name, PhaseType.DESIGN
        )

    def test_can_navigate_backward_nonexistent(self):
        """Test backward navigation for non-existent workflow."""
        assert not self.state_tracker.can_navigate_backward(
            "nonexistent", PhaseType.REQUIREMENTS
        )

    def test_navigate_backward_to_requirements(self):
        """Test navigating backward to requirements."""
        self.workflow_state.current_phase = PhaseType.DESIGN
        self.workflow_state.phase_status[PhaseType.REQUIREMENTS] = PhaseStatus.APPROVED
        self.workflow_state.phase_status[PhaseType.DESIGN] = PhaseStatus.IN_PROGRESS
        self.state_tracker.track_workflow(self.workflow_state)

        success = self.state_tracker.navigate_backward(
            self.feature_name, PhaseType.REQUIREMENTS
        )
        assert success

        workflow = self.state_tracker._workflows[self.feature_name]
        assert workflow.current_phase == PhaseType.REQUIREMENTS
        assert workflow.phase_status[PhaseType.REQUIREMENTS] == PhaseStatus.IN_PROGRESS
        assert workflow.phase_status[PhaseType.DESIGN] == PhaseStatus.NOT_STARTED
        assert workflow.phase_status[PhaseType.TASKS] == PhaseStatus.NOT_STARTED

    def test_navigate_backward_to_design(self):
        """Test navigating backward to design."""
        self.workflow_state.current_phase = PhaseType.TASKS
        self.workflow_state.phase_status[PhaseType.DESIGN] = PhaseStatus.APPROVED
        self.workflow_state.phase_status[PhaseType.TASKS] = PhaseStatus.IN_PROGRESS
        self.state_tracker.track_workflow(self.workflow_state)

        success = self.state_tracker.navigate_backward(
            self.feature_name, PhaseType.DESIGN
        )
        assert success

        workflow = self.state_tracker._workflows[self.feature_name]
        assert workflow.current_phase == PhaseType.DESIGN
        assert workflow.phase_status[PhaseType.DESIGN] == PhaseStatus.IN_PROGRESS
        assert workflow.phase_status[PhaseType.TASKS] == PhaseStatus.NOT_STARTED

    def test_navigate_backward_not_allowed(self):
        """Test navigating backward when not allowed."""
        self.state_tracker.track_workflow(self.workflow_state)

        success = self.state_tracker.navigate_backward(
            self.feature_name, PhaseType.DESIGN
        )
        assert not success

    def test_get_next_phase_from_requirements(self):
        """Test getting next phase from requirements."""
        self.state_tracker.track_workflow(self.workflow_state)

        next_phase = self.state_tracker.get_next_phase(self.feature_name)
        assert next_phase == PhaseType.DESIGN

    def test_get_next_phase_from_design(self):
        """Test getting next phase from design."""
        self.workflow_state.current_phase = PhaseType.DESIGN
        self.state_tracker.track_workflow(self.workflow_state)

        next_phase = self.state_tracker.get_next_phase(self.feature_name)
        assert next_phase == PhaseType.TASKS

    def test_get_next_phase_from_tasks(self):
        """Test getting next phase from tasks (none)."""
        self.workflow_state.current_phase = PhaseType.TASKS
        self.state_tracker.track_workflow(self.workflow_state)

        next_phase = self.state_tracker.get_next_phase(self.feature_name)
        assert next_phase is None

    def test_get_next_phase_nonexistent(self):
        """Test getting next phase for non-existent workflow."""
        next_phase = self.state_tracker.get_next_phase("nonexistent")
        assert next_phase is None

    def test_get_previous_phase_from_design(self):
        """Test getting previous phase from design."""
        self.workflow_state.current_phase = PhaseType.DESIGN
        self.state_tracker.track_workflow(self.workflow_state)

        previous_phase = self.state_tracker.get_previous_phase(self.feature_name)
        assert previous_phase == PhaseType.REQUIREMENTS

    def test_get_previous_phase_from_tasks(self):
        """Test getting previous phase from tasks."""
        self.workflow_state.current_phase = PhaseType.TASKS
        self.state_tracker.track_workflow(self.workflow_state)

        previous_phase = self.state_tracker.get_previous_phase(self.feature_name)
        assert previous_phase == PhaseType.DESIGN

    def test_get_previous_phase_from_requirements(self):
        """Test getting previous phase from requirements (none)."""
        self.state_tracker.track_workflow(self.workflow_state)

        previous_phase = self.state_tracker.get_previous_phase(self.feature_name)
        assert previous_phase is None

    def test_is_workflow_complete_false(self):
        """Test checking if workflow is complete when not all approved."""
        self.workflow_state.phase_status[PhaseType.REQUIREMENTS] = PhaseStatus.APPROVED
        self.state_tracker.track_workflow(self.workflow_state)

        assert not self.state_tracker.is_workflow_complete(self.feature_name)

    def test_is_workflow_complete_true(self):
        """Test checking if workflow is complete when all approved."""
        self.workflow_state.phase_status[PhaseType.REQUIREMENTS] = PhaseStatus.APPROVED
        self.workflow_state.phase_status[PhaseType.DESIGN] = PhaseStatus.APPROVED
        self.workflow_state.phase_status[PhaseType.TASKS] = PhaseStatus.APPROVED
        self.state_tracker.track_workflow(self.workflow_state)

        assert self.state_tracker.is_workflow_complete(self.feature_name)

    def test_is_workflow_complete_nonexistent(self):
        """Test checking if workflow is complete for non-existent workflow."""
        assert not self.state_tracker.is_workflow_complete("nonexistent")

    def test_get_workflow_summary(self):
        """Test getting workflow summary."""
        self.state_tracker.track_workflow(self.workflow_state)

        summary = self.state_tracker.get_workflow_summary(self.feature_name)
        assert summary is not None
        assert summary["feature_name"] == self.feature_name
        assert summary["current_phase"] == "requirements"
        assert summary["completion_percentage"] == 0.0
        assert not summary["can_proceed"]
        assert summary["requires_approval"]
        assert not summary["is_complete"]
        assert summary["next_phase"] == "design"
        assert summary["previous_phase"] is None

    def test_get_workflow_summary_nonexistent(self):
        """Test getting workflow summary for non-existent workflow."""
        summary = self.state_tracker.get_workflow_summary("nonexistent")
        assert summary is None

    def test_update_workflow_state(self):
        """Test updating workflow state."""
        self.state_tracker.track_workflow(self.workflow_state)

        # Update the workflow state
        self.workflow_state.current_phase = PhaseType.DESIGN
        self.state_tracker.update_workflow_state(self.workflow_state)

        current_phase = self.state_tracker.get_current_phase(self.feature_name)
        assert current_phase == PhaseType.DESIGN

    def test_remove_workflow_existing(self):
        """Test removing existing workflow."""
        self.state_tracker.track_workflow(self.workflow_state)
        self.state_tracker.record_approval(
            self.feature_name, PhaseType.REQUIREMENTS, True
        )

        success = self.state_tracker.remove_workflow(self.feature_name)
        assert success

        # Verify workflow and history are removed
        assert self.state_tracker.get_current_phase(self.feature_name) is None
        assert self.state_tracker.get_approval_history(self.feature_name) == []

    def test_remove_workflow_nonexistent(self):
        """Test removing non-existent workflow."""
        success = self.state_tracker.remove_workflow("nonexistent")
        assert not success

    def test_list_tracked_workflows_empty(self):
        """Test listing tracked workflows when empty."""
        workflows = self.state_tracker.list_tracked_workflows()
        assert workflows == []

    def test_list_tracked_workflows_multiple(self):
        """Test listing tracked workflows with multiple entries."""
        workflow1 = self.workflow_state
        workflow2 = WorkflowState(
            feature_name="feature2",
            current_phase=PhaseType.DESIGN,
            phase_status={
                PhaseType.REQUIREMENTS: PhaseStatus.APPROVED,
                PhaseType.DESIGN: PhaseStatus.IN_PROGRESS,
                PhaseType.TASKS: PhaseStatus.NOT_STARTED,
            },
            can_proceed=False,
            requires_approval=True,
            last_updated=datetime.now(),
        )

        self.state_tracker.track_workflow(workflow1)
        self.state_tracker.track_workflow(workflow2)

        workflows = self.state_tracker.list_tracked_workflows()
        assert set(workflows) == {self.feature_name, "feature2"}
