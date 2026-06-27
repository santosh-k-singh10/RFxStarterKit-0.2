"""
RFP Analyzer — Scoping Designer v1.2
==========================================
Phase 2 module: Requirements → Scoping output.

Two analysis paths:
  Enriched (preferred):  ScopingDesigner().analyze_enriched(EnrichedModules)
  Flat / legacy:         ScopingDesigner().analyze(ScopingInput)

Quick start:
    from scoping_designer import ScopingDesigner, EnrichedModules

    em     = EnrichedModules.from_file("rfp_enriched_requirements.json")
    result = ScopingDesigner(api_key="sk-ant-...").analyze_enriched(
                 em, project_name="My Portal", domain_context="ecommerce"
             )
    ScopingDesigner().export_markdown(result, "scoping.md")
"""

from .designer import ScopingDesigner
from .preferences import (
    UserPreferences, PreferencesCollector,
    BuildApproach, CloudProvider, PackagedPlatform,
    ComplianceRegime, ClientChannel, IntegrationStyle, DeliveryTimeline,
)
from .models import (
    ArchitectureInput, ArchitectureOutput,
    EnrichedModules, EnrichedRequirement,
    Domain, Actor, SystemContext,
    ArchitecturePattern, Component, ArchitectureRisk,
    StoryPointRange,
    DeploymentTarget, Complexity, ActorType,
    ComponentType, RiskLevel, ImplType,
    ArchitectureSummary,
)
from .exporters import MarkdownExporter, JsonExporter, HtmlExporter

__version__ = "1.2.0"
__all__ = [
    "ScopingDesigner",
    "UserPreferences", "PreferencesCollector",
    "BuildApproach", "CloudProvider", "PackagedPlatform",
    "ComplianceRegime", "ClientChannel", "IntegrationStyle", "DeliveryTimeline",
    "ArchitectureInput", "ArchitectureOutput",
    "EnrichedModules", "EnrichedRequirement",
    "Domain", "Actor", "SystemContext",
    "ArchitecturePattern", "Component", "ArchitectureRisk",
    "StoryPointRange",
    "DeploymentTarget", "Complexity", "ActorType",
    "ComponentType", "RiskLevel", "ImplType",
    "ArchitectureSummary",
    "MarkdownExporter", "JsonExporter", "HtmlExporter",
]

# Made with Bob
