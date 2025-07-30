# MCP规范驱动开发API文档

本文档为规范驱动开发服务器中所有可用的MCP工具提供全面的API文档。

## 概述

MCP规范驱动开发工具通过三个主要类别的工具为AI助手提供全面的规范驱动开发方法论：

- **内容访问工具**：访问模板、方法论指南和示例
- **工作流管理工具**：管理三阶段规范工作流
- **验证工具**：根据质量标准验证规范文档

## 内容访问工具

### get_template

获取用于规范创建的文档模板。

**参数：**
- `template_type` (字符串，必需)：要获取的模板类型
  - `"requirements"`：EARS格式需求模板
  - `"design"`：设计文档结构模板
  - `"tasks"`：实施任务规划模板

**返回：**
- 格式化文本形式的模板内容
- 包含占位符和结构指导
- 包含示例和格式说明

**使用示例：**
```json
{
  "name": "get_template",
  "arguments": {
    "template_type": "requirements"
  }
}
```

**Example Response:**
```
# Requirements Document

## Introduction

[Brief description of the feature and its purpose]

## Requirements

### Requirement 1

**User Story:** As a [role], I want [feature], so that [benefit]

#### Acceptance Criteria

1. WHEN [event] THEN [system] SHALL [response]
2. IF [precondition] THEN [system] SHALL [response]
...
```

### get_methodology_guide

Retrieves methodology documentation and best practices.

**Parameters:**
- `guide_type` (string, required): Type of guide to retrieve
  - `"workflow"`: Overall three-phase workflow documentation
  - `"ears-format"`: EARS format requirements guide
  - `"phase-transitions"`: Phase transition rules and approval process
  - `"best-practices"`: General best practices for spec development

**Returns:**
- Comprehensive methodology documentation
- Step-by-step guidance
- Best practices and common pitfalls

**Example Usage:**
```json
{
  "name": "get_methodology_guide",
  "arguments": {
    "guide_type": "workflow"
  }
}
```

### list_available_content

Lists all available content types and their descriptions.

**Parameters:**
- None

**Returns:**
- Complete inventory of available templates, guides, and examples
- Brief descriptions of each content type
- Usage recommendations

**Example Usage:**
```json
{
  "name": "list_available_content",
  "arguments": {}
}
```

### get_examples_and_case_studies

Retrieves examples and case studies for learning and reference.

**Parameters:**
- `example_type` (string, required): Type of example to retrieve
  - `"complete-spec"`: Full spec example from requirements through tasks
  - `"requirements-examples"`: Sample requirements documents
  - `"design-examples"`: Sample design documents
  - `"task-examples"`: Sample task planning documents
  - `"common-pitfalls"`: Common mistakes and how to avoid them
  - `"troubleshooting"`: Troubleshooting scenarios and solutions

**Returns:**
- Relevant examples with explanations
- Case studies with lessons learned
- Troubleshooting guidance

**Example Usage:**
```json
{
  "name": "get_examples_and_case_studies",
  "arguments": {
    "example_type": "complete-spec"
  }
}
```

## Workflow Management Tools

### create_workflow

Initializes a new spec workflow for a feature.

**Parameters:**
- `feature_name` (string, required): Name of the feature (kebab-case format)
- `initial_description` (string, optional): Brief description of the feature

**Returns:**
- Workflow initialization confirmation
- Current phase status
- Next steps guidance

**Example Usage:**
```json
{
  "name": "create_workflow",
  "arguments": {
    "feature_name": "user-authentication",
    "initial_description": "Add user login and registration functionality"
  }
}
```

### get_workflow_status

Retrieves current workflow status and phase information.

**Parameters:**
- `feature_name` (string, required): Name of the feature

**Returns:**
- Current phase (requirements, design, or tasks)
- Phase completion status
- Approval status for each phase
- Available next actions

**Example Usage:**
```json
{
  "name": "get_workflow_status",
  "arguments": {
    "feature_name": "user-authentication"
  }
}
```

### transition_phase

Transitions workflow to the next phase after approval.

**Parameters:**
- `feature_name` (string, required): Name of the feature
- `from_phase` (string, required): Current phase
  - `"requirements"`, `"design"`, or `"tasks"`
- `to_phase` (string, required): Target phase
- `approval_confirmed` (boolean, required): Explicit approval confirmation

**Returns:**
- Transition confirmation
- New phase status
- Next steps guidance

**Example Usage:**
```json
{
  "name": "transition_phase",
  "arguments": {
    "feature_name": "user-authentication",
    "from_phase": "requirements",
    "to_phase": "design",
    "approval_confirmed": true
  }
}
```

### navigate_backward

Allows returning to previous phases for modifications.

**Parameters:**
- `feature_name` (string, required): Name of the feature
- `target_phase` (string, required): Phase to return to
- `reason` (string, optional): Reason for backward navigation

**Returns:**
- Navigation confirmation
- Updated workflow status
- Impact assessment

**Example Usage:**
```json
{
  "name": "navigate_backward",
  "arguments": {
    "feature_name": "user-authentication",
    "target_phase": "requirements",
    "reason": "Need to add additional security requirements"
  }
}
```

### check_transition_requirements

Checks if workflow can transition to next phase.

**Parameters:**
- `feature_name` (string, required): Name of the feature
- `target_phase` (string, required): Desired target phase

**Returns:**
- Transition readiness status
- Missing requirements
- Validation results
- Approval status

