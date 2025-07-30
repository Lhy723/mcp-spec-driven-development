# 用户指南：AI助手的MCP规范驱动开发

本指南帮助AI编程助手有效使用MCP规范驱动开发工具，指导用户进行系统化的功能开发。

## 概述

MCP规范驱动开发工具使AI助手能够帮助用户通过结构化的三阶段工作流程创建高质量的功能规范：

1. **需求阶段** - 将想法转化为EARS格式的需求
2. **设计阶段** - 创建全面的技术设计
3. **任务阶段** - 生成可执行的实施计划

## 开始使用

### 初始设置

当用户想要创建新的功能规范时：

1. **创建新工作流**：
   ```json
   {
     "name": "create_workflow",
     "arguments": {
       "feature_name": "user-authentication",
       "initial_description": "添加用户登录和注册功能"
     }
   }
   ```

2. **了解方法论**：
   ```json
   {
     "name": "get_methodology_guide",
     "arguments": {
       "topic": "workflow",
       "language": "zh"
     }
   }
   ```

3. **获取适当的模板**：
   ```json
   {
     "name": "get_template",
     "arguments": {
       "template_type": "requirements",
       "language": "zh"
     }
   }
   ```

### 基本工作流模式

```
用户想法 → 需求 → 设计 → 任务 → 实施
```

每个阶段都需要用户明确批准后才能进入下一阶段。

## 阶段1：需求开发

### 目标
将用户想法转化为结构化、可测试的EARS格式需求。

### 关键步骤

1. **获取需求模板**
   ```json
   {
     "name": "get_template",
     "arguments": {
       "template_type": "requirements",
       "language": "zh"
     }
   }
   ```

2. **了解EARS格式**
   ```json
   {
     "name": "get_methodology_guide",
     "arguments": {
       "topic": "ears_format",
       "language": "zh"
     }
   }
   ```

3. **创建需求文档**
   - 使用模板结构
   - 以"作为[角色]，我想要[功能]，以便[收益]"格式编写用户故事
   - 使用EARS格式创建验收标准：
     - 当[事件]时，[系统]应当[响应]
     - 如果[前置条件]，那么[系统]应当[响应]

4. **验证需求**
   ```json
   {
     "name": "validate_document",
     "arguments": {
       "document_type": "requirements",
       "content": "[需求文档内容]"
     }
   }
   ```

5. **获得用户批准**
   - 向用户展示需求文档
   - 明确询问："需求看起来怎么样？如果没问题，我们可以进入设计阶段。"
   - 只有在明确批准后才能继续

### 需求最佳实践

- **具体明确**：每个需求都应该是可测试和可测量的
- **使用EARS格式**：确保一致性和清晰度
- **包含边界情况**：考虑错误条件和边界情况
- **编号需求**：使用层次编号（1.1、1.2等）
- **链接用户故事**：每个需求都应该追溯到用户故事

## 阶段2：设计开发

### 目标
基于批准的需求创建全面的技术设计。

### 关键步骤

1. **获取设计模板**
   ```json
   {
     "name": "get_template",
     "arguments": {
       "template_type": "design",
       "language": "zh"
     }
   }
   ```

2. **研究和上下文构建**
   - 为功能进行必要的研究
   - 构建技术上下文
   - 考虑架构影响

3. **创建设计文档**
   必需部分：
   - **概述**：高级功能描述
   - **架构**：系统架构和组件
   - **组件和接口**：详细的组件设计
   - **数据模型**：数据结构和关系
   - **错误处理**：错误场景和恢复
   - **测试策略**：功能测试方法

4. **验证设计**
   ```json
   {
     "name": "validate_document",
     "arguments": {
       "document_type": "design",
       "content": "[设计文档内容]"
     }
   }
   ```

5. **检查需求可追溯性**
   ```json
   {
     "name": "validate_requirement_traceability",
     "arguments": {
       "feature_name": "feature-name",
       "requirements_content": "[需求内容]",
       "design_content": "[设计内容]"
     }
   }
   ```

