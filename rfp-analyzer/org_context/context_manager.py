"""
org_context/context_manager.py
-------------------------------
Central manager for organizational context.

Handles loading, validation, caching, and providing context
to various components of the RFP analyzer.

Supports multiple context sources:
- Local YAML/JSON files
- Remote URLs (SharePoint, OneDrive, Box, HTTP, S3)
- IBM ICA Context Studio via MCP
"""

from __future__ import annotations

import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, TYPE_CHECKING
from urllib.parse import urlparse
import structlog

from .context_schema import OrganizationContext

if TYPE_CHECKING:
    from .context_studio_client import ContextStudioClient

log = structlog.get_logger(__name__)


class ContextManager:
    """
    Manages organizational context throughout the RFP analysis lifecycle.
    
    Responsibilities:
    - Load context from YAML/JSON configuration files
    - Validate context against schemas
    - Provide context to agents and other components
    - Cache context for performance
    - Support hot-reloading of context updates
    """
    
    def __init__(
        self,
        config_path: Optional[str | Path] = None,
        use_context_studio: bool = False,
        mcp_client: Optional['ContextStudioClient'] = None
    ):
        """
        Initialize the context manager.
        
        Parameters
        ----------
        config_path : str | Path | None
            Path to the organization configuration file (YAML or JSON).
            If None and not using Context Studio, uses default context.
        use_context_studio : bool
            If True, fetch context from Context Studio via MCP
        mcp_client : ContextStudioClient | None
            MCP client for Context Studio server. If None and use_context_studio
            is True, will create client from environment variables.
        """
        self._context: Optional[OrganizationContext] = None
        self._config_path: Optional[Path] = None
        self._use_context_studio = use_context_studio
        self._mcp_client = mcp_client
        
        if use_context_studio:
            if mcp_client is None:
                # Create Context Studio client from environment variables
                try:
                    from .context_studio_client import create_context_studio_client
                    self._mcp_client = create_context_studio_client()
                    if self._mcp_client:
                        log.info("context_studio_client_created_from_env")
                    else:
                        log.warning("context_studio_client_not_configured")
                        self._use_context_studio = False
                except Exception as e:
                    log.error("failed_to_create_context_studio_client", error=str(e))
                    log.warning("falling_back_to_local_context")
                    self._use_context_studio = False
            
            if self._use_context_studio:
                self._load_from_context_studio()
        elif config_path:
            self.load_context(config_path)
        else:
            self._context = self._create_default_context()
            log.info("context_manager_initialized", mode="default")
    
    def load_context(
        self,
        config_path: str | Path,
        remote_kwargs: Optional[Dict[str, Any]] = None
    ) -> OrganizationContext:
        """
        Load organizational context from a configuration file or remote URL.
        
        Parameters
        ----------
        config_path : str | Path
            Path to YAML or JSON configuration file, or remote URL
            (SharePoint, OneDrive, Box, HTTP, S3)
        remote_kwargs : dict, optional
            Additional parameters for remote loaders (credentials, etc.)
            
        Returns
        -------
        OrganizationContext
            Loaded and validated context
            
        Raises
        ------
        FileNotFoundError
            If config file doesn't exist
        ValueError
            If config file is invalid or cannot be parsed
        """
        # Check if it's a remote URL
        config_str = str(config_path)
        parsed = urlparse(config_str)
        
        if parsed.scheme in ('http', 'https', 's3') or any(
            domain in parsed.netloc
            for domain in ['sharepoint.com', 'onedrive', '1drv.ms', 'box.com']
        ):
            # Load from remote
            log.info("detected_remote_url", url=config_str, scheme=parsed.scheme)
            try:
                from .remote_loaders import load_remote_context
                config_path = load_remote_context(config_str, **(remote_kwargs or {}))
                log.info("remote_context_downloaded", local_path=str(config_path))
            except ImportError as e:
                raise ImportError(
                    f"Remote context loading requires additional dependencies. "
                    f"See org_context/remote_loaders.py for details. Error: {e}"
                )
        else:
            config_path = Path(config_path)
            
            if not config_path.exists():
                raise FileNotFoundError(f"Context config not found: {config_path}")
        
        self._config_path = config_path
        
        log.info("loading_context", path=str(config_path))
        
        try:
            # Load file based on extension
            if config_path.suffix in ('.yaml', '.yml'):
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
            elif config_path.suffix == '.json':
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
            else:
                raise ValueError(f"Unsupported config format: {config_path.suffix}")
            
            # Set context root to config file's parent directory
            if 'context_root' not in config_data:
                config_data['context_root'] = str(config_path.parent)
            
            # Set default subdirectories if not specified
            context_root = Path(config_data['context_root'])
            if 'templates_dir' not in config_data:
                config_data['templates_dir'] = str(context_root / 'templates')
            if 'standards_dir' not in config_data:
                config_data['standards_dir'] = str(context_root / 'standards')
            if 'examples_dir' not in config_data:
                config_data['examples_dir'] = str(context_root / 'examples')
            
            # Parse and validate with Pydantic
            self._context = OrganizationContext(**config_data)
            
            log.info(
                "context_loaded_successfully",
                org_name=self._context.name,
                industry=self._context.industry,
                compliance_frameworks=len(self._context.compliance.frameworks),
                tech_stack_languages=len(self._context.tech_stack.preferred_languages),
            )
            
            return self._context
            
        except yaml.YAMLError as e:
            log.error("yaml_parse_error", error=str(e), path=str(config_path))
            raise ValueError(f"Invalid YAML in config file: {e}")
        except json.JSONDecodeError as e:
            log.error("json_parse_error", error=str(e), path=str(config_path))
            raise ValueError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            log.error("context_load_error", error=str(e), path=str(config_path))
            raise ValueError(f"Failed to load context: {e}")
    
    def reload_context(self) -> OrganizationContext:
        """
        Reload context from the original config file.
        
        Useful for hot-reloading after configuration changes.
        
        Returns
        -------
        OrganizationContext
            Reloaded context
            
        Raises
        ------
        RuntimeError
            If no config path is set (using default context)
        """
        if not self._config_path:
            raise RuntimeError("Cannot reload: no config file path set")
        
        log.info("reloading_context", path=str(self._config_path))
        return self.load_context(self._config_path)
    
    def get_context(self) -> OrganizationContext:
        """
        Get the current organizational context.
        
        Returns
        -------
        OrganizationContext
            Current context (default if none loaded)
        """
        if self._context is None:
            self._context = self._create_default_context()
        
        return self._context
    
    def _load_from_context_studio(self):
        """
        Load context from Context Studio via MCP.
        
        Fetches organizational context from Context Studio MCP server
        and creates OrganizationContext object.
        """
        if not self._mcp_client:
            log.error("mcp_client_not_available")
            self._context = self._create_default_context()
            return
        
        try:
            log.info("loading_context_from_studio")
            
            # Fetch data from Context Studio using vector queries
            # Query for organizational information
            org_query_result = self._mcp_client.vector_query(
                "organization name, industry, company information",
                top_k=3
            )
            
            # Query for tech stack
            tech_query_result = self._mcp_client.vector_query(
                "technology stack, programming languages, cloud providers, databases, architecture patterns",
                top_k=5
            )
            
            # Query for compliance
            compliance_query_result = self._mcp_client.vector_query(
                "compliance frameworks, certifications, regulatory requirements",
                top_k=5
            )
            
            # Parse and transform Context Studio responses
            from .context_studio_parser import parse_context_studio_responses
            context_data = parse_context_studio_responses(
                org_query_result,
                tech_query_result,
                compliance_query_result
            )
            
            # Create OrganizationContext from parsed data
            self._context = OrganizationContext(**context_data)
            
            # Log detailed context information
            log.info(
                "context_loaded_from_studio",
                org_name=self._context.name,
                industry=self._context.industry,
                compliance_frameworks=len(self._context.compliance.frameworks),
                tech_stack_languages=len(self._context.tech_stack.preferred_languages),
            )
            
            # Log what will be used in prompts
            print("\n" + "="*60)
            print("✓ CONNECTED TO IBM ICA CONTEXT STUDIO")
            print("="*60)
            print(f"Organization: {self._context.name}")
            print(f"Industry: {self._context.industry}")
            print(f"\nTech Stack (will be used in prompts):")
            print(f"  Languages: {', '.join(self._context.tech_stack.preferred_languages[:5])}")
            print(f"  Cloud: {', '.join(self._context.tech_stack.cloud_providers)}")
            print(f"  Databases: {', '.join(self._context.tech_stack.databases[:3])}")
            print(f"\nCompliance Requirements (will be used in prompts):")
            print(f"  Frameworks: {', '.join(self._context.compliance.frameworks)}")
            print(f"\nNaming Conventions (will be used in prompts):")
            print(f"  Functional: {self._context.naming_conventions.functional_prefix}")
            print(f"  Non-Functional: {self._context.naming_conventions.non_functional_prefix}")
            print(f"  Compliance: {self._context.naming_conventions.compliance_prefix}")
            print("="*60 + "\n")
            
        except Exception as e:
            log.error("failed_to_load_from_studio", error=str(e))
            log.warning("falling_back_to_default_context")
            self._context = self._create_default_context()
    
    def _create_default_context(self) -> OrganizationContext:
        """
        Create a default organizational context.
        
        Used when no configuration file is provided or when Context Studio fails.
        
        Returns
        -------
        OrganizationContext
            Default context with sensible defaults
        """
        log.info("creating_default_context")
        
        return OrganizationContext(
            name="Default Organization",
            industry="Technology",
            description="Default organizational context for RFP analysis"
        )
    
    def reload_from_context_studio(self) -> OrganizationContext:
        """
        Reload context from Context Studio.
        
        Useful for refreshing context after updates in Context Studio.
        
        Returns
        -------
        OrganizationContext
            Reloaded context
            
        Raises
        ------
        RuntimeError
            If not using Context Studio mode
        """
        if not self._use_context_studio:
            raise RuntimeError("Cannot reload from Context Studio: not in Context Studio mode")
        
        if self._mcp_client and hasattr(self._mcp_client, '_cache'):
            # Clear MCP client cache to force fresh fetch
            self._mcp_client._cache.clear()
        
        log.info("reloading_context_from_studio")
        self._load_from_context_studio()
        
        if self._context is None:
            self._context = self._create_default_context()
        
        return self._context
    
    def search_context(
        self,
        query: str,
        top_k: int = 10
    ) -> Dict[str, Any]:
        """
        Search organizational context using semantic search.
        
        Only available when using Context Studio mode.
        
        Parameters
        ----------
        query : str
            Search query
        top_k : int
            Maximum results to return
            
        Returns
        -------
        dict
            Search results with relevance scores
            
        Raises
        ------
        RuntimeError
            If not using Context Studio mode
        """
        if not self._use_context_studio or not self._mcp_client:
            raise RuntimeError("Search only available in Context Studio mode")
        
        log.info("searching_context", query=query, top_k=top_k)
        return self._mcp_client.search_context(query, top_k=top_k)
    
    def get_domain_knowledge(
        self,
        domain: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get domain-specific knowledge from Context Studio.
        
        Only available when using Context Studio mode.
        
        Parameters
        ----------
        domain : str, optional
            Domain name
            
        Returns
        -------
        dict
            Domain knowledge data
            
        Raises
        ------
        RuntimeError
            If not using Context Studio mode
        """
        if not self._use_context_studio or not self._mcp_client:
            raise RuntimeError("Domain knowledge only available in Context Studio mode")
        
        log.info("fetching_domain_knowledge", domain=domain)
        return self._mcp_client.get_domain_knowledge(domain)
    
    def get_historical_rfps(
        self,
        industry: Optional[str] = None,
        limit: int = 5
    ) -> Dict[str, Any]:
        """
        Get historical RFP data from Context Studio.
        
        Only available when using Context Studio mode.
        
        Parameters
        ----------
        industry : str, optional
            Filter by industry
        limit : int
            Maximum RFPs to return
            
        Returns
        -------
        dict
            Historical RFP data
            
        Raises
        ------
        RuntimeError
            If not using Context Studio mode
        """
        if not self._use_context_studio or not self._mcp_client:
            raise RuntimeError("Historical RFPs only available in Context Studio mode")
        
        log.info("fetching_historical_rfps", industry=industry, limit=limit)
        return self._mcp_client.get_historical_rfps(industry, limit)
    
    def get_agent_context(self, agent_type: str) -> dict:
        """
        Get context relevant to a specific agent type.
        
        Parameters
        ----------
        agent_type : str
            Type of agent: "functional", "non_functional", "compliance", 
            "ambiguity", "risk"
            
        Returns
        -------
        dict
            Context dictionary tailored for the agent
        """
        context = self.get_context()
        
        base_context = {
            "org_name": context.name,
            "industry": context.industry,
            "naming_conventions": context.naming_conventions.model_dump(),
            "priority_mapping": context.priority_mapping.model_dump(),
        }
        
        if agent_type == "functional":
            return {
                **base_context,
                "tech_stack": context.tech_stack.model_dump(),
                "domain_knowledge": context.domain_knowledge.model_dump(),
            }
        
        elif agent_type == "non_functional":
            return {
                **base_context,
                "tech_stack": context.tech_stack.model_dump(),
                "risk_thresholds": context.risk_thresholds.model_dump(),
            }
        
        elif agent_type == "compliance":
            return {
                **base_context,
                "compliance": context.compliance.model_dump(),
                "domain_knowledge": context.domain_knowledge.model_dump(),
            }
        
        elif agent_type == "ambiguity":
            return {
                **base_context,
                "domain_knowledge": context.domain_knowledge.model_dump(),
            }
        
        elif agent_type == "risk":
            return {
                **base_context,
                "risk_thresholds": context.risk_thresholds.model_dump(),
                "tech_stack": context.tech_stack.model_dump(),
            }
        
        else:
            return base_context
    
    def get_prompt_context(self, agent_type: str) -> str:
        """
        Get formatted context string for inclusion in agent prompts.
        
        Parameters
        ----------
        agent_type : str
            Type of agent
            
        Returns
        -------
        str
            Formatted context string for prompt injection
        """
        agent_context = self.get_agent_context(agent_type)
        context = self.get_context()
        
        # Log what context is being injected into prompts
        context_source = "IBM ICA Context Studio (MCP)" if self._mcp_client else "Local Files"
        log.info(
            "injecting_context_into_agent_prompt",
            agent_type=agent_type,
            org_name=context.name,
            context_source=context_source
        )
        
        print(f"\n📋 Injecting context into {agent_type.upper()} agent prompt:")
        print(f"   Source: {context_source}")
        print(f"   Organization: {context.name}")
        if agent_type == "functional":
            print(f"   Tech Stack: {', '.join(context.tech_stack.preferred_languages[:3])}")
        elif agent_type == "compliance":
            print(f"   Compliance: {', '.join(context.compliance.frameworks)}")
        elif agent_type in ("risk", "non_functional"):
            print(f"   Risk Indicators: {len(context.risk_thresholds.high_complexity_indicators)} complexity, {len(context.risk_thresholds.timeline_red_flags)} timeline")
        
        lines = [
            f"ORGANIZATIONAL CONTEXT:",
            f"Organization: {context.name}",
            f"Industry: {context.industry}",
            "",
        ]
        
        if agent_type == "functional":
            lines.extend([
                "TECHNOLOGY PREFERENCES:",
                f"- Languages: {', '.join(context.tech_stack.preferred_languages) or 'Not specified'}",
                f"- Cloud: {', '.join(context.tech_stack.cloud_providers) or 'Not specified'}",
                f"- Databases: {', '.join(context.tech_stack.databases) or 'Not specified'}",
                f"- Architecture: {', '.join(context.tech_stack.architecture_patterns) or 'Not specified'}",
                "",
            ])
        
        if agent_type == "compliance":
            lines.extend([
                "COMPLIANCE REQUIREMENTS:",
                f"- Frameworks: {', '.join(context.compliance.frameworks) or 'None specified'}",
                f"- Certifications: {', '.join(context.compliance.certifications) or 'None specified'}",
                "",
            ])
        
        if agent_type in ("risk", "non_functional"):
            lines.extend([
                "RISK INDICATORS:",
                f"- High complexity: {', '.join(context.risk_thresholds.high_complexity_indicators[:3])}...",
                f"- Timeline risks: {', '.join(context.risk_thresholds.timeline_red_flags[:3])}...",
                "",
            ])
        
        lines.extend([
            "NAMING CONVENTION:",
            f"- Use prefix: {context.naming_conventions.functional_prefix if agent_type == 'functional' else context.naming_conventions.requirement_prefix}",
            f"- Format: PREFIX{context.naming_conventions.separator}NNN",
            "",
            "PRIORITY DETECTION:",
            f"- MUST: {', '.join(context.priority_mapping.must_keywords[:3])}...",
            f"- SHOULD: {', '.join(context.priority_mapping.should_keywords[:3])}...",
            "",
        ])
        
        return "\n".join(lines)
    
    def validate_requirement_id(self, req_id: str, category: str) -> bool:
        """
        Validate if a requirement ID follows organizational conventions.
        
        Parameters
        ----------
        req_id : str
            Requirement ID to validate
        category : str
            Expected category
            
        Returns
        -------
        bool
            True if ID follows conventions
        """
        context = self.get_context()
        
        prefix_map = {
            "functional": context.naming_conventions.functional_prefix,
            "non_functional": context.naming_conventions.non_functional_prefix,
            "compliance": context.naming_conventions.compliance_prefix,
            "ambiguity": context.naming_conventions.ambiguity_prefix,
            "risk": context.naming_conventions.risk_prefix,
        }
        
        expected_prefix = prefix_map.get(category, context.naming_conventions.requirement_prefix)
        separator = context.naming_conventions.separator
        
        return req_id.startswith(f"{expected_prefix}{separator}")
    
    def export_context_summary(self) -> dict:
        """
        Export a summary of the current context for logging/debugging.
        
        Returns
        -------
        dict
            Summary of context configuration
        """
        context = self.get_context()
        
        return {
            "organization": {
                "name": context.name,
                "industry": context.industry,
            },
            "tech_stack": {
                "languages": len(context.tech_stack.preferred_languages),
                "cloud_providers": len(context.tech_stack.cloud_providers),
                "databases": len(context.tech_stack.databases),
            },
            "compliance": {
                "frameworks": len(context.compliance.frameworks),
                "certifications": len(context.compliance.certifications),
            },
            "output_preferences": {
                "cost_estimates": context.output_preferences.include_cost_estimates,
                "timeline_estimates": context.output_preferences.include_timeline_estimates,
                "team_sizing": context.output_preferences.include_team_sizing,
                "custom_sections": len(context.output_preferences.custom_sections),
            },
            "paths": {
                "context_root": str(context.context_root) if context.context_root else None,
                "templates_dir": str(context.templates_dir) if context.templates_dir else None,
                "standards_dir": str(context.standards_dir) if context.standards_dir else None,
            }
        }


# Global context manager instance (singleton pattern)
_global_context_manager: Optional[ContextManager] = None


def get_context_manager() -> ContextManager:
    """
    Get the global context manager instance.
    
    Returns
    -------
    ContextManager
        Global context manager (creates if doesn't exist)
    """
    global _global_context_manager
    
    if _global_context_manager is None:
        _global_context_manager = ContextManager()
    
    return _global_context_manager


def initialize_context_manager(
    config_path: Optional[str | Path] = None,
    remote_kwargs: Optional[Dict[str, Any]] = None,
    use_context_studio: Optional[bool] = None,
    mcp_client: Optional['ContextStudioClient'] = None
) -> ContextManager:
    """
    Initialize the global context manager with a configuration file, remote URL, or Context Studio.
    
    Parameters
    ----------
    config_path : str | Path | None
        Path to configuration file or remote URL
        (SharePoint, OneDrive, Box, HTTP, S3)
    remote_kwargs : dict, optional
        Additional parameters for remote loaders (credentials, etc.)
    use_context_studio : bool, optional
        If True, use Context Studio via MCP. If None, checks CONTEXT_STUDIO_ENABLED env var.
    mcp_client : ContextStudioClient, optional
        Pre-configured MCP client. If None, creates from environment variables.
        
    Returns
    -------
    ContextManager
        Initialized context manager
        
    Examples
    --------
    # Context Studio (from environment variables)
    initialize_context_manager(use_context_studio=True)
    
    # Context Studio (with explicit client)
    from org_context.context_studio_client import create_context_studio_client
    client = create_context_studio_client(...)
    initialize_context_manager(use_context_studio=True, mcp_client=client)
    
    # Local file
    initialize_context_manager("org_context/config/org_config.yaml")
    
    # SharePoint
    initialize_context_manager(
        "https://company.sharepoint.com/sites/team/Shared Documents/org_config.yaml",
        remote_kwargs={
            "client_id": "...",
            "client_secret": "...",
            "tenant_id": "..."
        }
    )
    
    # OneDrive
    initialize_context_manager(
        "https://company-my.sharepoint.com/personal/user/Documents/org_config.yaml",
        remote_kwargs={"access_token": "..."}
    )
    
    # HTTP with auth
    initialize_context_manager(
        "https://config.company.com/org_config.yaml",
        remote_kwargs={"auth": ("username", "password")}
    )
    """
    global _global_context_manager
    
    # Check environment variable if use_context_studio not explicitly set
    if use_context_studio is None:
        import os
        use_context_studio = os.getenv('CONTEXT_STUDIO_ENABLED', 'false').lower() == 'true'
    
    if use_context_studio:
        # Initialize with Context Studio
        _global_context_manager = ContextManager(
            use_context_studio=True,
            mcp_client=mcp_client
        )
    elif config_path:
        # Initialize with config file
        _global_context_manager = ContextManager()
        _global_context_manager.load_context(config_path, remote_kwargs)
    else:
        # Initialize with default context
        _global_context_manager = ContextManager()
    
    return _global_context_manager

# Made with Bob