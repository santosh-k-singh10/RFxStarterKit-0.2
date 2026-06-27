"""
org_context/mcp_context_client.py
----------------------------------
MCP client for fetching organizational context from Context Studio MCP server.

This module provides a high-level interface to interact with the Context Studio
MCP server hosted on IBM ICA.
"""

from __future__ import annotations

import json
import os
from typing import Dict, Any, Optional, List
import structlog
import httpx
from datetime import datetime, timedelta

log = structlog.get_logger(__name__)


class MCPContextClient:
    """
    Client for interacting with Context Studio MCP server.
    
    This client connects to the Context Studio MCP server hosted on IBM ICA
    and provides methods to fetch organizational context data.
    """
    
    def __init__(
        self,
        mcp_url: str,
        mcp_gateway_token: str,
        context_studio_key: str,
        cache_ttl: int = 300  # 5 minutes default
    ):
        """
        Initialize MCP Context Client.
        
        Parameters
        ----------
        mcp_url : str
            URL of the MCP gateway server
        mcp_gateway_token : str
            Bearer token for MCP gateway authentication
        context_studio_key : str
            API key for Context Studio
        cache_ttl : int
            Cache time-to-live in seconds (default: 300)
        """
        self.mcp_url = mcp_url.rstrip('/')
        self.headers = {
            'Authorization': f'Bearer {mcp_gateway_token}',
            'x-api-key': context_studio_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, tuple[Any, datetime]] = {}
        
        log.info(
            "mcp_context_client_initialized",
            mcp_url=mcp_url,
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
    
    def _call_mcp_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call an MCP tool on the Context Studio server.
        
        Parameters
        ----------
        tool_name : str
            Name of the MCP tool to call
        arguments : dict
            Arguments to pass to the tool
            
        Returns
        -------
        dict
            Tool response data
            
        Raises
        ------
        Exception
            If the MCP call fails
        """
        cache_key = f"{tool_name}:{json.dumps(arguments, sort_keys=True)}"
        
        # Check cache first
        cached_result = self._get_from_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        # Make MCP call using JSON-RPC 2.0 format
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
                    # Extract content from MCP response
                    mcp_result = result['result']
                    
                    if 'content' in mcp_result and len(mcp_result['content']) > 0:
                        content = mcp_result['content'][0]
                        if content.get('type') == 'text':
                            data = json.loads(content['text'])
                            
                            # Cache the result
                            self._set_cache(cache_key, data)
                            
                            log.info("mcp_tool_success", tool=tool_name)
                            return data
                    
                    # If result is directly the data (not wrapped in content)
                    if isinstance(mcp_result, dict) and 'content' not in mcp_result:
                        self._set_cache(cache_key, mcp_result)
                        log.info("mcp_tool_success", tool=tool_name)
                        return mcp_result
                
                elif 'error' in result:
                    error_msg = result['error'].get('message', 'Unknown error')
                    raise ValueError(f"MCP error: {error_msg}")
                
                raise ValueError(f"Unexpected MCP response format: {result}")
                
        except httpx.HTTPError as e:
            log.error("mcp_http_error", tool=tool_name, error=str(e))
            raise Exception(f"Failed to call MCP tool {tool_name}: {e}")
        except json.JSONDecodeError as e:
            log.error("mcp_json_error", tool=tool_name, error=str(e))
            raise Exception(f"Failed to parse MCP response for {tool_name}: {e}")
        except Exception as e:
            log.error("mcp_call_error", tool=tool_name, error=str(e))
            raise
    
    def get_organization_context(
        self,
        organization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch complete organizational configuration from Context Studio.
        
        Parameters
        ----------
        organization_id : str, optional
            Organization identifier (uses default if not provided)
            
        Returns
        -------
        dict
            Organization context including tech stack, compliance, naming conventions
        """
        arguments = {}
        if organization_id:
            arguments['organization_id'] = organization_id
        
        return self._call_mcp_tool('get_organization_context', arguments)
    
    def get_domain_knowledge(
        self,
        domain: Optional[str] = None,
        knowledge_type: str = 'all'
    ) -> Dict[str, Any]:
        """
        Fetch domain-specific terminology and knowledge.
        
        Parameters
        ----------
        domain : str, optional
            Domain name (e.g., 'healthcare', 'retail')
        knowledge_type : str
            Type of knowledge: 'terms', 'acronyms', 'technologies', 'vendors', 'all'
            
        Returns
        -------
        dict
            Domain knowledge data
        """
        arguments = {'knowledge_type': knowledge_type}
        if domain:
            arguments['domain'] = domain
        
        return self._call_mcp_tool('get_domain_knowledge', arguments)
    
    def get_standards_document(
        self,
        standard_type: str,
        standard_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch organizational standards documents.
        
        Parameters
        ----------
        standard_type : str
            Type of standard: 'coding', 'security', 'compliance', 'all'
        standard_id : str, optional
            Specific standard ID
            
        Returns
        -------
        dict
            Standards document data
        """
        arguments = {'standard_type': standard_type}
        if standard_id:
            arguments['standard_id'] = standard_id
        
        return self._call_mcp_tool('get_standards_document', arguments)
    
    def get_template(
        self,
        template_type: str,
        template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch document templates.
        
        Parameters
        ----------
        template_type : str
            Type of template: 'proposal_response', 'technical_spec', 'sow', 'all'
        template_id : str, optional
            Specific template ID
            
        Returns
        -------
        dict
            Template data
        """
        arguments = {'template_type': template_type}
        if template_id:
            arguments['template_id'] = template_id
        
        return self._call_mcp_tool('get_template', arguments)
    
    def get_historical_rfps(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical RFP data for context.
        
        Parameters
        ----------
        filters : dict, optional
            Filters to apply (industry, technology, outcome, years_back)
        limit : int
            Maximum number of RFPs to return
            
        Returns
        -------
        list
            List of historical RFP data
        """
        arguments = {'limit': limit}
        if filters:
            arguments['filters'] = filters
        
        result = self._call_mcp_tool('get_historical_rfps', arguments)
        
        # Result should be a list
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and 'rfps' in result:
            return result['rfps']
        else:
            log.warning("unexpected_historical_rfps_format", result=result)
            return []
    
    def search_context(
        self,
        query: str,
        context_types: Optional[List[str]] = None,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Semantic search across all context types.
        
        Parameters
        ----------
        query : str
            Search query
        context_types : list, optional
            Types to search: ['organization', 'domain_knowledge', 'standards', 
                             'templates', 'historical_rfps']
        limit : int
            Maximum number of results
            
        Returns
        -------
        list
            Search results with relevance scores
        """
        arguments = {
            'query': query,
            'limit': limit
        }
        if context_types:
            arguments['context_types'] = context_types
        
        result = self._call_mcp_tool('search_context', arguments)
        
        # Result should be a list
        if isinstance(result, list):
            return result
        elif isinstance(result, dict) and 'results' in result:
            return result['results']
        else:
            log.warning("unexpected_search_results_format", result=result)
            return []
    
    def clear_cache(self):
        """Clear all cached data."""
        self._cache.clear()
        log.info("cache_cleared")


def create_mcp_context_client(
    mcp_url: Optional[str] = None,
    mcp_gateway_token: Optional[str] = None,
    context_studio_key: Optional[str] = None,
    cache_ttl: Optional[int] = None
) -> MCPContextClient:
    """
    Factory function to create MCP Context Client from environment variables.
    
    Parameters
    ----------
    mcp_url : str, optional
        MCP gateway URL (defaults to CONTEXT_STUDIO_MCP_URL env var)
    mcp_gateway_token : str, optional
        MCP gateway token (defaults to CONTEXT_STUDIO_MCP_TOKEN env var)
    context_studio_key : str, optional
        Context Studio API key (defaults to CONTEXT_STUDIO_API_KEY env var)
    cache_ttl : int, optional
        Cache TTL in seconds (defaults to CONTEXT_STUDIO_CACHE_TTL env var or 300)
        
    Returns
    -------
    MCPContextClient
        Configured MCP context client
        
    Raises
    ------
    ValueError
        If required credentials are not provided
    """
    mcp_url = mcp_url or os.getenv('CONTEXT_STUDIO_MCP_URL')
    mcp_gateway_token = mcp_gateway_token or os.getenv('CONTEXT_STUDIO_MCP_TOKEN')
    context_studio_key = context_studio_key or os.getenv('CONTEXT_STUDIO_API_KEY')
    cache_ttl = cache_ttl or int(os.getenv('CONTEXT_STUDIO_CACHE_TTL', '300'))
    
    if not mcp_url:
        raise ValueError("MCP URL not provided. Set CONTEXT_STUDIO_MCP_URL environment variable.")
    if not mcp_gateway_token:
        raise ValueError("MCP gateway token not provided. Set CONTEXT_STUDIO_MCP_TOKEN environment variable.")
    if not context_studio_key:
        raise ValueError("Context Studio API key not provided. Set CONTEXT_STUDIO_API_KEY environment variable.")
    
    return MCPContextClient(
        mcp_url=mcp_url,
        mcp_gateway_token=mcp_gateway_token,
        context_studio_key=context_studio_key,
        cache_ttl=cache_ttl
    )


# Example usage
if __name__ == "__main__":
    # Create client from environment variables
    client = create_mcp_context_client()
    
    # Fetch organization context
    org_context = client.get_organization_context()
    print(f"Organization: {org_context.get('name')}")
    print(f"Industry: {org_context.get('industry')}")
    
    # Search context
    results = client.search_context("HIPAA compliance")
    print(f"\nSearch results: {len(results)}")
    for result in results:
        print(f"  - {result.get('title')} (score: {result.get('score')})")

# Made with Bob