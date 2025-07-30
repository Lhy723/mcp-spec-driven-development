"""Tests for task validator."""

import pytest

from src.mcp_spec_driven_development.validation.task_validator import (
    TaskItem,
    TaskValidator,
)


class TestTaskValidator:
    """Test cases for TaskValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = TaskValidator()

    def test_valid_task_document(self):
        """Test validation of a properly formatted task document."""
        content = """# Implementation Plan

- [ ] 1. Set up project structure and core interfaces
  - Create directory structure for authentication components
  - Initialize Python project configuration
  - Define core interfaces and types
  - _Requirements: 1.1, 2.4_

- [ ] 2. Implement authentication service
  - _Requirements: 2.0_
- [ ] 2.1 Create user model with validation
  - Write User class with email and password fields
  - Implement validation methods for data integrity
  - Add password hashing functionality
  - Write unit tests for User model
  - _Requirements: 1.2, 2.1_

- [ ] 2.2 Build authentication API endpoints
  - Create POST /login endpoint for user authentication
  - Implement JWT token generation and validation
  - Add error handling for invalid credentials
  - Write integration tests for authentication flow
  - _Requirements: 1.3, 2.2_

- [ ] 3. Create comprehensive test suite
  - Write unit tests for all authentication components
  - Implement integration tests for complete workflows
  - Add error scenario testing
  - _Requirements: 3.1, 3.2_
"""

        results = self.validator.validate(content)

        # Should have no errors for valid document
        errors = [r for r in results if r.type == "error"]
        assert len(errors) == 0

    def test_missing_document_title(self):
        """Test validation of document without title."""
        content = """- [ ] 1. Some task
  - Task details
  - _Requirements: 1.1_
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        assert any("title" in r.message.lower() for r in errors)

    def test_no_tasks_in_document(self):
        """Test validation of document without tasks."""
        content = """# Implementation Plan

This document has no tasks.
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        assert any("at least one task" in r.message.lower() for r in errors)

    def test_non_coding_task_detection(self):
        """Test detection of non-coding tasks."""
        content = """# Implementation Plan

- [ ] 1. Conduct user testing sessions
  - Gather user feedback on interface
  - Analyze usage patterns
  - _Requirements: 1.1_

- [ ] 2. Deploy to production environment
  - Set up production servers
  - Configure deployment pipeline
  - _Requirements: 2.1_

- [ ] 3. Create user training materials
  - Write user documentation
  - Prepare training videos
  - _Requirements: 3.1_
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        non_coding_errors = [r for r in errors if "non-coding activity" in r.message]

        # Should detect multiple non-coding activities
        assert len(non_coding_errors) >= 3

    def test_missing_requirements_reference(self):
        """Test detection of tasks without requirements references."""
        content = """# Implementation Plan

- [ ] 1. Implement user authentication
  - Create login functionality
  - Add password validation

- [ ] 2. Build user interface
  - Create login form
  - Add styling
  - _Requirements: 2.1_
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        req_errors = [
            r for r in errors if "missing requirements reference" in r.message
        ]

        assert len(req_errors) == 1  # Task 1 missing requirements

    def test_invalid_requirements_reference_format(self):
        """Test detection of invalid requirement reference formats."""
        content = """# Implementation Plan

- [ ] 1. Implement authentication
  - Create login system
  - _Requirements: user auth, security_

