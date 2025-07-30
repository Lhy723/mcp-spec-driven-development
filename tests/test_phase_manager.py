"""Tests for phase management system."""

from datetime import datetime

import pytest

from src.mcp_spec_driven_development.workflow.models import PhaseStatus, PhaseType
from src.mcp_spec_driven_development.workflow.phase_manager import PhaseManager


class TestPhaseManager:
    """Test cases for PhaseManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.phase_manager = PhaseManager()
        self.feature_name = "test-feature"

    def test_create_workflow(self):
        """Test creating a new workflow."""
        workflow = self.phase_manager.create_workflow(self.feature_name)

        assert workflow.feature_name == self.feature_name
        assert workflow.current_phase == PhaseType.REQUIREMENTS
        assert workflow.phase_status[PhaseType.REQUIREMENTS] == PhaseStatus.NOT_STARTED
        assert workflow.phase_status[PhaseType.DESIGN] == PhaseStatus.NOT_STARTED
        assert workflow.phase_status[PhaseType.TASKS] == PhaseStatus.NOT_STARTED
        assert not workflow.can_proceed
        assert workflow.requires_approval
        assert isinstance(workflow.last_updated, datetime)

    def test_get_workflow_existing(self):
        """Test getting an existing workflow."""
        created_workflow = self.phase_manager.create_workflow(self.feature_name)
        retrieved_workflow = self.phase_manager.get_workflow(self.feature_name)

        assert retrieved_workflow == created_workflow

    def test_get_workflow_nonexistent(self):
        """Test getting a non-existent workflow."""
        workflow = self.phase_manager.get_workflow("nonexistent")
        assert workflow is None

    def test_start_requirements_phase(self):
        """Test starting the requirements phase."""
        self.phase_manager.create_workflow(self.feature_name)
        workflow = self.phase_manager.start_requirements_phase(self.feature_name)

        assert workflow.current_phase == PhaseType.REQUIREMENTS
        assert workflow.phase_status[PhaseType.REQUIREMENTS] == PhaseStatus.IN_PROGRESS
        assert not workflow.can_proceed
        assert workflow.requires_approval

    def test_start_requirements_phase_nonexistent_workflow(self):
        """Test starting requirements phase for non-existent workflow."""
        with pytest.raises(ValueError, match="No workflow found"):
            self.phase_manager.start_requirements_phase("nonexistent")

    def test_start_requirements_phase_wrong_current_phase(self):
        """Test starting requirements phase from wrong current phase."""
        workflow = self.phase_manager.create_workflow(self.feature_name)
        workflow.current_phase = PhaseType.DESIGN

        with pytest.raises(ValueError, match="Cannot start requirements phase"):
            self.phase_manager.start_requirements_phase(self.feature_name)

    def test_complete_requirements_phase(self):
        """Test completing the requirements phase."""
        self.phase_manager.create_workflow(self.feature_name)
        self.phase_manager.start_requirements_phase(self.feature_name)
        workflow = self.phase_manager.complete_requirements_phase(self.feature_name)

        assert workflow.phase_status[PhaseType.REQUIREMENTS] == PhaseStatus.REVIEW
        assert not workflow.can_proceed
        assert workflow.requires_approval

    def test_complete_requirements_phase_not_in_progress(self):
        """Test completing requirements phase when not in progress."""
        self.phase_manager.create_workflow(self.feature_name)

        with pytest.raises(ValueError, match="Requirements phase is not in progress"):
            self.phase_manager.complete_requirements_phase(self.feature_name)

    def test_approve_requirements_phase(self):
        """Test approving the requirements phase."""
        self.phase_manager.create_workflow(self.feature_name)
        self.phase_manager.start_requirements_phase(self.feature_name)
        self.phase_manager.complete_requirements_phase(self.feature_name)
        workflow = self.phase_manager.approve_requirements_phase(self.feature_name)

        assert workflow.phase_status[PhaseType.REQUIREMENTS] == PhaseStatus.APPROVED
        assert workflow.current_phase == PhaseType.DESIGN
        assert workflow.can_proceed
        assert not workflow.requires_approval

    def test_approve_requirements_phase_not_in_review(self):
        """Test approving requirements phase when not in review."""
        self.phase_manager.create_workflow(self.feature_name)
        self.phase_manager.start_requirements_phase(self.feature_name)

        with pytest.raises(
            ValueError, match="Requirements phase is not ready for approval"
        ):
            self.phase_manager.approve_requirements_phase(self.feature_name)

    def test_start_design_phase(self):
        """Test starting the design phase."""
        self.phase_manager.create_workflow(self.feature_name)
        self.phase_manager.start_requirements_phase(self.feature_name)
        self.phase_manager.complete_requirements_phase(self.feature_name)
        self.phase_manager.approve_requirements_phase(self.feature_name)
        workflow = self.phase_manager.start_design_phase(self.feature_name)

        assert workflow.current_phase == PhaseType.DESIGN
        assert workflow.phase_status[PhaseType.DESIGN] == PhaseStatus.IN_PROGRESS
        assert not workflow.can_proceed
        assert workflow.requires_approval

    def test_start_design_phase_requirements_not_approved(self):
        """Test starting design phase when requirements not approved."""
        self.phase_manager.create_workflow(self.feature_name)
        workflow = self.phase_manager.get_workflow(self.feature_name)
        workflow.current_phase = PhaseType.DESIGN

        with pytest.raises(ValueError, match="Requirements phase must be approved"):
            self.phase_manager.start_design_phase(self.feature_name)

    def test_complete_design_phase(self):
        """Test completing the design phase."""
        # Set up workflow through requirements
        self.phase_manager.create_workflow(self.feature_name)
        self.phase_manager.start_requirements_phase(self.feature_name)
        self.phase_manager.complete_requirements_phase(self.feature_name)
        self.phase_manager.approve_requirements_phase(self.feature_name)
        self.phase_manager.start_design_phase(self.feature_name)

        workflow = self.phase_manager.complete_design_phase(self.feature_name)

        assert workflow.phase_status[PhaseType.DESIGN] == PhaseStatus.REVIEW
        assert not workflow.can_proceed
        assert workflow.requires_approval

    def test_approve_design_phase(self):
        """Test approving the design phase."""
        # Set up workflow through design
        self.phase_manager.create_workflow(self.feature_name)
        self.phase_manager.start_requirements_phase(self.feature_name)
        self.phase_manager.complete_requirements_phase(self.feature_name)
        self.phase_manager.approve_requirements_phase(self.feature_name)
        self.phase_manager.start_design_phase(self.feature_name)
        self.phase_manager.complete_design_phase(self.feature_name)

        workflow = self.phase_manager.approve_design_phase(self.feature_name)

        assert workflow.phase_status[PhaseType.DESIGN] == PhaseStatus.APPROVED
        assert workflow.current_phase == PhaseType.TASKS
        assert workflow.can_proceed
        assert not workflow.requires_approval

    def test_start_tasks_phase(self):
        """Test starting the tasks phase."""
        # Set up workflow through design
        self.phase_manager.create_workflow(self.feature_name)
        self.phase_manager.start_requirements_phase(self.feature_name)
        self.phase_manager.complete_requirements_phase(self.feature_name)
        self.phase_manager.approve_requirements_phase(self.feature_name)
        self.phase_manager.start_design_phase(self.feature_name)
        self.phase_manager.complete_design_phase(self.feature_name)
        self.phase_manager.approve_design_phase(self.feature_name)

        workflow = self.phase_manager.start_tasks_phase(self.feature_name)

        assert workflow.current_phase == PhaseType.TASKS
        assert workflow.phase_status[PhaseType.TASKS] == PhaseStatus.IN_PROGRESS
        assert not workflow.can_proceed
        assert workflow.requires_approval

    def test_start_tasks_phase_design_not_approved(self):
        """Test starting tasks phase when design not approved."""
        self.phase_manager.create_workflow(self.feature_name)
        workflow = self.phase_manager.get_workflow(self.feature_name)
        workflow.current_phase = PhaseType.TASKS

        with pytest.raises(ValueError, match="Design phase must be approved"):
            self.phase_manager.start_tasks_phase(self.feature_name)

    def test_complete_tasks_phase(self):
        """Test completing the tasks phase."""
        # Set up workflow through tasks
        self.phase_manager.create_workflow(self.feature_name)
        self.phase_manager.start_requirements_phase(self.feature_name)
        self.phase_manager.complete_requirements_phase(self.feature_name)
        self.phase_manager.approve_requirements_phase(self.feature_name)
        self.phase_manager.start_design_phase(self.feature_name)
        self.phase_manager.complete_design_phase(self.feature_name)
        self.phase_manager.approve_design_phase(self.feature_name)
        self.phase_manager.start_tasks_phase(self.feature_name)

        workflow = self.phase_manager.complete_tasks_phase(self.feature_name)

        assert workflow.phase_status[PhaseType.TASKS] == PhaseStatus.REVIEW
        assert not workflow.can_proceed
        assert workflow.requires_approval

    def test_approve_tasks_phase(self):
        """Test approving the tasks phase."""
        # Set up workflow through tasks
        self.phase_manager.create_workflow(self.feature_name)
        self.phase_manager.start_requirements_phase(self.feature_name)
        self.phase_manager.complete_requirements_phase(self.feature_name)
        self.phase_manager.approve_requirements_phase(self.feature_name)
        self.phase_manager.start_design_phase(self.feature_name)
        self.phase_manager.complete_design_phase(self.feature_name)
        self.phase_manager.approve_design_phase(self.feature_name)
        self.phase_manager.start_tasks_phase(self.feature_name)
        self.phase_manager.complete_tasks_phase(self.feature_name)

        workflow = self.phase_manager.approve_tasks_phase(self.feature_name)

        assert workflow.phase_status[PhaseType.TASKS] == PhaseStatus.APPROVED
        assert not workflow.can_proceed
        assert not workflow.requires_approval

    def test_can_transition_to_phase_requirements(self):
        """Test transition to requirements phase (always allowed)."""
        self.phase_manager.create_workflow(self.feature_name)

        assert self.phase_manager.can_transition_to_phase(
            self.feature_name, PhaseType.REQUIREMENTS
        )

    def test_can_transition_to_phase_design_requirements_approved(self):
        """Test transition to design phase when requirements approved."""
        self.phase_manager.create_workflow(self.feature_name)
        workflow = self.phase_manager.get_workflow(self.feature_name)
        workflow.phase_status[PhaseType.REQUIREMENTS] = PhaseStatus.APPROVED

        assert self.phase_manager.can_transition_to_phase(
            self.feature_name, PhaseType.DESIGN
        )

    def test_can_transition_to_phase_design_requirements_not_approved(self):
        """Test transition to design phase when requirements not approved."""
        self.phase_manager.create_workflow(self.feature_name)

        assert not self.phase_manager.can_transition_to_phase(
            self.feature_name, PhaseType.DESIGN
        )

    def test_can_transition_to_phase_tasks_both_approved(self):
        """Test transition to tasks phase when both requirements and design approved."""
        self.phase_manager.create_workflow(self.feature_name)
        workflow = self.phase_manager.get_workflow(self.feature_name)
        workflow.phase_status[PhaseType.REQUIREMENTS] = PhaseStatus.APPROVED
        workflow.phase_status[PhaseType.DESIGN] = PhaseStatus.APPROVED

        assert self.phase_manager.can_transition_to_phase(
            self.feature_name, PhaseType.TASKS
        )

    def test_can_transition_to_phase_tasks_not_all_approved(self):
        """Test transition to tasks phase when not all previous phases approved."""
        self.phase_manager.create_workflow(self.feature_name)
        workflow = self.phase_manager.get_workflow(self.feature_name)
        workflow.phase_status[PhaseType.REQUIREMENTS] = PhaseStatus.APPROVED
        # Design not approved

        assert not self.phase_manager.can_transition_to_phase(
            self.feature_name, PhaseType.TASKS
        )

    def test_can_transition_to_phase_nonexistent_workflow(self):
        """Test transition check for non-existent workflow."""
        assert not self.phase_manager.can_transition_to_phase(
            "nonexistent", PhaseType.REQUIREMENTS
        )
