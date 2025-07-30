"""Recovery and rollback capabilities for the MCP spec-driven development tool."""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

from .error_handler import get_error_handler
from .exceptions import (
    RecoverySuggestion,
    SpecDrivenDevelopmentError,
    StateError,
    WorkflowError,
)
from .workflow.models import PhaseStatus, PhaseType, WorkflowState


class RecoveryAction(Enum):
    """Types of recovery actions available."""

    ROLLBACK_STATE = "rollback_state"
    RESET_PHASE = "reset_phase"
    RESTORE_BACKUP = "restore_backup"
    GRACEFUL_DEGRADATION = "graceful_degradation"
    ALTERNATIVE_PATH = "alternative_path"


@dataclass
class StateSnapshot:
    """Represents a snapshot of workflow state for rollback purposes."""

    feature_name: str
    timestamp: datetime
    current_phase: PhaseType
    phase_statuses: Dict[PhaseType, PhaseStatus]
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary for serialization."""
        return {
            "feature_name": self.feature_name,
            "timestamp": self.timestamp.isoformat(),
            "current_phase": self.current_phase.value,
            "phase_statuses": {
                phase.value: status.value
                for phase, status in self.phase_statuses.items()
            },
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StateSnapshot":
        """Create snapshot from dictionary."""
        return cls(
            feature_name=data["feature_name"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            current_phase=PhaseType(data["current_phase"]),
            phase_statuses={
                PhaseType(k): PhaseStatus(v) for k, v in data["phase_statuses"].items()
            },
            metadata=data["metadata"],
        )


@dataclass
class RecoveryPlan:
    """Represents a recovery plan for handling failures."""

    action: RecoveryAction
    description: str
    steps: List[str]
    fallback_options: List[str]
    success_criteria: List[str]
    estimated_time: str
    risk_level: str  # "low", "medium", "high"


class RecoveryManager:
    """Manages recovery and rollback capabilities for workflow failures."""

    def __init__(
        self, backup_dir: Optional[Path] = None, logger: Optional[logging.Logger] = None
    ):
        """Initialize recovery manager."""
        self.backup_dir = backup_dir or Path.cwd() / ".kiro" / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)
        self.error_handler = get_error_handler()

        # State snapshots for rollback
        self._state_snapshots: Dict[str, List[StateSnapshot]] = {}

        # Recovery handlers for different error types
        self._recovery_handlers: Dict[str, Callable] = {
            "validation": self._handle_validation_recovery,
            "workflow": self._handle_workflow_recovery,
            "content": self._handle_content_recovery,
            "state": self._handle_state_recovery,
            "task": self._handle_task_recovery,
        }

        # Graceful degradation handlers
        self._degradation_handlers: Dict[str, Callable] = {
            "content_access": self._degrade_content_access,
            "validation": self._degrade_validation,
            "workflow_management": self._degrade_workflow_management,
        }

    def create_state_snapshot(
        self, workflow_state: WorkflowState, metadata: Optional[Dict[str, Any]] = None
    ) -> StateSnapshot:
        """Create a snapshot of current workflow state."""
        snapshot = StateSnapshot(
            feature_name=workflow_state.feature_name,
            timestamp=datetime.now(),
            current_phase=workflow_state.current_phase,
            phase_statuses=workflow_state.phase_status.copy(),
            metadata=metadata or {},
        )

        # Store snapshot in memory
        if workflow_state.feature_name not in self._state_snapshots:
            self._state_snapshots[workflow_state.feature_name] = []

        self._state_snapshots[workflow_state.feature_name].append(snapshot)

        # Keep only last 10 snapshots per feature
        if len(self._state_snapshots[workflow_state.feature_name]) > 10:
            self._state_snapshots[workflow_state.feature_name] = self._state_snapshots[
                workflow_state.feature_name
            ][-10:]

        # Persist snapshot to disk
        self._persist_snapshot(snapshot)

        self.logger.info(
            f"Created state snapshot for {workflow_state.feature_name} at phase {workflow_state.current_phase.value}"
        )
        return snapshot

    def rollback_to_snapshot(
        self, feature_name: str, snapshot_index: int = -1
    ) -> StateSnapshot:
        """
        Rollback workflow state to a previous snapshot.

        Args:
            feature_name: Name of the feature to rollback
            snapshot_index: Index of snapshot to rollback to (-1 for most recent)

        Returns:
            The snapshot that was rolled back to

        Raises:
            StateError: If rollback fails or no snapshots available
        """
        try:
            snapshots = self._state_snapshots.get(feature_name, [])
            if not snapshots:
                raise self.error_handler.handle_state_error(
                    message=f"No state snapshots available for feature: {feature_name}",
                    feature_name=feature_name,
                    state_operation="rollback",
                )

            if abs(snapshot_index) > len(snapshots):
                raise self.error_handler.handle_state_error(
                    message=f"Invalid snapshot index {snapshot_index} for feature {feature_name}",
                    feature_name=feature_name,
                    state_operation="rollback",
                )

            target_snapshot = snapshots[snapshot_index]

            # Create recovery plan
            recovery_plan = RecoveryPlan(
                action=RecoveryAction.ROLLBACK_STATE,
                description=f"Rollback {feature_name} to state from {target_snapshot.timestamp}",
                steps=[
                    f"Restore phase to {target_snapshot.current_phase.value}",
                    "Restore phase statuses",
                    "Update workflow metadata",
                    "Verify state consistency",
                ],
                fallback_options=[
                    "Try different snapshot",
                    "Reset to initial state",
                    "Manual state reconstruction",
                ],
                success_criteria=[
                    "Workflow state matches snapshot",
                    "All phase statuses restored",
                    "No validation errors",
                ],
                estimated_time="< 1 minute",
                risk_level="low",
            )

            self.logger.info(
                f"Executing rollback plan for {feature_name}: {recovery_plan.description}"
            )

            # Execute rollback (this would integrate with actual state management)
            # For now, we return the snapshot that would be restored
            return target_snapshot

        except Exception as e:
            raise self.error_handler.handle_state_error(
                message=f"Failed to rollback state for {feature_name}: {str(e)}",
                feature_name=feature_name,
                state_operation="rollback",
                context={"snapshot_index": snapshot_index, "original_error": str(e)},
            )

    def get_recovery_plan(self, error: SpecDrivenDevelopmentError) -> RecoveryPlan:
        """
        Generate a recovery plan for a specific error.

        Args:
            error: The error to create a recovery plan for

        Returns:
            A recovery plan with specific steps and options
        """
        error_type = error.__class__.__name__.lower().replace("error", "")

        if error_type in self._recovery_handlers:
            return self._recovery_handlers[error_type](error)
        else:
            return self._create_generic_recovery_plan(error)

    def execute_graceful_degradation(
        self, component: str, error: Exception
    ) -> Dict[str, Any]:
        """
        Execute graceful degradation for a failing component.

        Args:
            component: The component that is failing
            error: The error that occurred

        Returns:
            Dictionary with degradation results and fallback information
        """
        if component in self._degradation_handlers:
            return self._degradation_handlers[component](error)
        else:
            return self._default_degradation(component, error)

    def get_alternative_paths(
        self, failed_operation: str, context: Dict[str, Any]
    ) -> List[str]:
        """
        Get alternative paths when a primary operation fails.

        Args:
            failed_operation: The operation that failed
            context: Context information about the failure

        Returns:
            List of alternative approaches
        """
        alternatives = {
            "phase_transition": [
                "Skip validation temporarily and proceed",
                "Use manual phase tracking",
                "Reset workflow and restart from beginning",
                "Create new workflow instance",
            ],
            "document_validation": [
                "Use basic format checking instead of full validation",
                "Proceed with warnings instead of errors",
                "Use template comparison for validation",
                "Manual review and approval",
            ],
            "content_access": [
                "Use fallback content from built-in templates",
                "Generate minimal content dynamically",
                "Use cached content from previous sessions",
                "Prompt user to provide content manually",
            ],
            "state_management": [
                "Use file-based state persistence",
                "Implement in-memory state tracking",
                "Use simplified state model",
                "Manual state reconstruction",
            ],
        }

        return alternatives.get(
            failed_operation,
            [
                "Retry operation with different parameters",
                "Use simplified version of operation",
                "Skip operation and continue with workflow",
                "Contact system administrator for assistance",
            ],
        )

    def _persist_snapshot(self, snapshot: StateSnapshot) -> None:
        """Persist snapshot to disk for durability."""
        try:
            feature_dir = self.backup_dir / snapshot.feature_name
            feature_dir.mkdir(exist_ok=True)

            snapshot_file = (
                feature_dir
                / f"snapshot_{snapshot.timestamp.strftime('%Y%m%d_%H%M%S')}.json"
            )

            with open(snapshot_file, "w") as f:
                json.dump(snapshot.to_dict(), f, indent=2)

            self.logger.debug(f"Persisted snapshot to {snapshot_file}")

        except Exception as e:
            self.logger.warning(f"Failed to persist snapshot: {e}")

    def _load_snapshots_from_disk(self, feature_name: str) -> List[StateSnapshot]:
        """Load snapshots from disk for a feature."""
        snapshots = []
        try:
            feature_dir = self.backup_dir / feature_name
            if not feature_dir.exists():
                return snapshots

            for snapshot_file in feature_dir.glob("snapshot_*.json"):
                try:
                    with open(snapshot_file, "r") as f:
                        data = json.load(f)
                    snapshots.append(StateSnapshot.from_dict(data))
                except Exception as e:
                    self.logger.warning(f"Failed to load snapshot {snapshot_file}: {e}")

            # Sort by timestamp
            snapshots.sort(key=lambda s: s.timestamp)

        except Exception as e:
            self.logger.warning(f"Failed to load snapshots for {feature_name}: {e}")

        return snapshots

    def _handle_validation_recovery(
        self, error: SpecDrivenDevelopmentError
    ) -> RecoveryPlan:
        """Handle recovery for validation errors."""
        return RecoveryPlan(
            action=RecoveryAction.GRACEFUL_DEGRADATION,
            description="Recover from validation errors with reduced validation",
            steps=[
                "Identify critical vs non-critical validation errors",
                "Apply fixes for critical errors only",
                "Use fallback validation for non-critical issues",
                "Proceed with warnings for minor issues",
            ],
            fallback_options=[
                "Skip validation temporarily",
                "Use template-based validation",
                "Manual review and approval",
                "Use previous successful validation",
            ],
            success_criteria=[
                "Critical errors resolved",
                "Document structure is valid",
                "Workflow can proceed",
            ],
            estimated_time="2-5 minutes",
            risk_level="low",
        )

    def _handle_workflow_recovery(
        self, error: SpecDrivenDevelopmentError
    ) -> RecoveryPlan:
        """Handle recovery for workflow errors."""
        return RecoveryPlan(
            action=RecoveryAction.ROLLBACK_STATE,
            description="Recover from workflow errors by rolling back to stable state",
            steps=[
                "Identify last stable workflow state",
                "Rollback to previous phase if necessary",
                "Reset phase status to valid state",
                "Re-attempt workflow operation",
            ],
            fallback_options=[
                "Create new workflow instance",
                "Use manual workflow tracking",
                "Skip problematic phase temporarily",
                "Reset entire workflow",
            ],
            success_criteria=[
                "Workflow state is consistent",
                "Phase transitions work correctly",
                "User can proceed with development",
            ],
            estimated_time="1-3 minutes",
            risk_level="medium",
        )

    def _handle_content_recovery(
        self, error: SpecDrivenDevelopmentError
    ) -> RecoveryPlan:
        """Handle recovery for content access errors."""
        return RecoveryPlan(
            action=RecoveryAction.ALTERNATIVE_PATH,
            description="Recover from content access errors using fallback content",
            steps=[
                "Attempt to use fallback content providers",
                "Generate minimal content if needed",
                "Use cached content from previous sessions",
                "Provide user with manual content options",
            ],
            fallback_options=[
                "Use built-in minimal templates",
                "Generate content dynamically",
                "Prompt user to provide content",
                "Continue without specific content",
            ],
            success_criteria=[
                "User has access to necessary content",
                "Workflow can continue",
                "Content quality is acceptable",
            ],
            estimated_time="< 1 minute",
            risk_level="low",
        )

    def _handle_state_recovery(self, error: SpecDrivenDevelopmentError) -> RecoveryPlan:
        """Handle recovery for state management errors."""
        return RecoveryPlan(
            action=RecoveryAction.RESTORE_BACKUP,
            description="Recover from state errors by restoring from backup",
            steps=[
                "Identify available state backups",
                "Select most recent valid backup",
                "Restore state from backup",
                "Verify state consistency",
            ],
            fallback_options=[
                "Initialize fresh state",
                "Use file-based state persistence",
                "Manual state reconstruction",
                "Reset to default state",
            ],
            success_criteria=[
                "State is consistent and valid",
                "Workflow operations work correctly",
                "No data loss occurred",
            ],
            estimated_time="1-2 minutes",
            risk_level="medium",
        )

    def _handle_task_recovery(self, error: SpecDrivenDevelopmentError) -> RecoveryPlan:
        """Handle recovery for task execution errors."""
        return RecoveryPlan(
            action=RecoveryAction.ALTERNATIVE_PATH,
            description="Recover from task execution errors with alternative approaches",
            steps=[
                "Analyze task dependencies and requirements",
                "Break down complex tasks into smaller steps",
                "Identify alternative implementation approaches",
                "Provide additional context and guidance",
            ],
            fallback_options=[
                "Skip non-critical tasks temporarily",
                "Use simplified task implementations",
                "Manual task execution guidance",
                "Defer task to later phase",
            ],
            success_criteria=[
                "Task can be executed successfully",
                "Requirements are still met",
                "Development can proceed",
            ],
            estimated_time="5-10 minutes",
            risk_level="low",
        )

    def _create_generic_recovery_plan(
        self, error: SpecDrivenDevelopmentError
    ) -> RecoveryPlan:
        """Create a generic recovery plan for unknown error types."""
        return RecoveryPlan(
            action=RecoveryAction.GRACEFUL_DEGRADATION,
            description="Generic recovery from unexpected error",
            steps=[
                "Log error details for analysis",
                "Attempt to continue with reduced functionality",
                "Provide user with error information and options",
                "Suggest alternative approaches",
            ],
            fallback_options=[
                "Restart the operation",
                "Use simplified functionality",
                "Manual intervention",
                "Contact support",
            ],
            success_criteria=[
                "System remains functional",
                "User can continue working",
                "Error is properly logged",
            ],
            estimated_time="Variable",
            risk_level="medium",
        )

    def _degrade_content_access(self, error: Exception) -> Dict[str, Any]:
        """Graceful degradation for content access failures."""
        return {
            "status": "degraded",
            "functionality": "fallback_content",
            "message": "Using built-in fallback content due to access issues",
            "limitations": [
                "Content may be less comprehensive",
                "Examples may be generic",
                "Updates may not be available",
            ],
            "recovery_actions": [
                "Check content file permissions",
                "Verify content directory structure",
                "Update content files if needed",
            ],
        }

    def _degrade_validation(self, error: Exception) -> Dict[str, Any]:
        """Graceful degradation for validation failures."""
        return {
            "status": "degraded",
            "functionality": "basic_validation",
            "message": "Using basic validation due to validation system issues",
            "limitations": [
                "Only critical errors will be caught",
                "Format checking may be limited",
                "Some quality checks disabled",
            ],
            "recovery_actions": [
                "Review documents manually",
                "Use template comparison",
                "Enable full validation when possible",
            ],
        }

    def _degrade_workflow_management(self, error: Exception) -> Dict[str, Any]:
        """Graceful degradation for workflow management failures."""
        return {
            "status": "degraded",
            "functionality": "manual_tracking",
            "message": "Using manual workflow tracking due to system issues",
            "limitations": [
                "Automatic phase transitions disabled",
                "State tracking may be limited",
                "Approval workflow simplified",
            ],
            "recovery_actions": [
                "Track progress manually",
                "Use file-based state if needed",
                "Restart workflow system when possible",
            ],
        }

    def _default_degradation(self, component: str, error: Exception) -> Dict[str, Any]:
        """Default graceful degradation for unknown components."""
        return {
            "status": "degraded",
            "functionality": "limited",
            "message": f"Component {component} is operating with limited functionality",
            "limitations": [
                "Some features may be unavailable",
                "Performance may be reduced",
                "Manual intervention may be required",
            ],
            "recovery_actions": [
                "Check system logs",
                "Restart component if possible",
                "Contact system administrator",
            ],
        }
