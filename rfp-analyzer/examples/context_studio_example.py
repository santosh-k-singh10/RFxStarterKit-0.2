#!/usr/bin/env python3
"""
Example: Using Context Studio MCP Server for Organizational Context

This script demonstrates how to use the Context Studio MCP integration
to fetch organizational context dynamically instead of using local files.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from org_context.context_manager import initialize_context_manager, get_context_manager
from org_context.mcp_context_client import create_mcp_context_client


def example_1_auto_initialization():
    """
    Example 1: Auto-initialize from environment variables.
    
    This is the simplest approach - just set environment variables
    and the context manager will automatically connect to Context Studio.
    """
    print("=" * 60)
    print("Example 1: Auto-initialization from environment variables")
    print("=" * 60)
    
    # Set environment variables (normally done in .env file)
    os.environ['CONTEXT_STUDIO_ENABLED'] = 'true'
    os.environ['CONTEXT_STUDIO_MCP_URL'] = 'https://servicesessentials.ibm.com/mcp-gateway/service/gateway/servers/8ccdd203bdee4014b08e82eedb6046e2/mcp'
    os.environ['CONTEXT_STUDIO_MCP_TOKEN'] = 'your-mcp-gateway-token'
    os.environ['CONTEXT_STUDIO_API_KEY'] = 'your-context-studio-key'
    
    # Initialize context manager - it will automatically use Context Studio
    cm = initialize_context_manager()
    
    # Get organizational context
    context = cm.get_context()
    
    print(f"\nOrganization: {context.name}")
    print(f"Industry: {context.industry}")
    print(f"Tech Stack Languages: {', '.join(context.tech_stack.preferred_languages)}")
    print(f"Compliance Frameworks: {', '.join(context.compliance.frameworks)}")
    print(f"\nContext loaded from: Context Studio (MCP)")


def example_2_explicit_client():
    """
    Example 2: Create MCP client explicitly with custom configuration.
    
    Use this approach when you need more control over the MCP client
    configuration or want to use different credentials.
    """
    print("\n" + "=" * 60)
    print("Example 2: Explicit MCP client creation")
    print("=" * 60)
    
    # Create MCP client with explicit configuration
    mcp_client = create_mcp_context_client(
        mcp_url='https://servicesessentials.ibm.com/mcp-gateway/service/gateway/servers/8ccdd203bdee4014b08e82eedb6046e2/mcp',
        mcp_gateway_token='your-mcp-gateway-token',
        context_studio_key='your-context-studio-key',
        cache_ttl=600  # 10 minutes cache
    )
    
    # Initialize context manager with the client
    cm = initialize_context_manager(
        use_context_studio=True,
        mcp_client=mcp_client
    )
    
    context = cm.get_context()
    
    print(f"\nOrganization: {context.name}")
    print(f"Description: {context.description}")


def example_3_search_context():
    """
    Example 3: Search organizational context using semantic search.
    
    This demonstrates the powerful search capability available
    when using Context Studio.
    """
    print("\n" + "=" * 60)
    print("Example 3: Semantic search across context")
    print("=" * 60)
    
    cm = get_context_manager()
    
    # Search for HIPAA-related context
    results = cm.search_context(
        query="HIPAA compliance requirements",
        context_types=["standards", "domain_knowledge"],
        limit=5
    )
    
    print(f"\nSearch results for 'HIPAA compliance requirements':")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('title', 'Untitled')}")
        print(f"   Type: {result.get('type', 'Unknown')}")
        print(f"   Score: {result.get('score', 0):.2f}")
        print(f"   Excerpt: {result.get('excerpt', '')[:100]}...")


def example_4_domain_knowledge():
    """
    Example 4: Fetch domain-specific knowledge.
    
    Get terminology, acronyms, and technology information
    specific to your industry domain.
    """
    print("\n" + "=" * 60)
    print("Example 4: Fetch domain knowledge")
    print("=" * 60)
    
    cm = get_context_manager()
    
    # Get healthcare domain knowledge
    domain_knowledge = cm.get_domain_knowledge(
        domain="healthcare",
        knowledge_type="all"
    )
    
    print(f"\nDomain: Healthcare")
    
    if 'terms' in domain_knowledge:
        print(f"\nTerms ({len(domain_knowledge['terms'])}):")
        for term in domain_knowledge['terms'][:3]:
            print(f"  - {term.get('term')}: {term.get('definition', '')[:60]}...")
    
    if 'acronyms' in domain_knowledge:
        print(f"\nAcronyms ({len(domain_knowledge['acronyms'])}):")
        for acronym in domain_knowledge['acronyms'][:3]:
            print(f"  - {acronym.get('acronym')}: {acronym.get('expansion')}")


def example_5_historical_rfps():
    """
    Example 5: Get historical RFP data for context.
    
    Retrieve past RFP responses to learn from previous
    successful proposals.
    """
    print("\n" + "=" * 60)
    print("Example 5: Fetch historical RFPs")
    print("=" * 60)
    
    cm = get_context_manager()
    
    # Get historical RFPs for retail industry
    historical_rfps = cm.get_historical_rfps(
        filters={
            "industry": "Retail",
            "outcome": "won",
            "years_back": 3
        },
        limit=5
    )
    
    print(f"\nHistorical RFPs (Retail, Won, Last 3 years): {len(historical_rfps)}")
    
    for i, rfp in enumerate(historical_rfps, 1):
        print(f"\n{i}. {rfp.get('title', 'Untitled')}")
        print(f"   Client: {rfp.get('client', 'Unknown')}")
        print(f"   Value: ${rfp.get('value', 0):,.0f}")
        print(f"   Duration: {rfp.get('duration', 'Unknown')}")
        print(f"   Team Size: {rfp.get('team_size', 'Unknown')}")


def example_6_agent_context():
    """
    Example 6: Get context tailored for specific agents.
    
    Different agents need different context. This shows how
    to get agent-specific context.
    """
    print("\n" + "=" * 60)
    print("Example 6: Agent-specific context")
    print("=" * 60)
    
    cm = get_context_manager()
    
    # Get context for functional requirements agent
    functional_context = cm.get_agent_context("functional")
    
    print("\nFunctional Agent Context:")
    print(f"  Organization: {functional_context['org_name']}")
    print(f"  Tech Stack Languages: {len(functional_context['tech_stack']['preferred_languages'])}")
    print(f"  Domain Knowledge Terms: {len(functional_context.get('domain_knowledge', {}).get('terms', []))}")
    
    # Get context for compliance agent
    compliance_context = cm.get_agent_context("compliance")
    
    print("\nCompliance Agent Context:")
    print(f"  Organization: {compliance_context['org_name']}")
    print(f"  Compliance Frameworks: {len(compliance_context['compliance']['frameworks'])}")
    print(f"  Certifications: {len(compliance_context['compliance']['certifications'])}")


def example_7_reload_context():
    """
    Example 7: Reload context from Context Studio.
    
    Useful when context has been updated in Context Studio
    and you want to refresh without restarting the application.
    """
    print("\n" + "=" * 60)
    print("Example 7: Reload context from Context Studio")
    print("=" * 60)
    
    cm = get_context_manager()
    
    print("\nCurrent context:")
    context = cm.get_context()
    print(f"  Organization: {context.name}")
    
    print("\nReloading context from Context Studio...")
    cm.reload_from_context_studio()
    
    print("Context reloaded successfully!")
    context = cm.get_context()
    print(f"  Organization: {context.name}")


def example_8_fallback_behavior():
    """
    Example 8: Fallback to local files when Context Studio unavailable.
    
    Demonstrates graceful degradation when Context Studio
    is not available.
    """
    print("\n" + "=" * 60)
    print("Example 8: Fallback behavior")
    print("=" * 60)
    
    # Try Context Studio first
    print("\nAttempting to use Context Studio...")
    try:
        cm = initialize_context_manager(use_context_studio=True)
        context = cm.get_context()
        print(f"✓ Context loaded from Context Studio")
        print(f"  Organization: {context.name}")
    except Exception as e:
        print(f"✗ Context Studio unavailable: {e}")
        print("\nFalling back to local configuration...")
        
        # Fallback to local file
        cm = initialize_context_manager(
            config_path="org_context/config/org_config.yaml"
        )
        context = cm.get_context()
        print(f"✓ Context loaded from local file")
        print(f"  Organization: {context.name}")


def main():
    """Run all examples."""
    print("\n" + "=" * 60)
    print("Context Studio MCP Integration Examples")
    print("=" * 60)
    
    try:
        # Run examples
        example_1_auto_initialization()
        example_2_explicit_client()
        example_3_search_context()
        example_4_domain_knowledge()
        example_5_historical_rfps()
        example_6_agent_context()
        example_7_reload_context()
        example_8_fallback_behavior()
        
        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

# Made with Bob
