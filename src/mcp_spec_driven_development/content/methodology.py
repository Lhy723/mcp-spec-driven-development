"""Methodology guides access system for spec-driven development."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class MethodologyTopic(Enum):
    """Available methodology topics."""

    WORKFLOW = "workflow"
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    TASKS = "tasks"
    EARS_FORMAT = "ears_format"
    PHASE_TRANSITIONS = "phase_transitions"
    BEST_PRACTICES = "best_practices"
    TROUBLESHOOTING = "troubleshooting"


@dataclass
class MethodologyGuide:
    """Methodology guide content structure."""

    topic: MethodologyTopic
    title: str
    content: str
    related_topics: List[MethodologyTopic]
    examples: List[str]


class MethodologyGuides:
    """Repository for spec-driven development methodology guides."""

    def __init__(self):
        """Initialize methodology guides with built-in content."""
        self._guides = self._load_builtin_guides()

    def _load_builtin_guides(self) -> Dict[str, MethodologyGuide]:
        """Load built-in methodology guides."""
        guides = {}

        # Load English guides
        guides[MethodologyTopic.WORKFLOW.value] = self._load_methodology_file(
            "workflow.md", MethodologyTopic.WORKFLOW
        )
        guides[MethodologyTopic.EARS_FORMAT.value] = self._load_methodology_file(
            "ears-format.md", MethodologyTopic.EARS_FORMAT
        )
        guides[MethodologyTopic.PHASE_TRANSITIONS.value] = self._load_methodology_file(
            "phase-transitions.md", MethodologyTopic.PHASE_TRANSITIONS
        )

        # Load Chinese guides
        guides[f"{MethodologyTopic.WORKFLOW.value}-zh"] = self._load_methodology_file(
            "workflow-zh.md", MethodologyTopic.WORKFLOW
        )
        guides[
            f"{MethodologyTopic.EARS_FORMAT.value}-zh"
        ] = self._load_methodology_file(
            "ears-format-zh.md", MethodologyTopic.EARS_FORMAT
        )

        # Add fallback guides for missing files
        for topic in MethodologyTopic:
            if topic.value not in guides:
                guides[topic.value] = self._get_fallback_guide(topic)

        return guides

    def _get_workflow_guide(self) -> MethodologyGuide:
        """Get three-phase workflow documentation."""
        content = """# Spec-Driven Development Workflow

## Overview

Spec-driven development follows a systematic three-phase approach to transform feature ideas into implementation plans:

**Requirements → Design → Tasks**

Each phase builds upon the previous one and requires explicit approval before proceeding to the next phase.

## Phase 1: Requirements

**Purpose**: Transform rough feature ideas into structured, testable requirements using EARS format.

**Key Activities**:
- Write user stories in "As a [role], I want [feature], so that [benefit]" format
- Create acceptance criteria using EARS format (Easy Approach to Requirements Syntax)
- Ensure requirements are testable, specific, and complete
- Get explicit user approval before proceeding

**Output**: requirements.md file with structured requirements

## Phase 2: Design

**Purpose**: Create comprehensive technical design based on approved requirements.

**Key Activities**:
- Research relevant technologies and approaches
- Design system architecture and component interfaces
- Define data models and error handling strategies
- Plan testing approach
- Ensure design addresses all requirements
- Get explicit user approval before proceeding

**Output**: design.md file with detailed technical design

## Phase 3: Tasks

**Purpose**: Break down design into actionable implementation tasks.

**Key Activities**:
- Create discrete, manageable coding tasks
- Ensure each task references specific requirements
- Sequence tasks for incremental development
- Focus on test-driven development approach
- Get explicit user approval before implementation

**Output**: tasks.md file with implementation checklist

## Key Principles

