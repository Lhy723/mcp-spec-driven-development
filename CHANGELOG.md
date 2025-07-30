# 更新日志

此项目的所有重要更改都将记录在此文件中。

格式基于[Keep a Changelog](https://keepachangelog.com/en/1.0.0/)，
此项目遵循[语义化版本](https://semver.org/spec/v2.0.0.html)。

## [未发布]

## [0.1.0] - 2025-01-29

### 新增
- MCP规范驱动开发工具首次发布
- 三阶段工作流系统（需求 → 设计 → 任务）
- EARS格式需求支持
- 全面的文档模板
- 内置验证系统
- 多语言支持（英文和中文）
- MCP协议集成
- 用于模板和方法论的内容访问工具
- 用于阶段转换的工作流管理工具
- 用于文档质量保证的验证工具
- UV和UVX支持，便于部署
- 全面的测试套件
- 中英文双语文档

### 功能特性
- **内容访问工具**：
  - `get_template` - 获取文档模板
  - `get_methodology_guide` - 访问方法论指南
  - `list_available_content` - 列出可用内容
  - `get_examples_and_case_studies` - 获取示例和案例研究

- **工作流管理工具**：
  - `create_workflow` - 初始化新功能工作流
  - `get_workflow_status` - 检查工作流状态
  - `transition_phase` - 在阶段间移动
  - `navigate_backward` - 返回到之前的阶段
  - `check_transition_requirements` - 验证转换要求
  - `get_approval_guidance` - 获取批准指导

- **验证工具**：
  - `validate_document` - 验证文档质量
  - `get_validation_checklist` - 获取质量检查清单
  - `explain_validation_error` - 解释验证错误
  - `validate_requirement_traceability` - 验证可追溯性

### 技术特性
- Python 3.10+ 支持
- MCP协议 1.12.2+ 兼容性
- 具有可配置级别的结构化日志
- 健康监控和性能跟踪
- 全面的错误处理和恢复
- 整个代码库的类型提示
- MCP操作的异步/等待支持

### 文档
- 完整的安装指南
- AI助手用户指南
- 带示例的API文档
- 故障排除指南
- 维护程序
- 多语言文档支持

[Unreleased]: https://github.com/your-org/mcp-spec-driven-development/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/your-org/mcp-spec-driven-development/releases/tag/v0.1.0
