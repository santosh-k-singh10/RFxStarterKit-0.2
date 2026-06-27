"""
api/router.py — FastAPI router for the preferences + scoping endpoints.

Mount this router in your main FastAPI app:

    from api.router import router
    app.include_router(router, prefix="/api")

Endpoints:
    GET  /api/health
    POST /api/preferences   → validate preferences, return structured JSON
    POST /api/analyze       → full pipeline (preferences + reqs → scoping)
"""

from __future__ import annotations

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse

from schemas import (
    PreferencesRequest,
    PreferencesResponse,
    AnalyzeRequest,
    EnrichedAnalyzeRequest,
    HealthResponse,
    ErrorResponse,
)
from scoping_designer.preferences import PreferencesCollector
from scoping_designer.designer import ScopingDesigner
from scoping_designer.models import EnrichedModules, DeploymentTarget
from config import config

logger = logging.getLogger(__name__)

router = APIRouter()
_OUTPUTS_ROOT = Path("outputs")
# ── Module-level constants ────────────────────────────────────────────────────

_DEPLOYMENT_MAP = {
    "cloud": DeploymentTarget.CLOUD,
    "on_prem": DeploymentTarget.ON_PREM,
    "hybrid": DeploymentTarget.HYBRID,
    "saas": DeploymentTarget.SAAS,
}


def _ensure_llm_configured() -> None:
    """Validate that at least one supported LLM provider is configured."""
    if not config.is_llm_configured():
        raise HTTPException(
            status_code=503,
            detail=(
                "No LLM provider is configured. Set either OPENAI_API_BASE + "
                "OPENAI_API_KEY + MODEL_ID, or ANTHROPIC_API_KEY."
            ),
        )


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", value.strip()).strip("_").lower()
    return slug or "system"


def _ensure_run_dir(project_name: str) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir = _OUTPUTS_ROOT / f"{timestamp}_{_slugify(project_name)}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def _save_preferences_output(project_name: str, payload: dict[str, Any], response_data: dict[str, Any]) -> dict[str, str]:
    run_dir = _ensure_run_dir(project_name)
    request_path = run_dir / "preferences_request.json"
    response_path = run_dir / "preferences_response.json"
    _write_json(request_path, payload)
    _write_json(response_path, response_data)
    return {
        "run_dir": str(run_dir),
        "request_json": str(request_path),
        "response_json": str(response_path),
    }


def _save_architecture_output(
    project_name: str,
    request_payload: dict[str, Any],
    enriched_payload: dict[str, Any],
    architecture_payload: dict[str, Any],
) -> dict[str, str]:
    from scoping_designer.designer import ScopingDesigner
    from scoping_designer.exporters import HtmlExporter, MarkdownExporter

    run_dir = _ensure_run_dir(project_name)
    request_path = run_dir / "architecture_request.json"
    enriched_path = run_dir / "architecture_enriched.json"
    architecture_path = run_dir / "architecture_output.json"
    markdown_path = run_dir / "architecture_export.md"
    html_path = run_dir / "architecture_export.html"

    _write_json(request_path, request_payload)
    _write_json(enriched_path, enriched_payload)
    _write_json(architecture_path, architecture_payload)

    output = ScopingDesigner.from_dict(architecture_payload)
    markdown_path.write_text(MarkdownExporter().export(output), encoding="utf-8")
    html_path.write_text(HtmlExporter().export(output), encoding="utf-8")

    return {
        "run_dir": str(run_dir),
        "request_json": str(request_path),
        "enriched_json": str(enriched_path),
        "architecture_json": str(architecture_path),
        "architecture_markdown": str(markdown_path),
        "architecture_html": str(html_path),
    }



# ── Health ────────────────────────────────────────────────────────────────────

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health check",
)
async def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        version="1.1.0",
        module="rfp_analyzer.api",
    )


# ── Preferences ───────────────────────────────────────────────────────────────

