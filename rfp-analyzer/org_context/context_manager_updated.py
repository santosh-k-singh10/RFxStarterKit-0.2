"""
Updated _load_from_context_studio method for context_manager.py

Replace the existing method with this implementation.
"""

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

# Made with Bob
