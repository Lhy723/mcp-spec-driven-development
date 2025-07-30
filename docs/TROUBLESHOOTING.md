# 故障排除指南

本指南帮助解决使用MCP规范驱动开发工具时的常见问题。

## 安装和设置问题

### 包安装问题

#### 问题：`pip install mcp-spec-driven-development` 失败

**症状：**
- 找不到包的错误
- 依赖解析失败
- 权限错误

**解决方案：**

1. **更新pip并重试：**
   ```bash
   python -m pip install --upgrade pip
   pip install mcp-spec-driven-development
   ```

2. **使用虚拟环境：**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install mcp-spec-driven-development
   ```

3. **从源码安装：**
   ```bash
   git clone https://github.com/your-org/mcp-spec-driven-development.git
   cd mcp-spec-driven-development
   pip install -e .
   ```

4. **使用UV安装（推荐）：**
   ```bash
   uv sync
   ```

#### 问题：安装后导入错误

**症状：**
- `ModuleNotFoundError: No module named 'mcp_spec_driven_development'`
- 依赖导入错误

**解决方案：**

1. **验证安装：**
   ```bash
   pip list | grep mcp-spec-driven-development
   python -c "import mcp_spec_driven_development; print('安装成功')"
   ```

2. **Check Python path:**
   ```bash
   python -c "import sys; print(sys.path)"
   ```

3. **Reinstall with dependencies:**
   ```bash
   pip uninstall mcp-spec-driven-development
   pip install mcp-spec-driven-development[dev]
   ```

### Server Startup Issues

#### Issue: Server fails to start

**Symptoms:**
- Server exits immediately
- Connection refused errors
- Configuration errors

**Solutions:**

1. **Check configuration:**
   ```bash
   export MCP_LOG_LEVEL=DEBUG
   python -m mcp_spec_driven_development
   ```

2. **Verify dependencies:**
   ```bash
   python -c "import mcp, pydantic, jinja2, structlog; print('All dependencies OK')"
   ```

3. **Check file permissions:**
   ```bash
   ls -la scripts/start-server.py
   chmod +x scripts/start-server.py
   ```

#### Issue: MCP client cannot connect

**Symptoms:**
- Client connection timeouts
- Protocol errors
- Tool discovery failures

**Solutions:**

1. **Verify MCP client configuration:**
   ```json
   {
     "mcpServers": {
       "spec-driven-development": {
         "command": "python",
         "args": ["-m", "mcp_spec_driven_development"],
         "env": {
           "MCP_LOG_LEVEL": "DEBUG"
         }
       }
     }
   }
   ```

2. **Test server directly:**
   ```bash
   echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}' | python -m mcp_spec_driven_development
   ```

3. **Check logs:**
   ```bash
   export MCP_LOG_FILE=/tmp/mcp-debug.log
   python -m mcp_spec_driven_development
   tail -f /tmp/mcp-debug.log
   ```

## Tool Usage Issues

### Content Access Problems

#### Issue: Templates not loading

**Symptoms:**
- `get_template` returns empty content
- Template format errors
- Missing template sections

**Solutions:**

1. **Check content directory:**
   ```bash
   python -c "from mcp_spec_driven_development.config import ServerConfig; print(ServerConfig.from_env().content_root)"
   ```

2. **Verify template files exist:**
   ```bash
   ls -la src/mcp_spec_driven_development/content/data/templates/
   ```

3. **Test template loading:**
   ```python
   from mcp_spec_driven_development.content.templates import TemplateManager
   tm = TemplateManager()
   print(tm.get_template("requirements"))
   ```

#### Issue: Methodology guides not accessible

**Symptoms:**
- `get_methodology_guide` returns errors
- Missing methodology content
- Outdated guidance

**Solutions:**

1. **Check methodology files:**
   ```bash
   ls -la src/mcp_spec_driven_development/content/data/methodology/
   ```

2. **Test methodology loading:**
   ```python
   from mcp_spec_driven_development.content.methodology import MethodologyManager
   mm = MethodologyManager()
   print(mm.get_guide("workflow"))
   ```

3. **Update content cache:**
   ```bash
   export MCP_CACHE_TTL=0  # Disable caching
   python -m mcp_spec_driven_development
   ```

### Workflow Management Problems

#### Issue: Workflow state not persisting

**Symptoms:**
- Workflow status resets between sessions
- Phase transitions not saved
- Lost approval status

**Solutions:**

1. **Check workflow state directory:**
   ```bash
   ls -la .kiro/specs/
   ```

2. **Verify file permissions:**
   ```bash
   chmod -R 755 .kiro/specs/
   ```

3. **Test state persistence:**
   ```python
   from mcp_spec_driven_development.workflow.state_tracker import StateTracker
   st = StateTracker()
   print(st.get_workflow_state("test-feature"))
   ```

#### Issue: Phase transitions blocked

**Symptoms:**
- Cannot transition to next phase
- Approval requirements not met
- Validation blocking transition

**Solutions:**

1. **Check transition requirements:**
   ```json
   {
     "name": "check_transition_requirements",
     "arguments": {
       "feature_name": "your-feature",
       "target_phase": "design"
     }
   }
   ```

2. **Validate current phase document:**
   ```json
   {
     "name": "validate_document",
     "arguments": {
       "document_type": "requirements",
       "content": "[your document content]"
     }
   }
   ```

3. **Get approval guidance:**
   ```json
   {
     "name": "get_approval_guidance",
     "arguments": {
       "feature_name": "your-feature",
       "phase": "requirements"
     }
   }
   ```

### Validation Issues

#### Issue: Document validation fails

**Symptoms:**
- Validation errors with unclear messages
- False positive validation failures
- Inconsistent validation results

**Solutions:**

1. **Get detailed error explanation:**
   ```json
   {
     "name": "explain_validation_error",
     "arguments": {
       "error_type": "[error from validation]",
       "context": "Additional context"
     }
   }
   ```

2. **Check validation checklist:**
   ```json
   {
     "name": "get_validation_checklist",
     "arguments": {
       "document_type": "requirements"
     }
   }
   ```

3. **Test with known good document:**
   ```json
   {
     "name": "get_examples_and_case_studies",
     "arguments": {
       "example_type": "requirements-examples"
     }
   }
   ```

#### Issue: EARS format validation problems

**Symptoms:**
- EARS format not recognized
- Acceptance criteria validation fails
- User story format errors

**Solutions:**

1. **Review EARS format guide:**
   ```json
   {
     "name": "get_methodology_guide",
     "arguments": {
       "guide_type": "ears-format"
     }
   }
   ```

2. **Check format examples:**
   ```
   Correct EARS format:
   - WHEN [event] THEN [system] SHALL [response]
   - IF [precondition] THEN [system] SHALL [response]
   - WHERE [feature] IS [state] THEN [system] SHALL [response]
   ```

3. **Validate incrementally:**
   - Start with one requirement
   - Add requirements one by one
   - Validate after each addition

## Performance Issues

### Slow Response Times

#### Issue: Tools respond slowly

**Symptoms:**
- Long delays for tool responses
- Timeouts on tool calls
- High memory usage

**Solutions:**

1. **Enable performance monitoring:**
   ```bash
   export MCP_HEALTH_CHECK_ENABLED=true
   python -m mcp_spec_driven_development
   ```

2. **Adjust cache settings:**
   ```bash
   export MCP_CACHE_TTL=7200  # 2 hours
   export MCP_MAX_CONTENT_SIZE=2097152  # 2MB
   ```

3. **Check system resources:**
   ```bash
   top -p $(pgrep -f mcp_spec_driven_development)
   ```

#### Issue: Memory usage grows over time

**Symptoms:**
- Increasing memory consumption
- Out of memory errors
- System slowdown

**Solutions:**

1. **Monitor memory usage:**
   ```python
   import psutil
   import os
   process = psutil.Process(os.getpid())
   print(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.2f} MB")
   ```

2. **Reduce cache size:**
   ```bash
   export MCP_CACHE_TTL=1800  # 30 minutes
   export MCP_MAX_CONTENT_SIZE=524288  # 512KB
   ```

3. **Restart server periodically:**
   ```bash
   # Add to cron for periodic restart
   0 */6 * * * systemctl restart mcp-spec-driven-development
   ```

## Content and Template Issues

### Missing or Corrupted Content

#### Issue: Content files missing

**Symptoms:**
- Empty responses from content tools
- File not found errors
- Incomplete templates

**Solutions:**

1. **Verify content structure:**
   ```bash
   find src/mcp_spec_driven_development/content/data -type f -name "*.md"
   ```

2. **Reinstall package:**
   ```bash
   pip uninstall mcp-spec-driven-development
   pip install mcp-spec-driven-development --force-reinstall
   ```

3. **Check content integrity:**
   ```python
   from mcp_spec_driven_development.content.content_loader import ContentLoader
   loader = ContentLoader()
   print(loader.verify_content_integrity())
   ```

#### Issue: Template formatting problems

**Symptoms:**
- Malformed template output
- Missing placeholders
- Incorrect structure

**Solutions:**

1. **Check template syntax:**
   ```bash
   python -c "import jinja2; jinja2.Template(open('template.md').read())"
   ```

2. **Validate template content:**
   ```python
   from mcp_spec_driven_development.content.templates import TemplateManager
   tm = TemplateManager()
   template = tm.get_template("requirements")
   print(len(template))  # Should be > 0
   ```

3. **Use fallback content:**
   ```python
   from mcp_spec_driven_development.fallback_content import get_fallback_template
   print(get_fallback_template("requirements"))
   ```

## Integration Issues

### MCP Client Integration

#### Issue: Tools not appearing in client

**Symptoms:**
- Empty tool list
- Client cannot discover tools
- Tool definitions missing

**Solutions:**

1. **Test tool listing:**
   ```bash
   echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | python -m mcp_spec_driven_development
   ```

2. **Check tool registration:**
   ```python
   from mcp_spec_driven_development.server import server
   print(len(server._tool_handlers))
   ```

3. **Verify MCP protocol compliance:**
   ```bash
   python -m pytest tests/test_mcp_protocol_compliance.py -v
   ```

#### Issue: Tool calls fail

**Symptoms:**
- Tool execution errors
- Invalid argument errors
- Response format issues

**Solutions:**

1. **Test tool calls directly:**
   ```bash
   echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "get_template", "arguments": {"template_type": "requirements"}}}' | python -m mcp_spec_driven_development
   ```

2. **Check argument validation:**
   ```python
   from mcp_spec_driven_development.tools.content_tools import ContentAccessTools
   tools = ContentAccessTools()
   result = tools.handle_tool_call("get_template", {"template_type": "requirements"})
   print(result)
   ```

3. **Enable debug logging:**
   ```bash
   export MCP_LOG_LEVEL=DEBUG
   python -m mcp_spec_driven_development
   ```

## Logging and Debugging

### Log Analysis

#### Issue: Understanding log messages

**Common Log Patterns:**

1. **Successful tool call:**
   ```
   INFO Tool call completed tool_name=get_template success=True
   ```

2. **Validation failure:**
   ```
   WARNING Validation failed document_type=requirements errors=3
   ```

3. **Workflow transition:**
   ```
   INFO Phase transition feature=my-feature from=requirements to=design
   ```

#### Issue: Log file not created

**Solutions:**

1. **Check log file permissions:**
   ```bash
   touch /var/log/mcp-spec-driven-development.log
   chmod 666 /var/log/mcp-spec-driven-development.log
   ```

2. **Use alternative log location:**
   ```bash
   export MCP_LOG_FILE=./mcp-debug.log
   python -m mcp_spec_driven_development
   ```

3. **Enable console logging:**
   ```bash
   export MCP_LOG_FORMAT=console
   python -m mcp_spec_driven_development
   ```

### Debug Mode

#### Enable comprehensive debugging:

```bash
export MCP_LOG_LEVEL=DEBUG
export MCP_LOG_FORMAT=console
export MCP_HEALTH_CHECK_ENABLED=true
export MCP_CACHE_TTL=0  # Disable caching
python -m mcp_spec_driven_development
```

## Health Monitoring

### Health Check Failures

#### Issue: Health checks failing

**Symptoms:**
- Health status reports unhealthy
- Component checks failing
- Performance degradation

**Solutions:**

1. **Check individual components:**
   ```python
   from mcp_spec_driven_development.monitoring import health_monitor
   import asyncio

   async def check_health():
       content_ok = await health_monitor._check_content_system()
       workflow_ok = await health_monitor._check_workflow_system()
       validation_ok = await health_monitor._check_validation_system()
       print(f"Content: {content_ok}, Workflow: {workflow_ok}, Validation: {validation_ok}")

   asyncio.run(check_health())
   ```

2. **Get health report:**
   ```python
   from mcp_spec_driven_development.monitoring import health_monitor
   print(health_monitor.get_health_report())
   ```

3. **Reset health state:**
   ```python
   from mcp_spec_driven_development.monitoring import health_monitor
   health_monitor.metrics = health_monitor.HealthMetrics()
   ```

## Recovery Procedures

### Complete System Reset

If all else fails, perform a complete reset:

1. **Stop the server:**
   ```bash
   pkill -f mcp_spec_driven_development
   ```

2. **Clear cache and state:**
   ```bash
   rm -rf ~/.cache/mcp-spec-driven-development/
   rm -rf .kiro/specs/*/workflow-state.json
   ```

3. **Reinstall package:**
   ```bash
   pip uninstall mcp-spec-driven-development
   pip install mcp-spec-driven-development --force-reinstall
   ```

4. **Restart with clean configuration:**
   ```bash
   unset MCP_LOG_FILE MCP_CONTENT_ROOT MCP_CACHE_TTL
   python -m mcp_spec_driven_development
   ```

### Backup and Restore

#### Backup important data:

```bash
# Backup specs
tar -czf specs-backup.tar.gz .kiro/specs/

# Backup configuration
cp .env .env.backup

# Backup logs
cp /var/log/mcp-spec-driven-development.log mcp.log.backup
```

#### Restore from backup:

```bash
# Restore specs
tar -xzf specs-backup.tar.gz

# Restore configuration
cp .env.backup .env
```

## Getting Help

### Diagnostic Information

When reporting issues, include:

1. **System information:**
   ```bash
   python --version
   pip list | grep mcp
   uname -a
   ```

2. **Configuration:**
   ```bash
   env | grep MCP_
   ```

3. **Error logs:**
   ```bash
   tail -50 /var/log/mcp-spec-driven-development.log
   ```

4. **Health status:**
   ```python
   from mcp_spec_driven_development.monitoring import health_monitor
   print(health_monitor.get_health_report())
   ```

### Support Channels

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: Check API.md and USER_GUIDE.md
- **Community**: Join discussions and get help
- **Professional Support**: Contact for enterprise support

### Self-Diagnosis

Run the deployment verification tests:

```bash
python -m pytest tests/test_deployment_verification.py -v
```

This will identify most common configuration and setup issues.

## Prevention

### Best Practices

1. **Regular Updates:**
   ```bash
   pip install --upgrade mcp-spec-driven-development
   ```

2. **Monitor Health:**
   ```bash
   export MCP_HEALTH_CHECK_ENABLED=true
   ```

3. **Backup Regularly:**
   ```bash
   # Add to cron
   0 2 * * * tar -czf /backup/specs-$(date +\%Y\%m\%d).tar.gz .kiro/specs/
   ```

4. **Use Version Control:**
   ```bash
   git init .kiro/specs/
   git add .
   git commit -m "Initial spec commit"
   ```

5. **Test Changes:**
   ```bash
   python -m pytest tests/ -v
   ```

Remember: Most issues can be resolved by checking logs, verifying configuration, and ensuring all dependencies are properly installed.
