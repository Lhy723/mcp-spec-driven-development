# Phase Transitions and Approval Process

## Overview

Phase transitions are critical quality gates in the spec-driven development process. Each transition requires explicit stakeholder approval and ensures completeness before proceeding to the next phase.

## Transition Requirements

### Requirements → Design Transition

**Prerequisites**:
- [ ] Requirements document is complete and well-structured
- [ ] All user stories follow proper format ("As a [role], I want [feature], so that [benefit]")
- [ ] Acceptance criteria use EARS format consistently
- [ ] Edge cases and error conditions are documented
- [ ] Requirements are testable and specific
- [ ] Document has been reviewed for quality and completeness

**Approval Process**:
1. Present completed requirements document to stakeholder
2. Ask explicitly: "Do the requirements look good? If so, we can move on to the design."
3. Wait for clear, explicit approval
4. If feedback is provided, address all concerns completely
5. Re-present updated document and ask for approval again
6. Only proceed to design phase after receiving explicit approval

**What Constitutes Approval**:
- ✅ "Yes", "Approved", "Looks good", "Perfect"
- ✅ "Ready to proceed", "Let's move on", "That works"
- ✅ "Sounds good", "I'm satisfied", "Go ahead"

**What Does NOT Constitute Approval**:
- ❌ Questions or requests for clarification
- ❌ Suggestions for changes or improvements
- ❌ Silence or no response
- ❌ Tentative responses like "Maybe", "I think so", "Probably"

### Design → Tasks Transition

**Prerequisites**:
- [ ] Design document addresses all requirements comprehensively
- [ ] Architecture is clearly documented with diagrams where appropriate
- [ ] Components and interfaces are well-defined
- [ ] Data models are complete and validated
- [ ] Error handling strategies are documented
- [ ] Testing approach is outlined
- [ ] All design decisions are justified

**Approval Process**:
1. Present completed design document to stakeholder
2. Ask explicitly: "Does the design look good? If so, we can move on to the implementation plan."
3. Wait for clear, explicit approval
4. If feedback is provided, address all concerns completely
5. Re-present updated document and ask for approval again
6. Only proceed to tasks phase after receiving explicit approval

### Tasks → Implementation Transition

**Prerequisites**:
- [ ] All tasks are actionable and coding-focused
- [ ] Each task references specific requirements
- [ ] Implementation order is logical and incremental
- [ ] All requirements are covered by tasks
- [ ] Tasks are appropriately scoped and manageable
- [ ] Dependencies between tasks are clear

**Approval Process**:
1. Present completed tasks document to stakeholder
2. Ask explicitly: "Do the tasks look good?"
3. Wait for clear, explicit approval
4. If feedback is provided, address all concerns completely
5. Re-present updated document and ask for approval again
6. Implementation can begin after receiving explicit approval

## Handling Feedback

### Feedback Response Process
1. **Acknowledge**: Confirm understanding of the feedback
2. **Clarify**: Ask questions if feedback is unclear
3. **Address**: Make all requested changes completely
4. **Validate**: Ensure changes don't break other parts
5. **Re-present**: Show updated document for approval

### Types of Feedback

#### Clarification Requests
- Stakeholder asks questions about content
- Provide clear explanations
- Update document if clarification reveals gaps

#### Change Requests
- Stakeholder requests modifications
- Make all requested changes
- Ensure changes are consistent throughout document

#### Additional Requirements
- New requirements emerge during review
- Document new requirements properly
- Update subsequent sections as needed

## Backward Navigation

### When to Go Back
- Stakeholder requests changes to previous phase
- Gaps discovered during current phase development
- Requirements evolve or change significantly
- Design doesn't adequately address requirements

### Backward Navigation Process
1. **Identify the Issue**: Clearly understand what needs to change
2. **Return to Appropriate Phase**: Go back to the phase that needs updates
3. **Make Necessary Changes**: Update the document completely
4. **Get Approval**: Obtain explicit approval for updated document
5. **Progress Forward**: Move through subsequent phases again

### Common Backward Navigation Scenarios

#### During Design Phase
- Requirements are incomplete or unclear
- New requirements are discovered
- Existing requirements need modification

#### During Tasks Phase
- Design doesn't address all requirements
- Architecture needs significant changes
- New design elements are needed

## Quality Gates

### Requirements Phase Quality Gate
- [ ] Document structure follows template
- [ ] All user stories are complete and properly formatted
- [ ] EARS format is used correctly for acceptance criteria
- [ ] Edge cases and error conditions are covered
- [ ] Requirements are testable and specific
- [ ] Stakeholder has provided explicit approval

### Design Phase Quality Gate
- [ ] All requirements are addressed in design
- [ ] Architecture is clearly documented
- [ ] Components and interfaces are defined
- [ ] Data models are complete
- [ ] Error handling is comprehensive
- [ ] Testing strategy is included
- [ ] Stakeholder has provided explicit approval

### Tasks Phase Quality Gate
- [ ] All tasks are actionable coding activities
- [ ] Each task references specific requirements
- [ ] Implementation order is logical
- [ ] All requirements are covered by tasks
- [ ] Task dependencies are clear
- [ ] Stakeholder has provided explicit approval

## Best Practices for Transitions

### Communication
- Be clear and direct when asking for approval
- Use specific language: "Do the [phase] look good?"
- Don't assume approval; always ask explicitly
- Confirm understanding of any feedback

### Documentation
- Keep documents updated and consistent
- Maintain version history of changes
- Document rationale for significant changes
- Ensure traceability between phases

### Process Management
- Don't rush through approval processes
- Allow adequate time for stakeholder review
- Be prepared to iterate multiple times
- Focus on quality over speed

## Troubleshooting Transitions

### Stakeholder Won't Approve
- Ask specific questions about concerns
- Provide options when stakeholder is unsure
- Break down complex decisions into smaller parts
- Offer to return to previous phases if needed

### Endless Revision Cycles
- Focus on one aspect at a time
- Provide concrete examples and options
- Summarize what has been established
- Suggest moving to different areas if stuck

### Scope Creep
- Document new requirements properly
- Assess impact on existing work
- Get approval for scope changes
- Update all affected documents

The approval process is fundamental to spec-driven development success. It ensures stakeholder satisfaction, maintains quality standards, and provides clear checkpoints for project progression.