@router.post(
    "/preferences",
    summary="Validate and structure user preferences",
    description=(
        "Accepts the raw form payload from the preferences intake UI, "
        "validates it, infers domain context, and returns a structured "
        "preferences object ready to pass into /api/analyze."
    ),
)
async def collect_preferences(body: PreferencesRequest) -> dict[str, Any]:
    logger.info("=" * 70)
    logger.info("POST /api/preferences - Starting preferences collection")
    logger.info("=" * 70)
    
    try:
        logger.info("Input preferences:")
        logger.info(f"  - Build approach: {body.approach}")
        logger.info(f"  - Deployment: {body.deployment}")
        logger.info(f"  - Cloud provider: {body.cloud}")
        logger.info(f"  - Compliance: {body.compliance}")
        logger.info(f"  - Channels: {body.channels}")
        logger.info(f"  - Integration style: {body.integration}")
        logger.info(f"  - Timeline: {body.timeline}")
        
        # Use PreferencesCollector to process and validate
        logger.info("Processing preferences with PreferencesCollector...")
        prefs = PreferencesCollector.from_dict(body.model_dump())
        
        logger.info("Preferences processed successfully")
        logger.info(f"  - Inferred domain context: {prefs.inferred_domain_context}")
        logger.info(f"  - Extra constraints: {len(prefs.extra_constraints)} items")
        
        data = cast(dict[str, Any], prefs.to_dict())
        project_name = data.get("existing_tech_estate") or "preferences"
        saved_files = _save_preferences_output(project_name, body.model_dump(), data)
        logger.info("Preferences collection completed successfully")
        logger.info("=" * 70)
        return {
            "summary": data,
            "saved_files": saved_files,
        }
    except Exception as e:
        logger.error("Preferences parsing failed")
        logger.exception("Error details:")
        raise HTTPException(status_code=422, detail=str(e))


# ── Analyze ───────────────────────────────────────────────────────────────────

