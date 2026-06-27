"""
RFP Analyzer — End-to-end pipeline example  (v1.2)
===================================================

Pipeline:
  Phase 1   → requirement extraction  (separate tool)
  Phase 1.5 → enrichment              (automatic via enricher module)
  Phase 2   → scoping generation ← this file demonstrates

Run:
  python example_usage.py --mock                 # no API key needed
  ANTHROPIC_API_KEY=sk-ant-... python example_usage.py
  python example_usage.py --api-key sk-ant-...
  python example_usage.py --requirements requirements.md
"""

import sys, os, json, argparse
import asyncio

from scoping_designer import (
    ScopingDesigner, EnrichedModules, ArchitectureInput,
    DeploymentTarget,
)
from scoping_designer.preferences import (
    PreferencesCollector, UserPreferences,
    BuildApproach, CloudProvider, ComplianceRegime,
    ClientChannel, IntegrationStyle, DeliveryTimeline,
)
from scoping_designer.enricher import RequirementEnricher
from scoping_designer.exporters import MarkdownExporter, JsonExporter

# ── Minimal sample enriched modules (ABC e-commerce) ─────────────────────────
SAMPLE_ENRICHED = {
    "total": 12, "phase": "1.5_enriched",
    "modules": {
        "identity_access": [
            {"id":"FR-001","type":"FR","title":"User Registration and Login","priority":"MUST","confidence":100,
             "description":"Secure account registration and login.","is_ambiguous":False,
             "related_ids":["FR-002","FR-004"],"module":"identity_access","impl_type":"custom_build","actors":["customer","guest"]},
            {"id":"FR-004","type":"FR","title":"Role-Based Access Control","priority":"MUST","confidence":100,
             "description":"RBAC for Admin, Customer, Guest.","is_ambiguous":False,
             "related_ids":["FR-001"],"module":"identity_access","impl_type":"custom_build","actors":["admin","customer","guest"]},
            {"id":"FR-015","type":"FR","title":"Social Media Login","priority":"MUST","confidence":100,
             "description":"OAuth via Google/Facebook.","is_ambiguous":False,
             "related_ids":["FR-001"],"module":"identity_access","impl_type":"third_party_integration","actors":["customer","guest"]},
        ],
        "cart_checkout": [
            {"id":"FR-006","type":"FR","title":"Shopping Cart","priority":"MUST","confidence":100,
             "description":"Add/remove/update cart items.","is_ambiguous":False,
             "related_ids":["FR-007"],"module":"cart_checkout","impl_type":"custom_build","actors":["customer"]},
            {"id":"FR-007","type":"FR","title":"Payment Processing","priority":"MUST","confidence":100,
             "description":"Stripe or PayPal integration.","is_ambiguous":False,
             "related_ids":["FR-006","FR-008"],"module":"cart_checkout","impl_type":"third_party_integration","actors":["customer"]},
            {"id":"FR-008","type":"FR","title":"Order Tracking","priority":"MUST","confidence":100,
             "description":"Track current and past orders.","is_ambiguous":False,
             "related_ids":["FR-007"],"module":"cart_checkout","impl_type":"custom_build","actors":["customer"]},
        ],
        "compliance_privacy": [
            {"id":"CR-001","type":"CR","title":"PCI DSS compliance","priority":"MUST","confidence":98,
             "description":"Payment card data compliance via Stripe tokenisation.","is_ambiguous":False,
             "related_ids":["FR-007"],"module":"compliance_privacy","impl_type":"compliance_control","actors":["system"]},
            {"id":"CR-003","type":"CR","title":"GDPR compliance","priority":"MUST","confidence":97,
             "description":"EU data protection.","is_ambiguous":False,
             "related_ids":[],"module":"compliance_privacy","impl_type":"compliance_control","actors":["system"]},
            {"id":"FR-018","type":"FR","title":"Cookie Consent","priority":"MUST","confidence":100,
             "description":"GDPR cookie consent banner.","is_ambiguous":False,
             "related_ids":["CR-003"],"module":"compliance_privacy","impl_type":"compliance_control","actors":["customer","guest"]},
        ],
        "platform_nfr": [
            {"id":"NFR-001","type":"NFR","title":"Page Load < 2s","priority":"MUST","confidence":98,
             "description":"All pages load within 2 seconds.","is_ambiguous":False,
             "related_ids":[],"module":"platform_nfr","impl_type":"configuration","actors":["all"]},
            {"id":"NFR-002","type":"NFR","title":"1000 Concurrent Users","priority":"MUST","confidence":97,
             "description":"System handles 1000 concurrent users.","is_ambiguous":False,
             "related_ids":[],"module":"platform_nfr","impl_type":"configuration","actors":["all"]},
            {"id":"NFR-003","type":"NFR","title":"99.9% Uptime SLA","priority":"MUST","confidence":99,
             "description":"System uptime SLA.","is_ambiguous":False,
             "related_ids":[],"module":"platform_nfr","impl_type":"configuration","actors":["all"]},
        ],
    }
}

