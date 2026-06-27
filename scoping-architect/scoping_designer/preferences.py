"""
Preferences module — User preferences collection and validation.

Bridges the web form → ArchitectureInput.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
import logging

from .models import ArchitectureInput, DeploymentTarget

logger = logging.getLogger(__name__)


# ── Enums ─────────────────────────────────────────────────────────────────────

class BuildApproach(str, Enum):
    GREENFIELD = "greenfield"
    PACKAGED = "packaged"
    EXTEND = "extend"
    HYBRID = "hybrid"


class CloudProvider(str, Enum):
    AWS = "aws"
    AZURE = "azure"
    GCP = "gcp"
    IBM_CLOUD = "ibm_cloud"
    NO_PREF = "no_pref"


class PackagedPlatform(str, Enum):
    SALESFORCE = "salesforce"
    SAP = "sap"
    SERVICENOW = "servicenow"
    MS365 = "ms365"
    ORACLE = "oracle"
    WORKDAY = "workday"
    OTHER = "other"


class ComplianceRegime(str, Enum):
    HIPAA = "hipaa"
    PCI_DSS = "pci"
    FEDRAMP = "fedramp"
    GDPR = "gdpr"
    SOX = "sox"
    ISO27001 = "iso27001"
    NONE = "none"


class ClientChannel(str, Enum):
    WEB = "web"
    MOBILE_NATIVE = "mobile_native"
    PWA = "pwa"
    API_ONLY = "api_only"
    DESKTOP = "desktop"


class IntegrationStyle(str, Enum):
    REST = "rest"
    EVENT = "event"
    ESB = "esb"
    FHIR = "fhir"
    NO_PREF = "no_pref"


class DeliveryTimeline(str, Enum):
    FIXED = "fixed"
    TARGET = "target"
    PHASED = "phased"
    TBD = "tbd"


# ── UserPreferences ───────────────────────────────────────────────────────────

@dataclass
class UserPreferences:
    """
    Structured user preferences from the intake form.
    Collected via PreferencesCollector.
    """
    build_approach: BuildApproach = BuildApproach.GREENFIELD
    deployment_target_raw: str = "cloud"
    cloud_provider: Optional[CloudProvider] = None
    packaged_platforms: list[PackagedPlatform] = field(default_factory=list)
    compliance_regimes: list[ComplianceRegime] = field(default_factory=list)
    client_channels: list[ClientChannel] = field(default_factory=list)
    integration_style: Optional[IntegrationStyle] = None
    delivery_timeline: Optional[DeliveryTimeline] = None
    existing_tech_estate: str = ""
    team_skill_notes: str = ""
    inferred_domain_context: Optional[str] = None
    extra_constraints: list[str] = field(default_factory=list)

    @property
    def deployment_target(self) -> DeploymentTarget:
        mapping = {
            "cloud": DeploymentTarget.CLOUD,
            "on_prem": DeploymentTarget.ON_PREM,
            "hybrid": DeploymentTarget.HYBRID,
            "saas": DeploymentTarget.SAAS,
        }
        return mapping.get(self.deployment_target_raw.lower(), DeploymentTarget.CLOUD)

    def to_architecture_input(
        self, requirements: str, project_name: str = "the system"
    ) -> ArchitectureInput:
        """Convert preferences to ArchitectureInput for Phase 2."""
        constraints = list(self.extra_constraints)
        
        if self.cloud_provider and self.cloud_provider != CloudProvider.NO_PREF:
            constraints.append(f"Cloud provider: {self.cloud_provider.value}")
        
        if self.compliance_regimes:
            regimes = ", ".join(c.value.upper() for c in self.compliance_regimes if c != ComplianceRegime.NONE)
            if regimes:
                constraints.append(f"Compliance: {regimes}")
        
        if self.client_channels:
            channels = ", ".join(c.value for c in self.client_channels)
            constraints.append(f"Client channels: {channels}")
        
        if self.integration_style and self.integration_style != IntegrationStyle.NO_PREF:
            constraints.append(f"Integration style: {self.integration_style.value}")
        
        if self.delivery_timeline and self.delivery_timeline != DeliveryTimeline.TBD:
            constraints.append(f"Timeline: {self.delivery_timeline.value}")
        
        if self.existing_tech_estate:
            constraints.append(f"Existing tech: {self.existing_tech_estate}")
        
        if self.packaged_platforms:
            platforms = ", ".join(p.value for p in self.packaged_platforms)
            constraints.append(f"Packaged platforms: {platforms}")

        return ArchitectureInput(
            requirements=requirements,
            project_name=project_name,
            deployment_target=self.deployment_target,
            domain_context=self.inferred_domain_context,
            extra_constraints=constraints,
        )


    def to_dict(self) -> dict:
        return {
            "build_approach": self.build_approach.value,
            "deployment_target": self.deployment_target_raw,
            "cloud_provider": self.cloud_provider.value if self.cloud_provider else None,
            "packaged_platforms": [p.value for p in self.packaged_platforms],
            "compliance_regimes": [c.value for c in self.compliance_regimes],
            "client_channels": [ch.value for ch in self.client_channels],
            "integration_style": self.integration_style.value if self.integration_style else None,
            "delivery_timeline": self.delivery_timeline.value if self.delivery_timeline else None,
            "existing_tech_estate": self.existing_tech_estate,
            "inferred_domain_context": self.inferred_domain_context,
            "extra_constraints": self.extra_constraints,
        }


# ── PreferencesCollector ──────────────────────────────────────────────────────

class PreferencesCollector:
    """
    Factory for building UserPreferences from various input formats.
    Handles validation and domain inference.
    """

    @classmethod
    def from_dict(cls, data: dict) -> UserPreferences:
        """Parse preferences from API request dict."""
        logger.info("PreferencesCollector.from_dict() called")
        logger.info(f"  - Input keys: {list(data.keys())}")
        
        # Parse enums safely
        approach = data.get("approach", "greenfield")
        if isinstance(approach, str):
            approach = BuildApproach(approach)
        logger.info(f"  - Build approach: {approach}")
        
        cloud = data.get("cloud")
        if cloud and isinstance(cloud, str):
            cloud = CloudProvider(cloud)
        
        platforms = []
        for p in data.get("platform", []):
            if isinstance(p, str):
                platforms.append(PackagedPlatform(p))
            else:
                platforms.append(p)
        
        compliance = []
        for c in data.get("compliance", []):
            if isinstance(c, str):
                compliance.append(ComplianceRegime(c))
            else:
                compliance.append(c)
        
        channels = []
        for ch in data.get("channels", []):
            if isinstance(ch, str):
                channels.append(ClientChannel(ch))
            else:
                channels.append(ch)
        
        integration = data.get("integration")
        if integration and isinstance(integration, str):
            integration = IntegrationStyle(integration)
        
        timeline = data.get("timeline")
        if timeline and isinstance(timeline, str):
            timeline = DeliveryTimeline(timeline)
        
        # Infer domain context
        logger.info("Inferring domain context...")
        domain_context = cls._infer_domain(data, compliance)
        logger.info(f"  - Inferred domain: {domain_context or 'None'}")
        
        # Build extra constraints
        extra_constraints = []
        skill_notes = data.get("skill_notes", "")
        if skill_notes:
            extra_constraints.append(f"Team skills: {skill_notes}")
        
        logger.info("UserPreferences created")
        logger.info(f"  - Deployment: {data.get('deployment', 'cloud')}")
        logger.info(f"  - Compliance regimes: {len(compliance)}")
        logger.info(f"  - Client channels: {len(channels)}")
        logger.info(f"  - Extra constraints: {len(extra_constraints)}")
        
        return UserPreferences(
            build_approach=approach,
            deployment_target_raw=data.get("deployment", "cloud"),
            cloud_provider=cloud,
            packaged_platforms=platforms,
            compliance_regimes=compliance,
            client_channels=channels,
            integration_style=integration,
            delivery_timeline=timeline,
            existing_tech_estate=data.get("tech_estate", ""),
            team_skill_notes=skill_notes,
            inferred_domain_context=domain_context,
            extra_constraints=extra_constraints,
        )

    @staticmethod
    def _infer_domain(data: dict, compliance: list[ComplianceRegime]) -> Optional[str]:
        """Infer domain context from preferences."""
        if ComplianceRegime.HIPAA in compliance:
            return "healthcare"
        if ComplianceRegime.PCI_DSS in compliance:
            # Could be ecommerce or fintech
            tech_estate = data.get("tech_estate", "").lower()
            if any(word in tech_estate for word in ["stripe", "payment", "shop", "cart", "ecommerce"]):
                return "ecommerce"
            return "fintech"
        if ComplianceRegime.FEDRAMP in compliance:
            return "government"
        
        # Check tech estate for clues
        tech_estate = data.get("tech_estate", "").lower()
        if any(word in tech_estate for word in ["ehr", "emr", "fhir", "hl7", "patient"]):
            return "healthcare"
        if any(word in tech_estate for word in ["shop", "cart", "ecommerce", "retail"]):
            return "ecommerce"
        if any(word in tech_estate for word in ["logistics", "shipping", "warehouse", "supply"]):
            return "logistics"
        
        deployment = data.get("deployment", "").lower()
        if deployment == "saas":
            return "saas_platform"
        
        return None

    def to_dict(self) -> dict:
        """This is called on the UserPreferences instance, not the collector."""
        raise NotImplementedError("Call to_dict() on UserPreferences instance")