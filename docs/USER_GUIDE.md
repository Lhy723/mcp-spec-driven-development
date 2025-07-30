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

## 多语言支持

工具支持中英文内容，在工具调用中使用 `language` 参数：

```json
{
  "name": "get_template",
  "arguments": {
    "template_type": "requirements",
    "language": "zh"
  }
}
```

可用语言：
- `"zh"` - 中文（默认）
- `"en"` - 英文

## 工具参考

### 内容访问工具
- `get_template` - 获取文档模板
- `get_methodology_guide` - 访问方法论指南
- `list_available_content` - 列出所有可用内容
- `get_examples_and_case_studies` - 获取示例和案例研究

### 工作流管理工具
- `create_workflow` - 初始化新的功能工作流
- `get_workflow_status` - 检查当前工作流状态
- `transition_phase` - 转换到下一个阶段
- `navigate_backward` - 返回到之前的阶段
- `check_transition_requirements` - 验证阶段转换要求
- `get_approval_guidance` - 获取批准指导

### 验证工具
- `validate_document` - 验证规范文档质量
- `get_validation_checklist` - 获取质量检查清单
- `explain_validation_error` - 解释验证错误
- `validate_requirement_traceability` - 验证需求可追溯性

完整的API文档请参阅 [API.md](API.md)。
