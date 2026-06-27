"""
api/schemas.py — Pydantic request/response schemas for the FastAPI layer.

Kept separate from scoping_designer/models.py (which uses plain dataclasses)
so the core module stays dependency-free. This layer handles HTTP validation only.
"""

from __future__ import annotations

from typing import Optional, Any
from pydantic import BaseModel, Field

from scoping_designer.preferences import (
    BuildApproach,
    CloudProvider,
    PackagedPlatform,
    ComplianceRegime,
    ClientChannel,
    IntegrationStyle,
    DeliveryTimeline,
)


# ── Request schemas ───────────────────────────────────────────────────────────

class PreferencesRequest(BaseModel):
    """
    POST /api/preferences
    Mirrors the 3-step web form exactly — all fields optional with sensible defaults
    so partial saves mid-wizard also work.
    """
    approach:    BuildApproach            = Field(BuildApproach.GREENFIELD, description="Build approach")
    deployment:  str                      = Field("cloud",                  description="Deployment target: cloud|on_prem|hybrid|saas")
    cloud:       Optional[CloudProvider]  = Field(None,                     description="Cloud provider preference")
    platform:    list[PackagedPlatform]   = Field(default_factory=list,     description="Packaged platforms if applicable")
    compliance:  list[ComplianceRegime]   = Field(default_factory=list,     description="Compliance regimes")
    channels:    list[ClientChannel]      = Field(default_factory=list,     description="Client channel requirements")
    integration: Optional[IntegrationStyle] = Field(None,                   description="Integration style preference")
    timeline:    Optional[DeliveryTimeline] = Field(None,                   description="Delivery timeline")
    tech_estate: str                      = Field("",                       description="Existing technology estate (free text)")
    skill_notes: str                      = Field("",                       description="Team skill notes / stack preferences")

    model_config = {"use_enum_values": True}


class AnalyzeRequest(BaseModel):
    """
    POST /api/analyze
    Full pipeline: preferences + requirements → scoping output.
    """
    preferences:  PreferencesRequest = Field(..., description="User preferences from the intake form")
    requirements: str                = Field(..., min_length=10, description="Extracted requirements text (Phase 1 output). Must be at least 10 characters.")
    project_name: str                = Field(default="the system", description="Project / product name")


# ── Enriched analyze request (Phase 1.5 path) ─────────────────────────────────

class EnrichedAnalyzeRequest(BaseModel):
    """
    POST /api/analyze/enriched — module-grouped Phase 1.5 input.

    Body shape:
    {
      "project_name": "ABC Platform",
      "deployment": "cloud",
      "cloud_provider": "AWS",
      "domain_context": "ecommerce",
      "compliance": ["PCI DSS", "GDPR"],
      "timeline": "Fixed deadline",
      "extra_constraints": ["React + Node.js preferred"],
      "modules": {
        "identity_access": [ { ...EnrichedRequirement... } ],
        "cart_checkout":   [ { ...EnrichedRequirement... } ],
        ...
      }
    }
    """
    project_name:       str            = Field("the system")
    deployment:         str            = Field("cloud")
    cloud_provider:     Optional[str]  = Field(None)
    domain_context:     Optional[str]  = Field(None)
    compliance:         list[str]      = Field(default_factory=list)
    timeline:           Optional[str]  = Field(None)
    extra_constraints:  list[str]      = Field(default_factory=list)
    build_approach:     Optional[str]  = Field(None, description="Build approach: greenfield|packaged|extend|hybrid")
    packaged_platforms: list[str]      = Field(default_factory=list, description="Packaged platforms if applicable (e.g., ['sap', 'salesforce'])")
    modules:            dict[str, list[dict[str, Any]]] = Field(...)


# ── Response schemas ──────────────────────────────────────────────────────────

class StoryPointRangeSchema(BaseModel):
    low:  int
    mid:  int
    high: int


class ComponentSchema(BaseModel):
    name:                str
    type:                str
    description:         str
    complexity:          str
    complexity_reason:   str
    compliance_impacted: bool
    module:              Optional[str]
    impl_type:           Optional[str]
    actors:              list[str]
    source_requirements: list[str]
    estimation_signals:  list[str]
    dependencies:        list[str]
    story_point_range:   Optional[StoryPointRangeSchema]


class ArchitectureOutputResponse(BaseModel):
    project_name:      str
    deployment_target: str
    is_enriched:       bool
    summary:           dict[str, Any]
    domains:           list[dict[str, Any]]
    system_context:    dict[str, Any]
    architecture:      dict[str, Any]
    components:        list[dict[str, Any]]
    risks:             list[dict[str, Any]]
    scoping_metadata:  Optional[dict[str, Any]] = None


class PreferencesResponse(BaseModel):
    """Response from POST /api/preferences — structured + validated preferences."""
    build_approach:          str
    deployment_target:       str
    cloud_provider:          Optional[str]
    packaged_platforms:      list[str]
    compliance_regimes:      list[str]
    client_channels:         list[str]
    integration_style:       Optional[str]
    delivery_timeline:       Optional[str]
    existing_tech_estate:    str
    inferred_domain_context: Optional[str]
    extra_constraints:       list[str]


class HealthResponse(BaseModel):
    status:  str
    version: str
    module:  str


class ErrorResponse(BaseModel):
    error:  str
    detail: Optional[str] = None