SAMPLE_REQUIREMENTS_MD = """# Requirements

## Functional Requirements

### FR-001: User Registration and Login
**Priority:** MUST | **Confidence:** 100%
Secure account registration and login with email/password.

### FR-004: Role-Based Access Control
**Priority:** MUST | **Confidence:** 100%
RBAC for Admin, Customer, Guest roles.

### FR-006: Shopping Cart
**Priority:** MUST | **Confidence:** 100%
Add/remove/update cart items with real-time price calculation.

### FR-007: Payment Processing
**Priority:** MUST | **Confidence:** 100%
Stripe or PayPal integration for secure payments.

## Non-Functional Requirements

### NFR-001: Page Load Performance
**Priority:** MUST | **Confidence:** 98%
All pages must load within 2 seconds.

### NFR-002: Concurrent Users
**Priority:** MUST | **Confidence:** 97%
System must handle 1000 concurrent users.

## Compliance Requirements

### CR-001: PCI DSS Compliance
**Priority:** MUST | **Confidence:** 98%
Payment card data compliance via Stripe tokenization.

### CR-003: GDPR Compliance
**Priority:** MUST | **Confidence:** 97%
EU data protection compliance with cookie consent.
"""


async def run_enriched_async(api_key: str, enriched_data: dict | None = None):
    """Run enriched analysis path (Phase 1.5 → Phase 2)"""
    print("=" * 60)
    print("RFP Analyzer — Phase 2 (Enriched path with auto-enrichment)")
    print("=" * 60)

    if enriched_data:
        print("\n[1] Using provided enriched modules...")
        em = EnrichedModules.from_dict(enriched_data)
    else:
        print("\n[1] Using built-in sample enriched modules (ABC e-commerce)...")
        em = EnrichedModules.from_dict(SAMPLE_ENRICHED)

    print(f"    Modules: {list(em.modules.keys())}")
    print(f"    Total requirements: {em.total}")
    print(f"    Third-party integrations: {em.third_party_count}")
    print(f"    Ambiguities: {len(em.ambiguities)}")

    print("\n[2] Running Phase 2 — architecture generation + traceability…")
    designer = ScopingDesigner(api_key=api_key, max_tokens=8000)
    result = await designer.analyze_enriched_async(
        em,
        project_name="ABC Company E-commerce Platform",
        deployment_target=DeploymentTarget.CLOUD,
        domain_context="ecommerce",
        extra_constraints=["Cloud provider: AWS", "Timeline: 6-month phased delivery"],
    )

    print(f"\n✅ Architecture generated")
    print(f"   Pattern:        {result.architecture.recommended}")
    print(f"   Components:     {result.summary.component_count}")
    print(f"   Story points:   {result.total_story_points}")
    print(f"   High risks:     {len(result.high_risks)}")
    print(f"   Compliance:     {len(result.compliance_components)} components in scope")

    print("\n── Components ──────────────────────────────────────────")
    for c in result.components:
        sp = f"[{c.story_point_range.low}–{c.story_point_range.mid}–{c.story_point_range.high} sp]" if c.story_point_range else ""
        flag = " ⚑" if c.compliance_impacted else ""
        traces = f" ← {','.join(c.source_requirements)}" if c.source_requirements else ""
        print(f"  {c.complexity.value:6s}  {c.name} ({c.impl_type or c.type.value}){flag}  {sp}{traces}")

    print("\n── High risks ──────────────────────────────────────────")
    for r in result.high_risks:
        print(f"  🔴 {r.risk}")

    # Export using the new exporters
    print("\n[3] Exporting results...")
    md_exporter = MarkdownExporter()
    json_exporter = JsonExporter()
    
    with open("architecture_output.md", "w", encoding="utf-8") as f:
        f.write(md_exporter.export(result))
    
    with open("architecture_output.json", "w", encoding="utf-8") as f:
        f.write(json_exporter.export(result, indent=2))
    
    print("📄 Exported → architecture_output.md + architecture_output.json")


