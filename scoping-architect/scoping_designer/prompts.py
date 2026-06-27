"""
Prompt builder — v1.2.

Two build paths:
  1. from_enriched_modules() — uses Phase 1.5 module-grouped input (preferred)
  2. flat requirements string — legacy Phase 1 path (still supported)

Domain overlays inject domain-specific instructions when domain_context is set.
"""

from __future__ import annotations
from typing import Optional
from .models import ArchitectureInput

# ── Domain overlays ───────────────────────────────────────────────────────────

DOMAIN_OVERLAYS: dict[str, str] = {
    "healthcare": (
        "This is a HEALTHCARE system. Flag every component handling PHI/ePHI "
        "(complianceImpacted=true). Note HIPAA Security Rule in domainNote. "
        "Highlight FHIR integration and EHR vendor dependency risks."
    ),
    "ecommerce": (
        "This is an E-COMMERCE platform. Flag every component in PCI DSS scope "
        "(complianceImpacted=true). Note Stripe/PayPal tokenisation as the PCI mechanism. "
        "Highlight performance-critical paths: product search, checkout, and cart."
    ),
    "fintech": (
        "This is a FINTECH system. Flag PCI-DSS scope (complianceImpacted=true). "
        "Highlight encryption, tokenisation, and audit trail requirements."
    ),
    "government": (
        "This is a GOVERNMENT system. Flag FedRAMP/FISMA scope (complianceImpacted=true). "
        "Highlight data sovereignty, audit logging, and Section 508 accessibility."
    ),
    "logistics": (
        "This is a LOGISTICS / SUPPLY CHAIN system. Highlight real-time tracking, "
        "IoT integration, and event-driven architecture opportunities."
    ),
    "saas_platform": (
        "This is a SAAS PLATFORM. Highlight multi-tenant isolation, subscription billing, "
        "tenant data partitioning, and self-service onboarding components."
    ),
}

# ── Platform overlays (for packaged solutions) ────────────────────────────────

PLATFORM_OVERLAYS: dict[str, str] = {
    "sap": """\
## SAP S/4HANA PACKAGED SOLUTION ARCHITECTURE

This is an SAP S/4HANA implementation. Your architecture MUST include TWO LAYERS:

### 1. STANDARD SAP MODULES LAYER (Configuration - NOT Custom Build)
List ALL required standard SAP modules as separate components:
- **SAP Financial Accounting (FI)**: General ledger, AP/AR, asset accounting
- **SAP Controlling (CO)**: Cost centers, profit centers, internal orders
- **SAP Materials Management (MM)**: Procurement, inventory, material master
- **SAP Sales & Distribution (SD)**: Sales orders, pricing, shipping, billing
- **SAP Production Planning (PP)**: Production orders, work centers, BOMs, MRP
- **SAP Quality Management (QM)**: Inspection lots, quality notifications, CoA
- **SAP Plant Maintenance (PM)**: Equipment master, maintenance orders, calibration
- **SAP Warehouse Management (EWM or IM)**: Storage, picking, lot tracking
- **SAP Treasury (TRM)**: Cash management, bank accounting (if needed)

For EACH standard SAP module component:
- type: "SAP Standard Module"
- implType: "sap_standard_config"
- complexity: Based on configuration scope (Low=basic setup, Medium=multi-entity, High=GxP/pharma)
- storyPointRange: Use CONFIGURATION ranges (NOT custom development):
  * Low complexity: 15-25-40 SP
  * Medium complexity: 25-40-60 SP
  * High complexity: 40-60-90 SP
- description: What will be CONFIGURED (not built), e.g., "Configure chart of accounts, company codes, fiscal year variants, GL account master, sub-ledger integration"
- estimationSignals: Configuration items, e.g., ["Multi-entity consolidation", "5-country localization", "GMP material status"]

### 2. CUSTOM EXTENSIONS LAYER (Development)
List custom components that EXTEND or ENHANCE standard SAP:
- Compliance overlays (e.g., GMP validation engine, 21 CFR Part 11 e-signature)
- Industry-specific enhancements (e.g., pharmaceutical batch genealogy)
- Custom Fiori apps
- Integration adapters (e.g., MES connector, e-invoice gateway)

For custom extension components:
- type: "Backend Service" or "SAP Enhancement" or "Integration"
- implType: "sap_custom_enhancement" or "sap_abap_development" or "custom_build"
- complexity: Based on development effort
- storyPointRange: Use DEVELOPMENT ranges:
  * Low: 5-8-13 SP
  * Medium: 13-21-34 SP
  * High: 21-34-55 SP
  * Very High: 34-55-89 SP

### CRITICAL RULES:
1. **DO NOT mark standard SAP modules as "custom_build"** - they are "sap_standard_config"
2. **Separate configuration effort from development effort** in story points
3. **Map requirements to BOTH layers**: Standard module + Custom enhancement
4. **Include localization** as separate components if multi-country (10-20 SP per country)
5. **Show traceability**: Which requirements drive which standard modules

Example component structure:
```json
{
  "name": "SAP Materials Management (MM)",
  "module": "materials_management",
  "type": "SAP Standard Module",
  "implType": "sap_standard_config",
  "complexity": "High",
  "complexityReason": "GMP-compliant material status management and batch traceability",
  "storyPointRange": {"low": 40, "mid": 55, "high": 70},
  "estimationSignals": ["Material types with GMP status", "Batch management", "Lot/expiry tracking", "Quarantine workflows"],
  "description": "Configure SAP MM for pharmaceutical procurement and inventory with GMP material status, batch management, and regulatory compliance"
}
```
""",
    "salesforce": """\
## SALESFORCE PACKAGED SOLUTION ARCHITECTURE

This is a Salesforce implementation. Include:
1. Standard Salesforce objects/modules (Sales Cloud, Service Cloud, etc.) - mark as "platform_standard_config"
2. Custom Apex/Lightning components - mark as "platform_custom_code"
3. Integration adapters

Use configuration SP ranges (20-60) for standard setup, development ranges (13-89) for custom code.
""",
}

# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM_BASE = """\
You are a senior solutions architect. Analyse the provided requirements and produce a \
complete architecture artefact for delivery estimation.

When requirements are MODULE-GROUPED (Phase 1.5 enriched input), use the module \
boundaries directly as bounded capability areas. Each module maps to one or more \
estimable components. The impl_type field (custom_build | third_party_integration | \
configuration | compliance_control) tells you how each requirement will be implemented — \
use this to calibrate component complexity and estimation signals accurately.

Respond ONLY with a single valid JSON object. No markdown, no preamble. Schema:

{
  "domains": [
    {"name":string,"requirements":[string],"count":number,
     "color":"blue"|"teal"|"purple"|"amber"|"coral"|"green"|"red"|"gray"}
  ],
  "systemContext": {
    "description": string,
    "actors": [{"name":string,"type":"human"|"internal_system"|"external_system","description":string}],
    "integrations": [string]
  },
  "architecture": {
    "recommended": string,
    "rationale": string,
    "domainNote": string|null,
    "keyPrinciples": [string],
    "alternatives": [{"name":string,"tradeoff":string}],
    "layerDiagram": [{"layer":string,"components":[string]}]
  },
  "components": [
    {
      "name": string,
      "module": string,
      "type": "Frontend"|"Backend Service"|"API Gateway"|"Data Store"|"AI/ML"|"Integration"|"Security"|"Infrastructure"|"Compliance"|"SAP Standard Module"|"SAP Enhancement"|"Platform Standard Module",
      "description": string,
      "complexity": "Low"|"Medium"|"High",
      "complexityReason": string,
      "complianceImpacted": boolean,
      "implType": "custom_build"|"third_party_integration"|"configuration"|"compliance_control"|"not_applicable"|"sap_standard_config"|"sap_custom_enhancement"|"sap_abap_development"|"platform_standard_config",
      "actors": [string],
      "dependencies": [string],
      "estimationSignals": [string],
      "storyPointRange": {"low":number,"mid":number,"high":number}
    }
  ],
  "risks": [
    {"risk":string,"level":"High"|"Medium"|"Low","mitigation":string,"refId":string|null,"module":string|null}
  ],
  "summary": {
    "domainCount":number,"actorCount":number,"componentCount":number,
    "openAmbiguities":number,"avgComplexity":string,
    "complianceComponents":number,"totalStorypointsMid":number
  }
}

