"""
ScopingDesigner — v1.2

Two analysis paths:
  analyze(input_)              — flat requirements (Phase 1 / legacy)
  analyze_enriched(enriched)   — module-grouped Phase 1.5 input (preferred)

Both return ScopingOutput. The enriched path additionally runs a
requirement → component traceability pass and populates source_requirements
and story_point_range on every component.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from typing import Optional

from .models import (
    ArchitectureInput, ArchitectureOutput, ArchitectureSummary,
    ArchitecturePattern, ArchitectureAlternative, ArchitectureLayer,
    SystemContext, Actor, ActorType,
    Domain, Component, ComponentType, Complexity,
    ArchitectureRisk, RiskLevel, DeploymentTarget,
    EnrichedModules, StoryPointRange,
)
from .prompts import (
    build_system_prompt, build_user_prompt,
    TRACEABILITY_SYSTEM, build_traceability_prompt,
)

from llm_client import llm_client

logger = logging.getLogger(__name__)


class ScopingDesignerError(Exception):
    """Raised when analysis fails after all retries."""


class ScopingDesigner:
    """
    Phase 2 module — Requirements → Scoping.

    Parameters
    ----------
    api_key     : Anthropic API key (or set ANTHROPIC_API_KEY env var)
    model       : Model string — default claude-sonnet-4-20250514
    max_tokens  : Completion token budget (5000 recommended for enriched input)
    max_retries : Retry count on transient API errors
    retry_delay : Base backoff delay in seconds
    """

    DEFAULT_MODEL = "claude-sonnet-4-20250514"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        max_tokens: int = 16000,
        max_retries: int = 3,
        retry_delay: float = 2.0,
    ):
        self.model       = model
        self.max_tokens  = max_tokens
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._api_key    = api_key
        self._client     = None
        self._aclient    = None

    # ── Public: enriched path (preferred) ────────────────────────────────────

    def analyze_enriched(
        self,
        enriched: EnrichedModules,
        project_name: str = "the system",
        deployment_target: DeploymentTarget = DeploymentTarget.CLOUD,
        domain_context: Optional[str] = None,
        extra_constraints: Optional[list[str]] = None,
        build_approach: Optional[str] = None,
        packaged_platforms: Optional[list[str]] = None,
    ) -> ArchitectureOutput:
        """
        Synchronous enriched analysis.
        Accepts Phase 1.5 module-grouped requirements directly.

        Example
        -------
        >>> em = EnrichedModules.from_file("rfp_enriched_requirements.json")
        >>> result = ScopingDesigner().analyze_enriched(
        ...     em, project_name="ABC Portal", domain_context="ecommerce"
        ... )
        """
        logger.info("Starting synchronous enriched analysis")
        logger.info(f"  - Project: {project_name}")
        logger.info(f"  - Deployment: {deployment_target}")
        logger.info(f"  - Domain: {domain_context}")
        logger.info(f"  - Total requirements: {len(enriched.all_requirements)}")
        
        logger.info("Building ArchitectureInput from enriched modules...")
        inp = ArchitectureInput.from_enriched_modules(
            enriched, project_name=project_name,
            deployment_target=deployment_target,
            domain_context=domain_context,
            extra_constraints=extra_constraints,
        )
        
        logger.info("Calling LLM for architecture generation...")
        raw   = self._call_sync(inp, build_approach=build_approach, packaged_platforms=packaged_platforms)
        
        logger.info("Parsing LLM response...")
        out   = self._parse(raw, inp)
        
        logger.info("Attaching traceability information...")
        out   = self._attach_traceability_sync(out, enriched)
        
        logger.info("Synchronous enriched analysis complete")
        return out

    async def analyze_enriched_async(
        self,
        enriched: EnrichedModules,
        project_name: str = "the system",
        deployment_target: DeploymentTarget = DeploymentTarget.CLOUD,
        domain_context: Optional[str] = None,
        extra_constraints: Optional[list[str]] = None,
        build_approach: Optional[str] = None,
        packaged_platforms: Optional[list[str]] = None,
    ) -> ArchitectureOutput:
        """Async version of analyze_enriched — use in FastAPI routes."""
        logger.info("Starting async enriched analysis")
        logger.info(f"  - Project: {project_name}")
        logger.info(f"  - Deployment: {deployment_target}")
        logger.info(f"  - Domain: {domain_context}")
        logger.info(f"  - Total requirements: {len(enriched.all_requirements)}")
        
        logger.info("Building ArchitectureInput from enriched modules...")
        inp = ArchitectureInput.from_enriched_modules(
            enriched, project_name=project_name,
            deployment_target=deployment_target,
            domain_context=domain_context,
            extra_constraints=extra_constraints,
        )
        
        logger.info("Calling LLM for architecture generation (async)...")
        raw = await self._call_async(inp, build_approach=build_approach, packaged_platforms=packaged_platforms)
        
        logger.info("Parsing LLM response...")
        out = self._parse(raw, inp)
        
        logger.info("Attaching traceability information (async)...")
        out = await self._attach_traceability_async(out, enriched)
        
        logger.info("Async enriched analysis complete")
        return out

    # ── Public: flat / legacy path ────────────────────────────────────────────

    def analyze(self, input_: ArchitectureInput) -> ArchitectureOutput:
        """Synchronous flat-requirements analysis."""
        logger.info("Starting synchronous flat-requirements analysis")
        logger.info(f"  - Project: {input_.project_name}")
        logger.info(f"  - Requirements length: {len(input_.requirements)} chars")
        
        logger.info("Calling LLM for architecture generation...")
        raw = self._call_sync(input_)
        
        logger.info("Parsing LLM response...")
        result = self._parse(raw, input_)
        
        logger.info("Synchronous analysis complete")
        return result

    async def analyze_async(self, input_: ArchitectureInput) -> ArchitectureOutput:
        """Async flat-requirements analysis."""
        logger.info("Starting async flat-requirements analysis")
        logger.info(f"  - Project: {input_.project_name}")
        logger.info(f"  - Requirements length: {len(input_.requirements)} chars")
        
        logger.info("Calling LLM for architecture generation (async)...")
        raw = await self._call_async(input_)
        
        logger.info("Parsing LLM response...")
        result = self._parse(raw, input_)
        
        logger.info("Async analysis complete")
        return result

    def analyze_markdown(
        self,
        markdown: str,
        project_name: str = "the system",
        deployment_target: DeploymentTarget = DeploymentTarget.CLOUD,
        domain_context: Optional[str] = None,
    ) -> ArchitectureOutput:
        """Convenience: pass Phase 1 markdown directly."""
        inp = ArchitectureInput.from_rfp_output(
            markdown, project_name=project_name,
            deployment_target=deployment_target,
            domain_context=domain_context,
        )
        return self.analyze(inp)

    # ── Exporters ─────────────────────────────────────────────────────────────

    def export_markdown(self, output: ArchitectureOutput, path: Optional[str] = None) -> str:
        from .exporters import MarkdownExporter
        md = MarkdownExporter().export(output)
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(md)
            logger.info("Markdown → %s", path)
        return md

    def export_json(self, output: ArchitectureOutput, path: Optional[str] = None) -> str:
        from .exporters import JsonExporter
        js = JsonExporter().export(output)
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(js)
            logger.info("JSON → %s", path)
        return js

    # ── Traceability ──────────────────────────────────────────────────────────

    def _attach_traceability_sync(
        self, out: ArchitectureOutput, enriched: EnrichedModules
    ) -> ArchitectureOutput:
        """Run traceability pass synchronously and attach results to components."""
        logger.info("Running traceability pass (sync)...")
        try:
            trace_map = self._run_traceability_sync(out, enriched)
            self._apply_traceability(out, trace_map)
            logger.info(f"  - Traced {sum(len(v) for v in trace_map.values())} requirement-component links")
        except Exception as e:
            logger.warning("Traceability pass failed (non-fatal): %s", e)
        return out

    async def _attach_traceability_async(
        self, out: ArchitectureOutput, enriched: EnrichedModules
    ) -> ArchitectureOutput:
        logger.info("Running traceability pass (async)...")
        try:
            trace_map = await self._run_traceability_async(out, enriched)
            self._apply_traceability(out, trace_map)
            logger.info(f"  - Traced {sum(len(v) for v in trace_map.values())} requirement-component links")
        except Exception as e:
            logger.warning("Traceability pass failed (non-fatal): %s", e)
        return out

    def _build_traceability_inputs(
        self, out: ArchitectureOutput, enriched: EnrichedModules
    ) -> tuple[list[dict], list[str]]:
        req_ids = [
            {"id": r.id, "title": r.title, "module": r.module}
            for r in enriched.all_requirements
            if r.type in ("FR", "NFR", "CR")
        ]
        comp_names = [c.name for c in out.components]
        return req_ids, comp_names

    def _run_traceability_sync(
        self, out: ArchitectureOutput, enriched: EnrichedModules
    ) -> dict[str, list[str]]:
        req_ids, comp_names = self._build_traceability_inputs(out, enriched)
        # Estimate tokens: ~50 per requirement + ~30 per component
        estimated_tokens = len(req_ids) * 50 + len(comp_names) * 30 + 1000
        max_tokens = max(4000, min(estimated_tokens, 8000))
        
        client = self._get_sync_client()
        msg = client.messages.create(
            model=self.model, max_tokens=max_tokens,
            system=TRACEABILITY_SYSTEM,
            messages=[{"role": "user", "content": build_traceability_prompt(req_ids, comp_names)}],
        )
        text = "".join(getattr(block, "text", "") for block in msg.content)
        return self._parse_trace_response(text)

    async def _run_traceability_async(
        self, out: ArchitectureOutput, enriched: EnrichedModules
    ) -> dict[str, list[str]]:
        req_ids, comp_names = self._build_traceability_inputs(out, enriched)
        # Estimate tokens: ~50 per requirement + ~30 per component
        estimated_tokens = len(req_ids) * 50 + len(comp_names) * 30 + 1000
        max_tokens = max(4000, min(estimated_tokens, 8000))
        
        client = await self._get_async_client()
        msg = await client.messages.create(
            model=self.model, max_tokens=max_tokens,
            system=TRACEABILITY_SYSTEM,
            messages=[{"role": "user", "content": build_traceability_prompt(req_ids, comp_names)}],
        )
        text = "".join(getattr(block, "text", "") for block in msg.content)
        return self._parse_trace_response(text)

    @staticmethod
    def _parse_trace_response(text: str) -> dict[str, list[str]]:
        cleaned = text.replace("```json", "").replace("```", "").strip()
        trace_map: dict[str, list[str]] = {}
        for item in json.loads(cleaned):
            comp = item.get("component", "")
            req  = item.get("req_id", "")
            if comp and req:
                trace_map.setdefault(comp, [])
                if req not in trace_map[comp]:
                    trace_map[comp].append(req)
        return trace_map

    @staticmethod
    def _apply_traceability(
        out: ArchitectureOutput, trace_map: dict[str, list[str]]
    ) -> None:
        for comp in out.components:
            comp.source_requirements = trace_map.get(comp.name, [])

    # ── API clients (lazy init) ───────────────────────────────────────────────

    def _get_sync_client(self):
        if self._client is None:
            try:
                import anthropic
            except ImportError:
                raise ImportError("pip install anthropic")
            self._client = anthropic.Anthropic(api_key=self._api_key)
        return self._client

    async def _get_async_client(self):
        if self._aclient is None:
            try:
                import anthropic
            except ImportError:
                raise ImportError("pip install anthropic")
            self._aclient = anthropic.AsyncAnthropic(api_key=self._api_key)
        return self._aclient

    # ── API calls with retry ──────────────────────────────────────────────────

    def _extract_text_content(self, response: dict) -> str:
        content = response.get("content", [])
        if not content:
            raise ScopingDesignerError("LLM response did not contain any content.")
        text_parts = [
            item.get("text", "")
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        ]
        text = "".join(text_parts).strip()
        if not text:
            raise ScopingDesignerError("LLM response did not contain text content.")
        return text

    def _call_sync(self, input_: ArchitectureInput, build_approach: Optional[str] = None, packaged_platforms: Optional[list[str]] = None) -> dict:
        system = build_system_prompt(input_, build_approach=build_approach, packaged_platforms=packaged_platforms)

        for attempt in range(1, self.max_retries + 1):
            compact = attempt > 1 and input_.is_enriched
            logger.info("Building prompts...")
            user = build_user_prompt(input_, compact=compact)
            logger.info(f"  - System prompt: {len(system)} chars")
            logger.info(f"  - User prompt: {len(user)} chars")
            logger.info(f"  - Compact prompt mode: {compact}")

            try:
                logger.info(f"LLM API call attempt {attempt}/{self.max_retries}")
                logger.info(f"  - Max tokens: {self.max_tokens}")
                logger.info(f"  - Temperature: 0.2")

                response = asyncio.run(
                    llm_client.create_message(
                        messages=[{"role": "user", "content": user}],
                        system=system,
                        max_tokens=self.max_tokens,
                        temperature=0.2,
                    )
                )

                logger.info("LLM response received")
                if "usage" in response:
                    logger.info(f"  - Input tokens: {response['usage'].get('input_tokens', 'N/A')}")
                    logger.info(f"  - Output tokens: {response['usage'].get('output_tokens', 'N/A')}")

                return self._safe_json(self._extract_text_content(response))
            except Exception as e:
                if attempt == self.max_retries:
                    logger.error(f"API failed after {self.max_retries} attempts")
                    raise ScopingDesignerError(
                        f"API failed after {self.max_retries} attempts: {e}"
                    ) from e
                wait = self.retry_delay * (2 ** (attempt - 1))
                logger.warning("Attempt %d failed - retrying in %.1fs", attempt, wait)
                time.sleep(wait)
        raise ScopingDesignerError("Synchronous scoping generation exited without a result.")

    async def _call_async(self, input_: ArchitectureInput, build_approach: Optional[str] = None, packaged_platforms: Optional[list[str]] = None) -> dict:
        system = build_system_prompt(input_, build_approach=build_approach, packaged_platforms=packaged_platforms)

        for attempt in range(1, self.max_retries + 1):
            compact = attempt > 1 and input_.is_enriched
            logger.info("Building prompts...")
            user = build_user_prompt(input_, compact=compact)
            logger.info(f"  - System prompt: {len(system)} chars")
            logger.info(f"  - User prompt: {len(user)} chars")
            logger.info(f"  - Compact prompt mode: {compact}")

            try:
                logger.info(f"LLM API call attempt {attempt}/{self.max_retries} (async)")
                logger.info(f"  - Max tokens: {self.max_tokens}")
                logger.info(f"  - Temperature: 0.2")

                response = await llm_client.create_message(
                    messages=[{"role": "user", "content": user}],
                    system=system,
                    max_tokens=self.max_tokens,
                    temperature=0.2,
                )

                logger.info("LLM response received")
                if "usage" in response:
                    logger.info(f"  - Input tokens: {response['usage'].get('input_tokens', 'N/A')}")
                    logger.info(f"  - Output tokens: {response['usage'].get('output_tokens', 'N/A')}")

                return self._safe_json(self._extract_text_content(response))
            except Exception as e:
                if attempt == self.max_retries:
                    logger.error(f"Async API failed after {self.max_retries} attempts")
                    raise ScopingDesignerError(
                        f"Async API failed after {self.max_retries} attempts: {e}"
                    ) from e
                wait = self.retry_delay * (2 ** (attempt - 1))
                logger.warning("Attempt %d failed — retrying in %.1fs", attempt, wait)
                await asyncio.sleep(wait)
        raise ScopingDesignerError("Async scoping generation exited without a result.")

    @staticmethod
    def _safe_json(text: str) -> dict:
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
        
        # Try parsing as-is first
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning(f"Initial JSON parse failed: {e}, attempting fixes...")
            
            # Common fix: Remove trailing commas before closing brackets/braces
            import re
            fixed = re.sub(r',(\s*[}\]])', r'\1', cleaned)
            
            try:
                return json.loads(fixed)
            except json.JSONDecodeError:
                # Try to repair truncated JSON by closing open structures
                logger.info("Attempting to repair truncated JSON...")
                repaired = fixed
                
                # Count unclosed brackets and braces
                open_braces = repaired.count('{') - repaired.count('}')
                open_brackets = repaired.count('[') - repaired.count(']')
                open_quotes = repaired.count('"') % 2
                
                # Close any open string
                if open_quotes == 1:
                    repaired += '"'
                
                # Close any open arrays
                for _ in range(open_brackets):
                    repaired += ']'
                
                # Close any open objects
                for _ in range(open_braces):
                    repaired += '}'
                
                # Remove trailing commas again after repair
                repaired = re.sub(r',(\s*[}\]])', r'\1', repaired)
                
                try:
                    logger.info("Successfully repaired truncated JSON")
                    return json.loads(repaired)
                except json.JSONDecodeError:
                    # Try to find and extract valid JSON
                    # Look for the outermost { } pair
                    start = fixed.find('{')
                    if start != -1:
                        # Find matching closing brace
                        depth = 0
                        for i in range(start, len(fixed)):
                            if fixed[i] == '{':
                                depth += 1
                            elif fixed[i] == '}':
                                depth -= 1
                                if depth == 0:
                                    try:
                                        return json.loads(fixed[start:i+1])
                                    except json.JSONDecodeError:
                                        pass
                    
                    # If all fixes fail, raise original error with context
                    logger.error(f"JSON parsing failed. Raw response length: {len(text)}")
                    logger.error(f"First 1000 chars:\n{text[:1000]}")
                    logger.error(f"Last 500 chars:\n{text[-500:]}")
                    raise ScopingDesignerError(
                        f"API returned invalid JSON: {e}\n\n"
                        f"Raw (first 500 chars):\n{text[:500]}\n\n"
                        f"Raw (last 200 chars):\n{text[-200:]}"
                    ) from e

    # ── Response → dataclass mapping ─────────────────────────────────────────

    @staticmethod
    def _parse(data: dict, input_: ArchitectureInput) -> ArchitectureOutput:
        logger.info("Parsing architecture output...")
        
        domains = [
            Domain(
                name=d["name"], icon=d.get("icon", "box"), color=d.get("color", "blue"),
                requirements=d.get("requirements", []),
                count=d.get("count", len(d.get("requirements", []))),
            )
            for d in data.get("domains", [])
        ]
        logger.info(f"  - Parsed {len(domains)} domains")

        ctx_raw = data.get("systemContext", {})
        actors  = [
            Actor(
                name=a["name"],
                type=ActorType(a.get("type", "external_system")),
                description=a.get("description", ""),
            )
            for a in ctx_raw.get("actors", [])
        ]
        system_context = SystemContext(
            description=ctx_raw.get("description", ""),
            actors=actors,
            integrations=ctx_raw.get("integrations", []),
        )

        arch_raw = data.get("architecture", {})
        architecture = ArchitecturePattern(
            recommended=arch_raw.get("recommended", ""),
            rationale=arch_raw.get("rationale", ""),
            domain_note=arch_raw.get("domainNote"),
            key_principles=arch_raw.get("keyPrinciples", []),
            alternatives=[
                ArchitectureAlternative(name=a["name"], tradeoff=a["tradeoff"])
                for a in arch_raw.get("alternatives", [])
            ],
            layers=[
                ArchitectureLayer(layer=l["layer"], components=l.get("components", []))
                for l in arch_raw.get("layerDiagram", [])
            ],
        )

        components = []
        for c in data.get("components", []):
            sp_raw = c.get("storyPointRange") or c.get("story_point_range")
            sp = StoryPointRange.from_dict(sp_raw) if sp_raw else None
            components.append(Component(
                name=c["name"],
                type=ComponentType(c.get("type", "Backend Service")),
                description=c.get("description", ""),
                complexity=Complexity(c.get("complexity", "Medium")),
                complexity_reason=c.get("complexityReason", c.get("complexity_reason", "")),
                compliance_impacted=c.get("complianceImpacted", c.get("compliance_impacted", False)),
                dependencies=c.get("dependencies", []),
                estimation_signals=c.get("estimationSignals", c.get("estimation_signals", [])),
                module=c.get("module"),
                impl_type=c.get("implType", c.get("impl_type")),
                actors=c.get("actors", []),
                source_requirements=c.get("sourceRequirements", c.get("source_requirements", [])),
                story_point_range=sp,
            ))

        risks = [
            ArchitectureRisk(
                risk=r["risk"],
                level=RiskLevel(r.get("level", "Medium")),
                mitigation=r.get("mitigation", ""),
                ref_id=r.get("refId", r.get("ref_id")),
                module=r.get("module"),
            )
            for r in data.get("risks", [])
        ]

        s = data.get("summary", {})
        total_sp_mid = sum(
            c.story_point_range.mid if c.story_point_range else 0
            for c in components
        )
        summary = ArchitectureSummary(
            domain_count=s.get("domainCount", len(domains)),
            actor_count=s.get("actorCount", len(actors)),
            component_count=s.get("componentCount", len(components)),
            open_ambiguities=s.get("openAmbiguities", 0),
            avg_complexity=s.get("avgComplexity", "Medium"),
            compliance_components=s.get("complianceComponents", sum(1 for c in components if c.compliance_impacted)),
            total_story_points_mid=s.get("totalStorypointsMid", total_sp_mid),
        )

        return ArchitectureOutput(
            input=input_, domains=domains, system_context=system_context,
            architecture=architecture, components=components,
            risks=risks, summary=summary,
        )

    @staticmethod
    def from_dict(data: dict) -> ArchitectureOutput:
        """
        Reconstruct ArchitectureOutput from a dict (e.g., from API response).
        Useful for export endpoints that receive the full JSON output.
        
        Example
        -------
        >>> output_dict = result.to_dict()
        >>> reconstructed = ArchitectureDesigner.from_dict(output_dict)
        """
        logger.info("Reconstructing ArchitectureOutput from dict...")
        
        # Reconstruct ArchitectureInput
        input_data = data.get("input", {})
        if isinstance(input_data, dict):
            deployment = DeploymentTarget(data.get("deployment_target", "cloud"))
            arch_input = ArchitectureInput(
                requirements=input_data.get("requirements", ""),
                project_name=data.get("project_name", "the system"),
                deployment_target=deployment,
                domain_context=input_data.get("domain_context"),
                extra_constraints=input_data.get("extra_constraints", []),
            )
        else:
            # Fallback if input is not provided
            deployment = DeploymentTarget(data.get("deployment_target", "cloud"))
            arch_input = ArchitectureInput(
                requirements="",
                project_name=data.get("project_name", "the system"),
                deployment_target=deployment,
            )
        
        # Use existing _parse method with the reconstructed input
        return ScopingDesigner._parse(data, arch_input)
