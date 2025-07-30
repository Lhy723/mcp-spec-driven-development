# EARS Format Guide

## Introduction

EARS (Easy Approach to Requirements Syntax) is a structured format for writing clear, testable acceptance criteria. It provides consistent patterns that eliminate ambiguity and ensure requirements can be validated.

## Core EARS Patterns

### 1. Event-Driven Requirements (WHEN...THEN)

**Pattern**: `WHEN [trigger event] THEN [system] SHALL [response]`

**Use Case**: Requirements triggered by specific events or user actions.

**Examples**:
- WHEN user clicks the login button THEN system SHALL validate credentials
- WHEN file upload completes THEN system SHALL display success message
- WHEN session expires THEN system SHALL redirect user to login page
- WHEN invalid data is submitted THEN system SHALL display validation errors

### 2. Conditional Requirements (IF...THEN)

**Pattern**: `IF [precondition] THEN [system] SHALL [response]`

**Use Case**: Requirements that depend on specific conditions or states.

**Examples**:
- IF user is not authenticated THEN system SHALL deny access to protected resources
- IF file size exceeds 10MB THEN system SHALL reject the upload
- IF user has admin privileges THEN system SHALL display admin panel
- IF database connection fails THEN system SHALL show error message

### 3. State-Based Requirements (WHILE...THEN)

**Pattern**: `WHILE [system state] THEN [system] SHALL [response]`

**Use Case**: Requirements that apply during specific system states.

**Examples**:
- WHILE backup is running THEN system SHALL display progress indicator
- WHILE user is typing THEN system SHALL show auto-suggestions
- WHILE data is loading THEN system SHALL show loading spinner
- WHILE maintenance mode is active THEN system SHALL display maintenance message

### 4. Feature-Specific Requirements (WHERE...THEN)

**Pattern**: `WHERE [feature/location] THEN [system] SHALL [response]`

**Use Case**: Requirements that apply to specific features or locations.

**Examples**:
- WHERE user profile page THEN system SHALL display user information
- WHERE search results page THEN system SHALL highlight search terms
- WHERE mobile device THEN system SHALL use responsive layout
- WHERE admin dashboard THEN system SHALL show system statistics

## Writing Guidelines

### Use Active Voice
- ✅ "system SHALL validate input"
- ❌ "input SHALL be validated"

### Be Specific and Measurable
- ✅ "system SHALL respond within 2 seconds"
- ❌ "system SHALL respond quickly"
- ✅ "system SHALL support up to 1000 concurrent users"
- ❌ "system SHALL handle many users"

### Include Quantifiable Criteria
- Response times: "within X seconds"
- Capacity limits: "up to X users/items/requests"
- Data limits: "files up to X MB"
- Accuracy requirements: "with 99% accuracy"

### Cover All Scenarios
- **Normal Flow**: Happy path scenarios
- **Edge Cases**: Boundary conditions and limits
- **Error Conditions**: What happens when things go wrong
- **Alternative Flows**: Different ways to achieve the same goal

## Advanced EARS Patterns

### Combined Conditions
- `WHEN [event] AND [condition] THEN [system] SHALL [response]`
- `IF [condition1] AND [condition2] THEN [system] SHALL [response]`

**Examples**:
- WHEN user submits form AND all fields are valid THEN system SHALL save data
- IF user is authenticated AND has write permissions THEN system SHALL allow editing

### Negative Conditions
- `WHEN [event] AND NOT [condition] THEN [system] SHALL [response]`
- `IF NOT [condition] THEN [system] SHALL [response]`

**Examples**:
- WHEN user attempts login AND NOT authenticated THEN system SHALL request credentials
- IF user does NOT have admin role THEN system SHALL hide admin features

## Validation Rules

### Each EARS Statement Must Have:
1. **Clear Trigger**: Specific event, condition, or context
2. **Defined Actor**: Who or what performs the action (usually "system")
3. **Specific Response**: Measurable, testable outcome
4. **Appropriate Modal**: Use "SHALL" for mandatory requirements

### Quality Checklist:
- [ ] Trigger/condition is specific and unambiguous
- [ ] Response is measurable and testable
- [ ] Statement uses active voice
- [ ] Quantifiable criteria are included where relevant
- [ ] Edge cases and error conditions are covered

## Common Mistakes to Avoid

### Vague Language
- ❌ "system SHALL be user-friendly"
- ✅ "WHEN user navigates to any page THEN system SHALL load within 3 seconds"

### Implementation Details
- ❌ "system SHALL use MySQL database to store user data"
- ✅ "WHEN user data is submitted THEN system SHALL persist data permanently"

### Untestable Criteria
- ❌ "system SHALL look professional"
- ✅ "WHERE user interface THEN system SHALL follow established design guidelines"

### Missing Context
- ❌ "system SHALL validate input"
- ✅ "WHEN user submits registration form THEN system SHALL validate all required fields"

## Testing EARS Requirements

Each EARS statement should be directly testable:

1. **Identify the Trigger**: Set up the condition or event
2. **Execute the Action**: Perform the specified trigger
3. **Verify the Response**: Confirm the system responds as specified
4. **Measure the Outcome**: Validate quantifiable criteria

## Examples by Domain

### User Authentication
- WHEN user enters valid credentials THEN system SHALL grant access within 2 seconds
- IF user enters invalid password 3 times THEN system SHALL lock account for 15 minutes
- WHILE user session is active THEN system SHALL maintain authentication state
- WHERE login page THEN system SHALL provide password reset option

### Data Management
- WHEN user saves document THEN system SHALL persist changes within 1 second
- IF document exceeds 50MB THEN system SHALL reject upload with error message
- WHILE data sync is in progress THEN system SHALL show sync status indicator
- WHERE data entry form THEN system SHALL validate required fields on submit

### User Interface
- WHEN page loads THEN system SHALL display content within 3 seconds
- IF screen width is less than 768px THEN system SHALL use mobile layout
- WHILE form is being submitted THEN system SHALL disable submit button
- WHERE navigation menu THEN system SHALL highlight current page

This structured approach ensures requirements are clear, testable, and implementable while maintaining consistency across the entire specification.
