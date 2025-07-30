"""MCP tools for content access (templates, methodology, examples)."""

from typing import Any, Dict, List, Optional

from mcp.types import TextContent, Tool

from ..content.content_loader import ContentLoader
from ..content.methodology import MethodologyGuides, MethodologyTopic
from ..content.templates import TemplateRepository, TemplateType


class ContentAccessTools:
    """MCP tools for accessing spec-driven development content."""

    def __init__(self):
        """Initialize content access tools."""
        self.content_loader = ContentLoader()
        self.template_repo = TemplateRepository()
        self.methodology_guides = MethodologyGuides()

    def get_tool_definitions(self) -> List[Tool]:
        """Get MCP tool definitions for content access."""
        return [
            Tool(
                name="get_template",
                description="Get template for spec document creation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "template_type": {
                            "type": "string",
                            "enum": ["requirements", "design", "tasks"],
                            "description": "Type of template to retrieve",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["en", "zh"],
                            "description": "Language for template (en=English, zh=Chinese)",
                            "default": "en",
                        },
                        "feature_name": {
                            "type": "string",
                            "description": "Optional feature name for template customization",
                        },
                        "context": {
                            "type": "object",
                            "description": "Optional context data for template rendering",
                        },
                    },
                    "required": ["template_type"],
                },
            ),
            Tool(
                name="get_methodology_guide",
                description="Get spec-driven development methodology documentation",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "topic": {
                            "type": "string",
                            "enum": [
                                "workflow",
                                "requirements",
                                "design",
                                "tasks",
                                "ears_format",
                                "phase_transitions",
                                "best_practices",
                                "troubleshooting",
                            ],
                            "description": "Methodology topic to retrieve",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["en", "zh"],
                            "description": "Language for guide (en=English, zh=Chinese)",
                            "default": "en",
                        },
                    },
                    "required": ["topic"],
                },
            ),
            Tool(
                name="list_available_content",
                description="List all available content types and topics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "content_type": {
                            "type": "string",
                            "enum": ["templates", "methodology", "all"],
                            "description": "Type of content to list",
                        },
                        "language": {
                            "type": "string",
                            "enum": ["en", "zh"],
                            "description": "Language for content (en=English, zh=Chinese)",
                            "default": "en",
                        },
                    },
                    "required": ["content_type"],
                },
            ),
            Tool(
                name="get_examples_and_case_studies",
                description="Get examples and case studies for spec development",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "category": {
                            "type": "string",
                            "enum": [
                                "requirements",
                                "design",
                                "tasks",
                                "validation",
                                "pitfalls",
                                "complete_specs",
                            ],
                            "description": "Category of examples to retrieve",
                        },
                        "specific_topic": {
                            "type": "string",
                            "description": "Optional specific topic within the category",
                        },
                    },
                    "required": ["category"],
                },
            ),
        ]

    async def handle_get_template(self, arguments: Dict[str, Any]) -> List[TextContent]:
        """Handle get_template tool call."""
        template_type_str = arguments.get("template_type", "requirements")
        feature_name = arguments.get("feature_name", "")
        context = arguments.get("context", {})
        language = arguments.get("language", "en")

        try:
            # Convert string to enum
            template_type = TemplateType(template_type_str)

            # Get template content with language support
            content = self.template_repo.get_template(template_type, language)

            if not content:
                # Fallback to English if Chinese not available
                if language == "zh":
                    content = self.template_repo.get_template(template_type, "en")
                    content = f"# 注意：中文模板暂不可用，显示英文版本\n\n{content}"

            return [TextContent(type="text", text=content)]

        except ValueError as e:
            error_msg = f"Invalid template type '{template_type_str}'. Available types: requirements, design, tasks"
            return [TextContent(type="text", text=f"Error: {error_msg}")]
        except Exception as e:
            return [
                TextContent(type="text", text=f"Error retrieving template: {str(e)}")
            ]

    async def handle_get_methodology_guide(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_methodology_guide tool call."""
        topic_str = arguments.get("topic", "workflow")
        language = arguments.get("language", "en")

        try:
            # Convert string to enum
            topic = MethodologyTopic(topic_str)

            # Get methodology content with language support
            guide = self.methodology_guides.get_guide(topic, language)

            if guide:
                content = guide.content
            else:
                # Fallback to English if Chinese not available
                if language == "zh":
                    guide = self.methodology_guides.get_guide(topic, "en")
                    if guide:
                        content = f"# 注意：中文指南暂不可用，显示英文版本\n\n{guide.content}"
                    else:
                        content = f"指南 '{topic_str}' 不可用"
                else:
                    content = f"Guide '{topic_str}' not available"

            return [TextContent(type="text", text=content)]

        except ValueError:
            available_topics = [topic.value for topic in MethodologyTopic]
            error_msg = f"Invalid topic '{topic_str}'. Available topics: {', '.join(available_topics)}"
            return [TextContent(type="text", text=f"Error: {error_msg}")]
        except Exception as e:
            return [
                TextContent(
                    type="text", text=f"Error retrieving methodology guide: {str(e)}"
                )
            ]

    async def handle_list_available_content(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle list_available_content tool call."""
        content_type = arguments.get("content_type", "all")
        language = arguments.get("language", "en")

        try:
            result = {}

            if content_type in ["templates", "all"]:
                if language == "zh":
                    result["模板"] = ["需求模板", "设计模板", "任务模板"]
                else:
                    result["templates"] = [t.value for t in TemplateType]

            if content_type in ["methodology", "all"]:
                available_guides = self.methodology_guides.list_available_guides(
                    language
                )
                if language == "zh":
                    result["方法论主题"] = [
                        guide.replace("-zh", "") for guide in available_guides
                    ]
                else:
                    result["methodology_topics"] = available_guides

            if content_type == "all":
                if language == "zh":
                    result["示例类别"] = ["需求示例", "设计示例", "任务示例", "验证示例", "常见陷阱", "完整规范"]
                else:
                    result["examples_categories"] = [
                        "requirements",
                        "design",
                        "tasks",
                        "validation",
                        "pitfalls",
                        "complete_specs",
                    ]

            # Format as readable text
            content_lines = []
            for category, items in result.items():
                content_lines.append(f"## {category.replace('_', ' ').title()}")
                for item in items:
                    content_lines.append(f"- {item}")
                content_lines.append("")

            content = "\n".join(content_lines)
            return [TextContent(type="text", text=content)]

        except Exception as e:
            return [TextContent(type="text", text=f"Error listing content: {str(e)}")]

    async def handle_get_examples_and_case_studies(
        self, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle get_examples_and_case_studies tool call."""
        category = arguments.get("category", "requirements")
        specific_topic = arguments.get("specific_topic")

        try:
            content = self._get_examples_content(category, specific_topic)
            return [TextContent(type="text", text=content)]

        except Exception as e:
            return [
                TextContent(type="text", text=f"Error retrieving examples: {str(e)}")
            ]

    def _get_examples_content(
        self, category: str, specific_topic: Optional[str] = None
    ) -> str:
        """Get examples and case studies content."""
        examples = {
            "requirements": self._get_requirements_examples(),
            "design": self._get_design_examples(),
            "tasks": self._get_tasks_examples(),
            "validation": self._get_validation_examples(),
            "pitfalls": self._get_pitfalls_examples(),
            "complete_specs": self._get_complete_spec_examples(),
        }

        if category not in examples:
            available = ", ".join(examples.keys())
            return f"Error: Invalid category '{category}'. Available categories: {available}"

        content = examples[category]

        # Filter by specific topic if provided
        if specific_topic:
            # This is a simplified implementation - in a real system you might
            # have more sophisticated topic filtering
            if specific_topic.lower() not in content.lower():
                return f"No examples found for topic '{specific_topic}' in category '{category}'"

        return content

    def _get_requirements_examples(self) -> str:
        """Get requirements examples."""
        return """# Requirements Examples

## Good EARS Format Examples

### Event-Driven (WHEN...THEN)
- WHEN user clicks the login button THEN system SHALL validate credentials within 2 seconds
- WHEN invalid credentials are entered THEN system SHALL display error message "Invalid username or password"
- WHEN user session expires THEN system SHALL redirect to login page and clear session data

### Conditional (IF...THEN)
- IF user is not authenticated THEN system SHALL deny access to protected resources
- IF file size exceeds 10MB THEN system SHALL reject upload with error message
- IF user has admin role THEN system SHALL display administrative functions

### State-Based (WHILE...THEN)
- WHILE backup operation is running THEN system SHALL display progress indicator
- WHILE user is typing in search field THEN system SHALL show auto-suggestions
- WHILE data is loading THEN system SHALL show loading spinner

### Feature-Specific (WHERE...THEN)
- WHERE user profile page THEN system SHALL display user information and edit options
- WHERE mobile device THEN system SHALL use responsive layout with touch-friendly controls
- WHERE search results page THEN system SHALL highlight matching search terms

## Complete Requirement Example

### Requirement 1

**User Story:** As a project manager, I want to create feature specifications, so that I can ensure systematic development of new features.

#### Acceptance Criteria

1. WHEN project manager accesses spec creation tool THEN system SHALL display template selection options
2. IF no template type is selected THEN system SHALL default to requirements template
3. WHEN template is selected THEN system SHALL generate document with proper structure and placeholders
4. WHERE spec document is created THEN system SHALL save it in .kiro/specs/{feature_name}/ directory

## Common Mistakes to Avoid

### Bad Examples (Don't Do This)
- ❌ "System should be user-friendly" (vague, not testable)
- ❌ "Response time should be fast" (not measurable)
- ❌ "User can login" (missing conditions and system response)

### Good Examples (Do This)
- ✅ "WHEN user enters valid credentials THEN system SHALL authenticate within 2 seconds"
- ✅ "IF authentication fails THEN system SHALL display specific error message"
- ✅ "WHERE login page THEN system SHALL provide username and password fields"
"""

    def _get_design_examples(self) -> str:
        """Get design examples."""
        return """# Design Examples

## Architecture Diagram Example

```mermaid
graph TB
    UI[User Interface] --> API[API Layer]
    API --> BL[Business Logic]
    API --> Auth[Authentication]
    BL --> DB[(Database)]
    BL --> Cache[(Cache)]
    Auth --> DB
```

## Component Interface Example

### UserService Component

**Purpose**: Manages user authentication and profile operations

**Key Responsibilities**:
- User authentication and session management
- Profile data validation and updates
- Password security and encryption
- User role and permission management

**Interface**:
```python
class UserService:
    async def authenticate(self, username: str, password: str) -> AuthResult
    async def get_profile(self, user_id: str) -> UserProfile
    async def update_profile(self, user_id: str, data: ProfileData) -> bool
    async def change_password(self, user_id: str, old_pwd: str, new_pwd: str) -> bool
```

## Data Model Example

```python
@dataclass
class User:
    id: str
    username: str
    email: str
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None

    def validate(self) -> List[ValidationError]:
        errors = []
        if not self.username or len(self.username) < 3:
            errors.append(ValidationError("Username must be at least 3 characters"))
        if not self._is_valid_email(self.email):
            errors.append(ValidationError("Invalid email format"))
        return errors
```

## Error Handling Strategy Example

### Authentication Errors
- **Invalid Credentials**: Return generic "Invalid username or password" message
- **Account Locked**: Return "Account temporarily locked" with unlock time
- **Session Expired**: Redirect to login with session timeout message

### Recovery Mechanisms
- **Database Connection Lost**: Retry with exponential backoff, fallback to cache
- **Service Unavailable**: Return cached data with staleness indicator
- **Validation Failures**: Return specific field-level error messages

## Testing Strategy Example

### Unit Testing
- Test each component in isolation with mocked dependencies
- Use property-based testing for data validation functions
- Achieve 90%+ code coverage for business logic

### Integration Testing
- Test API endpoints with real database connections
- Verify authentication flows end-to-end
- Test error scenarios and recovery mechanisms

### Validation Testing
- Verify all requirements are addressed in implementation
- Test edge cases and boundary conditions
- Validate performance requirements under load
"""

    def _get_tasks_examples(self) -> str:
        """Get tasks examples."""
        return """# Tasks Examples

## Good Task Structure

### Setup Tasks
- [ ] 1. Set up project structure and core interfaces
  - Create directory structure for models, services, and API components
  - Define base interfaces and abstract classes
  - Set up dependency injection container
  - Configure logging and error handling framework
  - _Requirements: 1.1, 2.4_

### Implementation Tasks with Subtasks
- [ ] 2. Implement user authentication system
- [ ] 2.1 Create user data models and validation
  - Implement User, UserProfile, and AuthResult classes
  - Add data validation methods with comprehensive error messages
  - Write unit tests for model validation logic
  - _Requirements: 1.2, 3.1_

- [ ] 2.2 Build authentication service
  - Implement UserService with authentication methods
  - Add password hashing and verification using bcrypt
  - Create session management with JWT tokens
  - Write unit tests for authentication logic
  - _Requirements: 1.2, 1.3_

- [ ] 2.3 Create authentication API endpoints
  - Implement login, logout, and token refresh endpoints
  - Add request validation and error handling
  - Write integration tests for API endpoints
  - _Requirements: 1.4, 2.1_

### Testing Tasks
- [ ] 3. Create comprehensive test suite
- [ ] 3.1 Write unit tests for core components
  - Test user models with various input scenarios
  - Test authentication service with mocked dependencies
  - Achieve 90%+ code coverage for business logic
  - _Requirements: All requirements for quality assurance_

## Task Quality Checklist

### ✅ Good Tasks
- Specific coding activities (implement, create, write)
- Reference specific requirements (1.1, 2.3)
- Build incrementally on previous tasks
- Include testing as part of implementation
- Focus on concrete deliverables

### ❌ Bad Tasks
- "Research authentication options" (not coding)
- "Deploy to production" (not development)
- "Get user feedback" (not coding)
- "Improve performance" (too vague)
- "Support user authentication" (too high-level)

## Dependency Management Example

### Correct Task Sequence
1. Set up project structure (foundation)
2. Create data models (needed by services)
3. Implement services (uses models)
4. Create API endpoints (uses services)
5. Add integration tests (tests complete flow)

### Incorrect Task Sequence
❌ Starting with API endpoints before models exist
❌ Writing tests before implementation exists
❌ Creating complex features before basic structure
"""

    def _get_validation_examples(self) -> str:
        """Get validation examples."""
        return """# Validation Examples

## Requirements Validation

### EARS Format Validation
✅ **Good**: "WHEN user clicks submit THEN system SHALL validate form data"
❌ **Bad**: "System validates form data" (missing trigger and SHALL)

✅ **Good**: "IF user is not authenticated THEN system SHALL redirect to login page"
❌ **Bad**: "Unauthenticated users are redirected" (passive voice, missing SHALL)

### User Story Validation
✅ **Good**: "As a project manager, I want to create specifications, so that I can ensure systematic development"
❌ **Bad**: "As a user, I want to use the system" (too generic, no clear benefit)

## Design Validation

### Required Sections Checklist
- [ ] Overview with technology stack
- [ ] Architecture with diagrams
- [ ] Components and interfaces
- [ ] Data models with validation
- [ ] Error handling strategy
- [ ] Testing strategy

### Requirement Traceability Example
```
Requirement 1.1: User authentication
├── Design: UserService component (Section 3.2)
├── Design: Authentication API (Section 3.3)
└── Design: Session management (Section 4.1)
```

## Task Validation

### Requirement References
✅ **Good**: "_Requirements: 1.1, 2.3, 3.2_" (specific references)
❌ **Bad**: "_Requirements: User authentication_" (too general)

### Actionability Check
✅ **Good**: "Implement UserService.authenticate() method with password hashing"
❌ **Bad**: "Support user authentication" (not specific enough)

## Common Validation Errors

### Requirements Phase
- Missing EARS format keywords (WHEN, IF, THEN, SHALL)
- Vague acceptance criteria ("user-friendly", "fast")
- Generic user roles ("user" instead of "admin", "customer")
- Missing edge cases and error conditions

### Design Phase
- Missing required sections (architecture, components, testing)
- No requirement traceability
- Vague component descriptions
- Missing error handling strategy

### Tasks Phase
- Non-coding tasks (deployment, user testing)
- Missing requirement references
- Tasks that don't build incrementally
- Abstract tasks without specific deliverables

## Validation Result Examples

### Error Result
```
Type: error
Message: Requirement 1 acceptance criterion 2 does not follow EARS format
Location: Requirement 1, line 15
Suggestion: Use EARS format: WHEN/IF/WHILE/WHERE [condition] THEN [system] SHALL [response]
```

### Warning Result
```
Type: warning
Message: Requirement 2 uses generic "user" role
Location: Requirement 2, line 8
Suggestion: Use a specific role like "developer", "admin", "customer", etc.
```
"""

    def _get_pitfalls_examples(self) -> str:
        """Get common pitfalls and solutions."""
        return """# Common Pitfalls and Solutions

## Requirements Phase Pitfalls

### Pitfall: Vague Requirements
**Problem**: "System should be user-friendly and fast"
**Why it's bad**: Not testable, subjective, no clear success criteria
**Solution**: Use specific, measurable criteria
**Better**: "WHEN user submits form THEN system SHALL respond within 2 seconds"

### Pitfall: Missing Edge Cases
**Problem**: Only covering happy path scenarios
**Why it's bad**: Real-world usage includes errors and edge cases
**Solution**: Systematically consider error conditions
**Example**: Add requirements for invalid input, network failures, timeout scenarios

### Pitfall: Implementation Details in Requirements
**Problem**: "System shall use MySQL database with connection pooling"
**Why it's bad**: Requirements should specify what, not how
**Solution**: Focus on functional requirements
**Better**: "WHEN user data is stored THEN system SHALL persist data reliably"

## Design Phase Pitfalls

### Pitfall: Skipping Research
**Problem**: Making technology choices without investigation
**Why it's bad**: May choose inappropriate solutions
**Solution**: Research during design phase, document findings
**Example**: Compare authentication libraries, document pros/cons

### Pitfall: Over-Engineering
**Problem**: Designing for every possible future requirement
**Why it's bad**: Adds complexity without current value
**Solution**: Design for current requirements, plan for extensibility
**Example**: Simple user roles now, extensible permission system later

### Pitfall: Poor Requirement Traceability
**Problem**: Design elements that don't map to requirements
**Why it's bad**: Scope creep, unnecessary complexity
**Solution**: Ensure every design element addresses specific requirements
**Example**: Create traceability matrix linking design to requirements

## Tasks Phase Pitfalls

### Pitfall: Non-Coding Tasks
**Problem**: "Deploy to production", "Get user feedback", "Write documentation"
**Why it's bad**: These aren't implementation tasks for developers
**Solution**: Focus only on coding activities
**Better**: "Implement deployment configuration", "Write automated tests"

### Pitfall: Abstract Tasks
**Problem**: "Support user authentication", "Handle errors gracefully"
**Why it's bad**: Not specific enough for immediate action
**Solution**: Break down into concrete coding steps
**Better**: "Implement UserService.authenticate() method", "Add try-catch blocks with specific error messages"

### Pitfall: Poor Task Sequencing
**Problem**: Tasks that depend on components not yet built
**Why it's bad**: Cannot execute tasks in order
**Solution**: Sequence tasks to build incrementally
**Example**: Models → Services → APIs → Integration

## Workflow Pitfalls

### Pitfall: Skipping Phases
**Problem**: Jumping directly to implementation without design
**Why it's bad**: Leads to poor architecture and missed requirements
**Solution**: Follow systematic three-phase approach
**Recovery**: Stop implementation, go back to create proper design

### Pitfall: Proceeding Without Approval
**Problem**: Moving to next phase without explicit user approval
**Why it's bad**: May build wrong solution
**Solution**: Always get explicit approval before proceeding
**Example**: "Do the requirements look good? If so, we can move on to design."

### Pitfall: Ignoring User Feedback
**Problem**: Dismissing user concerns or change requests
**Why it's bad**: Final solution won't meet user needs
**Solution**: Address all feedback thoroughly before seeking approval
**Recovery**: Revise documents based on feedback, ask for approval again

## Recovery Strategies

### When Requirements Are Wrong
1. Acknowledge the issue
2. Gather correct requirements from user
3. Update requirements document completely
4. Get approval for updated requirements
5. Update design and tasks to match

### When Design Is Inadequate
1. Identify specific design problems
2. Conduct additional research if needed
3. Revise design to address issues
4. Ensure all requirements are covered
5. Get approval before proceeding to tasks

### When Tasks Are Unworkable
1. Analyze why tasks are problematic
2. Return to design if architectural changes needed
3. Break complex tasks into smaller ones
4. Improve requirement traceability
5. Resequence for better incremental flow

## Prevention Best Practices

### Requirements Phase
- Use structured EARS format consistently
- Ask "How would we test this?" for each requirement
- Consider error cases and edge conditions
- Get specific about user roles and scenarios

### Design Phase
- Research thoroughly during design
- Document all design decisions and rationales
- Create clear architecture diagrams
- Ensure comprehensive requirement coverage

### Tasks Phase
- Focus exclusively on coding activities
- Maintain clear requirement traceability
- Plan for incremental development
- Validate task sequence and dependencies

### Workflow Management
- Never skip phases or proceed without approval
- Address all user feedback completely
- Maintain systematic approach throughout
- Be prepared to iterate and refine
"""

    def _get_complete_spec_examples(self) -> str:
        """Get complete specification examples."""
        return """# Complete Specification Examples

## Example: User Authentication Feature

### Requirements Document

# Requirements Document

## Introduction

This feature enables secure user authentication for the application, allowing users to log in, maintain sessions, and access protected resources based on their roles.

## Requirements

### Requirement 1

**User Story:** As a user, I want to log into the application, so that I can access my personalized content and features.

#### Acceptance Criteria

1. WHEN user enters valid credentials THEN system SHALL authenticate user within 2 seconds
2. WHEN user enters invalid credentials THEN system SHALL display error message "Invalid username or password"
3. IF user account is locked THEN system SHALL display message "Account temporarily locked, try again in X minutes"
4. WHERE login page THEN system SHALL provide username and password input fields

### Requirement 2

**User Story:** As a user, I want my session to be maintained securely, so that I don't have to re-authenticate frequently.

#### Acceptance Criteria

1. WHEN user successfully authenticates THEN system SHALL create secure session token
2. WHILE user session is active THEN system SHALL allow access to protected resources
3. IF session expires THEN system SHALL redirect user to login page
4. WHEN user logs out THEN system SHALL invalidate session token

### Design Document

# Design Document

## Overview

The authentication system uses JWT tokens for stateless session management, with bcrypt for password hashing and role-based access control. The design follows a layered architecture with clear separation between API, business logic, and data layers.

**Technology Stack:**
- JWT for session tokens
- bcrypt for password hashing
- Redis for token blacklisting
- PostgreSQL for user data

## Architecture

```mermaid
graph TB
    Client[Client Application] --> API[Authentication API]
    API --> AuthService[Authentication Service]
    API --> Middleware[JWT Middleware]
    AuthService --> UserRepo[User Repository]
    AuthService --> TokenService[Token Service]
    UserRepo --> DB[(PostgreSQL)]
    TokenService --> Cache[(Redis)]
```

## Components and Interfaces

### AuthenticationService

**Purpose**: Handles user authentication and session management

**Key Responsibilities**:
- Credential validation and user authentication
- JWT token generation and validation
- Password hashing and verification
- Session lifecycle management

**Interface**:
```python
class AuthenticationService:
    async def authenticate(self, username: str, password: str) -> AuthResult
    async def validate_token(self, token: str) -> TokenValidation
    async def refresh_token(self, refresh_token: str) -> TokenPair
    async def logout(self, token: str) -> bool
```

## Data Models

```python
@dataclass
class User:
    id: str
    username: str
    email: str
    password_hash: str
    role: UserRole
    created_at: datetime
    last_login: Optional[datetime] = None

@dataclass
class AuthResult:
    success: bool
    user: Optional[User]
    access_token: Optional[str]
    refresh_token: Optional[str]
    error_message: Optional[str]
```

## Error Handling

- **Invalid Credentials**: Generic error message to prevent username enumeration
- **Account Lockout**: Temporary lockout after failed attempts with exponential backoff
- **Token Expiry**: Automatic refresh with fallback to re-authentication
- **Service Failures**: Graceful degradation with cached authentication data

## Testing Strategy

- **Unit Tests**: Test authentication logic with mocked dependencies
- **Integration Tests**: Test API endpoints with real database
- **Security Tests**: Test against common attack vectors (brute force, token manipulation)
- **Performance Tests**: Validate authentication response times under load

### Tasks Document

# Implementation Plan

- [ ] 1. Set up authentication project structure
  - Create directory structure for auth components (models, services, api)
  - Set up dependency injection for authentication services
  - Configure JWT and bcrypt libraries
  - _Requirements: 1.1, 2.1_

- [ ] 2. Implement user data models
- [ ] 2.1 Create User model with validation
  - Implement User dataclass with all required fields
  - Add password hashing methods using bcrypt
  - Create user validation logic for username and email
  - Write unit tests for User model validation
  - _Requirements: 1.1, 2.1_

- [ ] 2.2 Create authentication result models
  - Implement AuthResult and TokenValidation dataclasses
  - Add error handling and success state management
  - Write unit tests for result model behavior
  - _Requirements: 1.1, 1.2, 2.1_

- [ ] 3. Build authentication service layer
- [ ] 3.1 Implement core authentication logic
  - Create AuthenticationService with credential validation
  - Implement password verification using bcrypt
  - Add user lookup and authentication flow
  - Write unit tests for authentication logic
  - _Requirements: 1.1, 1.2_

- [ ] 3.2 Add JWT token management
  - Implement TokenService for JWT generation and validation
  - Add token refresh and expiration handling
  - Create token blacklisting for logout functionality
  - Write unit tests for token operations
  - _Requirements: 2.1, 2.2, 2.4_

- [ ] 4. Create authentication API endpoints
- [ ] 4.1 Build login and logout endpoints
  - Implement POST /auth/login with credential validation
  - Implement POST /auth/logout with token invalidation
  - Add proper HTTP status codes and error responses
  - Write integration tests for auth endpoints
  - _Requirements: 1.1, 1.2, 1.3, 2.4_

- [ ] 4.2 Add token refresh endpoint
  - Implement POST /auth/refresh for token renewal
  - Add refresh token validation and new token generation
  - Handle refresh token expiration scenarios
  - Write integration tests for token refresh flow
  - _Requirements: 2.1, 2.3_

- [ ] 5. Implement JWT middleware
- [ ] 5.1 Create authentication middleware
  - Build JWT validation middleware for protected routes
  - Add token extraction from Authorization header
  - Implement user context injection for authenticated requests
  - Write unit tests for middleware functionality
  - _Requirements: 2.2, 2.3_

- [ ] 6. Add comprehensive error handling
- [ ] 6.1 Implement authentication error handling
  - Create specific error types for authentication failures
  - Add rate limiting for failed login attempts
  - Implement account lockout with exponential backoff
  - Write tests for error scenarios and recovery
  - _Requirements: 1.3, 2.3_

This example demonstrates how a complete specification flows from high-level requirements through detailed design to specific implementation tasks, with clear traceability throughout.
"""

    async def handle_tool_call(
        self, name: str, arguments: Dict[str, Any]
    ) -> List[TextContent]:
        """Handle MCP tool calls for content access."""
        handlers = {
            "get_template": self.handle_get_template,
            "get_methodology_guide": self.handle_get_methodology_guide,
            "list_available_content": self.handle_list_available_content,
            "get_examples_and_case_studies": self.handle_get_examples_and_case_studies,
        }

        handler = handlers.get(name)
        if not handler:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

        return await handler(arguments)