Rules:
- storyPointRange: Fibonacci scale (1,2,3,5,8,13,21). low=optimistic, mid=realistic, high=worst-case.
- estimationSignals: 2–4 short technical specifics (e.g. "Stripe Checkout SDK", "JWT refresh rotation").
- complexityReason: one sentence naming the dominant complexity driver.
- implType on component: inherit from the dominant requirement impl_type in this component's module.
- complianceImpacted: true for any component touching regulated data or in compliance scope.
- Do not invent requirements not in the input. Surface ambiguities as risks.
"""


def build_system_prompt(input_: ArchitectureInput, build_approach: Optional[str] = None, packaged_platforms: Optional[list] = None) -> str:
    """
    Build system prompt with domain and platform overlays.
    
    Args:
        input_: Architecture input with requirements
        build_approach: "greenfield", "packaged", "extend", "hybrid" (from preferences)
        packaged_platforms: List of platform names like ["sap", "salesforce"] (from preferences)
    """
    prompt = _SYSTEM_BASE
    
    # Add domain overlay if specified
    if input_.domain_context:
        overlay = DOMAIN_OVERLAYS.get(input_.domain_context.lower().strip())
        if overlay:
            prompt += f"\n\nDOMAIN CONTEXT:\n{overlay}"
    
    # Add platform overlay for packaged solutions
    if build_approach == "packaged" and packaged_platforms:
        # Use first platform (primary)
        platform_key = packaged_platforms[0].lower().strip()
        platform_overlay = PLATFORM_OVERLAYS.get(platform_key)
        if platform_overlay:
            prompt += f"\n\n{platform_overlay}"
    
    return prompt


def build_user_prompt(input_: ArchitectureInput, compact: bool = False) -> str:
    lines: list[str] = [
        f"Project: {input_.project_name}",
        f"Deployment: {input_.deployment_target.label()}",
    ]
    if input_.domain_context:
        lines.append(f"Domain: {input_.domain_context}")
    if input_.extra_constraints:
        lines.append("Constraints:")
        lines.extend(f"  - {c}" for c in input_.extra_constraints)

    if input_.is_enriched and input_.enriched_modules:
        em = input_.enriched_modules
        max_requirements_per_module = 4 if compact else 8
        lines += [
            "",
            "== MODULE-GROUPED REQUIREMENTS (Phase 1.5 enriched) ==",
            f"Total: {em.total} requirements across {len(em.modules)} modules",
            f"Ambiguities open: {len(em.ambiguities)}",
            f"Third-party integrations: {em.third_party_count}",
            "",
            em.module_summary(max_requirements_per_module=max_requirements_per_module),
            "",
            "Keep descriptions concise. Prefer short phrases over long paragraphs.",
            "Limit components to the minimum estimable set needed for delivery planning.",
            "Produce the full architecture artefact JSON using the module boundaries above.",
        ]
    else:
        lines += ["", "Requirements:", input_.requirements_as_str(), "",
                  "Keep descriptions concise. Prefer short phrases over long paragraphs.",
                  "Produce the full architecture artefact JSON."]

    return "\n".join(lines)


# ── Traceability prompt ───────────────────────────────────────────────────────

TRACEABILITY_SYSTEM = """\
You map software requirements to architecture components.
Respond ONLY with a valid JSON array. No preamble. No markdown.
Each entry: {"req_id": string, "component": string}
One requirement can map to multiple components.
Use only component names from the provided list — exactly as given.
"""

def build_traceability_prompt(req_ids: list[dict], component_names: list[str]) -> str:
    return (
        f"Requirements:\n{json.dumps(req_ids, indent=2)}\n\n"
        f"Components:\n{json.dumps(component_names)}\n\n"
        "Map each requirement to the component(s) it drives."
    )

import json  # noqa: E402 — needed by build_traceability_prompt