6. **获得用户批准**
   - 向用户展示设计文档
   - 明确询问："设计看起来怎么样？如果没问题，我们可以进入实施计划。"
   - 只有在明确批准后才能继续

## 阶段3：任务开发

### 目标
创建具有离散编码任务的可执行实施计划。

### 关键步骤

1. **获取任务模板**
   ```json
   {
     "name": "get_template",
     "arguments": {
       "template_type": "tasks",
       "language": "zh"
     }
   }
   ```

2. **创建实施计划**
   - 将设计分解为离散的编码任务
   - 使用复选框格式和层次编号
   - 每个任务都应该是编码代理可执行的
   - 包含每个任务的需求引用
   - 确保增量进展和早期测试

3. **验证任务**
   ```json
   {
     "name": "validate_document",
     "arguments": {
       "document_type": "tasks",
       "content": "[任务文档内容]"
     }
   }
   ```

4. **验证完整的可追溯性**
   ```json
   {
     "name": "validate_requirement_traceability",
     "arguments": {
       "feature_name": "feature-name",
       "requirements_content": "[需求内容]",
       "design_content": "[设计内容]",
       "tasks_content": "[任务内容]"
     }
   }
   ```

5. **获得用户批准**
   - 向用户展示任务文档
   - 明确询问："任务看起来怎么样？"
   - 只有在明确批准后才能继续

## 工作流管理

### 检查工作流状态

```json
{
  "name": "get_workflow_status",
  "arguments": {
    "feature_name": "feature-name"
  }
}
```

### 阶段转换

只有在明确用户批准后才能转换：

```json
{
  "name": "transition_phase",
  "arguments": {
    "feature_name": "feature-name",
    "from_phase": "requirements",
    "to_phase": "design",
    "approval_confirmed": true
  }
}
```

### 向后导航

如果用户需要修改早期阶段：

```json
{
  "name": "navigate_backward",
  "arguments": {
    "feature_name": "feature-name",
    "target_phase": "requirements",
    "reason": "需要添加额外的需求"
  }
}
```

## 验证和质量保证

### 文档验证

在向用户展示之前始终验证文档：

```json
{
  "name": "validate_document",
  "arguments": {
    "document_type": "requirements|design|tasks",
    "content": "[文档内容]"
  }
}
```

### 理解验证错误

当验证失败时：

```json
{
  "name": "explain_validation_error",
  "arguments": {
    "error_type": "[验证错误类型]",
    "context": "[额外上下文]"
  }
}
```

### 验证检查清单

在创建文档之前获取质量标准：

```json
{
  "name": "get_validation_checklist",
  "arguments": {
    "document_type": "requirements"
  }
}
```

## 学习和参考

### 可用内容

列出所有可用资源：

```json
{
  "name": "list_available_content",
  "arguments": {
    "language": "zh"
  }
}
```

### 示例和案例研究

获取学习示例：

```json
{
  "name": "get_examples_and_case_studies",
  "arguments": {
    "category": "complete-spec"
  }
}
```

### 方法论指导

访问详细方法论：

```json
{
  "name": "get_methodology_guide",
  "arguments": {
    "topic": "workflow",
    "language": "zh"
  }
}
```

## 常见场景

### 场景1：从头开始的新功能

1. 用户提供粗略想法
2. 创建工作流
3. 获取需求模板
4. 帮助用户创建需求
5. 验证并获得批准
6. 转换到设计阶段
7. 创建设计文档
8. 验证并获得批准
9. 转换到任务阶段
10. 创建实施计划
11. 验证并获得批准

### 场景2：改进现有规范

1. 检查当前工作流状态
2. 导航到适当阶段
3. 获取验证检查清单
4. 验证现有文档
5. 帮助用户修复问题
6. 重新验证并获得批准

### 场景3：学习方法论

1. 列出可用内容
2. 获取方法论指南
3. 展示示例和案例研究
4. 解释最佳实践
5. 指导练习

## 错误处理

### 常见错误和解决方案

- **验证失败**：使用explain_validation_error工具
- **工作流问题**：检查工作流状态和需求
- **找不到内容**：使用list_available_content查看选项
- **阶段转换被阻止**：使用check_transition_requirements

