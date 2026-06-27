"""
app/services/claude_service.py
-------------------------------
Service layer for Claude API calls (architecture & solution mapping).
"""

import os
import json
from typing import List, Dict, Any, Optional
import structlog
import anthropic

log = structlog.get_logger(__name__)

# System prompts
ARCHITECTURE_PROMPT = """You are a solution architect. Given the following accepted requirements from an RFP, generate a Mermaid.js architecture diagram using graph TD syntax.

Include:
- User-facing layers
- Backend services
- Databases
- Integrations
- Security boundaries

Label each node with the req_id it satisfies where relevant.

Output ONLY the raw Mermaid code starting with 'graph TD'. No explanation, no markdown fences."""

COMPONENTS_PROMPT = """You are a solution architect. Given these requirements, return a JSON array of system components.

Each object must have exactly these fields:
{
  "name": "Component Name",
  "type": "frontend|backend|database|integration|infrastructure|security",
  "description": "What this component does",
  "related_req_ids": ["FR-001", "NFR-003"]
}

Output ONLY valid JSON. No preamble, no explanation."""

SOLUTION_MAPPING_PROMPT = """You are an enterprise architect. Map each of the following requirements to the best-fit solution from this list: {solutions}.

For each requirement return:
{{
  "req_id": "FR-001",
  "best_fit_solution": "SAP S/4HANA",
  "coverage": "native|configuration|customisation|gap",
  "module": "Specific module/feature name",
  "rationale": "Why this solution fits"
}}

coverage must be exactly one of: native | configuration | customisation | gap

Output ONLY a valid JSON array. No preamble."""


async def generate_architecture_diagram(requirements: List[Dict]) -> str:
    """
    Generate Mermaid diagram from requirements.
    
    Args:
        requirements: List of requirement dicts
    
    Returns:
        Mermaid diagram code
    """
    log.info("architecture_diagram_start", count=len(requirements))
    
    # Filter to accepted requirements only
    accepted_reqs = [
        r for r in requirements 
        if r.get('review_status') in ['accepted', 'modified']
    ]
    
    if not accepted_reqs:
        log.warning("no_accepted_requirements_for_architecture")
        return "graph TD\n  A[No accepted requirements]"
    
    # Build requirement text
    req_text = "\n".join([
        f"- [{r['id']}] {r['title']}: {r['description']}"
        for r in accepted_reqs[:50]  # Limit to 50 to avoid token limits
    ])
    
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": f"{ARCHITECTURE_PROMPT}\n\nRequirements:\n{req_text}"
            }]
        )
        
        diagram = message.content[0].text
        log.info("architecture_diagram_generated", length=len(diagram))
        return diagram
        
    except Exception as e:
        log.error("architecture_diagram_error", error=str(e))
        raise


async def identify_components(requirements: List[Dict]) -> List[Dict]:
    """
    Identify system components from requirements.
    
    Args:
        requirements: List of requirement dicts
    
    Returns:
        List of component dicts
    """
    log.info("components_identification_start", count=len(requirements))
    
    # Filter to accepted requirements only
    accepted_reqs = [
        r for r in requirements 
        if r.get('review_status') in ['accepted', 'modified']
    ]
    
    if not accepted_reqs:
        log.warning("no_accepted_requirements_for_components")
        return []
    
    # Build requirement text
    req_text = "\n".join([
        f"- [{r['id']}] {r['title']}: {r['description']}"
        for r in accepted_reqs[:50]  # Limit to 50
    ])
    
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{
                "role": "user",
                "content": f"{COMPONENTS_PROMPT}\n\nRequirements:\n{req_text}"
            }]
        )
        
        components = json.loads(message.content[0].text)
        log.info("components_identified", count=len(components))
        return components
        
    except Exception as e:
        log.error("components_identification_error", error=str(e))
        raise


async def map_to_solutions(requirements: List[Dict], solutions: List[str]) -> Dict:
    """
    Map requirements to target solutions.
    
    Args:
        requirements: List of requirement dicts
        solutions: List of solution names to evaluate
    
    Returns:
        Dict with mapping and summary
    """
    log.info("solution_mapping_start", 
            requirements_count=len(requirements),
            solutions=solutions)
    
    # Filter to accepted requirements only
    accepted_reqs = [
        r for r in requirements 
        if r.get('review_status') in ['accepted', 'modified']
    ]
    
    if not accepted_reqs:
        log.warning("no_accepted_requirements_for_solution_mapping")
        return {"mapping": [], "summary": {}}
    
    # Build requirement text
    req_text = "\n".join([
        f"- [{r['id']}] {r['title']}: {r['description']}"
        for r in accepted_reqs[:100]  # Can handle more for solution mapping
    ])
    
    try:
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        prompt = SOLUTION_MAPPING_PROMPT.format(solutions=", ".join(solutions))
        
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=8000,
            messages=[{
                "role": "user",
                "content": f"{prompt}\n\nRequirements:\n{req_text}"
            }]
        )
        
        mapping = json.loads(message.content[0].text)
        
        # Generate summary
        summary = {}
        for solution in solutions:
            summary[solution] = {
                "native": 0,
                "configuration": 0,
                "customisation": 0,
                "gap": 0
            }
        
        for item in mapping:
            solution = item.get("best_fit_solution", "")
            coverage = item.get("coverage", "gap")
            if solution in summary:
                summary[solution][coverage] += 1
        
        log.info("solution_mapping_complete", 
                mapped_count=len(mapping),
                solutions_evaluated=len(solutions))
        
        return {
            "mapping": mapping,
            "summary": summary
        }
        
    except Exception as e:
        log.error("solution_mapping_error", error=str(e))
        raise