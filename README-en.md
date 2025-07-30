# MCP Spec-Driven Development

A Model Context Protocol (MCP) tool that provides AI assistants with a systematic methodology for feature development.

[中文文档](README-zh.md) | [English](README.md)

## Overview

The MCP Spec-Driven Development tool enables AI programming assistants to guide users through creating high-quality feature specifications using a structured three-phase workflow:

1. **Requirements Phase** - Transform ideas into structured EARS format requirements
2. **Design Phase** - Create comprehensive technical design documents
3. **Tasks Phase** - Generate actionable implementation plans

## Features

- 🎯 **Systematic Methodology** - Three-phase workflow ensures quality and completeness
- 📝 **EARS Format Requirements** - Structured, testable acceptance criteria
- 🏗️ **Comprehensive Design Templates** - Include architecture, components, and testing strategies
- ✅ **Actionable Task Plans** - Discrete coding tasks with requirement traceability
- 🔍 **Built-in Validation** - Quality checks and document validation
- 📊 **Progress Tracking** - Workflow state management and phase transitions
- 🔄 **Iterative Improvement** - Support for feedback and revisions
- 🌐 **Multi-language Support** - Available in English and Chinese

## Quick Start

### Installation

#### Using UV (Recommended)
```bash
# Clone the repository
git clone https://github.com/your-org/mcp-spec-driven-development.git
cd mcp-spec-driven-development

# Install with UV
uv sync
```

#### Using pip
```bash
pip install mcp-spec-driven-development
```

### MCP Client Configuration

Add the server to your MCP client configuration:

#### Using UV (Recommended)
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

#### Using UVX
```json
{
  "mcpServers": {
    "spec-driven-development": {
      "command": "uvx",
      "args": ["--from", ".", "mcp-spec-driven-development"],
      "cwd": "/path/to/mcp-spec-driven-development",
      "env": {
        "MCP_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

#### Using Python Module
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

### Basic Usage

1. **Create a new workflow**
   ```json
   {
     "name": "create_workflow",
     "arguments": {
       "feature_name": "user-authentication",
       "initial_description": "Add user login and registration functionality"
     }
   }
   ```

2. **Get a requirements template**
   ```json
   {
     "name": "get_template",
     "arguments": {
       "template_type": "requirements",
       "language": "en"
     }
   }
   ```

3. **Validate documents**
   ```json
   {
     "name": "validate_document",
     "arguments": {
       "document_type": "requirements",
       "content": "Your requirements document content..."
     }
   }
   ```

## Workflow Process

### Phase 1: Requirements Development
- Create requirements document using structured templates
- Write acceptance criteria in EARS format
- Validate requirements completeness and quality
- Obtain stakeholder approval

### Phase 2: Design Development
- Create technical design based on approved requirements
- Include architecture diagrams and component specifications
- Define data models and interfaces
- Plan error handling and testing strategies

### Phase 3: Task Planning
- Break down design into executable coding tasks
- Ensure requirement traceability
- Sequence tasks in logical order
- Include testing and validation steps

## Available Tools

### Content Access Tools
- `get_template` - Retrieve document templates
- `get_methodology_guide` - Access methodology guides
- `list_available_content` - List all available content
- `get_examples_and_case_studies` - Get examples and case studies

### Workflow Management Tools
- `create_workflow` - Initialize new feature workflow
- `get_workflow_status` - Check current workflow status
- `transition_phase` - Move to next phase
- `navigate_backward` - Return to previous phase
- `check_transition_requirements` - Verify phase transition requirements

### Validation Tools
- `validate_document` - Validate spec document quality
- `get_validation_checklist` - Get quality checklists
- `explain_validation_error` - Explain validation errors
- `validate_requirement_traceability` - Verify requirement traceability

## Multi-language Support

The tool supports both English and Chinese content. Use the `language` parameter in tool calls:

```json
{
  "name": "get_template",
  "arguments": {
    "template_type": "requirements",
    "language": "zh"
  }
}
```

Available languages:
- `"en"` - English (default)
- `"zh"` - Chinese (中文)

## Environment Configuration

```bash
# Server configuration
export MCP_SERVER_NAME="mcp-spec-driven-development"
export MCP_SERVER_VERSION="0.1.0"

# Logging configuration
export MCP_LOG_LEVEL="INFO"          # DEBUG, INFO, WARNING, ERROR, CRITICAL
export MCP_LOG_FORMAT="console"      # console, json
export MCP_LOG_FILE="/path/to/log"   # Optional log file path

# Performance settings
export MCP_MAX_CONTENT_SIZE="1048576"  # 1MB max content size
export MCP_CACHE_TTL="3600"            # 1 hour cache TTL

# Health monitoring
export MCP_HEALTH_CHECK_ENABLED="true"
export MCP_HEALTH_CHECK_INTERVAL="30"  # seconds
```

## Development

### Setup Development Environment
```bash
# Clone repository
git clone https://github.com/your-org/mcp-spec-driven-development.git
cd mcp-spec-driven-development

# Install development dependencies
uv sync --group dev

# Run tests
pytest tests/ -v

# Run code checks
black src/ tests/
mypy src/
```

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Run specific test categories
pytest tests/test_integration_end_to_end.py -v
pytest tests/test_performance_benchmarks.py -v

# Run coverage tests
pytest tests/ --cov=src/mcp_spec_driven_development --cov-report=html
```

## Project Structure

```
mcp-spec-driven-development/
├── src/mcp_spec_driven_development/
│   ├── __init__.py
│   ├── server.py                    # MCP server entry point
│   ├── config.py                    # Configuration management
│   ├── content/                     # Content management
│   │   ├── templates.py
│   │   ├── methodology.py
│   │   └── data/                    # Templates and methodology files
│   ├── tools/                       # MCP tool implementations
│   │   ├── content_tools.py
│   │   ├── workflow_tools.py
│   │   └── validation_tools.py
│   ├── workflow/                    # Workflow management
│   │   ├── models.py
│   │   ├── phase_manager.py
│   │   └── state_tracker.py
│   └── validation/                  # Document validation
│       ├── requirements_validator.py
│       ├── design_validator.py
│       └── task_validator.py
├── tests/                          # Test suite
├── scripts/                        # Utility scripts
└── pyproject.toml                 # Project configuration
```

## Documentation

- [Installation Guide](INSTALLATION.md) - Detailed installation and setup instructions
- [User Guide](USER_GUIDE.md) - How to use the tool with AI assistants
- [API Documentation](API.md) - Complete tool reference and examples
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions
- [Maintenance Guide](MAINTENANCE.md) - Maintenance and update procedures

## Contributing

We welcome contributions! Please see our contributing guidelines for details.

### Development Workflow
1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Ensure all tests pass
5. Submit a pull request

### Code Standards
- Use Black for code formatting
- Use MyPy for type checking
- Maintain test coverage > 90%
- Follow PEP 8 style guidelines

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📖 Check the [documentation](docs/) for detailed guides
- 🐛 Report issues on [GitHub Issues](https://github.com/your-org/mcp-spec-driven-development/issues)
- 💬 Ask questions in [Discussions](https://github.com/your-org/mcp-spec-driven-development/discussions)

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes.

---

**Note**: This tool is designed for use with AI programming assistants, providing structured feature development methodology through the MCP protocol.
