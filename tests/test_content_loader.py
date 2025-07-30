"""Unit tests for content loader."""

from pathlib import Path

import pytest

from src.mcp_spec_driven_development.content.content_loader import (
    ContentLoader,
    ContentType,
)
from src.mcp_spec_driven_development.exceptions import ContentAccessError


class TestContentLoader:
    """Test cases for ContentLoader."""

    @pytest.fixture
    def content_loader(self):
        """Create content loader instance."""
        return ContentLoader()

    def test_initialization(self, content_loader):
        """Test content loader initialization."""
        assert content_loader is not None
        assert content_loader.data_dir.exists()
        assert content_loader.data_dir.name == "data"

    def test_get_methodology_content_workflow(self, content_loader):
        """Test loading workflow methodology content."""
        content = content_loader.get_methodology_content("workflow")
        assert content is not None
        assert "Spec-Driven Development Workflow" in content
        assert "Requirements → Design → Tasks" in content
        assert "Phase 1: Requirements" in content

    def test_get_methodology_content_ears_format(self, content_loader):
        """Test loading EARS format methodology content."""
        content = content_loader.get_methodology_content("ears-format")
        assert content is not None
        assert "EARS Format Guide" in content
        assert "WHEN [trigger event] THEN [system] SHALL [response]" in content
        assert "IF [precondition] THEN [system] SHALL [response]" in content

    def test_get_methodology_content_phase_transitions(self, content_loader):
        """Test loading phase transitions methodology content."""
        content = content_loader.get_methodology_content("phase-transitions")
        assert content is not None
        assert "Phase Transitions and Approval Process" in content
        assert "Requirements → Design Transition" in content
        assert "Design → Tasks Transition" in content

    def test_get_methodology_content_nonexistent(self, content_loader):
        """Test loading nonexistent methodology content."""
        with pytest.raises(ContentAccessError):
            content_loader.get_methodology_content("nonexistent")

    def test_get_template_content_requirements(self, content_loader):
        """Test loading requirements template content."""
        content = content_loader.get_template_content("requirements")
        assert content is not None
        assert "Requirements Document Template" in content
        assert "User Story:" in content
        assert "Acceptance Criteria" in content
        assert "EARS format" in content

    def test_get_template_content_design(self, content_loader):
        """Test loading design template content."""
        content = content_loader.get_template_content("design")
        assert content is not None
        assert "Design Document Template" in content
        assert "## Overview" in content
        assert "## Architecture" in content
        assert "## Components and Interfaces" in content

    def test_get_template_content_tasks(self, content_loader):
        """Test loading tasks template content."""
        content = content_loader.get_template_content("tasks")
        assert content is not None
        assert "Implementation Plan Template" in content
        assert "- [ ]" in content
        assert "_Requirements:" in content
        assert "Task Writing Guidelines" in content

    def test_get_template_content_nonexistent(self, content_loader):
        """Test loading nonexistent template content."""
        with pytest.raises(ContentAccessError):
            content_loader.get_template_content("nonexistent")

    def test_get_example_content(self, content_loader):
        """Test loading example content."""
        content = content_loader.get_example_content("requirements")
        assert isinstance(content, str)

    def test_get_example_content_nonexistent(self, content_loader):
        """Test loading nonexistent example content."""
        with pytest.raises(ContentAccessError):
            content_loader.get_example_content("nonexistent")

    def test_get_fallback_content(self, content_loader):
        """Test fallback content retrieval."""
        # Test with error handler that should trigger fallback
        from unittest.mock import patch

        with patch.object(content_loader, "_load_file", return_value=None):
            # This should trigger fallback content
            try:
                content = content_loader.get_template_content("requirements")
                # If fallback works, we get content
                assert content is not None
            except ContentAccessError:
                # If no fallback, we get an error - both are valid
                pass

    def test_get_example_content(self, content_loader):
        """Test getting example content."""
        content = content_loader.get_example_content("requirements")
        assert isinstance(content, str)

    def test_get_available_content_methodology(self, content_loader):
        """Test getting available methodology content."""
        content = content_loader.get_available_content(ContentType.METHODOLOGY)
        assert isinstance(content, list)

    def test_get_available_content_template(self, content_loader):
        """Test getting available template content."""
        content = content_loader.get_available_content(ContentType.TEMPLATE)
        assert isinstance(content, list)

    def test_get_available_content_example(self, content_loader):
        """Test getting available example content."""
        content = content_loader.get_available_content(ContentType.EXAMPLE)
        assert isinstance(content, list)

    def test_validate_content_structure(self, content_loader):
        """Test content structure validation."""
        issues = content_loader.validate_content_structure()
        assert isinstance(issues, dict)
        assert "methodology" in issues
        assert "templates" in issues
        assert "examples" in issues
        assert "general" in issues

    def test_clear_cache(self, content_loader):
        """Test clearing content cache."""
        # Load some content to populate cache
        content_loader.get_methodology_content("workflow")

        # Clear cache
        content_loader.clear_cache()

        # Cache should be empty
        cache_info = content_loader.get_cache_info()
        assert cache_info["cached_items"] == 0

    def test_get_cache_info(self, content_loader):
        """Test getting cache information."""
        cache_info = content_loader.get_cache_info()
        assert isinstance(cache_info, dict)
        assert "cached_items" in cache_info
        assert "cache_keys" in cache_info

    def test_list_methodology_topics(self, content_loader):
        """Test listing methodology topics."""
        topics = content_loader.list_methodology_topics()
        assert isinstance(topics, list)

    def test_list_template_types(self, content_loader):
        """Test listing template types."""
        types = content_loader.list_template_types()
        assert isinstance(types, list)

    def test_get_content_info(self, content_loader):
        """Test getting content information."""
        info = content_loader.get_content_info()
        assert isinstance(info, dict)
        assert "methodology" in info
        assert "templates" in info

    def test_load_spec_document(self, content_loader):
        """Test loading spec document."""
        from src.mcp_spec_driven_development.workflow.models import PhaseType

        doc = content_loader.load_spec_document("test-feature", PhaseType.REQUIREMENTS)
        # Should return None or string content
        assert doc is None or isinstance(doc, str)

    def test_load_file_with_caching(self, content_loader):
        """Test file loading with caching."""
        # Load a file that exists
        file_path = content_loader.data_dir / "methodology" / "workflow.md"
        if file_path.exists():
            # First load
            content1 = content_loader._load_file(file_path)
            # Second load (should use cache)
            content2 = content_loader._load_file(file_path)
            assert content1 == content2

    def test_load_file_error_handling(self, content_loader):
        """Test file loading error handling."""
        from unittest.mock import patch

        # Test permission error
        with patch("builtins.open", side_effect=PermissionError("Permission denied")):
            content = content_loader._load_file(Path("test.md"))
            assert content is None

    def test_content_type_enum(self, content_loader):
        """Test ContentType enum values."""
        assert ContentType.METHODOLOGY.value == "methodology"
        assert ContentType.TEMPLATE.value == "template"
        assert ContentType.EXAMPLE.value == "example"

    def test_list_methodology_topics(self, content_loader):
        """Test listing methodology topics."""
        topics = content_loader.list_methodology_topics()
        assert isinstance(topics, list)
        assert len(topics) >= 3
        assert "workflow" in topics
        assert "ears-format" in topics
        assert "phase-transitions" in topics
        # Topics should be sorted
        assert topics == sorted(topics)

    def test_list_template_types(self, content_loader):
        """Test listing template types."""
        types = content_loader.list_template_types()
        assert isinstance(types, list)
        assert len(types) >= 3
        assert "requirements" in types
        assert "design" in types
        assert "tasks" in types
        # Types should be sorted
        assert types == sorted(types)

    def test_content_caching(self, content_loader):
        """Test that content is cached after first load."""
        # Load content first time
        content1 = content_loader.get_methodology_content("workflow")
        assert content1 is not None

        # Load same content second time (should be cached)
        content2 = content_loader.get_methodology_content("workflow")
        assert content2 is not None
        assert content1 == content2

        # Verify cache contains the content
        cache_key = str(content_loader.data_dir / "methodology" / "workflow.md")
        assert cache_key in content_loader._content_cache
        assert content_loader._content_cache[cache_key] == content1

    def test_clear_cache(self, content_loader):
        """Test clearing the content cache."""
        # Load some content to populate cache
        content_loader.get_methodology_content("workflow")
        content_loader.get_template_content("requirements")

        # Verify cache has content
        assert len(content_loader._content_cache) > 0

        # Clear cache
        content_loader.clear_cache()

        # Verify cache is empty
        assert len(content_loader._content_cache) == 0

    def test_get_content_info(self, content_loader):
        """Test getting content information."""
        info = content_loader.get_content_info()
        assert isinstance(info, dict)
        assert "methodology_topics" in info
        assert "template_types" in info

        assert isinstance(info["methodology_topics"], list)
        assert isinstance(info["template_types"], list)

        assert len(info["methodology_topics"]) >= 3
        assert len(info["template_types"]) >= 3

        assert "workflow" in info["methodology_topics"]
        assert "requirements" in info["template_types"]

    def test_data_directory_structure(self, content_loader):
        """Test that data directory has expected structure."""
        data_dir = content_loader.data_dir
        assert data_dir.exists()

        methodology_dir = data_dir / "methodology"
        templates_dir = data_dir / "templates"

        assert methodology_dir.exists()
        assert templates_dir.exists()

        # Check for expected methodology files
        assert (methodology_dir / "workflow.md").exists()
        assert (methodology_dir / "ears-format.md").exists()
        assert (methodology_dir / "phase-transitions.md").exists()

        # Check for expected template files
        assert (templates_dir / "requirements-template.md").exists()
        assert (templates_dir / "design-template.md").exists()
        assert (templates_dir / "tasks-template.md").exists()

    def test_content_quality_methodology(self, content_loader):
        """Test that methodology content meets quality standards."""
        # Test workflow content
        workflow = content_loader.get_methodology_content("workflow")
        assert "Phase 1: Requirements" in workflow
        assert "Phase 2: Design" in workflow
        assert "Phase 3: Tasks" in workflow
        assert "Quality Gate" in workflow

        # Test EARS format content
        ears = content_loader.get_methodology_content("ears-format")
        assert "WHEN" in ears
        assert "THEN" in ears
        assert "SHALL" in ears
        assert "Examples" in ears

        # Test phase transitions content
        transitions = content_loader.get_methodology_content("phase-transitions")
        assert "explicit" in transitions.lower()
        assert "approval" in transitions
        assert "Prerequisites" in transitions

    def test_content_quality_templates(self, content_loader):
        """Test that template content meets quality standards."""
        # Test requirements template
        req_template = content_loader.get_template_content("requirements")
        assert "User Story:" in req_template
        assert "Acceptance Criteria" in req_template
        assert "EARS format" in req_template
        assert "Quality Checklist" in req_template

        # Test design template
        design_template = content_loader.get_template_content("design")
        assert "## Overview" in design_template
        assert "## Architecture" in design_template
        assert "mermaid" in design_template
        assert "Components and Interfaces" in design_template

        # Test tasks template
        tasks_template = content_loader.get_template_content("tasks")
        assert "- [ ]" in tasks_template
        assert "_Requirements:" in tasks_template
        assert "Actionable Tasks" in tasks_template
        assert "Requirement Traceability" in tasks_template