- [ ] 2. Build interface
  - Create forms
  - _Requirements: 2.1, invalid-ref_
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        format_errors = [
            r for r in errors if "invalid requirement reference format" in r.message
        ]

        assert len(format_errors) >= 2  # Multiple invalid formats

    def test_vague_language_detection(self):
        """Test detection of vague language in tasks."""
        content = """# Implementation Plan

- [ ] 1. Set up the system properly
  - Make it work correctly
  - Add security features
  - _Requirements: 1.1_

- [ ] 2. Implement user management
  - Handle errors appropriately
  - Optimize performance
  - _Requirements: 2.1_
"""

        results = self.validator.validate(content)

        warnings = [r for r in results if r.type == "warning"]
        vague_warnings = [r for r in warnings if "vague language" in r.message]

        assert len(vague_warnings) >= 3  # Multiple vague terms detected

    def test_missing_actionable_verbs(self):
        """Test detection of tasks without actionable verbs."""
        content = """# Implementation Plan

- [ ] 1. User authentication system
  - Login functionality
  - Password validation
  - _Requirements: 1.1_

- [ ] 2. Database connection
  - Data storage
  - Query operations
  - _Requirements: 2.1_
"""

        results = self.validator.validate(content)

        warnings = [r for r in results if r.type == "warning"]
        verb_warnings = [r for r in warnings if "actionable coding verbs" in r.message]

        assert len(verb_warnings) >= 2  # Both tasks lack action verbs

    def test_task_numbering_validation(self):
        """Test validation of task numbering."""
        content = """# Implementation Plan

- [ ] 1. First task
  - Task details
  - _Requirements: 1.1_

- [ ] 3. Third task (skipped 2)
  - Task details
  - _Requirements: 2.1_

- [ ] 2. Second task (out of order)
  - Task details
  - _Requirements: 3.1_
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        numbering_errors = [r for r in errors if "numbering error" in r.message]

        assert len(numbering_errors) >= 2  # Tasks 3 and 2 are incorrectly numbered

    def test_subtask_numbering_validation(self):
        """Test validation of subtask numbering."""
        content = """# Implementation Plan

- [ ] 1. Main task
  - Main task details
  - _Requirements: 1.1_

- [ ] 1.1 First subtask
  - Subtask details
  - _Requirements: 1.2_

- [ ] 1.3 Third subtask (skipped 1.2)
  - Subtask details
  - _Requirements: 1.3_

- [ ] 2. Second main task
  - Main task details
  - _Requirements: 2.1_