1. **Systematic Progression**: Never skip phases or proceed without approval
2. **Requirement Traceability**: Every design element and task must trace back to requirements
3. **Incremental Development**: Tasks should build incrementally on each other
4. **Quality Gates**: Each phase includes validation and approval checkpoints
5. **User-Centered**: Regular user feedback and approval throughout the process"""

        return MethodologyGuide(
            topic=MethodologyTopic.WORKFLOW,
            title="Spec-Driven Development Workflow",
            content=content,
            related_topics=[
                MethodologyTopic.REQUIREMENTS,
                MethodologyTopic.DESIGN,
                MethodologyTopic.TASKS,
                MethodologyTopic.PHASE_TRANSITIONS,
            ],
            examples=["Complete workflow example", "Phase transition examples"],
        )

    def _get_requirements_guide(self) -> MethodologyGuide:
        """Get requirements phase documentation."""
        content = """# Requirements Phase Guide

## Purpose

Transform rough feature ideas into structured, testable requirements that serve as the foundation for design and implementation.

## EARS Format (Easy Approach to Requirements Syntax)

Use these patterns for acceptance criteria:

- **WHEN** [trigger event] **THEN** [system] **SHALL** [response]
- **IF** [precondition] **THEN** [system] **SHALL** [response]
- **WHERE** [feature applies] **THEN** [system] **SHALL** [response]
- **WHILE** [system state] **THEN** [system] **SHALL** [response]

## User Story Format

**Template**: As a [role], I want [feature], so that [benefit]

**Guidelines**:
- Role should be specific (user, admin, developer, etc.)
- Feature should be concrete and actionable
- Benefit should explain the value or motivation

## Requirements Structure

### Document Organization
1. **Introduction**: Brief feature overview and context
2. **Requirements**: Numbered list of user stories with acceptance criteria

### Quality Criteria
- Each requirement must be testable
- Acceptance criteria must be specific and measurable
- Requirements should cover normal flows, edge cases, and error conditions
- All stakeholder needs should be represented

## Common Pitfalls

1. **Vague Requirements**: Avoid subjective terms like "fast", "user-friendly"
2. **Missing Edge Cases**: Consider error conditions and boundary cases
3. **Implementation Details**: Focus on what, not how
4. **Incomplete Coverage**: Ensure all user needs are addressed

## Validation Checklist

- [ ] All user stories follow the standard format
- [ ] Acceptance criteria use EARS format
- [ ] Requirements are testable and specific
- [ ] Edge cases and error conditions are covered
- [ ] Requirements are numbered and organized
- [ ] Introduction provides clear context"""

        return MethodologyGuide(
            topic=MethodologyTopic.REQUIREMENTS,
            title="Requirements Phase Guide",
            content=content,
            related_topics=[
                MethodologyTopic.EARS_FORMAT,
                MethodologyTopic.WORKFLOW,
                MethodologyTopic.BEST_PRACTICES,
            ],
            examples=[
                "EARS format examples",
                "User story examples",
                "Requirements validation examples",
            ],
        )

    def _get_design_guide(self) -> MethodologyGuide:
        """Get design phase documentation."""
        content = """# Design Phase Guide

## Purpose

Create comprehensive technical design that addresses all requirements and provides clear implementation guidance.

## Required Sections

### 1. Overview
- Feature summary and technology stack
- High-level architectural approach
- Key design decisions and rationales

### 2. Architecture
- System architecture diagrams (use Mermaid when possible)
- Component relationships and data flow
- Integration points and external dependencies

### 3. Components and Interfaces
- Detailed component descriptions
- Interface definitions and contracts
- Responsibility boundaries

### 4. Data Models
- Data structures and relationships
- Validation rules and constraints
- Storage and persistence considerations

### 5. Error Handling
- Error scenarios and recovery strategies
- User feedback and logging approaches
- Graceful degradation plans

### 6. Testing Strategy
- Unit testing approach
- Integration testing plans
- Validation and quality assurance methods

## Design Principles

