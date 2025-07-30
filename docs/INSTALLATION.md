# 安装指南

本指南介绍如何为AI助手安装和设置MCP规范驱动开发工具。

## 前置要求

- Python 3.10 或更高版本
- pip 或 uv 包管理器
- Git（用于开发安装）

## 安装方法

### 方法1：从PyPI安装（推荐）

```bash
# 使用 pip
pip install mcp-spec-driven-development

# 使用 uv（更快）
uv add mcp-spec-driven-development
```

### 方法2：从源码安装

```bash
# 克隆仓库
git clone https://github.com/your-org/mcp-spec-driven-development.git
cd mcp-spec-driven-development

# 使用 uv 安装（推荐）
uv sync

# 或使用 pip 安装
pip install -e .
```

### 方法3：开发安装

```bash
# 克隆并安装开发依赖
git clone https://github.com/your-org/mcp-spec-driven-development.git
cd mcp-spec-driven-development

# 安装开发依赖
uv sync --group dev

# 或使用 pip
pip install -e ".[dev]"
```

## 配置

### 环境变量

服务器可以通过环境变量进行配置：

```bash
# 服务器标识
export MCP_SERVER_NAME="mcp-spec-driven-development"
export MCP_SERVER_VERSION="0.1.0"

# 日志配置
export MCP_LOG_LEVEL="INFO"          # DEBUG, INFO, WARNING, ERROR, CRITICAL
export MCP_LOG_FORMAT="console"      # console, json
export MCP_LOG_FILE="/path/to/log"   # 可选的日志文件路径

# 内容配置
export MCP_CONTENT_ROOT="/path/to/content"  # 可选的自定义内容路径

# 性能设置
export MCP_MAX_CONTENT_SIZE="1048576"  # 1MB 最大内容大小
export MCP_CACHE_TTL="3600"            # 1小时缓存TTL

# 健康监控
export MCP_HEALTH_CHECK_ENABLED="true"
export MCP_HEALTH_CHECK_INTERVAL="30"  # 秒
export MCP_HEALTH_CHECK_TIMEOUT="5"    # 秒
```

### 配置文件

在项目目录中创建 `.env` 文件：

```env
MCP_LOG_LEVEL=INFO
MCP_LOG_FORMAT=console
MCP_HEALTH_CHECK_ENABLED=true
```

## 运行服务器

### 方法1：直接Python执行

```bash
# 直接运行服务器
python -m mcp_spec_driven_development

# 或使用安装的脚本
mcp-spec-driven-development
```

### 方法2：使用UV运行（推荐）

```bash
# 使用 uv run 运行
uv run python -m mcp_spec_driven_development

# 或使用脚本
uv run mcp-spec-driven-development
```

### 方法3：使用启动脚本

```bash
# 使用提供的启动脚本（生产环境）
python scripts/start-server.py
```

### 方法4：作为服务运行（Linux/systemd）

创建systemd服务文件 `/etc/systemd/system/mcp-spec-driven-development.service`：

```ini
[Unit]
Description=MCP 规范驱动开发服务器
After=network.target

[Service]
Type=simple
User=mcp
Group=mcp
WorkingDirectory=/opt/mcp-spec-driven-development
Environment=MCP_LOG_LEVEL=INFO
Environment=MCP_LOG_FORMAT=json
Environment=MCP_LOG_FILE=/var/log/mcp-spec-driven-development.log
ExecStart=/opt/mcp-spec-driven-development/.venv/bin/python scripts/start-server.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```bash
sudo systemctl enable mcp-spec-driven-development
sudo systemctl start mcp-spec-driven-development
sudo systemctl status mcp-spec-driven-development
```

## MCP客户端配置

### 用于AI助手

将服务器添加到MCP客户端配置中：

```json
{
  "mcpServers": {
    "spec-driven-development": {
      "command": "mcp-spec-driven-development",
      "args": [],
      "env": {
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 使用UV方式（推荐）

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

### 用于开发/测试

```json
{
  "mcpServers": {
    "spec-driven-development": {
      "command": "python",
      "args": ["-m", "mcp_spec_driven_development"],
      "cwd": "/path/to/mcp-spec-driven-development",
      "env": {
        "MCP_LOG_LEVEL": "DEBUG",
        "MCP_LOG_FORMAT": "console"
      }
    }
  }
}
```

## 验证安装

### 测试安装

```bash
# 测试包是否正确安装
python -c "import mcp_spec_driven_development; print('安装成功')"

# 测试服务器启动（没有MCP客户端时会立即退出）
python -m mcp_spec_driven_development
```

### 运行健康检查

```bash
# 运行部署验证测试
pytest tests/test_deployment_verification.py -v

# 运行所有测试以验证安装
pytest tests/ -v
```

### 检查服务器健康状态

服务器提供健康监控功能。运行时，可以通过监控系统检查健康状态。

## 故障排除

### 常见问题

#### 导入错误

```bash
# 如果遇到导入错误，确保包已安装
pip list | grep mcp-spec-driven-development

# 必要时重新安装
pip uninstall mcp-spec-driven-development
pip install mcp-spec-driven-development
```

#### 权限错误

```bash
# 如果作为服务运行，确保权限正确
sudo chown -R mcp:mcp /opt/mcp-spec-driven-development
sudo chmod +x scripts/start-server.py
```

#### 日志文件问题

```bash
# 确保日志目录存在且可写
sudo mkdir -p /var/log
sudo chown mcp:mcp /var/log/mcp-spec-driven-development.log
```

### 调试模式

启用调试日志进行故障排除：

```bash
export MCP_LOG_LEVEL=DEBUG
export MCP_LOG_FORMAT=console
python -m mcp_spec_driven_development
```

### 性能问题

如果遇到性能问题：

1. 增加缓存TTL：`export MCP_CACHE_TTL=7200`
2. 减少最大内容大小：`export MCP_MAX_CONTENT_SIZE=524288`
3. 监控健康检查：`export MCP_HEALTH_CHECK_ENABLED=true`

## 更新

### 从PyPI更新

```bash
# 使用 pip
pip install --upgrade mcp-spec-driven-development

# 使用 uv
uv add mcp-spec-driven-development --upgrade
```

### 从源码更新

```bash
cd mcp-spec-driven-development
git pull origin main
uv sync
```

## 卸载

```bash
# 卸载包
pip uninstall mcp-spec-driven-development

# 移除服务（如果已安装）
sudo systemctl stop mcp-spec-driven-development
sudo systemctl disable mcp-spec-driven-development
sudo rm /etc/systemd/system/mcp-spec-driven-development.service

# 移除日志和数据
sudo rm -rf /var/log/mcp-spec-driven-development.log
```

## 支持

如有安装问题：

1. 查看[故障排除指南](TROUBLESHOOTING.md)
2. 检查服务器日志中的错误信息
3. 运行部署验证测试
4. 查看GitHub issues了解已知问题

## 下一步

安装完成后，请参阅：

- [用户指南](USER_GUIDE.md) - 如何与AI助手一起使用该工具
- [API文档](API.md) - 完整的工具参考
- [故障排除指南](TROUBLESHOOTING.md) - 常见问题和解决方案
