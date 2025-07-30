# 项目结构

```
mcp-spec-driven-development/
├── .git/                           # Git版本控制
├── .gitignore                      # Git忽略文件配置
├── .kiro/                          # Kiro IDE配置
├── .pre-commit-config.yaml         # Pre-commit钩子配置
├── dist/                           # 构建分发文件
├── scripts/                        # 实用脚本
│   └── start-server.py            # 服务器启动脚本
├── src/                           # 源代码目录
│   └── mcp_spec_driven_development/
│       ├── __init__.py            # 包初始化文件
│       ├── __main__.py            # 模块入口点
│       ├── server.py              # MCP服务器主文件
│       ├── config.py              # 配置管理
│       ├── content/               # 内容管理模块
│       │   ├── __init__.py
│       │   ├── content_loader.py  # 内容加载器
│       │   ├── methodology.py     # 方法论管理
│       │   ├── templates.py       # 模板管理
│       │   └── data/              # 数据文件
│       │       ├── methodology/   # 方法论文件
│       │       │   ├── ears-format.md
│       │       │   ├── ears-format-zh.md
│       │       │   ├── phase-transitions.md
│       │       │   ├── workflow.md
│       │       │   └── workflow-zh.md
│       │       └── templates/     # 模板文件
│       │           ├── design-template.md
│       │           ├── design-template-zh.md
│       │           ├── requirements-template.md
│       │           ├── requirements-template-zh.md
│       │           ├── tasks-template.md
│       │           └── tasks-template-zh.md
│       ├── tools/                 # MCP工具实现
│       │   ├── __init__.py
│       │   ├── content_tools.py   # 内容访问工具
│       │   ├── task_execution_tools.py
│       │   ├── validation_tools.py # 验证工具
│       │   └── workflow_tools.py  # 工作流管理工具
│       ├── validation/            # 文档验证模块
│       │   ├── __init__.py
│       │   ├── design_validator.py
│       │   ├── requirements_validator.py
│       │   └── task_validator.py
│       └── workflow/              # 工作流管理模块
│           ├── __init__.py
│           ├── models.py          # 数据模型
│           ├── phase_manager.py   # 阶段管理器
│           └── state_tracker.py   # 状态跟踪器
├── tests/                         # 测试套件
│   ├── __init__.py
│   ├── test_*.py                  # 各种测试文件
│   └── ...
├── .venv/                         # 虚拟环境（本地开发）
├── API.md                         # API文档
├── CHANGELOG.md                   # 更新日志
├── CONTRIBUTING.md                # 贡献指南
├── INSTALLATION.md                # 安装指南
├── LICENSE                        # MIT许可证
├── MAINTENANCE.md                 # 维护指南
├── PROJECT_STRUCTURE.md           # 项目结构说明（本文件）
├── pyproject.toml                 # 项目配置文件
├── README.md                      # 项目说明（中文）
├── README-en.md                   # 项目说明（英文）
├── TROUBLESHOOTING.md             # 故障排除指南
├── USER_GUIDE.md                  # 用户指南
└── uv.lock                        # UV依赖锁定文件
```

## 核心模块说明

### 服务器核心
- `server.py` - MCP服务器主入口点，处理工具调用和路由
- `config.py` - 服务器配置管理，支持环境变量配置
- `__init__.py` - 包初始化和版本信息

### 内容管理 (`content/`)
- `templates.py` - 文档模板管理，支持中英文模板
- `methodology.py` - 方法论指南管理，包含工作流和EARS格式指导
- `content_loader.py` - 统一的内容加载接口
- `data/` - 存储模板和方法论的Markdown文件

### MCP工具 (`tools/`)
- `content_tools.py` - 内容访问工具（模板、指南、示例）
- `workflow_tools.py` - 工作流管理工具（创建、状态、转换）
- `validation_tools.py` - 文档验证工具（质量检查、错误解释）

### 工作流管理 (`workflow/`)
- `models.py` - 工作流数据模型定义
- `phase_manager.py` - 阶段管理和转换逻辑
- `state_tracker.py` - 工作流状态跟踪

### 文档验证 (`validation/`)
- `requirements_validator.py` - 需求文档验证
- `design_validator.py` - 设计文档验证
- `task_validator.py` - 任务文档验证

## 文档结构

### 用户文档
- `README.md` - 项目主要说明（中文）
- `README-en.md` - 项目说明英文版
- `INSTALLATION.md` - 详细安装指南
- `USER_GUIDE.md` - AI助手使用指南
- `API.md` - 完整的API参考文档

### 开发文档
- `CONTRIBUTING.md` - 贡献者指南
- `MAINTENANCE.md` - 维护和更新程序
- `TROUBLESHOOTING.md` - 常见问题解决方案
- `CHANGELOG.md` - 版本更新历史

### 配置文件
- `pyproject.toml` - 项目配置、依赖和构建设置
- `.gitignore` - Git忽略文件配置
- `.pre-commit-config.yaml` - 代码质量检查配置
- `uv.lock` - UV包管理器依赖锁定

## 特性

### 多语言支持
- 所有模板和方法论文档都有中英文版本
- 工具支持 `language` 参数选择语言
- 默认使用中文，英文作为回退

### 模块化设计
- 清晰的模块分离和职责划分
- 易于扩展和维护
- 完整的类型提示支持

### 质量保证
- 全面的测试覆盖
- 代码格式化和类型检查
- 文档验证和质量控制
- Pre-commit钩子确保代码质量

### 部署支持
- 支持UV、UVX和传统pip安装
- 多种MCP客户端配置方式
- 环境变量配置支持
- 健康监控和日志记录
