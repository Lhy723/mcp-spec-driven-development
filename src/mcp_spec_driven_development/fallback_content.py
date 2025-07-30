"""Fallback content providers for when primary content access fails."""

from enum import Enum
from typing import Any, Dict, Optional


class FallbackContentType(Enum):
    """Types of fallback content available."""

    METHODOLOGY = "methodology"
    TEMPLATE = "template"
    EXAMPLE = "example"


class FallbackContentProvider:
    """Provides fallback content when primary content sources fail."""

    # Minimal fallback templates
    FALLBACK_TEMPLATES = {
        "requirements": """# Requirements Document

## Introduction

[Brief description of the feature]

## Requirements

### Requirement 1

**User Story:** As a [role], I want [feature], so that [benefit]

#### Acceptance Criteria

1. WHEN [event] THEN [system] SHALL [response]
2. IF [condition] THEN [system] SHALL [response]

### Requirement 2

**User Story:** As a [role], I want [feature], so that [benefit]

#### Acceptance Criteria

1. WHEN [event] THEN [system] SHALL [response]
2. WHEN [event] AND [condition] THEN [system] SHALL [response]
""",
        "design": """# Design Document

## Overview

[Brief overview of the feature design]

## Architecture

[High-level architecture description]

## Components and Interfaces

[Description of main components and their interfaces]

## Data Models

[Data structures and models used]

## Error Handling

[Error handling strategy]

## Testing Strategy

[Approach to testing the feature]
""",
        "tasks": """# Implementation Plan

- [ ] 1. Set up project structure
  - Create necessary directories and files
  - Set up basic configuration
  - _Requirements: 1.1_

- [ ] 2. Implement core functionality
  - [ ] 2.1 Create main components
    - Implement primary business logic
    - Add necessary interfaces
    - _Requirements: 1.2_

  - [ ] 2.2 Add supporting features
    - Implement helper functions
    - Add utility components
    - _Requirements: 1.3_

- [ ] 3. Create tests
  - Write unit tests for core functionality
  - Add integration tests
  - _Requirements: All_
""",
    }

    # Minimal fallback methodology content
    FALLBACK_METHODOLOGY = {
        "workflow": """# Spec-Driven Development Workflow

The spec-driven development process follows three main phases:

## 1. Requirements Phase
- Define clear user stories
- Write acceptance criteria in EARS format
- Get explicit approval before proceeding

## 2. Design Phase
- Create comprehensive design document
- Address all requirements
- Include architecture and component details
- Get explicit approval before proceeding

## 3. Tasks Phase
- Break down design into actionable tasks
- Reference specific requirements
- Ensure tasks are implementable
- Get explicit approval before implementation

## Phase Transitions
- Each phase must be completed and approved
- Backward navigation is allowed for modifications
- Validation ensures quality at each step
""",
        "ears-format": """# EARS Format Guide

EARS (Easy Approach to Requirements Syntax) provides a structured way to write acceptance criteria.

## Basic Patterns

### WHEN...THEN...SHALL
Used for event-driven requirements:
- WHEN [event occurs] THEN [system] SHALL [response]

### IF...THEN...SHALL
Used for conditional requirements:
- IF [condition is true] THEN [system] SHALL [response]

### WHILE...THEN...SHALL
Used for continuous conditions:
- WHILE [condition persists] THEN [system] SHALL [response]

### WHERE...THEN...SHALL
Used for state-based requirements:
- WHERE [system is in state] THEN [system] SHALL [response]

## Examples

1. WHEN user clicks submit button THEN system SHALL validate form data
2. IF validation fails THEN system SHALL display error message
3. WHILE user is typing THEN system SHALL provide real-time feedback
4. WHERE user has admin privileges THEN system SHALL show admin menu
""",
        "phase-transitions": """# Phase Transition Rules

## Requirements to Design
- All requirements must be complete and approved
- User stories must be properly formatted
- Acceptance criteria must follow EARS format
- Explicit user approval required

## Design to Tasks
- Design document must include all required sections
- All requirements must be addressed in design
- Architecture and components must be clearly defined
- Explicit user approval required

## Tasks Completion
- All tasks must reference specific requirements
- Tasks must be actionable and implementable
- Dependencies must be properly ordered
- Explicit user approval required

## Backward Navigation
- Users can return to previous phases for modifications
- Changes may require re-approval of subsequent phases
- Validation ensures consistency across phases
""",
    }

    # Minimal fallback examples
    FALLBACK_EXAMPLES = {
        "requirements": """Example requirement with proper EARS format:

### Requirement 1

**User Story:** As a user, I want to log into the system, so that I can access my personal dashboard.

#### Acceptance Criteria

1. WHEN user enters valid credentials THEN system SHALL authenticate user and redirect to dashboard
2. IF credentials are invalid THEN system SHALL display error message and remain on login page
3. WHEN user clicks "forgot password" THEN system SHALL send password reset email
4. IF user account is locked THEN system SHALL display account locked message
""",
        "design": """Example design section with proper structure:

## Components and Interfaces

### Authentication Service
- **Purpose**: Handles user authentication and session management
- **Interface**: AuthService with methods: login(), logout(), validateSession()
- **Dependencies**: UserRepository, SessionManager

### User Repository
- **Purpose**: Manages user data persistence
- **Interface**: UserRepo with methods: findByEmail(), updateUser(), createUser()
- **Dependencies**: Database connection

This design addresses Requirements 1.1, 1.2, and 1.3 by providing secure authentication flow.
""",
        "tasks": """Example task with proper format and requirements reference:

- [ ] 1.1 Implement user authentication service
  - Create AuthService class with login/logout methods
  - Add password hashing and validation
  - Implement session management
  - Write unit tests for authentication logic
  - _Requirements: 1.1, 1.2_
""",
    }

    def __init__(self):
        """Initialize fallback content provider."""
        pass

    def get_fallback_template(self, template_type: str) -> Optional[str]:
        """Get fallback template content."""
        return self.FALLBACK_TEMPLATES.get(template_type)

    def get_fallback_methodology(self, topic: str) -> Optional[str]:
        """Get fallback methodology content."""
        return self.FALLBACK_METHODOLOGY.get(topic)

    def get_fallback_example(self, example_type: str) -> Optional[str]:
        """Get fallback example content."""
        return self.FALLBACK_EXAMPLES.get(example_type)

    def get_generic_error_guidance(self, error_type: str) -> str:
        """Get generic guidance for common error types."""
        guidance = {
            "validation": """
Validation Error Guidance:
1. Check document format and structure
2. Ensure all required sections are present
3. Verify content follows established patterns
4. Use templates as reference for proper format
""",
            "workflow": """
Workflow Error Guidance:
1. Check current phase status
2. Ensure previous phases are completed and approved
3. Follow the three-phase sequence: Requirements → Design → Tasks
4. Get explicit user approval before phase transitions
""",
            "content": """
Content Access Error Guidance:
1. Verify content type and item name are correct
2. Check if files exist in expected locations
3. Use fallback content if primary sources are unavailable
4. Report persistent content access issues
""",
            "state": """
State Management Error Guidance:
1. Initialize workflow if it doesn't exist
2. Check feature name matches existing workflows
3. Verify state operations are valid for current phase
4. Consider resetting state if corruption is detected
""",
            "task": """
Task Execution Error Guidance:
1. Ensure task dependencies are satisfied
2. Verify task requirements are clear and actionable
3. Check that prerequisite phases are completed
4. Break down complex tasks into smaller steps
""",
        }

        return guidance.get(
            error_type, "No specific guidance available for this error type."
        )

    def get_recovery_steps(self, error_context: Dict[str, Any]) -> list[str]:
        """Get step-by-step recovery instructions based on error context."""
        error_type = error_context.get("error_type", "unknown")

        if error_type == "validation":
            return [
                "1. Review the validation error messages",
                "2. Check the document against the appropriate template",
                "3. Fix formatting and structural issues",
                "4. Re-run validation to confirm fixes",
                "5. Proceed with workflow once validation passes",
            ]
        elif error_type == "workflow":
            return [
                "1. Check current workflow status",
                "2. Complete any pending phase requirements",
                "3. Get user approval for current phase",
                "4. Retry the workflow operation",
                "5. Contact support if issues persist",
            ]
        elif error_type == "content":
            return [
                "1. Verify the requested content type and name",
                "2. Check if content files exist in the data directory",
                "3. Use fallback content if primary sources fail",
                "4. Report missing content to administrators",
                "5. Continue with available content",
            ]
        else:
            return [
                "1. Review the error message and context",
                "2. Check system logs for additional details",
                "3. Try the operation again",
                "4. Use alternative approaches if available",
                "5. Contact support if the problem persists",
            ]

    def get_alternative_approaches(self, failed_operation: str) -> list[str]:
        """Get alternative approaches when primary operations fail."""
        alternatives = {
            "template_access": [
                "Use minimal fallback templates",
                "Create templates manually based on examples",
                "Reference methodology guides for structure",
                "Use previous successful documents as templates",
            ],
            "methodology_access": [
                "Use built-in fallback methodology content",
                "Reference standard spec-driven development practices",
                "Follow the basic three-phase workflow",
                "Consult external documentation resources",
            ],
            "validation": [
                "Perform manual validation using checklists",
                "Use template comparison for structure validation",
                "Focus on critical validation rules first",
                "Proceed with warnings if errors are non-critical",
            ],
            "workflow_transition": [
                "Reset workflow state and restart",
                "Use manual phase tracking",
                "Skip problematic transitions temporarily",
                "Create new workflow instance",
            ],
            "state_management": [
                "Initialize fresh workflow state",
                "Use file-based state backup",
                "Implement manual state tracking",
                "Reset to last known good state",
            ],
        }

        return alternatives.get(
            failed_operation,
            [
                "Try the operation again after a brief delay",
                "Use alternative tools or methods",
                "Implement manual workarounds",
                "Contact system administrators",
            ],
        )
