"""Data models for workflow management."""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


class PhaseType(Enum):
    """Types of phases in the spec-driven development workflow."""

    REQUIREMENTS = "requirements"
    DESIGN = "design"
    TASKS = "tasks"


class StatusType(Enum):
    """Status types for spec documents."""

    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"


class PhaseStatus(Enum):
    """Status types for workflow phases."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    APPROVED = "approved"


@dataclass
class SpecDocument:
    """Represents a spec document in a specific phase."""

    feature_name: str
    phase: PhaseType
    status: StatusType
    content: str
    last_modified: datetime
    validation_results: Optional[List["ValidationResult"]] = None


@dataclass
class WorkflowState:
    """Represents the current state of a spec workflow."""

    feature_name: str
    current_phase: PhaseType
    phase_status: Dict[PhaseType, PhaseStatus]
    can_proceed: bool
    requires_approval: bool
    last_updated: datetime


@dataclass
class ValidationLocation:
    """Location information for validation results."""

    section: str
    line: Optional[int] = None


@dataclass
class ValidationResult:
    """Result of document validation."""

    type: str  # 'error', 'warning', 'info'
    message: str
    location: Optional[ValidationLocation] = None
    suggestion: Optional[str] = None
