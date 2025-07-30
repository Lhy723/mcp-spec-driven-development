"""Performance tests for content retrieval and validation using pytest-benchmark."""

import asyncio
from unittest.mock import patch

import pytest

from src.mcp_spec_driven_development.content.content_loader import ContentLoader
from src.mcp_spec_driven_development.tools.content_tools import ContentAccessTools
from src.mcp_spec_driven_development.tools.validation_tools import ValidationTools
from src.mcp_spec_driven_development.tools.workflow_tools import WorkflowManagementTools
from src.mcp_spec_driven_development.validation.design_validator import DesignValidator
from src.mcp_spec_driven_development.validation.requirements_validator import (
    RequirementsValidator,
)
from src.mcp_spec_driven_development.validation.task_validator import TaskValidator


class TestPerformanceBenchmarks:
    """Performance benchmarks for core functionality."""

    @pytest.fixture
    def content_loader(self):
        """Create content loader instance."""
        return ContentLoader()

    @pytest.fixture
    def content_tools(self):
        """Create content tools instance."""
        return ContentAccessTools()

    @pytest.fixture
    def validation_tools(self):
        """Create validation tools instance."""
        return ValidationTools()

    @pytest.fixture
    def workflow_tools(self):
        """Create workflow tools instance."""
        return WorkflowManagementTools()

    @pytest.fixture
    def requirements_validator(self):
        """Create requirements validator instance."""
        return RequirementsValidator()

    @pytest.fixture
    def design_validator(self):
        """Create design validator instance."""
        return DesignValidator()

    @pytest.fixture
    def task_validator(self):
        """Create task validator instance."""
        return TaskValidator()

    @pytest.fixture
    def sample_requirements(self):
        """Sample requirements document for testing."""
        return """
        # Requirements Document

        ## Introduction
        This is a sample requirements document for performance testing.

        ## Requirements

        ### Requirement 1
        **User Story:** As a user, I want to test performance, so that I can measure system speed.

        #### Acceptance Criteria
        1. WHEN the system is tested THEN it SHALL respond within acceptable time limits
        2. WHEN multiple requests are made THEN the system SHALL handle them efficiently

        ### Requirement 2
        **User Story:** As a developer, I want fast validation, so that I can iterate quickly.

        #### Acceptance Criteria
        1. WHEN validation is performed THEN it SHALL complete within 100ms
        2. WHEN content is loaded THEN it SHALL be cached for subsequent requests
        """

    @pytest.fixture
    def sample_design(self):
        """Sample design document for testing."""
        return """
        # Design Document

        ## Overview
        This is a sample design document for performance testing.

        ## Architecture
        The system follows a modular architecture with clear separation of concerns.

        ## Components and Interfaces
        - Content Management Layer
        - Validation Layer
        - Workflow Management Layer

        ## Data Models
        The system uses well-defined data models for all entities.

        ## Error Handling
        Comprehensive error handling is implemented throughout.

        ## Testing Strategy
        Performance testing is included in the testing strategy.
        """

    def test_content_loader_methodology_performance(self, benchmark, content_loader):
        """Benchmark methodology content loading performance."""

        def load_methodology():
            return content_loader.get_methodology_content("workflow")

        result = benchmark(load_methodology)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_content_loader_template_performance(self, benchmark, content_loader):
        """Benchmark template content loading performance."""

        def load_template():
            return content_loader.get_template_content("requirements")

        result = benchmark(load_template)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_content_loader_caching_performance(self, benchmark, content_loader):
        """Benchmark content loading with caching."""
        # First load to populate cache
        content_loader.get_methodology_content("workflow")

        def load_cached_content():
            return content_loader.get_methodology_content("workflow")

        result = benchmark(load_cached_content)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_requirements_validation_performance(
        self, benchmark, requirements_validator, sample_requirements
    ):
        """Benchmark requirements validation performance."""

        def validate_requirements():
            return requirements_validator.validate(sample_requirements)

        result = benchmark(validate_requirements)
        assert result is not None

    def test_design_validation_performance(
        self, benchmark, design_validator, sample_design
    ):
        """Benchmark design validation performance."""

        def validate_design():
            return design_validator.validate(sample_design)

        result = benchmark(validate_design)
        assert result is not None

    def test_task_validation_performance(self, benchmark, task_validator):
        """Benchmark task validation performance."""
        sample_tasks = """
        # Implementation Plan

        - [ ] 1. Set up project structure
          - Create directory structure
          - Initialize configuration
          - _Requirements: 1.1_

        - [ ] 2. Implement core functionality
          - Build main components
          - Add error handling
          - _Requirements: 1.2, 2.1_
        """

        def validate_tasks():
            return task_validator.validate(sample_tasks)

        result = benchmark(validate_tasks)
        assert result is not None

    @pytest.mark.asyncio
    async def test_content_tools_async_performance(self, benchmark, content_tools):
        """Benchmark async content tools performance."""

        async def get_methodology_async():
            return await content_tools.handle_get_methodology_guide(
                {"topic": "workflow"}
            )

        def run_async_operation():
            return asyncio.run(get_methodology_async())

        result = benchmark(run_async_operation)
        assert len(result) == 1
        assert len(result[0].text) > 0

    @pytest.mark.asyncio
    async def test_validation_tools_async_performance(
        self, benchmark, validation_tools, sample_requirements
    ):
        """Benchmark async validation tools performance."""

        async def validate_document_async():
            return await validation_tools.handle_validate_document(
                {"document_type": "requirements", "content": sample_requirements}
            )

        def run_async_validation():
            return asyncio.run(validate_document_async())

        result = benchmark(run_async_validation)
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_workflow_tools_async_performance(self, benchmark, workflow_tools):
        """Benchmark async workflow tools performance."""

        async def create_workflow_async():
            return await workflow_tools.handle_create_workflow(
                {"feature_name": "perf-test"}
            )

        def run_async_workflow():
            return asyncio.run(create_workflow_async())

        result = benchmark(run_async_workflow)
        assert len(result) == 1

    def test_multiple_content_loads_performance(self, benchmark, content_loader):
        """Benchmark multiple content loads."""

        def load_multiple_content():
            results = []
            topics = ["workflow", "ears-format", "phase-transitions"]
            for topic in topics:
                try:
                    result = content_loader.get_methodology_content(topic)
                    results.append(result)
                except:
                    # Some topics might not exist, that's ok for performance testing
                    pass
            return results

        results = benchmark(load_multiple_content)
        assert len(results) > 0

    def test_validation_with_large_content_performance(
        self, benchmark, requirements_validator
    ):
        """Benchmark validation with large content."""
        # Create large requirements document
        large_requirements = """
        # Requirements Document

        ## Introduction
        This is a large requirements document for performance testing.
        """ + "\n".join(
            [
                f"""
        ### Requirement {i}
        **User Story:** As a user, I want feature {i}, so that I can achieve goal {i}.

        #### Acceptance Criteria
        1. WHEN condition {i} occurs THEN system SHALL respond with action {i}
        2. WHEN user performs action {i} THEN system SHALL validate input {i}
        3. WHEN validation passes THEN system SHALL process request {i}
        """
                for i in range(1, 21)  # 20 requirements
            ]
        )

        def validate_large_content():
            return requirements_validator.validate(large_requirements)

        result = benchmark(validate_large_content)
        assert result is not None

    def test_concurrent_content_access_performance(self, benchmark, content_loader):
        """Benchmark concurrent content access."""
        import threading
        import time

        def concurrent_access():
            results = []
            errors = []

            def load_content(topic):
                try:
                    result = content_loader.get_methodology_content("workflow")
                    results.append(len(result))
                except Exception as e:
                    errors.append(e)

            # Create multiple threads
            threads = []
            for _ in range(5):
                thread = threading.Thread(target=load_content, args=("workflow",))
                threads.append(thread)

            # Start all threads
            for thread in threads:
                thread.start()

            # Wait for completion
            for thread in threads:
                thread.join()

            return len(results), len(errors)

        result_count, error_count = benchmark(concurrent_access)
        assert result_count > 0
        assert error_count == 0

    def test_cache_performance_comparison(self, benchmark, content_loader):
        """Compare performance with and without caching."""
        # Clear cache first
        content_loader.clear_cache()

        def load_without_cache():
            content_loader.clear_cache()
            return content_loader.get_methodology_content("workflow")

        def load_with_cache():
            # First call populates cache
            content_loader.get_methodology_content("workflow")
            # Second call uses cache
            return content_loader.get_methodology_content("workflow")

        # Benchmark without cache
        result1 = benchmark.pedantic(load_without_cache, rounds=5, iterations=1)

        # Benchmark with cache
        result2 = benchmark.pedantic(load_with_cache, rounds=5, iterations=1)

        assert isinstance(result1, str)
        assert isinstance(result2, str)
        assert result1 == result2  # Same content

    def test_validation_error_performance(self, benchmark, requirements_validator):
        """Benchmark validation performance with errors."""
        invalid_requirements = "This is not a valid requirements document"

        def validate_invalid_content():
            return requirements_validator.validate(invalid_requirements)

        result = benchmark(validate_invalid_content)
        assert result is not None

    def test_memory_usage_during_operations(self, benchmark, content_loader):
        """Test memory usage during content operations."""
        import gc

        def memory_intensive_operation():
            # Load multiple pieces of content
            results = []
            for _ in range(10):
                try:
                    result = content_loader.get_methodology_content("workflow")
                    results.append(result)
                except:
                    pass

            # Force garbage collection
            gc.collect()
            return len(results)

        result = benchmark(memory_intensive_operation)
        assert result > 0

    @pytest.mark.asyncio
    async def test_async_tool_chain_performance(
        self, benchmark, content_tools, validation_tools
    ):
        """Benchmark chained async tool operations."""

        async def tool_chain():
            # Get template
            template_result = await content_tools.handle_get_template(
                {"template_type": "requirements"}
            )
            template_content = template_result[0].text

            # Validate content
            validation_result = await validation_tools.handle_validate_document(
                {
                    "document_type": "requirements",
                    "content": template_content[:500],  # Use part of template
                }
            )

            return len(validation_result)

        def run_tool_chain():
            return asyncio.run(tool_chain())

        result = benchmark(run_tool_chain)
        assert result == 1

    def test_content_structure_validation_performance(self, benchmark, content_loader):
        """Benchmark content structure validation performance."""

        def validate_structure():
            return content_loader.validate_content_structure()

        result = benchmark(validate_structure)
        assert isinstance(result, dict)

    def test_available_content_listing_performance(self, benchmark, content_loader):
        """Benchmark available content listing performance."""
        from src.mcp_spec_driven_development.content.content_loader import ContentType

        def list_available_content():
            results = []
            for content_type in ContentType:
                result = content_loader.get_available_content(content_type)
                results.extend(result)
            return results

        result = benchmark(list_available_content)
        assert isinstance(result, list)