1. **Requirement Traceability**: Every design element must address specific requirements
2. **Modularity**: Design for maintainable, testable components
3. **Scalability**: Consider future growth and changes
4. **Security**: Address security concerns from the start
5. **Performance**: Consider performance implications

## Research Integration

- Conduct research during design phase
- Document key findings and decisions
- Include relevant links and references
- Justify technology and approach choices

## Validation Checklist

- [ ] All requirements are addressed in the design
- [ ] Architecture is clearly documented with diagrams
- [ ] Components and interfaces are well-defined
- [ ] Data models are complete and validated
- [ ] Error handling is comprehensive
- [ ] Testing strategy covers all aspects
- [ ] Design decisions are justified"""

        return MethodologyGuide(
            topic=MethodologyTopic.DESIGN,
            title="Design Phase Guide",
            content=content,
            related_topics=[
                MethodologyTopic.WORKFLOW,
                MethodologyTopic.REQUIREMENTS,
                MethodologyTopic.BEST_PRACTICES,
            ],
            examples=[
                "Architecture diagrams",
                "Component design examples",
                "Data model examples",
            ],
        )

    def _get_tasks_guide(self) -> MethodologyGuide:
        """Get tasks phase documentation."""
        content = """# Tasks Phase Guide

## Purpose

Break down the approved design into discrete, actionable implementation tasks that can be executed systematically.

## Task Structure

### Format
```
- [ ] X. Task title
  - Implementation details
  - Specific requirements references
  - _Requirements: X.X, Y.Y_
```

### Hierarchy
- Use numbered tasks (1, 2, 3...)
- Use decimal notation for subtasks (1.1, 1.2, 2.1...)
- Maximum two levels of hierarchy
- Keep structure simple and clear

## Task Quality Criteria

### Actionable Tasks
- Each task must involve writing, modifying, or testing code
- Tasks should be specific enough for immediate execution
- Avoid high-level concepts; focus on concrete implementation

### Requirement Traceability
- Every task must reference specific requirements
- Use granular requirement references (1.1, 2.3) not just user stories
- Ensure all requirements are covered by tasks

### Incremental Development
- Tasks should build on previous tasks
- No orphaned or hanging code
- Early validation of core functionality
- Test-driven development approach

## Task Categories

### Setup Tasks
- Project structure and configuration
- Development environment setup
- Core interfaces and foundations

### Implementation Tasks
- Feature development in logical order
- Component implementation
- Integration and wiring

### Testing Tasks
- Unit test creation
- Integration test development
- Validation and quality assurance

## Common Pitfalls

1. **Non-Coding Tasks**: Avoid user testing, deployment, or business process tasks
2. **Too Abstract**: Tasks should be concrete implementation steps
3. **Missing Dependencies**: Ensure proper task sequencing
4. **Poor Traceability**: Every task must reference requirements

## Validation Checklist

- [ ] All tasks involve coding activities
- [ ] Tasks reference specific requirements
- [ ] Implementation order is logical
- [ ] All requirements are covered
- [ ] Tasks are actionable and specific
- [ ] Dependencies are properly sequenced"""

        return MethodologyGuide(
            topic=MethodologyTopic.TASKS,
            title="Tasks Phase Guide",
            content=content,
            related_topics=[
                MethodologyTopic.WORKFLOW,
                MethodologyTopic.DESIGN,
                MethodologyTopic.BEST_PRACTICES,
            ],
            examples=[
                "Task structure examples",
                "Dependency management",
                "Requirement traceability",
            ],
        )

    def _get_ears_format_guide(self) -> MethodologyGuide:
        """Get EARS format detailed guide."""
        content = """# EARS Format Guide

## What is EARS?

EARS (Easy Approach to Requirements Syntax) is a structured format for writing clear, testable acceptance criteria.

## EARS Patterns

### 1. Event-Driven (WHEN...THEN)
**Pattern**: WHEN [trigger event] THEN [system] SHALL [response]

