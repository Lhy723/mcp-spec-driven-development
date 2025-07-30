# 贡献指南

欢迎为MCP规范驱动开发项目做出贡献！本文档提供了贡献指南。

## 行为准则

通过参与此项目，您同意遵守我们的行为准则。请尊重所有贡献者，为每个人创造一个友好的环境。

## 如何贡献

### 报告问题

1. **首先搜索现有问题**以避免重复
2. **创建新问题时使用问题模板**
3. **提供详细信息**包括：
   - 重现问题的步骤
   - 预期与实际行为
   - 环境详细信息（操作系统、Python版本等）
   - 错误消息和日志

### 建议功能

1. **检查现有功能请求**以避免重复
2. **描述用例**以及为什么该功能有价值
3. **提供示例**说明如何使用该功能
4. **考虑实现复杂性**和维护负担

### 贡献代码

#### 开发环境设置

1. **在GitHub上Fork仓库**
2. **本地克隆您的fork**：
   ```bash
   git clone https://github.com/your-username/mcp-spec-driven-development.git
   cd mcp-spec-driven-development
   ```

3. **设置开发环境**：
   ```bash
   # 如果还没有安装UV，请先安装
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # 安装依赖
   uv sync --group dev

   # 安装pre-commit钩子
   uv run pre-commit install
   ```

4. **创建功能分支**：
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### 开发指南

##### 代码风格
- 使用**Black**进行代码格式化：`uv run black src/ tests/`
- 使用**MyPy**进行类型检查：`uv run mypy src/`
- 遵循**PEP 8**风格指南
- 使用**有意义的变量和函数名**
- 为所有函数和方法添加**类型提示**
- 使用**中文注释**说明代码逻辑

##### 测试
- 为新功能编写**全面的测试**
- 保持**测试覆盖率 > 90%**
- 使用**pytest**测试框架
- 包括**单元测试**和**集成测试**
- 测试**错误条件**和**边界情况**

##### 文档
- 更新所有公共函数和类的**文档字符串**
- 如果添加新功能，更新**README.md**
- 为新的MCP工具更新**API.md**
- 为新功能添加**示例**
- 优先支持**中文文档**，必要时提供英文版本

#### 运行测试

```bash
# 运行所有测试
uv run pytest tests/ -v

# 运行带覆盖率的测试
uv run pytest tests/ --cov=src/mcp_spec_driven_development --cov-report=html

# 运行特定测试类别
uv run pytest tests/test_integration_end_to_end.py -v
uv run pytest tests/test_performance_benchmarks.py -v

# 运行代码检查和类型检查
uv run black --check src/ tests/
uv run mypy src/
```

#### 提交指南

- 使用**约定式提交格式**：
  - `feat:` 新功能
  - `fix:` 错误修复
  - `docs:` 文档更改
  - `test:` 测试添加/更改
  - `refactor:` 代码重构
  - `chore:` 维护任务

- 编写**清晰的提交消息**：
  ```
  feat: 为模板添加中文语言支持

  - 添加所有文档模板的中文版本
  - 更新内容工具以支持语言参数
  - 当中文不可用时添加英文回退
  ```

#### Pull Request Process

1. **Ensure all tests pass** and coverage is maintained
2. **Update documentation** as needed
3. **Add changelog entry** in CHANGELOG.md
4. **Create pull request** with:
   - Clear title and description
   - Reference to related issues
   - Screenshots for UI changes (if applicable)
   - Testing instructions

5. **Respond to review feedback** promptly
6. **Squash commits** if requested before merging

### Contributing Documentation

#### Types of Documentation
- **User guides** for AI assistants and end users
- **API documentation** for MCP tools
- **Developer documentation** for contributors
- **Examples and tutorials**
- **Troubleshooting guides**

#### Documentation Standards
- Use **clear, concise language**
- Provide **practical examples**
- Include **code snippets** with proper syntax highlighting
- Support **multiple languages** when possible
- Keep documentation **up-to-date** with code changes

### Contributing Templates and Content

#### Template Guidelines
- Follow **established format** and structure
- Include **comprehensive examples**
- Support **both English and Chinese**
- Ensure **consistency** across templates
- Test templates with **real use cases**

#### Methodology Content
- Base on **proven practices** and research
- Provide **clear explanations** and rationale
- Include **practical examples**
- Consider **different skill levels**
- Maintain **consistency** with overall methodology

## Development Workflow

### Branch Strategy
- `main` - stable release branch
- `develop` - integration branch for features
- `feature/*` - feature development branches
- `hotfix/*` - urgent bug fix branches

### Release Process
1. **Feature freeze** on develop branch
2. **Create release branch** from develop
3. **Final testing** and bug fixes
4. **Update version** in pyproject.toml
5. **Update CHANGELOG.md**
6. **Merge to main** and tag release
7. **Deploy to PyPI**

## Getting Help

### Communication Channels
- **GitHub Issues** - for bugs and feature requests
- **GitHub Discussions** - for questions and general discussion
- **Pull Request Reviews** - for code-specific discussions

### Resources
- [MCP Protocol Documentation](https://modelcontextprotocol.io/)
- [Python Development Best Practices](https://docs.python.org/3/tutorial/)
- [UV Package Manager](https://docs.astral.sh/uv/)
- [Pytest Documentation](https://docs.pytest.org/)

## Recognition

Contributors will be recognized in:
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **GitHub contributors** page

## License

By contributing to this project, you agree that your contributions will be licensed under the MIT License.

## Questions?

If you have questions about contributing, please:
1. Check existing documentation
2. Search GitHub issues and discussions
3. Create a new discussion or issue
4. Reach out to maintainers

Thank you for contributing to MCP Spec-Driven Development!