- [ ] 2.1 Subtask of second main
  - Subtask details
  - _Requirements: 2.2_
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        subtask_errors = [r for r in errors if "Subtask numbering error" in r.message]

        assert len(subtask_errors) >= 1  # Subtask 1.3 should be 1.2

    def test_orphaned_subtask_detection(self):
        """Test detection of subtasks without parent tasks."""
        content = """# Implementation Plan

- [ ] 1. First task
  - Task details
  - _Requirements: 1.1_

- [ ] 2.1 Subtask without parent 2
  - Orphaned subtask
  - _Requirements: 2.1_

- [ ] 3.1 Another orphaned subtask
  - No parent task 3
  - _Requirements: 3.1_
"""

        results = self.validator.validate(content)

        errors = [r for r in results if r.type == "error"]
        orphan_errors = [
            r for r in errors if "no corresponding parent task" in r.message
        ]

        assert len(orphan_errors) == 2  # Both subtasks are orphaned

    def test_missing_implementation_details(self):
        """Test detection of tasks without implementation details."""
        content = """# Implementation Plan

- [ ] 1. Implement authentication
  - _Requirements: 1.1_

- [ ] 2. Build user interface
  - Create login form
  - Add validation
  - _Requirements: 2.1_
"""

        results = self.validator.validate(content)

        warnings = [r for r in results if r.type == "warning"]
        detail_warnings = [
            r for r in warnings if "lacks implementation details" in r.message
        ]

        assert len(detail_warnings) == 1  # Task 1 has no details

    def test_brief_task_title_warning(self):
        """Test warning for brief task titles."""
        content = """# Implementation Plan

- [ ] 1. Auth
  - Implement authentication
  - _Requirements: 1.1_

- [ ] 2. UI
  - Build interface
  - _Requirements: 2.1_

- [ ] 3. Implement comprehensive user authentication system
  - Create detailed login functionality
  - _Requirements: 3.1_
"""

        results = self.validator.validate(content)

        warnings = [r for r in results if r.type == "warning"]
        brief_warnings = [r for r in warnings if "title may be too brief" in r.message]

        assert len(brief_warnings) == 2  # Tasks 1 and 2 have brief titles

    def test_task_specificity_validation(self):
        """Test validation of task specificity."""
        content = """# Implementation Plan

- [ ] 1. Do some work
  - Make things happen
  - _Requirements: 1.1_

- [ ] 2. Create UserService class with authentication methods
  - Implement login() method with email validation
  - Add password hashing using bcrypt
  - Write unit tests for UserService methods
  - _Requirements: 2.1_
"""

        results = self.validator.validate(content)

        info_results = [r for r in results if r.type == "info"]
        specificity_info = [
            r
            for r in info_results
            if "more specific about implementation targets" in r.message
        ]

        assert len(specificity_info) == 1  # Task 1 lacks specifics

    def test_testing_task_validation(self):
        """Test validation of testing task presence."""
        content = """# Implementation Plan

- [ ] 1. Implement authentication
  - Create login system
  - Add password validation
  - _Requirements: 1.1_

- [ ] 2. Build user interface
  - Create forms
  - Add styling
  - _Requirements: 2.1_
"""

        results = self.validator.validate(content)

        warnings = [r for r in results if r.type == "warning"]
        testing_warnings = [r for r in warnings if "lacks testing tasks" in r.message]

        assert len(testing_warnings) >= 1

    def test_setup_task_recommendation(self):
        """Test recommendation for setup/foundation tasks."""
        content = """# Implementation Plan

- [ ] 1. Build complex feature
  - Implement advanced functionality
  - _Requirements: 1.1_

- [ ] 2. Add more features
  - Create additional components
  - _Requirements: 2.1_
"""

        results = self.validator.validate(content)

        info_results = [r for r in results if r.type == "info"]
        setup_info = [r for r in info_results if "setup/foundation tasks" in r.message]

        assert len(setup_info) >= 1

    def test_requirements_traceability_validation(self):
        """Test validation of requirements traceability."""
        task_content = """# Implementation Plan

- [ ] 1. Implement authentication
  - Create login system
  - _Requirements: 1.1, 2.3_

- [ ] 2. Build interface
  - Create forms
  - _Requirements: 1.2, 3.1_
"""

        requirements_content = """# Requirements Document

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

        results = self.validator.validate(task_content, requirements_content)

        # Should have warnings for uncovered requirements and errors for invalid references
        warnings = [r for r in results if r.type == "warning"]
        errors = [r for r in results if r.type == "error"]

        uncovered = [r for r in warnings if "not covered by any task" in r.message]
        invalid_refs = [r for r in errors if "non-existent requirement" in r.message]

        assert len(uncovered) >= 1  # Requirement 2 not covered
        assert len(invalid_refs) >= 2  # References 2.3 and 3.1 don't exist

    def test_parse_tasks(self):
        """Test parsing of task items."""
        content = """# Implementation Plan

- [ ] 1. Main task
  - Main task detail
  - _Requirements: 1.1_

- [ ] 1.1 Subtask
  - Subtask detail
  - _Requirements: 1.2_

- [x] 2. Completed task
  - Completed task detail
  - _Requirements: 2.1_
"""

        lines = content.split("\n")
        tasks = self.validator._parse_tasks(lines)

        assert len(tasks) == 3

        # Check main task
        main_task = tasks[0]
        assert main_task.number == "1"
        assert main_task.title == "Main task"
        assert not main_task.is_subtask
        assert main_task.parent_task is None
        assert "1.1" in main_task.requirements_refs

        # Check subtask
        subtask = tasks[1]
        assert subtask.number == "1.1"
        assert subtask.title == "Subtask"
        assert subtask.is_subtask
        assert subtask.parent_task == "1"
        assert "1.2" in subtask.requirements_refs

        # Check completed task
        completed_task = tasks[2]
        assert completed_task.number == "2"
        assert completed_task.title == "Completed task"
        assert not completed_task.is_subtask

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


class TestTaskItem:
    """Test cases for TaskItem dataclass."""

    def test_task_item_creation(self):
        """Test creation of TaskItem."""
        task = TaskItem(
            number="1.1",
            title="Implement authentication",
            details=["Create login system", "Add validation"],
            requirements_refs=["1.1", "2.3"],
            line_start=5,
            line_end=10,
            is_subtask=True,
            parent_task="1",
        )

        assert task.number == "1.1"
        assert task.title == "Implement authentication"
        assert len(task.details) == 2
        assert len(task.requirements_refs) == 2
        assert task.is_subtask
        assert task.parent_task == "1"