**Examples**:
- WHEN user clicks login button THEN system SHALL validate credentials
- WHEN invalid data is submitted THEN system SHALL display error message
- WHEN user session expires THEN system SHALL redirect to login page

### 2. Conditional (IF...THEN)
**Pattern**: IF [precondition] THEN [system] SHALL [response]

**Examples**:
- IF user is not authenticated THEN system SHALL deny access
- IF file size exceeds 10MB THEN system SHALL reject upload
- IF user has admin role THEN system SHALL show admin panel

### 3. State-Based (WHILE...THEN)
**Pattern**: WHILE [system state] THEN [system] SHALL [response]

**Examples**:
- WHILE backup is running THEN system SHALL display progress indicator
- WHILE user is typing THEN system SHALL show auto-suggestions
- WHILE data is loading THEN system SHALL show loading spinner

### 4. Feature-Specific (WHERE...THEN)
**Pattern**: WHERE [feature applies] THEN [system] SHALL [response]

**Examples**:
- WHERE user profile page THEN system SHALL display user information
- WHERE search results page THEN system SHALL highlight search terms
- WHERE mobile device THEN system SHALL use responsive layout

## Writing Guidelines

### Use Active Voice
- ✅ "system SHALL validate input"
- ❌ "input SHALL be validated"

### Be Specific
- ✅ "system SHALL display error message within 2 seconds"
- ❌ "system SHALL respond quickly"

### Use Measurable Criteria
- ✅ "system SHALL support up to 1000 concurrent users"
- ❌ "system SHALL handle many users"

### Include Error Conditions
- Normal flow: WHEN user submits valid form THEN system SHALL save data
- Error flow: WHEN user submits invalid form THEN system SHALL display validation errors

## Common Mistakes

1. **Vague Language**: Avoid subjective terms like "user-friendly", "fast", "intuitive"
2. **Implementation Details**: Focus on behavior, not how it's implemented
3. **Missing Conditions**: Specify when and where the requirement applies
4. **Untestable Criteria**: Ensure each criterion can be verified

## Validation Questions

For each EARS statement, ask:
- Is the trigger/condition clear and specific?
- Is the expected response measurable?
- Can this be tested automatically or manually?
- Are edge cases covered?"""

        return MethodologyGuide(
            topic=MethodologyTopic.EARS_FORMAT,
            title="EARS Format Guide",
            content=content,
            related_topics=[
                MethodologyTopic.REQUIREMENTS,
                MethodologyTopic.BEST_PRACTICES,
            ],
            examples=[
                "EARS pattern examples",
                "Good vs bad criteria",
                "Testing scenarios",
            ],
        )

    def _get_phase_transitions_guide(self) -> MethodologyGuide:
        """Get phase transition rules and approval process."""
        content = """# Phase Transitions Guide

## Overview

Phase transitions are critical checkpoints that ensure quality and completeness before proceeding to the next phase.

## Transition Rules

### Requirements → Design
**Prerequisites**:
- Requirements document is complete
- All user stories follow proper format
- Acceptance criteria use EARS format
- Edge cases and error conditions are covered
- **Explicit user approval is obtained**

**Transition Process**:
1. Present completed requirements document
2. Ask: "Do the requirements look good? If so, we can move on to the design."
3. Wait for explicit approval ("yes", "approved", "looks good")
4. If feedback is provided, make revisions and ask for approval again
5. Only proceed after clear approval

### Design → Tasks
**Prerequisites**:
- Design document addresses all requirements
- Architecture is clearly documented
- Components and interfaces are defined
- Data models are complete
- Error handling and testing strategies are included
- **Explicit user approval is obtained**

**Transition Process**:
1. Present completed design document
2. Ask: "Does the design look good? If so, we can move on to the implementation plan."
3. Wait for explicit approval
4. If feedback is provided, make revisions and ask for approval again
5. Only proceed after clear approval