### 恢复策略

- 始终为错误解决提供具体指导
- 当主要方法失败时提供替代方法
- 使用示例澄清复杂概念
- 将复杂任务分解为较小步骤

## AI助手最佳实践

### 沟通

- **清晰明确**：解释每个阶段及其目的
- **请求批准**：永远不要在没有明确用户批准的情况下继续
- **提供上下文**：解释为什么每个步骤都很重要
- **展示示例**：使用示例澄清概念

### 工作流管理

- **遵循流程**：不要跳过阶段或步骤
- **早期验证**：在向用户展示之前检查质量
- **跟踪进度**：使用工作流状态工具
- **优雅处理错误**：为修复提供清晰指导

### 质量保证

- **验证一切**：一致使用验证工具
- **检查可追溯性**：确保需求贯穿所有阶段
- **参考标准**：使用EARS格式和模板
- **鼓励最佳实践**：引导用户获得质量结果

## 故障排除

### 用户对流程的抵制

- 解释系统化方法的好处
- 展示成功结果的示例
- 从简单功能开始建立信心
- 强调质量和可维护性的好处

### 复杂功能

- 分解为较小的子功能
- 使用层次需求结构
- 考虑分阶段实施方法
- 首先专注于核心功能

### 验证失败

- 使用explain_validation_error获取具体指导
- 展示正确格式的示例
- 指导逐步修复
- 每次修复后重新验证

## 高级用法

### 自定义内容

- 为特定领域调整模板
- 创建特定领域的示例
- 自定义验证标准
- 构建组织特定的最佳实践

### 与开发工具集成

- 将规范导出到开发环境
- 链接到问题跟踪系统
- 从需求生成测试用例
- 从规范创建文档

### 持续改进

- 收集规范质量反馈
- 跟踪常见验证问题
- 基于使用情况完善模板
- 基于经验教训更新方法论

## 支持和资源

- **API文档**：完整的工具参考
- **故障排除指南**：常见问题和解决方案
- **示例库**：示例规范和案例研究
- **最佳实践**：经过验证的方法和模式

记住：目标是帮助用户创建高质量、可维护的功能规范，从而实现成功的实施。始终优先考虑质量而非速度，并确保用户在每个步骤都理解。

## Phase 1: Requirements Development

### Objective
Transform user ideas into structured, testable requirements using EARS format.

### Key Steps

1. **Get Requirements Template**
   ```json
   {
     "name": "get_template",
     "arguments": {"template_type": "requirements"}
   }
   ```

2. **Understand EARS Format**
   ```json
   {
     "name": "get_methodology_guide",
     "arguments": {"guide_type": "ears-format"}
   }
   ```

3. **Create Requirements Document**
   - Use the template structure
   - Write user stories in format: "As a [role], I want [feature], so that [benefit]"
   - Create acceptance criteria using EARS format:
     - WHEN [event] THEN [system] SHALL [response]
     - IF [precondition] THEN [system] SHALL [response]

4. **Validate Requirements**
   ```json
   {
     "name": "validate_document",
     "arguments": {
       "document_type": "requirements",
       "content": "[requirements document content]"
     }
   }
   ```

5. **Get User Approval**
   - Present the requirements to the user
   - Ask explicitly: "Do the requirements look good? If so, we can move on to the design."
   - Only proceed after explicit approval

### Requirements Best Practices

- **Be Specific**: Each requirement should be testable and measurable
- **Use EARS Format**: Ensures consistency and clarity
- **Include Edge Cases**: Consider error conditions and boundary cases
- **Number Requirements**: Use hierarchical numbering (1.1, 1.2, etc.)
- **Link User Stories**: Each requirement should trace to a user story

### Common Requirements Issues

- Missing acceptance criteria
- Vague or untestable requirements
- Incorrect EARS format usage
- Missing user story context

## Phase 2: Design Development

### Objective
Create comprehensive technical design based on approved requirements.

### Key Steps

