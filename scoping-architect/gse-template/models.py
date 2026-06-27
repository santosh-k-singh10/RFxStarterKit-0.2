"""
GSE (GreenStar Estimation Engine Input) Models
Data models for SAP implementation scoping questionnaire
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import date
from enum import Enum


class FieldType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    DROPDOWN = "dropdown"
    MULTI_SELECT = "multi_select"
    PERCENTAGE = "percentage"
    DATE = "date"
    YES_NO = "yes_no"


class FieldRequirement(str, Enum):
    MANDATORY = "M"
    OPTIONAL = "O"


@dataclass
class ApplicationScope:
    """Section 1: Application Scope"""
    standard_applications: List[str] = field(default_factory=list)  # Multi-select
    additional_applications: str = ""  # Free text
    module_scope: List[str] = field(default_factory=list)  # Multi-select


@dataclass
class GeographicalScope:
    """Section 2: Geographical/Organization Scope"""
    no_of_countries: int = 0
    no_of_company_codes: int = 0
    no_of_states_usa: Optional[int] = None
    no_of_plants: int = 0
    no_of_divisions: int = 0
    no_of_channels: Optional[int] = None
    no_of_currencies: Optional[int] = None
    company_revenue: str = ""  # Dropdown
    employees: Optional[int] = None
    core_users: int = 0
    self_service_users: Optional[int] = None
    project_language: str = "English"
    no_of_other_languages: Optional[int] = None
    process_localisation_requirement: Optional[float] = None
    rollout_in_scope: bool = False


@dataclass
class ProcessScope:
    """Section 3: Business Process Scope"""
    bph_model: str = ""  # Dropdown: APQC, Application BPH, IMPACT BPH
    impact_solution_primary: str = ""
    impact_solution_secondary: List[str] = field(default_factory=list)
    
    # L1 Process Scope
    record_to_report: bool = False
    order_to_cash: bool = False
    procure_to_pay: bool = False
    plan_to_manufacture: bool = False
    
    # L2 and L3 selections stored as dict
    l2_selections: Dict[str, List[str]] = field(default_factory=dict)
    l3_selections: List[str] = field(default_factory=list)
    custom_processes: List[str] = field(default_factory=list)
    include_scrum_masters: bool = False


@dataclass
class WRICEFScope:
    """WRICEF Objects Scope"""
    s4_reports: int = 0
    s4_abap_interfaces: int = 0
    end_to_end_pi_interfaces: int = 0
    end_to_end_btp_interfaces: int = 0
    s4_conversions: int = 0
    s4_enhancements: int = 0
    s4_forms: int = 0
    s4_workflows: int = 0
    end_to_end_cpi_ds_interfaces: int = 0
    
    @property
    def total(self) -> int:
        return (self.s4_reports + self.s4_abap_interfaces + 
                self.end_to_end_pi_interfaces + self.end_to_end_btp_interfaces +
                self.s4_conversions + self.s4_enhancements + self.s4_forms +
                self.s4_workflows + self.end_to_end_cpi_ds_interfaces)


@dataclass
class ApplicationDevelopmentScope:
    """Section 4: Application Development Scope"""
    wricef_in_scope: bool = False
    pilot_scope: Optional[WRICEFScope] = None
    rollout_scope: Optional[WRICEFScope] = None
    
    # Integration Settings
    integration_layer_type: str = ""  # PI/PO, BTP, etc.
    no_of_systems_to_integrate: Optional[int] = None
    interface_migration_in_scope: bool = False
    no_of_interfaces_to_migrate: Optional[int] = None
    
    # Fiori Scope
    standard_fiori_in_scope: bool = False
    no_of_standard_fiori_apps: Optional[int] = None
    custom_fiori_in_scope: bool = False
    no_of_custom_fiori_objects: Optional[int] = None
    
    # Analytics Scope
    bw4hana_in_scope: bool = False
    no_of_bw_reports: Optional[int] = None
    embedded_analytics_in_scope: bool = False
    standard_analytical_fiori_apps: Optional[int] = None
    custom_analytical_fiori_apps: Optional[int] = None
    sac_reporting_in_scope: bool = False
    no_of_sac_stories: Optional[int] = None


@dataclass
class DataConversionScope:
    """Section 5: Data Conversion Scope"""
    data_conversion_in_scope: bool = False
    data_migration_scope: str = ""  # Extract, Transform, Load
    legacy_system: str = ""
    historical_data_migration: bool = False
    data_migration_tool: str = ""  # DMC, BODS, etc.
    other_tool: str = ""
    no_of_data_objects: int = 0
    no_of_data_load_cycles: int = 4
    no_of_source_systems: int = 1


@dataclass
class AutomationTestingScope:
    """Automation Testing"""
    automation_testing_in_scope: bool = False
    automation_testing_tool: str = ""
    no_of_automation_test_scenario_creation_sap_gui: int = 0
    no_of_automation_test_scenario_creation_web_fiori: int = 0
    no_of_automation_test_scenario_execution_sap_gui: int = 0
    no_of_automation_test_scenario_execution_web_fiori: int = 0
    no_of_automation_test_execution_cycles: int = 0


@dataclass
class IntegrationTestingScope:
    """Integration Testing (SIT)"""
    sit_testing_in_scope: bool = False
    test_scenarios_creation: int = 0
    test_scenarios_execution: int = 0
    sit_cycles: int = 0  # Max 3


@dataclass
class RegressionTestingScope:
    """Regression Testing"""
    regression_testing_in_scope: bool = False
    avg_no_of_regression_test_scenario_modification: int = 0
    modification_factor_percentage: float = 0.0
    avg_no_of_regression_test_scenario_execution: int = 0
    no_of_regression_execution_cycles: int = 0


@dataclass
class PerformanceTestingScope:
    """Performance Testing"""
    performance_testing_in_scope: bool = False
    performance_testing_tool: str = ""
    application_complexity: str = ""  # Simple, Medium, Complex


@dataclass
class TestingScope:
    """Section 6: Testing Scope"""
    automation_testing: Optional[AutomationTestingScope] = None
    integration_testing: Optional[IntegrationTestingScope] = None
    regression_testing: Optional[RegressionTestingScope] = None
    performance_testing: Optional[PerformanceTestingScope] = None


@dataclass
class InfrastructureScope:
    """Infrastructure Provisioning/Basis Scope"""
    infrastructure_provisioning_scope: List[str] = field(default_factory=list)  # Multi-select
    application_inventory: str = ""


@dataclass
class SecurityScope:
    """Security Scope"""
    security_in_scope: bool = False
    no_of_locations_plants: int = 0
    security_design_build_months: float = 0.0
    no_of_end_users: int = 0
    no_of_project_team_members: int = 0
    no_of_l3_processes: int = 0
    sap_cloud_applications: int = 0
    identity_access_mgmt: str = "Basic"
    grc_ac_only: bool = False
    css_in_scope: bool = False


@dataclass
class InfrastructureAuthorizationScope:
    """Section 7: Infrastructure & Authorization Scope"""
    infrastructure: Optional[InfrastructureScope] = None
    security: Optional[SecurityScope] = None


@dataclass
class OCMScope:
    """Organizational Change Management Scope"""
    change_management_in_scope: bool = False
    ibm_involvement: str = ""  # Only Advisory Scope, Full
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


@dataclass
class TrainingScope:
    """Training Scope"""
    training_in_scope: bool = False
    training_approach: str = ""  # Train The Trainer, etc.
    target_trainees: int = 0
    training_strategy: bool = False
    training_deployment: bool = False
    training_content_development: bool = False
    training_tool: str = ""  # Enable Now, etc.
    reuse_adapt_percentage: float = 0.0
    no_of_level3_for_training: int = 0
    wbt_percentage: float = 0.0
    ilt_percentage: float = 0.0


@dataclass
class ChangeManagementTrainingScope:
    """Section 8: Change Management & Training Scope"""
    ocm: Optional[OCMScope] = None
    training: Optional[TrainingScope] = None


@dataclass
class ImplementationScope:
    """Section 9: Implementation Scope"""
    project_start_date: Optional[date] = None
    timeline_given_by_client: bool = False
    ibm_proposing_alternate_timeline: bool = False
    ibm_impact_asset_used: bool = False
    rollout_in_scope: bool = False
    rollout_type: str = ""  # Geographical/Functional
    no_of_rollouts_planned: int = 0
    rollout_phase_duration_factor: str = ""  # Low, Medium, High


@dataclass
class GSEQuestionnaire:
    """Complete GSE (GreenStar Estimation Engine Input) Scoping Questionnaire"""
    application_scope: ApplicationScope = field(default_factory=ApplicationScope)
    geographical_scope: GeographicalScope = field(default_factory=GeographicalScope)
    process_scope: ProcessScope = field(default_factory=ProcessScope)
    application_development_scope: ApplicationDevelopmentScope = field(default_factory=ApplicationDevelopmentScope)
    data_conversion_scope: DataConversionScope = field(default_factory=DataConversionScope)
    testing_scope: TestingScope = field(default_factory=TestingScope)
    infrastructure_authorization_scope: InfrastructureAuthorizationScope = field(default_factory=InfrastructureAuthorizationScope)
    change_management_training_scope: ChangeManagementTrainingScope = field(default_factory=ChangeManagementTrainingScope)
    implementation_scope: ImplementationScope = field(default_factory=ImplementationScope)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            "application_scope": self.application_scope.__dict__,
            "geographical_scope": self.geographical_scope.__dict__,
            "process_scope": self.process_scope.__dict__,
            "application_development_scope": self.application_development_scope.__dict__,
            "data_conversion_scope": self.data_conversion_scope.__dict__,
            "testing_scope": self.testing_scope.__dict__ if self.testing_scope else None,
            "infrastructure_authorization_scope": self.infrastructure_authorization_scope.__dict__ if self.infrastructure_authorization_scope else None,
            "change_management_training_scope": self.change_management_training_scope.__dict__ if self.change_management_training_scope else None,
            "implementation_scope": self.implementation_scope.__dict__,
        }

# Made with Bob
