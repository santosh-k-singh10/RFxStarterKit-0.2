"""
tests/test_models.py — Tests for architecture_designer.models

Tests data model creation, serialization, and validation without requiring API calls.
"""
import pytest
from architecture_designer.models import (
    DeploymentTarget, Complexity, ComponentType, RiskLevel, ImplType,
    StoryPointRange, EnrichedRequirement, EnrichedModules,
    Component, ArchitectureRisk, Domain, ArchitectureSummary
)


class TestEnumerations:
    """Test enum types and their labels."""
    
    def test_deployment_target_values(self):
        """Test DeploymentTarget enum has expected values."""
        assert DeploymentTarget.CLOUD.value == "cloud"
        assert DeploymentTarget.ON_PREM.value == "on_prem"
        assert DeploymentTarget.HYBRID.value == "hybrid"
        assert DeploymentTarget.SAAS.value == "saas"
    
    def test_deployment_target_labels(self):
        """Test DeploymentTarget provides human-readable labels."""
        assert "AWS" in DeploymentTarget.CLOUD.label()
        assert "On-premise" in DeploymentTarget.ON_PREM.label()
    
    def test_complexity_values(self):
        """Test Complexity enum values."""
        assert Complexity.LOW.value == "Low"
        assert Complexity.MEDIUM.value == "Medium"
        assert Complexity.HIGH.value == "High"
    
    def test_impl_type_values(self):
        """Test ImplType enum for Phase 1.5 support."""
        assert ImplType.CUSTOM_BUILD.value == "custom_build"
        assert ImplType.THIRD_PARTY_INTEGRATION.value == "third_party_integration"
        assert ImplType.CONFIGURATION.value == "configuration"


class TestStoryPointRange:
    """Test story point range model."""
    
    def test_create_story_point_range(self):
        """Test creating a story point range."""
        spr = StoryPointRange(low=3, mid=5, high=8)
        assert spr.low == 3
        assert spr.mid == 5
        assert spr.high == 8
    
    def test_story_point_range_to_dict(self):
        """Test serialization to dict."""
        spr = StoryPointRange(low=3, mid=5, high=8)
        d = spr.to_dict()
        assert d == {"low": 3, "mid": 5, "high": 8}
    
    def test_story_point_range_from_dict(self):
        """Test deserialization from dict."""
        d = {"low": 3, "mid": 5, "high": 8}
        spr = StoryPointRange.from_dict(d)
        assert spr.low == 3
        assert spr.mid == 5
        assert spr.high == 8
    
    def test_story_point_range_defaults(self):
        """Test default values are zero."""
        spr = StoryPointRange()
        assert spr.low == 0
        assert spr.mid == 0
        assert spr.high == 0


class TestEnrichedRequirement:
    """Test enriched requirement model from Phase 1.5."""
    
    def test_create_enriched_requirement(self):
        """Test creating an enriched requirement."""
        req = EnrichedRequirement(
            id="FR-001",
            type="FR",
            title="User Authentication",
            description="Users must be able to log in",
            priority="MUST",
            confidence=95,
            module="identity_access",
            impl_type="custom_build",
            actors=["customer", "admin"]
        )
        assert req.id == "FR-001"
        assert req.type == "FR"
        assert req.module == "identity_access"
        assert req.impl_type == "custom_build"
        assert "customer" in req.actors
    
    def test_enriched_requirement_defaults(self):
        """Test default values for optional fields."""
        req = EnrichedRequirement(
            id="FR-001",
            type="FR",
            title="Test"
        )
        assert req.priority == "MUST"
        assert req.confidence is None
        assert req.description == ""
        assert req.is_ambiguous is False
        assert req.actors == []
    
    def test_enriched_requirement_from_dict(self):
        """Test deserialization from dict."""
        d = {
            "id": "FR-001",
            "type": "FR",
            "title": "Test",
            "module": "test_module",
            "impl_type": "custom_build",
            "actors": ["user"]
        }
        req = EnrichedRequirement.from_dict(d)
        assert req.id == "FR-001"
        assert req.module == "test_module"
        assert req.actors == ["user"]


