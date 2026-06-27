"""
Requirement Enricher — Automatic Phase 1.5 enrichment

Parses Phase 1 markdown requirements and enriches them with:
- Module mapping (which functional area)
- Implementation type (custom build, 3rd-party, etc.)
- Actors (who it serves)
- Dependency direction (relationships between requirements)

This module replicates the logic from rfp_requirement_enricher.html
but runs server-side for automatic enrichment.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Optional, Any
from dataclasses import dataclass, field

from .models import EnrichedModules, EnrichedRequirement, ImplType

logger = logging.getLogger(__name__)

# Module definitions
MODULES = [
    'identity_access', 'product_catalog', 'cart_checkout', 
    'content_management', 'integrations', 'compliance_privacy', 'platform_nfr'
]

MODULE_LABELS = {
    'identity_access': 'Identity & access',
    'product_catalog': 'Product catalog',
    'cart_checkout': 'Cart & checkout',
    'content_management': 'Content management',
    'integrations': 'Integrations',
    'compliance_privacy': 'Compliance & privacy',
    'platform_nfr': 'Platform NFRs'
}

IMPL_TYPES = ['custom_build', 'third_party_integration', 'configuration', 'compliance_control', 'not_applicable']
ACTORS = ['customer', 'admin', 'guest', 'system', 'all']
DEP_DIRS = ['depends_on', 'depended_by', 'bidirectional', 'none']


@dataclass
class ParsedRequirement:
    """Intermediate parsed requirement before enrichment."""
    id: str
    type: str
    title: str
    priority: str = "MUST"
    confidence: Optional[int] = None
    section: str = ""
    description: str = ""
    is_ambiguous: bool = False
    clarification: str = ""
    related_ids: list[str] = field(default_factory=list)


class RequirementEnricher:
    """
    Enriches Phase 1 markdown requirements with module, impl_type, and actors.
    
    Uses LLM to classify requirements into functional modules and determine
    implementation approach.
    """
    
    ENRICHMENT_SYSTEM_PROMPT = """You are a senior solutions architect enriching a software requirement model for architecture generation.

For each requirement, add three fields:
1. "module" — which functional module this belongs to. Choose ONE from: identity_access | product_catalog | cart_checkout | content_management | integrations | compliance_privacy | platform_nfr
2. "impl_type" — how it will be implemented. Choose ONE from: custom_build | third_party_integration | configuration | compliance_control | not_applicable
3. "actors" — who this serves. Array, choose from: customer | admin | guest | system | all

Rules for module mapping:
- identity_access: authentication, login, registration, RBAC, password, sessions, social login
- product_catalog: products, search, filtering, categories, SKUs, inventory browsing  
- cart_checkout: cart, orders, payments, checkout flow, order tracking, email notifications for orders
- content_management: blog, admin dashboard, CMS, image gallery, SEO, content pages
- integrations: third-party services — analytics, CRM, email service, social auth APIs
- compliance_privacy: GDPR, CCPA, PCI DSS, cookie consent, privacy pages, SSL, security audits, WCAG
- platform_nfr: performance, uptime, scalability, hosting, backups, browser compat, responsive design

Rules for impl_type:
- custom_build: logic that must be written from scratch (auth flows, business logic, UI components)
- third_party_integration: wrapping an external API or service (Stripe, PayPal, SendGrid, Google Analytics, CRM)
- configuration: setting up infrastructure or tooling with minimal custom code (SSL cert, hosting setup, analytics tag)
- compliance_control: legal or regulatory requirement satisfied by policy + tooling (GDPR consent, PCI tokenization via Stripe)
- not_applicable: ambiguities, risks, or meta-requirements that aren't directly built

Rules for actors:
- customer: end users browsing, buying, managing accounts
- admin: staff managing content, orders, products
- guest: unauthenticated users
- system: automated/background processes (email sending, backups, analytics)
- all: applies to everyone (accessibility, performance)

