"""Unit tests for template repository system."""

import pytest
from jinja2 import Environment, TemplateNotFound

from src.mcp_spec_driven_development.content.templates import (
    MemoryTemplateLoader,
    TemplateContext,
    TemplateRepository,
    TemplateType,
)


class TestMemoryTemplateLoader:
    """Test cases for MemoryTemplateLoader."""

    def test_get_source_existing_template(self):
        """Test getting source for existing template."""
        templates = {"test": "Hello {{ name }}"}
        loader = MemoryTemplateLoader(templates)
        env = Environment(loader=loader)

        source, _, _ = loader.get_source(env, "test")
        assert source == "Hello {{ name }}"

    def test_get_source_missing_template(self):
        """Test getting source for missing template raises TemplateNotFound."""
        templates = {"test": "Hello {{ name }}"}
        loader = MemoryTemplateLoader(templates)
        env = Environment(loader=loader)

        with pytest.raises(TemplateNotFound):
            loader.get_source(env, "missing")


class TestTemplateRepository:
    """Test cases for TemplateRepository."""

    @pytest.fixture
    def template_repo(self):
        """Create template repository instance."""
        return TemplateRepository()

    def test_initialization(self, template_repo):
        """Test template repository initialization."""
        assert template_repo is not None
        assert len(template_repo._templates) == 3
        assert TemplateType.REQUIREMENTS.value in template_repo._templates
        assert TemplateType.DESIGN.value in template_repo._templates
        assert TemplateType.TASKS.value in template_repo._templates

    def test_get_template_requirements(self, template_repo):
        """Test getting requirements template."""
        template = template_repo.get_template(TemplateType.REQUIREMENTS)
        assert "# Requirements Document" in template
        assert "## Introduction" in template
        assert "## Requirements" in template
        assert "**User Story:**" in template
        assert "#### Acceptance Criteria" in template

    def test_get_template_design(self, template_repo):
        """Test getting design template."""
        template = template_repo.get_template(TemplateType.DESIGN)
        assert "# Design Document" in template
        assert "## Overview" in template
        assert "## Architecture" in template
        assert "## Components and Interfaces" in template
        assert "## Data Models" in template
        assert "## Error Handling" in template
        assert "## Testing Strategy" in template

    def test_get_template_tasks(self, template_repo):
        """Test getting tasks template."""
        template = template_repo.get_template(TemplateType.TASKS)
        assert "# Implementation Plan" in template
        assert "- [ ]" in template
        assert "_Requirements:" in template

    def test_render_template_basic(self, template_repo):
        """Test basic template rendering."""
        context = {"feature_name": "test-feature"}
        result = template_repo.render_template(TemplateType.REQUIREMENTS, context)
        assert "# Requirements Document" in result

    def test_render_template_invalid_type(self, template_repo):
        """Test rendering with invalid template type."""
        # Use a string that doesn't correspond to any template
        from unittest.mock import Mock

        invalid_type = Mock()
        invalid_type.value = "invalid_template_type"

        with pytest.raises(ValueError, match="Template not found"):
            template_repo.render_template(invalid_type)

    def test_get_requirements_template_default(self, template_repo):
        """Test getting requirements template with default values."""
        result = template_repo.get_requirements_template()
        assert "# Requirements Document" in result
        assert "As a [role], I want [feature], so that [benefit]" in result
        assert "WHEN [event] THEN [system] SHALL [response]" in result
        assert "IF [condition] THEN [system] SHALL [response]" in result

    def test_get_requirements_template_custom(self, template_repo):
        """Test getting requirements template with custom values."""
        requirements = [
            {
                "user_story": "As a developer, I want templates, so that I can create specs",
                "acceptance_criteria": [
                    "WHEN I request a template THEN the system SHALL return formatted content",
                    "WHEN template is invalid THEN the system SHALL return error",
                ],
            }
        ]

        result = template_repo.get_requirements_template(
            feature_name="template-system",
            introduction="Template system for spec creation",
            requirements=requirements,
        )

        assert "Template system for spec creation" in result
        assert "As a developer, I want templates, so that I can create specs" in result
        assert (
            "WHEN I request a template THEN the system SHALL return formatted content"
            in result
        )

    def test_get_design_template_default(self, template_repo):
        """Test getting design template with default values."""
        result = template_repo.get_design_template()
        assert "# Design Document" in result
        assert "## Overview" in result
        assert "```mermaid" in result

    def test_get_design_template_custom(self, template_repo):
        """Test getting design template with custom values."""
        result = template_repo.get_design_template(
            feature_name="test-feature",
            overview="Custom overview",
            architecture="Custom architecture",
            component_name="TestComponent",
            component_purpose="Testing purposes",
        )

        assert "Custom overview" in result
        assert "Custom architecture" in result
        assert "TestComponent" in result
        assert "Testing purposes" in result

    def test_get_tasks_template_default(self, template_repo):
        """Test getting tasks template with default values."""
        result = template_repo.get_tasks_template()
        assert "# Implementation Plan" in result
        assert "- [ ] 1. Set up project structure" in result
        assert "_Requirements: 1.1_" in result

    def test_get_tasks_template_custom(self, template_repo):
        """Test getting tasks template with custom values."""
        tasks = [
            {
                "title": "Create database schema",
                "details": "- Design tables\n  - _Requirements: 2.1_",
            },
            {
                "title": "Implement API endpoints",
                "subtasks": [
                    {
                        "title": "Create user endpoints",
                        "details": "- POST /users\n  - GET /users\n  - _Requirements: 2.2_",
                    }
                ],
            },
        ]

        result = template_repo.get_tasks_template(
            feature_name="api-system", tasks=tasks
        )

        assert "Create database schema" in result
        assert "Implement API endpoints" in result
        assert "Create user endpoints" in result
        assert "POST /users" in result

    def test_validate_template_format_requirements_valid(self, template_repo):
        """Test validating valid requirements format."""
        content = """# Requirements Document

## Introduction
Test intro

## Requirements

### Requirement 1
Test requirement"""

        assert template_repo.validate_template_format(
            TemplateType.REQUIREMENTS, content
        )

    def test_validate_template_format_requirements_invalid(self, template_repo):
        """Test validating invalid requirements format."""
        content = "Invalid content"
        assert not template_repo.validate_template_format(
            TemplateType.REQUIREMENTS, content
        )

    def test_validate_template_format_design_valid(self, template_repo):
        """Test validating valid design format."""
        content = """# Design Document

## Overview
Test overview"""

        assert template_repo.validate_template_format(TemplateType.DESIGN, content)

    def test_validate_template_format_design_invalid(self, template_repo):
        """Test validating invalid design format."""
        content = "Invalid content"
        assert not template_repo.validate_template_format(TemplateType.DESIGN, content)

    def test_validate_template_format_tasks_valid(self, template_repo):
        """Test validating valid tasks format."""
        content = """# Implementation Plan

- [ ] 1. First task
  - Task details"""

        assert template_repo.validate_template_format(TemplateType.TASKS, content)

    def test_validate_template_format_tasks_invalid(self, template_repo):
        """Test validating invalid tasks format."""
        content = "Invalid content"
        assert not template_repo.validate_template_format(TemplateType.TASKS, content)

    def test_template_rendering_with_complex_data(self, template_repo):
        """Test template rendering with complex nested data."""
        requirements = [
            {
                "user_story": "As a user, I want feature A, so that I can do X",
                "acceptance_criteria": [
                    "WHEN condition A THEN system SHALL do Y",
                    "WHEN condition B THEN system SHALL do Z",
                ],
            },
            {
                "user_story": "As an admin, I want feature B, so that I can manage users",
                "acceptance_criteria": [
                    "WHEN admin logs in THEN system SHALL show admin panel",
                    "IF user is unauthorized THEN system SHALL deny access",
                ],
            },
        ]

        result = template_repo.get_requirements_template(
            feature_name="user-management",
            introduction="User management system with role-based access",
            requirements=requirements,
        )

        assert "User management system with role-based access" in result
        assert "As a user, I want feature A, so that I can do X" in result
        assert "As an admin, I want feature B, so that I can manage users" in result
        assert "WHEN condition A THEN system SHALL do Y" in result
        assert "IF user is unauthorized THEN system SHALL deny access" in result
        assert "### Requirement 1" in result
        assert "### Requirement 2" in result