**Example Usage:**
```json
{
  "name": "check_transition_requirements",
  "arguments": {
    "feature_name": "user-authentication",
    "target_phase": "design"
  }
}
```

### get_approval_guidance

Provides guidance on approval process for current phase.

**Parameters:**
- `feature_name` (string, required): Name of the feature
- `phase` (string, required): Phase requiring approval

**Returns:**
- Approval criteria checklist
- Review guidelines
- Common approval blockers
- Next steps after approval

**Example Usage:**
```json
{
  "name": "get_approval_guidance",
  "arguments": {
    "feature_name": "user-authentication",
    "phase": "requirements"
  }
}
```

## Validation Tools

### validate_document

Validates spec documents against quality standards.

**Parameters:**
- `document_type` (string, required): Type of document to validate
  - `"requirements"`, `"design"`, or `"tasks"`
- `content` (string, required): Document content to validate
- `feature_name` (string, optional): Feature name for context

**Returns:**
- Validation results with pass/fail status
- Detailed error messages and locations
- Suggestions for improvement
- Quality score

**Example Usage:**
```json
{
  "name": "validate_document",
  "arguments": {
    "document_type": "requirements",
    "content": "# Requirements Document\n\n## Requirements\n\n### Requirement 1\n...",
    "feature_name": "user-authentication"
  }
}
```

### get_validation_checklist

Retrieves validation checklist for document types.

**Parameters:**
- `document_type` (string, required): Type of document
  - `"requirements"`, `"design"`, or `"tasks"`

**Returns:**
- Comprehensive validation checklist
- Quality criteria explanations
- Common validation failures
- Best practices

**Example Usage:**
```json
{
  "name": "get_validation_checklist",
  "arguments": {
    "document_type": "requirements"
  }
}
```

### explain_validation_error

Provides detailed explanation of validation errors.

**Parameters:**
- `error_type` (string, required): Type of validation error
- `context` (string, optional): Additional context about the error

**Returns:**
- Detailed error explanation
- Root cause analysis
- Step-by-step resolution guidance
- Prevention tips

**Example Usage:**
```json
{
  "name": "explain_validation_error",
  "arguments": {
    "error_type": "missing_ears_format",
    "context": "Requirements document validation failed"
  }
}
```

### validate_requirement_traceability

Validates traceability between requirements, design, and tasks.

**Parameters:**
- `feature_name` (string, required): Name of the feature
- `requirements_content` (string, required): Requirements document content
- `design_content` (string, optional): Design document content
- `tasks_content` (string, optional): Tasks document content

**Returns:**
- Traceability matrix
- Missing requirement coverage
- Orphaned design elements
- Unlinked tasks

**Example Usage:**
```json
{
  "name": "validate_requirement_traceability",
  "arguments": {
    "feature_name": "user-authentication",
    "requirements_content": "...",
    "design_content": "...",
    "tasks_content": "..."
  }
}
```

## Error Handling

All tools follow consistent error handling patterns:

### Error Response Format

```json
{
  "type": "text",
  "text": "Error: [Error message with specific details]"
}
```

### Common Error Types

- **ValidationError**: Document validation failures
- **WorkflowError**: Invalid workflow state transitions
- **ContentNotFoundError**: Requested content not available
- **ConfigurationError**: Server configuration issues

### Error Recovery

- All errors include specific guidance for resolution
- Validation errors provide line-by-line feedback
- Workflow errors suggest valid next actions
- Content errors offer alternative options

## Usage Patterns

### Complete Spec Development Workflow

1. **Initialize Workflow**
   ```json
   {"name": "create_workflow", "arguments": {"feature_name": "my-feature"}}
   ```

2. **Get Requirements Template**
   ```json
   {"name": "get_template", "arguments": {"template_type": "requirements"}}
   ```

3. **Validate Requirements**
   ```json
   {"name": "validate_document", "arguments": {"document_type": "requirements", "content": "..."}}
   ```

4. **Transition to Design**
   ```json
   {"name": "transition_phase", "arguments": {"feature_name": "my-feature", "from_phase": "requirements", "to_phase": "design", "approval_confirmed": true}}
   ```

5. **Continue through Design and Tasks phases**

### Validation-First Approach

1. **Get Validation Checklist**
   ```json
   {"name": "get_validation_checklist", "arguments": {"document_type": "requirements"}}
   ```

2. **Create Document Following Checklist**

3. **Validate Document**
   ```json
   {"name": "validate_document", "arguments": {"document_type": "requirements", "content": "..."}}
   ```

4. **Fix Issues and Re-validate**

### Learning and Reference

1. **List Available Content**
   ```json
   {"name": "list_available_content", "arguments": {}}
   ```

2. **Get Examples**
   ```json
   {"name": "get_examples_and_case_studies", "arguments": {"example_type": "complete-spec"}}
   ```

3. **Get Methodology Guidance**
   ```json
   {"name": "get_methodology_guide", "arguments": {"guide_type": "workflow"}}
   ```

## Performance Considerations

- Content retrieval is cached for improved performance
- Validation operations are optimized for large documents
- Workflow state is persisted across sessions
- Health monitoring tracks performance metrics

## Security and Privacy

- No sensitive data is stored or transmitted
- All content is methodology-focused and generic
- Validation operates on document structure, not content
- No external network calls are made

## Versioning

- API version: 1.0.0
- MCP protocol version: 1.12.2+
- Backward compatibility maintained for major versions
- Deprecation notices provided for breaking changes
