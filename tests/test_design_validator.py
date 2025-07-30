"""Tests for design validator."""

import pytest

from src.mcp_spec_driven_development.validation.design_validator import (
    DesignSection,
    DesignValidator,
)


class TestDesignValidator:
    """Test cases for DesignValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = DesignValidator()

    def test_valid_design_document(self):
        """Test validation of a properly formatted design document."""
        content = """# Design Document

## Overview

This feature provides user authentication capabilities with secure session management.

## Architecture

```mermaid
graph TB
    UI[User Interface] --> Auth[Authentication Service]
    Auth --> DB[Database]
    Auth --> Session[Session Manager]
```

The architecture follows a layered approach with clear separation of concerns.

## Components and Interfaces

### Authentication Service

**Purpose**: Handles user authentication and authorization

**Key Responsibilities**:
- Validate user credentials
- Generate authentication tokens
- Manage user sessions

**Interface**: REST API with JSON payloads

### Session Manager

**Purpose**: Manages user session lifecycle

**Key Responsibilities**:
- Create and destroy sessions
- Validate session tokens
- Handle session expiration

**Interface**: Internal service interface

## Data Models

User authentication data structures and validation rules.

```python
@dataclass
class User:
    id: str
    email: str
    password_hash: str
```

## Error Handling

Authentication errors are handled gracefully with appropriate user feedback.

### Error Categories
- Invalid credentials: Return 401 with error message
- Session expired: Return 403 with refresh prompt
- System errors: Return 500 with generic message

## Testing Strategy

Comprehensive testing approach covering all authentication scenarios.

### Unit Testing
- Test individual component methods
- Mock external dependencies

### Integration Testing
- Test complete authentication flows
- Validate error handling paths
"""

        results = self.validator.validate(content)

        # Should have no errors for valid document
        errors = [r for r in results if r.type == "error"]
        assert len(errors) == 0

    def test_missing_document_title(self):
        """Test validation of document without title."""
        content = """## Overview

Some content without title.

## Architecture

Architecture content.
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        assert any("title" in r.message.lower() for r in errors)

    def test_missing_required_sections(self):
        """Test validation of document with missing required sections."""
        content = """# Design Document

## Overview

This is just an overview.

## Architecture

Some architecture content.
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        error_messages = [r.message for r in errors]

        # Should have errors for missing required sections
        assert any("Components and Interfaces" in msg for msg in error_messages)
        assert any("Data Models" in msg for msg in error_messages)
        assert any("Error Handling" in msg for msg in error_messages)
        assert any("Testing Strategy" in msg for msg in error_messages)

    def test_empty_required_sections(self):
        """Test validation of document with empty required sections."""
        content = """# Design Document

## Overview

This feature provides authentication.

## Architecture

## Components and Interfaces

## Data Models

## Error Handling

## Testing Strategy
"""

        results = self.validator.validate(content)

        warnings = [r for r in results if r.type == "warning"]
        empty_warnings = [r for r in warnings if "empty" in r.message.lower()]

        # Should have warnings for empty sections
        assert len(empty_warnings) >= 4  # At least 4 empty sections

    def test_heading_hierarchy_validation(self):
        """Test validation of heading hierarchy."""
        content = """# Design Document

## Overview

Content here.

#### Skipped Level

This skips from h2 to h4.

## Architecture

Normal section.
"""

        results = self.validator.validate(content)

        warnings = [r for r in results if r.type == "warning"]
        hierarchy_warnings = [r for r in warnings if "hierarchy" in r.message.lower()]

        assert len(hierarchy_warnings) >= 1

    def test_architecture_section_validation(self):
        """Test validation of architecture section."""
        content = """# Design Document

## Overview

Overview content.

## Architecture

Just text without diagrams.

## Components and Interfaces

### Component A

**Purpose**: Does something

**Key Responsibilities**:
- Task 1
- Task 2

**Interface**: API interface

## Data Models

Data model content.

## Error Handling

Error handling content.

## Testing Strategy

