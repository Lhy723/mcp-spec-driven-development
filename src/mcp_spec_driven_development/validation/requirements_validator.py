"""Requirements document validator for EARS format compliance and structure validation."""

import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from ..workflow.models import ValidationLocation, ValidationResult


@dataclass
class RequirementSection:
    """Represents a parsed requirement section."""

    number: str
    user_story: Optional[str]
    acceptance_criteria: List[str]
    line_start: int
    line_end: int


class RequirementsValidator:
    """Validates requirements documents for EARS format compliance and structure."""

    # EARS format patterns
    EARS_PATTERNS = [
        r"^WHEN\s+.+\s+THEN\s+.+\s+SHALL\s+.+$",
        r"^IF\s+.+\s+THEN\s+.+\s+SHALL\s+.+$",
        r"^WHILE\s+.+\s+THEN\s+.+\s+SHALL\s+.+$",
        r"^WHERE\s+.+\s+THEN\s+.+\s+SHALL\s+.+$",
    ]

    # User story pattern
    USER_STORY_PATTERN = r"^As\s+an?\s+.+,\s+I\s+want\s+.+,\s+so\s+that\s+.+\.?$"

    # Requirement header pattern
    REQUIREMENT_HEADER_PATTERN = r"^###\s+Requirement\s+(\d+(?:\.\d+)*)\s*$"

    def __init__(self):
        """Initialize the requirements validator."""
        self.compiled_ears_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in self.EARS_PATTERNS
        ]
        self.user_story_regex = re.compile(self.USER_STORY_PATTERN, re.IGNORECASE)
        self.requirement_header_regex = re.compile(self.REQUIREMENT_HEADER_PATTERN)

    def validate(self, content: str) -> List[ValidationResult]:
        """
        Validate a requirements document with comprehensive error handling.

        Args:
            content: The requirements document content

        Returns:
            List of validation results

        Raises:
            ValidationError: If validation cannot be performed due to critical errors
        """
        from ..error_handler import get_error_handler
        from ..exceptions import ValidationError

        error_handler = get_error_handler()
        results = []

        try:
            # Validate input
            if not content or not content.strip():
                raise error_handler.handle_validation_error(
                    message="Requirements document is empty or contains only whitespace",
                    document_type="requirements",
                    context={"content_length": len(content) if content else 0},
                )

            lines = content.split("\n")

            # Check document structure with error handling
            try:
                results.extend(self._validate_document_structure(lines))
            except Exception as e:
                results.append(
                    ValidationResult(
                        type="error",
                        message=f"Error validating document structure: {str(e)}",
                        location=ValidationLocation(section="document"),
                        suggestion="Check document format and structure",
                    )
                )

            # Parse requirements sections with error handling
            try:
                requirements = self._parse_requirements(lines)
            except Exception as e:
                raise error_handler.handle_validation_error(
                    message=f"Failed to parse requirements sections: {str(e)}",
                    document_type="requirements",
                    context={"line_count": len(lines), "parsing_error": str(e)},
                )

            # Validate each requirement with error handling
            for req in requirements:
                try:
                    results.extend(self._validate_requirement(req, lines))
                except Exception as e:
                    results.append(
                        ValidationResult(
                            type="error",
                            message=f"Error validating requirement {req.number}: {str(e)}",
                            location=ValidationLocation(
                                section=f"Requirement {req.number}", line=req.line_start
                            ),
                            suggestion="Check requirement format and content",
                        )
                    )

            # Validate requirement numbering with error handling
            try:
                results.extend(self._validate_requirement_numbering(requirements))
            except Exception as e:
                results.append(
                    ValidationResult(
                        type="error",
                        message=f"Error validating requirement numbering: {str(e)}",
                        location=ValidationLocation(section="requirements"),
                        suggestion="Check requirement numbering sequence",
                    )
                )

            # Check for critical validation failures
            critical_errors = [r for r in results if r.type == "error"]
            if (
                len(critical_errors) > 10
            ):  # Too many errors might indicate structural issues
                error_handler.handle_validation_error(
                    message=f"Too many validation errors ({len(critical_errors)}), document may have structural issues",
                    validation_results=results,
                    document_type="requirements",
                    context={
                        "error_count": len(critical_errors),
                        "total_results": len(results),
                    },
                )

            return results

        except ValidationError:
            raise
        except Exception as e:
            raise error_handler.handle_validation_error(
                message=f"Unexpected error during requirements validation: {str(e)}",
                document_type="requirements",
                context={
                    "original_error": str(e),
                    "content_preview": content[:200] if content else "",
                },
            )

    def _validate_document_structure(self, lines: List[str]) -> List[ValidationResult]:
        """Validate the overall document structure."""
        results = []

        # Check for required sections
        has_title = any(line.strip().startswith("# ") for line in lines)
        has_introduction = any("## Introduction" in line for line in lines)
        has_requirements = any("## Requirements" in line for line in lines)

        if not has_title:
            results.append(
                ValidationResult(
                    type="error",
                    message="Document must have a title (# Requirements Document)",
                    location=ValidationLocation(section="document"),
                    suggestion="Add a title at the beginning: # Requirements Document",
                )
            )

        if not has_introduction:
            results.append(
                ValidationResult(
                    type="error",
                    message="Document must have an Introduction section",
                    location=ValidationLocation(section="document"),
                    suggestion="Add an ## Introduction section after the title",
                )
            )

        if not has_requirements:
            results.append(
                ValidationResult(
                    type="error",
                    message="Document must have a Requirements section",
                    location=ValidationLocation(section="document"),
                    suggestion="Add a ## Requirements section",
                )
            )

        return results

    def _parse_requirements(self, lines: List[str]) -> List[RequirementSection]:
        """Parse requirement sections from the document."""
        requirements = []
        current_req = None
        in_requirements_section = False

        for i, line in enumerate(lines):
            line_num = i + 1

            # Check if we're in the requirements section
            if line.strip() == "## Requirements":
                in_requirements_section = True
                continue
            elif line.strip().startswith("## ") and line.strip() != "## Requirements":
                in_requirements_section = False
                continue

            if not in_requirements_section:
                continue

            # Check for requirement header
            match = self.requirement_header_regex.match(line.strip())
            if match:
                # Save previous requirement
                if current_req:
                    current_req.line_end = i
                    requirements.append(current_req)

                # Start new requirement
                current_req = RequirementSection(
                    number=match.group(1),
                    user_story=None,
                    acceptance_criteria=[],
                    line_start=line_num,
                    line_end=line_num,
                )
            elif current_req:
                # Look for user story
                if line.strip().startswith("**User Story:**"):
                    story_text = line.strip().replace("**User Story:**", "").strip()
                    current_req.user_story = story_text

                # Look for acceptance criteria (numbered list items)
                elif re.match(r"^\d+\.\s+", line.strip()):
                    criteria_text = re.sub(r"^\d+\.\s+", "", line.strip())
                    current_req.acceptance_criteria.append(criteria_text)

        # Don't forget the last requirement
        if current_req:
            current_req.line_end = len(lines)
            requirements.append(current_req)

        return requirements

    def _validate_requirement(
        self, req: RequirementSection, lines: List[str]
    ) -> List[ValidationResult]:
        """Validate a single requirement section."""
        results = []
        section_name = f"Requirement {req.number}"

        # Validate user story
        results.extend(self._validate_user_story(req, section_name))

        # Validate acceptance criteria
        results.extend(self._validate_acceptance_criteria(req, section_name))

        return results

    def _validate_user_story(
        self, req: RequirementSection, section_name: str
    ) -> List[ValidationResult]:
        """Validate the user story format."""
        results = []

        if not req.user_story:
            results.append(
                ValidationResult(
                    type="error",
                    message=f"{section_name} is missing a user story",
                    location=ValidationLocation(
                        section=section_name, line=req.line_start
                    ),
                    suggestion="Add a user story in format: As a [role], I want [feature], so that [benefit].",
                )
            )
            return results

        # Check user story format
        if not self.user_story_regex.match(req.user_story):
            results.append(
                ValidationResult(
                    type="error",
                    message=f"{section_name} user story does not follow the required format",
                    location=ValidationLocation(
                        section=section_name, line=req.line_start
                    ),
                    suggestion="Use format: As a [role], I want [feature], so that [benefit].",
                )
            )

        # Check for generic roles
        if req.user_story and (
            "as a user" in req.user_story.lower()
            or "as an user" in req.user_story.lower()
        ):
            results.append(
                ValidationResult(
                    type="warning",
                    message=f'{section_name} uses generic "user" role',
                    location=ValidationLocation(
                        section=section_name, line=req.line_start
                    ),
                    suggestion='Use a specific role like "developer", "admin", "customer", etc.',
                )
            )

        return results

    def _validate_acceptance_criteria(
        self, req: RequirementSection, section_name: str
    ) -> List[ValidationResult]:
        """Validate acceptance criteria for EARS format compliance."""
        results = []

        if not req.acceptance_criteria:
            results.append(
                ValidationResult(
                    type="error",
                    message=f"{section_name} has no acceptance criteria",
                    location=ValidationLocation(
                        section=section_name, line=req.line_start
                    ),
                    suggestion="Add at least one acceptance criterion in EARS format",
                )
            )
            return results

        for i, criteria in enumerate(req.acceptance_criteria):
            criteria_num = i + 1

            # Check EARS format compliance
            is_ears_compliant = any(
                pattern.match(criteria) for pattern in self.compiled_ears_patterns
            )

            if not is_ears_compliant:
                results.append(
                    ValidationResult(
                        type="error",
                        message=f"{section_name} acceptance criterion {criteria_num} does not follow EARS format",
                        location=ValidationLocation(
                            section=section_name, line=req.line_start + 2 + i
                        ),
                        suggestion="Use EARS format: WHEN/IF/WHILE/WHERE [condition] THEN [system] SHALL [response]",
                    )
                )

            # Check for "SHALL" requirement
            if "SHALL" not in criteria.upper():
                results.append(
                    ValidationResult(
                        type="error",
                        message=f'{section_name} acceptance criterion {criteria_num} missing "SHALL"',
                        location=ValidationLocation(
                            section=section_name, line=req.line_start + 2 + i
                        ),
                        suggestion='Use "SHALL" to indicate mandatory requirements',
                    )
                )

            # Check for vague language
            vague_terms = [
                "user-friendly",
                "fast",
                "good",
                "nice",
                "better",
                "improved",
                "efficient",
            ]
            for term in vague_terms:
                if term.lower() in criteria.lower():
                    results.append(
                        ValidationResult(
                            type="warning",
                            message=f'{section_name} acceptance criterion {criteria_num} contains vague term "{term}"',
                            location=ValidationLocation(
                                section=section_name, line=req.line_start + 2 + i
                            ),
                            suggestion="Use specific, measurable criteria instead of vague terms",
                        )
                    )

        return results

    def _validate_requirement_numbering(
        self, requirements: List[RequirementSection]
    ) -> List[ValidationResult]:
        """Validate requirement numbering and hierarchy."""
        results = []

        if not requirements:
            return results

        # Check for sequential numbering
        expected_numbers = []
        for i in range(1, len(requirements) + 1):
            expected_numbers.append(str(i))

        actual_numbers = [req.number for req in requirements]

        # Check for missing or out-of-order requirements
        for i, (expected, actual) in enumerate(zip(expected_numbers, actual_numbers)):
            if expected != actual:
                results.append(
                    ValidationResult(
                        type="error",
                        message=f"Requirement numbering error: expected {expected}, found {actual}",
                        location=ValidationLocation(
                            section=f"Requirement {actual}",
                            line=requirements[i].line_start,
                        ),
                        suggestion=f"Renumber this requirement to {expected}",
                    )
                )

        # Check for duplicate numbers
        seen_numbers = set()
        for req in requirements:
            if req.number in seen_numbers:
                results.append(
                    ValidationResult(
                        type="error",
                        message=f"Duplicate requirement number: {req.number}",
                        location=ValidationLocation(
                            section=f"Requirement {req.number}", line=req.line_start
                        ),
                        suggestion="Use unique sequential numbers for each requirement",
                    )
                )
            seen_numbers.add(req.number)

        return results