1. **Get Design Template**
   ```json
   {
     "name": "get_template",
     "arguments": {"template_type": "design"}
   }
   ```

2. **Research and Context Building**
   - Conduct necessary research for the feature
   - Build up technical context
   - Consider architecture implications

3. **Create Design Document**
   Required sections:
   - **Overview**: High-level feature description
   - **Architecture**: System architecture and components
   - **Components and Interfaces**: Detailed component design
   - **Data Models**: Data structures and relationships
   - **Error Handling**: Error scenarios and recovery
   - **Testing Strategy**: Approach to testing the feature

4. **Validate Design**
   ```json
   {
     "name": "validate_document",
     "arguments": {
       "document_type": "design",
       "content": "[design document content]"
     }
   }
   ```

5. **Check Requirements Traceability**
   ```json
   {
     "name": "validate_requirement_traceability",
     "arguments": {
       "feature_name": "feature-name",
       "requirements_content": "[requirements content]",
       "design_content": "[design content]"
     }
   }
   ```

6. **Get User Approval**
   - Present the design to the user
   - Ask explicitly: "Does the design look good? If so, we can move on to the implementation plan."
   - Only proceed after explicit approval

### Design Best Practices

- **Address All Requirements**: Every requirement should be covered
- **Include Diagrams**: Use Mermaid for architecture diagrams
- **Consider Non-Functional Requirements**: Performance, security, scalability
- **Document Decisions**: Explain design choices and trade-offs
- **Plan for Testing**: Include testing strategy from the start

### Common Design Issues

- Missing required sections
- Poor requirements traceability
- Insufficient technical detail
- Missing error handling considerations

## Phase 3: Tasks Development

### Objective
Create actionable implementation plan with discrete coding tasks.

### Key Steps

1. **Get Tasks Template**
   ```json
   {
     "name": "get_template",
     "arguments": {"template_type": "tasks"}
   }
   ```

2. **Create Implementation Plan**
   - Break design into discrete coding tasks
   - Use checkbox format with hierarchical numbering
   - Each task should be actionable by a coding agent
   - Include requirement references for each task
   - Ensure incremental progress and early testing

3. **Validate Tasks**
   ```json
   {
     "name": "validate_document",
     "arguments": {
       "document_type": "tasks",
       "content": "[tasks document content]"
     }
   }
   ```

4. **Validate Complete Traceability**
   ```json
   {
     "name": "validate_requirement_traceability",
     "arguments": {
       "feature_name": "feature-name",
       "requirements_content": "[requirements content]",
       "design_content": "[design content]",
       "tasks_content": "[tasks content]"
     }
   }
   ```

5. **Get User Approval**
   - Present the tasks to the user
   - Ask explicitly: "Do the tasks look good?"
   - Only proceed after explicit approval

### Tasks Best Practices

- **One Task at a Time**: Each task should be independently executable
- **Reference Requirements**: Link tasks back to specific requirements
- **Incremental Progress**: Build functionality step by step
- **Test-Driven**: Include testing tasks throughout
- **No Orphaned Code**: Every piece of code should integrate

### Common Tasks Issues

- Tasks too large or complex
- Missing requirement references
- Poor dependency management
- Non-actionable task descriptions

## Workflow Management

### Checking Workflow Status

```json
{
  "name": "get_workflow_status",
  "arguments": {"feature_name": "feature-name"}
}
```

### Phase Transitions

Only transition after explicit user approval:

```json
{
  "name": "transition_phase",
  "arguments": {
    "feature_name": "feature-name",
    "from_phase": "requirements",
    "to_phase": "design",
    "approval_confirmed": true
  }
}
```

### Backward Navigation

If users need to modify earlier phases:

```json
{
  "name": "navigate_backward",
  "arguments": {
    "feature_name": "feature-name",
    "target_phase": "requirements",
    "reason": "Need to add additional requirements"
  }
}
```

## Validation and Quality Assurance

### Document Validation

Always validate documents before presenting to users:

```json
{
  "name": "validate_document",
  "arguments": {
    "document_type": "requirements|design|tasks",
    "content": "[document content]"
  }
}
```