Testing content.
"""

        results = self.validator.validate(content)

        warnings = [r for r in results if r.type == "warning"]
        diagram_warnings = [r for r in warnings if "diagram" in r.message.lower()]

        assert len(diagram_warnings) >= 1

    def test_architecture_with_valid_mermaid(self):
        """Test architecture section with valid Mermaid diagram."""
        content = """# Design Document

## Overview

Overview content.

## Architecture

```mermaid
graph TB
    A[Component A] --> B[Component B]
    B --> C[Component C]
```

This diagram shows the component relationships.

## Components and Interfaces

### Component A

**Purpose**: Main component

**Key Responsibilities**:
- Handle requests
- Process data

**Interface**: REST API

## Data Models

Data models here.

## Error Handling

Error handling here.

## Testing Strategy

Testing strategy here.
"""

        results = self.validator.validate(content)

        # Should not have diagram warnings
        warnings = [r for r in results if r.type == "warning"]
        diagram_warnings = [r for r in warnings if "diagram" in r.message.lower()]

        assert len(diagram_warnings) == 0

    def test_components_section_validation(self):
        """Test validation of components section."""
        content = """# Design Document

## Overview

Overview content.

## Architecture

Architecture with diagram.

```mermaid
graph TB
    A --> B
```

## Components and Interfaces

Just some text without component definitions.

## Data Models

Data models.

## Error Handling

Error handling.

## Testing Strategy

Testing strategy.
"""

        results = self.validator.validate(content)

        warnings = [r for r in results if r.type == "warning"]
        component_warnings = [r for r in warnings if "component" in r.message.lower()]

        assert len(component_warnings) >= 1

    def test_component_missing_details(self):
        """Test validation of component missing required details."""
        content = """# Design Document

## Overview

Overview content.

## Architecture

```mermaid
graph TB
    A --> B
```

## Components and Interfaces

### Component A

Just a component without proper structure.

### Component B

**Purpose**: Has purpose but missing other details

## Data Models

Data models.

## Error Handling

Error handling.

## Testing Strategy

Testing strategy.
"""

        results = self.validator.validate(content)

        warnings = [r for r in results if r.type == "warning"]

        # Should have warnings for missing purpose, responsibilities, interface
        purpose_warnings = [r for r in warnings if "purpose" in r.message.lower()]
        resp_warnings = [r for r in warnings if "responsibilities" in r.message.lower()]
        interface_warnings = [r for r in warnings if "interface" in r.message.lower()]

        assert len(purpose_warnings) >= 1  # Component A missing purpose
        assert len(resp_warnings) >= 2  # Both components missing responsibilities
        assert len(interface_warnings) >= 2  # Both components missing interface

    def test_requirements_traceability_validation(self):
        """Test validation of requirements traceability."""
        design_content = """# Design Document

## Overview

This design addresses user authentication requirements.

_Requirements: 1.1, 2.3_

## Architecture

```mermaid
graph TB
    A --> B
```

_Requirements: 1.2_

## Components and Interfaces

### Auth Service

**Purpose**: Authentication service

**Key Responsibilities**:
- Validate credentials

**Interface**: REST API

_Requirements: 2.1_

## Data Models

User data models.

## Error Handling

Error handling approach.

## Testing Strategy

Testing approach.
"""

        requirements_content = """# Requirements Document

## Introduction

Authentication requirements.

## Requirements

### Requirement 1

**User Story:** As a user, I want to authenticate.

#### Acceptance Criteria

1. WHEN user logs in THEN system SHALL authenticate

### Requirement 2

**User Story:** As a system, I want to manage sessions.

#### Acceptance Criteria

