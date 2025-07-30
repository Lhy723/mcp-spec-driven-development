"""MCP tools for document validation and feedback."""

from typing import Any, Dict, List

from mcp.types import TextContent, Tool

from ..validation.design_validator import DesignValidator
from ..validation.requirements_validator import RequirementsValidator
from ..validation.task_validator import TaskValidator
from ..workflow.models import ValidationResult


class ValidationTools:
    """MCP tools for validating spec documents."""

    def __init__(self):
        """Initialize validation tools."""
        self.requirements_validator = RequirementsValidator()
        self.design_validator = DesignValidator()
        self.task_validator = TaskValidator()

    def get_tool_definitions(self) -> List[Tool]:
        """Get MCP tool definitions for validation."""
        return [
            Tool(
                name="validate_document",
                description="Validate spec document against standards",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_type": {
                            "type": "string",
                            "enum": ["requirements", "design", "tasks"],
                            "description": "Type of document to validate",
                        },
                        "content": {
                            "type": "string",
                            "description": "Document content to validate",
                        },
                        "feature_name": {
                            "type": "string",
                            "description": "Optional feature name for context",
                        },
                    },
                    "required": ["document_type", "content"],
                },
            ),
            Tool(
                name="get_validation_checklist",
                description="Get validation checklist for a document type",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "document_type": {
                            "type": "string",
                            "enum": ["requirements", "design", "tasks"],
                            "description": "Type of document to get checklist for",
                        }
                    },
                    "required": ["document_type"],
                },
            ),
            Tool(
                name="explain_validation_error",
                description="Get detailed explanation and guidance for validation errors",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "error_type": {
                            "type": "string",
                            "description": "Type of validation error to explain",
                        },
                        "document_type": {
                            "type": "string",
                            "enum": ["requirements", "design", "tasks"],
                            "description": "Document type the error relates to",
                        },
                    },
                    "required": ["error_type", "document_type"],
                },
            ),
            Tool(
                name="validate_requirement_traceability",
                description="Validate traceability between requirements, design, and tasks",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "requirements_content": {
                            "type": "string",
                            "description": "Requirements document content",
                        },
                        "design_content": {
                            "type": "string",
                            "description": "Optional design document content",
                        },
                        "tasks_content": {
                            "type": "string",
                            "description": "Optional tasks document content",
                        },
                    },
                    "required": ["requirements_content"],
                },
            ),
        ]

    async def handle_validate_document(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle validate_document tool call."""
        document_type = arguments.get("document_type", "")
        content = arguments.get("content", "")
        feature_name = arguments.get("feature_name", "")

        if not document_type or not content:
            return [
                TextContent(
                    type="text", text="Error: document_type and content are required"
                )
            ]

        try:
            # Perform validation based on document type
            if document_type == "requirements":
                results = self.requirements_validator.validate(content)
            elif document_type == "design":
                results = self.design_validator.validate(content)
            elif document_type == "tasks":
                results = self.task_validator.validate(content)
            else:
                return [
                    TextContent(
                        type="text", text=f"Invalid document type: {document_type}"
                    )
                ]

            # Format validation results
            response = self._format_validation_results(
                document_type, results, feature_name
            )

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error during validation: {str(e)}")]

    def _format_validation_results(
        self,
        document_type: str,
        results: List[ValidationResult],
        feature_name: str = "",
    ) -> str:
        """Format validation results into readable text."""
        if not results:
            return f"""# Validation Results: {document_type.title()} Document

## ✅ Validation Passed

The {document_type} document meets all quality standards and format requirements.

### Summary
- **Document Type**: {document_type.title()}
- **Feature**: {feature_name or 'Not specified'}
- **Status**: All validation checks passed
- **Errors**: 0
- **Warnings**: 0

The document is ready for review and approval.
"""

        # Categorize results
        errors = [r for r in results if r.type == "error"]
        warnings = [r for r in results if r.type == "warning"]
        info = [r for r in results if r.type == "info"]

        # Build response
        response = f"""# Validation Results: {document_type.title()} Document

## Summary
- **Document Type**: {document_type.title()}
- **Feature**: {feature_name or 'Not specified'}
- **Status**: {'❌ Failed' if errors else '⚠️ Passed with warnings' if warnings else '✅ Passed'}
- **Errors**: {len(errors)}
- **Warnings**: {len(warnings)}
- **Info**: {len(info)}

"""

        # Add errors section
        if errors:
            response += "## ❌ Errors (Must Fix)\n\n"
            for i, error in enumerate(errors, 1):
                response += f"### Error {i}\n"
                response += f"**Message**: {error.message}\n"
                if error.location:
                    if error.location.line:
                        response += f"**Location**: {error.location.section}, line {error.location.line}\n"
                    else:
                        response += f"**Location**: {error.location.section}\n"
                if error.suggestion:
                    response += f"**Suggestion**: {error.suggestion}\n"
                response += "\n"

        # Add warnings section
        if warnings:
            response += "## ⚠️ Warnings (Recommended Fixes)\n\n"
            for i, warning in enumerate(warnings, 1):
                response += f"### Warning {i}\n"
                response += f"**Message**: {warning.message}\n"
                if warning.location:
                    if warning.location.line:
                        response += f"**Location**: {warning.location.section}, line {warning.location.line}\n"
                    else:
                        response += f"**Location**: {warning.location.section}\n"
                if warning.suggestion:
                    response += f"**Suggestion**: {warning.suggestion}\n"
                response += "\n"

        # Add info section
        if info:
            response += "## ℹ️ Information\n\n"
            for i, item in enumerate(info, 1):
                response += f"### Info {i}\n"
                response += f"**Message**: {item.message}\n"
                if item.location:
                    if item.location.line:
                        response += f"**Location**: {item.location.section}, line {item.location.line}\n"
                    else:
                        response += f"**Location**: {item.location.section}\n"
                if item.suggestion:
                    response += f"**Note**: {item.suggestion}\n"
                response += "\n"

        # Add next steps
        response += "## Next Steps\n\n"
        if errors:
            response += "1. **Fix all errors** - These must be resolved before the document can be approved\n"
            response += "2. **Address warnings** - These improve document quality\n"
            response += (
                "3. **Re-validate** - Run validation again after making changes\n"
            )
            response += "4. **Seek approval** - Present corrected document to user\n"
        elif warnings:
            response += (
                "1. **Consider addressing warnings** - These improve document quality\n"
            )
            response += "2. **Document is acceptable** - Can proceed with approval if warnings are acceptable\n"
            response += (
                "3. **Present to user** - Get explicit approval before proceeding\n"
            )
        else:
            response += "1. **Document is ready** - All validation checks passed\n"
            response += "2. **Present to user** - Get explicit approval before proceeding to next phase\n"

        return response

    async def handle_get_validation_checklist(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_validation_checklist tool call."""
        document_type = arguments.get("document_type", "")

        if not document_type:
            return [TextContent(type="text", text="Error: document_type is required")]

        try:
            checklist = self._get_validation_checklist(document_type)
            return [TextContent(type="text", text=checklist)]

        except Exception as e:
            return [
                TextContent(
                    type="text", text=f"Error getting validation checklist: {str(e)}"
                )
            ]

    def _get_validation_checklist(self, document_type: str) -> str:
        """Get validation checklist for document type."""
        if document_type == "requirements":
            return """# Requirements Document Validation Checklist

## Document Structure
- [ ] Document has a title (# Requirements Document)
- [ ] Document has an Introduction section
- [ ] Document has a Requirements section
- [ ] Introduction provides clear feature context

## Requirements Format
- [ ] Each requirement has a numbered header (### Requirement X)
- [ ] Requirements are numbered sequentially (1, 2, 3...)
- [ ] No duplicate requirement numbers
- [ ] Requirements are properly organized

## User Stories
- [ ] Each requirement has a user story
- [ ] User stories follow format: "As a [role], I want [feature], so that [benefit]"
- [ ] Roles are specific (not just "user")
- [ ] Features are concrete and actionable
- [ ] Benefits explain clear value

## Acceptance Criteria
- [ ] Each requirement has acceptance criteria
- [ ] Acceptance criteria use EARS format
- [ ] All criteria include "SHALL" for mandatory requirements
- [ ] Criteria use proper EARS patterns:
  - WHEN [event] THEN [system] SHALL [response]
  - IF [condition] THEN [system] SHALL [response]
  - WHILE [state] THEN [system] SHALL [response]
  - WHERE [location] THEN [system] SHALL [response]

## Content Quality
- [ ] Requirements are testable and specific
- [ ] No vague language ("user-friendly", "fast", "good")
- [ ] Edge cases and error conditions are covered
- [ ] All stakeholder needs are represented
- [ ] Requirements are independent and atomic

## Common Issues to Avoid
- [ ] No implementation details in requirements
- [ ] No subjective or unmeasurable criteria
- [ ] No missing error handling requirements
- [ ] No gaps in user workflow coverage
"""

        elif document_type == "design":
            return """# Design Document Validation Checklist

## Document Structure
- [ ] Document has a title (# Design Document)
- [ ] All required sections are present:
  - [ ] Overview
  - [ ] Architecture
  - [ ] Components and Interfaces
  - [ ] Data Models
  - [ ] Error Handling
  - [ ] Testing Strategy

## Overview Section
- [ ] Provides comprehensive feature summary
- [ ] Includes technology stack information
- [ ] Explains high-level architectural approach
- [ ] Documents key design decisions

## Architecture Section
- [ ] Includes system architecture description
- [ ] Has architecture diagrams (Mermaid preferred)
- [ ] Shows component relationships
- [ ] Documents integration points

## Components and Interfaces
- [ ] All major components are described
- [ ] Component purposes are clear
- [ ] Key responsibilities are listed
- [ ] Interfaces are well-defined
- [ ] Dependencies are documented

## Data Models
- [ ] All data structures are defined
- [ ] Relationships are documented
- [ ] Validation rules are specified
- [ ] Storage considerations are addressed

## Error Handling
- [ ] Error scenarios are identified
- [ ] Recovery strategies are defined
- [ ] User feedback approaches are planned
- [ ] Graceful degradation is considered

## Testing Strategy
- [ ] Unit testing approach is defined
- [ ] Integration testing is planned
- [ ] Validation methods are specified
- [ ] Quality assurance is addressed

## Requirement Traceability
- [ ] All requirements are addressed in design
- [ ] Design elements trace back to requirements
- [ ] No orphaned design components
- [ ] Requirements coverage is complete

## Quality Checks
- [ ] Design decisions are justified
- [ ] Technology choices are explained
- [ ] Scalability is considered
- [ ] Security concerns are addressed
- [ ] Performance implications are discussed
"""

        elif document_type == "tasks":
            return """# Tasks Document Validation Checklist

## Document Structure
- [ ] Document has a title (# Implementation Plan)
- [ ] Tasks are formatted as checkbox list
- [ ] Task numbering is sequential and consistent
- [ ] Hierarchy is clear (max 2 levels)

## Task Format
- [ ] All tasks use checkbox format (- [ ])
- [ ] Tasks are numbered (1, 2, 3... or 1.1, 1.2...)
- [ ] Task titles are descriptive
- [ ] Task details are indented properly

## Task Content
- [ ] All tasks involve coding activities
- [ ] Tasks are specific and actionable
- [ ] Tasks specify what files/components to create/modify
- [ ] Tasks are concrete enough for immediate execution

## Requirement Traceability
- [ ] All tasks reference specific requirements
- [ ] Requirement references use granular format (1.1, 2.3)
- [ ] All requirements are covered by tasks
- [ ] No orphaned tasks without requirement references

## Task Dependencies
- [ ] Tasks are sequenced logically
- [ ] Each task builds on previous tasks
- [ ] No circular dependencies
- [ ] Foundation tasks come first

## Implementation Strategy
- [ ] Tasks support incremental development
- [ ] Core functionality is validated early
- [ ] Test-driven development is planned
- [ ] No orphaned or disconnected code

## Task Categories
- [ ] Setup and foundation tasks are included
- [ ] Implementation tasks are comprehensive
- [ ] Testing tasks are integrated
- [ ] Integration and wiring tasks are present

## Quality Checks
- [ ] No non-coding tasks (deployment, user testing)
- [ ] No abstract or high-level tasks
- [ ] Tasks are appropriately sized
- [ ] Implementation order makes sense

## Common Issues to Avoid
- [ ] No tasks for user acceptance testing
- [ ] No deployment or production tasks
- [ ] No business process or organizational tasks
- [ ] No marketing or communication tasks
- [ ] No tasks that can't be completed through coding
"""

        else:
            return f"Error: Invalid document type '{document_type}'. Available types: requirements, design, tasks"

    async def handle_explain_validation_error(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle explain_validation_error tool call."""
        error_type = arguments.get("error_type", "")
        document_type = arguments.get("document_type", "")

        if not error_type or not document_type:
            return [
                TextContent(
                    type="text", text="Error: error_type and document_type are required"
                )
            ]

        try:
            explanation = self._get_error_explanation(error_type, document_type)
            return [TextContent(type="text", text=explanation)]

        except Exception as e:
            return [
                TextContent(
                    type="text", text=f"Error explaining validation error: {str(e)}"
                )
            ]

    def _get_error_explanation(self, error_type: str, document_type: str) -> str:
        """Get detailed explanation for validation error."""
        explanations = {
            "requirements": {
                "ears_format": """# EARS Format Error Explanation

## What is EARS Format?
EARS (Easy Approach to Requirements Syntax) is a structured way to write clear, testable acceptance criteria.

## Required Patterns
Acceptance criteria must use one of these patterns:
- **WHEN** [trigger event] **THEN** [system] **SHALL** [response]
- **IF** [precondition] **THEN** [system] **SHALL** [response]
- **WHILE** [system state] **THEN** [system] **SHALL** [response]
- **WHERE** [feature location] **THEN** [system] **SHALL** [response]

## Common Mistakes
❌ **Bad**: "System validates user input"
✅ **Good**: "WHEN user submits form THEN system SHALL validate input data"

❌ **Bad**: "User can login successfully"
✅ **Good**: "WHEN user enters valid credentials THEN system SHALL authenticate within 2 seconds"

## Key Requirements
1. Must include trigger/condition (WHEN, IF, WHILE, WHERE)
2. Must include "THEN" to separate condition from response
3. Must include "SHALL" to indicate mandatory requirement
4. Must be specific and testable

## How to Fix
1. Identify the trigger or condition
2. Specify what the system must do
3. Use the appropriate EARS pattern
4. Make it specific and measurable
""",
                "user_story_format": """# User Story Format Error Explanation

## Required Format
User stories must follow this exact format:
**"As a [role], I want [feature], so that [benefit]"**

## Components
- **Role**: Specific user type (admin, customer, developer, etc.)
- **Feature**: What functionality is needed
- **Benefit**: Why this feature provides value

## Common Mistakes
❌ **Bad**: "As a user, I want to use the system"
- Too generic role ("user")
- Vague feature description
- No clear benefit

✅ **Good**: "As a project manager, I want to create feature specifications, so that I can ensure systematic development"
- Specific role (project manager)
- Clear feature (create specifications)
- Clear benefit (systematic development)

## How to Fix
1. Replace "user" with specific role
2. Make feature concrete and actionable
3. Explain the value or motivation
4. Ensure benefit is meaningful to the role
""",
                "missing_sections": """# Missing Sections Error Explanation

## Required Sections
Requirements documents must have:
1. **Title**: # Requirements Document
2. **Introduction**: ## Introduction
3. **Requirements**: ## Requirements

## Purpose of Each Section
- **Title**: Clearly identifies document type
- **Introduction**: Provides context and feature overview
- **Requirements**: Contains the actual requirements

## How to Fix
Add the missing section(s) to your document:

```markdown
# Requirements Document

## Introduction
[Brief description of the feature and its purpose]

## Requirements
[Your requirements go here]
```
""",
            },
            "design": {
                "missing_sections": """# Missing Design Sections Error Explanation

## Required Sections
Design documents must include all of these sections:
1. **Overview** - Feature summary and technology stack
2. **Architecture** - System design and component relationships
3. **Components and Interfaces** - Detailed component descriptions
4. **Data Models** - Data structures and relationships
5. **Error Handling** - Error scenarios and recovery strategies
6. **Testing Strategy** - Testing approach and quality assurance

## Why Each Section Matters
- **Overview**: Provides context and high-level approach
- **Architecture**: Shows how components work together
- **Components**: Details implementation boundaries
- **Data Models**: Defines data structures and validation
- **Error Handling**: Plans for failure scenarios
- **Testing**: Ensures quality and validation approach

## How to Fix
Add the missing section(s) with appropriate content for your feature.
""",
                "requirement_traceability": """# Requirement Traceability Error Explanation

## What is Requirement Traceability?
Every element in the design must address specific requirements from the requirements document.

## Why It Matters
- Ensures all requirements are addressed
- Prevents scope creep
- Validates design completeness
- Enables change impact analysis

## Common Issues
- Design components that don't map to requirements
- Requirements not addressed in design
- Vague connections between requirements and design

## How to Fix
1. Review each requirement from requirements document
2. Ensure design addresses each requirement
3. Add missing design elements for uncovered requirements
4. Remove design elements that don't serve requirements
5. Create explicit traceability matrix if needed
""",
            },
            "tasks": {
                "non_coding_tasks": """# Non-Coding Tasks Error Explanation

## What Are Non-Coding Tasks?
Tasks that cannot be completed by writing, modifying, or testing code.

## Examples of Non-Coding Tasks (Avoid These)
❌ "Deploy to production"
❌ "Get user feedback"
❌ "Write documentation"
❌ "Conduct user testing"
❌ "Set up monitoring"

## Examples of Coding Tasks (Use These)
✅ "Implement UserService.authenticate() method"
✅ "Create User model with validation"
✅ "Write unit tests for authentication logic"
✅ "Add error handling to API endpoints"

## Why This Matters
Task lists are for implementation planning. Non-coding activities belong in separate project management processes.

## How to Fix
1. Focus only on code implementation activities
2. Break abstract concepts into concrete coding steps
3. Specify files, classes, or functions to create/modify
4. Ensure tasks can be completed in development environment
""",
                "missing_requirement_references": """# Missing Requirement References Error Explanation

## What Are Requirement References?
Each task must reference the specific requirements it implements.

## Required Format
Tasks should end with: `_Requirements: X.X, Y.Y_`

## Examples
✅ **Good**:
```
- [ ] 1.1 Create User model with validation
  - Implement User class with email and password fields
  - Add validation methods for data integrity
  - _Requirements: 1.2, 3.1_
```

❌ **Bad**:
```
- [ ] 1.1 Create User model
  - Implement User class
```

## Why This Matters
- Ensures all requirements are covered
- Enables traceability from requirements to implementation
- Helps prioritize tasks based on requirement importance
- Validates completeness of implementation plan

## How to Fix
1. Review requirements document
2. Identify which requirements each task addresses
3. Add requirement references using format: _Requirements: X.X, Y.Y_
4. Use granular requirement numbers (1.1, 2.3) not just user story numbers
""",
            },
        }

        doc_explanations = explanations.get(document_type, {})
        explanation = doc_explanations.get(error_type.lower())

        if not explanation:
            return f"""# Error Explanation Not Found

## Error Details
- **Error Type**: {error_type}
- **Document Type**: {document_type}

## Available Explanations
This specific error explanation is not available. Common validation errors include:

### Requirements Document
- ears_format
- user_story_format
- missing_sections

### Design Document
- missing_sections
- requirement_traceability

### Tasks Document
- non_coding_tasks
- missing_requirement_references

Please check the error type and try again, or use the validation checklist for general guidance.
"""

        return explanation

    async def handle_validate_requirement_traceability(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle validate_requirement_traceability tool call."""
        requirements_content = arguments.get("requirements_content", "")
        design_content = arguments.get("design_content", "")
        tasks_content = arguments.get("tasks_content", "")

        if not requirements_content:
            return [
                TextContent(type="text", text="Error: requirements_content is required")
            ]

        try:
            # Parse requirements to extract requirement IDs
            req_ids = self._extract_requirement_ids(requirements_content)

            response = f"""# Requirement Traceability Analysis

## Requirements Found
Total requirements identified: {len(req_ids)}
"""

            for req_id in req_ids:
                response += f"- Requirement {req_id}\n"

            # Check design traceability if provided
            if design_content:
                design_coverage = self._check_design_coverage(req_ids, design_content)
                response += f"\n## Design Coverage\n"
                for req_id, covered in design_coverage.items():
                    status = "✅" if covered else "❌"
                    response += f"- Requirement {req_id}: {status} {'Addressed' if covered else 'Not addressed'}\n"

            # Check tasks traceability if provided
            if tasks_content:
                task_coverage = self._check_task_coverage(req_ids, tasks_content)
                response += f"\n## Task Coverage\n"
                for req_id, covered in task_coverage.items():
                    status = "✅" if covered else "❌"
                    response += f"- Requirement {req_id}: {status} {'Referenced' if covered else 'Not referenced'}\n"

                # Check for orphaned task references
                orphaned_refs = self._find_orphaned_task_references(
                    req_ids, tasks_content
                )
                if orphaned_refs:
                    response += f"\n## ⚠️ Orphaned Task References\n"
                    response += "These task references don't match any requirements:\n"
                    for ref in orphaned_refs:
                        response += f"- {ref}\n"

            # Summary and recommendations
            response += "\n## Summary\n"
            if design_content and tasks_content:
                design_issues = sum(
                    1 for covered in design_coverage.values() if not covered
                )
                task_issues = sum(
                    1 for covered in task_coverage.values() if not covered
                )

                if design_issues == 0 and task_issues == 0:
                    response += "✅ **Excellent traceability** - All requirements are properly addressed\n"
                else:
                    response += f"❌ **Traceability issues found**:\n"
                    if design_issues > 0:
                        response += (
                            f"- {design_issues} requirements not addressed in design\n"
                        )
                    if task_issues > 0:
                        response += (
                            f"- {task_issues} requirements not referenced in tasks\n"
                        )

            response += "\n## Recommendations\n"
            response += "1. Ensure all requirements are addressed in design\n"
            response += "2. Verify all requirements are referenced in tasks\n"
            response += "3. Remove or correct orphaned task references\n"
            response += "4. Update documents to improve traceability\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            return [
                TextContent(
                    type="text", text=f"Error validating traceability: {str(e)}"
                )
            ]

    def _extract_requirement_ids(self, content: str) -> List[str]:
        """Extract requirement IDs from requirements document."""
        import re

        # Look for requirement headers like "### Requirement 1" or "### Requirement 1.1"
        pattern = r"###\s+Requirement\s+(\d+(?:\.\d+)*)"
        matches = re.findall(pattern, content)
        return matches

    def _check_design_coverage(
        self, req_ids: List[str], design_content: str
    ) -> Dict[str, bool]:
        """Check if requirements are addressed in design."""
        coverage = {}

        for req_id in req_ids:
            # Simple check - look for requirement ID mentioned in design
            # This is a basic implementation - could be more sophisticated
            covered = (
                f"requirement {req_id}" in design_content.lower()
                or f"req {req_id}" in design_content.lower()
            )
            coverage[req_id] = covered

        return coverage

    def _check_task_coverage(
        self, req_ids: List[str], tasks_content: str
    ) -> Dict[str, bool]:
        """Check if requirements are referenced in tasks."""
        import re

        coverage = {}

        # Extract all requirement references from tasks
        ref_pattern = r"_Requirements?:\s*([^_\n]+)_"
        ref_matches = re.findall(ref_pattern, tasks_content)

        # Parse all referenced requirement IDs
        referenced_ids = set()
        for match in ref_matches:
            # Split by comma and clean up
            ids = [id.strip() for id in match.split(",")]
            referenced_ids.update(ids)

        # Check coverage for each requirement
        for req_id in req_ids:
            coverage[req_id] = req_id in referenced_ids

        return coverage

    def _find_orphaned_task_references(
        self, req_ids: List[str], tasks_content: str
    ) -> List[str]:
        """Find task references that don't match any requirements."""
        import re

        # Extract all requirement references from tasks
        ref_pattern = r"_Requirements?:\s*([^_\n]+)_"
        ref_matches = re.findall(ref_pattern, tasks_content)

        # Parse all referenced requirement IDs
        referenced_ids = []
        for match in ref_matches:
            ids = [id.strip() for id in match.split(",")]
            referenced_ids.extend(ids)

        # Find orphaned references
        valid_req_ids = set(req_ids)
        orphaned = [ref for ref in referenced_ids if ref not in valid_req_ids]

        return list(set(orphaned))  # Remove duplicates

    async def handle_tool_call(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle MCP tool calls for validation."""
        handlers = {
            "validate_document": self.handle_validate_document,
            "get_validation_checklist": self.handle_get_validation_checklist,
            "explain_validation_error": self.handle_explain_validation_error,
            "validate_requirement_traceability": self.handle_validate_requirement_traceability,
        }

        handler = handlers.get(name)
        if not handler:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return await handler(arguments)
