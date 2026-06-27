"""
Data models for the Architecture Designer module.
All models use plain dataclasses — zero external dependencies.

v1.2 additions (Phase 1.5 enrichment support):
  - Component: module, impl_type, actors, source_requirements, story_point_range
  - ArchitectureRisk: module field
  - ArchitectureSummary: total_story_points_mid
  - EnrichedModules: typed container for Phase 1.5 grouped input
  - ArchitectureInput: from_enriched_modules() factory
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional
import json


# ── Enumerations ──────────────────────────────────────────────────────────────

class DeploymentTarget(str, Enum):
    CLOUD   = "cloud"
    ON_PREM = "on_prem"
    HYBRID  = "hybrid"
    SAAS    = "saas"

    def label(self) -> str:
        return {"cloud": "Cloud (AWS / Azure / GCP)", "on_prem": "On-premise",
                "hybrid": "Hybrid", "saas": "SaaS / multi-tenant"}[self.value]


class Complexity(str, Enum):
    LOW    = "Low"
    MEDIUM = "Medium"
    HIGH   = "High"


class ActorType(str, Enum):
    HUMAN           = "human"
    INTERNAL_SYSTEM = "internal_system"
    EXTERNAL_SYSTEM = "external_system"


class ComponentType(str, Enum):
    FRONTEND    = "Frontend"
    BACKEND     = "Backend Service"
    API_GATEWAY = "API Gateway"
    DATA_STORE  = "Data Store"
    AI_ML       = "AI/ML"
    INTEGRATION = "Integration"
    SECURITY    = "Security"
    INFRA       = "Infrastructure"
    COMPLIANCE  = "Compliance"
    
    # SAP-specific component types
    SAP_STANDARD_MODULE = "SAP Standard Module"
    SAP_FIORI_APP = "SAP Fiori App"
    SAP_ENHANCEMENT = "SAP Enhancement"
    
    # Generic platform types (for future Salesforce, ServiceNow, etc.)
    PLATFORM_STANDARD = "Platform Standard Module"
    PLATFORM_CONFIG = "Platform Configuration"
    PLATFORM_EXTENSION = "Platform Extension"


class RiskLevel(str, Enum):
    HIGH   = "High"
    MEDIUM = "Medium"
    LOW    = "Low"


class ImplType(str, Enum):
    """Implementation type — inherited from Phase 1.5 enrichment."""
    CUSTOM_BUILD           = "custom_build"
    THIRD_PARTY_INTEGRATION = "third_party_integration"
    CONFIGURATION          = "configuration"
    COMPLIANCE_CONTROL     = "compliance_control"
    NOT_APPLICABLE         = "not_applicable"
    
    # SAP-specific implementation types
    SAP_STANDARD_CONFIG    = "sap_standard_config"      # Standard SAP module configuration (20-60 SP)
    SAP_CUSTOM_ENHANCEMENT = "sap_custom_enhancement"   # ABAP/Fiori enhancements (13-89 SP)
    SAP_ABAP_DEVELOPMENT   = "sap_abap_development"     # Custom ABAP development (21-89 SP)
    SAP_FIORI_CUSTOM       = "sap_fiori_custom"         # Custom Fiori apps (13-55 SP)
    
    # Generic platform types (for future expansion)
    PLATFORM_STANDARD_CONFIG = "platform_standard_config"  # Standard platform configuration
    PLATFORM_CUSTOM_CODE     = "platform_custom_code"      # Custom code on platform


# ── Story point range ─────────────────────────────────────────────────────────

@dataclass
class StoryPointRange:
    """Fibonacci-scale story point estimate: low (optimistic), mid (realistic), high (worst-case)."""
    low:  int = 0
    mid:  int = 0
    high: int = 0

    def to_dict(self) -> dict:
        return {"low": self.low, "mid": self.mid, "high": self.high}

    @classmethod
    def from_dict(cls, d: dict) -> "StoryPointRange":
        return cls(low=d.get("low", 0), mid=d.get("mid", 0), high=d.get("high", 0))


# ── Enriched requirement (Phase 1.5 output) ───────────────────────────────────

@dataclass
class EnrichedRequirement:
    """
    Single requirement as enriched by Phase 1.5.
    Maps to one entry in the modules dict from rfp_enriched_requirements.json.
    """
    id:            str
    type:          str                      # FR | NFR | CR | AMB | RISK
    title:         str
    priority:      str = "MUST"
    confidence:    Optional[int] = None
    description:   str = ""
    is_ambiguous:  bool = False
    clarification: str = ""
    related_ids:   list[str] = field(default_factory=list)
    module:        Optional[str] = None     # identity_access | cart_checkout | …
    impl_type:     Optional[str] = None     # custom_build | third_party_integration | …
    actors:        list[str] = field(default_factory=list)
    dependency_direction: dict[str, str] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, d: dict) -> "EnrichedRequirement":
        return cls(
            id=d.get("id", ""),
            type=d.get("type", "FR"),
            title=d.get("title", ""),
            priority=d.get("priority", "MUST"),
            confidence=d.get("confidence"),
            description=d.get("description", ""),
            is_ambiguous=d.get("is_ambiguous", False),
            clarification=d.get("clarification", ""),
            related_ids=d.get("related_ids", []),
            module=d.get("module"),
            impl_type=d.get("impl_type"),
            actors=d.get("actors", []),
            dependency_direction=d.get("dependency_direction", {}),
        )


@dataclass
class EnrichedModules:
    """
    Container for the full Phase 1.5 output — requirements grouped by functional module.
    Constructed from rfp_enriched_requirements.json.
    """
    modules:      dict[str, list[EnrichedRequirement]]
    total:        int = 0
    generated_at: str = ""
    phase:        str = "1.5_enriched"

    # ── Module label map ──────────────────────────────────────────────────────
    MODULE_LABELS: dict = field(default_factory=lambda: {
        "identity_access":    "Identity & access",
        "product_catalog":    "Product catalog",
        "cart_checkout":      "Cart & checkout",
        "content_management": "Content management",
        "integrations":       "Integrations",
        "compliance_privacy": "Compliance & privacy",
        "platform_nfr":       "Platform NFRs",
    })

    @classmethod
    def from_dict(cls, data: dict) -> "EnrichedModules":
        """Parse rfp_enriched_requirements.json output."""
        raw_modules = data.get("modules", {})
        modules = {
            mod: [EnrichedRequirement.from_dict(r) for r in reqs]
            for mod, reqs in raw_modules.items()
            if isinstance(reqs, list)
        }
        return cls(
            modules=modules,
            total=data.get("total", sum(len(v) for v in modules.values())),
            generated_at=data.get("generated", ""),
            phase=data.get("phase", "1.5_enriched"),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "EnrichedModules":
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def from_file(cls, path: str) -> "EnrichedModules":
        with open(path, encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

    # ── Accessors ─────────────────────────────────────────────────────────────

    @property
    def all_requirements(self) -> list[EnrichedRequirement]:
        return [r for reqs in self.modules.values() for r in reqs]

    @property
    def functional(self) -> list[EnrichedRequirement]:
        return [r for r in self.all_requirements if r.type == "FR"]

    @property
    def non_functional(self) -> list[EnrichedRequirement]:
        return [r for r in self.all_requirements if r.type == "NFR"]

    @property
    def compliance(self) -> list[EnrichedRequirement]:
        return [r for r in self.all_requirements if r.type == "CR"]

    @property
    def ambiguities(self) -> list[EnrichedRequirement]:
        return [r for r in self.all_requirements if r.is_ambiguous]

    @property
    def third_party_count(self) -> int:
        return sum(1 for r in self.all_requirements if r.impl_type == "third_party_integration")

    def module_summary(self, max_requirements_per_module: int = 8) -> str:
        """
        Build a concise human-readable module summary for injection into prompts.
        Limits per-module requirement detail to keep architecture prompts bounded.
        """
        lines = []
        for mod, reqs in self.modules.items():
            if not reqs:
                continue
            label = self.MODULE_LABELS.get(mod, mod)
            custom = sum(1 for r in reqs if r.impl_type == "custom_build")
            integ = sum(1 for r in reqs if r.impl_type == "third_party_integration")
            config = sum(1 for r in reqs if r.impl_type == "configuration")
            comp_ctrl = sum(1 for r in reqs if r.impl_type == "compliance_control")
            ambig = sum(1 for r in reqs if r.is_ambiguous)
            actors = sorted(set(a for r in reqs for a in r.actors))
            lines.append(f"\nMODULE: {label}")
            lines.append(
                f"  Counts: {len(reqs)} total ({custom} custom, {integ} integrations, {config} config, {comp_ctrl} compliance"
                f"{', ' + str(ambig) + ' ambiguous' if ambig else ''})"
            )
            lines.append(f"  Actors: {', '.join(actors) if actors else 'unspecified'}")

            prioritized = [
                r for r in reqs
                if r.type in ("FR", "NFR", "CR")
            ]
            prioritized.sort(
                key=lambda r: (
                    0 if r.type == "FR" else 1 if r.type == "NFR" else 2,
                    0 if r.priority == "MUST" else 1,
                    r.id,
                )
            )

            shown = prioritized[:max_requirements_per_module]
            for r in shown:
                actors_str = "/".join(r.actors) if r.actors else "?"
                lines.append(f"  - [{r.id}] {r.title} ({r.impl_type or 'unknown'}, actors:{actors_str})")

            remaining = len(prioritized) - len(shown)
            if remaining > 0:
                lines.append(f"  - ... {remaining} additional requirements summarized in counts above")

        return "\n".join(lines)


# ── ArchitectureInput ─────────────────────────────────────────────────────────

@dataclass
class ArchitectureInput:
    """
    Input to ArchitectureDesigner.

    Two construction paths:
      1. Flat requirements (Phase 1 direct / legacy):  ArchitectureInput(requirements="...")
      2. Enriched modules  (Phase 1.5 preferred):      ArchitectureInput.from_enriched_modules(em)
    """
    requirements:     str | list[str] = ""
    project_name:     str = "the system"
    deployment_target: DeploymentTarget = DeploymentTarget.CLOUD
    domain_context:   Optional[str] = None
    extra_constraints: list[str] = field(default_factory=list)

    # Populated when constructed from enriched modules — None for legacy path
    enriched_modules: Optional[EnrichedModules] = field(default=None, repr=False)

    @property
    def is_enriched(self) -> bool:
        return self.enriched_modules is not None

    # ── Factories ─────────────────────────────────────────────────────────────

    @classmethod
    def from_enriched_modules(
        cls,
        enriched: EnrichedModules,
        project_name: str = "the system",
        deployment_target: DeploymentTarget = DeploymentTarget.CLOUD,
        domain_context: Optional[str] = None,
        extra_constraints: Optional[list[str]] = None,
    ) -> "ArchitectureInput":
        """
        Preferred constructor — uses Phase 1.5 module-grouped requirements.
        The module summary replaces the flat requirements string in prompts.
        """
        return cls(
            requirements=enriched.module_summary(),
            project_name=project_name,
            deployment_target=deployment_target,
            domain_context=domain_context,
            extra_constraints=extra_constraints or [],
            enriched_modules=enriched,
        )

    @classmethod
    def from_rfp_output(cls, rfp_data: dict | str, **kwargs) -> "ArchitectureInput":
        """Legacy factory — accepts flat Phase 1 dict/JSON/markdown."""
        if isinstance(rfp_data, str):
            try:
                parsed = json.loads(rfp_data)
                if isinstance(parsed, dict):
                    rfp_data = parsed
                else:
                    return cls(requirements=rfp_data, **kwargs)
            except json.JSONDecodeError:
                return cls(requirements=rfp_data, **kwargs)

        reqs = rfp_data.get("requirements", rfp_data.get("extracted_requirements", ""))
        if isinstance(reqs, list):
            reqs = "\n".join(f"- {r}" if not r.startswith("-") else r for r in reqs)
        return cls(
            requirements=reqs,
            project_name=rfp_data.get("project_name", kwargs.get("project_name", "the system")),
            **{k: v for k, v in kwargs.items() if k != "project_name"},
        )

    def requirements_as_str(self) -> str:
        if isinstance(self.requirements, list):
            return "\n".join(f"- {r}" if not r.startswith("-") else r for r in self.requirements)
        return self.requirements


# ── Output sub-models ─────────────────────────────────────────────────────────

@dataclass
class Domain:
    name: str
    requirements: list[str]
    icon:  str = "box"
    color: str = "blue"
    count: int = 0

    def __post_init__(self):
        if self.count == 0:
            self.count = len(self.requirements)


@dataclass
class Actor:
    name: str
    type: ActorType
    description: str


@dataclass
class SystemContext:
    description:  str
    actors:       list[Actor]
    integrations: list[str] = field(default_factory=list)


@dataclass
class ArchitectureAlternative:
    name: str
    tradeoff: str


@dataclass
class ArchitectureLayer:
    layer: str
    components: list[str]


@dataclass
class ArchitecturePattern:
    recommended:    str
    rationale:      str
    key_principles: list[str] = field(default_factory=list)
    alternatives:   list[ArchitectureAlternative] = field(default_factory=list)
    layers:         list[ArchitectureLayer] = field(default_factory=list)
    domain_note:    Optional[str] = None


@dataclass
class Component:
    name:              str
    type:              ComponentType
    description:       str
    complexity:        Complexity
    complexity_reason: str
    estimation_signals: list[str] = field(default_factory=list)
    dependencies:       list[str] = field(default_factory=list)
    compliance_impacted: bool = False
    # ── Phase 1.5 enrichment fields ──────────────────────────────────────────
    module:             Optional[str] = None   # identity_access | cart_checkout | …
    impl_type:          Optional[str] = None   # custom_build | third_party_integration | …
    actors:             list[str] = field(default_factory=list)
    source_requirements: list[str] = field(default_factory=list)   # ["FR-001","NFR-002"]
    story_point_range:  Optional[StoryPointRange] = None


@dataclass
class SAPStandardModule:
    """
    Represents a standard SAP S/4HANA module that requires configuration (not custom development).
    Used to explicitly show standard platform modules in packaged solution architectures.
    """
    module_code: str          # e.g., "FI", "CO", "MM", "PP", "QM", "PM", "SD", "EWM", "TRM"
    module_name: str          # e.g., "Financial Accounting", "Controlling"
    description: str          # What this module does
    configuration_scope: str  # What needs to be configured (e.g., "Chart of accounts, GL setup")
    story_point_range: StoryPointRange = field(default_factory=lambda: StoryPointRange(20, 40, 60))
    customizations: list[str] = field(default_factory=list)  # List of custom enhancements needed
    source_requirements: list[str] = field(default_factory=list)  # Requirements that need this module
    is_in_scope: bool = True  # Whether this module is part of the implementation
    
    # Standard SAP module definitions
    STANDARD_MODULES = {
        "FI": {
            "name": "Financial Accounting",
            "description": "General ledger, accounts payable/receivable, asset accounting",
            "config_scope": "Chart of accounts, company codes, fiscal year, GL accounts, sub-ledgers",
            "sp_range": StoryPointRange(30, 45, 60)
        },
        "CO": {
            "name": "Controlling",
            "description": "Cost center accounting, profit center accounting, internal orders",
            "config_scope": "Cost centers, profit centers, cost elements, activity types, PPA logic",
            "sp_range": StoryPointRange(25, 40, 55)
        },
        "MM": {
            "name": "Materials Management",
            "description": "Procurement, inventory management, material master",
            "config_scope": "Material types, valuation classes, purchasing org, plant/storage locations",
            "sp_range": StoryPointRange(30, 50, 70)
        },
        "SD": {
            "name": "Sales & Distribution",
            "description": "Sales orders, pricing, shipping, billing",
            "config_scope": "Sales org, distribution channels, pricing procedures, shipping points",
            "sp_range": StoryPointRange(25, 40, 60)
        },
        "PP": {
            "name": "Production Planning",
            "description": "Production orders, work centers, BOMs, capacity planning",
            "config_scope": "Production versions, work centers, routing, MRP, batch management",
            "sp_range": StoryPointRange(40, 65, 90)
        },
        "QM": {
            "name": "Quality Management",
            "description": "Inspection lots, quality notifications, certificates of analysis",
            "config_scope": "Inspection plans, quality info records, sampling procedures, CoA templates",
            "sp_range": StoryPointRange(35, 55, 75)
        },
        "PM": {
            "name": "Plant Maintenance",
            "description": "Equipment master, maintenance orders, preventive maintenance",
            "config_scope": "Equipment master, maintenance plans, work orders, calibration schedules",
            "sp_range": StoryPointRange(20, 35, 50)
        },
        "EWM": {
            "name": "Extended Warehouse Management",
            "description": "Advanced warehouse processes, storage bins, wave picking",
            "config_scope": "Warehouse structure, storage types, putaway/picking strategies",
            "sp_range": StoryPointRange(30, 50, 70)
        },
        "IM": {
            "name": "Inventory Management",
            "description": "Basic warehouse management, goods movements",
            "config_scope": "Storage locations, movement types, lot tracking",
            "sp_range": StoryPointRange(15, 25, 40)
        },
        "TRM": {
            "name": "Treasury Management",
            "description": "Cash management, bank accounting, trade finance",
            "config_scope": "Bank accounts, payment methods, cash flow categories",
            "sp_range": StoryPointRange(15, 25, 40)
        }
    }
    
    @classmethod
    def from_code(cls, module_code: str, source_requirements: Optional[list[str]] = None) -> "SAPStandardModule":
        """Create a standard SAP module from its code (e.g., 'FI', 'MM')"""
        if module_code not in cls.STANDARD_MODULES:
            raise ValueError(f"Unknown SAP module code: {module_code}")
        
        module_def = cls.STANDARD_MODULES[module_code]
        return cls(
            module_code=module_code,
            module_name=module_def["name"],
            description=module_def["description"],
            configuration_scope=module_def["config_scope"],
            story_point_range=module_def["sp_range"],
            source_requirements=source_requirements or []
        )


@dataclass
class ArchitectureRisk:
    risk:       str
    level:      RiskLevel
    mitigation: str
    ref_id:     Optional[str] = None
    module:     Optional[str] = None   # which functional module this risk belongs to


@dataclass
class ArchitectureSummary:
    domain_count:          int
    actor_count:           int
    component_count:       int
    open_ambiguities:      int
    avg_complexity:        str
    compliance_components: int = 0
    total_story_points_mid: int = 0   # sum of all component mid story points


# ── Primary output model ──────────────────────────────────────────────────────

@dataclass
class ArchitectureOutput:
    """Full output from ArchitectureDesigner.analyze() or analyze_enriched()."""
    input:          ArchitectureInput
    domains:        list[Domain]
    system_context: SystemContext
    architecture:   ArchitecturePattern
    components:     list[Component]
    risks:          list[ArchitectureRisk]
    summary:        ArchitectureSummary

    # ── Convenience accessors ─────────────────────────────────────────────────

    @property
    def high_complexity_components(self) -> list[Component]:
        return [c for c in self.components if c.complexity == Complexity.HIGH]

    @property
    def compliance_components(self) -> list[Component]:
        return [c for c in self.components if c.compliance_impacted]

    @property
    def high_risks(self) -> list[ArchitectureRisk]:
        return [r for r in self.risks if r.level == RiskLevel.HIGH]

    def components_by_type(self, ctype: ComponentType) -> list[Component]:
        return [c for c in self.components if c.type == ctype]

    def components_by_module(self, module: str) -> list[Component]:
        return [c for c in self.components if c.module == module]

    @property
    def total_story_points(self) -> dict[str, int]:
        return {
            "low":  sum(c.story_point_range.low  if c.story_point_range else 0 for c in self.components),
            "mid":  sum(c.story_point_range.mid  if c.story_point_range else 0 for c in self.components),
            "high": sum(c.story_point_range.high if c.story_point_range else 0 for c in self.components),
        }

    # ── Serialization ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        def _actor(a: Actor) -> dict:
            return {"name": a.name, "type": a.type.value, "description": a.description}

        def _component(c: Component) -> dict:
            return {
                "name":               c.name,
                "type":               c.type.value,
                "description":        c.description,
                "complexity":         c.complexity.value,
                "complexity_reason":  c.complexity_reason,
                "estimation_signals": c.estimation_signals,
                "dependencies":       c.dependencies,
                "compliance_impacted": c.compliance_impacted,
                "module":             c.module,
                "impl_type":          c.impl_type,
                "actors":             c.actors,
                "source_requirements": c.source_requirements,
                "story_point_range":  c.story_point_range.to_dict() if c.story_point_range else None,
            }

        sp = self.total_story_points
        return {
            "project_name":     self.input.project_name,
            "deployment_target": self.input.deployment_target.value,
            "is_enriched":      self.input.is_enriched,
            "summary":          {
                "domain_count":           self.summary.domain_count,
                "actor_count":            self.summary.actor_count,
                "component_count":        self.summary.component_count,
                "open_ambiguities":       self.summary.open_ambiguities,
                "avg_complexity":         self.summary.avg_complexity,
                "compliance_components":  self.summary.compliance_components,
                "total_story_points_mid": sp["mid"],
                "story_points":           sp,
            },
            "domains": [
                {"name": d.name, "count": d.count, "requirements": d.requirements}
                for d in self.domains
            ],
            "system_context": {
                "description":  self.system_context.description,
                "actors":       [_actor(a) for a in self.system_context.actors],
                "integrations": self.system_context.integrations,
            },
            "architecture": {
                "recommended":    self.architecture.recommended,
                "rationale":      self.architecture.rationale,
                "key_principles": self.architecture.key_principles,
                "domain_note":    self.architecture.domain_note,
                "alternatives":   [{"name": a.name, "tradeoff": a.tradeoff} for a in self.architecture.alternatives],
                "layers":         [{"layer": l.layer, "components": l.components} for l in self.architecture.layers],
            },
            "components": [_component(c) for c in self.components],
            "risks": [
                {"risk": r.risk, "level": r.level.value, "mitigation": r.mitigation,
                 "ref_id": r.ref_id, "module": r.module}
                for r in self.risks
            ],
        }

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent)
