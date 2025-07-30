"""MCP tools for workflow management (phase transitions, state tracking)."""

from typing import Any, Dict, List

from mcp.types import TextContent, Tool

from ..workflow.models import PhaseStatus, PhaseType
from ..workflow.phase_manager import PhaseManager
from ..workflow.state_tracker import StateTracker


class WorkflowManagementTools:
    """MCP tools for managing spec-driven development workflow."""

    def __init__(self):
        """Initialize workflow management tools."""
        self.phase_manager = PhaseManager()
        self.state_tracker = StateTracker()

    def get_tool_definitions(self) -> List[Tool]:
        """Get MCP tool definitions for workflow management."""
        return [
            Tool(
                name="create_workflow",
                description="Create a new spec workflow for a feature",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature to create workflow for",
                        }
                    },
                    "required": ["feature_name"],
                },
            ),
            Tool(
                name="get_workflow_status",
                description="Get current workflow status and phase information",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature to check status for",
                        }
                    },
                    "required": ["feature_name"],
                },
            ),
            Tool(
                name="transition_phase",
                description="Transition workflow to next phase or approve current phase",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature",
                        },
                        "action": {
                            "type": "string",
                            "enum": ["start", "complete", "approve"],
                            "description": "Action to perform on current phase",
                        },
                        "phase": {
                            "type": "string",
                            "enum": ["requirements", "design", "tasks"],
                            "description": "Optional specific phase to act on",
                        },
                    },
                    "required": ["feature_name", "action"],
                },
            ),
            Tool(
                name="navigate_backward",
                description="Navigate backward to modify a previous phase",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature",
                        },
                        "target_phase": {
                            "type": "string",
                            "enum": ["requirements", "design"],
                            "description": "Phase to navigate back to",
                        },
                    },
                    "required": ["feature_name", "target_phase"],
                },
            ),
            Tool(
                name="check_transition_requirements",
                description="Check if workflow can transition to a specific phase",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature",
                        },
                        "target_phase": {
                            "type": "string",
                            "enum": ["requirements", "design", "tasks"],
                            "description": "Phase to check transition requirements for",
                        },
                    },
                    "required": ["feature_name", "target_phase"],
                },
            ),
            Tool(
                name="get_approval_guidance",
                description="Get guidance on what approval is needed for current phase",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "feature_name": {
                            "type": "string",
                            "description": "Name of the feature",
                        }
                    },
                    "required": ["feature_name"],
                },
            ),
        ]

    async def handle_create_workflow(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle create_workflow tool call."""
        feature_name = arguments.get("feature_name", "")

        if not feature_name:
            return [TextContent(type="text", text="Error: feature_name is required")]

        try:
            # Create workflow
            workflow_state = self.phase_manager.create_workflow(feature_name)
            self.state_tracker.track_workflow(workflow_state)

            # Format response
            response = f"""# Workflow Created: {feature_name}

## Initial State
- **Current Phase**: {workflow_state.current_phase.value}
- **Status**: {workflow_state.phase_status[workflow_state.current_phase].value}
- **Requires Approval**: {workflow_state.requires_approval}
- **Can Proceed**: {workflow_state.can_proceed}

## Next Steps
1. Start the requirements phase by gathering feature requirements
2. Create requirements document following EARS format
3. Get explicit user approval before proceeding to design

## Phase Overview
- **Requirements**: Define what the feature should do
- **Design**: Plan how the feature will be implemented
- **Tasks**: Break down implementation into actionable steps

Use `get_workflow_status` to check progress at any time.
"""

            return [TextContent(type="text", text=response)]

        except Exception as e:
            from ..error_handler import get_error_handler

            error_handler = get_error_handler()

            try:
                error = error_handler.handle_workflow_error(
                    message=f"Failed to create workflow for feature '{feature_name}': {str(e)}",
                    attempted_action="workflow_creation",
                    context={"feature_name": feature_name, "original_error": str(e)},
                )
                return [TextContent(type="text", text=error.get_formatted_message())]
            except Exception:
                return [
                    TextContent(type="text", text=f"Error creating workflow: {str(e)}")
                ]

    async def handle_get_workflow_status(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_workflow_status tool call."""
        feature_name = arguments.get("feature_name", "")

        if not feature_name:
            return [TextContent(type="text", text="Error: feature_name is required")]

        try:
            # Get workflow summary
            summary = self.state_tracker.get_workflow_summary(feature_name)

            if not summary:
                return [
                    TextContent(
                        type="text",
                        text=f"No workflow found for feature: {feature_name}",
                    )
                ]

            # Format detailed status
            response = f"""# Workflow Status: {feature_name}

## Current State
- **Current Phase**: {summary['current_phase']}
- **Completion**: {summary['completion_percentage']:.1%}
- **Requires Approval**: {'Yes' if summary['requires_approval'] else 'No'}
- **Can Proceed**: {'Yes' if summary['can_proceed'] else 'No'}
- **Workflow Complete**: {'Yes' if summary['is_complete'] else 'No'}

## Phase Status
"""

            # Add phase status details
            phase_icons = {
                "not_started": "⏸️",
                "in_progress": "🔄",
                "review": "👀",
                "approved": "✅",
            }

            for phase, status in summary["phase_statuses"].items():
                icon = phase_icons.get(status, "❓")
                response += f"- **{phase.title()}**: {icon} {status.replace('_', ' ').title()}\n"

            # Add navigation info
            response += "\n## Navigation\n"
            if summary["next_phase"]:
                response += f"- **Next Phase**: {summary['next_phase']}\n"
            if summary["previous_phase"]:
                response += f"- **Previous Phase**: {summary['previous_phase']}\n"

            # Add guidance based on current state
            response += "\n## Current Actions Available\n"

            current_phase = summary["current_phase"]
            current_status = summary["phase_statuses"][current_phase]

            if current_status == "not_started":
                response += f"- Start working on {current_phase} phase\n"
                response += f"- Use `transition_phase` with action 'start' to begin\n"
            elif current_status == "in_progress":
                response += f"- Continue working on {current_phase} phase\n"
                response += f"- Use `transition_phase` with action 'complete' when ready for review\n"
            elif current_status == "review":
                response += f"- {current_phase.title()} phase is ready for approval\n"
                response += f"- Use `transition_phase` with action 'approve' after user approval\n"
            elif current_status == "approved" and not summary["is_complete"]:
                if summary["can_proceed"]:
                    response += (
                        f"- Ready to move to next phase: {summary['next_phase']}\n"
                    )
                    response += (
                        f"- Use `transition_phase` with action 'start' for next phase\n"
                    )

            # Add backward navigation options
            if summary["previous_phase"]:
                response += f"- Can navigate back to {summary['previous_phase']} phase if changes needed\n"
                response += f"- Use `navigate_backward` to return to previous phase\n"

            response += f"\n**Last Updated**: {summary['last_updated']}"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            from ..error_handler import get_error_handler

            error_handler = get_error_handler()

            try:
                error = error_handler.handle_workflow_error(
                    message=f"Failed to get workflow status for feature '{feature_name}': {str(e)}",
                    attempted_action="status_query",
                    context={"feature_name": feature_name, "original_error": str(e)},
                )
                return [TextContent(type="text", text=error.get_formatted_message())]
            except Exception:
                return [
                    TextContent(
                        type="text", text=f"Error getting workflow status: {str(e)}"
                    )
                ]

    async def handle_transition_phase(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle transition_phase tool call."""
        feature_name = arguments.get("feature_name", "")
        action = arguments.get("action", "")
        phase_str = arguments.get("phase")

        if not feature_name or not action:
            return [
                TextContent(
                    type="text", text="Error: feature_name and action are required"
                )
            ]

        try:
            # Get current workflow
            workflow = self.phase_manager.get_workflow(feature_name)
            if not workflow:
                return [
                    TextContent(
                        type="text",
                        text=f"No workflow found for feature: {feature_name}",
                    )
                ]

            # Determine target phase
            if phase_str:
                try:
                    target_phase = PhaseType(phase_str)
                except ValueError:
                    return [
                        TextContent(type="text", text=f"Invalid phase: {phase_str}")
                    ]
            else:
                target_phase = workflow.current_phase

            # Perform action
            if action == "start":
                workflow = self._start_phase(feature_name, target_phase)
            elif action == "complete":
                workflow = self._complete_phase(feature_name, target_phase)
            elif action == "approve":
                workflow = self._approve_phase(feature_name, target_phase)
            else:
                return [
                    TextContent(
                        type="text",
                        text=f"Invalid action: {action}. Use 'start', 'complete', or 'approve'",
                    )
                ]

            # Update state tracker
            self.state_tracker.update_workflow_state(workflow)

            # Record approval if applicable
            if action == "approve":
                self.state_tracker.record_approval(feature_name, target_phase, True)

            # Format response
            response = f"""# Phase Transition: {feature_name}

## Action Completed
- **Action**: {action.title()} {target_phase.value} phase
- **New Status**: {workflow.phase_status[target_phase].value}
- **Current Phase**: {workflow.current_phase.value}

## Updated State
- **Requires Approval**: {'Yes' if workflow.requires_approval else 'No'}
- **Can Proceed**: {'Yes' if workflow.can_proceed else 'No'}

## Next Steps
"""

            # Add guidance for next steps
            if action == "start":
                response += f"- Begin working on {target_phase.value} phase\n"
                response += f"- Use appropriate templates and methodology guides\n"
                response += (
                    f"- Complete the phase and use 'complete' action when ready\n"
                )
            elif action == "complete":
                response += (
                    f"- {target_phase.value.title()} phase is now ready for review\n"
                )
                response += f"- Present the completed document to user for approval\n"
                response += (
                    f"- Use 'approve' action after receiving explicit user approval\n"
                )
            elif action == "approve":
                if workflow.can_proceed:
                    next_phase = self.state_tracker.get_next_phase(feature_name)
                    if next_phase:
                        response += f"- Ready to start {next_phase.value} phase\n"
                        response += f"- Use 'start' action to begin next phase\n"
                    else:
                        response += "- Workflow is complete! All phases approved.\n"
                        response += "- Ready to begin implementation of tasks\n"
                else:
                    response += f"- {target_phase.value.title()} phase approved\n"
                    response += f"- Continue with current workflow\n"

            return [TextContent(type="text", text=response)]

        except ValueError as e:
            from ..error_handler import get_error_handler

            error_handler = get_error_handler()

            try:
                error = error_handler.handle_workflow_error(
                    message=f"Invalid phase transition: {str(e)}",
                    current_phase=phase_str,
                    attempted_action="phase_transition",
                    context={
                        "feature_name": feature_name,
                        "action": action,
                        "phase": phase_str,
                    },
                )
                return [TextContent(type="text", text=error.get_formatted_message())]
            except Exception:
                return [TextContent(type="text", text=f"Transition error: {str(e)}")]
        except Exception as e:
            from ..error_handler import get_error_handler

            error_handler = get_error_handler()

            try:
                error = error_handler.handle_workflow_error(
                    message=f"Failed to transition phase: {str(e)}",
                    current_phase=phase_str,
                    attempted_action="phase_transition",
                    context={
                        "feature_name": feature_name,
                        "action": action,
                        "phase": phase_str,
                        "original_error": str(e),
                    },
                )
                return [TextContent(type="text", text=error.get_formatted_message())]
            except Exception:
                return [
                    TextContent(
                        type="text", text=f"Error during phase transition: {str(e)}"
                    )
                ]

    def _start_phase(self, feature_name: str, phase: PhaseType):
        """Start a specific phase."""
        if phase == PhaseType.REQUIREMENTS:
            return self.phase_manager.start_requirements_phase(feature_name)
        elif phase == PhaseType.DESIGN:
            return self.phase_manager.start_design_phase(feature_name)
        elif phase == PhaseType.TASKS:
            return self.phase_manager.start_tasks_phase(feature_name)
        else:
            raise ValueError(f"Cannot start unknown phase: {phase}")

    def _complete_phase(self, feature_name: str, phase: PhaseType):
        """Complete a specific phase."""
        if phase == PhaseType.REQUIREMENTS:
            return self.phase_manager.complete_requirements_phase(feature_name)
        elif phase == PhaseType.DESIGN:
            return self.phase_manager.complete_design_phase(feature_name)
        elif phase == PhaseType.TASKS:
            return self.phase_manager.complete_tasks_phase(feature_name)
        else:
            raise ValueError(f"Cannot complete unknown phase: {phase}")

    def _approve_phase(self, feature_name: str, phase: PhaseType):
        """Approve a specific phase."""
        if phase == PhaseType.REQUIREMENTS:
            return self.phase_manager.approve_requirements_phase(feature_name)
        elif phase == PhaseType.DESIGN:
            return self.phase_manager.approve_design_phase(feature_name)
        elif phase == PhaseType.TASKS:
            return self.phase_manager.approve_tasks_phase(feature_name)
        else:
            raise ValueError(f"Cannot approve unknown phase: {phase}")

    async def handle_navigate_backward(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle navigate_backward tool call."""
        feature_name = arguments.get("feature_name", "")
        target_phase_str = arguments.get("target_phase", "")

        if not feature_name or not target_phase_str:
            return [
                TextContent(
                    type="text",
                    text="Error: feature_name and target_phase are required",
                )
            ]

        try:
            target_phase = PhaseType(target_phase_str)
        except ValueError:
            return [
                TextContent(
                    type="text", text=f"Invalid target phase: {target_phase_str}"
                )
            ]

        try:
            # Check if backward navigation is allowed
            can_navigate = self.state_tracker.can_navigate_backward(
                feature_name, target_phase
            )

            if not can_navigate:
                return [
                    TextContent(
                        type="text",
                        text=f"Cannot navigate backward to {target_phase.value} phase from current state",
                    )
                ]

            # Perform backward navigation
            success = self.state_tracker.navigate_backward(feature_name, target_phase)

            if not success:
                return [
                    TextContent(
                        type="text",
                        text=f"Failed to navigate backward to {target_phase.value} phase",
                    )
                ]

            # Get updated workflow state
            workflow = self.phase_manager.get_workflow(feature_name)
            if workflow:
                self.state_tracker.update_workflow_state(workflow)

            response = f"""# Backward Navigation: {feature_name}

## Navigation Completed
- **Target Phase**: {target_phase.value}
- **Current Phase**: {target_phase.value}
- **Status**: in_progress (ready for modifications)

## Impact
- Current phase reset to in_progress
- All subsequent phases reset to not_started
- Previous work in later phases will need to be redone

## Next Steps
1. Make necessary modifications to {target_phase.value} phase
2. Complete the phase when modifications are done
3. Get user approval before proceeding
4. Subsequent phases will need to be updated based on changes

## Warning
Backward navigation resets progress in later phases. Ensure this is necessary before proceeding.
"""

            return [TextContent(type="text", text=response)]

        except Exception as e:
            from ..error_handler import get_error_handler

            error_handler = get_error_handler()

            try:
                error = error_handler.handle_workflow_error(
                    message=f"Failed to navigate backward: {str(e)}",
                    attempted_action="backward_navigation",
                    context={
                        "feature_name": feature_name,
                        "target_phase": target_phase_str,
                        "original_error": str(e),
                    },
                )
                return [TextContent(type="text", text=error.get_formatted_message())]
            except Exception:
                return [
                    TextContent(
                        type="text", text=f"Error during backward navigation: {str(e)}"
                    )
                ]

    async def handle_check_transition_requirements(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle check_transition_requirements tool call."""
        feature_name = arguments.get("feature_name", "")
        target_phase_str = arguments.get("target_phase", "")

        if not feature_name or not target_phase_str:
            return [
                TextContent(
                    type="text",
                    text="Error: feature_name and target_phase are required",
                )
            ]

        try:
            target_phase = PhaseType(target_phase_str)
        except ValueError:
            return [
                TextContent(
                    type="text", text=f"Invalid target phase: {target_phase_str}"
                )
            ]

        try:
            # Check transition requirements
            can_transition = self.phase_manager.can_transition_to_phase(
                feature_name, target_phase
            )

            # Get current workflow state
            workflow = self.phase_manager.get_workflow(feature_name)
            if not workflow:
                return [
                    TextContent(
                        type="text",
                        text=f"No workflow found for feature: {feature_name}",
                    )
                ]

            response = f"""# Transition Requirements Check: {feature_name}

## Target Phase: {target_phase.value}
- **Can Transition**: {'Yes' if can_transition else 'No'}

## Current State
- **Current Phase**: {workflow.current_phase.value}
- **Current Status**: {workflow.phase_status[workflow.current_phase].value}

## Requirements for {target_phase.value} Phase
"""

            if target_phase == PhaseType.REQUIREMENTS:
                response += "- No prerequisites (can always return to requirements)\n"
                response += "- Used for starting new workflows or making changes\n"
            elif target_phase == PhaseType.DESIGN:
                req_status = workflow.phase_status[PhaseType.REQUIREMENTS]
                response += f"- Requirements phase must be approved (currently: {req_status.value})\n"
                if req_status != PhaseStatus.APPROVED:
                    response += "- ❌ Requirements phase needs approval before design can start\n"
                else:
                    response += "- ✅ Requirements approved, design phase can start\n"
            elif target_phase == PhaseType.TASKS:
                req_status = workflow.phase_status[PhaseType.REQUIREMENTS]
                design_status = workflow.phase_status[PhaseType.DESIGN]
                response += f"- Requirements phase must be approved (currently: {req_status.value})\n"
                response += f"- Design phase must be approved (currently: {design_status.value})\n"

                if req_status != PhaseStatus.APPROVED:
                    response += "- ❌ Requirements phase needs approval\n"
                else:
                    response += "- ✅ Requirements approved\n"

                if design_status != PhaseStatus.APPROVED:
                    response += "- ❌ Design phase needs approval\n"
                else:
                    response += "- ✅ Design approved\n"

            # Add recommendations
            response += "\n## Recommendations\n"
            if can_transition:
                response += f"- Ready to transition to {target_phase.value} phase\n"
                response += f"- Use `transition_phase` with action 'start' to begin\n"
            else:
                response += "- Complete and approve prerequisite phases first\n"
                response += "- Check workflow status for current phase requirements\n"

            return [TextContent(type="text", text=response)]

        except Exception as e:
            from ..error_handler import get_error_handler

            error_handler = get_error_handler()

            try:
                error = error_handler.handle_workflow_error(
                    message=f"Failed to check transition requirements: {str(e)}",
                    attempted_action="transition_check",
                    context={"feature_name": feature_name, "original_error": str(e)},
                )
                return [TextContent(type="text", text=error.get_formatted_message())]
            except Exception:
                return [
                    TextContent(
                        type="text",
                        text=f"Error checking transition requirements: {str(e)}",
                    )
                ]

    async def handle_get_approval_guidance(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_approval_guidance tool call."""
        feature_name = arguments.get("feature_name", "")

        if not feature_name:
            return [TextContent(type="text", text="Error: feature_name is required")]

        try:
            # Get workflow state
            workflow = self.phase_manager.get_workflow(feature_name)
            if not workflow:
                return [
                    TextContent(
                        type="text",
                        text=f"No workflow found for feature: {feature_name}",
                    )
                ]

            current_phase = workflow.current_phase
            current_status = workflow.phase_status[current_phase]

            response = f"""# Approval Guidance: {feature_name}

## Current Phase: {current_phase.value}
- **Status**: {current_status.value}
- **Requires Approval**: {'Yes' if workflow.requires_approval else 'No'}

## Approval Process for {current_phase.value.title()} Phase
"""

            if current_status == PhaseStatus.NOT_STARTED:
                response += """
### Phase Not Started
- Start working on the phase first
- Use `transition_phase` with action 'start'
- Complete the phase before seeking approval
"""
            elif current_status == PhaseStatus.IN_PROGRESS:
                response += f"""
### Phase In Progress
- Continue working on {current_phase.value} document
- Complete all required sections and content
- Use `transition_phase` with action 'complete' when ready
- Then present document to user for approval
"""
            elif current_status == PhaseStatus.REVIEW:
                response += f"""
### Ready for Approval
The {current_phase.value} phase is complete and ready for user approval.

#### What to Present to User
- Show the completed {current_phase.value} document
- Highlight key sections and decisions
- Ask for explicit approval using specific language

#### Approval Questions to Ask User
"""

                if current_phase == PhaseType.REQUIREMENTS:
                    response += '- "Do the requirements look good? If so, we can move on to the design."\n'
                elif current_phase == PhaseType.DESIGN:
                    response += '- "Does the design look good? If so, we can move on to the implementation plan."\n'
                elif current_phase == PhaseType.TASKS:
                    response += '- "Do the tasks look good?"\n'

                response += """
#### What Counts as Approval
- ✅ "Yes", "Approved", "Looks good", "Perfect"
- ✅ "Ready to proceed", "Let's move on"
- ✅ "That works", "Sounds good"

#### What Doesn't Count as Approval
- ❌ Questions or requests for clarification
- ❌ Suggestions for changes
- ❌ Silence or no response
- ❌ "Maybe", "I think so", "Probably"

#### After Getting Approval
- Use `transition_phase` with action 'approve'
- This will move workflow to next phase
- Begin working on next phase when ready
"""
            elif current_status == PhaseStatus.APPROVED:
                response += f"""
### Phase Already Approved
- {current_phase.value.title()} phase is already approved
- Ready to move to next phase or workflow is complete
- Use `get_workflow_status` to see next steps
"""

            # Add handling feedback section
            response += """
## Handling User Feedback

### If User Requests Changes
1. Make the requested modifications to the document
2. Present updated document to user
3. Ask for approval again using the same questions
4. Repeat until explicit approval is received

### If User Has Questions
1. Answer questions thoroughly
2. Make any necessary clarifications in document
3. Present updated document
4. Ask for approval again

### If User Seems Unsure
1. Offer specific options or examples
2. Break down complex decisions into smaller parts
3. Provide additional context or methodology guidance
4. Ask targeted questions to understand concerns

## Important Notes
- Never proceed without explicit approval
- Address all feedback before asking for approval again
- Be prepared to iterate multiple times
- User approval is required for quality assurance
"""

            return [TextContent(type="text", text=response)]

        except Exception as e:
            from ..error_handler import get_error_handler

            error_handler = get_error_handler()

            try:
                error = error_handler.handle_workflow_error(
                    message=f"Failed to get approval guidance: {str(e)}",
                    attempted_action="approval_guidance",
                    context={"feature_name": feature_name, "original_error": str(e)},
                )
                return [TextContent(type="text", text=error.get_formatted_message())]
            except Exception:
                return [
                    TextContent(
                        type="text", text=f"Error getting approval guidance: {str(e)}"
                    )
                ]

    async def handle_tool_call(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle MCP tool calls for workflow management."""
        handlers = {
            "create_workflow": self.handle_create_workflow,
            "get_workflow_status": self.handle_get_workflow_status,
            "transition_phase": self.handle_transition_phase,
            "navigate_backward": self.handle_navigate_backward,
            "check_transition_requirements": self.handle_check_transition_requirements,
            "get_approval_guidance": self.handle_get_approval_guidance,
        }

        handler = handlers.get(name)
        if not handler:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return await handler(arguments)
