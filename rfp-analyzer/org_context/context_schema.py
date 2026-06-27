"""
org_context/context_schema.py
------------------------------
Pydantic models for organizational context configuration.

These schemas define the structure of organizational knowledge,
standards, and preferences used throughout the RFP analysis process.
"""

from __future__ import annotations

from typing import Optional
from pathlib import Path
from pydantic import BaseModel, Field, field_validator


class TechStack(BaseModel):
    """Organization's technology stack preferences."""
    
    preferred_languages: list[str] = Field(
        default_factory=list,
        description="Preferred programming languages"
    )
    cloud_providers: list[str] = Field(
        default_factory=list,
        description="Approved cloud providers"
    )
    databases: list[str] = Field(
        default_factory=list,
        description="Preferred database systems"
    )
    frameworks: list[str] = Field(
        default_factory=list,
        description="Preferred frameworks and libraries"
    )
    architecture_patterns: list[str] = Field(
        default_factory=list,
        description="Preferred architecture patterns (microservices, monolith, etc.)"
    )


class ComplianceRequirements(BaseModel):
    """Compliance frameworks and certifications."""
    
    frameworks: list[str] = Field(
        default_factory=list,
        description="Required compliance frameworks (GDPR, HIPAA, SOC2, etc.)"
    )
    certifications: list[str] = Field(
        default_factory=list,
        description="Required certifications"
    )
    standards: list[str] = Field(
        default_factory=list,
        description="Industry standards to follow"
    )


class NamingConventions(BaseModel):
    """Requirement ID naming conventions."""
    
    requirement_prefix: str = Field(
        default="REQ",
        description="General requirement prefix"
    )
    functional_prefix: str = Field(
        default="FR",
        description="Functional requirement prefix"
    )
    non_functional_prefix: str = Field(
        default="NFR",
        description="Non-functional requirement prefix"
    )
    compliance_prefix: str = Field(
        default="CR",
        description="Compliance requirement prefix"
    )
    ambiguity_prefix: str = Field(
        default="AMB",
        description="Ambiguity item prefix"
    )
    risk_prefix: str = Field(
        default="RISK",
        description="Risk item prefix"
    )
    separator: str = Field(
        default="-",
        description="Separator between prefix and number"
    )
    padding: int = Field(
        default=3,
        ge=1,
        le=5,
        description="Number of digits for padding (e.g., 3 = 001, 002)"
    )


class PriorityMapping(BaseModel):
    """Keywords for automatic priority detection."""
    
    must_keywords: list[str] = Field(
        default_factory=lambda: ["shall", "must", "required", "mandatory"],
        description="Keywords indicating MUST priority"
    )
    should_keywords: list[str] = Field(
        default_factory=lambda: ["should", "recommended", "preferred"],
        description="Keywords indicating SHOULD priority"
    )
    could_keywords: list[str] = Field(
        default_factory=lambda: ["may", "could", "optional", "nice to have"],
        description="Keywords indicating COULD priority"
    )
    wont_keywords: list[str] = Field(
        default_factory=lambda: ["will not", "won't", "excluded"],
        description="Keywords indicating WON'T priority"
    )


class RiskThresholds(BaseModel):
    """Risk assessment thresholds and indicators."""
    
    high_complexity_indicators: list[str] = Field(
        default_factory=lambda: [
            "AI/ML", "machine learning", "blockchain", "real-time",
            "distributed system", "high availability", "scalability"
        ],
        description="Keywords indicating high technical complexity"
    )
    timeline_red_flags: list[str] = Field(
        default_factory=lambda: [
            "< 3 months", "immediate", "urgent", "ASAP",
            "tight deadline", "aggressive timeline"
        ],
        description="Keywords indicating timeline risks"
    )
    resource_constraints: list[str] = Field(
        default_factory=lambda: [
            "limited budget", "small team", "part-time",
            "shared resources", "constrained"
        ],
        description="Keywords indicating resource constraints"
    )
    high_risk_score_threshold: float = Field(
        default=0.7,
        ge=0.0,
        le=1.0,
        description="Threshold for flagging high-risk items"
    )


class OutputPreferences(BaseModel):
    """Output format and content preferences."""
    
    include_cost_estimates: bool = Field(
        default=True,
        description="Include cost estimation in outputs"
    )
    include_timeline_estimates: bool = Field(
        default=True,
        description="Include timeline estimation in outputs"
    )
    include_team_sizing: bool = Field(
        default=True,
        description="Include team composition recommendations"
    )
    custom_sections: list[str] = Field(
        default_factory=lambda: [
            "Technical Approach",
            "Team Composition",
            "Risk Mitigation Strategy",
            "Implementation Timeline"
        ],
        description="Custom sections to include in reports"
    )
    excel_template: Optional[str] = Field(
        default=None,
        description="Path to custom Excel template"
    )
    markdown_template: Optional[str] = Field(
        default=None,
        description="Path to custom Markdown template"
    )
    branding: dict[str, str] = Field(
        default_factory=dict,
        description="Branding elements (logo_path, primary_color, secondary_color)"
    )