### Understanding Validation Errors

When validation fails:

```json
{
  "name": "explain_validation_error",
  "arguments": {
    "error_type": "[error type from validation]",
    "context": "[additional context]"
  }
}
```

### Validation Checklists

Get quality criteria before creating documents:

```json
{
  "name": "get_validation_checklist",
  "arguments": {"document_type": "requirements"}
}
```

## Learning and Reference

### Available Content

List all available resources:

```json
{
  "name": "list_available_content",
  "arguments": {}
}
```

### Examples and Case Studies

Get examples for learning:

```json
{
  "name": "get_examples_and_case_studies",
  "arguments": {"example_type": "complete-spec"}
}
```

### Methodology Guidance

Access detailed methodology:

```json
{
  "name": "get_methodology_guide",
  "arguments": {"guide_type": "workflow"}
}
```

## Common Scenarios

### Scenario 1: New Feature from Scratch

1. User provides rough idea
2. Create workflow
3. Get requirements template
4. Help user create requirements
5. Validate and get approval
6. Transition to design phase
7. Create design document
8. Validate and get approval
9. Transition to tasks phase
10. Create implementation plan
11. Validate and get approval

### Scenario 2: Improving Existing Spec

1. Check current workflow status
2. Navigate to appropriate phase
3. Get validation checklist
4. Validate existing document
5. Help user fix issues
6. Re-validate and get approval

### Scenario 3: Learning the Methodology

1. List available content
2. Get methodology guides
3. Show examples and case studies
4. Explain best practices
5. Guide through practice exercise

## Error Handling

### Common Errors and Solutions

- **Validation Failures**: Use explain_validation_error tool
- **Workflow Issues**: Check workflow status and requirements
- **Content Not Found**: Use list_available_content to see options
- **Phase Transition Blocked**: Use check_transition_requirements

### Recovery Strategies

- Always provide specific guidance for error resolution
- Offer alternative approaches when primary methods fail
- Use examples to clarify complex concepts
- Break down complex tasks into smaller steps

## Best Practices for AI Assistants

### Communication

- **Be Clear**: Explain each phase and its purpose
- **Ask for Approval**: Never proceed without explicit user approval
- **Provide Context**: Explain why each step is important
- **Show Examples**: Use examples to clarify concepts

### Workflow Management

- **Follow the Process**: Don't skip phases or steps
- **Validate Early**: Check quality before presenting to users
- **Track Progress**: Use workflow status tools
- **Handle Errors Gracefully**: Provide clear guidance for fixes

### Quality Assurance

- **Validate Everything**: Use validation tools consistently
- **Check Traceability**: Ensure requirements flow through all phases
- **Reference Standards**: Use EARS format and templates
- **Encourage Best Practices**: Guide users toward quality outcomes

## Troubleshooting

### User Resistance to Process

- Explain benefits of systematic approach
- Show examples of successful outcomes
- Start with simpler features to build confidence
- Emphasize quality and maintainability benefits

### Complex Features

- Break into smaller sub-features
- Use hierarchical requirements structure
- Consider phased implementation approach
- Focus on core functionality first

### Validation Failures

- Use explain_validation_error for specific guidance
- Show examples of correct format
- Guide through step-by-step fixes
- Re-validate after each fix

## Advanced Usage

### Custom Content

- Adapt templates for specific domains
- Create domain-specific examples
- Customize validation criteria
- Build organization-specific best practices

### Integration with Development Tools

- Export specs to development environments
- Link to issue tracking systems
- Generate test cases from requirements
- Create documentation from specs

### Continuous Improvement

- Collect feedback on spec quality
- Track common validation issues
- Refine templates based on usage
- Update methodology based on lessons learned

## Support and Resources

- **API Documentation**: Complete tool reference
- **Troubleshooting Guide**: Common issues and solutions
- **Examples Repository**: Sample specs and case studies
- **Best Practices**: Proven approaches and patterns

Remember: The goal is to help users create high-quality, maintainable feature specifications that lead to successful implementations. Always prioritize quality over speed and ensure user understanding at each step.
