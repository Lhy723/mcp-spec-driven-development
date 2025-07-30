"""Content loader for methodology files and templates."""

import logging
import os
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

from ..error_handler import get_error_handler
from ..exceptions import ContentAccessError
from ..fallback_content import FallbackContentProvider
from ..workflow.models import PhaseType


class ContentType(Enum):
    """Types of content available."""

    METHODOLOGY = "methodology"
    TEMPLATE = "template"
    EXAMPLE = "example"


class ContentLoader:
    """Loads methodology content and templates from data files with error handling and fallbacks."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize content loader with data directory path and error handling."""
        self.data_dir = Path(__file__).parent / "data"
        self._content_cache: Dict[str, str] = {}
        self.logger = logger or logging.getLogger(__name__)
        self.error_handler = get_error_handler()
        self.fallback_provider = FallbackContentProvider()

        # Register fallback handlers
        self.error_handler.register_fallback_handler(
            "content_methodology", self.fallback_provider.get_fallback_methodology
        )
        self.error_handler.register_fallback_handler(
            "content_template", self.fallback_provider.get_fallback_template
        )
        self.error_handler.register_fallback_handler(
            "content_example", self.fallback_provider.get_fallback_example
        )

    def get_methodology_content(self, topic: str) -> str:
        """
        Load methodology content by topic with error handling and fallbacks.

        Args:
            topic: The methodology topic to load

        Returns:
            The methodology content (primary or fallback)

        Raises:
            ContentAccessError: If content cannot be loaded and no fallback is available
        """
        file_path = self.data_dir / "methodology" / f"{topic}.md"

        try:
            content = self._load_file(file_path)
            if content is not None:
                return content

            # File doesn't exist, try fallback
            fallback_content = self.fallback_provider.get_fallback_methodology(topic)
            if fallback_content:
                self.logger.warning(
                    f"Using fallback methodology content for topic: {topic}"
                )
                return fallback_content

            # No fallback available
            raise self.error_handler.handle_content_access_error(
                message=f"Methodology content not found for topic: {topic}",
                content_type="methodology",
                requested_item=topic,
                context={"file_path": str(file_path)},
            )

        except ContentAccessError:
            raise
        except Exception as e:
            raise self.error_handler.handle_content_access_error(
                message=f"Failed to load methodology content for topic '{topic}': {str(e)}",
                content_type="methodology",
                requested_item=topic,
                context={"file_path": str(file_path), "original_error": str(e)},
            )

    def get_template_content(self, template_type: str) -> str:
        """
        Load template content by type with error handling and fallbacks.

        Args:
            template_type: The template type to load

        Returns:
            The template content (primary or fallback)

        Raises:
            ContentAccessError: If content cannot be loaded and no fallback is available
        """
        file_path = self.data_dir / "templates" / f"{template_type}-template.md"

        try:
            content = self._load_file(file_path)
            if content is not None:
                return content

            # File doesn't exist, try fallback
            fallback_content = self.fallback_provider.get_fallback_template(
                template_type
            )
            if fallback_content:
                self.logger.warning(
                    f"Using fallback template content for type: {template_type}"
                )
                return fallback_content

            # No fallback available
            raise self.error_handler.handle_content_access_error(
                message=f"Template content not found for type: {template_type}",
                content_type="template",
                requested_item=template_type,
                context={"file_path": str(file_path)},
            )

        except ContentAccessError:
            raise
        except Exception as e:
            raise self.error_handler.handle_content_access_error(
                message=f"Failed to load template content for type '{template_type}': {str(e)}",
                content_type="template",
                requested_item=template_type,
                context={"file_path": str(file_path), "original_error": str(e)},
            )

    def get_example_content(self, example_type: str) -> str:
        """
        Load example content by type with error handling and fallbacks.

        Args:
            example_type: The example type to load

        Returns:
            The example content (primary or fallback)

        Raises:
            ContentAccessError: If content cannot be loaded and no fallback is available
        """
        file_path = self.data_dir / "examples" / f"{example_type}-example.md"

        try:
            content = self._load_file(file_path)
            if content is not None:
                return content

            # File doesn't exist, try fallback
            fallback_content = self.fallback_provider.get_fallback_example(example_type)
            if fallback_content:
                self.logger.warning(
                    f"Using fallback example content for type: {example_type}"
                )
                return fallback_content

            # No fallback available
            raise self.error_handler.handle_content_access_error(
                message=f"Example content not found for type: {example_type}",
                content_type="example",
                requested_item=example_type,
                context={"file_path": str(file_path)},
            )

        except ContentAccessError:
            raise
        except Exception as e:
            raise self.error_handler.handle_content_access_error(
                message=f"Failed to load example content for type '{example_type}': {str(e)}",
                content_type="example",
                requested_item=example_type,
                context={"file_path": str(file_path), "original_error": str(e)},
            )

    def get_available_content(self, content_type: ContentType) -> List[str]:
        """
        Get list of available content items for a given type.

        Args:
            content_type: The type of content to list

        Returns:
            List of available content item names
        """
        try:
            if content_type == ContentType.METHODOLOGY:
                directory = self.data_dir / "methodology"
                pattern = "*.md"
            elif content_type == ContentType.TEMPLATE:
                directory = self.data_dir / "templates"
                pattern = "*-template.md"
            elif content_type == ContentType.EXAMPLE:
                directory = self.data_dir / "examples"
                pattern = "*-example.md"
            else:
                return []

            if not directory.exists():
                self.logger.warning(f"Content directory does not exist: {directory}")
                return []

            files = list(directory.glob(pattern))

            # Extract content names from filenames
            content_names = []
            for file_path in files:
                if content_type == ContentType.TEMPLATE:
                    # Remove "-template.md" suffix
                    name = file_path.stem.replace("-template", "")
                elif content_type == ContentType.EXAMPLE:
                    # Remove "-example.md" suffix
                    name = file_path.stem.replace("-example", "")
                else:
                    # Remove ".md" suffix
                    name = file_path.stem
                content_names.append(name)

            return sorted(content_names)

        except Exception as e:
            self.logger.error(f"Error listing {content_type.value} content: {e}")
            return []

    def validate_content_structure(self) -> Dict[str, List[str]]:
        """
        Validate the content directory structure and report issues.

        Returns:
            Dictionary with content types as keys and lists of issues as values
        """
        issues = {"methodology": [], "templates": [], "examples": [], "general": []}

        try:
            # Check if data directory exists
            if not self.data_dir.exists():
                issues["general"].append(
                    f"Data directory does not exist: {self.data_dir}"
                )
                return issues

            # Check methodology directory
            methodology_dir = self.data_dir / "methodology"
            if not methodology_dir.exists():
                issues["methodology"].append("Methodology directory does not exist")
            else:
                expected_files = [
                    "workflow.md",
                    "ears-format.md",
                    "phase-transitions.md",
                ]
                for expected_file in expected_files:
                    file_path = methodology_dir / expected_file
                    if not file_path.exists():
                        issues["methodology"].append(
                            f"Missing methodology file: {expected_file}"
                        )

            # Check templates directory
            templates_dir = self.data_dir / "templates"
            if not templates_dir.exists():
                issues["templates"].append("Templates directory does not exist")
            else:
                expected_templates = [
                    "requirements-template.md",
                    "design-template.md",
                    "tasks-template.md",
                ]
                for expected_template in expected_templates:
                    file_path = templates_dir / expected_template
                    if not file_path.exists():
                        issues["templates"].append(
                            f"Missing template file: {expected_template}"
                        )

            # Check examples directory (optional)
            examples_dir = self.data_dir / "examples"
            if examples_dir.exists():
                example_files = list(examples_dir.glob("*-example.md"))
                if not example_files:
                    issues["examples"].append(
                        "Examples directory exists but contains no example files"
                    )

        except Exception as e:
            issues["general"].append(f"Error validating content structure: {str(e)}")

        return issues

    def _load_file(self, file_path: Path) -> Optional[str]:
        """
        Load content from file with caching and comprehensive error handling.

        Args:
            file_path: Path to the file to load

        Returns:
            File content if successful, None if file doesn't exist

        Raises:
            Exception: For file access errors other than file not found
        """
        cache_key = str(file_path)

        # Return cached content if available
        if cache_key in self._content_cache:
            return self._content_cache[cache_key]

        # Check if file exists
        if not file_path.exists():
            return None

        # Load from file
        try:
            content = file_path.read_text(encoding="utf-8")
            self._content_cache[cache_key] = content
            self.logger.debug(f"Loaded content from: {file_path}")
            return content

        except UnicodeDecodeError as e:
            raise Exception(f"Unicode decode error reading {file_path}: {e}")
        except PermissionError as e:
            raise Exception(f"Permission denied reading {file_path}: {e}")
        except OSError as e:
            raise Exception(f"OS error reading {file_path}: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error reading {file_path}: {e}")

    def clear_cache(self) -> None:
        """Clear the content cache."""
        self._content_cache.clear()
        self.logger.debug("Content cache cleared")

    def get_cache_info(self) -> Dict[str, int]:
        """Get information about the content cache."""
        return {
            "cached_items": len(self._content_cache),
            "cache_keys": list(self._content_cache.keys()),
        }

        return None

    def list_methodology_topics(self) -> list[str]:
        """List available methodology topics."""
        methodology_dir = self.data_dir / "methodology"
        if not methodology_dir.exists():
            return []

        topics = []
        for file_path in methodology_dir.glob("*.md"):
            topic = file_path.stem
            topics.append(topic)

        return sorted(topics)

    def list_template_types(self) -> list[str]:
        """List available template types."""
        templates_dir = self.data_dir / "templates"
        if not templates_dir.exists():
            return []

        types = []
        for file_path in templates_dir.glob("*-template.md"):
            template_type = file_path.stem.replace("-template", "")
            types.append(template_type)

        return sorted(types)

    def clear_cache(self) -> None:
        """Clear the content cache."""
        self._content_cache.clear()

    def get_content_info(self) -> Dict[str, list[str]]:
        """Get information about available content."""
        return {
            "methodology_topics": self.list_methodology_topics(),
            "template_types": self.list_template_types(),
        }

    def load_spec_document(self, feature_name: str, phase: PhaseType) -> Optional[str]:
        """Load a spec document for a specific feature and phase."""
        # Construct path to spec document
        spec_path = Path.cwd() / ".kiro" / "specs" / feature_name / f"{phase.value}.md"

        try:
            if spec_path.exists():
                return spec_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"Error loading spec document {spec_path}: {e}")

        return None