async def run_with_auto_enrichment(api_key: str, requirements_md: str):
    """Run full pipeline with automatic enrichment (Phase 1 → 1.5 → 2)"""
    print("=" * 60)
    print("RFP Analyzer — Full Pipeline (Auto-enrichment)")
    print("=" * 60)

    print("\n[1] Auto-enriching requirements (Phase 1.5)...")
    enricher = RequirementEnricher()
    enriched = await enricher.enrich_markdown(requirements_md)
    
    print(f"    ✓ Enriched {enriched.total} requirements into {len(enriched.modules)} modules")
    
    print("\n[2] Running architecture analysis...")
    await run_enriched_async(api_key, enriched_data={"modules": enriched.modules, "total": enriched.total})


def run_flat(api_key: str):
    """Legacy flat-requirements path — still fully supported."""
    print("=" * 60)
    print("RFP Analyzer — Phase 2 (Flat / legacy path)")
    print("=" * 60)

    prefs = UserPreferences(
        build_approach=BuildApproach.GREENFIELD,
        deployment_target_raw="cloud",
        cloud_provider=CloudProvider.AWS,
        compliance_regimes=[ComplianceRegime.PCI_DSS, ComplianceRegime.GDPR],
        client_channels=[ClientChannel.WEB],
        integration_style=IntegrationStyle.REST,
        delivery_timeline=DeliveryTimeline.PHASED,
    )
    arch_input = prefs.to_architecture_input(
        requirements="- User login and registration\n- Product catalog with search\n- Cart and Stripe payment\n- Admin dashboard\n- GDPR cookie consent",
        project_name="ABC E-commerce",
    )
    result = ScopingDesigner(api_key=api_key).analyze(arch_input)
    print(f"\n✅ Pattern: {result.architecture.recommended}")
    print(f"   Components: {result.summary.component_count}")


def run_mock():
    print("=" * 60)
    print("RFP Analyzer v1.2 — Mock mode (no API key)")
    print("=" * 60)

    print("\n── EnrichedModules ─────────────────────────────────────")
    em = EnrichedModules.from_dict(SAMPLE_ENRICHED)
    print(f"  Modules:       {list(em.modules.keys())}")
    print(f"  Total:         {em.total}")
    print(f"  3rd-party:     {em.third_party_count}")
    print(f"  Functional:    {len(em.functional)}")
    print(f"  Compliance:    {len(em.compliance)}")

    print("\n── ArchitectureInput.from_enriched_modules() ───────────")
    inp = ArchitectureInput.from_enriched_modules(
        em, project_name="ABC E-commerce",
        deployment_target=DeploymentTarget.CLOUD,
        domain_context="ecommerce",
    )
    print(f"  is_enriched:   {inp.is_enriched}")
    print(f"  domain:        {inp.domain_context}")
    print(f"  Summary preview (first 200 chars):")
    print("  " + inp.requirements_as_str()[:200].replace("\n", "\n  "))

    print("\n── FastAPI endpoints (run: python run.py) ──────────────")
    print("  POST /api/preferences")
    print("  POST /api/analyze              ← auto-enriches markdown requirements")
    print("  POST /api/analyze/enriched     ← Phase 1.5 module JSON")
    print("  POST /api/export/markdown      ← export as Markdown")
    print("  POST /api/export/json          ← export as JSON")
    print("  GET  /api/health")
    print("  GET  /docs                     ← Swagger UI")
    print("  GET  /                         ← Web form")

    print("\n── All imports verified ────────────────────────────────")
    import scoping_designer as ad
    names = ["ScopingDesigner","EnrichedModules","EnrichedRequirement",
             "StoryPointRange","ImplType","ArchitectureInput","ArchitectureOutput",
             "UserPreferences","PreferencesCollector"]
    for n in names:
        assert hasattr(ad, n), f"Missing: {n}"
    print(f"  {len(names)} exports verified ✅")
    print("\n  Run with --api-key sk-ant-... for a real analysis.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api-key",       default=os.getenv("ANTHROPIC_API_KEY"))
    parser.add_argument("--requirements",  default=None, help="Path to requirements markdown file")
    parser.add_argument("--flat",          action="store_true", help="Use flat/legacy path")
    parser.add_argument("--mock",          action="store_true")
    args = parser.parse_args()

    if args.mock or not args.api_key:
        run_mock()
    elif args.flat:
        run_flat(args.api_key)
    elif args.requirements:
        # Load requirements from file and run with auto-enrichment
        with open(args.requirements, 'r', encoding='utf-8') as f:
            requirements_md = f.read()
        asyncio.run(run_with_auto_enrichment(args.api_key, requirements_md))
    else:
        # Use sample enriched data
        asyncio.run(run_enriched_async(args.api_key))

# Made with Bob
