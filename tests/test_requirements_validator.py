"""Tests for requirements validator."""

import pytest

from src.mcp_spec_driven_development.validation.requirements_validator import (
    RequirementSection,
    RequirementsValidator,
)


class TestRequirementsValidator:
    """Test cases for RequirementsValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = RequirementsValidator()

    def test_valid_requirements_document(self):
        """Test validation of a properly formatted requirements document."""
        content = """# Requirements Document

## Introduction

This feature enables users to authenticate with the system.

## Requirements

### Requirement 1

**User Story:** As a registered user, I want to log into the system, so that I can access my personal data.

#### Acceptance Criteria

1. WHEN user enters valid credentials THEN system SHALL grant access within 2 seconds
2. IF user enters invalid credentials THEN system SHALL display error message
3. WHILE authentication is in progress THEN system SHALL show loading indicator

### Requirement 2

**User Story:** As an administrator, I want to manage user accounts, so that I can maintain system security.

#### Acceptance Criteria

1. WHERE admin panel THEN system SHALL display user management interface
2. WHEN admin deletes user THEN system SHALL remove user data permanently
"""

        results = self.validator.validate(content)

        # Should have no errors for valid document
        errors = [r for r in results if r.type == "error"]
        assert len(errors) == 0

    def test_missing_document_structure(self):
        """Test validation of document with missing required sections."""
        content = """Some content without proper structure"""

        results = self.validator.validate(content)

        # Should have errors for missing title, introduction, and requirements
        error_messages = [r.message for r in results if r.type == "error"]
        assert any("title" in msg.lower() for msg in error_messages)
        assert any("introduction" in msg.lower() for msg in error_messages)
        assert any("requirements" in msg.lower() for msg in error_messages)

    def test_missing_user_story(self):
        """Test validation of requirement without user story."""
        content = """# Requirements Document

## Introduction

Test document.

## Requirements

### Requirement 1

#### Acceptance Criteria

1. WHEN user clicks button THEN system SHALL respond
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        assert any("missing a user story" in r.message for r in errors)

    def test_invalid_user_story_format(self):
        """Test validation of incorrectly formatted user story."""
        content = """# Requirements Document

## Introduction

Test document.

## Requirements

### Requirement 1

**User Story:** I want to login to the system.

#### Acceptance Criteria

1. WHEN user enters credentials THEN system SHALL authenticate
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        assert any("does not follow the required format" in r.message for r in errors)

    def test_generic_user_role_warning(self):
        """Test warning for generic user role."""
        content = """# Requirements Document

## Introduction

Test document.

## Requirements

### Requirement 1

**User Story:** As a user, I want to login, so that I can access the system.

#### Acceptance Criteria

1. WHEN user enters credentials THEN system SHALL authenticate
"""

        results = self.validator.validate(content)

        warnings = [r for r in results if r.type == "warning"]
        assert any('generic "user" role' in r.message for r in warnings)

    def test_missing_acceptance_criteria(self):
        """Test validation of requirement without acceptance criteria."""
        content = """# Requirements Document

## Introduction

Test document.

## Requirements

### Requirement 1

**User Story:** As a developer, I want to test the system, so that I can ensure quality.
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        assert any("has no acceptance criteria" in r.message for r in errors)

    def test_non_ears_format_criteria(self):
        """Test validation of acceptance criteria not in EARS format."""
        content = """# Requirements Document

## Introduction

Test document.

## Requirements

### Requirement 1

**User Story:** As a developer, I want to test the system, so that I can ensure quality.

#### Acceptance Criteria

1. The system should be fast
2. Users can login easily
3. WHEN user clicks button THEN system SHALL respond
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        ears_errors = [r for r in errors if "does not follow EARS format" in r.message]
        assert len(ears_errors) == 2  # First two criteria are not EARS format

    def test_missing_shall_in_criteria(self):
        """Test validation of acceptance criteria missing SHALL."""
        content = """# Requirements Document

## Introduction

Test document.

## Requirements

### Requirement 1

**User Story:** As a developer, I want to test the system, so that I can ensure quality.

#### Acceptance Criteria

