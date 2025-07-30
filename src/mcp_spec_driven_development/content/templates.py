"""Template repository system for spec-driven development documents."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Optional

import jinja2
from jinja2 import BaseLoader, Environment, TemplateNotFound


class TemplateType(Enum):
    """Supported template types."""

    REQUIREMENTS = "requirements"
    DESIGN = "design"
    TASKS = "tasks"


@dataclass
class TemplateContext:
    """Context data for template rendering."""

    feature_name: str
    additional_data: Optional[Dict[str, Any]] = None


class MemoryTemplateLoader(BaseLoader):
    """In-memory template loader for Jinja2."""

    def __init__(self, templates: Dict[str, str]):
        self.templates = templates

    def get_source(
        self, environment: Environment, template: str
    ) -> tuple[str, None, None]:
        """Get template source."""
        if template not in self.templates:
            raise TemplateNotFound(template)
        source = self.templates[template]
        return source, None, None


class TemplateRepository:
    """Repository for managing spec document templates."""

    def __init__(self):
        """Initialize template repository with built-in templates."""
        self._templates = self._load_builtin_templates()
        self._env = Environment(
            loader=MemoryTemplateLoader(self._templates),
            autoescape=False,
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _load_builtin_templates(self) -> Dict[str, str]:
        """Load built-in templates for each document type."""
        templates = {}

        # Load English templates
        templates[TemplateType.REQUIREMENTS.value] = self._load_template_file(
            "requirements-template.md"
        )
        templates[TemplateType.DESIGN.value] = self._load_template_file(
            "design-template.md"
        )
        templates[TemplateType.TASKS.value] = self._load_template_file(
            "tasks-template.md"
        )

        # Load Chinese templates
        templates[f"{TemplateType.REQUIREMENTS.value}-zh"] = self._load_template_file(
            "requirements-template-zh.md"
        )
        templates[f"{TemplateType.DESIGN.value}-zh"] = self._load_template_file(
            "design-template-zh.md"
        )
        templates[f"{TemplateType.TASKS.value}-zh"] = self._load_template_file(
            "tasks-template-zh.md"
        )

        return templates

    def _get_requirements_template(self) -> str:
        """Get EARS format requirements template."""
        return """# Requirements Document

## Introduction

{{ introduction | default("This feature enables [brief description of the feature and its purpose].") }}

## Requirements

{% for requirement in requirements %}
### Requirement {{ loop.index }}

**User Story:** {{ requirement.user_story | default("As a [role], I want [feature], so that [benefit]") }}

#### Acceptance Criteria

{% for criteria in requirement.acceptance_criteria %}
{{ loop.index }}. {{ criteria | default("WHEN [event] THEN [system] SHALL [response]") }}
{% endfor %}

{% endfor %}"""

    def _get_design_template(self) -> str:
        """Get design document structure template."""
        return """# Design Document

## Overview

{{ overview | default("[Provide a comprehensive overview of the feature design, including technology stack and architectural approach]") }}

## Architecture

{{ architecture | default("[Describe the high-level architecture with diagrams if applicable]") }}

```mermaid
graph TB
    {{ mermaid_diagram | default("A[Component A] --> B[Component B]") }}
```

## Components and Interfaces

{{ components | default("[Detail the key components and their interfaces]") }}

### {{ component_name | default("Component Name") }}

**Purpose**: {{ component_purpose | default("[Component purpose and responsibilities]") }}

**Key Responsibilities**:
{{ component_responsibilities | default("- [Responsibility 1]\n- [Responsibility 2]") }}

**Interface**: {{ component_interface | default("[Interface description]") }}

## Data Models

{{ data_models | default("[Define the data structures and models used]") }}

```python
{{ data_model_code | default("# Data model definitions") }}
```

## Error Handling

{{ error_handling | default("[Describe error handling strategies and recovery mechanisms]") }}

## Testing Strategy