1. WHEN session expires THEN system SHALL prompt re-authentication
"""

        results = self.validator.validate(design_content, requirements_content)

        # Should have warnings for unaddressed requirements and invalid references
        warnings = [r for r in results if r.type == "warning"]
        errors = [r for r in results if r.type == "error"]

        # Check for unaddressed requirements (2 is not referenced)
        unaddressed = [r for r in warnings if "not addressed" in r.message]
        assert len(unaddressed) >= 1

        # Check for invalid references (2.1, 2.3 don't exist)
        invalid_refs = [r for r in errors if "non-existent requirement" in r.message]
        assert len(invalid_refs) >= 2

    def test_no_requirements_traceability(self):
        """Test design without any requirement references."""
        design_content = """# Design Document

## Overview

Design without requirement references.

## Architecture

```mermaid
graph TB
    A --> B
```

## Components and Interfaces

### Component A

**Purpose**: Does something

**Key Responsibilities**:
- Task 1

**Interface**: API

## Data Models

Data models.

## Error Handling

Error handling.

## Testing Strategy

Testing.
"""

        requirements_content = """# Requirements Document

## Requirements

### Requirement 1

**User Story:** As a user, I want something.

#### Acceptance Criteria

1. WHEN user acts THEN system SHALL respond
"""

        results = self.validator.validate(design_content, requirements_content)

        warnings = [r for r in results if r.type == "warning"]
        traceability_warnings = [
            r for r in warnings if "traceability" in r.message.lower()
        ]

        assert len(traceability_warnings) >= 1

    def test_parse_sections(self):
        """Test parsing of design sections."""
        content = """# Design Document

## Overview

Overview content here.

## Architecture

Architecture content here.

## Components and Interfaces

Components content here.
"""

        lines = content.split("\n")
        sections = self.validator._parse_sections(lines)

        assert len(sections) == 3
        assert "Overview" in sections
        assert "Architecture" in sections
        assert "Components and Interfaces" in sections

        assert "Overview content here." in sections["Overview"].content
        assert sections["Overview"].line_start == 3

    def test_extract_requirement_numbers(self):
        """Test extraction of requirement numbers from requirements document."""
        requirements_content = """# Requirements Document

## Requirements

### Requirement 1

Content here.

### Requirement 2

More content.

### Requirement 3.1

Sub-requirement content.
"""

        req_numbers = self.validator._extract_requirement_numbers(requirements_content)

        assert "1" in req_numbers
        assert "2" in req_numbers
        assert "3.1" in req_numbers
        assert len(req_numbers) == 3

    def test_extract_requirement_references(self):
        """Test extraction of requirement references from design document."""
        design_content = """# Design Document

## Overview

This addresses authentication.

_Requirements: 1.1, 2.3_

## Architecture

Architecture details.

_Requirements: 1.2, 3.1_

## Components

Component details.

_Requirements: 2.1_
"""

        refs = self.validator._extract_requirement_references(design_content)

        assert "1.1" in refs
        assert "2.3" in refs
        assert "1.2" in refs
        assert "3.1" in refs
        assert "2.1" in refs
        assert len(refs) == 5

    def test_extract_component_section(self):
        """Test extraction of specific component section content."""
        content = """### Component A

**Purpose**: First component

**Responsibilities**:
- Task 1
- Task 2

### Component B

**Purpose**: Second component

**Responsibilities**:
- Task 3
"""

        comp_a_content = self.validator._extract_component_section(
            content, "Component A"
        )
        comp_b_content = self.validator._extract_component_section(
            content, "Component B"
        )

        assert "**Purpose**: First component" in comp_a_content
        assert "Task 1" in comp_a_content
        assert "Task 2" in comp_a_content
        assert "Second component" not in comp_a_content

        assert "**Purpose**: Second component" in comp_b_content
        assert "Task 3" in comp_b_content
        assert "First component" not in comp_b_content


class TestDesignSection:
    """Test cases for DesignSection dataclass."""

    def test_design_section_creation(self):
        """Test creation of DesignSection."""
        section = DesignSection(
            name="Overview",
            content="This is the overview content.",
            line_start=5,
            line_end=10,
            subsections=[],
        )

        assert section.name == "Overview"
        assert section.content == "This is the overview content."
        assert section.line_start == 5
        assert section.line_end == 10
        assert len(section.subsections) == 0