class TestEnrichedModules:
    """Test enriched modules container."""
    
    def test_create_enriched_modules(self, sample_enriched_modules):
        """Test creating EnrichedModules from dict."""
        em = EnrichedModules.from_dict(sample_enriched_modules)
        assert em.total == 3
        assert "identity_access" in em.modules
        assert "platform_nfrs" in em.modules
        assert len(em.modules["identity_access"]) == 2
    
    def test_enriched_modules_module_summary(self, sample_enriched_modules):
        """Test module_summary() generates correct format."""
        em = EnrichedModules.from_dict(sample_enriched_modules)
        summary = em.module_summary()
        
        assert "identity_access" in summary
        assert "platform_nfrs" in summary
        assert "2 requirements" in summary
        assert "FR-001" in summary
        assert "FR-002" in summary


class TestComponent:
    """Test Component model with Phase 1.5 enhancements."""
    
    def test_create_component_basic(self):
        """Test creating a basic component."""
        comp = Component(
            name="Auth Service",
            type=ComponentType.BACKEND,
            description="Authentication service",
            complexity=Complexity.MEDIUM,
            complexity_reason="OAuth2 integration"
        )
        assert comp.name == "Auth Service"
        assert comp.type == ComponentType.BACKEND
        assert comp.complexity == Complexity.MEDIUM
    
    def test_component_with_enrichment_fields(self):
        """Test component with Phase 1.5 enrichment fields."""
        spr = StoryPointRange(low=5, mid=8, high=13)
        comp = Component(
            name="Auth Service",
            type=ComponentType.BACKEND,
            description="Authentication service",
            complexity=Complexity.MEDIUM,
            complexity_reason="OAuth2 integration",
            module="identity_access",
            impl_type="custom_build",
            actors=["customer", "admin"],
            source_requirements=["FR-001", "FR-002"],
            story_point_range=spr
        )
        assert comp.module == "identity_access"
        assert comp.impl_type == "custom_build"
        assert comp.actors == ["customer", "admin"]
        assert comp.source_requirements == ["FR-001", "FR-002"]
        assert comp.story_point_range is not None
        assert comp.story_point_range.mid == 8


class TestArchitectureRisk:
    """Test architecture risk model."""
    
    def test_create_risk(self):
        """Test creating an architecture risk."""
        risk = ArchitectureRisk(
            risk="Authentication complexity underestimated",
            level=RiskLevel.HIGH,
            mitigation="Use proven OAuth2 library",
            ref_id="NFR-001",
            module="identity_access"
        )
        assert risk.risk == "Authentication complexity underestimated"
        assert risk.level == RiskLevel.HIGH
        assert risk.module == "identity_access"
    
    def test_risk_defaults(self):
        """Test default values for optional fields."""
        risk = ArchitectureRisk(
            risk="Test risk",
            level=RiskLevel.LOW,
            mitigation="Test mitigation"
        )
        assert risk.ref_id is None
        assert risk.module is None


class TestDomain:
    """Test domain model."""
    
    def test_create_domain(self):
        """Test creating a domain."""
        domain = Domain(
            name="Identity & Access",
            requirements=["User auth", "RBAC"],
            count=2,
            color="blue"
        )
        assert domain.name == "Identity & Access"
        assert domain.count == 2
        assert len(domain.requirements) == 2


class TestArchitectureSummary:
    """Test architecture summary model."""
    
    def test_create_summary(self):
        """Test creating an architecture summary."""
        summary = ArchitectureSummary(
            domain_count=6,
            actor_count=4,
            component_count=10,
            open_ambiguities=2,
            avg_complexity="Medium",
            compliance_components=3,
            total_story_points_mid=87
        )
        assert summary.domain_count == 6
        assert summary.actor_count == 4
        assert summary.component_count == 10
        assert summary.total_story_points_mid == 87
        assert summary.compliance_components == 3
        assert summary.avg_complexity == "Medium"


# Run tests with: pytest tests/test_models.py -v

# Made with Bob