### Tasks → Implementation
**Prerequisites**:
- All tasks reference specific requirements
- Tasks are actionable and coding-focused
- Implementation order is logical
- All requirements are covered by tasks
- **Explicit user approval is obtained**

**Transition Process**:
1. Present completed tasks document
2. Ask: "Do the tasks look good?"
3. Wait for explicit approval
4. If feedback is provided, make revisions and ask for approval again
5. Implementation can begin after approval

## Approval Requirements

### What Counts as Approval
- ✅ "Yes", "Approved", "Looks good", "Perfect"
- ✅ "Ready to proceed", "Let's move on"
- ✅ "That works", "Sounds good"

### What Doesn't Count as Approval
- ❌ Questions or requests for clarification
- ❌ Suggestions for changes
- ❌ Silence or no response
- ❌ "Maybe", "I think so", "Probably"

## Backward Navigation

### When to Go Back
- User requests changes to previous phase
- Gaps discovered during current phase
- Requirements change or evolve
- Design doesn't fully address requirements

### Process
1. Acknowledge the need to revisit previous phase
2. Make necessary updates to the earlier document
3. Get approval for the updated document
4. Proceed forward through phases again

## Quality Gates

### Requirements Phase
- [ ] All user stories are complete
- [ ] EARS format is used correctly
- [ ] Edge cases are covered
- [ ] Requirements are testable
- [ ] User has explicitly approved

### Design Phase
- [ ] All requirements are addressed
- [ ] Architecture is documented
- [ ] Components are defined
- [ ] Testing strategy is included
- [ ] User has explicitly approved

### Tasks Phase
- [ ] All tasks are actionable
- [ ] Requirements are referenced
- [ ] Implementation order is logical
- [ ] All requirements are covered
- [ ] User has explicitly approved

## Common Transition Issues

1. **Proceeding Without Approval**: Never assume approval; always ask explicitly
2. **Ignoring Feedback**: Address all user feedback before asking for approval again
3. **Skipping Phases**: Each phase must be completed and approved
4. **Poor Documentation**: Ensure documents are complete before seeking approval"""

        return MethodologyGuide(
            topic=MethodologyTopic.PHASE_TRANSITIONS,
            title="Phase Transitions Guide",
            content=content,
            related_topics=[MethodologyTopic.WORKFLOW, MethodologyTopic.BEST_PRACTICES],
            examples=[
                "Approval conversation examples",
                "Feedback handling",
                "Backward navigation scenarios",
            ],
        )

    def _get_best_practices_guide(self) -> MethodologyGuide:
        """Get best practices content."""
        content = """# Best Practices Guide

## General Principles

### 1. User-Centered Approach
- Always prioritize user needs and feedback
- Seek explicit approval at each phase
- Be responsive to user requests for changes
- Maintain clear communication throughout

### 2. Quality Over Speed
- Take time to create thorough, accurate documents
- Don't rush through phases to save time
- Validate each phase before proceeding
- Address feedback completely

### 3. Systematic Progression
- Follow the three-phase workflow consistently
- Don't skip phases or combine them
- Ensure each phase builds on the previous one
- Maintain traceability throughout

## Requirements Best Practices

### Writing User Stories
- Use specific roles (not just "user")
- Focus on user value and benefits
- Keep stories independent and testable
- Cover all user types and scenarios

### Acceptance Criteria
- Use EARS format consistently
- Cover normal flows, edge cases, and errors
- Make criteria specific and measurable
- Ensure criteria are testable

### Requirements Organization
- Use clear numbering and hierarchy
- Group related requirements logically
- Provide context in the introduction
- Keep requirements focused and atomic

## Design Best Practices

### Architecture Documentation
- Use diagrams to illustrate complex relationships
- Document key design decisions and rationales
- Consider scalability and maintainability
- Address security and performance concerns

### Component Design
- Define clear interfaces and responsibilities
- Minimize coupling between components
- Plan for testability and modularity
- Document dependencies and interactions

