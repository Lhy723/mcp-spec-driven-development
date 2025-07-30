"""Unit tests for methodology guides access system."""

import pytest

from src.mcp_spec_driven_development.content.methodology import (
    MethodologyGuide,
    MethodologyGuides,
    MethodologyTopic,
)


class TestMethodologyGuides:
    """Test cases for MethodologyGuides."""

    @pytest.fixture
    def methodology_guides(self):
        """Create methodology guides instance."""
        return MethodologyGuides()

    def test_initialization(self, methodology_guides):
        """Test methodology guides initialization."""
        assert methodology_guides is not None
        assert len(methodology_guides._guides) == 8

        # Check all expected topics are present
        expected_topics = [
            MethodologyTopic.WORKFLOW,
            MethodologyTopic.REQUIREMENTS,
            MethodologyTopic.DESIGN,
            MethodologyTopic.TASKS,
            MethodologyTopic.EARS_FORMAT,
            MethodologyTopic.PHASE_TRANSITIONS,
            MethodologyTopic.BEST_PRACTICES,
            MethodologyTopic.TROUBLESHOOTING,
        ]

        for topic in expected_topics:
            assert topic in methodology_guides._guides

    def test_get_guide_workflow(self, methodology_guides):
        """Test getting workflow guide."""
        guide = methodology_guides.get_guide(MethodologyTopic.WORKFLOW)
        assert guide is not None
        assert guide.topic == MethodologyTopic.WORKFLOW
        assert "Spec-Driven Development Workflow" in guide.title
        assert "Requirements → Design → Tasks" in guide.content
        assert "Phase 1: Requirements" in guide.content
        assert "Phase 2: Design" in guide.content
        assert "Phase 3: Tasks" in guide.content

    def test_get_guide_requirements(self, methodology_guides):
        """Test getting requirements guide."""
        guide = methodology_guides.get_guide(MethodologyTopic.REQUIREMENTS)
        assert guide is not None
        assert guide.topic == MethodologyTopic.REQUIREMENTS
        assert "Requirements Phase Guide" in guide.title
        assert "EARS Format" in guide.content
        assert "User Story Format" in guide.content
        assert "As a [role], I want [feature], so that [benefit]" in guide.content

    def test_get_guide_design(self, methodology_guides):
        """Test getting design guide."""
        guide = methodology_guides.get_guide(MethodologyTopic.DESIGN)
        assert guide is not None
        assert guide.topic == MethodologyTopic.DESIGN
        assert "Design Phase Guide" in guide.title
        assert "Required Sections" in guide.content
        assert "Overview" in guide.content
        assert "Architecture" in guide.content
        assert "Components and Interfaces" in guide.content

    def test_get_guide_tasks(self, methodology_guides):
        """Test getting tasks guide."""
        guide = methodology_guides.get_guide(MethodologyTopic.TASKS)
        assert guide is not None
        assert guide.topic == MethodologyTopic.TASKS
        assert "Tasks Phase Guide" in guide.title
        assert "Task Structure" in guide.content
        assert "Requirement Traceability" in guide.content
        assert "_Requirements: X.X, Y.Y_" in guide.content

    def test_get_guide_ears_format(self, methodology_guides):
        """Test getting EARS format guide."""
        guide = methodology_guides.get_guide(MethodologyTopic.EARS_FORMAT)
        assert guide is not None
        assert guide.topic == MethodologyTopic.EARS_FORMAT
        assert "EARS Format Guide" in guide.title
        assert "WHEN [trigger event] THEN [system] SHALL [response]" in guide.content
        assert "IF [precondition] THEN [system] SHALL [response]" in guide.content

    def test_get_guide_phase_transitions(self, methodology_guides):
        """Test getting phase transitions guide."""
        guide = methodology_guides.get_guide(MethodologyTopic.PHASE_TRANSITIONS)
        assert guide is not None
        assert guide.topic == MethodologyTopic.PHASE_TRANSITIONS
        assert "Phase Transitions Guide" in guide.title
        assert "Requirements → Design" in guide.content
        assert "Design → Tasks" in guide.content
        assert "Explicit user approval" in guide.content

    def test_get_guide_best_practices(self, methodology_guides):
        """Test getting best practices guide."""
        guide = methodology_guides.get_guide(MethodologyTopic.BEST_PRACTICES)
        assert guide is not None
        assert guide.topic == MethodologyTopic.BEST_PRACTICES
        assert "Best Practices Guide" in guide.title
        assert "User-Centered Approach" in guide.content
        assert "Quality Over Speed" in guide.content
        assert "Systematic Progression" in guide.content

    def test_get_guide_troubleshooting(self, methodology_guides):
        """Test getting troubleshooting guide."""
        guide = methodology_guides.get_guide(MethodologyTopic.TROUBLESHOOTING)
        assert guide is not None
        assert guide.topic == MethodologyTopic.TROUBLESHOOTING
        assert "Troubleshooting Guide" in guide.title
        assert "Common Problems and Solutions" in guide.content
        assert "Requirements Phase Issues" in guide.content
        assert "Design Phase Issues" in guide.content
        assert "Tasks Phase Issues" in guide.content

    def test_get_guide_content(self, methodology_guides):
        """Test getting guide content as string."""
        content = methodology_guides.get_guide_content(MethodologyTopic.WORKFLOW)
        assert "Spec-Driven Development Workflow" in content
        assert "Requirements → Design → Tasks" in content

    def test_get_guide_content_invalid(self, methodology_guides):
        """Test getting content for invalid topic."""
        # Create a mock invalid topic
        from unittest.mock import Mock

        invalid_topic = Mock()
        invalid_topic.value = "invalid_topic"

        content = methodology_guides.get_guide_content(invalid_topic)
        assert "Guide not found for topic: invalid_topic" in content

    def test_get_all_topics(self, methodology_guides):
        """Test getting all available topics."""
        topics = methodology_guides.get_all_topics()
        assert len(topics) == 8
        assert MethodologyTopic.WORKFLOW in topics
        assert MethodologyTopic.REQUIREMENTS in topics
        assert MethodologyTopic.DESIGN in topics
        assert MethodologyTopic.TASKS in topics
        assert MethodologyTopic.EARS_FORMAT in topics
        assert MethodologyTopic.PHASE_TRANSITIONS in topics
        assert MethodologyTopic.BEST_PRACTICES in topics
        assert MethodologyTopic.TROUBLESHOOTING in topics

    def test_search_guides_by_title(self, methodology_guides):
        """Test searching guides by title."""
        results = methodology_guides.search_guides("workflow")
        assert len(results) >= 1
        assert any("Workflow" in guide.title for guide in results)

    def test_search_guides_by_content(self, methodology_guides):
        """Test searching guides by content."""
        results = methodology_guides.search_guides("EARS format")
        assert len(results) >= 1
        assert any("EARS" in guide.content for guide in results)

    def test_search_guides_case_insensitive(self, methodology_guides):
        """Test case-insensitive search."""
        results_lower = methodology_guides.search_guides("requirements")
        results_upper = methodology_guides.search_guides("REQUIREMENTS")
        results_mixed = methodology_guides.search_guides("Requirements")

        assert len(results_lower) == len(results_upper) == len(results_mixed)
        assert len(results_lower) >= 1

    def test_search_guides_no_results(self, methodology_guides):
        """Test search with no matching results."""
        results = methodology_guides.search_guides("nonexistent_term_xyz")
        assert len(results) == 0

    def test_get_related_guides(self, methodology_guides):
        """Test getting related guides."""
        related = methodology_guides.get_related_guides(MethodologyTopic.WORKFLOW)
        assert len(related) > 0

        # Workflow should be related to requirements, design, tasks, and phase transitions
        related_topics = [guide.topic for guide in related]
        assert MethodologyTopic.REQUIREMENTS in related_topics
        assert MethodologyTopic.DESIGN in related_topics
        assert MethodologyTopic.TASKS in related_topics
        assert MethodologyTopic.PHASE_TRANSITIONS in related_topics

    def test_get_related_guides_invalid_topic(self, methodology_guides):
        """Test getting related guides for invalid topic."""
        from unittest.mock import Mock

        invalid_topic = Mock()
        invalid_topic.value = "invalid"

        related = methodology_guides.get_related_guides(invalid_topic)
        assert len(related) == 0

    def test_get_guide_by_phase_requirements(self, methodology_guides):
        """Test getting guide by phase name - requirements."""
        guide = methodology_guides.get_guide_by_phase("requirements")
        assert guide is not None
        assert guide.topic == MethodologyTopic.REQUIREMENTS

    def test_get_guide_by_phase_design(self, methodology_guides):
        """Test getting guide by phase name - design."""
        guide = methodology_guides.get_guide_by_phase("design")
        assert guide is not None
        assert guide.topic == MethodologyTopic.DESIGN

    def test_get_guide_by_phase_tasks(self, methodology_guides):
        """Test getting guide by phase name - tasks."""
        guide = methodology_guides.get_guide_by_phase("tasks")
        assert guide is not None
        assert guide.topic == MethodologyTopic.TASKS

    def test_get_guide_by_phase_workflow(self, methodology_guides):
        """Test getting guide by phase name - workflow."""
        guide = methodology_guides.get_guide_by_phase("workflow")
        assert guide is not None
        assert guide.topic == MethodologyTopic.WORKFLOW

    def test_get_guide_by_phase_case_insensitive(self, methodology_guides):
        """Test getting guide by phase name is case insensitive."""
        guide_lower = methodology_guides.get_guide_by_phase("requirements")
        guide_upper = methodology_guides.get_guide_by_phase("REQUIREMENTS")
        guide_mixed = methodology_guides.get_guide_by_phase("Requirements")

        assert guide_lower is not None
        assert guide_upper is not None
        assert guide_mixed is not None
        assert guide_lower.topic == guide_upper.topic == guide_mixed.topic

    def test_get_guide_by_phase_invalid(self, methodology_guides):
        """Test getting guide by invalid phase name."""
        guide = methodology_guides.get_guide_by_phase("invalid_phase")
        assert guide is None

    def test_guide_structure_completeness(self, methodology_guides):
        """Test that all guides have required structure."""
        for topic in methodology_guides.get_all_topics():
            guide = methodology_guides.get_guide(topic)
            assert guide is not None
            assert guide.topic == topic
            assert guide.title is not None and len(guide.title) > 0
            assert guide.content is not None and len(guide.content) > 0
            assert isinstance(guide.related_topics, list)
            assert isinstance(guide.examples, list)

    def test_guide_content_quality(self, methodology_guides):
        """Test that guide content meets quality standards."""
        # Test workflow guide has key sections
        workflow_guide = methodology_guides.get_guide(MethodologyTopic.WORKFLOW)
        assert "Phase 1: Requirements" in workflow_guide.content
        assert "Phase 2: Design" in workflow_guide.content
        assert "Phase 3: Tasks" in workflow_guide.content

        # Test requirements guide has EARS information
        req_guide = methodology_guides.get_guide(MethodologyTopic.REQUIREMENTS)
        assert "EARS Format" in req_guide.content
        assert "WHEN" in req_guide.content
        assert "THEN" in req_guide.content
        assert "SHALL" in req_guide.content

        # Test design guide has required sections
        design_guide = methodology_guides.get_guide(MethodologyTopic.DESIGN)
        assert "Overview" in design_guide.content
        assert "Architecture" in design_guide.content
        assert "Components and Interfaces" in design_guide.content
        assert "Data Models" in design_guide.content

        # Test tasks guide has structure information
        tasks_guide = methodology_guides.get_guide(MethodologyTopic.TASKS)
        assert "Task Structure" in tasks_guide.content
        assert "Requirement Traceability" in tasks_guide.content
        assert "_Requirements:" in tasks_guide.content