Respond ONLY with a JSON array. Each object must have: "id", "module", "impl_type", "actors". No other keys. No preamble.

Example:
[{"id":"FR-001","module":"identity_access","impl_type":"custom_build","actors":["customer","guest"]},{"id":"NFR-001","module":"platform_nfr","impl_type":"configuration","actors":["all"]}]"""

    DEPENDENCY_SYSTEM_PROMPT = """You are a solutions architect. For each pair of related requirements, determine the dependency direction.

"depends_on" = this requirement cannot work without the related requirement
"depended_by" = this requirement is a prerequisite the related requirement needs
"bidirectional" = they have mutual dependency or are tightly coupled
"none" = they are related by domain but not technically dependent

Respond ONLY with a JSON array. Each object: {"id": string, "related": string, "direction": "depends_on"|"depended_by"|"bidirectional"|"none"}. No preamble."""

    DEFAULT_ENRICHMENT_CHUNK_SIZE = 8   # Further reduced to prevent JSON truncation
    MIN_ENRICHMENT_CHUNK_SIZE = 3       # Minimum chunk size for retry logic
    MAX_TOKENS_PER_REQUIREMENT = 150    # Estimated tokens per requirement in response

    def __init__(self, llm_client: Any = None):
        """
        Initialize enricher.
        
        Args:
            llm_client: Optional LLM client. If None, uses the global llm_client.
        """
        self.llm_client = llm_client
        if self.llm_client is None:
            from llm_client import llm_client as global_client
            self.llm_client = global_client
    
    def _estimate_response_tokens(self, num_requirements: int) -> int:
        """
        Estimate the number of tokens needed for the response.
        Each requirement typically needs ~150 tokens in the JSON response.
        """
        return num_requirements * self.MAX_TOKENS_PER_REQUIREMENT + 500  # +500 for JSON structure
    
    def _normalize_markdown(self, markdown: str) -> str:
        """
        Normalize uploaded markdown to reduce encoding artifacts that can confuse
        downstream prompting and parsing.
        """
        if not markdown:
            return markdown

        replacements = {
            "\u2014": "-",
            "\u2013": "-",
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u00a0": " ",
            "\ufffd": "",
            "�?": "-",
            "�s�": "-",
        }

        normalized = markdown.replace("\r\n", "\n").replace("\r", "\n")
        for old, new in replacements.items():
            normalized = normalized.replace(old, new)

        normalized = re.sub(r"[ \t]+", " ", normalized)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        return normalized.strip()

    def _extract_text_from_response(self, response: dict[str, Any]) -> str:
        """Extract text content from the LLM response payload."""
        content = response.get("content", [])
        text_parts: list[str] = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text_parts.append(item.get("text", ""))
            elif hasattr(item, "type") and getattr(item, "type", None) == "text":
                text_parts.append(getattr(item, "text", ""))

        text = "".join(text_parts).strip()
        if not text:
            raise ValueError("LLM response did not contain text content.")
        return text

    def _safe_json_loads(self, text: str, context: str) -> Any:
        """
        Parse LLM JSON defensively. Handles fenced code blocks, trailing commas,
        truncated strings, and extra wrapper text.
        """
        cleaned = text.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1] if lines and lines[-1].strip() == "```" else lines[1:]).strip()

        cleaned = cleaned.replace("```json", "").replace("```", "").strip()

        def _try_load(candidate: str) -> Any:
            return json.loads(candidate)

        try:
            return _try_load(cleaned)
        except json.JSONDecodeError as original_error:
            logger.warning("%s JSON parse failed: %s", context, original_error)

            fixed = re.sub(r",(\s*[}\]])", r"\1", cleaned)

            try:
                return _try_load(fixed)
            except json.JSONDecodeError:
                repaired = fixed

                open_quotes = repaired.count('"') % 2
                open_braces = repaired.count("{") - repaired.count("}")
                open_brackets = repaired.count("[") - repaired.count("]")

                if open_quotes == 1:
                    repaired += '"'
                if open_brackets > 0:
                    repaired += "]" * open_brackets
                if open_braces > 0:
                    repaired += "}" * open_braces

                repaired = re.sub(r",(\s*[}\]])", r"\1", repaired)

                try:
                    logger.info("Recovered malformed JSON for %s via repair", context)
                    return _try_load(repaired)
                except json.JSONDecodeError:
                    array_match = re.search(r"\[\s*{.*}\s*]", fixed, re.DOTALL)
                    if array_match:
                        try:
                            logger.info("Recovered malformed JSON for %s via array extraction", context)
                            return _try_load(array_match.group(0))
                        except json.JSONDecodeError:
                            pass

                    object_match = re.search(r"{.*}", fixed, re.DOTALL)
                    if object_match:
                        try:
                            logger.info("Recovered malformed JSON for %s via object extraction", context)
                            return _try_load(object_match.group(0))
                        except json.JSONDecodeError:
                            pass

                    logger.error("%s JSON parsing failed. Raw response length: %d", context, len(text))
                    logger.error("%s raw response start:\n%s", context, text[:1000])
                    logger.error("%s raw response end:\n%s", context, text[-500:])
                    raise ValueError(f"{context} returned invalid JSON: {original_error}") from original_error

    def parse_markdown(self, markdown: str) -> list[ParsedRequirement]:
        """
        Parse Phase 1 markdown into structured requirements.
        
        Args:
            markdown: Phase 1 markdown output with ### FR-001 — Title format
            
        Returns:
            List of ParsedRequirement objects
        """
        logger.info("Parsing markdown requirements...")
        requirements = []
        markdown = self._normalize_markdown(markdown)
        
        # Split by requirement headers (### FR-001, ### NFR-001, etc.)
        sections = re.split(r'\n### ', "\n" + markdown)
        
        for section in sections[1:]:  # Skip first empty section
            lines = section.strip().split('\n')
            if not lines:
                continue
                
            header_line = lines[0]
            
            # Extract ID (FR-001, IBM-FR-001, NFR-001, CR-001, AMB-001, RISK-001)
            id_match = re.match(r'^((?:IBM-)?(?:FR|NFR|CR|AMB|RISK)-\d+)', header_line)
            if not id_match:
                continue
                
            req_id = id_match.group(1)
            req_type = req_id.split('-')[0]
            
            # Extract title (after ID and separator)
            title_part = re.sub(r'^((?:IBM-)?(?:FR|NFR|CR|AMB|RISK)-\d+)\s*[—–-]\s*', '', header_line)
            title_part = re.sub(r'⚠.*$', '', title_part).strip()
            
            is_ambiguous = '⚠' in header_line
            
            # Parse metadata from lines
            priority = 'MUST'
            confidence = None
            section_ref = ''
            description = ''
            clarification = ''
            related_raw = ''
            
            for line in lines[1:]:
                if '**Priority:**' in line:
                    priority = re.sub(r'.*\*\*Priority:\*\*\s*', '', line).strip().upper()
                elif '**Confidence:**' in line:
                    conf_str = re.sub(r'.*\*\*Confidence:\*\*\s*', '', line).replace('%', '').strip()
                    try:
                        confidence = int(conf_str)
                    except ValueError:
                        pass
                elif '**Section:**' in line:
                    section_ref = re.sub(r'.*\*\*Section:\*\*\s*', '', line).strip()
                elif line.startswith('> **Clarification'):
                    clarification = re.sub(r'^>\s*\*\*Clarification needed:\*\*\s*', '', line).strip()
                elif line.startswith('_Related:'):
                    related_raw = re.sub(r'_Related:\s*', '', line).replace('_', '').strip()
                elif line and not line.startswith('-') and not line.startswith('>') and not line.startswith('_'):
                    if len(description) < 300:
                        if description:
                            description += ' '
                        description += line.strip()
            
            # Parse related IDs
            related_ids = []
            if related_raw:
                related_ids = [r.strip() for r in related_raw.split(',') if r.strip()]
            
            requirements.append(ParsedRequirement(
                id=req_id,
                type=req_type,
                title=title_part,
                priority=priority,
                confidence=confidence,
                section=section_ref,
                description=description.strip(),
                is_ambiguous=is_ambiguous,
                clarification=clarification,
                related_ids=related_ids
            ))
        
        logger.info(f"  - Parsed {len(requirements)} requirements")
        logger.info(f"  - Types: FR={sum(1 for r in requirements if r.type=='FR')}, "
                   f"NFR={sum(1 for r in requirements if r.type=='NFR')}, "
                   f"CR={sum(1 for r in requirements if r.type=='CR')}, "
                   f"AMB={sum(1 for r in requirements if r.type=='AMB')}, "
                   f"RISK={sum(1 for r in requirements if r.type=='RISK')}")
        
        return requirements
    
    def _chunk_requirements(
        self,
        requirements: list[ParsedRequirement],
        chunk_size: int,
    ) -> list[list[ParsedRequirement]]:
        """Split requirements into stable chunks for LLM enrichment."""
        return [
            requirements[i:i + chunk_size]
            for i in range(0, len(requirements), chunk_size)
        ]

    def _default_enrichment_for(self, req: ParsedRequirement) -> dict[str, Any]:
        """
        Deterministic fallback when LLM output for a chunk cannot be recovered.
        Conservative defaults keep the pipeline moving.
        """
        req_type = req.type.upper()
        title_desc = f"{req.title} {req.description}".lower()

        if req_type == "NFR":
            module = "platform_nfr"
            actors = ["all"]
        elif req_type in {"CR", "AMB", "RISK"}:
            module = "compliance_privacy" if any(
                token in title_desc for token in ["compliance", "privacy", "regulatory", "audit", "gdpr", "pci", "sox"]
            ) else "platform_nfr"
            actors = ["admin"]
        elif any(token in title_desc for token in ["integration", "api", "interface", "sync", "mes", "fccs", "payroll"]):
            module = "integrations"
            actors = ["system", "admin"]
        else:
            module = "platform_nfr"
            actors = ["admin", "system"]

        if req_type in {"AMB", "RISK"}:
            impl_type = "not_applicable"
        elif module == "integrations":
            impl_type = "third_party_integration"
        elif req_type == "CR":
            impl_type = "compliance_control"
        else:
            impl_type = "custom_build"

        return {
            "id": req.id,
            "module": module,
            "impl_type": impl_type,
            "actors": actors,
        }

    async def _enrich_chunk_with_retry(
        self,
        requirements: list[ParsedRequirement],
        chunk_size: int,
        label: str,
    ) -> list[dict[str, Any]]:
        """
        Enrich a chunk of requirements. If JSON is truncated, recursively retry
        with smaller chunks. Final fallback uses deterministic defaults.
        """
        if not requirements:
            return []

        payload = [
            {"id": r.id, "title": r.title, "description": r.description, "type": r.type}
            for r in requirements
        ]
        prompt = f"Enrich these requirements:\n{json.dumps(payload, indent=2)}"
        
        # Calculate required tokens dynamically
        estimated_tokens = self._estimate_response_tokens(len(requirements))
        max_tokens = max(8000, estimated_tokens)  # Minimum 8000, or estimated requirement

        try:
            raw = await self._call_llm(self.ENRICHMENT_SYSTEM_PROMPT, prompt, max_tokens=max_tokens)
            parsed = self._safe_json_loads(raw, label)
            if not isinstance(parsed, list):
                raise ValueError(f"{label} response must be a JSON array.")
            return [item for item in parsed if isinstance(item, dict) and item.get("id")]
        except Exception as e:
            logger.warning("%s failed for %d requirements: %s", label, len(requirements), e)

            if len(requirements) <= self.MIN_ENRICHMENT_CHUNK_SIZE:
                logger.warning(
                    "%s falling back to deterministic enrichment for %d requirements",
                    label,
                    len(requirements),
                )
                return [self._default_enrichment_for(req) for req in requirements]

            # Adaptive chunk size reduction - more aggressive for larger chunks
            if len(requirements) > 10:
                next_chunk_size = max(self.MIN_ENRICHMENT_CHUNK_SIZE, len(requirements) // 3)
            else:
                next_chunk_size = max(self.MIN_ENRICHMENT_CHUNK_SIZE, len(requirements) // 2)
            
            logger.info(
                "%s retrying with smaller chunks (current=%d, next=%d)",
                label,
                len(requirements),
                next_chunk_size,
            )

            results: list[dict[str, Any]] = []
            subchunks = self._chunk_requirements(requirements, next_chunk_size)
            for index, subchunk in enumerate(subchunks, start=1):
                results.extend(
                    await self._enrich_chunk_with_retry(
                        subchunk,
                        next_chunk_size,
                        f"{label}.{index}",
                    )
                )
            return results

    async def enrich_requirements(self, requirements: list[ParsedRequirement]) -> list[EnrichedRequirement]:
        """
        Enrich parsed requirements with module, impl_type, and actors using LLM.
        
        Args:
            requirements: List of parsed requirements
            
        Returns:
            List of EnrichedRequirement objects
        """
        logger.info("Enriching requirements with LLM...")
        
        # Split into coarse groups, then chunk each group to avoid token truncation
        fr_nfr = [r for r in requirements if r.type in ['FR', 'NFR']]
        cr_amb_risk = [r for r in requirements if r.type in ['CR', 'AMB', 'RISK']]
        
        logger.info(f"  - Group 1: {len(fr_nfr)} FR/NFR requirements")
        logger.info(f"  - Group 2: {len(cr_amb_risk)} CR/AMB/RISK requirements")
        logger.info(f"  - Default chunk size: {self.DEFAULT_ENRICHMENT_CHUNK_SIZE}")
        logger.info("Calling LLM for enrichment with chunking...")
        
        enrich_map = {}

        result1 = await self._enrich_chunk_with_retry(
            fr_nfr,
            self.DEFAULT_ENRICHMENT_CHUNK_SIZE,
            "Requirement enrichment batch 1",
        )
        result2 = await self._enrich_chunk_with_retry(
            cr_amb_risk,
            self.DEFAULT_ENRICHMENT_CHUNK_SIZE,
            "Requirement enrichment batch 2",
        )

        for item in result1 + result2:
            if isinstance(item, dict) and item.get('id'):
                enrich_map[item['id']] = item

        logger.info(f"  - Enriched {len(enrich_map)} requirements")
        
        # Build enriched requirements
        enriched = []
        for req in requirements:
            enrich_data = enrich_map.get(req.id, {})
            
            # Map impl_type string to ImplType enum
            impl_type_str = enrich_data.get('impl_type')
            impl_type = None
            if impl_type_str:
                try:
                    impl_type = ImplType(impl_type_str)
                except ValueError:
                    logger.warning(f"Unknown impl_type '{impl_type_str}' for {req.id}, using None")
            
            enriched.append(EnrichedRequirement(
                id=req.id,
                type=req.type,
                title=req.title,
                description=req.description,
                priority=req.priority,
                confidence=req.confidence,
                is_ambiguous=req.is_ambiguous,
                clarification=req.clarification,
                related_ids=req.related_ids,
                module=enrich_data.get('module'),
                impl_type=impl_type,
                actors=enrich_data.get('actors', []),
                dependency_direction={}
            ))
        
        return enriched
    
    async def infer_dependencies(self, requirements: list[EnrichedRequirement]) -> None:
        """
        Infer dependency directions between related requirements.
        Modifies requirements in-place.
        
        Args:
            requirements: List of enriched requirements
        """
        logger.info("Inferring dependency directions...")
        
        # Build dependency pairs from related_ids
        dep_pairs = []
        req_map = {r.id: r for r in requirements}
        
        for req in requirements:
            if req.type == 'FR' and req.related_ids:
                for related_id in req.related_ids[:3]:  # Limit to 3 per requirement
                    related_req = req_map.get(related_id)
                    if related_req:
                        dep_pairs.append({
                            "id": req.id,
                            "related": related_id,
                            "titles": f"{req.title} <-> {related_req.title}"
                        })
        
        if not dep_pairs:
            logger.info("  - No dependency pairs to process")
            return
        
        # Limit to first 20 pairs to avoid token limits
        dep_pairs = dep_pairs[:20]
        logger.info(f"  - Processing {len(dep_pairs)} dependency pairs")
        
        try:
            dep_prompt = f"Determine dependency direction for these pairs:\n{json.dumps(dep_pairs, indent=2)}"
            dep_raw = await self._call_llm(self.DEPENDENCY_SYSTEM_PROMPT, dep_prompt)
            
            dep_results = self._safe_json_loads(dep_raw, "Dependency inference")
            
            # Apply dependency directions
            for item in dep_results:
                req_id = item.get('id')
                related_id = item.get('related')
                direction = item.get('direction')
                
                if req_id and related_id and direction:
                    req = req_map.get(req_id)
                    if req:
                        req.dependency_direction[related_id] = direction
            
            logger.info(f"  - Applied {len(dep_results)} dependency directions")
            
        except Exception as e:
            logger.warning(f"Dependency inference failed (non-fatal): {e}")
    
    async def enrich_markdown(self, markdown: str) -> EnrichedModules:
        """
        Complete enrichment pipeline: parse markdown → enrich → infer dependencies.
        
        Args:
            markdown: Phase 1 markdown output
            
        Returns:
            EnrichedModules object ready for architecture generation
        """
        logger.info("=" * 70)
        logger.info("Starting automatic requirement enrichment")
        logger.info("=" * 70)
        
        # Step 1: Parse markdown
        parsed = self.parse_markdown(markdown)
        if not parsed:
            raise ValueError("No requirements found in markdown. Check format (### FR-001 — Title)")
        
        # Step 2: Enrich with LLM
        enriched = await self.enrich_requirements(parsed)
        
        # Step 3: Infer dependencies
        await self.infer_dependencies(enriched)
        
        # Step 4: Group by module
        modules = {}
        for module_name in MODULES:
            modules[module_name] = []
        modules['unclassified'] = []
        
        for req in enriched:
            if req.module and req.module in modules:
                modules[req.module].append(req)
            else:
                modules['unclassified'].append(req)
        
        # Remove empty modules
        modules = {k: v for k, v in modules.items() if v}
        
        logger.info("Enrichment complete")
        logger.info(f"  - Total requirements: {len(enriched)}")
        logger.info(f"  - Modules: {len(modules)}")
        logger.info(f"  - Module breakdown:")
        for module_name, reqs in modules.items():
            logger.info(f"    - {MODULE_LABELS.get(module_name, module_name)}: {len(reqs)} requirements")
        logger.info("=" * 70)
        
        return EnrichedModules(
            modules=modules,
            total=len(enriched),
            generated_at="",
            phase="1.5_enriched_auto"
        )
    
    async def _call_llm(self, system_prompt: str, user_prompt: str, max_tokens: int = 8000) -> str:
        """
        Call LLM and return cleaned response text.
        
        Args:
            system_prompt: System prompt for the LLM
            user_prompt: User prompt for the LLM
            max_tokens: Maximum tokens for the response (default: 8000)
        """
        if self.llm_client is None:
            raise RuntimeError("RequirementEnricher LLM client is not configured.")
        
        logger.info(f"  - Calling LLM with max_tokens={max_tokens}")
        response = await self.llm_client.create_message(
            messages=[{"role": "user", "content": user_prompt}],
            system=system_prompt,
            max_tokens=max_tokens,
            temperature=0.2
        )
        
        return self._extract_text_from_response(response)

# Made with Bob