### Research Integration
- Conduct research during design phase
- Document findings and their impact on design
- Include relevant references and links
- Justify technology choices

## Tasks Best Practices

### Task Definition
- Make tasks specific and actionable
- Focus on coding activities only
- Ensure tasks build incrementally
- Reference specific requirements

### Task Organization
- Sequence tasks logically
- Start with foundational components
- Plan for early testing and validation
- Avoid orphaned or disconnected code

### Implementation Planning
- Prioritize test-driven development
- Plan for incremental delivery
- Consider dependencies and prerequisites
- Focus on core functionality first

## Common Anti-Patterns

### Requirements Phase
- ❌ Vague or subjective requirements
- ❌ Missing edge cases and error conditions
- ❌ Implementation details in requirements
- ❌ Proceeding without user approval

### Design Phase
- ❌ Skipping research and investigation
- ❌ Over-engineering or under-designing
- ❌ Poor documentation of decisions
- ❌ Not addressing all requirements

### Tasks Phase
- ❌ Including non-coding tasks
- ❌ Tasks that are too abstract or high-level
- ❌ Poor requirement traceability
- ❌ Illogical task sequencing

## Quality Assurance

### Document Review
- Check for completeness and accuracy
- Verify format compliance
- Ensure requirement traceability
- Validate against quality criteria

### User Feedback
- Present documents clearly
- Ask specific questions about approval
- Address all feedback thoroughly
- Confirm understanding of changes

### Continuous Improvement
- Learn from each spec development cycle
- Refine processes based on experience
- Update templates and guides as needed
- Share lessons learned with team"""

        return MethodologyGuide(
            topic=MethodologyTopic.BEST_PRACTICES,
            title="Best Practices Guide",
            content=content,
            related_topics=[
                MethodologyTopic.WORKFLOW,
                MethodologyTopic.REQUIREMENTS,
                MethodologyTopic.DESIGN,
                MethodologyTopic.TASKS,
            ],
            examples=[
                "Quality checklists",
                "Review processes",
                "Improvement strategies",
            ],
        )

    def _get_troubleshooting_guide(self) -> MethodologyGuide:
        """Get troubleshooting guides for common pitfalls."""
        content = """# Troubleshooting Guide

## Common Problems and Solutions

### Requirements Phase Issues

#### Problem: Vague or Unclear Requirements
**Symptoms**: Requirements use subjective language, lack specific criteria
**Solution**:
- Use EARS format for all acceptance criteria
- Replace subjective terms with measurable criteria
- Add specific examples and edge cases
- Ask clarifying questions about user needs

#### Problem: Missing Edge Cases
**Symptoms**: Only happy path scenarios are covered
**Solution**:
- Systematically consider error conditions
- Think about boundary cases and limits
- Consider different user types and permissions
- Add validation and security requirements

#### Problem: Requirements Stall or Go in Circles
**Symptoms**: Endless revisions without progress
**Solution**:
- Focus on one aspect at a time
- Provide specific examples and options
- Summarize what's been established
- Suggest moving to different requirement areas

### Design Phase Issues

#### Problem: Design Doesn't Address All Requirements
**Symptoms**: Some requirements are not covered in design
**Solution**:
- Create traceability matrix
- Review each requirement systematically
- Add missing design elements
- Update architecture to accommodate all needs

#### Problem: Over-Engineering or Under-Engineering
**Symptoms**: Design is too complex or too simple
**Solution**:
- Focus on current requirements, not future possibilities
- Ensure design addresses all stated needs
- Break complex designs into phases
- Validate design decisions against requirements

#### Problem: Insufficient Research
**Symptoms**: Technology choices are not justified
**Solution**:
- Research during design phase, not before
- Document key findings and decisions
- Include relevant links and references
- Justify choices based on requirements

### Tasks Phase Issues

#### Problem: Tasks Are Too Abstract
**Symptoms**: Tasks describe concepts rather than coding activities
**Solution**:
- Focus on specific implementation steps
- Break abstract tasks into concrete coding activities
- Specify files and components to create/modify
- Ensure tasks are immediately actionable

