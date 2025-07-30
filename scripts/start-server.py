#!/usr/bin/env python3
"""
Startup script for MCP Spec-Driven Development server.

This script provides a robust entry point for the MCP server with proper
error handling, logging configuration, and graceful shutdown.
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from typing import Optional

import structlog

from mcp_spec_driven_development.config import ServerConfig, setup_logging
from mcp_spec_driven_development.server import main as server_main


class ServerManager:
    """Manages the MCP server lifecycle with proper startup and shutdown."""

    def __init__(self, config: ServerConfig):
        self.config = config
        self.logger = structlog.get_logger(__name__)
        self._shutdown_event = asyncio.Event()

    async def start(self) -> None:
        """Start the MCP server with proper signal handling."""
        # Setup signal handlers for graceful shutdown
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._signal_handler)

        self.logger.info(
            "Starting MCP Spec-Driven Development server",
            version=self.config.version,
            log_level=self.config.log_level,
        )

        try:
            # Start the server
            await server_main()
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt, shutting down...")
        except Exception as e:
            self.logger.error("Server error", error=str(e), exc_info=True)
            raise
        finally:
            await self._cleanup()

    def _signal_handler(self, signum: int, frame) -> None:
        """Handle shutdown signals."""
        self.logger.info("Received shutdown signal", signal=signum)
        self._shutdown_event.set()

    async def _cleanup(self) -> None:
        """Perform cleanup operations."""
        self.logger.info("Server shutdown complete")


def main() -> None:
    """Main entry point for the server startup script."""
    try:
        # Load configuration
        config = ServerConfig.from_env()

        # Setup logging
        setup_logging(config.log_level, config.log_format)

        # Create and start server manager
        server_manager = ServerManager(config)
        asyncio.run(server_manager.start())

    except Exception as e:
        print(f"Failed to start server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