{{ testing_strategy | default("[Outline the testing approach including unit, integration, and validation testing]") }}"""

    def _get_tasks_template(self) -> str:
        """Get task planning format template."""
        return """# Implementation Plan

{% for task in tasks %}
- [ ] {{ loop.index }}. {{ task.title | default("Task description") }}
{% if task.subtasks %}
{% for subtask in task.subtasks %}
- [ ] {{ loop.index }}.{{ loop.index }} {{ subtask.title | default("Subtask description") }}
  {{ subtask.details | default("- Task implementation details\n  - _Requirements: X.X_") | indent(2, True) }}
{% endfor %}
{% else %}
  {{ task.details | default("- Task implementation details\n  - _Requirements: X.X_") | indent(2, True) }}
{% endif %}

{% endfor %}"""

    def _load_template_file(self, filename: str) -> str:
        """Load template from file."""
        try:
            template_path = Path(__file__).parent / "data" / "templates" / filename
            if template_path.exists():
                return template_path.read_text(encoding="utf-8")
            else:
                # Fallback to built-in templates
                if "requirements" in filename:
                    return self._get_requirements_template()
                elif "design" in filename:
                    return self._get_design_template()
                elif "tasks" in filename:
                    return self._get_tasks_template()
                return ""
        except Exception:
            return ""

    def get_template(self, template_type: TemplateType, language: str = "en") -> str:
        """Get raw template content."""
        if language == "zh":
            template_key = f"{template_type.value}-zh"
        else:
            template_key = template_type.value
        return self._templates.get(template_key, "")

    def render_template(
        self, template_type: TemplateType, context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Render template with provided context."""
        if context is None:
            context = {}

        try:
            template = self._env.get_template(template_type.value)
            return template.render(**context)
        except TemplateNotFound:
            raise ValueError(f"Template not found: {template_type.value}")
        except Exception as e:
            raise ValueError(f"Template rendering failed: {str(e)}")

    def get_requirements_template(
        self,
        feature_name: str = "",
        introduction: str = "",
        requirements: Optional[list] = None,
    ) -> str:
        """Get rendered requirements template with EARS format."""
        if requirements is None:
            requirements = [
                {
                    "user_story": "As a [role], I want [feature], so that [benefit]",
                    "acceptance_criteria": [
                        "WHEN [event] THEN [system] SHALL [response]",
                        "IF [condition] THEN [system] SHALL [response]",
                    ],
                }
            ]

        context = {
            "feature_name": feature_name,
            "introduction": introduction,
            "requirements": requirements,
        }

        return self.render_template(TemplateType.REQUIREMENTS, context)

    def get_design_template(
        self,
        feature_name: str = "",
        overview: str = "",
        architecture: str = "",
        **kwargs,
    ) -> str:
        """Get rendered design template with structure."""
        context = {
            "feature_name": feature_name,
            "overview": overview,
            "architecture": architecture,
            **kwargs,
        }

        return self.render_template(TemplateType.DESIGN, context)

    def get_tasks_template(
        self, feature_name: str = "", tasks: Optional[list] = None
    ) -> str:
        """Get rendered tasks template with proper directory structure support."""
        if tasks is None:
            tasks = [
                {
                    "title": "Set up project structure",
                    "details": "- Create directory structure\n  - _Requirements: 1.1_",
                }
            ]

        context = {"feature_name": feature_name, "tasks": tasks}

        return self.render_template(TemplateType.TASKS, context)

    def validate_template_format(
        self, template_type: TemplateType, content: str
    ) -> bool:
        """Validate that content matches expected template format."""
        try:
            # Basic validation - check for required sections
            if template_type == TemplateType.REQUIREMENTS:
                return (
                    "# Requirements Document" in content
                    and "## Requirements" in content
                )
            elif template_type == TemplateType.DESIGN:
                return "# Design Document" in content and "## Overview" in content
            elif template_type == TemplateType.TASKS:
                return "# Implementation Plan" in content and "- [ ]" in content
            return False
        except Exception:
            return False