#### Problem: Poor Requirement Traceability
**Symptoms**: Tasks don't reference specific requirements
**Solution**:
- Add requirement references to each task
- Use granular references (1.1, 2.3) not just user stories
- Ensure all requirements are covered
- Create traceability matrix if needed

#### Problem: Illogical Task Sequence
**Symptoms**: Tasks have dependency issues or poor ordering
**Solution**:
- Start with foundational components
- Ensure each task builds on previous ones
- Plan for early testing and validation
- Avoid orphaned or disconnected code

### Workflow Issues

#### Problem: User Won't Approve Documents
**Symptoms**: User keeps requesting changes or seems unsatisfied
**Solution**:
- Ask specific questions about concerns
- Provide options when user is unsure
- Break down complex decisions
- Offer to return to previous phases if needed

#### Problem: Skipping Phases or Rushing
**Symptoms**: Pressure to move quickly through phases
**Solution**:
- Explain importance of systematic approach
- Show how skipping phases leads to problems later
- Focus on quality over speed
- Demonstrate value of each phase

#### Problem: Scope Creep During Development
**Symptoms**: New requirements emerge during design or tasks
**Solution**:
- Document new requirements properly
- Return to requirements phase if needed
- Get approval for scope changes
- Update design and tasks accordingly

## Recovery Strategies

### When Requirements Need Major Changes
1. Acknowledge the need for changes
2. Update requirements document completely
3. Get explicit approval for updated requirements
4. Update design to reflect new requirements
5. Revise tasks based on updated design

### When Design Has Fundamental Issues
1. Identify specific problems with current design
2. Conduct additional research if needed
3. Create revised design addressing issues
4. Ensure all requirements are still covered
5. Get approval before proceeding to tasks

### When Tasks Are Unworkable
1. Analyze why tasks are problematic
2. Return to design phase if architectural changes needed
3. Break down complex tasks into smaller ones
4. Improve requirement traceability
5. Resequence tasks for better flow

## Prevention Strategies

### Requirements Phase
- Use structured templates and formats
- Ask probing questions about edge cases
- Provide examples to clarify concepts
- Validate understanding with user

### Design Phase
- Research thoroughly during design
- Document all design decisions
- Create clear architecture diagrams
- Ensure comprehensive coverage

### Tasks Phase
- Focus on coding activities only
- Maintain clear requirement traceability
- Plan incremental development approach
- Validate task sequence and dependencies

## When to Seek Help

- User feedback is consistently negative
- Requirements seem impossible to satisfy
- Technical constraints conflict with requirements
- Workflow is stuck in endless loops
- Quality standards cannot be met

