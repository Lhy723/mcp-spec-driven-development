"""Phase management system for spec-driven development workflow."""

from datetime import datetime
from typing import Dict, Optional

from .models import PhaseStatus, PhaseType, WorkflowState


class PhaseManager:
    """Manages the three-phase spec workflow orchestration."""

    def __init__(self):
        """Initialize the phase manager."""
        self._workflows: Dict[str, WorkflowState] = {}

    def create_workflow(self, feature_name: str) -> WorkflowState:
        """Create a new workflow for a feature.

        Args:
            feature_name: Name of the feature to create workflow for

        Returns:
            WorkflowState: Initial workflow state
        """
        workflow_state = WorkflowState(
            feature_name=feature_name,
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

        self._workflows[feature_name] = workflow_state
        return workflow_state

    def get_workflow(self, feature_name: str) -> Optional[WorkflowState]:
        """Get workflow state for a feature.

        Args:
            feature_name: Name of the feature

        Returns:
            WorkflowState or None if not found
        """
        return self._workflows.get(feature_name)

    def start_requirements_phase(self, feature_name: str) -> WorkflowState:
        """Start the requirements phase for a feature.

        Args:
            feature_name: Name of the feature

        Returns:
            WorkflowState: Updated workflow state

        Raises:
            ValueError: If workflow doesn't exist or phase cannot be started
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            raise ValueError(f"No workflow found for feature: {feature_name}")

        if workflow.current_phase != PhaseType.REQUIREMENTS:
            raise ValueError(
                f"Cannot start requirements phase from {workflow.current_phase.value}"
            )

        workflow.phase_status[PhaseType.REQUIREMENTS] = PhaseStatus.IN_PROGRESS
        workflow.can_proceed = False
        workflow.requires_approval = True
        workflow.last_updated = datetime.now()

        return workflow

    def complete_requirements_phase(self, feature_name: str) -> WorkflowState:
        """Mark requirements phase as complete and ready for review.

        Args:
            feature_name: Name of the feature

        Returns:
            WorkflowState: Updated workflow state

        Raises:
            ValueError: If workflow doesn't exist or phase cannot be completed
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            raise ValueError(f"No workflow found for feature: {feature_name}")

        if workflow.current_phase != PhaseType.REQUIREMENTS:
            raise ValueError(
                f"Cannot complete requirements phase from {workflow.current_phase.value}"
            )

        if workflow.phase_status[PhaseType.REQUIREMENTS] != PhaseStatus.IN_PROGRESS:
            raise ValueError("Requirements phase is not in progress")

        workflow.phase_status[PhaseType.REQUIREMENTS] = PhaseStatus.REVIEW
        workflow.can_proceed = False
        workflow.requires_approval = True
        workflow.last_updated = datetime.now()

        return workflow

    def approve_requirements_phase(self, feature_name: str) -> WorkflowState:
        """Approve requirements phase and transition to design.

        Args:
            feature_name: Name of the feature

        Returns:
            WorkflowState: Updated workflow state

        Raises:
            ValueError: If workflow doesn't exist or phase cannot be approved
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            raise ValueError(f"No workflow found for feature: {feature_name}")

        if workflow.current_phase != PhaseType.REQUIREMENTS:
            raise ValueError(
                f"Cannot approve requirements phase from {workflow.current_phase.value}"
            )

        if workflow.phase_status[PhaseType.REQUIREMENTS] != PhaseStatus.REVIEW:
            raise ValueError("Requirements phase is not ready for approval")

        workflow.phase_status[PhaseType.REQUIREMENTS] = PhaseStatus.APPROVED
        workflow.current_phase = PhaseType.DESIGN
        workflow.can_proceed = True
        workflow.requires_approval = False
        workflow.last_updated = datetime.now()

        return workflow

    def start_design_phase(self, feature_name: str) -> WorkflowState:
        """Start the design phase for a feature.

        Args:
            feature_name: Name of the feature

        Returns:
            WorkflowState: Updated workflow state

        Raises:
            ValueError: If workflow doesn't exist or phase cannot be started
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            raise ValueError(f"No workflow found for feature: {feature_name}")

        if workflow.current_phase != PhaseType.DESIGN:
            raise ValueError(
                f"Cannot start design phase from {workflow.current_phase.value}"
            )

        if workflow.phase_status[PhaseType.REQUIREMENTS] != PhaseStatus.APPROVED:
            raise ValueError(
                "Requirements phase must be approved before starting design"
            )

        workflow.phase_status[PhaseType.DESIGN] = PhaseStatus.IN_PROGRESS
        workflow.can_proceed = False
        workflow.requires_approval = True
        workflow.last_updated = datetime.now()

        return workflow

    def complete_design_phase(self, feature_name: str) -> WorkflowState:
        """Mark design phase as complete and ready for review.

        Args:
            feature_name: Name of the feature

        Returns:
            WorkflowState: Updated workflow state

        Raises:
            ValueError: If workflow doesn't exist or phase cannot be completed
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            raise ValueError(f"No workflow found for feature: {feature_name}")

        if workflow.current_phase != PhaseType.DESIGN:
            raise ValueError(
                f"Cannot complete design phase from {workflow.current_phase.value}"
            )

        if workflow.phase_status[PhaseType.DESIGN] != PhaseStatus.IN_PROGRESS:
            raise ValueError("Design phase is not in progress")

        workflow.phase_status[PhaseType.DESIGN] = PhaseStatus.REVIEW
        workflow.can_proceed = False
        workflow.requires_approval = True
        workflow.last_updated = datetime.now()

        return workflow

    def approve_design_phase(self, feature_name: str) -> WorkflowState:
        """Approve design phase and transition to tasks.

        Args:
            feature_name: Name of the feature

        Returns:
            WorkflowState: Updated workflow state

        Raises:
            ValueError: If workflow doesn't exist or phase cannot be approved
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            raise ValueError(f"No workflow found for feature: {feature_name}")

        if workflow.current_phase != PhaseType.DESIGN:
            raise ValueError(
                f"Cannot approve design phase from {workflow.current_phase.value}"
            )

        if workflow.phase_status[PhaseType.DESIGN] != PhaseStatus.REVIEW:
            raise ValueError("Design phase is not ready for approval")

        workflow.phase_status[PhaseType.DESIGN] = PhaseStatus.APPROVED
        workflow.current_phase = PhaseType.TASKS
        workflow.can_proceed = True
        workflow.requires_approval = False
        workflow.last_updated = datetime.now()

        return workflow

    def start_tasks_phase(self, feature_name: str) -> WorkflowState:
        """Start the tasks phase for a feature.

        Args:
            feature_name: Name of the feature

        Returns:
            WorkflowState: Updated workflow state

        Raises:
            ValueError: If workflow doesn't exist or phase cannot be started
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            raise ValueError(f"No workflow found for feature: {feature_name}")

        if workflow.current_phase != PhaseType.TASKS:
            raise ValueError(
                f"Cannot start tasks phase from {workflow.current_phase.value}"
            )

        if workflow.phase_status[PhaseType.DESIGN] != PhaseStatus.APPROVED:
            raise ValueError("Design phase must be approved before starting tasks")

        workflow.phase_status[PhaseType.TASKS] = PhaseStatus.IN_PROGRESS
        workflow.can_proceed = False
        workflow.requires_approval = True
        workflow.last_updated = datetime.now()

        return workflow

    def complete_tasks_phase(self, feature_name: str) -> WorkflowState:
        """Mark tasks phase as complete and ready for review.

        Args:
            feature_name: Name of the feature

        Returns:
            WorkflowState: Updated workflow state

        Raises:
            ValueError: If workflow doesn't exist or phase cannot be completed
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            raise ValueError(f"No workflow found for feature: {feature_name}")

        if workflow.current_phase != PhaseType.TASKS:
            raise ValueError(
                f"Cannot complete tasks phase from {workflow.current_phase.value}"
            )

        if workflow.phase_status[PhaseType.TASKS] != PhaseStatus.IN_PROGRESS:
            raise ValueError("Tasks phase is not in progress")

        workflow.phase_status[PhaseType.TASKS] = PhaseStatus.REVIEW
        workflow.can_proceed = False
        workflow.requires_approval = True
        workflow.last_updated = datetime.now()

        return workflow

    def approve_tasks_phase(self, feature_name: str) -> WorkflowState:
        """Approve tasks phase and complete the workflow.

        Args:
            feature_name: Name of the feature

        Returns:
            WorkflowState: Updated workflow state

        Raises:
            ValueError: If workflow doesn't exist or phase cannot be approved
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            raise ValueError(f"No workflow found for feature: {feature_name}")

        if workflow.current_phase != PhaseType.TASKS:
            raise ValueError(
                f"Cannot approve tasks phase from {workflow.current_phase.value}"
            )

        if workflow.phase_status[PhaseType.TASKS] != PhaseStatus.REVIEW:
            raise ValueError("Tasks phase is not ready for approval")

        workflow.phase_status[PhaseType.TASKS] = PhaseStatus.APPROVED
        workflow.can_proceed = False
        workflow.requires_approval = False
        workflow.last_updated = datetime.now()

        return workflow

    def can_transition_to_phase(
        self, feature_name: str, target_phase: PhaseType
    ) -> bool:
        """Check if workflow can transition to a specific phase.

        Args:
            feature_name: Name of the feature
            target_phase: Phase to transition to

        Returns:
            bool: True if transition is allowed
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            return False

        if target_phase == PhaseType.REQUIREMENTS:
            return True  # Can always go back to requirements
        elif target_phase == PhaseType.DESIGN:
            return workflow.phase_status[PhaseType.REQUIREMENTS] == PhaseStatus.APPROVED
        elif target_phase == PhaseType.TASKS:
            return (
                workflow.phase_status[PhaseType.REQUIREMENTS] == PhaseStatus.APPROVED
                and workflow.phase_status[PhaseType.DESIGN] == PhaseStatus.APPROVED
            )

        return False
