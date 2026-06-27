"""
org_context/context_studio_parser.py
------------------------------------
Parser for Context Studio responses.

Transforms Context Studio vector query results (JSON-LD format)
into OrganizationContext format.
"""

import json
from typing import Dict, Any, List, Set
import structlog

log = structlog.get_logger(__name__)


def parse_context_studio_responses(
    org_result: Dict[str, Any],
    tech_result: Dict[str, Any],
    compliance_result: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Parse Context Studio vector query responses and transform to OrganizationContext format.
    
    Parameters
    ----------
    org_result : dict
        Organization query result from Context Studio
    tech_result : dict
        Technology stack query result from Context Studio
    compliance_result : dict
        Compliance query result from Context Studio
        
    Returns
    -------
    dict
        Parsed context data in OrganizationContext format
    """
    # Extract items from results
    org_items = org_result.get('items', [])
    tech_items = tech_result.get('items', [])
    compliance_items = compliance_result.get('items', [])
    
    log.info(
        "parsing_context_studio_responses",
        org_items=len(org_items),
        tech_items=len(tech_items),
        compliance_items=len(compliance_items)
    )
    
    # Initialize context data with defaults
    context_data = {
        "name": "Organization from Context Studio",
        "industry": "Technology",
        "tech_stack": {
            "preferred_languages": ["Python", "JavaScript", "Java"],
            "cloud_providers": ["AWS", "Azure"],
            "databases": ["PostgreSQL", "MongoDB"],
            "architecture_patterns": ["Microservices", "REST API", "Event-Driven"]
        },
        "compliance": {
            "frameworks": ["ISO27001", "SOC2"],
            "certifications": []
        },
        "naming_conventions": {
            "functional_prefix": "FR",
            "non_functional_prefix": "NFR",
            "compliance_prefix": "CR",
            "risk_prefix": "RISK",
            "ambiguity_prefix": "AMB",
            "requirement_prefix": "REQ",
            "separator": "-"
        },
        "risk_thresholds": {
            "high_complexity_indicators": [
                "real-time", "high-availability", "distributed", "microservices",
                "machine learning", "AI", "blockchain", "multi-tenant"
            ],
            "timeline_red_flags": [
                "aggressive timeline", "tight deadline", "immediate", "urgent",
                "ASAP", "rush", "expedited"
            ],
            "budget_risk_factors": [
                "fixed price", "not-to-exceed", "budget constraints",
                "cost-sensitive", "limited budget"
            ]
        },
        "priority_keywords": {
            "must": ["must", "required", "mandatory", "shall", "critical"],
            "should": ["should", "recommended", "preferred", "desired"],
            "could": ["could", "optional", "nice-to-have", "if possible"]
        }
    }
    
    # Parse organization information
    org_data = _parse_organization_items(org_items)
    if org_data:
        context_data.update(org_data)
    
    # Parse tech stack
    tech_data = _parse_tech_stack_items(tech_items)
    if tech_data:
        context_data['tech_stack'].update(tech_data)
    
    # Parse compliance
    compliance_data = _parse_compliance_items(compliance_items)
    if compliance_data:
        context_data['compliance'].update(compliance_data)
    
    log.info(
        "context_parsed_from_studio",
        org_name=context_data['name'],
        languages=len(context_data['tech_stack']['preferred_languages']),
        frameworks=len(context_data['compliance']['frameworks'])
    )
    
    return context_data


def _parse_organization_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Parse organization information from Context Studio items."""
    org_data = {}
    
    for item in items:
        content = item.get('content', '')
        try:
            if content.strip().startswith('{'):
                data = json.loads(content)
                
                # Check for organization data in JSON-LD
                if '@type' in data:
                    type_val = data.get('@type', '')
                    if 'Organization' in str(type_val) or 'org:' in str(type_val):
                        if 'name' in data or 'org:name' in data:
                            org_data['name'] = data.get('name') or data.get('org:name')
                        if 'industry' in data or 'org:industry' in data:
                            org_data['industry'] = data.get('industry') or data.get('org:industry')
                        
                        log.debug("parsed_organization_data", name=org_data.get('name'))
        except json.JSONDecodeError:
            # Not JSON, skip
            pass
        except Exception as e:
            log.warning("failed_to_parse_org_item", error=str(e))
    
    return org_data


def _parse_tech_stack_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Parse technology stack from Context Studio items."""
    languages_set: Set[str] = set()
    cloud_set: Set[str] = set()
    db_set: Set[str] = set()
    patterns_set: Set[str] = set()
    
    for item in items:
        content = item.get('content', '')
        try:
            if content.strip().startswith('{'):
                data = json.loads(content)
                
                # Look for tech stack data in various JSON-LD formats
                # Standard format
                if 'std:programmingLanguages' in data:
                    langs = data['std:programmingLanguages']
                    if isinstance(langs, list):
                        languages_set.update(langs)
                
                if 'std:cloudPlatforms' in data:
                    clouds = data['std:cloudPlatforms']
                    if isinstance(clouds, list):
                        cloud_set.update(clouds)
                
                if 'std:databases' in data:
                    dbs = data['std:databases']
                    if isinstance(dbs, list):
                        db_set.update(dbs)
                
                if 'std:architecturePatterns' in data:
                    patterns = data['std:architecturePatterns']
                    if isinstance(patterns, list):
                        patterns_set.update(patterns)
                
                # Alternative formats
                for key in ['programmingLanguages', 'languages', 'tech_stack']:
                    if key in data and isinstance(data[key], list):
                        languages_set.update(data[key])
                
                for key in ['cloudProviders', 'cloud', 'cloudPlatforms']:
                    if key in data and isinstance(data[key], list):
                        cloud_set.update(data[key])
                
                for key in ['databases', 'db', 'dataStores']:
                    if key in data and isinstance(data[key], list):
                        db_set.update(data[key])
                
        except json.JSONDecodeError:
            pass
        except Exception as e:
            log.warning("failed_to_parse_tech_item", error=str(e))
    
    tech_data = {}
    if languages_set:
        tech_data['preferred_languages'] = list(languages_set)
        log.debug("parsed_languages", count=len(languages_set))
    if cloud_set:
        tech_data['cloud_providers'] = list(cloud_set)
        log.debug("parsed_cloud_providers", count=len(cloud_set))
    if db_set:
        tech_data['databases'] = list(db_set)
        log.debug("parsed_databases", count=len(db_set))
    if patterns_set:
        tech_data['architecture_patterns'] = list(patterns_set)
    
    return tech_data


def _parse_compliance_items(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Parse compliance requirements from Context Studio items."""
    frameworks_set: Set[str] = set()
    certs_set: Set[str] = set()
    
    for item in items:
        content = item.get('content', '')
        try:
            if content.strip().startswith('{'):
                data = json.loads(content)
                
                # Look for compliance data in various JSON-LD formats
                if 'compliance:frameworks' in data:
                    frameworks = data['compliance:frameworks']
                    if isinstance(frameworks, list):
                        frameworks_set.update(frameworks)
                
                if 'compliance:certifications' in data:
                    certs = data['compliance:certifications']
                    if isinstance(certs, list):
                        certs_set.update(certs)
                
                # Alternative formats
                for key in ['frameworks', 'complianceFrameworks', 'regulations']:
                    if key in data and isinstance(data[key], list):
                        frameworks_set.update(data[key])
                
                for key in ['certifications', 'certs']:
                    if key in data and isinstance(data[key], list):
                        certs_set.update(data[key])
                
        except json.JSONDecodeError:
            pass
        except Exception as e:
            log.warning("failed_to_parse_compliance_item", error=str(e))
    
    compliance_data = {}
    if frameworks_set:
        compliance_data['frameworks'] = list(frameworks_set)
        log.debug("parsed_compliance_frameworks", count=len(frameworks_set))
    if certs_set:
        compliance_data['certifications'] = list(certs_set)
        log.debug("parsed_certifications", count=len(certs_set))
    
    return compliance_data

# Made with Bob