Remember: It's better to take time to get it right than to rush through and create problems later."""

        return MethodologyGuide(
            topic=MethodologyTopic.TROUBLESHOOTING,
            title="Troubleshooting Guide",
            content=content,
            related_topics=[
                MethodologyTopic.WORKFLOW,
                MethodologyTopic.BEST_PRACTICES,
                MethodologyTopic.PHASE_TRANSITIONS,
            ],
            examples=[
                "Problem scenarios",
                "Recovery procedures",
                "Prevention checklists",
            ],
        )

    def get_guide(self, topic: MethodologyTopic) -> Optional[MethodologyGuide]:
        """Get methodology guide by topic."""
        return self._guides.get(topic)

    def get_guide_content(self, topic: MethodologyTopic) -> str:
        """Get methodology guide content as string."""
        guide = self.get_guide(topic)
        return guide.content if guide else f"Guide not found for topic: {topic.value}"

    def get_all_topics(self) -> List[MethodologyTopic]:
        """Get list of all available methodology topics."""
        return list(self._guides.keys())

    def search_guides(self, query: str) -> List[MethodologyGuide]:
        """Search guides by content or title."""
        query_lower = query.lower()
        results = []

        for guide in self._guides.values():
            if (
                query_lower in guide.title.lower()
                or query_lower in guide.content.lower()
                or any(query_lower in example.lower() for example in guide.examples)
            ):
                results.append(guide)

        return results

    def get_related_guides(self, topic: MethodologyTopic) -> List[MethodologyGuide]:
        """Get guides related to the specified topic."""
        guide = self.get_guide(topic)
        if not guide:
            return []

        related = []
        for related_topic in guide.related_topics:
            related_guide = self.get_guide(related_topic)
            if related_guide:
                related.append(related_guide)

        return related

    def get_guide_by_phase(self, phase: str) -> Optional[MethodologyGuide]:
        """Get methodology guide for specific phase."""
        phase_mapping = {
            "requirements": MethodologyTopic.REQUIREMENTS,
            "design": MethodologyTopic.DESIGN,
            "tasks": MethodologyTopic.TASKS,
            "workflow": MethodologyTopic.WORKFLOW,
        }

        topic = phase_mapping.get(phase.lower())
        return self.get_guide(topic) if topic else None

    def _load_methodology_file(
        self, filename: str, topic: MethodologyTopic
    ) -> MethodologyGuide:
        """Load methodology guide from file."""
        try:
            from pathlib import Path

            methodology_path = Path(__file__).parent / "data" / "methodology" / filename
            if methodology_path.exists():
                content = methodology_path.read_text(encoding="utf-8")
                return MethodologyGuide(
                    topic=topic,
                    title=filename.replace(".md", "").replace("-", " ").title(),
                    content=content,
                    related_topics=[],
                    examples=[],
                )
            else:
                return self._get_fallback_guide(topic)
        except Exception:
            return self._get_fallback_guide(topic)

    def _get_fallback_guide(self, topic: MethodologyTopic) -> MethodologyGuide:
        """Get fallback guide for topic."""
        if topic == MethodologyTopic.WORKFLOW:
            return self._get_workflow_guide()
        elif topic == MethodologyTopic.EARS_FORMAT:
            return self._get_ears_format_guide()
        elif topic == MethodologyTopic.REQUIREMENTS:
            return self._get_requirements_guide()
        elif topic == MethodologyTopic.DESIGN:
            return self._get_design_guide()
        elif topic == MethodologyTopic.TASKS:
            return self._get_tasks_guide()
        elif topic == MethodologyTopic.PHASE_TRANSITIONS:
            return self._get_phase_transitions_guide()
        elif topic == MethodologyTopic.BEST_PRACTICES:
            return self._get_best_practices_guide()
        elif topic == MethodologyTopic.TROUBLESHOOTING:
            return self._get_troubleshooting_guide()
        else:
            return MethodologyGuide(
                topic=topic,
                title=topic.value.replace("_", " ").title(),
                content=f"# {topic.value.replace('_', ' ').title()}\n\n指南内容正在开发中...",
                related_topics=[],
                examples=[],
            )

    def get_guide(
        self, topic: MethodologyTopic, language: str = "en"
    ) -> Optional[MethodologyGuide]:
        """Get methodology guide for specific topic."""
        if language == "zh":
            guide_key = f"{topic.value}-zh"
        else:
            guide_key = topic.value
        return self._guides.get(guide_key)

    def list_available_guides(self, language: str = "en") -> List[str]:
        """List all available methodology guides."""
        if language == "zh":
            return [key for key in self._guides.keys() if key.endswith("-zh")]
        else:
            return [key for key in self._guides.keys() if not key.endswith("-zh")]

    def get_all_guides(self, language: str = "en") -> Dict[str, MethodologyGuide]:
        """Get all methodology guides."""
        if language == "zh":
            return {k: v for k, v in self._guides.items() if k.endswith("-zh")}
        else:
            return {k: v for k, v in self._guides.items() if not k.endswith("-zh")}
