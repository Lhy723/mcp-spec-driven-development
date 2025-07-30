# MCP规范驱动开发工具

一个为AI助手提供系统化功能开发方法论的MCP（模型上下文协议）工具。

[中文文档](README.md) | [English](README-en.md)

## 概述

MCP规范驱动开发工具使AI编程助手能够指导用户通过结构化的三阶段工作流程创建高质量的功能规范：

1. **需求阶段** - 将想法转化为EARS格式的结构化需求
2. **设计阶段** - 创建全面的技术设计文档
3. **任务阶段** - 生成可执行的实施计划

## 特性

- 🎯 **系统化方法论** - 三阶段工作流确保质量和完整性
- 📝 **EARS格式需求** - 结构化、可测试的验收标准
- 🏗️ **全面设计模板** - 包含架构、组件和测试策略
- ✅ **可执行任务计划** - 具有需求可追溯性的离散编码任务
- 🔍 **内置验证** - 质量检查和文档验证
- 📊 **进度跟踪** - 工作流状态管理和阶段转换
- 🔄 **迭代改进** - 支持反馈和修订

## 快速开始

### 安装

#### 使用UV（推荐）
```bash
# 克隆仓库
git clone https://github.com/your-org/mcp-spec-driven-development.git
cd mcp-spec-driven-development

# 使用UV安装
uv sync
```

#### 使用pip
```bash
pip install mcp-spec-driven-development
```

### MCP客户端配置

将服务器添加到你的MCP客户端配置中：

#### 使用UV运行（推荐）
```json
{
  "mcpServers": {
    "spec-driven-development": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_spec_driven_development"],
      "cwd": "/path/to/mcp-spec-driven-development",
      "env": {
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### 使用Python模块
```json
{
  "mcpServers": {
    "spec-driven-development": {
      "command": "python",
      "args": ["-m", "mcp_spec_driven_development"],
      "env": {
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 基本使用

1. **创建新工作流**
   ```json
   {
     "name": "create_workflow",
     "arguments": {
       "feature_name": "user-authentication",
       "initial_description": "添加用户登录和注册功能"
     }
   }
   ```

2. **获取需求模板**
   ```json
   {
     "name": "get_template",
     "arguments": {
       "template_type": "requirements"
     }
   }
   ```

3. **验证文档**
   ```json
   {
     "name": "validate_document",
     "arguments": {
       "document_type": "requirements",
       "content": "你的需求文档内容..."
     }
   }
   ```

## 工作流程

### 阶段1：需求开发
- 使用结构化模板创建需求文档
- 以EARS格式编写验收标准
- 验证需求完整性和质量
- 获得利益相关者批准

### 阶段2：设计开发
- 基于批准的需求创建技术设计
- 包含架构图和组件规范
- 定义数据模型和接口
- 规划错误处理和测试策略

### 阶段3：任务规划
- 将设计分解为可执行的编码任务
- 确保需求可追溯性
- 按逻辑顺序排列任务
- 包含测试和验证步骤

## 可用工具

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

### 验证工具
- `validate_document` - 验证规范文档质量
- `get_validation_checklist` - 获取质量检查清单
- `explain_validation_error` - 解释验证错误
- `validate_requirement_traceability` - 验证需求可追溯性

## 环境变量配置

```bash
# 服务器配置
export MCP_SERVER_NAME="mcp-spec-driven-development"
export MCP_SERVER_VERSION="0.0.1"

# 日志配置
export MCP_LOG_LEVEL="INFO"          # DEBUG, INFO, WARNING, ERROR, CRITICAL
export MCP_LOG_FORMAT="console"      # console, json
export MCP_LOG_FILE="/path/to/log"   # 可选的日志文件路径

# 性能设置
export MCP_MAX_CONTENT_SIZE="1048576"  # 1MB 最大内容大小
export MCP_CACHE_TTL="3600"            # 1小时缓存TTL

# 健康监控
export MCP_HEALTH_CHECK_ENABLED="true"
export MCP_HEALTH_CHECK_INTERVAL="30"  # 秒
```

## 开发

### 设置开发环境
```bash
# 克隆仓库
git clone https://github.com/your-org/mcp-spec-driven-development.git
cd mcp-spec-driven-development

# 安装开发依赖
uv sync --group dev

# 运行测试
pytest tests/ -v

# 运行代码检查
black src/ tests/
mypy src/
```

### 运行测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试类别
pytest tests/test_integration_end_to_end.py -v
pytest tests/test_performance_benchmarks.py -v

# 运行覆盖率测试
pytest tests/ --cov=src/mcp_spec_driven_development --cov-report=html
```

## 项目结构

```
mcp-spec-driven-development/
├── src/mcp_spec_driven_development/
│   ├── __init__.py
│   ├── server.py                    # MCP服务器入口点
│   ├── config.py                    # 配置管理
│   ├── content/                     # 内容管理
│   │   ├── templates.py
│   │   ├── methodology.py
│   │   └── data/                    # 模板和方法论文件
│   ├── tools/                       # MCP工具实现
│   │   ├── content_tools.py
│   │   ├── workflow_tools.py
│   │   └── validation_tools.py
│   ├── workflow/                    # 工作流管理
│   │   ├── models.py
│   │   ├── phase_manager.py
│   │   └── state_tracker.py
│   └── validation/                  # 文档验证
│       ├── requirements_validator.py
│       ├── design_validator.py
│       └── task_validator.py
├── tests/                          # 测试套件
├── scripts/                        # 实用脚本
├── docs/                          # 文档
│   ├── INSTALLATION.md            # 安装指南
│   ├── USER_GUIDE.md             # 用户指南
│   ├── API.md                    # API文档
│   └── TROUBLESHOOTING.md        # 故障排除
└── pyproject.toml                # 项目配置
```

## 文档

- [安装指南](docs/INSTALLATION.md) - 详细的安装和设置说明
- [用户指南](docs/USER_GUIDE.md) - 如何与AI助手一起使用该工具
- [API文档](docs/API.md) - 完整的工具参考和示例
- [故障排除](docs/TROUBLESHOOTING.md) - 常见问题和解决方案
- [维护指南](docs/MAINTENANCE.md) - 维护和更新程序

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 支持

- 📖 查看[文档](docs/)了解详细指南
- 🐛 在[GitHub Issues](https://github.com/Lhy723/mcp-spec-driven-development/issues)报告问题
- 💬 在[讨论区](https://github.com/Lhy723/mcp-spec-driven-development/discussions)提问

## 更新日志

查看 [CHANGELOG.md](CHANGELOG.md) 了解版本历史和更改。

---

**注意**：此工具专为与AI编程助手一起使用而设计，通过MCP协议提供结构化的功能开发方法论。