@router.post(
    "/analyze",
    summary="Full pipeline: preferences + requirements → architecture",
    description=(
        "Runs the full Phase 2 pipeline. Combines the structured preferences "
        "with the extracted requirements and calls the Anthropic API to produce "
        "system context, proposed architecture, and estimable component breakdown. "
        "Requires ANTHROPIC_API_KEY to be set in the environment."
    ),
    responses={
        200: {"description": "Full ArchitectureOutput as JSON"},
        503: {"model": ErrorResponse, "description": "API key not configured"},
        500: {"model": ErrorResponse, "description": "Analysis failed"},
    },
)
async def analyze(body: AnalyzeRequest) -> dict[str, Any]:
    logger.info("=" * 70)
    logger.info("POST /api/analyze - Starting architecture analysis with auto-enrichment")
    logger.info("=" * 70)
    
    _ensure_llm_configured()

    try:
        logger.info(f"Project: {body.project_name}")
        logger.info(f"Requirements length: {len(body.requirements)} characters")
        
        # Validate requirements
        if not body.requirements or len(body.requirements.strip()) < 10:
            logger.error(f"Requirements validation failed: length={len(body.requirements) if body.requirements else 0}")
            raise HTTPException(
                status_code=422,
                detail="Requirements must be at least 10 characters long. Please provide valid requirements text."
            )
        
        # Build preferences from the validated request
        logger.info("Building preferences from request...")
        logger.info(f"Preferences data: {body.preferences.model_dump()}")
        prefs = PreferencesCollector.from_dict(body.preferences.model_dump())
        logger.info(f"  - Deployment target: {prefs.deployment_target}")
        logger.info(f"  - Domain context: {prefs.inferred_domain_context}")

        # AUTO-ENRICH: Convert markdown requirements to enriched modules
        logger.info("Auto-enriching requirements (Phase 1.5)...")
        from scoping_designer.enricher import RequirementEnricher
        
        enricher = RequirementEnricher()
        enriched = await enricher.enrich_markdown(body.requirements)
        
        logger.info(f"Requirements enriched: {enriched.total} requirements in {len(enriched.modules)} modules")

        # Build deployment target and constraints
        deployment = prefs.deployment_target
        constraints = list(prefs.extra_constraints)
        if prefs.cloud_provider and prefs.cloud_provider.value != 'no_pref':
            constraints.append(f"Cloud provider: {prefs.cloud_provider.value}")
        if prefs.compliance_regimes:
            regimes = ", ".join(c.value.upper() for c in prefs.compliance_regimes if c.value != 'none')
            if regimes:
                constraints.append(f"Compliance: {regimes}")

        # Extract build approach and packaged platforms for SAP-aware prompts
        build_approach = prefs.build_approach.value if prefs.build_approach else None
        packaged_platforms = [p.value for p in prefs.packaged_platforms] if prefs.packaged_platforms else None
        
        logger.info(f"Build approach: {build_approach}")
        logger.info(f"Packaged platforms: {packaged_platforms}")
        
        # Run enriched analysis (preferred path)
        logger.info("Initializing ArchitectureDesigner for enriched analysis...")
        designer = ScopingDesigner(api_key=config.ANTHROPIC_API_KEY or None, max_tokens=12000)
        
        logger.info("Starting enriched async architecture analysis...")
        result = await designer.analyze_enriched_async(
            enriched,
            project_name=body.project_name,
            deployment_target=deployment,
            domain_context=prefs.inferred_domain_context,
            extra_constraints=constraints,
            build_approach=build_approach,
            packaged_platforms=packaged_platforms
        )
        
        logger.info("Architecture analysis completed successfully")
        logger.info(f"  - Components generated: {len(result.components)}")
        logger.info(f"  - Domains identified: {len(result.domains)}")
        logger.info(f"  - Risks identified: {len(result.risks)}")
        logger.info(f"  - Total story points (mid): {result.summary.total_story_points_mid}")
        logger.info("=" * 70)

        result_dict = result.to_dict()
        enriched_payload = {
            "modules": {
                module_name: [req.__dict__ for req in reqs]
                for module_name, reqs in enriched.modules.items()
            },
            "total": enriched.total,
        }
        
        # Extract scoping metadata for GSE pre-fill
        from scoping_designer.scoping_metadata_extractor import extract_scoping_metadata
        enriched_payload["scoping_metadata"] = extract_scoping_metadata(enriched_payload)
        saved_files = _save_architecture_output(
            body.project_name,
            body.model_dump(),
            enriched_payload,
            result_dict,
        )
        return {
            "summary": {
                "project_name": body.project_name,
                "deployment_target": deployment.value,
                "domain_context": prefs.inferred_domain_context,
                "requirements_total": enriched.total,
                "module_count": len(enriched.modules),
                "component_count": len(result.components),
                "domain_count": len(result.domains),
                "risk_count": len(result.risks),
                "total_story_points_mid": result.summary.total_story_points_mid,
                "architecture_pattern": result.architecture.recommended,
            },
            "saved_files": saved_files,
            "artifacts": {
                "architecture": result_dict,
            },
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Architecture analysis failed")
        logger.exception("Error details:")
        raise HTTPException(status_code=500, detail=str(e))


# ── Analyze: enriched path (Phase 1.5) ───────────────────────────────────────

@router.post(
    "/analyze/enriched",
    summary="Phase 1.5 path — module-grouped requirements → architecture",
    description=(
        "Preferred endpoint. Accepts the JSON output of Phase 1.5 enrichment "
        "(rfp_enriched_requirements.json). Uses module groupings, impl_type, "
        "and actor annotations to produce more accurate architecture, component "
        "decomposition, story point ranges, and requirement traceability."
    ),
    responses={
        200: {"description": "Full ArchitectureOutput as JSON"},
        503: {"model": ErrorResponse, "description": "API key not configured"},
        500: {"model": ErrorResponse, "description": "Analysis failed"},
    },
)
async def analyze_enriched(body: EnrichedAnalyzeRequest) -> dict[str, Any]:
    """
    Enriched analysis pipeline:
      1. Parse EnrichedModules from modules dict
      2. Build ArchitectureInput with module_summary() as requirements
      3. Call Claude — architecture pass (5000 tokens)
      4. Call Claude — traceability pass (2000 tokens, non-blocking on failure)
      5. Return ArchitectureOutput with story_point_range + source_requirements on components
    """
    logger.info("=" * 70)
    logger.info("POST /api/analyze/enriched - Starting enriched analysis")
    logger.info("=" * 70)
    
    _ensure_llm_configured()

    try:
        logger.info(f"Project: {body.project_name}")
        logger.info(f"Deployment: {body.deployment}")
        logger.info(f"Domain context: {body.domain_context}")
        logger.info(f"Modules: {len(body.modules)}")
        
        # Parse enriched modules from request body
        logger.info("Parsing enriched modules...")
        total_reqs = sum(len(reqs) for reqs in body.modules.values())
        enriched = EnrichedModules.from_dict({
            "modules": body.modules,
            "total": total_reqs,
        })
        logger.info(f"  - Total requirements: {total_reqs}")
        logger.info(f"  - Module breakdown:")
        for module_name, reqs in body.modules.items():
            logger.info(f"    • {module_name}: {len(reqs)} requirements")

        # Build deployment target
        deployment = _DEPLOYMENT_MAP.get(body.deployment, DeploymentTarget.CLOUD)
        logger.info(f"  - Deployment target: {deployment}")

        # Build constraints from request
        constraints = list(body.extra_constraints)
        if body.cloud_provider:
            constraints.append(f"Cloud provider: {body.cloud_provider}")
        if body.compliance:
            constraints.append(f"Compliance: {', '.join(body.compliance)}")
        if body.timeline:
            constraints.append(f"Timeline: {body.timeline}")
        logger.info(f"  - Total constraints: {len(constraints)}")

        logger.info("Initializing ArchitectureDesigner (max_tokens=5000)...")
        designer = ScopingDesigner(
            api_key=config.ANTHROPIC_API_KEY or None,
            max_tokens=5000,
        )
        
        # Extract build approach and packaged platforms for SAP-aware prompts
        build_approach = body.build_approach
        packaged_platforms = body.packaged_platforms if body.packaged_platforms else None
        
        logger.info(f"Build approach: {build_approach}")
        logger.info(f"Packaged platforms: {packaged_platforms}")
        
        logger.info("Starting enriched async analysis...")
        result = await designer.analyze_enriched_async(
            enriched,
            project_name=body.project_name,
            deployment_target=deployment,
            domain_context=body.domain_context,
            extra_constraints=constraints,
            build_approach=build_approach,
            packaged_platforms=packaged_platforms,
        )
        
        logger.info("Enriched analysis completed successfully")
        logger.info(f"  - Components: {len(result.components)}")
        logger.info(f"  - Domains: {len(result.domains)}")
        logger.info(f"  - Risks: {len(result.risks)}")
        logger.info(f"  - Total story points (mid): {result.summary.total_story_points_mid}")
        logger.info("=" * 70)
        
        result_dict = result.to_dict()
        
        # Extract scoping metadata for GSE pre-fill
        from scoping_designer.scoping_metadata_extractor import extract_scoping_metadata
        enriched_payload_with_metadata = {"modules": body.modules, "total": total_reqs}
        enriched_payload_with_metadata["scoping_metadata"] = extract_scoping_metadata(enriched_payload_with_metadata)
        
        saved_files = _save_architecture_output(
            body.project_name,
            body.model_dump(),
            enriched_payload_with_metadata,
            result_dict,
        )
        return {
            "summary": {
                "project_name": body.project_name,
                "deployment_target": deployment.value,
                "domain_context": body.domain_context,
                "requirements_total": total_reqs,
                "module_count": len(enriched.modules),
                "component_count": len(result.components),
                "domain_count": len(result.domains),
                "risk_count": len(result.risks),
                "total_story_points_mid": result.summary.total_story_points_mid,
                "architecture_pattern": result.architecture.recommended,
            },
            "saved_files": saved_files,
            "artifacts": {
                "architecture": result_dict,
            },
        }

    except Exception as e:
        logger.error("Enriched analysis failed")
        logger.exception("Error details:")
        raise HTTPException(status_code=500, detail=str(e))


# ── Export endpoints ──────────────────────────────────────────────────────────

@router.post(
    "/export/markdown",
    summary="Export architecture analysis as Markdown",
    description=(
        "Accepts the full ArchitectureOutput JSON and exports it as a "
        "comprehensive Markdown document with story points, traceability, "
        "and module grouping."
    ),
    response_class=HTMLResponse,
)
async def export_markdown(body: dict[str, Any]) -> str:
    """
    Export architecture output as Markdown.
    Expects the full ArchitectureOutput JSON from /api/analyze or /api/analyze/enriched.
    """
    logger.info("=" * 70)
    logger.info("POST /api/export/markdown - Exporting to Markdown")
    logger.info("=" * 70)
    
    try:
        from scoping_designer.exporters import MarkdownExporter
        from scoping_designer.designer import ScopingDesigner
        
        # Reconstruct ScopingOutput from dict
        logger.info("Reconstructing ScopingOutput from JSON...")
        output = ScopingDesigner.from_dict(body)
        
        logger.info("Generating Markdown export...")
        exporter = MarkdownExporter()
        markdown = exporter.export(output)
        
        logger.info(f"Markdown export generated ({len(markdown)} characters)")
        logger.info("=" * 70)
        
        return markdown
        
    except Exception as e:
        logger.error("Markdown export failed")
        logger.exception("Error details:")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/export/json",
    summary="Export architecture analysis as formatted JSON",
    description=(
        "Accepts the full ArchitectureOutput and returns it as "
        "formatted JSON with proper indentation."
    ),
)
async def export_json(body: dict[str, Any], indent: int = 2) -> dict[str, Any]:
    """
    Export architecture output as formatted JSON.
    Expects the full ArchitectureOutput JSON from /api/analyze or /api/analyze/enriched.
    """
    logger.info("=" * 70)
    logger.info("POST /api/export/json - Exporting to JSON")
    logger.info("=" * 70)
    
    try:
        from scoping_designer.exporters import JsonExporter
        from scoping_designer.designer import ScopingDesigner
        
        # Reconstruct ScopingOutput from dict
        logger.info("Reconstructing ScopingOutput from JSON...")
        output = ScopingDesigner.from_dict(body)
        
        logger.info("Generating JSON export...")
        exporter = JsonExporter()
        json_str = exporter.export(output, indent=indent)
        
        logger.info(f"JSON export generated ({len(json_str)} characters)")
        logger.info("=" * 70)
        
        # Return as dict for FastAPI to serialize
        import json
        return json.loads(json_str)
        
    except Exception as e:
        logger.error("JSON export failed")
        logger.exception("Error details:")
        raise HTTPException(status_code=500, detail=str(e))


