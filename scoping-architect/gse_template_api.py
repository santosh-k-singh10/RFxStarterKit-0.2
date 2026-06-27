"""
GSE (GreenStar Estimation Engine Input) Questionnaire API Router
FastAPI endpoints for the GreenStar Estimation Engine Input Questionnaire
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import json
import os

router = APIRouter(prefix="/api/gse", tags=["GSE (GreenStar Estimation Engine Input) Questionnaire"])


# Pydantic models for API validation
class ApplicationScopeRequest(BaseModel):
    standard_applications: List[str] = Field(default_factory=list)
    additional_applications: str = ""
    module_scope: List[str] = Field(default_factory=list)


class GeographicalScopeRequest(BaseModel):
    no_of_countries: int = Field(ge=0)
    no_of_company_codes: int = Field(ge=0)
    no_of_states_usa: Optional[int] = Field(None, ge=0)
    no_of_plants: int = Field(ge=0)
    no_of_divisions: int = Field(ge=0)
    no_of_channels: Optional[int] = Field(None, ge=0)
    no_of_currencies: Optional[int] = Field(None, ge=0)
    company_revenue: str
    employees: Optional[int] = Field(None, ge=0)
    core_users: int = Field(ge=0)
    self_service_users: Optional[int] = Field(None, ge=0)
    project_language: str = "English"
    no_of_other_languages: Optional[int] = Field(None, ge=0)
    process_localisation_requirement: Optional[float] = Field(None, ge=0, le=1)
    rollout_in_scope: bool = False


class ProcessScopeRequest(BaseModel):
    bph_model: str
    impact_solution_primary: str
    impact_solution_secondary: List[str] = Field(default_factory=list)
    record_to_report: bool = False
    order_to_cash: bool = False
    procure_to_pay: bool = False
    plan_to_manufacture: bool = False
    l2_selections: Dict[str, List[str]] = Field(default_factory=dict)
    l3_selections: List[str] = Field(default_factory=list)
    custom_processes: List[str] = Field(default_factory=list)
    include_scrum_masters: bool = False


class WRICEFScopeRequest(BaseModel):
    s4_reports: int = Field(0, ge=0)
    s4_abap_interfaces: int = Field(0, ge=0)
    end_to_end_pi_interfaces: int = Field(0, ge=0)
    end_to_end_btp_interfaces: int = Field(0, ge=0)
    s4_conversions: int = Field(0, ge=0)
    s4_enhancements: int = Field(0, ge=0)
    s4_forms: int = Field(0, ge=0)
    s4_workflows: int = Field(0, ge=0)
    end_to_end_cpi_ds_interfaces: int = Field(0, ge=0)


class ApplicationDevelopmentScopeRequest(BaseModel):
    wricef_in_scope: bool = False
    pilot_scope: Optional[WRICEFScopeRequest] = None
    rollout_scope: Optional[WRICEFScopeRequest] = None
    integration_layer_type: str = ""
    no_of_systems_to_integrate: Optional[int] = Field(None, ge=0)
    interface_migration_in_scope: bool = False
    no_of_interfaces_to_migrate: Optional[int] = Field(None, ge=0)
    standard_fiori_in_scope: bool = False
    no_of_standard_fiori_apps: Optional[int] = Field(None, ge=0)
    custom_fiori_in_scope: bool = False
    no_of_custom_fiori_objects: Optional[int] = Field(None, ge=0)
    bw4hana_in_scope: bool = False
    no_of_bw_reports: Optional[int] = Field(None, ge=0)
    embedded_analytics_in_scope: bool = False
    standard_analytical_fiori_apps: Optional[int] = Field(None, ge=0)
    custom_analytical_fiori_apps: Optional[int] = Field(None, ge=0)
    sac_reporting_in_scope: bool = False
    no_of_sac_stories: Optional[int] = Field(None, ge=0)


class DataConversionScopeRequest(BaseModel):
    data_conversion_in_scope: bool = False
    data_migration_scope: str = ""
    legacy_system: str = ""
    historical_data_migration: bool = False
    data_migration_tool: str = ""
    other_tool: str = ""
    no_of_data_objects: int = Field(0, ge=0)
    no_of_data_load_cycles: int = Field(4, ge=1)
    no_of_source_systems: int = Field(1, ge=1)


class TestingScopeRequest(BaseModel):
    # Automation Testing
    automation_testing_in_scope: bool = False
    automation_testing_tool: str = ""
    no_of_automation_test_scenario_creation_sap_gui: int = Field(0, ge=0)
    no_of_automation_test_scenario_creation_web_fiori: int = Field(0, ge=0)
    no_of_automation_test_scenario_execution_sap_gui: int = Field(0, ge=0)
    no_of_automation_test_scenario_execution_web_fiori: int = Field(0, ge=0)
    no_of_automation_test_execution_cycles: int = Field(0, ge=0)
    
    # Integration Testing
    sit_testing_in_scope: bool = False
    test_scenarios_creation: int = Field(0, ge=0)
    test_scenarios_execution: int = Field(0, ge=0)
    sit_cycles: int = Field(0, ge=0, le=3)
    
    # Regression Testing
    regression_testing_in_scope: bool = False
    avg_no_of_regression_test_scenario_modification: int = Field(0, ge=0)
    modification_factor_percentage: float = Field(0.0, ge=0, le=1)
    avg_no_of_regression_test_scenario_execution: int = Field(0, ge=0)
    no_of_regression_execution_cycles: int = Field(0, ge=0)
    
    # Performance Testing
    performance_testing_in_scope: bool = False
    performance_testing_tool: str = ""
    application_complexity: str = ""


class InfrastructureAuthorizationScopeRequest(BaseModel):
    # Infrastructure
    infrastructure_provisioning_scope: List[str] = Field(default_factory=list)
    application_inventory: str = ""
    
    # Security
    security_in_scope: bool = False
    no_of_locations_plants: int = Field(0, ge=0)
    security_design_build_months: float = Field(0.0, ge=0)
    no_of_end_users: int = Field(0, ge=0)
    no_of_project_team_members: int = Field(0, ge=0)
    no_of_l3_processes: int = Field(0, ge=0)
    sap_cloud_applications: int = Field(0, ge=0)
    identity_access_mgmt: str = "Basic"
    grc_ac_only: bool = False
    css_in_scope: bool = False


class ChangeManagementTrainingScopeRequest(BaseModel):
    # OCM
    change_management_in_scope: bool = False
    ibm_involvement: str = ""
    transformation_strategy: bool = False
    stakeholder_communication_strategy: bool = False
    change_impact_analysis: bool = False
    value_realization_framework: bool = False
    organization_design: bool = False
    stakeholder_engagement: bool = False
    cultural_transformation: bool = False
    role_mapping: bool = False
    user_adoption_dashboard: bool = False
    value_realization_dashboard: bool = False
    
    # Training
    training_in_scope: bool = False
    training_approach: str = ""
    target_trainees: int = Field(0, ge=0)
    training_strategy: bool = False
    training_deployment: bool = False
    training_content_development: bool = False
    training_tool: str = ""
    reuse_adapt_percentage: float = Field(0.0, ge=0, le=1)
    no_of_level3_for_training: int = Field(0, ge=0)
    wbt_percentage: float = Field(0.0, ge=0, le=1)
    ilt_percentage: float = Field(0.0, ge=0, le=1)


class ImplementationScopeRequest(BaseModel):
    project_start_date: Optional[date] = None
    timeline_given_by_client: bool = False
    ibm_proposing_alternate_timeline: bool = False
    ibm_impact_asset_used: bool = False
    rollout_in_scope: bool = False
    rollout_type: str = ""
    no_of_rollouts_planned: int = Field(0, ge=0)
    rollout_phase_duration_factor: str = ""


class GSEQuestionnaireRequest(BaseModel):
    application_scope: ApplicationScopeRequest
    geographical_scope: GeographicalScopeRequest
    process_scope: ProcessScopeRequest
    application_development_scope: ApplicationDevelopmentScopeRequest
    data_conversion_scope: DataConversionScopeRequest
    testing_scope: TestingScopeRequest
    infrastructure_authorization_scope: InfrastructureAuthorizationScopeRequest
    change_management_training_scope: ChangeManagementTrainingScopeRequest
    implementation_scope: ImplementationScopeRequest


class GSEQuestionnaireResponse(BaseModel):
    success: bool
    message: str
    questionnaire_id: str
    saved_at: str
    data: Optional[Dict[str, Any]] = None


@router.post("/submit", response_model=GSEQuestionnaireResponse)
async def submit_questionnaire(questionnaire: GSEQuestionnaireRequest):
    """
    Submit a completed GSE (GreenStar Estimation Engine Input) questionnaire
    """
    try:
        # Generate unique ID
        questionnaire_id = f"GSE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create output directory if it doesn't exist
        output_dir = "outputs/gsc-questionnaires"
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to JSON file
        output_file = os.path.join(output_dir, f"{questionnaire_id}.json")
        
        questionnaire_data = questionnaire.dict()
        questionnaire_data["questionnaire_id"] = questionnaire_id
        questionnaire_data["submitted_at"] = datetime.now().isoformat()
        
        with open(output_file, 'w') as f:
            json.dump(questionnaire_data, f, indent=2, default=str)
        
        return GSEQuestionnaireResponse(
            success=True,
            message="Questionnaire submitted successfully",
            questionnaire_id=questionnaire_id,
            saved_at=datetime.now().isoformat(),
            data=questionnaire_data
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving questionnaire: {str(e)}")


@router.get("/questionnaire/{questionnaire_id}")
async def get_questionnaire(questionnaire_id: str):
    """
    Retrieve a saved questionnaire by ID
    """
    try:
        output_file = f"outputs/gsc-questionnaires/{questionnaire_id}.json"
        
        if not os.path.exists(output_file):
            raise HTTPException(status_code=404, detail="Questionnaire not found")
        
        with open(output_file, 'r') as f:
            data = json.load(f)
        
        return {
            "success": True,
            "questionnaire_id": questionnaire_id,
            "data": data
        }
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Questionnaire not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving questionnaire: {str(e)}")


@router.get("/questionnaires")
async def list_questionnaires():
    """
    List all saved questionnaires
    """
    try:
        output_dir = "outputs/gsc-questionnaires"
        
        if not os.path.exists(output_dir):
            return {"success": True, "questionnaires": []}
        
        files = [f for f in os.listdir(output_dir) if f.endswith('.json')]
        questionnaires = []
        
        for file in files:
            with open(os.path.join(output_dir, file), 'r') as f:
                data = json.load(f)
                questionnaires.append({
                    "questionnaire_id": data.get("questionnaire_id"),
                    "submitted_at": data.get("submitted_at"),
                    "project_name": data.get("application_scope", {}).get("standard_applications", ["Unknown"])[0] if data.get("application_scope", {}).get("standard_applications") else "Unknown"
                })
        
        return {
            "success": True,
            "count": len(questionnaires),
            "questionnaires": sorted(questionnaires, key=lambda x: x["submitted_at"], reverse=True)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing questionnaires: {str(e)}")


@router.get("/dropdown-options")
async def get_dropdown_options():
    """
    Get all dropdown options for the form
    """
    return {
        "standard_applications": [
            "SAP S/4HANA",
            "Workday Financials",
            "Oracle ERP",
            "Salesforce Cloud",
            "Microsoft Dynamics 365"
        ],
        "company_revenue": [
            "<$1B USD in annual revenue",
            "$1B-$5B USD in annual revenue",
            "$5B-$10B USD in annual revenue",
            ">$10B USD in annual revenue"
        ],
        "project_language": ["English", "Non-English"],
        "bph_models": ["APQC", "Application BPH", "IMPACT BPH"],
        "integration_layer_types": ["PI/PO", "BTP", "CPI", "Other"],
        "data_migration_scopes": ["Extract Only", "Transform Only", "Load Only", "Extract, Transform, Load"],
        "data_migration_tools": ["DMC", "SAP Data Services (BODS)", "Other"],
        "automation_testing_tools": ["TOSCA SAP GUI", "TOSCA Web/Fiori", "UFT", "Selenium"],
        "application_complexity": ["Simple", "Medium", "Complex"],
        "infrastructure_provisioning_scope": ["Landscape Design", "System Provisioning", "Network Configuration", "Backup & Recovery"],
        "identity_access_mgmt": ["Basic", "Advanced", "Enterprise"],
        "ibm_involvement": ["Only Advisory Scope", "Full"],
        "training_approach": ["Train The Trainer [TTT]", "Direct Training", "Hybrid"],
        "training_tools": ["Enable Now", "No Training Tool", "Custom Tool"],
        "rollout_types": ["Geographical", "Functional", "Hybrid"],
        "rollout_phase_duration_factors": ["Low", "Medium", "High"]
    }


@router.post("/prefill")
async def prefill_from_enriched_json(enriched_data: dict):
    """
    Extract GSE (GreenStar Estimation Engine Input) questionnaire pre-fill data from enriched RFP JSON.

    Expects enriched JSON with scoping_metadata block.
    Returns flat field mapping ready for GSE form population.
    """
    try:
        scoping_metadata = enriched_data.get("scoping_metadata", {})
        
        if not scoping_metadata:
            raise HTTPException(
                status_code=400,
                detail="No scoping_metadata found in enriched JSON. Ensure the enrichment pipeline has run."
            )
        
        # Helper to safely extract value from metadata field
        def _val(path: str, default=None):
            keys = path.split('.')
            node = scoping_metadata
            for key in keys:
                if isinstance(node, dict):
                    node = node.get(key)
                else:
                    return default
            if isinstance(node, dict) and 'value' in node:
                return node['value']
            return default
        
        # Helper to safely extract confidence from metadata field
        def _conf(path: str, default="needs-input"):
            keys = path.split('.')
            node = scoping_metadata
            for key in keys:
                if isinstance(node, dict):
                    node = node.get(key)
                else:
                    return default
            if isinstance(node, dict) and 'confidence' in node:
                return node['confidence']
            return default
        
        # Map scoping_metadata to GSE fields
        fields = {
            # Geography
            "no_of_countries": _val("geography.no_of_countries"),
            "no_of_company_codes": _val("geography.no_of_company_codes"),
            "no_of_plants": _val("geography.no_of_plants"),
            "no_of_divisions": _val("geography.no_of_divisions"),
            "project_language": _val("geography.project_language", "English"),
            "rollout_in_scope": "Yes" if _val("geography.rollout_in_scope") else "No",
            "rollout_type": _val("geography.rollout_type", "Geographical"),
            "no_of_rollouts": _val("geography.no_of_rollouts"),
            "timeline_given_by_client": "Yes" if _val("geography.timeline_given_by_client") else "No",
            
            # Users
            "core_users": _val("users.core_users"),
            "self_service_users": _val("users.self_service_users"),
            "end_users": _val("users.end_users"),
            "target_trainees": _val("users.target_trainees"),
            
            # Applications
            "standard_applications": _val("applications.standard_applications", []),
            "additional_applications": (
                ", ".join(_val("applications.additional_applications", []) or [])
                if isinstance(_val("applications.additional_applications"), list)
                else str(_val("applications.additional_applications") or "")
            ),
            "module_scope": _val("applications.module_scope", []),
            "l1_processes": _val("applications.l1_processes", []),
            
            # Implementation
            "bph_model": _val("implementation.bph_model", "IMPACT BPH"),
            
            # WRICEF
            "wricef_in_scope": "Yes" if _val("wricef.wricef_in_scope") else "No",
            "integration_layer": _val("wricef.integration_layer", "BTP"),
            "pilot_reports": _val("wricef.reports", 0),
            "pilot_forms": _val("wricef.forms", 0),
            "pilot_enhancements": _val("wricef.enhancements", 0),
            "pilot_abap_interfaces": _val("wricef.abap_interfaces", 0),
            "pilot_btp_interfaces": _val("wricef.btp_interfaces", 0),
            "pilot_conversions": _val("wricef.conversions"),
            
            # Data Migration
            "data_conversion_in_scope": "Yes" if _val("data_migration.in_scope") else "No",
            "data_migration_tool": _val("data_migration.tool", "DMC"),
            "no_of_data_objects": _val("data_migration.no_of_data_objects"),
            "no_of_load_cycles": _val("data_migration.no_of_load_cycles", 4),
            "no_of_source_systems": _val("data_migration.no_of_source_systems"),
            
            # Testing
            "automation_testing_in_scope": "Yes" if _val("testing.automation_in_scope") else "No",
            "sit_in_scope": "Yes" if _val("testing.sit_in_scope") else "No",
            "sit_cycles": _val("testing.sit_cycles", 2),
            "sit_scenarios_proxy": _val("testing.sit_scenarios_proxy"),
            
            # Security
            "security_in_scope": "Yes" if _val("security.in_scope") else "No",
            "no_of_l3_processes": _val("security.no_of_l3_processes"),
            
            # Change Management
            "ocm_in_scope": "Yes" if _val("change_management.ocm_in_scope") else "No",
            "training_in_scope": "Yes" if _val("change_management.training_in_scope") else "No",
            "training_approach": _val("change_management.training_approach"),
            "ibm_involvement": _val("change_management.ibm_involvement", "Full"),
        }
        
        # Build confidence map
        confidence = {
            "no_of_countries": _conf("geography.no_of_countries"),
            "no_of_company_codes": _conf("geography.no_of_company_codes"),
            "no_of_plants": _conf("geography.no_of_plants"),
            "no_of_divisions": _conf("geography.no_of_divisions"),
            "project_language": _conf("geography.project_language"),
            "rollout_in_scope": _conf("geography.rollout_in_scope"),
            "rollout_type": _conf("geography.rollout_type"),
            "no_of_rollouts": _conf("geography.no_of_rollouts"),
            "timeline_given_by_client": _conf("geography.timeline_given_by_client"),
            "core_users": _conf("users.core_users"),
            "self_service_users": _conf("users.self_service_users"),
            "end_users": _conf("users.end_users"),
            "target_trainees": _conf("users.target_trainees"),
            "standard_applications": _conf("applications.standard_applications"),
            "additional_applications": _conf("applications.additional_applications"),
            "module_scope": _conf("applications.module_scope"),
            "l1_processes": _conf("applications.l1_processes"),
            "bph_model": _conf("implementation.bph_model"),
            "wricef_in_scope": _conf("wricef.wricef_in_scope"),
            "integration_layer": _conf("wricef.integration_layer"),
            "pilot_reports": _conf("wricef.reports"),
            "pilot_forms": _conf("wricef.forms"),
            "pilot_enhancements": _conf("wricef.enhancements"),
            "pilot_abap_interfaces": _conf("wricef.abap_interfaces"),
            "pilot_btp_interfaces": _conf("wricef.btp_interfaces"),
            "pilot_conversions": _conf("wricef.conversions"),
            "data_conversion_in_scope": _conf("data_migration.in_scope"),
            "data_migration_tool": _conf("data_migration.tool"),
            "no_of_data_objects": _conf("data_migration.no_of_data_objects"),
            "no_of_load_cycles": _conf("data_migration.no_of_load_cycles"),
            "no_of_source_systems": _conf("data_migration.no_of_source_systems"),
            "automation_testing_in_scope": _conf("testing.automation_in_scope"),
            "sit_in_scope": _conf("testing.sit_in_scope"),
            "sit_cycles": _conf("testing.sit_cycles"),
            "sit_scenarios_proxy": _conf("testing.sit_scenarios_proxy"),
            "security_in_scope": _conf("security.in_scope"),
            "no_of_l3_processes": _conf("security.no_of_l3_processes"),
            "ocm_in_scope": _conf("change_management.ocm_in_scope"),
            "training_in_scope": _conf("change_management.training_in_scope"),
            "training_approach": _conf("change_management.training_approach"),
            "ibm_involvement": _conf("change_management.ibm_involvement"),
        }
        
        # Get fill summary
        fill_summary = scoping_metadata.get("fill_summary", {})
        
        return {
            "fields": fields,
            "confidence": confidence,
            "fill_summary": {
                "auto_filled": fill_summary.get("auto_filled", 0),
                "estimated": fill_summary.get("estimated", 0),
                "needs_input": fill_summary.get("needs_input", 0),
                "fill_rate_pct": fill_summary.get("fill_rate_pct", 0.0)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error extracting GSE pre-fill data: {str(e)}")

# Made with Bob