1. WHEN user clicks button THEN system responds
2. IF condition is met THEN system SHALL act
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        shall_errors = [r for r in errors if 'missing "SHALL"' in r.message]
        assert len(shall_errors) == 1  # First criterion missing SHALL

    def test_vague_language_warning(self):
        """Test warning for vague language in acceptance criteria."""
        content = """# Requirements Document

## Introduction

Test document.

## Requirements

### Requirement 1

**User Story:** As a developer, I want to test the system, so that I can ensure quality.

#### Acceptance Criteria

1. WHEN user interacts THEN system SHALL be user-friendly
2. IF load increases THEN system SHALL be fast
3. WHEN user clicks THEN system SHALL respond efficiently
"""

        results = self.validator.validate(content)

        warnings = [r for r in results if r.type == "warning"]
        vague_warnings = [r for r in warnings if "vague term" in r.message]
        assert len(vague_warnings) == 3  # All three have vague terms

    def test_requirement_numbering_validation(self):
        """Test validation of requirement numbering."""
        content = """# Requirements Document

## Introduction

Test document.

## Requirements

### Requirement 1

**User Story:** As a developer, I want to test, so that I can ensure quality.

#### Acceptance Criteria

1. WHEN user acts THEN system SHALL respond

### Requirement 3

**User Story:** As a user, I want to use the system, so that I can get value.

#### Acceptance Criteria

1. WHEN user acts THEN system SHALL respond

### Requirement 2

**User Story:** As an admin, I want to manage, so that I can control access.

#### Acceptance Criteria

1. WHEN admin acts THEN system SHALL respond
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        numbering_errors = [r for r in errors if "numbering error" in r.message]
        assert len(numbering_errors) == 2  # Requirements 3 and 2 are out of order

    def test_duplicate_requirement_numbers(self):
        """Test validation of duplicate requirement numbers."""
        content = """# Requirements Document

## Introduction

Test document.

## Requirements

### Requirement 1

**User Story:** As a developer, I want to test, so that I can ensure quality.

#### Acceptance Criteria

1. WHEN user acts THEN system SHALL respond

### Requirement 1

**User Story:** As a user, I want to use the system, so that I can get value.

#### Acceptance Criteria

1. WHEN user acts THEN system SHALL respond
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        duplicate_errors = [
            r for r in errors if "Duplicate requirement number" in r.message
        ]
        assert len(duplicate_errors) == 1

    def test_ears_pattern_variations(self):
        """Test validation of different EARS pattern variations."""
        content = """# Requirements Document

## Introduction

Test document.

## Requirements

### Requirement 1

**User Story:** As a developer, I want to test patterns, so that I can validate EARS.

#### Acceptance Criteria

1. WHEN user clicks button THEN system SHALL respond immediately
2. IF user is authenticated THEN system SHALL grant access
3. WHILE process is running THEN system SHALL show progress
4. WHERE admin panel THEN system SHALL display controls
5. WHEN user submits AND data is valid THEN system SHALL save record
6. IF user is NOT authenticated THEN system SHALL deny access
"""

        results = self.validator.validate(content)

        # All criteria should be valid EARS format
        errors = [
            r for r in results if r.type == "error" and "EARS format" in r.message
        ]
        assert len(errors) == 0

    def test_parse_requirements_sections(self):
        """Test parsing of requirement sections."""
        content = """# Requirements Document

## Introduction

Test document.

## Requirements

### Requirement 1

**User Story:** As a developer, I want to test, so that I can ensure quality.

#### Acceptance Criteria

1. WHEN user acts THEN system SHALL respond
2. IF condition is met THEN system SHALL act

### Requirement 2

**User Story:** As a user, I want to use the system, so that I can get value.

#### Acceptance Criteria

1. WHERE interface THEN system SHALL display data
"""

        lines = content.split("\n")
        requirements = self.validator._parse_requirements(lines)

        assert len(requirements) == 2
        assert requirements[0].number == "1"
        assert requirements[1].number == "2"
        assert len(requirements[0].acceptance_criteria) == 2
        assert len(requirements[1].acceptance_criteria) == 1
        assert "As a developer" in requirements[0].user_story
        assert "As a user" in requirements[1].user_story

    def test_empty_requirements_section(self):
        """Test validation of document with empty requirements section."""
        content = """# Requirements Document

## Introduction

Test document.

## Requirements

"""

        results = self.validator.validate(content)

        # Should not crash, but may have warnings about empty section
        assert isinstance(results, list)

    def test_case_insensitive_ears_validation(self):
        """Test that EARS validation is case insensitive."""
        content = """# Requirements Document

## Introduction

Test document.

## Requirements

### Requirement 1

**User Story:** As a developer, I want to test case sensitivity, so that I can validate patterns.

#### Acceptance Criteria

1. when user clicks button then system shall respond
2. IF USER IS AUTHENTICATED THEN SYSTEM SHALL GRANT ACCESS
3. While Process Is Running Then System Shall Show Progress
"""

        results = self.validator.validate(content)

        # All criteria should be valid despite different cases
        ears_errors = [
            r for r in results if r.type == "error" and "EARS format" in r.message
        ]
        assert len(ears_errors) == 0


class TestRequirementSection:
    """Test cases for RequirementSection dataclass."""

    def test_requirement_section_creation(self):
        """Test creation of RequirementSection."""
        req = RequirementSection(
            number="1",
            user_story="As a user, I want to test, so that I can validate.",
            acceptance_criteria=["WHEN user acts THEN system SHALL respond"],
            line_start=10,
            line_end=15,
        )

        assert req.number == "1"
        assert "As a user" in req.user_story
        assert len(req.acceptance_criteria) == 1
        assert req.line_start == 10
        assert req.line_end == 15
