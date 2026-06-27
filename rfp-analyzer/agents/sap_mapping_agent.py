"""
SAP Mapping Agent - Maps RFP requirements to SAP modules.

This agent analyzes requirements and identifies appropriate SAP modules.
"""

import json
from typing import Dict, List, Any
from pathlib import Path


class SAPMappingAgent:
    """Agent for mapping RFP requirements to SAP modules."""
    
    def __init__(self):
        """Initialize the SAP Mapping Agent."""
        self.sap_modules = {
            "FI": ["financial", "accounting", "general ledger", "accounts payable", "accounts receivable", "GL", "AP", "AR"],
            "CO": ["controlling", "cost center", "profit center", "internal orders", "cost accounting"],
            "MM": ["materials management", "procurement", "purchasing", "inventory", "purchase order", "goods receipt"],
            "SD": ["sales", "distribution", "order management", "pricing", "sales order", "delivery", "shipping"],
            "PP": ["production planning", "manufacturing", "work orders", "capacity planning", "MRP"],
            "QM": ["quality management", "inspection", "quality control", "quality assurance"],
            "PM": ["plant maintenance", "equipment", "maintenance orders", "preventive maintenance"],
            "HR/HCM": ["human resources", "payroll", "personnel", "time management", "employee", "HR"],
            "WM": ["warehouse management", "storage", "goods movement", "bin management"],
            "PS": ["project system", "project management", "wbs", "project"],
            "BW/BI": ["business warehouse", "reporting", "analytics", "data warehouse", "BI", "business intelligence"],
            "CRM": ["customer relationship", "sales force", "marketing", "customer"],
            "SRM": ["supplier relationship", "vendor management", "sourcing", "supplier"],
            "SCM": ["supply chain", "planning", "logistics", "supply"],
        }
    
    def analyze_requirements(self, requirements: List[str]) -> Dict[str, Any]:
        """
        Analyze requirements and map them to SAP modules.
        
        Args:
            requirements: List of requirement descriptions
            
        Returns:
            Dictionary with mapped modules, coverage analysis, recommendations, and gaps
        """
        mapped_modules = {}
        
        for req in requirements:
            req_lower = req.lower()
            for module, keywords in self.sap_modules.items():
                if any(keyword in req_lower for keyword in keywords):
                    if module not in mapped_modules:
                        mapped_modules[module] = []
                    mapped_modules[module].append(req)
        
        # Calculate coverage
        total_requirements = len(requirements)
        mapped_requirements = sum(len(reqs) for reqs in mapped_modules.values())
        coverage_percentage = (mapped_requirements / total_requirements * 100) if total_requirements > 0 else 0
        
        # Identify gaps
        unmapped_requirements = [
            req for req in requirements
            if not any(req in reqs for reqs in mapped_modules.values())
        ]
        
        return {
            "mapped_modules": mapped_modules,
            "coverage_analysis": {
                "total_requirements": total_requirements,
                "mapped_requirements": mapped_requirements,
                "coverage_percentage": round(coverage_percentage, 2),
            },
            "recommendations": self._generate_recommendations(mapped_modules),
            "gaps": {
                "unmapped_requirements": unmapped_requirements,
                "custom_development_needed": len(unmapped_requirements) > 0,
            }
        }
    
    def _generate_recommendations(self, mapped_modules: Dict[str, List[str]]) -> List[str]:
        """Generate implementation recommendations."""
        recommendations = []
        
        if not mapped_modules:
            recommendations.append("No SAP modules identified. Consider custom development or alternative solutions.")
            return recommendations
        
        module_recommendations = {
            "FI": "Implement SAP FI for financial accounting with standard chart of accounts",
            "CO": "Set up cost center accounting for better cost control and reporting",
            "MM": "Deploy MM module for integrated procurement and inventory management",
            "SD": "Implement SD for end-to-end sales order processing",
            "PP": "Use PP module for production planning and shop floor control",
            "HR/HCM": "Deploy HCM for comprehensive human resource management",
            "BW/BI": "Implement BW/BI for advanced analytics and reporting capabilities",
        }
        
        for module in mapped_modules.keys():
            if module in module_recommendations:
                recommendations.append(module_recommendations[module])
        
        if len(mapped_modules) > 1:
            recommendations.append(
                f"Plan for integration between {len(mapped_modules)} SAP modules to ensure data consistency"
            )
        
        if len(mapped_modules) >= 5:
            recommendations.append("Consider SAP S/4HANA for comprehensive enterprise solution")
        
        return recommendations
    
    def generate_module_summary(self, analysis_result: Dict[str, Any]) -> str:
        """Generate a human-readable summary."""
        summary_lines = ["SAP Module Mapping Analysis", "=" * 50, ""]
        
        coverage = analysis_result["coverage_analysis"]
        summary_lines.append(f"Coverage: {coverage['mapped_requirements']}/{coverage['total_requirements']} requirements ({coverage['coverage_percentage']}%)")
        summary_lines.append("")
        
        summary_lines.append("Identified SAP Modules:")
        for module, requirements in analysis_result["mapped_modules"].items():
            summary_lines.append(f"  • {module}: {len(requirements)} requirement(s)")
        summary_lines.append("")
        
        if analysis_result["recommendations"]:
            summary_lines.append("Recommendations:")
            for rec in analysis_result["recommendations"]:
                summary_lines.append(f"  • {rec}")
            summary_lines.append("")
        
        gaps = analysis_result["gaps"]
        if gaps["unmapped_requirements"]:
            summary_lines.append(f"Gaps Identified: {len(gaps['unmapped_requirements'])} unmapped requirement(s)")
            summary_lines.append("These may require custom development or additional modules.")
        
        return "\n".join(summary_lines)


def create_sap_mapping_agent() -> SAPMappingAgent:
    """Factory function to create a SAP Mapping Agent instance."""
    return SAPMappingAgent()


def map_to_sap_modules(requirements: list) -> list:
    """
    Map requirements to SAP modules by adding sap_modules field to each requirement.
    
    Args:
        requirements: List of Requirement objects
        
    Returns:
        Updated list of requirements with SAP module mappings
    """
    agent = SAPMappingAgent()
    
    for req in requirements:
        # Get requirement text
        req_text = req.description if hasattr(req, 'description') else str(req)
        req_text_lower = req_text.lower()
        
        # Find matching SAP modules
        matched_modules = []
        for module, keywords in agent.sap_modules.items():
            if any(keyword in req_text_lower for keyword in keywords):
                matched_modules.append(module)
        
        # Add SAP modules to requirement - use sap_modules attribute directly
        # The Requirement model doesn't have a metadata dict, so we set the attribute directly
        try:
            req.sap_modules = matched_modules
        except (AttributeError, TypeError):
            # If the model doesn't allow setting this attribute, skip it
            pass
    
    return requirements