# ── Scoping Metadata schemas (GSE Pre-fill) ──────────────────────────────────

class ScopingMetadataField(BaseModel):
    """Individual field with extraction metadata."""
    value: Any = None
    confidence: str = Field(..., description="auto | estimated | needs-input")
    sources: list[str] = Field(default_factory=list)
    hint: str = ""


class GeographyMetadata(BaseModel):
    """Geography and organizational scope metadata."""
    countries: Optional[ScopingMetadataField] = None
    no_of_countries: Optional[ScopingMetadataField] = None
    no_of_company_codes: Optional[ScopingMetadataField] = None
    no_of_plants: Optional[ScopingMetadataField] = None
    no_of_divisions: Optional[ScopingMetadataField] = None
    rollout_in_scope: Optional[ScopingMetadataField] = None
    rollout_type: Optional[ScopingMetadataField] = None
    no_of_rollouts: Optional[ScopingMetadataField] = None
    project_language: Optional[ScopingMetadataField] = None
    project_start_date_hint: Optional[str] = None
    timeline_given_by_client: Optional[ScopingMetadataField] = None


class UsersMetadata(BaseModel):
    """User count metadata."""
    core_users: Optional[ScopingMetadataField] = None
    self_service_users: Optional[ScopingMetadataField] = None
    end_users: Optional[ScopingMetadataField] = None
    target_trainees: Optional[ScopingMetadataField] = None


class ApplicationsMetadata(BaseModel):
    """Application and module scope metadata."""
    standard_applications: Optional[ScopingMetadataField] = None
    additional_applications: Optional[ScopingMetadataField] = None
    module_scope: Optional[ScopingMetadataField] = None
    l1_processes: Optional[ScopingMetadataField] = None
    _module_sources: Optional[dict[str, list[str]]] = None
    _l1_sources: Optional[dict[str, list[str]]] = None


class WRICEFMetadata(BaseModel):
    """WRICEF object counts metadata."""
    wricef_in_scope: Optional[ScopingMetadataField] = None
    integration_layer: Optional[ScopingMetadataField] = None
    reports: Optional[ScopingMetadataField] = None
    forms: Optional[ScopingMetadataField] = None
    enhancements: Optional[ScopingMetadataField] = None
    abap_interfaces: Optional[ScopingMetadataField] = None
    btp_interfaces: Optional[ScopingMetadataField] = None
    conversions: Optional[ScopingMetadataField] = None
    _detail: Optional[dict[str, list[str]]] = None


class DataMigrationMetadata(BaseModel):
    """Data migration scope metadata."""
    in_scope: Optional[ScopingMetadataField] = None
    tool: Optional[ScopingMetadataField] = None
    no_of_data_objects: Optional[ScopingMetadataField] = None
    no_of_load_cycles: Optional[ScopingMetadataField] = None
    no_of_source_systems: Optional[ScopingMetadataField] = None
    _source_systems_found: Optional[list[str]] = None


class TestingMetadata(BaseModel):
    """Testing scope metadata."""
    automation_in_scope: Optional[ScopingMetadataField] = None
    sit_in_scope: Optional[ScopingMetadataField] = None
    sit_cycles: Optional[ScopingMetadataField] = None
    automation_scenarios_sap_gui: Optional[ScopingMetadataField] = None
    automation_scenarios_fiori: Optional[ScopingMetadataField] = None
    sit_scenarios_proxy: Optional[ScopingMetadataField] = None


class SecurityMetadata(BaseModel):
    """Security and authorization metadata."""
    in_scope: Optional[ScopingMetadataField] = None
    no_of_end_users: Optional[ScopingMetadataField] = None
    no_of_l3_processes: Optional[ScopingMetadataField] = None


class ChangeManagementMetadata(BaseModel):
    """OCM and training metadata."""
    ocm_in_scope: Optional[ScopingMetadataField] = None
    training_in_scope: Optional[ScopingMetadataField] = None
    training_approach: Optional[ScopingMetadataField] = None
    ibm_involvement: Optional[ScopingMetadataField] = None
    target_trainees: Optional[ScopingMetadataField] = None
    no_of_training_materials: Optional[ScopingMetadataField] = None


class ImplementationMetadata(BaseModel):
    """Implementation timeline metadata."""
    bph_model: Optional[ScopingMetadataField] = None
    methodology: Optional[ScopingMetadataField] = None
    go_live_hints: Optional[list[str]] = None


class FillSummary(BaseModel):
    """Fill rate summary."""
    total_fields: int = 0
    auto_filled: int = 0
    estimated: int = 0
    needs_input: int = 0
    fill_rate_pct: float = 0.0


class ScopingMetadata(BaseModel):
    """Complete scoping metadata extracted from enriched RFP."""
    extraction_version: str = "1.0.0"
    total_requirements: int = 0
    modules_analyzed: list[str] = Field(default_factory=list)
    fill_summary: Optional[FillSummary] = None
    geography: Optional[GeographyMetadata] = None
    users: Optional[UsersMetadata] = None
    applications: Optional[ApplicationsMetadata] = None
    wricef: Optional[WRICEFMetadata] = None
    data_migration: Optional[DataMigrationMetadata] = None
    testing: Optional[TestingMetadata] = None
    security: Optional[SecurityMetadata] = None
    change_management: Optional[ChangeManagementMetadata] = None
    implementation: Optional[ImplementationMetadata] = None
