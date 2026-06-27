"""
org_context/context_studio_client.py
------------------------------------
Client for IBM ICA Context Studio using actual Context Studio MCP tools.

This client uses the real Context Studio tools discovered from the MCP server:
- context-broker-get-contexts
- context-broker-vector-query
- context-broker-hybrid-query
- context-broker-graph-query
- context-broker-get-context-metadata
- context-broker-get-context-schema
"""

from __future__ import annotations

import json
from typing import Dict, Any, Optional, List
import structlog
import httpx
from datetime import datetime, timedelta

log = structlog.get_logger(__name__)


class ContextStudioClient:
    """
    Client for interacting with IBM ICA Context Studio MCP server.
    
    Uses the actual Context Studio tools to fetch organizational context.
    """
    
    def __init__(
        self,
        mcp_url: str,
        mcp_gateway_token: str,
        context_studio_key: str,
        context_id: str,
        agent_persona: str = "RFPAnalyzer",
        cache_ttl: int = 300
    ):
        """
        Initialize Context Studio Client.
        
        Parameters
        ----------
        mcp_url : str
            URL of the MCP gateway server
        mcp_gateway_token : str
            Bearer token for MCP gateway authentication
        context_studio_key : str
            API key for Context Studio
        context_id : str
            Context ID to query (your organization's context)
        agent_persona : str
            Agent persona identifier (default: "RFPAnalyzer")
        cache_ttl : int
            Cache time-to-live in seconds (default: 300)
        """
        self.mcp_url = mcp_url.rstrip('/')
        self.context_id = context_id
        self.agent_persona = agent_persona
        self.headers = {
            'Authorization': f'Bearer {mcp_gateway_token}',
            'x-api-key': context_studio_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        
        log.info(
            "context_studio_client_initialized",
            mcp_url=mcp_url,
            context_id=context_id,
            agent_persona=agent_persona,
            cache_ttl=cache_ttl
        )
    
    def _get_from_cache(self, key: str) -> Optional[Any]:
        """Get value from cache if not expired."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if datetime.now() - timestamp < timedelta(seconds=self.cache_ttl):
                log.debug("cache_hit", key=key)
                return value
            else:
                log.debug("cache_expired", key=key)
                del self._cache[key]
        return None
    
    def _set_cache(self, key: str, value: Any):
        """Set value in cache with current timestamp."""
        self._cache[key] = (value, datetime.now())
        log.debug("cache_set", key=key)
    
    def _call_mcp_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Call an MCP tool using JSON-RPC 2.0 protocol.
        
        Parameters
        ----------
        tool_name : str
            Name of the tool to call
        arguments : dict
            Tool arguments
            
        Returns
        -------
        Any
            Tool response data
        """
        # Check cache first
        cache_key = f"{tool_name}:{json.dumps(arguments, sort_keys=True)}"
        cached = self._get_from_cache(cache_key)
        if cached is not None:
            return cached
        
        # Prepare JSON-RPC 2.0 request
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        log.info("calling_mcp_tool", tool=tool_name, arguments=arguments)
        
        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    self.mcp_url,
                    headers=self.headers,
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                
                # Handle JSON-RPC 2.0 response format
                if 'result' in result:
                    mcp_result = result['result']
                    
                    # Extract content from MCP response
                    if 'content' in mcp_result and len(mcp_result['content']) > 0:
                        content = mcp_result['content'][0]
                        if content.get('type') == 'text':
                            data = json.loads(content['text'])
                            self._set_cache(cache_key, data)
                            log.info("mcp_tool_success", tool=tool_name)
                            return data
                    
                    # If result is directly the data
                    if isinstance(mcp_result, dict) and 'content' not in mcp_result:
                        self._set_cache(cache_key, mcp_result)
                        log.info("mcp_tool_success", tool=tool_name)
                        return mcp_result
                
                elif 'error' in result:
                    log.error("mcp_tool_error", tool=tool_name, error=result['error'])
                    raise Exception(f"MCP tool error: {result['error']}")
                
                log.warning("unexpected_mcp_response", tool=tool_name)
                return None
                
        except httpx.HTTPError as e:
            log.error("mcp_http_error", tool=tool_name, error=str(e))
            raise
        except json.JSONDecodeError as e:
            log.error("mcp_json_error", tool=tool_name, error=str(e))
            raise
        except Exception as e:
            log.error("mcp_call_failed", tool=tool_name, error=str(e))
            raise
    
    def get_all_contexts(self) -> List[Dict[str, Any]]:
        """
        Get list of all available contexts.
        
        Returns
        -------
        list
            List of contexts with context_id, name, and description
        """
        return self._call_mcp_tool("context-broker-get-contexts", {})
    
    def get_context_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the current context.
        
        Returns detailed information about context sources, connected systems,
        and manually ingested documents.
        
        Returns
        -------
        dict
            Context metadata including sources and ingestions
        """
        return self._call_mcp_tool("context-broker-get-context-metadata", {
            "context_id": self.context_id
        })
    
    def get_context_schema(self, ontology_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get ontology schema for the context.
        
        Parameters
        ----------
        ontology_name : str, optional
            Specific ontology name to retrieve
            
        Returns
        -------
        dict
            Ontology schema in JSON-LD format
        """
        args = {"context_id": self.context_id}
        if ontology_name:
            args["ontology_name"] = ontology_name
        
        return self._call_mcp_tool("context-broker-get-context-schema", args)
    
    def vector_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Perform vector-based semantic search.
        
        Parameters
        ----------
        query : str
            Natural language query
        top_k : int
            Number of results to return (default: 5)
            
        Returns
        -------
        dict
            Search results with semantic similarity
        """
        return self._call_mcp_tool("context-broker-vector-query", {
            "context_id": self.context_id,
            "AgentPersona": self.agent_persona,
            "query": query,
            "top_k": top_k
        })
    
    def graph_query(self, query: str, max_depth: int = 1, limit: int = 5) -> Dict[str, Any]:
        """
        Execute graph-based query to traverse relationships.
        
        Parameters
        ----------
        query : str
            Natural language query for graph search
        max_depth : int
            Maximum traversal depth (default: 1 for faster response)
        limit : int
            Maximum number of seed nodes (default: 5 for faster response)
            
        Returns
        -------
        dict
            Graph query results with relationships
        """
        return self._call_mcp_tool("context-broker-graph-query", {
            "context_id": self.context_id,
            "AgentPersona": self.agent_persona,
            "query": query,
            "max_depth": max_depth,
            "limit": limit
        })
    
    def hybrid_query(
        self,
        query: str,
        sources: Optional[List[str]] = None,
        semantic_weight: float = 0.5,
        graph_weight: float = 0.5
    ) -> Dict[str, Any]:
        """
        Combine semantic similarity and graph relationships.
        
        Parameters
        ----------
        query : str
            Natural language query
        sources : list, optional
            List of sources to query (default: ["graph", "vector"])
        semantic_weight : float
            Weight for semantic similarity (default: 0.5)
        graph_weight : float
            Weight for graph relationships (default: 0.5)
            
        Returns
        -------
        dict
            Combined search results
        """
        args = {
            "context_id": self.context_id,
            "AgentPersona": self.agent_persona,
            "query": query,
            "semantic_weight": semantic_weight,
            "graph_weight": graph_weight
        }
        
        if sources:
            args["sources"] = sources
        
        return self._call_mcp_tool("context-broker-hybrid-query", args)
    
    def get_organization_context(self) -> Dict[str, Any]:
        """
        Get organizational context using hybrid query.
        
        Queries for organization configuration, tech stack, compliance requirements,
        and naming conventions.
        
        Returns
        -------
        dict
            Organizational context data
        """
        query = """
        Retrieve organizational context including:
        - Organization name and industry
        - Technology stack (preferred languages, cloud providers, databases, architecture patterns)
        - Compliance requirements (frameworks, certifications)
        - Naming conventions (prefixes, separators)
        - Risk thresholds and indicators
        """
        
        return self.hybrid_query(query, sources=["graph", "vector"])
    
    def get_domain_knowledge(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Get domain-specific terminology and knowledge.
        
        Parameters
        ----------
        domain : str, optional
            Specific domain to query (e.g., 'healthcare', 'finance')
            
        Returns
        -------
        dict
            Domain knowledge including terminology and acronyms
        """
        query = f"Retrieve domain knowledge and terminology"
        if domain:
            query += f" for {domain} domain"
        query += " including definitions, acronyms, and glossaries"
        
        return self.vector_query(query, top_k=10)
    
    def get_standards(self, standard_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get organizational standards documents.
        
        Parameters
        ----------
        standard_type : str, optional
            Type of standard (e.g., 'coding', 'security', 'testing')
            
        Returns
        -------
        dict
            Standards documents
        """
        query = "Retrieve organizational standards"
        if standard_type:
            query += f" for {standard_type}"
        query += " including guidelines, best practices, and requirements"
        
        return self.vector_query(query, top_k=5)
    
    def get_templates(self, template_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get proposal and document templates.
        
        Parameters
        ----------
        template_type : str, optional
            Type of template (e.g., 'proposal_response', 'technical_approach')
            
        Returns
        -------
        dict
            Template documents
        """
        query = "Retrieve document templates"
        if template_type:
            query += f" for {template_type}"
        query += " including structure, sections, and content guidelines"
        
        return self.vector_query(query, top_k=3)
    
    def get_historical_rfps(self, industry: Optional[str] = None, limit: int = 5) -> Dict[str, Any]:
        """
        Get past RFP examples and outcomes.
        
        Parameters
        ----------
        industry : str, optional
            Filter by industry
        limit : int
            Maximum number of results (default: 5)
            
        Returns
        -------
        dict
            Historical RFP data
        """
        query = "Retrieve past RFP examples with outcomes and lessons learned"
        if industry:
            query += f" from {industry} industry"
        
        return self.vector_query(query, top_k=limit)
    
    def search_context(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        """
        Search across all organizational context.
        
        Parameters
        ----------
        query : str
            Search query
        top_k : int
            Maximum number of results (default: 10)
            
        Returns
        -------
        dict
            Search results across all context
        """
        return self.hybrid_query(query, sources=["graph", "vector", "scratchpad"])


def create_context_studio_client() -> Optional[ContextStudioClient]:
    """
    Create Context Studio client from environment variables.
    
    Returns
    -------
    ContextStudioClient or None
        Client instance if configuration is available, None otherwise
    """
    import os
    
    mcp_url = os.getenv("CONTEXT_STUDIO_MCP_URL")
    mcp_token = os.getenv("CONTEXT_STUDIO_MCP_TOKEN")
    api_key = os.getenv("CONTEXT_STUDIO_API_KEY")
    context_id = os.getenv("CONTEXT_STUDIO_CONTEXT_ID")
    agent_persona = os.getenv("CONTEXT_STUDIO_AGENT_PERSONA", "RFPAnalyzer")
    
    if not all([mcp_url, mcp_token, api_key, context_id]):
        log.warning(
            "context_studio_config_incomplete",
            has_url=bool(mcp_url),
            has_token=bool(mcp_token),
            has_key=bool(api_key),
            has_context_id=bool(context_id)
        )
        return None
    
    log.info("creating_context_studio_client_from_env")
    
    return ContextStudioClient(
        mcp_url=mcp_url,
        mcp_gateway_token=mcp_token,
        context_studio_key=api_key,
        context_id=context_id,
        agent_persona=agent_persona
    )

# Made with Bob
