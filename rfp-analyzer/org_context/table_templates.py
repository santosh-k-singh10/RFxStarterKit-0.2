"""
org_context/table_templates.py
-------------------------------
Table template management for IBM ICA Context Studio integration.

This module handles:
1. Loading table templates from Context Studio
2. Validating extracted tables against organizational standards
3. Enriching table data with historical context
4. Managing resource requirement templates
"""

from __future__ import annotations

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import structlog

log = structlog.get_logger(__name__)


class TableType(str, Enum):
    """Types of tables commonly found in RFPs."""
    RESOURCE_REQUIREMENTS = "resource_requirements"
    SLA_MATRIX = "sla_matrix"
    TIMELINE_MILESTONES = "timeline_milestones"
    COMPLIANCE_CHECKLIST = "compliance_checklist"
    TECHNICAL_SPECS = "technical_specs"
    PRICING_BREAKDOWN = "pricing_breakdown"
    DELIVERABLES = "deliverables"
    RISK_MATRIX = "risk_matrix"


@dataclass
class TableColumn:
    """Definition of a table column."""
    name: str
    data_type: str  # string, number, date, boolean, enum
    required: bool = True
    validation_rules: Optional[Dict[str, Any]] = None
    enum_values: Optional[List[str]] = None
    description: Optional[str] = None
    
    def validate_value(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a value against this column's rules.
        
        Returns
        -------
        tuple[bool, Optional[str]]
            (is_valid, error_message)
        """
        if value is None or value == "":
            if self.required:
                return False, f"Column '{self.name}' is required"
            return True, None
        
        # Type validation
        if self.data_type == "number":
            try:
                float(str(value))
            except ValueError:
                return False, f"Column '{self.name}' must be a number"
        
        # Enum validation
        if self.enum_values and str(value) not in self.enum_values:
            return False, f"Column '{self.name}' must be one of: {', '.join(self.enum_values)}"
        
        # Custom validation rules
        if self.validation_rules:
            if "min_value" in self.validation_rules:
                try:
                    if float(value) < self.validation_rules["min_value"]:
                        return False, f"Column '{self.name}' must be >= {self.validation_rules['min_value']}"
                except (ValueError, TypeError):
                    pass
            
            if "max_value" in self.validation_rules:
                try:
                    if float(value) > self.validation_rules["max_value"]:
                        return False, f"Column '{self.name}' must be <= {self.validation_rules['max_value']}"
                except (ValueError, TypeError):
                    pass
        
        return True, None


@dataclass
class TableTemplate:
    """Template definition for a specific table type."""
    table_type: TableType
    name: str
    description: str
    columns: List[TableColumn]
    min_rows: int = 1
    max_rows: Optional[int] = None
    tags: List[str] = field(default_factory=list)
    examples: List[Dict[str, Any]] = field(default_factory=list)
    
    def validate_table(self, table_data: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
        """
        Validate extracted table data against this template.
        
        Parameters
        ----------
        table_data : List[Dict[str, Any]]
            List of rows, where each row is a dictionary of column_name: value
            
        Returns
        -------
        tuple[bool, List[str]]
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Check row count
        if len(table_data) < self.min_rows:
            errors.append(f"Table must have at least {self.min_rows} rows, found {len(table_data)}")
        
        if self.max_rows and len(table_data) > self.max_rows:
            errors.append(f"Table must have at most {self.max_rows} rows, found {len(table_data)}")
        
        # Validate each row
        for row_idx, row in enumerate(table_data, 1):
            for column in self.columns:
                value = row.get(column.name)
                is_valid, error_msg = column.validate_value(value)
                if not is_valid:
                    errors.append(f"Row {row_idx}: {error_msg}")
        
        return len(errors) == 0, errors
    
    def enrich_table(self, table_data: List[Dict[str, Any]], context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Enrich table data with organizational context.
        
        Parameters
        ----------
        table_data : List[Dict[str, Any]]
            Extracted table data
        context_data : Dict[str, Any]
            Organizational context from Context Studio
            
        Returns
        -------
        List[Dict[str, Any]]
            Enriched table data with additional context
        """
        enriched = []
        
        for row in table_data:
            enriched_row = row.copy()
            
            # Add organizational context based on table type
            if self.table_type == TableType.RESOURCE_REQUIREMENTS:
                enriched_row = self._enrich_resource_row(enriched_row, context_data)
            elif self.table_type == TableType.SLA_MATRIX:
                enriched_row = self._enrich_sla_row(enriched_row, context_data)
            elif self.table_type == TableType.TECHNICAL_SPECS:
                enriched_row = self._enrich_tech_spec_row(enriched_row, context_data)
            
            enriched.append(enriched_row)
        
        return enriched
    
    def _enrich_resource_row(self, row: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich resource requirement row with organizational data."""
        role = row.get("role", "").lower()
        
        # Add standard rate if available
        if "resource_rates" in context:
            for rate_info in context.get("resource_rates", []):
                if rate_info.get("role", "").lower() == role:
                    row["standard_rate"] = rate_info.get("rate")
                    row["rate_currency"] = rate_info.get("currency", "USD")
                    break
        
        # Add skill requirements from org standards
        if "role_definitions" in context:
            for role_def in context.get("role_definitions", []):
                if role_def.get("role", "").lower() == role:
                    row["required_skills"] = role_def.get("required_skills", [])
                    row["preferred_skills"] = role_def.get("preferred_skills", [])
                    row["min_experience_years"] = role_def.get("min_experience", 0)
                    break
        
        return row
    
    def _enrich_sla_row(self, row: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich SLA row with organizational standards."""
        sla_type = row.get("sla_type", "").lower()
        
        # Add organizational SLA standards
        if "sla_standards" in context:
            for sla_std in context.get("sla_standards", []):
                if sla_std.get("type", "").lower() == sla_type:
                    row["org_standard"] = sla_std.get("standard_value")
                    row["meets_standard"] = self._compare_sla(
                        row.get("value"), 
                        sla_std.get("standard_value"),
                        sla_std.get("comparison", ">=")
                    )
                    break
        
        return row
    
    def _enrich_tech_spec_row(self, row: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich technical specification row with org tech stack."""
        tech_name = row.get("technology", "").lower()
        
        # Check if technology is in approved stack
        if "tech_stack" in context:
            approved_techs = [t.lower() for t in context.get("tech_stack", {}).get("approved_technologies", [])]
            row["is_approved"] = tech_name in approved_techs
            
            # Add preferred version if available
            for tech in context.get("tech_stack", {}).get("technology_versions", []):
                if tech.get("name", "").lower() == tech_name:
                    row["preferred_version"] = tech.get("version")
                    break
        
        return row
    
    def _compare_sla(self, value: Any, standard: Any, comparison: str) -> bool:
        """Compare SLA value against standard."""
        try:
            val = float(value)
            std = float(standard)
            
            if comparison == ">=":
                return val >= std
            elif comparison == "<=":
                return val <= std
            elif comparison == "==":
                return val == std
            elif comparison == ">":
                return val > std
            elif comparison == "<":
                return val < std
        except (ValueError, TypeError):
            return False
        
        return False


class TableTemplateManager:
    """Manages table templates from Context Studio."""
    
    def __init__(self):
        self.templates: Dict[TableType, TableTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default table templates."""
        # Resource Requirements Template
        self.templates[TableType.RESOURCE_REQUIREMENTS] = TableTemplate(
            table_type=TableType.RESOURCE_REQUIREMENTS,
            name="Resource Requirements",
            description="Standard template for resource/staffing requirements",
            columns=[
                TableColumn(
                    name="role",
                    data_type="string",
                    required=True,
                    description="Job role or position title"
                ),
                TableColumn(
                    name="quantity",
                    data_type="number",
                    required=True,
                    validation_rules={"min_value": 0},
                    description="Number of resources needed (FTE)"
                ),
                TableColumn(
                    name="skills",
                    data_type="string",
                    required=False,
                    description="Required skills and qualifications"
                ),
                TableColumn(
                    name="experience",
                    data_type="string",
                    required=False,
                    description="Years of experience required"
                ),
                TableColumn(
                    name="location",
                    data_type="string",
                    required=False,
                    description="Work location or timezone"
                ),
            ],
            tags=["staffing", "resources", "team"],
            examples=[
                {
                    "role": "Senior SAP Consultant",
                    "quantity": 2,
                    "skills": "SAP S/4HANA, Retail, ABAP",
                    "experience": "5+ years",
                    "location": "US Eastern Time"
                }
            ]
        )
        
        # SLA Matrix Template
        self.templates[TableType.SLA_MATRIX] = TableTemplate(
            table_type=TableType.SLA_MATRIX,
            name="SLA Matrix",
            description="Service Level Agreement requirements",
            columns=[
                TableColumn(
                    name="sla_type",
                    data_type="string",
                    required=True,
                    enum_values=["uptime", "response_time", "resolution_time", "availability"],
                    description="Type of SLA metric"
                ),
                TableColumn(
                    name="value",
                    data_type="string",
                    required=True,
                    description="SLA target value"
                ),
                TableColumn(
                    name="measurement",
                    data_type="string",
                    required=False,
                    description="How the SLA is measured"
                ),
            ],
            tags=["sla", "performance", "availability"]
        )
        
        log.info("default_templates_loaded", count=len(self.templates))
    
    def load_from_context_studio(self, context_studio_url: str, auth_token: str):
        """
        Load table templates from IBM ICA Context Studio.
        
        Parameters
        ----------
        context_studio_url : str
            URL to Context Studio API
        auth_token : str
            Authentication token for Context Studio
        """
        # TODO: Implement Context Studio API integration
        log.info("loading_templates_from_context_studio", url=context_studio_url)
        pass
    
    def get_template(self, table_type: TableType) -> Optional[TableTemplate]:
        """Get template for a specific table type."""
        return self.templates.get(table_type)
    
    def validate_table(self, table_type: TableType, table_data: List[Dict[str, Any]]) -> tuple[bool, List[str]]:
        """Validate table data against template."""
        template = self.get_template(table_type)
        if not template:
            return False, [f"No template found for table type: {table_type}"]
        
        return template.validate_table(table_data)
    
    def enrich_table(self, table_type: TableType, table_data: List[Dict[str, Any]], context_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Enrich table data with organizational context."""
        template = self.get_template(table_type)
        if not template:
            log.warning("no_template_for_enrichment", table_type=table_type)
            return table_data
        
        return template.enrich_table(table_data, context_data)


# Global instance
_template_manager: Optional[TableTemplateManager] = None


def get_template_manager() -> TableTemplateManager:
    """Get or create the global template manager instance."""
    global _template_manager
    if _template_manager is None:
        _template_manager = TableTemplateManager()
    return _template_manager

# Made with Bob