class DomainKnowledge(BaseModel):
    """Domain-specific knowledge and terminology."""
    
    industry_terms: dict[str, str] = Field(
        default_factory=dict,
        description="Industry-specific terms and definitions"
    )
    acronyms: dict[str, str] = Field(
        default_factory=dict,
        description="Acronym expansions"
    )
    vendor_preferences: list[str] = Field(
        default_factory=list,
        description="Preferred vendors and partners"
    )
    technology_glossary: dict[str, str] = Field(
        default_factory=dict,
        description="Technology terms and explanations"
    )


class OrganizationContext(BaseModel):
    """Complete organizational context configuration."""
    
    # Basic information
    name: str = Field(
        ...,
        description="Organization name"
    )
    industry: str = Field(
        default="Technology",
        description="Industry sector"
    )
    description: Optional[str] = Field(
        default=None,
        description="Organization description"
    )
    
    # Technical context
    tech_stack: TechStack = Field(
        default_factory=TechStack,
        description="Technology stack preferences"
    )
    
    # Compliance and standards
    compliance: ComplianceRequirements = Field(
        default_factory=ComplianceRequirements,
        description="Compliance requirements"
    )
    
    # Naming and conventions
    naming_conventions: NamingConventions = Field(
        default_factory=NamingConventions,
        description="Requirement naming conventions"
    )
    
    # Priority mapping
    priority_mapping: PriorityMapping = Field(
        default_factory=PriorityMapping,
        description="Priority detection keywords"
    )
    
    # Risk assessment
    risk_thresholds: RiskThresholds = Field(
        default_factory=RiskThresholds,
        description="Risk assessment thresholds"
    )
    
    # Output preferences
    output_preferences: OutputPreferences = Field(
        default_factory=OutputPreferences,
        description="Output format preferences"
    )
    
    # Domain knowledge
    domain_knowledge: DomainKnowledge = Field(
        default_factory=DomainKnowledge,
        description="Domain-specific knowledge"
    )
    
    # Paths
    context_root: Optional[Path] = Field(
        default=None,
        description="Root directory for context files"
    )
    templates_dir: Optional[Path] = Field(
        default=None,
        description="Directory containing templates"
    )
    standards_dir: Optional[Path] = Field(
        default=None,
        description="Directory containing standards documents"
    )
    examples_dir: Optional[Path] = Field(
        default=None,
        description="Directory containing example RFPs"
    )
    
    @field_validator('context_root', 'templates_dir', 'standards_dir', 'examples_dir')
    @classmethod
    def validate_paths(cls, v: Optional[Path]) -> Optional[Path]:
        """Ensure paths are Path objects if provided."""
        if v is not None and not isinstance(v, Path):
            return Path(v)
        return v
    
    def get_requirement_id(self, category: str, number: int) -> str:
        """
        Generate a requirement ID based on naming conventions.
        
        Parameters
        ----------
        category : str
            Requirement category (functional, non_functional, compliance, etc.)
        number : int
            Sequential number for the requirement
            
        Returns
        -------
        str
            Formatted requirement ID (e.g., "FR-001", "NFR-042")
        """
        prefix_map = {
            "functional": self.naming_conventions.functional_prefix,
            "non_functional": self.naming_conventions.non_functional_prefix,
            "compliance": self.naming_conventions.compliance_prefix,
            "ambiguity": self.naming_conventions.ambiguity_prefix,
            "risk": self.naming_conventions.risk_prefix,
        }
        
        prefix = prefix_map.get(category, self.naming_conventions.requirement_prefix)
        separator = self.naming_conventions.separator
        padding = self.naming_conventions.padding
        
        return f"{prefix}{separator}{number:0{padding}d}"
    
    def is_high_priority(self, text: str) -> bool:
        """
        Check if text contains high-priority keywords.
        
        Parameters
        ----------
        text : str
            Text to check for priority keywords
            
        Returns
        -------
        bool
            True if text contains MUST priority keywords
        """
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in self.priority_mapping.must_keywords)
    
    def detect_priority(self, text: str) -> str:
        """
        Detect priority level from text based on keywords.
        
        Parameters
        ----------
        text : str
            Text to analyze for priority keywords
            
        Returns
        -------
        str
            Priority level: "must", "should", "could", or "wont"
        """
        text_lower = text.lower()
        
        if any(keyword in text_lower for keyword in self.priority_mapping.must_keywords):
            return "must"
        elif any(keyword in text_lower for keyword in self.priority_mapping.should_keywords):
            return "should"
        elif any(keyword in text_lower for keyword in self.priority_mapping.could_keywords):
            return "could"
        elif any(keyword in text_lower for keyword in self.priority_mapping.wont_keywords):
            return "wont"
        
        return "should"  # Default to should if no keywords found
    
    def is_high_risk(self, text: str) -> bool:
        """
        Check if text contains high-risk indicators.
        
        Parameters
        ----------
        text : str
            Text to check for risk indicators
            
        Returns
        -------
        bool
            True if text contains high-risk indicators
        """
        text_lower = text.lower()
        
        has_complexity = any(
            indicator.lower() in text_lower 
            for indicator in self.risk_thresholds.high_complexity_indicators
        )
        has_timeline_risk = any(
            flag.lower() in text_lower 
            for flag in self.risk_thresholds.timeline_red_flags
        )
        has_resource_constraint = any(
            constraint.lower() in text_lower 
            for constraint in self.risk_thresholds.resource_constraints
        )
        
        return has_complexity or has_timeline_risk or has_resource_constraint
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True

