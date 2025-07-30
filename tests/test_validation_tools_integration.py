"""Integration tests for validation tools."""

import pytest
from mcp.types import TextContent

from src.mcp_spec_driven_development.tools.validation_tools import ValidationTools


class TestValidationToolsIntegration:
    """Integration tests for validation tools."""

    @pytest.fixture
    def validation_tools(self):
        """Create validation tools instance."""
        return ValidationTools()

    @pytest.mark.asyncio
    async def test_validate_requirements_document_valid(self, validation_tools):
        """Test validating a valid requirements document."""
        content = """# Requirements Document

## Introduction

This feature enables user authentication for the application.

## Requirements

### Requirement 1

**User Story:** As a user, I want to log into the application, so that I can access my personalized content.

#### Acceptance Criteria

1. WHEN user enters valid credentials THEN system SHALL authenticate within 2 seconds
2. IF credentials are invalid THEN system SHALL display error message "Invalid username or password"
"""

        arguments = {
            "document_type": "requirements",
            "content": content,
            "feature_name": "user-authentication",
        }
        result = await validation_tools.handle_validate_document(arguments)

        assert len(result) == 1
        response = result[0].text

        # Check validation passed (may have warnings but no errors)
        assert "**Errors**: 0" in response or "Errors: 0" in response

    @pytest.mark.asyncio
    async def test_validate_requirements_document_invalid(self, validation_tools):
        """Test validating an invalid requirements document."""
        content = """# Requirements Document

## Requirements

### Requirement 1

**User Story:** As a user, I want to use the system

#### Acceptance Criteria

1. System validates user input
2. User can login
"""

        arguments = {"document_type": "requirements", "content": content}
        result = await validation_tools.handle_validate_document(arguments)

        assert len(result) == 1
        response = result[0].text

        # Check validation failed
        assert "❌ Failed" in response or "**Errors**:" in response
        assert "EARS format" in response or "user story" in response

    @pytest.mark.asyncio
    async def test_validate_design_document_valid(self, validation_tools):
        """Test validating a valid design document."""
        content = """# Design Document

## Overview

This feature provides user authentication using JWT tokens and bcrypt for password hashing.

## Architecture

The system uses a layered architecture with API, service, and data layers.

## Components and Interfaces

### AuthService
- Handles user authentication
- Manages JWT tokens

## Data Models

```python
class User:
    id: str
    username: str
    password_hash: str
```

## Error Handling

Authentication errors return appropriate HTTP status codes with descriptive messages.

## Testing Strategy

Unit tests for authentication logic, integration tests for API endpoints.
"""

        arguments = {"document_type": "design", "content": content}
        result = await validation_tools.handle_validate_document(arguments)

        assert len(result) == 1
        response = result[0].text

        # Check validation passed
        assert "**Errors**: 0" in response

    @pytest.mark.asyncio
    async def test_validate_tasks_document_valid(self, validation_tools):
        """Test validating a valid tasks document."""
        content = """# Implementation Plan

- [ ] 1. Set up authentication project structure
  - Create directory structure for auth components
  - Set up dependency injection for services
  - _Requirements: 1.1_

- [ ] 2. Implement user authentication
- [ ] 2.1 Create User model with validation
  - Implement User class with password hashing
  - Add validation methods for user data
  - Write unit tests for User model
  - _Requirements: 1.1, 1.2_

- [ ] 2.2 Build authentication service
  - Implement AuthService with login/logout methods
  - Add JWT token generation and validation
  - Write unit tests for authentication logic
  - _Requirements: 1.2, 1.3_
"""

        arguments = {"document_type": "tasks", "content": content}
        result = await validation_tools.handle_validate_document(arguments)

        assert len(result) == 1
        response = result[0].text

        # Check validation is working (should have validation results)
        assert "Validation Results" in response

    @pytest.mark.asyncio
    async def test_validate_document_invalid_type(self, validation_tools):
        """Test validating document with invalid type."""
        arguments = {"document_type": "invalid_type", "content": "some content"}
        result = await validation_tools.handle_validate_document(arguments)

        assert len(result) == 1
        assert "Invalid document type" in result[0].text

    @pytest.mark.asyncio
    async def test_get_validation_checklist_requirements(self, validation_tools):
        """Test getting validation checklist for requirements."""
        arguments = {"document_type": "requirements"}
        result = await validation_tools.handle_get_validation_checklist(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check checklist content
        assert "Requirements Document Validation Checklist" in content
        assert "Document Structure" in content
        assert "User Stories" in content
        assert "Acceptance Criteria" in content
        assert "EARS format" in content
        assert "- [ ]" in content  # Checkbox format

    @pytest.mark.asyncio
    async def test_get_validation_checklist_design(self, validation_tools):
        """Test getting validation checklist for design."""
        arguments = {"document_type": "design"}
        result = await validation_tools.handle_get_validation_checklist(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check checklist content
        assert "Design Document Validation Checklist" in content
        assert "Overview Section" in content
        assert "Architecture Section" in content
        assert "Components and Interfaces" in content
        assert "Data Models" in content
        assert "Error Handling" in content
        assert "Testing Strategy" in content

    @pytest.mark.asyncio
    async def test_get_validation_checklist_tasks(self, validation_tools):
        """Test getting validation checklist for tasks."""
        arguments = {"document_type": "tasks"}
        result = await validation_tools.handle_get_validation_checklist(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check checklist content
        assert "Tasks Document Validation Checklist" in content
        assert "Task Format" in content
        assert "Requirement Traceability" in content
        assert "Task Dependencies" in content
        assert "Implementation Strategy" in content

    @pytest.mark.asyncio
    async def test_get_validation_checklist_invalid_type(self, validation_tools):
        """Test getting validation checklist for invalid type."""
        arguments = {"document_type": "invalid"}
        result = await validation_tools.handle_get_validation_checklist(arguments)

        assert len(result) == 1
        assert "Invalid document type" in result[0].text

    @pytest.mark.asyncio
    async def test_explain_validation_error_ears_format(self, validation_tools):
        """Test explaining EARS format validation error."""
        arguments = {"error_type": "ears_format", "document_type": "requirements"}
        result = await validation_tools.handle_explain_validation_error(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check explanation content
        assert "EARS Format Error Explanation" in content
        assert "Easy Approach to Requirements Syntax" in content
        assert "WHEN" in content
        assert "THEN" in content
        assert "SHALL" in content
        assert "Common Mistakes" in content
        assert "How to Fix" in content

    @pytest.mark.asyncio
    async def test_explain_validation_error_user_story(self, validation_tools):
        """Test explaining user story format error."""
        arguments = {"error_type": "user_story_format", "document_type": "requirements"}
        result = await validation_tools.handle_explain_validation_error(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check explanation content
        assert "User Story Format Error Explanation" in content
        assert "As a [role], I want [feature], so that [benefit]" in content
        assert "Common Mistakes" in content
        assert "How to Fix" in content

    @pytest.mark.asyncio
    async def test_explain_validation_error_not_found(self, validation_tools):
        """Test explaining validation error that doesn't exist."""
        arguments = {"error_type": "nonexistent_error", "document_type": "requirements"}
        result = await validation_tools.handle_explain_validation_error(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check error explanation not found
        assert "Error Explanation Not Found" in content
        assert "Available Explanations" in content

    @pytest.mark.asyncio
    async def test_validate_requirement_traceability_basic(self, validation_tools):
        """Test basic requirement traceability validation."""
        requirements_content = """# Requirements Document

## Requirements

### Requirement 1

**User Story:** As a user, I want to authenticate, so that I can access the system.

### Requirement 2

**User Story:** As an admin, I want to manage users, so that I can control access.
"""

        arguments = {"requirements_content": requirements_content}
        result = await validation_tools.handle_validate_requirement_traceability(
            arguments
        )

        assert len(result) == 1
        content = result[0].text

        # Check traceability analysis
        assert "Requirement Traceability Analysis" in content
        assert "Requirements Found" in content
        assert "Total requirements identified: 2" in content
        assert "Requirement 1" in content
        assert "Requirement 2" in content

    @pytest.mark.asyncio
    async def test_validate_requirement_traceability_with_design(
        self, validation_tools
    ):
        """Test requirement traceability with design document."""
        requirements_content = """# Requirements Document

## Requirements

### Requirement 1

**User Story:** As a user, I want to authenticate, so that I can access the system.
"""

        design_content = """# Design Document

## Overview

This design addresses requirement 1 for user authentication.

## Components

The AuthService component handles requirement 1 implementation.
"""

        arguments = {
            "requirements_content": requirements_content,
            "design_content": design_content,
        }
        result = await validation_tools.handle_validate_requirement_traceability(
            arguments
        )

        assert len(result) == 1
        content = result[0].text

        # Check design coverage
        assert "Design Coverage" in content
        assert "Requirement 1: ✅ Addressed" in content

    @pytest.mark.asyncio
    async def test_validate_requirement_traceability_with_tasks(self, validation_tools):
        """Test requirement traceability with tasks document."""
        requirements_content = """# Requirements Document

## Requirements

### Requirement 1

**User Story:** As a user, I want to authenticate, so that I can access the system.

### Requirement 2

**User Story:** As an admin, I want to manage users, so that I can control access.
"""

        tasks_content = """# Implementation Plan

- [ ] 1. Implement authentication
  - Create login functionality
  - _Requirements: 1_

- [ ] 2. Create user management
  - Add admin interface
  - _Requirements: 2_
"""

        arguments = {
            "requirements_content": requirements_content,
            "tasks_content": tasks_content,
        }
        result = await validation_tools.handle_validate_requirement_traceability(
            arguments
        )

        assert len(result) == 1
        content = result[0].text

        # Check task coverage
        assert "Task Coverage" in content
        assert "Requirement 1: ✅ Referenced" in content
        assert "Requirement 2: ✅ Referenced" in content

    @pytest.mark.asyncio
    async def test_validate_requirement_traceability_orphaned_references(
        self, validation_tools
    ):
        """Test detecting orphaned task references."""
        requirements_content = """# Requirements Document

## Requirements

### Requirement 1

**User Story:** As a user, I want to authenticate, so that I can access the system.
"""

        tasks_content = """# Implementation Plan

- [ ] 1. Implement authentication
  - Create login functionality
  - _Requirements: 1, 2, 3_
"""

        arguments = {
            "requirements_content": requirements_content,
            "tasks_content": tasks_content,
        }
        result = await validation_tools.handle_validate_requirement_traceability(
            arguments
        )

        assert len(result) == 1
        content = result[0].text

        # Check orphaned references
        assert "⚠️ Orphaned Task References" in content
        assert "2" in content
        assert "3" in content

    @pytest.mark.asyncio
    async def test_validate_requirement_traceability_complete_analysis(
        self, validation_tools
    ):
        """Test complete traceability analysis with all documents."""
        requirements_content = """# Requirements Document

## Requirements

### Requirement 1

**User Story:** As a user, I want to authenticate, so that I can access the system.

### Requirement 2

**User Story:** As an admin, I want to manage users, so that I can control access.
"""

        design_content = """# Design Document

## Overview

This design addresses requirement 1 for authentication but not requirement 2.
"""

        tasks_content = """# Implementation Plan

- [ ] 1. Implement authentication
  - _Requirements: 1_
"""

        arguments = {
            "requirements_content": requirements_content,
            "design_content": design_content,
            "tasks_content": tasks_content,
        }
        result = await validation_tools.handle_validate_requirement_traceability(
            arguments
        )

        assert len(result) == 1
        content = result[0].text

        # Check complete analysis
        assert "Design Coverage" in content
        assert "Task Coverage" in content
        assert "Summary" in content
        assert "Traceability issues found" in content
        assert (
            "not addressed in design" in content or "not referenced in tasks" in content
        )

    def test_tool_definitions(self, validation_tools):
        """Test that tool definitions are properly structured."""
        tools = validation_tools.get_tool_definitions()

        assert len(tools) == 4

        tool_names = [tool.name for tool in tools]
        expected_names = [
            "validate_document",
            "get_validation_checklist",
            "explain_validation_error",
            "validate_requirement_traceability",
        ]

        for name in expected_names:
            assert name in tool_names

        # Check that all tools have required properties
        for tool in tools:
            assert tool.name
            assert tool.description
            assert tool.inputSchema
            assert "type" in tool.inputSchema
            assert "properties" in tool.inputSchema
            assert "required" in tool.inputSchema

    @pytest.mark.asyncio
    async def test_handle_unknown_tool(self, validation_tools):
        """Test handling unknown tool call."""
        result = await validation_tools.handle_tool_call("unknown_tool", {})

        assert len(result) == 1
        assert "Unknown tool" in result[0].text
