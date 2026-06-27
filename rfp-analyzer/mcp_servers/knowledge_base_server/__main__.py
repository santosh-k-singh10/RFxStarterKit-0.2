"""
MCP Server Entry Point for Knowledge Base Server
-------------------------------------------------
Allows running the server as a module: python -m mcp_servers.knowledge_base_server
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to allow imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mcp_servers.knowledge_base_server.server import create_mcp_server, MCP_AVAILABLE
import structlog

log = structlog.get_logger(__name__)


async def main():
    """Run the Knowledge Base MCP Server."""
    if not MCP_AVAILABLE:
        print("Error: MCP package not available. Install with: pip install mcp")
        sys.exit(1)
    
    # Get context root from environment or use default
    import os
    context_root = os.getenv("CONTEXT_ROOT", "./org_context")
    
    log.info("starting_knowledge_base_server", context_root=context_root)
    print(f"Starting Knowledge Base MCP Server...")
    print(f"Context Root: {context_root}")
    
    # Create and run server
    server = create_mcp_server(context_root)
    
    # Import MCP server runner
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nServer stopped by user")
    except Exception as e:
        log.error("server_error", error=str(e))
        print(f"Error: {e}")
        sys.exit(1)

# Made with Bob
