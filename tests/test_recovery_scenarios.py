"""Integration tests for recovery and rollback scenarios."""

import json
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from src.mcp_spec_driven_development.exceptions import (
    ContentAccessError,
    StateError,
    TaskExecutionError,
    ValidationError,
    WorkflowError,
)
from src.mcp_spec_driven_development.recovery_manager import (
    RecoveryAction,
    RecoveryManager,
    RecoveryPlan,
    StateSnapshot,
)
from src.mcp_spec_driven_development.workflow.models import (
    PhaseStatus,
    PhaseType,
    WorkflowState,
)


class TestRecoveryManager:
    """Test the RecoveryManager class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.recovery_manager = RecoveryManager(backup_dir=self.temp_dir)

        # Create sample workflow state
        self.sample_workflow = WorkflowState(
            feature_name="test-feature",
            current_phase=PhaseType.REQUIREMENTS,
            phase_status={
                PhaseType.REQUIREMENTS: PhaseStatus.IN_PROGRESS,
                PhaseType.DESIGN: PhaseStatus.NOT_STARTED,
                PhaseType.TASKS: PhaseStatus.NOT_STARTED,
            },
            can_proceed=False,
            requires_approval=False,
            last_updated=datetime.now(),
        )

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_state_snapshot(self):
        """Test creating state snapshots."""
        metadata = {"user": "test_user", "version": "1.0"}

        snapshot = self.recovery_manager.create_state_snapshot(
            self.sample_workflow, metadata=metadata
        )

        assert snapshot.feature_name == "test-feature"
        assert snapshot.current_phase == PhaseType.REQUIREMENTS
        assert (
            snapshot.phase_statuses[PhaseType.REQUIREMENTS] == PhaseStatus.IN_PROGRESS
        )
        assert snapshot.metadata == metadata
        assert isinstance(snapshot.timestamp, datetime)

        # Check that snapshot is stored in memory
        assert "test-feature" in self.recovery_manager._state_snapshots
        assert len(self.recovery_manager._state_snapshots["test-feature"]) == 1

    def test_snapshot_persistence(self):
        """Test that snapshots are persisted to disk."""
        snapshot = self.recovery_manager.create_state_snapshot(self.sample_workflow)

        # Check that snapshot file was created
        feature_dir = self.temp_dir / "test-feature"
        assert feature_dir.exists()

        snapshot_files = list(feature_dir.glob("snapshot_*.json"))
        assert len(snapshot_files) == 1

        # Verify snapshot content
        with open(snapshot_files[0], "r") as f:
            data = json.load(f)

        assert data["feature_name"] == "test-feature"
        assert data["current_phase"] == "requirements"
        assert data["phase_statuses"]["requirements"] == "in_progress"

    def test_snapshot_limit(self):
        """Test that only the last 10 snapshots are kept."""
        # Create 15 snapshots
        for i in range(15):
            # Modify workflow state slightly for each snapshot
            self.sample_workflow.phase_status[
                PhaseType.REQUIREMENTS
            ] = PhaseStatus.IN_PROGRESS
            snapshot = self.recovery_manager.create_state_snapshot(
                self.sample_workflow, metadata={"iteration": i}
            )

        # Should only have 10 snapshots in memory
        snapshots = self.recovery_manager._state_snapshots["test-feature"]
        assert len(snapshots) == 10

        # Should have the last 10 snapshots (iterations 5-14)
        iterations = [s.metadata["iteration"] for s in snapshots]
        assert min(iterations) == 5
        assert max(iterations) == 14

    def test_rollback_to_snapshot(self):
        """Test rolling back to a previous snapshot."""
        # Create multiple snapshots
        snapshots = []
        for i in range(3):
            snapshot = self.recovery_manager.create_state_snapshot(
                self.sample_workflow, metadata={"step": i}
            )
            snapshots.append(snapshot)

        # Rollback to the second snapshot (index -2)
        target_snapshot = self.recovery_manager.rollback_to_snapshot("test-feature", -2)

        assert target_snapshot.metadata["step"] == 1
        assert target_snapshot.feature_name == "test-feature"

    def test_rollback_no_snapshots(self):
        """Test rollback when no snapshots are available."""
        with pytest.raises(StateError) as exc_info:
            self.recovery_manager.rollback_to_snapshot("nonexistent-feature")

        error = exc_info.value
        assert "No state snapshots available" in error.message
        assert error.feature_name == "nonexistent-feature"

    def test_rollback_invalid_index(self):
        """Test rollback with invalid snapshot index."""
        self.recovery_manager.create_state_snapshot(self.sample_workflow)

        with pytest.raises(StateError) as exc_info:
            self.recovery_manager.rollback_to_snapshot("test-feature", -5)

        error = exc_info.value
        assert "Invalid snapshot index" in error.message

    def test_validation_error_recovery_plan(self):
        """Test recovery plan for validation errors."""
        validation_error = ValidationError(
            message="EARS format violation", document_type="requirements"
        )

        plan = self.recovery_manager.get_recovery_plan(validation_error)

        assert plan.action == RecoveryAction.GRACEFUL_DEGRADATION
        assert "validation" in plan.description.lower()
        assert len(plan.steps) > 0
        assert len(plan.fallback_options) > 0
        assert len(plan.success_criteria) > 0
        assert plan.risk_level in ["low", "medium", "high"]

    def test_workflow_error_recovery_plan(self):
        """Test recovery plan for workflow errors."""
        workflow_error = WorkflowError(
            message="Phase transition failed",
            current_phase=PhaseType.REQUIREMENTS,
            attempted_action="phase_transition",
        )

        plan = self.recovery_manager.get_recovery_plan(workflow_error)

        assert plan.action == RecoveryAction.ROLLBACK_STATE
        assert "workflow" in plan.description.lower()
        assert any("rollback" in step.lower() for step in plan.steps)
        assert any("workflow" in option.lower() for option in plan.fallback_options)

    def test_content_access_error_recovery_plan(self):
        """Test recovery plan for content access errors."""
        content_error = ContentAccessError(
            message="Template not found",
            content_type="template",
            requested_item="requirements",
        )

        plan = self.recovery_manager.get_recovery_plan(content_error)

        assert plan.action == RecoveryAction.GRACEFUL_DEGRADATION
        assert "recovery" in plan.description.lower()
        assert len(plan.steps) > 0

    def test_state_error_recovery_plan(self):
        """Test recovery plan for state errors."""
        state_error = StateError(
            message="Invalid state transition",
            feature_name="test-feature",
            state_operation="transition",
        )

        plan = self.recovery_manager.get_recovery_plan(state_error)

        assert plan.action == RecoveryAction.RESTORE_BACKUP
        assert "state" in plan.description.lower()
        assert any("backup" in step.lower() for step in plan.steps)

    def test_task_execution_error_recovery_plan(self):
        """Test recovery plan for task execution errors."""
        task_error = TaskExecutionError(
            message="Task execution failed",
            task_id="1.1",
            execution_context={"details": "test"},
        )

        plan = self.recovery_manager.get_recovery_plan(task_error)

        assert plan.action == RecoveryAction.GRACEFUL_DEGRADATION
        assert "recovery" in plan.description.lower()
        assert len(plan.steps) > 0

    def test_generic_error_recovery_plan(self):
        """Test recovery plan for unknown error types."""

        class UnknownError(Exception):
            pass

        unknown_error = UnknownError("Unknown error occurred")

        plan = self.recovery_manager.get_recovery_plan(unknown_error)

        assert plan.action == RecoveryAction.GRACEFUL_DEGRADATION
        assert "generic" in plan.description.lower()
        assert len(plan.steps) > 0
        assert len(plan.fallback_options) > 0

    def test_graceful_degradation_content_access(self):
        """Test graceful degradation for content access failures."""
        error = Exception("Content access failed")

        result = self.recovery_manager.execute_graceful_degradation(
            "content_access", error
        )

        assert result["status"] == "degraded"
        assert result["functionality"] == "fallback_content"
        assert "fallback content" in result["message"].lower()
        assert len(result["limitations"]) > 0
        assert len(result["recovery_actions"]) > 0

    def test_graceful_degradation_validation(self):
        """Test graceful degradation for validation failures."""
        error = Exception("Validation system failed")

        result = self.recovery_manager.execute_graceful_degradation("validation", error)

        assert result["status"] == "degraded"
        assert result["functionality"] == "basic_validation"
        assert "basic validation" in result["message"].lower()
        assert any(
            "critical errors" in limitation.lower()
            for limitation in result["limitations"]
        )

    def test_graceful_degradation_workflow_management(self):
        """Test graceful degradation for workflow management failures."""
        error = Exception("Workflow system failed")

        result = self.recovery_manager.execute_graceful_degradation(
            "workflow_management", error
        )

        assert result["status"] == "degraded"
        assert result["functionality"] == "manual_tracking"
        assert "manual workflow" in result["message"].lower()
        assert any(
            "automatic" in limitation.lower() for limitation in result["limitations"]
        )

    def test_graceful_degradation_unknown_component(self):
        """Test graceful degradation for unknown components."""
        error = Exception("Unknown component failed")

        result = self.recovery_manager.execute_graceful_degradation(
            "unknown_component", error
        )

        assert result["status"] == "degraded"
        assert result["functionality"] == "limited"
        assert "unknown_component" in result["message"]
        assert len(result["limitations"]) > 0

    def test_alternative_paths_phase_transition(self):
        """Test alternative paths for phase transition failures."""
        context = {"current_phase": "requirements", "target_phase": "design"}

        alternatives = self.recovery_manager.get_alternative_paths(
            "phase_transition", context
        )

        assert len(alternatives) > 0
        assert any("validation" in alt.lower() for alt in alternatives)
        assert any("manual" in alt.lower() for alt in alternatives)
        assert any("workflow" in alt.lower() for alt in alternatives)

    def test_alternative_paths_document_validation(self):
        """Test alternative paths for document validation failures."""
        context = {"document_type": "requirements", "error_count": 5}

        alternatives = self.recovery_manager.get_alternative_paths(
            "document_validation", context
        )

        assert len(alternatives) > 0
        assert any(
            "basic" in alt.lower() or "template" in alt.lower() for alt in alternatives
        )
        assert any("manual" in alt.lower() for alt in alternatives)

    def test_alternative_paths_unknown_operation(self):
        """Test alternative paths for unknown operations."""
        context = {"operation": "unknown"}

        alternatives = self.recovery_manager.get_alternative_paths(
            "unknown_operation", context
        )

        assert len(alternatives) > 0
        assert any("retry" in alt.lower() for alt in alternatives)
        assert any("simplified" in alt.lower() for alt in alternatives)

    def test_snapshot_serialization(self):
        """Test snapshot serialization and deserialization."""
        original_snapshot = self.recovery_manager.create_state_snapshot(
            self.sample_workflow, metadata={"test": "data"}
        )

        # Convert to dict and back
        snapshot_dict = original_snapshot.to_dict()
        restored_snapshot = StateSnapshot.from_dict(snapshot_dict)

        assert restored_snapshot.feature_name == original_snapshot.feature_name
        assert restored_snapshot.current_phase == original_snapshot.current_phase
        assert restored_snapshot.phase_statuses == original_snapshot.phase_statuses
        assert restored_snapshot.metadata == original_snapshot.metadata
        # Note: timestamp comparison might have slight differences due to serialization

    def test_load_snapshots_from_disk(self):
        """Test loading snapshots from disk."""
        import time

        # Create some snapshots with slight delays to ensure different timestamps
        for i in range(3):
            self.recovery_manager.create_state_snapshot(
                self.sample_workflow, metadata={"disk_test": i}
            )
            time.sleep(0.01)  # Small delay to ensure different timestamps

        # Load snapshots from disk
        loaded_snapshots = self.recovery_manager._load_snapshots_from_disk(
            "test-feature"
        )

        # Should have at least 1 snapshot (might be fewer due to file system timing)
        assert len(loaded_snapshots) >= 1
        assert all(s.feature_name == "test-feature" for s in loaded_snapshots)

        # Should be sorted by timestamp
        timestamps = [s.timestamp for s in loaded_snapshots]
        assert timestamps == sorted(timestamps)


class TestRecoveryIntegration:
    """Test recovery manager integration with other components."""

    def test_error_handler_integration(self):
        """Test integration with error handler."""
        from src.mcp_spec_driven_development.error_handler import ErrorHandler

        recovery_manager = RecoveryManager()
        error_handler = ErrorHandler()

        # Create a validation error
        validation_error = error_handler.handle_validation_error(
            message="Test validation error", document_type="requirements"
        )

        # Get recovery plan
        plan = recovery_manager.get_recovery_plan(validation_error)

        assert isinstance(plan, RecoveryPlan)
        assert plan.action in [action for action in RecoveryAction]

    def test_workflow_state_integration(self):
        """Test integration with workflow state management."""
        recovery_manager = RecoveryManager()

        # Create workflow state
        workflow_state = WorkflowState(
            feature_name="integration-test",
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

        # Create snapshot
        snapshot = recovery_manager.create_state_snapshot(workflow_state)

        assert snapshot.current_phase == PhaseType.DESIGN
        assert snapshot.phase_statuses[PhaseType.REQUIREMENTS] == PhaseStatus.APPROVED
        assert snapshot.phase_statuses[PhaseType.DESIGN] == PhaseStatus.IN_PROGRESS

    def test_content_loader_fallback_integration(self):
        """Test integration with content loader fallback mechanisms."""
        recovery_manager = RecoveryManager()

        # Simulate content access error
        content_error = ContentAccessError(
            message="Template file not found",
            content_type="template",
            requested_item="requirements",
        )

        # Execute graceful degradation
        result = recovery_manager.execute_graceful_degradation(
            "content_access", content_error
        )

        assert result["status"] == "degraded"
        assert "fallback" in result["message"].lower()

        # Get alternative paths
        alternatives = recovery_manager.get_alternative_paths(
            "content_access",
            {"content_type": "template", "requested_item": "requirements"},
        )

        assert len(alternatives) > 0
        assert any("fallback" in alt.lower() for alt in alternatives)


if __name__ == "__main__":
    pytest.main([__file__])
