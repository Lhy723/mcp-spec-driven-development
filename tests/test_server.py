"""Tests for the MCP server functionality."""

from unittest.mock import AsyncMock, patch

import pytest
from mcp.types import TextContent

from mcp_spec_driven_development.server import (
    content_tools,
    handle_call_tool,
    handle_list_tools,
    server,
    validation_tools,
    workflow_tools,
)


@pytest.mark.asyncio
async def test_handle_list_tools():
    """Test that all tools are properly listed."""
    tools = await handle_list_tools()

    # Should have tools from all three categories
    assert len(tools) > 0

    # Check that we have tools from each category
    tool_names = [tool.name for tool in tools]

    # Content tools
    assert "get_template" in tool_names
    assert "get_methodology_guide" in tool_names

    # Workflow tools
    assert "create_workflow" in tool_names
    assert "get_workflow_status" in tool_names

    # Validation tools
    assert "validate_document" in tool_names


@pytest.mark.asyncio
async def test_handle_call_tool_content():
    """Test content tool routing."""
    with patch.object(
        content_tools, "handle_tool_call", new_callable=AsyncMock
    ) as mock_handler:
        mock_handler.return_value = [TextContent(type="text", text="test result")]

        result = await handle_call_tool(
            "get_template", {"template_type": "requirements"}
        )

        mock_handler.assert_called_once_with(
            "get_template", {"template_type": "requirements"}
        )
        assert len(result) == 1
        assert result[0].text == "test result"


@pytest.mark.asyncio
async def test_handle_call_tool_workflow():
    """Test workflow tool routing."""
    with patch.object(
        workflow_tools, "handle_tool_call", new_callable=AsyncMock
    ) as mock_handler:
        mock_handler.return_value = [TextContent(type="text", text="workflow result")]

        result = await handle_call_tool("create_workflow", {"feature_name": "test"})

        mock_handler.assert_called_once_with(
            "create_workflow", {"feature_name": "test"}
        )
        assert len(result) == 1
        assert result[0].text == "workflow result"


@pytest.mark.asyncio
async def test_handle_call_tool_validation():
    """Test validation tool routing."""
    with patch.object(
        validation_tools, "handle_tool_call", new_callable=AsyncMock
    ) as mock_handler:
        mock_handler.return_value = [TextContent(type="text", text="validation result")]

        result = await handle_call_tool(
            "validate_document", {"document_type": "requirements"}
        )

        mock_handler.assert_called_once_with(
            "validate_document", {"document_type": "requirements"}
        )
        assert len(result) == 1
        assert result[0].text == "validation result"


@pytest.mark.asyncio
async def test_handle_call_tool_unknown():
    """Test handling of unknown tool calls."""
    result = await handle_call_tool("unknown_tool", {})

    assert len(result) == 1
    assert "Error: Unknown tool: unknown_tool" in result[0].text


@pytest.mark.asyncio
async def test_handle_call_tool_no_arguments():
    """Test tool calls with no arguments."""
    with patch.object(
        content_tools, "handle_tool_call", new_callable=AsyncMock
    ) as mock_handler:
        mock_handler.return_value = [TextContent(type="text", text="no args result")]

        result = await handle_call_tool("get_template", None)

        mock_handler.assert_called_once_with("get_template", {})
        assert len(result) == 1
        assert result[0].text == "no args result"


@pytest.mark.asyncio
async def test_handle_call_tool_exception():
    """Test error handling in tool calls."""
    with patch.object(
        content_tools, "handle_tool_call", new_callable=AsyncMock
    ) as mock_handler:
        mock_handler.side_effect = Exception("Test error")

        result = await handle_call_tool("get_template", {})

        assert len(result) == 1
        assert "Error: Test error" in result[0].text


def test_server_initialization():
    """Test that the server is properly initialized."""
    assert server.name == "mcp-spec-driven-development"
    assert content_tools is not None
    assert workflow_tools is not None
    assert validation_tools is not None
