"""Design document validator for structure validation and requirements traceability."""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from ..workflow.models import ValidationLocation, ValidationResult


@dataclass
class DesignSection:
    """Represents a parsed design section."""

    name: str
    content: str
    line_start: int
    line_end: int
    subsections: List["DesignSection"]


class DesignValidator:
    """Validates design documents for structure and requirements traceability."""

    # Required sections for a complete design document
    REQUIRED_SECTIONS = [
        "Overview",
        "Architecture",
        "Components and Interfaces",
        "Data Models",
        "Error Handling",
        "Testing Strategy",
    ]

    # Mermaid diagram pattern
    MERMAID_PATTERN = r"```mermaid\s*\n.*?\n```"

    # Component section pattern
    COMPONENT_PATTERN = r"###\s+(.+)"

    # Requirements reference pattern (e.g., _Requirements: 1.1, 2.3_)
    REQUIREMENTS_REF_PATTERN = r"_Requirements?:\s*([0-9.,\s]+)_"

    def __init__(self):
        """Initialize the design validator."""
        self.mermaid_regex = re.compile(self.MERMAID_PATTERN, re.DOTALL | re.IGNORECASE)
        self.component_regex = re.compile(self.COMPONENT_PATTERN)
        self.requirements_ref_regex = re.compile(self.REQUIREMENTS_REF_PATTERN)

    def validate(
        self, content: str, requirements_content: Optional[str] = None
    ) -> List[ValidationResult]:
        """
        Validate a design document.

        Args:
            content: The design document content
            requirements_content: Optional requirements document for traceability checking

        Returns:
            List of validation results
        """
        results = []
        lines = content.split("\n")

        # Check document structure
        results.extend(self._validate_document_structure(lines))

        # Parse sections
        sections = self._parse_sections(lines)

        # Validate required sections presence
        results.extend(self._validate_required_sections(sections))

        # Validate architecture section
        results.extend(self._validate_architecture_section(content, sections))

        # Validate components section
        results.extend(self._validate_components_section(sections))

        # Validate requirements traceability if requirements provided
        if requirements_content:
            results.extend(
                self._validate_requirements_traceability(content, requirements_content)
            )

        return results

    def _validate_document_structure(self, lines: List[str]) -> List[ValidationResult]:
        """Validate the overall document structure."""
        results = []

        # Check for title
        has_title = any(line.strip().startswith("# ") for line in lines)
        if not has_title:
            results.append(
                ValidationResult(
                    type="error",
                    message="Document must have a title (# Design Document)",
                    location=ValidationLocation(section="document"),
                    suggestion="Add a title at the beginning: # Design Document",
                )
            )

        # Check for proper heading hierarchy
        heading_levels = []
        for i, line in enumerate(lines):
            if line.strip().startswith("#"):
                level = len(line.strip().split()[0])  # Count # characters
                heading_levels.append((level, i + 1))

        # Validate heading hierarchy (should not skip levels)
        for i in range(1, len(heading_levels)):
            current_level, current_line = heading_levels[i]
            prev_level, _ = heading_levels[i - 1]

            if current_level > prev_level + 1:
                results.append(
                    ValidationResult(
                        type="warning",
                        message=f"Heading hierarchy skips levels (from h{prev_level} to h{current_level})",
                        location=ValidationLocation(
                            section="document", line=current_line
                        ),
                        suggestion="Use sequential heading levels (h1, h2, h3, etc.)",
                    )
                )

        return results

    def _parse_sections(self, lines: List[str]) -> Dict[str, DesignSection]:
        """Parse sections from the document."""
        sections = {}
        current_section = None
        section_content = []

        for i, line in enumerate(lines):
            line_num = i + 1

            # Check for main section (## heading)
            if line.strip().startswith("## "):
                # Save previous section
                if current_section:
                    sections[current_section["name"]] = DesignSection(
                        name=current_section["name"],
                        content="\n".join(section_content),
                        line_start=current_section["line_start"],
                        line_end=line_num - 1,
                        subsections=[],
                    )

                # Start new section
                section_name = line.strip()[3:].strip()
                current_section = {"name": section_name, "line_start": line_num}
                section_content = []
            elif current_section:
                section_content.append(line)

        # Don't forget the last section
        if current_section:
            sections[current_section["name"]] = DesignSection(
                name=current_section["name"],
                content="\n".join(section_content),
                line_start=current_section["line_start"],
                line_end=len(lines),
                subsections=[],
            )

        return sections

    def _validate_required_sections(
        self, sections: Dict[str, DesignSection]
    ) -> List[ValidationResult]:
        """Validate that all required sections are present."""
        results = []

        for required_section in self.REQUIRED_SECTIONS:
            if required_section not in sections:
                results.append(
                    ValidationResult(
                        type="error",
                        message=f"Missing required section: {required_section}",
                        location=ValidationLocation(section="document"),
                        suggestion=f"Add a ## {required_section} section",
                    )
                )
            elif not sections[required_section].content.strip():
                results.append(
                    ValidationResult(
                        type="warning",
                        message=f'Section "{required_section}" is empty',
                        location=ValidationLocation(
                            section=required_section,
                            line=sections[required_section].line_start,
                        ),
                        suggestion=f"Add content to the {required_section} section",
                    )
                )

        return results

    def _validate_architecture_section(
        self, content: str, sections: Dict[str, DesignSection]
    ) -> List[ValidationResult]:
        """Validate the architecture section for diagrams and explanations."""
        results = []

        if "Architecture" not in sections:
            return results

        arch_section = sections["Architecture"]
        arch_content = arch_section.content

        # Check for architecture diagrams
        mermaid_diagrams = self.mermaid_regex.findall(arch_content)

        if not mermaid_diagrams:
            results.append(
                ValidationResult(
                    type="warning",
                    message="Architecture section lacks visual diagrams",
                    location=ValidationLocation(
                        section="Architecture", line=arch_section.line_start
                    ),
                    suggestion="Add Mermaid diagrams to illustrate the architecture",
                )
            )
        else:
            # Validate Mermaid diagram syntax (basic check)
            for diagram in mermaid_diagrams:
                if (
                    "graph" not in diagram.lower()
                    and "flowchart" not in diagram.lower()
                ):
                    results.append(
                        ValidationResult(
                            type="warning",
                            message="Mermaid diagram may be missing graph type declaration",
                            location=ValidationLocation(section="Architecture"),
                            suggestion="Ensure Mermaid diagrams start with graph type (e.g., graph TB, flowchart TD)",
                        )
                    )

        # Check for architecture explanation
        if len(arch_content.strip()) < 100:  # Arbitrary minimum length
            results.append(
                ValidationResult(
                    type="warning",
                    message="Architecture section appears too brief",
                    location=ValidationLocation(
                        section="Architecture", line=arch_section.line_start
                    ),
                    suggestion="Provide detailed explanation of architectural decisions and component relationships",
                )
            )

        return results

    def _validate_components_section(
        self, sections: Dict[str, DesignSection]
    ) -> List[ValidationResult]:
        """Validate the components and interfaces section."""
        results = []

        if "Components and Interfaces" not in sections:
            return results

        comp_section = sections["Components and Interfaces"]
        comp_content = comp_section.content

        # Find component subsections
        component_matches = self.component_regex.findall(comp_content)

        if not component_matches:
            results.append(
                ValidationResult(
                    type="warning",
                    message="Components section lacks component definitions",
                    location=ValidationLocation(
                        section="Components and Interfaces",
                        line=comp_section.line_start,
                    ),
                    suggestion="Define individual components using ### Component Name headings",
                )
            )
        else:
            # Validate each component has required information
            for component_name in component_matches:
                # Check for purpose, responsibilities, interface
                component_section_text = self._extract_component_section(
                    comp_content, component_name
                )

                if "Purpose" not in component_section_text:
                    results.append(
                        ValidationResult(
                            type="warning",
                            message=f'Component "{component_name}" missing purpose description',
                            location=ValidationLocation(
                                section="Components and Interfaces"
                            ),
                            suggestion="Add **Purpose**: description for each component",
                        )
                    )

                if "Responsibilities" not in component_section_text:
                    results.append(
                        ValidationResult(
                            type="warning",
                            message=f'Component "{component_name}" missing responsibilities',
                            location=ValidationLocation(
                                section="Components and Interfaces"
                            ),
                            suggestion="Add **Key Responsibilities**: list for each component",
                        )
                    )

                if "Interface" not in component_section_text:
                    results.append(
                        ValidationResult(
                            type="warning",
                            message=f'Component "{component_name}" missing interface definition',
                            location=ValidationLocation(
                                section="Components and Interfaces"
                            ),
                            suggestion="Add **Interface**: definition for each component",
                        )
                    )

        return results

    def _extract_component_section(self, content: str, component_name: str) -> str:
        """Extract the content for a specific component section."""
        lines = content.split("\n")
        in_component = False
        component_lines = []

        for line in lines:
            if line.strip() == f"### {component_name}":
                in_component = True
                continue
            elif line.strip().startswith("### ") and in_component:
                break
            elif in_component:
                component_lines.append(line)

        return "\n".join(component_lines)

    def _validate_requirements_traceability(
        self, design_content: str, requirements_content: str
    ) -> List[ValidationResult]:
        """Validate that design traces back to requirements."""
        results = []

        # Extract requirement numbers from requirements document
        req_numbers = self._extract_requirement_numbers(requirements_content)

        # Extract requirement references from design document
        design_refs = self._extract_requirement_references(design_content)

        # Check for requirements not addressed in design
        unaddressed_reqs = req_numbers - design_refs
        for req_num in unaddressed_reqs:
            results.append(
                ValidationResult(
                    type="warning",
                    message=f"Requirement {req_num} not addressed in design",
                    location=ValidationLocation(section="document"),
                    suggestion=f"Add design elements that address requirement {req_num}",
                )
            )

        # Check for invalid requirement references
        invalid_refs = design_refs - req_numbers
        for ref in invalid_refs:
            results.append(
                ValidationResult(
                    type="error",
                    message=f"Design references non-existent requirement {ref}",
                    location=ValidationLocation(section="document"),
                    suggestion=f"Remove reference to requirement {ref} or verify requirement exists",
                )
            )

        # Check if design has any requirement references at all
        if not design_refs and req_numbers:
            results.append(
                ValidationResult(
                    type="warning",
                    message="Design document lacks requirement traceability references",
                    location=ValidationLocation(section="document"),
                    suggestion="Add _Requirements: X.X_ references to link design elements to requirements",
                )
            )

        return results

    def _extract_requirement_numbers(self, requirements_content: str) -> Set[str]:
        """Extract requirement numbers from requirements document."""
        req_numbers = set()

        # Look for requirement headers like "### Requirement 1"
        req_header_pattern = r"###\s+Requirement\s+(\d+(?:\.\d+)*)"
        matches = re.findall(req_header_pattern, requirements_content)
        req_numbers.update(matches)

        # Also look for acceptance criteria numbering within requirements
        # This is more complex and might need refinement based on actual format

        return req_numbers

    def _extract_requirement_references(self, design_content: str) -> Set[str]:
        """Extract requirement references from design document."""
        refs = set()

        matches = self.requirements_ref_regex.findall(design_content)
        for match in matches:
            # Split by comma and clean up
            ref_list = [ref.strip() for ref in match.split(",")]
            refs.update(ref_list)

        return refs
