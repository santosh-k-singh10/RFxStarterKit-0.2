"""
Knowledge Base MCP Server
-------------------------
Provides semantic search and knowledge retrieval for organizational context.

This is a simplified implementation that demonstrates the architecture.
For production use, extend with:
- Full vector database integration (ChromaDB/Pinecone)
- Advanced embedding models
- Caching layer
- Authentication
"""

import os
import json
from pathlib import Path
from typing import Any, Optional, TYPE_CHECKING
import structlog

if TYPE_CHECKING:
    from mcp.server import Server
    from mcp.types import Tool, TextContent, Resource

try:
    from mcp.server import Server
    from mcp.types import Tool, TextContent, Resource
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    print("Warning: MCP not available. Install with: pip install mcp")

log = structlog.get_logger(__name__)


class KnowledgeBaseServer:
    """
    Simplified Knowledge Base MCP Server.
    
    Provides basic knowledge retrieval capabilities.
    For production, integrate with vector databases for semantic search.
    """
    
    def __init__(self, context_root: str = "./org_context"):
        """
        Initialize the knowledge base server.
        
        Parameters
        ----------
        context_root : str
            Root directory containing organizational context
        """
        self.context_root = Path(context_root)
        self.standards_dir = self.context_root / "standards"
        self.examples_dir = self.context_root / "examples"
        self.domain_knowledge_dir = self.context_root / "domain_knowledge"
        
        log.info("knowledge_base_server_initialized", context_root=str(self.context_root))
    
    def search_org_knowledge(
        self,
        query: str,
        category: str = "all",
        top_k: int = 5
    ) -> list[dict[str, Any]]:
        """
        Search organizational knowledge.
        
        Simplified implementation using keyword matching.
        For production, use vector embeddings and semantic search.
        
        Parameters
        ----------
        query : str
            Search query
        category : str
            Category to search in (standards, past_rfps, requirements_patterns, all)
        top_k : int
            Number of results to return
            
        Returns
        -------
        list[dict]
            Search results with content and metadata
        """
        log.info("searching_knowledge", query=query, category=category)
        
        results = []
        query_lower = query.lower()
        
        # Search standards
        if category in ("standards", "all"):
            results.extend(self._search_directory(
                self.standards_dir,
                query_lower,
                "standard"
            ))
        
        # Search examples
        if category in ("past_rfps", "examples", "all"):
            results.extend(self._search_directory(
                self.examples_dir,
                query_lower,
                "example"
            ))
        
        # Search domain knowledge
        if category in ("domain_knowledge", "all"):
            results.extend(self._search_directory(
                self.domain_knowledge_dir,
                query_lower,
                "domain_knowledge"
            ))
        
        # Sort by relevance (simple keyword count for now)
        results.sort(key=lambda x: x.get("relevance", 0), reverse=True)
        
        return results[:top_k]
    
    def _search_directory(
        self,
        directory: Path,
        query: str,
        category: str
    ) -> list[dict[str, Any]]:
        """Search files in a directory for query matches."""
        results = []
        
        if not directory.exists():
            return results
        
        for file_path in directory.rglob("*.md"):
            try:
                content = file_path.read_text(encoding="utf-8")
                content_lower = content.lower()
                
                # Simple relevance scoring based on keyword occurrences
                relevance = content_lower.count(query)
                
                if relevance > 0:
                    # Extract context around matches
                    lines = content.split("\n")
                    matching_lines = [
                        line for line in lines
                        if query in line.lower()
                    ]
                    
                    results.append({
                        "file": str(file_path.relative_to(self.context_root)),
                        "category": category,
                        "relevance": relevance,
                        "excerpt": "\n".join(matching_lines[:3]),
                        "full_path": str(file_path)
                    })
            except Exception as e:
                log.warning("file_read_error", file=str(file_path), error=str(e))
        
        return results
    
    def get_compliance_standard(self, framework: str) -> Optional[dict[str, Any]]:
        """
        Retrieve compliance standard details.
        
        Parameters
        ----------
        framework : str
            Compliance framework name (e.g., "GDPR", "HIPAA")
            
        Returns
        -------
        dict | None
            Standard details or None if not found
        """
        log.info("retrieving_compliance_standard", framework=framework)
        
        # Look for framework-specific file
        standard_file = self.standards_dir / f"{framework.lower()}.md"
        
        if standard_file.exists():
            try:
                content = standard_file.read_text(encoding="utf-8")
                return {
                    "framework": framework,
                    "content": content,
                    "file": str(standard_file.relative_to(self.context_root))
                }
            except Exception as e:
                log.error("standard_read_error", framework=framework, error=str(e))
        
        # Fallback: search in compliance_frameworks.md
        compliance_file = self.standards_dir / "compliance_frameworks.md"
        if compliance_file.exists():
            try:
                content = compliance_file.read_text(encoding="utf-8")
                if framework.lower() in content.lower():
                    return {
                        "framework": framework,
                        "content": content,
                        "file": str(compliance_file.relative_to(self.context_root)),
                        "note": "Extracted from general compliance document"
                    }
            except Exception as e:
                log.error("compliance_file_read_error", error=str(e))
        
        log.warning("compliance_standard_not_found", framework=framework)
        return None
    
    def find_similar_past_rfps(
        self,
        description: str,
        top_k: int = 3
    ) -> list[dict[str, Any]]:
        """
        Find similar past RFPs.
        
        Simplified implementation using keyword matching.
        For production, use vector embeddings for semantic similarity.
        
        Parameters
        ----------
        description : str
            RFP description to match against
        top_k : int
            Number of similar RFPs to return
            
        Returns
        -------
        list[dict]
            Similar past RFPs with metadata
        """
        log.info("finding_similar_rfps", description_length=len(description))
        
        past_rfps_dir = self.examples_dir / "past_rfps"
        
        if not past_rfps_dir.exists():
            log.warning("past_rfps_directory_not_found")
            return []
        
        results = []
        description_lower = description.lower()
        keywords = set(description_lower.split())
        
        for rfp_file in past_rfps_dir.rglob("*.md"):
            try:
                content = rfp_file.read_text(encoding="utf-8")
                content_lower = content.lower()
                
                # Calculate similarity based on keyword overlap
                content_words = set(content_lower.split())
                common_words = keywords.intersection(content_words)
                similarity = len(common_words) / len(keywords) if keywords else 0
                
                if similarity > 0.1:  # Threshold for relevance
                    results.append({
                        "file": str(rfp_file.relative_to(self.context_root)),
                        "similarity": similarity,
                        "excerpt": content[:500],
                        "full_path": str(rfp_file)
                    })
            except Exception as e:
                log.warning("rfp_file_read_error", file=str(rfp_file), error=str(e))
        
        # Sort by similarity
        results.sort(key=lambda x: x["similarity"], reverse=True)
        
        return results[:top_k]
    
    def index_document(
        self,
        file_path: str,
        category: str,
        metadata: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """
        Index a new document in the knowledge base.
        
        For production, this would:
        - Generate embeddings
        - Store in vector database
        - Update search indices
        
        Parameters
        ----------
        file_path : str
            Path to document to index
        category : str
            Category (standards, past_rfps, domain_knowledge)
        metadata : dict | None
            Additional metadata
            
        Returns
        -------
        dict
            Indexing result
        """
        log.info("indexing_document", file_path=file_path, category=category)
        
        source_path = Path(file_path)
        if not source_path.exists():
            return {"success": False, "error": "File not found"}
        
        # Determine target directory
        target_dirs = {
            "standards": self.standards_dir,
            "past_rfps": self.examples_dir / "past_rfps",
            "domain_knowledge": self.domain_knowledge_dir
        }
        
        target_dir = target_dirs.get(category)
        if not target_dir:
            return {"success": False, "error": f"Invalid category: {category}"}
        
        # Create directory if needed
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy file to knowledge base
        target_path = target_dir / source_path.name
        try:
            import shutil
            shutil.copy2(source_path, target_path)
            
            # Save metadata if provided
            if metadata:
                metadata_path = target_path.with_suffix(".meta.json")
                metadata_path.write_text(json.dumps(metadata, indent=2))
            
            log.info("document_indexed", target=str(target_path))
            return {
                "success": True,
                "indexed_path": str(target_path.relative_to(self.context_root)),
                "category": category
            }
        except Exception as e:
            log.error("indexing_error", error=str(e))
            return {"success": False, "error": str(e)}


# MCP Server setup (if MCP is available)
if MCP_AVAILABLE:
    def create_mcp_server(context_root: str = "./org_context") -> Server:
        """
        Create and configure the MCP server.
        
        Parameters
        ----------
        context_root : str
            Root directory for organizational context
            
        Returns
        -------
        Server
            Configured MCP server instance
        """
        server = Server("knowledge-base")
        kb = KnowledgeBaseServer(context_root)
        
        @server.list_tools()
        async def list_tools() -> list[Tool]:
            """List available tools."""
            return [
                Tool(
                    name="search_org_knowledge",
                    description="Search organizational knowledge base using keywords",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "query": {"type": "string", "description": "Search query"},
                            "category": {
                                "type": "string",
                                "enum": ["all", "standards", "past_rfps", "domain_knowledge"],
                                "default": "all"
                            },
                            "top_k": {"type": "integer", "default": 5}
                        },
                        "required": ["query"]
                    }
                ),
                Tool(
                    name="get_compliance_standard",
                    description="Retrieve detailed compliance standard information",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "framework": {"type": "string", "description": "Framework name (GDPR, HIPAA, etc.)"}
                        },
                        "required": ["framework"]
                    }
                ),
                Tool(
                    name="find_similar_past_rfps",
                    description="Find similar past RFPs based on description",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "description": {"type": "string", "description": "RFP description"},
                            "top_k": {"type": "integer", "default": 3}
                        },
                        "required": ["description"]
                    }
                ),
                Tool(
                    name="index_document",
                    description="Add a new document to the knowledge base",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "file_path": {"type": "string"},
                            "category": {
                                "type": "string",
                                "enum": ["standards", "past_rfps", "domain_knowledge"]
                            },
                            "metadata": {"type": "object"}
                        },
                        "required": ["file_path", "category"]
                    }
                )
            ]
        
        @server.call_tool()
        async def call_tool(name: str, arguments: dict) -> list[TextContent]:
            """Handle tool calls."""
            try:
                if name == "search_org_knowledge":
                    results = kb.search_org_knowledge(**arguments)
                    return [TextContent(
                        type="text",
                        text=json.dumps(results, indent=2)
                    )]
                
                elif name == "get_compliance_standard":
                    result = kb.get_compliance_standard(**arguments)
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2) if result else "Standard not found"
                    )]
                
                elif name == "find_similar_past_rfps":
                    results = kb.find_similar_past_rfps(**arguments)
                    return [TextContent(
                        type="text",
                        text=json.dumps(results, indent=2)
                    )]
                
                elif name == "index_document":
                    result = kb.index_document(**arguments)
                    return [TextContent(
                        type="text",
                        text=json.dumps(result, indent=2)
                    )]
                
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            
            except Exception as e:
                log.error("tool_call_error", tool=name, error=str(e))
                return [TextContent(
                    type="text",
                    text=f"Error: {str(e)}"
                )]
        
        return server


# Standalone usage
if __name__ == "__main__":
    import asyncio
    
    if MCP_AVAILABLE:
        async def main():
            server = create_mcp_server()
            # Run server (implementation depends on MCP server runner)
            print("Knowledge Base MCP Server ready")
        
        asyncio.run(main())
    else:
        # Demo mode without MCP
        print("Running in demo mode (MCP not available)")
        kb = KnowledgeBaseServer()
        
        # Test search
        results = kb.search_org_knowledge("authentication", category="all", top_k=3)
        print(f"\nSearch results: {len(results)} found")
        for r in results:
            print(f"  - {r['file']} (relevance: {r['relevance']})")

# Made with Bob
