"""规范驱动开发工具的主要MCP服务器入口点。"""

import asyncio
import logging
from typing import Any

import structlog
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .config import ServerConfig, setup_logging
from .tools.content_tools import ContentAccessTools
from .tools.validation_tools import ValidationTools
from .tools.workflow_tools import WorkflowManagementTools

# 设置结构化日志
config = ServerConfig.from_env()
setup_logging(config.log_level, config.log_format, config.log_file)
logger = structlog.get_logger(__name__)

# 初始化MCP服务器
server: Server = Server("mcp-spec-driven-development")

# 初始化工具处理器
content_tools = ContentAccessTools()
workflow_tools = WorkflowManagementTools()
validation_tools = ValidationTools()


@server.list_tools()  # type: ignore
async def handle_list_tools() -> list[Tool]:
    """列出规范驱动开发的可用MCP工具。"""
    logger.debug("正在列出可用工具")
    tools = []

    # 添加内容访问工具
    tools.extend(content_tools.get_tool_definitions())

    # 添加工作流管理工具
    tools.extend(workflow_tools.get_tool_definitions())

    # 添加验证工具
    tools.extend(validation_tools.get_tool_definitions())

    logger.info("已列出工具", tool_count=len(tools))
    return tools


@server.call_tool()  # type: ignore
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[TextContent]:
    """处理MCP工具调用。"""
    if arguments is None:
        arguments = {}

    logger.debug("正在处理工具调用", tool_name=name, arguments=arguments)

    try:
        # 路由到适当的工具处理器
        content_tool_names = {
            "get_template",
            "get_methodology_guide",
            "list_available_content",
            "get_examples_and_case_studies",
        }

        workflow_tool_names = {
            "create_workflow",
            "get_workflow_status",
            "transition_phase",
            "navigate_backward",
            "check_transition_requirements",
            "get_approval_guidance",
        }

        validation_tool_names = {
            "validate_document",
            "get_validation_checklist",
            "explain_validation_error",
            "validate_requirement_traceability",
        }

        if name in content_tool_names:
            result = await content_tools.handle_tool_call(name, arguments)
        elif name in workflow_tool_names:
            result = await workflow_tools.handle_tool_call(name, arguments)
        elif name in validation_tool_names:
            result = await validation_tools.handle_tool_call(name, arguments)
        else:
            raise ValueError(f"未知工具: {name}")

        logger.info("工具调用完成", tool_name=name, success=True)
        return result

    except Exception as e:
        logger.error("工具调用失败", tool_name=name, error=str(e), exc_info=True)
        return [TextContent(type="text", text=f"错误: {str(e)}")]


async def async_main() -> None:
    """MCP服务器的异步主入口点。"""
    logger.info("正在启动MCP服务器", server_name=config.name, version=config.version)

    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=config.name,
                    server_version=config.version,
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except Exception as e:
        logger.error("服务器启动失败", error=str(e), exc_info=True)
        raise


def main() -> None:
    """MCP服务器的同步入口点。"""
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
