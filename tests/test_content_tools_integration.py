"""Integration tests for content access tools."""

import pytest
from mcp.types import TextContent

from src.mcp_spec_driven_development.tools.content_tools import ContentAccessTools


class TestContentAccessToolsIntegration:
    """Integration tests for content access tools."""

    @pytest.fixture
    def content_tools(self):
        """Create content access tools instance."""
        return ContentAccessTools()

    @pytest.mark.asyncio
    async def test_get_template_requirements(self, content_tools):
        """Test getting requirements template."""
        arguments = {"template_type": "requirements"}
        result = await content_tools.handle_get_template(arguments)

        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        content = result[0].text

        # Check template structure
        assert "# Requirements Document" in content
        assert "## Introduction" in content
        assert "## Requirements" in content
        assert "**User Story:**" in content
        assert "#### Acceptance Criteria" in content

    @pytest.mark.asyncio
    async def test_get_template_with_context(self, content_tools):
        """Test getting template with rendering context."""
        arguments = {
            "template_type": "requirements",
            "feature_name": "user-authentication",
            "context": {
                "introduction": "This feature enables secure user login",
                "requirements": [
                    {
                        "user_story": "As a user, I want to log in securely, so that I can access my account",
                        "acceptance_criteria": [
                            "WHEN user enters valid credentials THEN system SHALL authenticate within 2 seconds",
                            "IF credentials are invalid THEN system SHALL display error message",
                        ],
                    }
                ],
            },
        }

        result = await content_tools.handle_get_template(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check rendered content
        assert "This feature enables secure user login" in content
        assert "As a user, I want to log in securely" in content
        assert "WHEN user enters valid credentials" in content

    @pytest.mark.asyncio
    async def test_get_template_invalid_type(self, content_tools):
        """Test getting template with invalid type."""
        arguments = {"template_type": "invalid"}
        result = await content_tools.handle_get_template(arguments)

        assert len(result) == 1
        assert "Error:" in result[0].text
        assert "Invalid template type" in result[0].text

    @pytest.mark.asyncio
    async def test_get_methodology_guide_workflow(self, content_tools):
        """Test getting workflow methodology guide."""
        arguments = {"topic": "workflow"}
        result = await content_tools.handle_get_methodology_guide(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check workflow guide content
        assert "Spec-Driven Development Workflow" in content
        assert "Requirements → Design → Tasks" in content
        assert "Phase 1: Requirements" in content
        assert "Phase 2: Design" in content
        assert "Phase 3: Tasks" in content

    @pytest.mark.asyncio
    async def test_get_methodology_guide_ears_format(self, content_tools):
        """Test getting EARS format guide."""
        arguments = {"topic": "ears_format"}
        result = await content_tools.handle_get_methodology_guide(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check EARS format content
        assert "EARS Format Guide" in content
        assert "WHEN" in content
        assert "THEN" in content
        assert "SHALL" in content
        assert "Easy Approach to Requirements Syntax" in content

    @pytest.mark.asyncio
    async def test_get_methodology_guide_invalid_topic(self, content_tools):
        """Test getting methodology guide with invalid topic."""
        arguments = {"topic": "invalid_topic"}
        result = await content_tools.handle_get_methodology_guide(arguments)

        assert len(result) == 1
        assert "Error:" in result[0].text
        assert "Invalid topic" in result[0].text

    @pytest.mark.asyncio
    async def test_list_available_content_all(self, content_tools):
        """Test listing all available content."""
        arguments = {"content_type": "all"}
        result = await content_tools.handle_list_available_content(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check content categories
        assert "Templates" in content
        assert "Methodology Topics" in content
        assert "Examples Categories" in content
        assert "requirements" in content
        assert "design" in content
        assert "tasks" in content

    @pytest.mark.asyncio
    async def test_list_available_content_templates_only(self, content_tools):
        """Test listing only templates."""
        arguments = {"content_type": "templates"}
        result = await content_tools.handle_list_available_content(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check template content
        assert "Templates" in content
        assert "requirements" in content
        assert "design" in content
        assert "tasks" in content
        # Should not contain methodology topics
        assert "workflow" not in content

    @pytest.mark.asyncio
    async def test_get_examples_requirements(self, content_tools):
        """Test getting requirements examples."""
        arguments = {"category": "requirements"}
        result = await content_tools.handle_get_examples_and_case_studies(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check requirements examples content
        assert "Requirements Examples" in content
        assert "EARS Format Examples" in content
        assert "WHEN" in content
        assert "THEN" in content
        assert "SHALL" in content
        assert "User Story" in content

    @pytest.mark.asyncio
    async def test_get_examples_design(self, content_tools):
        """Test getting design examples."""
        arguments = {"category": "design"}
        result = await content_tools.handle_get_examples_and_case_studies(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check design examples content
        assert "Design Examples" in content
        assert "Architecture Diagram" in content
        assert "mermaid" in content
        assert "Component Interface" in content
        assert "Data Model" in content

    @pytest.mark.asyncio
    async def test_get_examples_tasks(self, content_tools):
        """Test getting tasks examples."""
        arguments = {"category": "tasks"}
        result = await content_tools.handle_get_examples_and_case_studies(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check tasks examples content
        assert "Tasks Examples" in content
        assert "Good Task Structure" in content
        assert "- [ ]" in content
        assert "_Requirements:" in content
        assert "Implementation Tasks" in content

    @pytest.mark.asyncio
    async def test_get_examples_pitfalls(self, content_tools):
        """Test getting pitfalls examples."""
        arguments = {"category": "pitfalls"}
        result = await content_tools.handle_get_examples_and_case_studies(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check pitfalls content
        assert "Common Pitfalls" in content
        assert "Requirements Phase Pitfalls" in content
        assert "Design Phase Pitfalls" in content
        assert "Tasks Phase Pitfalls" in content
        assert "Recovery Strategies" in content

    @pytest.mark.asyncio
    async def test_get_examples_complete_specs(self, content_tools):
        """Test getting complete specification examples."""
        arguments = {"category": "complete_specs"}
        result = await content_tools.handle_get_examples_and_case_studies(arguments)

        assert len(result) == 1
        content = result[0].text

        # Check complete spec content
        assert "Complete Specification Examples" in content
        assert "User Authentication Feature" in content
        assert "Requirements Document" in content
        assert "Design Document" in content
        assert "Implementation Plan" in content

    @pytest.mark.asyncio
    async def test_get_examples_invalid_category(self, content_tools):
        """Test getting examples with invalid category."""
        arguments = {"category": "invalid_category"}
        result = await content_tools.handle_get_examples_and_case_studies(arguments)

        assert len(result) == 1
        assert "Error:" in result[0].text
        assert "Invalid category" in result[0].text

    @pytest.mark.asyncio
    async def test_get_examples_with_specific_topic(self, content_tools):
        """Test getting examples with specific topic filter."""
        arguments = {"category": "requirements", "specific_topic": "EARS"}
        result = await content_tools.handle_get_examples_and_case_studies(arguments)

        assert len(result) == 1
        content = result[0].text

        # Should contain EARS-related content
        assert "EARS" in content or "ears" in content.lower()

    @pytest.mark.asyncio
    async def test_get_examples_topic_not_found(self, content_tools):
        """Test getting examples with topic not found."""
        arguments = {"category": "requirements", "specific_topic": "nonexistent_topic"}
        result = await content_tools.handle_get_examples_and_case_studies(arguments)

        assert len(result) == 1
        assert "No examples found" in result[0].text

    def test_tool_definitions(self, content_tools):
        """Test that tool definitions are properly structured."""
        tools = content_tools.get_tool_definitions()

        assert len(tools) == 4

        tool_names = [tool.name for tool in tools]
        expected_names = [
            "get_template",
            "get_methodology_guide",
            "list_available_content",
            "get_examples_and_case_studies",
        ]

        for name in expected_names:
            assert name in tool_names

        # Check that all tools have required properties
        for tool in tools:
            assert tool.name
            assert tool.description
            assert tool.inputSchema
            assert "type" in tool.inputSchema
            assert "properties" in tool.inputSchema
            assert "required" in tool.inputSchema

    @pytest.mark.asyncio
    async def test_handle_unknown_tool(self, content_tools):
        """Test handling unknown tool call."""
        result = await content_tools.handle_tool_call("unknown_tool", {})

        assert len(result) == 1
        assert "Unknown tool" in result[0].text
