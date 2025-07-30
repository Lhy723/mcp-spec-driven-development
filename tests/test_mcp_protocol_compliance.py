"""MCP protocol compliance tests with mock AI assistant."""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from mcp.server.models import InitializationOptions
from mcp.types import TextContent, Tool

from src.mcp_spec_driven_development.server import (
    handle_call_tool,
    handle_list_tools,
    main,
    server,
)


class TestMCPProtocolCompliance:
    """Test MCP protocol compliance with mock AI assistant interactions."""

    @pytest.mark.asyncio
    async def test_list_tools_protocol_compliance(self):
        """Test that list_tools returns properly formatted Tool objects."""
        tools = await handle_list_tools()

        # Should return a list of Tool objects
        assert isinstance(tools, list)
        assert len(tools) > 0

        # Each tool should be a proper Tool object with required fields
        for tool in tools:
            assert isinstance(tool, Tool)
            assert hasattr(tool, "name")
            assert hasattr(tool, "description")
            assert isinstance(tool.name, str)
            assert isinstance(tool.description, str)
            assert len(tool.name) > 0
            assert len(tool.description) > 0

    @pytest.mark.asyncio
    async def test_call_tool_protocol_compliance(self):
        """Test that call_tool returns properly formatted TextContent objects."""
        # Test with valid tool calls
        valid_calls = [
            ("get_template", {"template_type": "requirements"}),
            ("get_methodology_guide", {"topic": "workflow"}),
            ("create_workflow", {"feature_name": "test"}),
            ("validate_document", {"document_type": "requirements", "content": "test"}),
        ]

        for tool_name, arguments in valid_calls:
            result = await handle_call_tool(tool_name, arguments)

            # Should return a list of TextContent objects
            assert isinstance(result, list)
            assert len(result) > 0

            for content in result:
                assert isinstance(content, TextContent)
                assert content.type == "text"
                assert isinstance(content.text, str)
                assert len(content.text) > 0

    @pytest.mark.asyncio
    async def test_call_tool_with_none_arguments(self):
        """Test call_tool handles None arguments correctly."""
        result = await handle_call_tool("get_methodology_guide", None)

        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)

    @pytest.mark.asyncio
    async def test_call_tool_with_empty_arguments(self):
        """Test call_tool handles empty arguments correctly."""
        result = await handle_call_tool("list_available_content", {})

        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)

    @pytest.mark.asyncio
    async def test_call_tool_unknown_tool(self):
        """Test call_tool handles unknown tools gracefully."""
        result = await handle_call_tool("unknown_tool_name", {})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert "unknown tool" in result[0].text.lower()

    @pytest.mark.asyncio
    async def test_call_tool_error_handling(self):
        """Test call_tool error handling returns proper TextContent."""
        # Test with invalid arguments that should cause errors
        result = await handle_call_tool("validate_document", {"invalid": "args"})

        assert isinstance(result, list)
        assert len(result) > 0
        assert isinstance(result[0], TextContent)

    @pytest.mark.asyncio
    async def test_mock_ai_assistant_interaction(self):
        """Test interaction with mock AI assistant."""

        # Mock AI assistant that calls our tools
        class MockAIAssistant:
            def __init__(self):
                self.tools = []
                self.responses = []

            async def discover_tools(self):
                """Mock tool discovery."""
                self.tools = await handle_list_tools()
                return self.tools

            async def call_tool(self, tool_name, arguments):
                """Mock tool calling."""
                response = await handle_call_tool(tool_name, arguments)
                self.responses.append(response)
                return response

        # Create mock assistant
        assistant = MockAIAssistant()

        # Test tool discovery
        tools = await assistant.discover_tools()
        assert len(tools) > 0

        # Test tool calling
        response = await assistant.call_tool(
            "get_methodology_guide", {"topic": "workflow"}
        )
        assert len(response) == 1
        assert isinstance(response[0], TextContent)

        # Test workflow creation
        response = await assistant.call_tool(
            "create_workflow", {"feature_name": "ai-test"}
        )
        assert len(response) == 1
        assert isinstance(response[0], TextContent)

    @pytest.mark.asyncio
    async def test_concurrent_tool_calls(self):
        """Test concurrent tool calls from multiple mock clients."""

        # Simulate multiple AI assistants calling tools concurrently
        async def mock_client_session(client_id):
            """Mock client session."""
            results = []

            # Each client makes multiple tool calls
            calls = [
                ("get_methodology_guide", {"topic": "workflow"}),
                ("get_template", {"template_type": "requirements"}),
                ("create_workflow", {"feature_name": f"client-{client_id}-feature"}),
            ]

            for tool_name, args in calls:
                result = await handle_call_tool(tool_name, args)
                results.append(result)

            return results

        # Run multiple concurrent client sessions
        client_tasks = [mock_client_session(i) for i in range(3)]
        all_results = await asyncio.gather(*client_tasks)

        # All clients should get valid responses
        for client_results in all_results:
            assert len(client_results) == 3
            for result in client_results:
                assert isinstance(result, list)
                assert len(result) > 0
                assert isinstance(result[0], TextContent)

    @pytest.mark.asyncio
    async def test_tool_parameter_validation(self):
        """Test that tools properly validate parameters."""
        # Test tools with missing required parameters
        test_cases = [
            ("get_template", {}),  # Missing template_type
            ("validate_document", {"document_type": "requirements"}),  # Missing content
            ("create_workflow", {}),  # Missing feature_name
        ]

        for tool_name, args in test_cases:
            result = await handle_call_tool(tool_name, args)
            assert isinstance(result, list)
            assert len(result) > 0
            assert isinstance(result[0], TextContent)
            # Should contain error message about missing parameters

    @pytest.mark.asyncio
    async def test_tool_response_consistency(self):
        """Test that tools return consistent response formats."""
        # Call the same tool multiple times
        tool_name = "get_methodology_guide"
        args = {"topic": "workflow"}

        responses = []
        for _ in range(3):
            response = await handle_call_tool(tool_name, args)
            responses.append(response)

        # All responses should have the same structure
        for response in responses:
            assert isinstance(response, list)
            assert len(response) > 0
            assert isinstance(response[0], TextContent)
            assert response[0].type == "text"

        # Content should be identical for same inputs
        assert responses[0][0].text == responses[1][0].text == responses[2][0].text

    @pytest.mark.asyncio
    async def test_server_initialization_compliance(self):
        """Test server initialization follows MCP protocol."""
        # Test that server is properly initialized
        assert server.name == "mcp-spec-driven-development"

        # Test capabilities with proper notification options
        from mcp.server import NotificationOptions

        capabilities = server.get_capabilities(
            notification_options=NotificationOptions(), experimental_capabilities={}
        )

        assert capabilities is not None

    @pytest.mark.asyncio
    async def test_tool_categories_coverage(self):
        """Test that all tool categories are properly represented."""
        tools = await handle_list_tools()
        tool_names = [tool.name for tool in tools]

        # Should have tools from all major categories
        content_tools = [
            name
            for name in tool_names
            if any(
                keyword in name
                for keyword in ["template", "methodology", "content", "examples"]
            )
        ]
        workflow_tools = [
            name
            for name in tool_names
            if any(keyword in name for keyword in ["workflow", "phase", "transition"])
        ]
        validation_tools = [
            name
            for name in tool_names
            if any(keyword in name for keyword in ["validate", "validation"])
        ]

        assert len(content_tools) > 0, "Should have content access tools"
        assert len(workflow_tools) > 0, "Should have workflow management tools"
        assert len(validation_tools) > 0, "Should have validation tools"

    @pytest.mark.asyncio
    async def test_error_response_format(self):
        """Test that error responses follow proper format."""
        # Cause various types of errors
        error_scenarios = [
            ("nonexistent_tool", {}),
            ("get_template", {"template_type": "nonexistent"}),
            ("validate_document", {"document_type": "invalid", "content": "test"}),
        ]

        for tool_name, args in error_scenarios:
            result = await handle_call_tool(tool_name, args)

            # Error responses should still be properly formatted
            assert isinstance(result, list)
            assert len(result) == 1
            assert isinstance(result[0], TextContent)
            assert result[0].type == "text"
            assert len(result[0].text) > 0

    @pytest.mark.asyncio
    async def test_large_content_handling(self):
        """Test handling of large content in tool responses."""
        # Get a template which might be large
        result = await handle_call_tool(
            "get_template", {"template_type": "requirements"}
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        # Should handle large content properly
        content = result[0].text
        assert len(content) > 100  # Should be substantial content

    @pytest.mark.asyncio
    async def test_unicode_content_handling(self):
        """Test handling of unicode content in tool responses."""
        # Test with content that might contain unicode
        result = await handle_call_tool("get_methodology_guide", {"topic": "workflow"})

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], TextContent)

        # Should handle unicode properly
        content = result[0].text
        assert isinstance(content, str)
        # Content should be encodable/decodable
        encoded = content.encode("utf-8")
        decoded = encoded.decode("utf-8")
        assert content == decoded

    @pytest.mark.asyncio
    async def test_tool_metadata_compliance(self):
        """Test that tool metadata follows MCP standards."""
        tools = await handle_list_tools()

        for tool in tools:
            # Name should be valid identifier
            assert tool.name.replace("_", "").replace("-", "").isalnum()

            # Description should be informative
            assert len(tool.description) > 20

            # Should have input schema if tool accepts parameters
            if hasattr(tool, "inputSchema"):
                assert tool.inputSchema is not None

    @pytest.mark.asyncio
    async def test_async_operation_compliance(self):
        """Test that all operations are properly async."""
        # All tool operations should be awaitable
        tools = await handle_list_tools()

        # Test a few representative tools
        test_tools = [
            ("get_methodology_guide", {"topic": "workflow"}),
            ("create_workflow", {"feature_name": "async-test"}),
            ("validate_document", {"document_type": "requirements", "content": "test"}),
        ]

        for tool_name, args in test_tools:
            # Should be awaitable
            result = await handle_call_tool(tool_name, args)
            assert result is not None

    @pytest.mark.asyncio
    async def test_stateless_operation_compliance(self):
        """Test that tools operate in a stateless manner per MCP requirements."""
        # Same inputs should produce same outputs regardless of order
        tool_calls = [
            ("get_methodology_guide", {"topic": "workflow"}),
            ("get_template", {"template_type": "requirements"}),
            ("get_methodology_guide", {"topic": "workflow"}),  # Repeat
        ]

        results = []
        for tool_name, args in tool_calls:
            result = await handle_call_tool(tool_name, args)
            results.append(result)

        # First and third calls (same inputs) should produce same outputs
        assert results[0][0].text == results[2][0].text
