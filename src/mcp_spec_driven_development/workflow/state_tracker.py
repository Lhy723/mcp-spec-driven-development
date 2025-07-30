"""State tracking system for spec-driven development workflow."""

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .models import PhaseStatus, PhaseType, WorkflowState


class StateTracker:
    """Tracks workflow state and manages transitions."""

    def __init__(self):
        """Initialize the state tracker."""
        self._workflows: Dict[str, WorkflowState] = {}
        self._approval_history: Dict[str, List[Tuple[PhaseType, datetime, bool]]] = {}

    def track_workflow(self, workflow_state: WorkflowState) -> None:
        """Start tracking a workflow state.

        Args:
            workflow_state: The workflow state to track
        """
        self._workflows[workflow_state.feature_name] = workflow_state
        if workflow_state.feature_name not in self._approval_history:
            self._approval_history[workflow_state.feature_name] = []

    def get_current_phase(self, feature_name: str) -> Optional[PhaseType]:
        """Get the current phase for a feature.

        Args:
            feature_name: Name of the feature

        Returns:
            PhaseType or None if workflow not found
        """
        workflow = self._workflows.get(feature_name)
        return workflow.current_phase if workflow else None

    def get_phase_status(
        self, feature_name: str, phase: PhaseType
    ) -> Optional[PhaseStatus]:
        """Get the status of a specific phase.

        Args:
            feature_name: Name of the feature
            phase: Phase to check status for

        Returns:
            PhaseStatus or None if workflow not found
        """
        workflow = self._workflows.get(feature_name)
        return workflow.phase_status.get(phase) if workflow else None

    def get_all_phase_statuses(
        self, feature_name: str
    ) -> Optional[Dict[PhaseType, PhaseStatus]]:
        """Get all phase statuses for a feature.

        Args:
            feature_name: Name of the feature

        Returns:
            Dictionary of phase statuses or None if workflow not found
        """
        workflow = self._workflows.get(feature_name)
        return workflow.phase_status.copy() if workflow else None

    def is_phase_complete(self, feature_name: str, phase: PhaseType) -> bool:
        """Check if a phase is complete (approved).

        Args:
            feature_name: Name of the feature
            phase: Phase to check

        Returns:
            bool: True if phase is approved
        """
        status = self.get_phase_status(feature_name, phase)
        return status == PhaseStatus.APPROVED if status else False

    def get_completion_percentage(self, feature_name: str) -> float:
        """Get overall completion percentage for a workflow.

        Args:
            feature_name: Name of the feature

        Returns:
            float: Completion percentage (0.0 to 1.0)
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            return 0.0

        total_phases = len(PhaseType)
        completed_phases = sum(
            1
            for status in workflow.phase_status.values()
            if status == PhaseStatus.APPROVED
        )

        return completed_phases / total_phases

    def requires_user_approval(self, feature_name: str) -> bool:
        """Check if workflow currently requires user approval.

        Args:
            feature_name: Name of the feature

        Returns:
            bool: True if user approval is required
        """
        workflow = self._workflows.get(feature_name)
        return workflow.requires_approval if workflow else False

    def can_proceed_to_next_phase(self, feature_name: str) -> bool:
        """Check if workflow can proceed to next phase.

        Args:
            feature_name: Name of the feature

        Returns:
            bool: True if can proceed
        """
        workflow = self._workflows.get(feature_name)
        return workflow.can_proceed if workflow else False

    def record_approval(
        self, feature_name: str, phase: PhaseType, approved: bool
    ) -> None:
        """Record user approval for a phase.

        Args:
            feature_name: Name of the feature
            phase: Phase that was approved/rejected
            approved: Whether the phase was approved
        """
        if feature_name not in self._approval_history:
            self._approval_history[feature_name] = []

        self._approval_history[feature_name].append((phase, datetime.now(), approved))

    def get_approval_history(
        self, feature_name: str
    ) -> List[Tuple[PhaseType, datetime, bool]]:
        """Get approval history for a feature.

        Args:
            feature_name: Name of the feature

        Returns:
            List of (phase, timestamp, approved) tuples
        """
        return self._approval_history.get(feature_name, []).copy()

    def get_last_approval(
        self, feature_name: str, phase: PhaseType
    ) -> Optional[Tuple[datetime, bool]]:
        """Get the last approval record for a specific phase.

        Args:
            feature_name: Name of the feature
            phase: Phase to check

        Returns:
            Tuple of (timestamp, approved) or None if not found
        """
        history = self._approval_history.get(feature_name, [])
        for recorded_phase, timestamp, approved in reversed(history):
            if recorded_phase == phase:
                return (timestamp, approved)
        return None

    def can_navigate_backward(self, feature_name: str, target_phase: PhaseType) -> bool:
        """Check if backward navigation to a phase is allowed.

        Args:
            feature_name: Name of the feature
            target_phase: Phase to navigate back to

        Returns:
            bool: True if backward navigation is allowed
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            return False

        current_phase = workflow.current_phase

        # Can always go back to requirements
        if target_phase == PhaseType.REQUIREMENTS:
            return True

        # Can go back to design if currently in tasks
        if target_phase == PhaseType.DESIGN and current_phase == PhaseType.TASKS:
            return True

        # Cannot go forward or to same phase
        return False

    def navigate_backward(self, feature_name: str, target_phase: PhaseType) -> bool:
        """Navigate backward to a previous phase.

        Args:
            feature_name: Name of the feature
            target_phase: Phase to navigate back to

        Returns:
            bool: True if navigation was successful
        """
        if not self.can_navigate_backward(feature_name, target_phase):
            return False

        workflow = self._workflows.get(feature_name)
        if not workflow:
            return False

        # Update current phase
        workflow.current_phase = target_phase

        # Reset status of target phase and all subsequent phases
        if target_phase == PhaseType.REQUIREMENTS:
            workflow.phase_status[PhaseType.REQUIREMENTS] = PhaseStatus.IN_PROGRESS
            workflow.phase_status[PhaseType.DESIGN] = PhaseStatus.NOT_STARTED
            workflow.phase_status[PhaseType.TASKS] = PhaseStatus.NOT_STARTED
        elif target_phase == PhaseType.DESIGN:
            workflow.phase_status[PhaseType.DESIGN] = PhaseStatus.IN_PROGRESS
            workflow.phase_status[PhaseType.TASKS] = PhaseStatus.NOT_STARTED

        # Update workflow flags
        workflow.can_proceed = False
        workflow.requires_approval = True
        workflow.last_updated = datetime.now()

        return True

    def get_next_phase(self, feature_name: str) -> Optional[PhaseType]:
        """Get the next phase in the workflow.

        Args:
            feature_name: Name of the feature

        Returns:
            PhaseType or None if at end or workflow not found
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            return None

        current_phase = workflow.current_phase

        if current_phase == PhaseType.REQUIREMENTS:
            return PhaseType.DESIGN
        elif current_phase == PhaseType.DESIGN:
            return PhaseType.TASKS
        else:
            return None  # Tasks is the final phase

    def get_previous_phase(self, feature_name: str) -> Optional[PhaseType]:
        """Get the previous phase in the workflow.

        Args:
            feature_name: Name of the feature

        Returns:
            PhaseType or None if at beginning or workflow not found
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            return None

        current_phase = workflow.current_phase

        if current_phase == PhaseType.DESIGN:
            return PhaseType.REQUIREMENTS
        elif current_phase == PhaseType.TASKS:
            return PhaseType.DESIGN
        else:
            return None  # Requirements is the first phase

    def is_workflow_complete(self, feature_name: str) -> bool:
        """Check if the entire workflow is complete.

        Args:
            feature_name: Name of the feature

        Returns:
            bool: True if all phases are approved
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            return False

        return all(
            status == PhaseStatus.APPROVED for status in workflow.phase_status.values()
        )

    def get_workflow_summary(self, feature_name: str) -> Optional[Dict]:
        """Get a summary of the workflow state.

        Args:
            feature_name: Name of the feature

        Returns:
            Dictionary with workflow summary or None if not found
        """
        workflow = self._workflows.get(feature_name)
        if not workflow:
            return None

        return {
            "feature_name": workflow.feature_name,
            "current_phase": workflow.current_phase.value,
            "phase_statuses": {
                phase.value: status.value
                for phase, status in workflow.phase_status.items()
            },
            "completion_percentage": self.get_completion_percentage(feature_name),
            "can_proceed": workflow.can_proceed,
            "requires_approval": workflow.requires_approval,
            "is_complete": self.is_workflow_complete(feature_name),
            "last_updated": workflow.last_updated.isoformat(),
            "next_phase": self.get_next_phase(feature_name).value
            if self.get_next_phase(feature_name)
            else None,
            "previous_phase": self.get_previous_phase(feature_name).value
            if self.get_previous_phase(feature_name)
            else None,
        }

    def update_workflow_state(self, workflow_state: WorkflowState) -> None:
        """Update the tracked workflow state.

        Args:
            workflow_state: Updated workflow state
        """
        self._workflows[workflow_state.feature_name] = workflow_state

    def remove_workflow(self, feature_name: str) -> bool:
        """Remove a workflow from tracking.

        Args:
            feature_name: Name of the feature

        Returns:
            bool: True if workflow was removed
        """
        if feature_name in self._workflows:
            del self._workflows[feature_name]
            if feature_name in self._approval_history:
                del self._approval_history[feature_name]
            return True
        return False

    def list_tracked_workflows(self) -> List[str]:
        """Get list of all tracked workflow feature names.

        Returns:
            List of feature names
        """
        return list(self._workflows.keys())
