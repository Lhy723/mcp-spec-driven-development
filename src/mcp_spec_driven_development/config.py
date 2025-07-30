"""Configuration management for MCP Spec-Driven Development server."""

import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional

import structlog

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
LogFormat = Literal["json", "console"]


@dataclass
class ServerConfig:
    """Configuration for the MCP server."""

    # Server identification
    name: str = "mcp-spec-driven-development"
    version: str = "0.1.0"

    # Logging configuration
    log_level: LogLevel = "INFO"
    log_format: LogFormat = "console"
    log_file: Optional[Path] = None

    # Content paths
    content_root: Path = Path(__file__).parent / "content" / "data"

    # Performance settings
    max_content_size: int = 1024 * 1024  # 1MB
    cache_ttl: int = 3600  # 1 hour

    @classmethod
    def from_env(cls) -> "ServerConfig":
        """Create configuration from environment variables."""
        return cls(
            name=os.getenv("MCP_SERVER_NAME", "mcp-spec-driven-development"),
            version=os.getenv("MCP_SERVER_VERSION", "0.1.0"),
            log_level=os.getenv("MCP_LOG_LEVEL", "INFO").upper(),  # type: ignore
            log_format=os.getenv("MCP_LOG_FORMAT", "console").lower(),  # type: ignore
            log_file=Path(log_file)
            if (log_file := os.getenv("MCP_LOG_FILE"))
            else None,
            content_root=Path(
                os.getenv(
                    "MCP_CONTENT_ROOT", str(Path(__file__).parent / "content" / "data")
                )
            ),
            max_content_size=int(os.getenv("MCP_MAX_CONTENT_SIZE", "1048576")),
            cache_ttl=int(os.getenv("MCP_CACHE_TTL", "3600")),
        )


def setup_logging(
    level: LogLevel, format_type: LogFormat, log_file: Optional[Path] = None
) -> None:
    """Setup structured logging with the specified configuration."""

    # Configure structlog
    processors = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if format_type == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(colors=True))

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, level),
        format="%(message)s" if format_type == "json" else None,
        handlers=[
            logging.FileHandler(log_file) if log_file else logging.StreamHandler(),
        ],
    )

    # Set MCP library log level to reduce noise
    logging.getLogger("mcp").setLevel(logging.WARNING)


def get_health_check_config() -> dict:
    """Get configuration for health checks and monitoring."""
    return {
        "enabled": os.getenv("MCP_HEALTH_CHECK_ENABLED", "true").lower() == "true",
        "interval": int(os.getenv("MCP_HEALTH_CHECK_INTERVAL", "30")),
        "timeout": int(os.getenv("MCP_HEALTH_CHECK_TIMEOUT", "5")),
        "endpoints": {
            "tools": True,
            "content": True,
            "validation": True,
        },
    }
