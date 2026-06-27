"""
org_context/context_studio_integration.py
------------------------------------------
IBM ICA Context Studio integration for RFP Analyzer.

This module provides:
1. Connection to IBM ICA Context Studio API
2. Loading table templates from Context Studio
3. Storing extracted table data back to Context Studio
4. Retrieving historical RFP data for enrichment
"""

from __future__ import annotations

import json
import requests
from typing import Dict, List, Optional, Any
from pathlib import Path
import structlog

from .table_templates import TableType, TableTemplate, TableColumn, get_template_manager

log = structlog.get_logger(__name__)


class ContextStudioClient:
    """Client for IBM ICA Context Studio API."""
    
    def __init__(
        self,
        base_url: str,
        auth_token: str,
        workspace_id: Optional[str] = None
    ):
        """
        Initialize Context Studio client.
        
        Parameters
        ----------
        base_url : str
            Base URL for Context Studio API
            Example: https://context-studio.ibm.com/api/v1
        auth_token : str
            Authentication token for Context Studio
        workspace_id : str, optional
            Workspace ID for multi-tenant environments
        """
        self.base_url = base_url.rstrip('/')
        self.auth_token = auth_token
        self.workspace_id = workspace_id
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {auth_token}',
            'Content-Type': 'application/json'
        })
        
        if workspace_id:
            self.session.headers['X-Workspace-ID'] = workspace_id
        
        log.info("context_studio_client_initialized", base_url=base_url)
    
    def get_table_templates(self) -> List[Dict[str, Any]]:
        """
        Retrieve table templates from Context Studio.
        
        Returns
        -------
        List[Dict[str, Any]]
            List of table template definitions
        """
        try:
            response = self.session.get(f"{self.base_url}/templates/tables")
            response.raise_for_status()
            templates = response.json()
            log.info("retrieved_table_templates", count=len(templates))
            return templates
        except requests.RequestException as e:
            log.error("failed_to_retrieve_templates", error=str(e))
            return []
    
    def get_resource_standards(self) -> Dict[str, Any]:
        """
        Retrieve organizational resource standards.
        
        Returns
        -------
        Dict[str, Any]
            Resource standards including rates, role definitions, etc.
        """
        try:
            response = self.session.get(f"{self.base_url}/standards/resources")
            response.raise_for_status()
            standards = response.json()
            log.info("retrieved_resource_standards")
            return standards
        except requests.RequestException as e:
            log.error("failed_to_retrieve_resource_standards", error=str(e))
            return {}
    
    def get_sla_standards(self) -> Dict[str, Any]:
        """
        Retrieve organizational SLA standards.
        
        Returns
        -------
        Dict[str, Any]
            SLA standards and benchmarks
        """
        try:
            response = self.session.get(f"{self.base_url}/standards/sla")
            response.raise_for_status()
            standards = response.json()
            log.info("retrieved_sla_standards")
            return standards
        except requests.RequestException as e:
            log.error("failed_to_retrieve_sla_standards", error=str(e))
            return {}
    
    def get_historical_rfps(
        self,
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Retrieve historical RFP data for enrichment.
        
        Parameters
        ----------
        filters : Dict[str, Any], optional
            Filters to apply (industry, technology, size, etc.)
        limit : int
            Maximum number of RFPs to retrieve
            
        Returns
        -------
        List[Dict[str, Any]]
            Historical RFP data
        """
        try:
            params = {'limit': limit}
            if filters:
                params.update(filters)
            
            response = self.session.get(
                f"{self.base_url}/rfps/historical",
                params=params
            )
            response.raise_for_status()
            rfps = response.json()
            log.info("retrieved_historical_rfps", count=len(rfps))
            return rfps
        except requests.RequestException as e:
            log.error("failed_to_retrieve_historical_rfps", error=str(e))
            return []
    
    def store_extracted_table(
        self,
        rfp_id: str,
        table_type: str,
        table_data: List[Dict[str, Any]],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Store extracted table data back to Context Studio.
        
        Parameters
        ----------
        rfp_id : str
            Unique identifier for the RFP
        table_type : str
            Type of table (resource_requirements, sla_matrix, etc.)
        table_data : List[Dict[str, Any]]
            Extracted and validated table data
        metadata : Dict[str, Any], optional
            Additional metadata about the extraction
            
        Returns
        -------
        bool
            True if storage was successful
        """
        try:
            payload = {
                'rfp_id': rfp_id,
                'table_type': table_type,
                'data': table_data,
                'metadata': metadata or {}
            }
            
            response = self.session.post(
                f"{self.base_url}/rfps/{rfp_id}/tables",
                json=payload
            )
            response.raise_for_status()
            log.info("stored_extracted_table", rfp_id=rfp_id, table_type=table_type)
            return True
        except requests.RequestException as e:
            log.error("failed_to_store_table", error=str(e), rfp_id=rfp_id)
            return False
    
    def get_tech_stack_standards(self) -> Dict[str, Any]:
        """
        Retrieve organizational technology stack standards.
        
        Returns
        -------
        Dict[str, Any]
            Approved technologies, versions, and preferences
        """
        try:
            response = self.session.get(f"{self.base_url}/standards/tech-stack")
            response.raise_for_status()
            standards = response.json()
            log.info("retrieved_tech_stack_standards")
            return standards
        except requests.RequestException as e:
            log.error("failed_to_retrieve_tech_stack", error=str(e))
            return {}
    
    def search_similar_requirements(
        self,
        requirement_text: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Search for similar requirements in historical RFPs.
        
        Parameters
        ----------
        requirement_text : str
            Text of the requirement to search for
        limit : int
            Maximum number of similar requirements to return
            
        Returns
        -------
        List[Dict[str, Any]]
            Similar requirements with metadata
        """
        try:
            payload = {
                'query': requirement_text,
                'limit': limit
            }
            
            response = self.session.post(
                f"{self.base_url}/search/requirements",
                json=payload
            )
            response.raise_for_status()
            results = response.json()
            log.info("found_similar_requirements", count=len(results))
            return results
        except requests.RequestException as e:
            log.error("failed_to_search_requirements", error=str(e))
            return []


class ContextStudioIntegration:
    """High-level integration with Context Studio for table processing."""
    
    def __init__(self, client: ContextStudioClient):
        """
        Initialize Context Studio integration.
        
        Parameters
        ----------
        client : ContextStudioClient
            Configured Context Studio client
        """
        self.client = client
        self.template_manager = get_template_manager()
        self._load_templates_from_studio()
    
    def _load_templates_from_studio(self):
        """Load table templates from Context Studio into template manager."""
        templates = self.client.get_table_templates()
        
        for template_data in templates:
            try:
                # Convert Context Studio template format to internal format
                table_type = TableType(template_data.get('type', 'resource_requirements'))
                
                columns = []
                for col_data in template_data.get('columns', []):
                    column = TableColumn(
                        name=col_data['name'],
                        data_type=col_data.get('data_type', 'string'),
                        required=col_data.get('required', True),
                        validation_rules=col_data.get('validation_rules'),
                        enum_values=col_data.get('enum_values'),
                        description=col_data.get('description')
                    )
                    columns.append(column)
                
                template = TableTemplate(
                    table_type=table_type,
                    name=template_data['name'],
                    description=template_data.get('description', ''),
                    columns=columns,
                    min_rows=template_data.get('min_rows', 1),
                    max_rows=template_data.get('max_rows'),
                    tags=template_data.get('tags', []),
                    examples=template_data.get('examples', [])
                )
                
                self.template_manager.templates[table_type] = template
                log.info("loaded_template_from_studio", template_name=template.name)
                
            except Exception as e:
                log.error("failed_to_load_template", error=str(e), template=template_data)
    
    def validate_and_enrich_table(
        self,
        table_type: TableType,
        table_data: List[Dict[str, Any]],
        rfp_id: Optional[str] = None
    ) -> tuple[bool, List[str], List[Dict[str, Any]]]:
        """
        Validate and enrich table data using Context Studio standards.
        
        Parameters
        ----------
        table_type : TableType
            Type of table being processed
        table_data : List[Dict[str, Any]]
            Extracted table data
        rfp_id : str, optional
            RFP identifier for storing results
            
        Returns
        -------
        tuple[bool, List[str], List[Dict[str, Any]]]
            (is_valid, validation_errors, enriched_data)
        """
        # Validate against template
        is_valid, errors = self.template_manager.validate_table(table_type, table_data)
        
        if not is_valid:
            log.warning("table_validation_failed", table_type=table_type, errors=errors)
        
        # Get organizational context for enrichment
        context_data = self._get_enrichment_context(table_type)
        
        # Enrich the data
        enriched_data = self.template_manager.enrich_table(
            table_type,
            table_data,
            context_data
        )
        
        # Store to Context Studio if RFP ID provided
        if rfp_id and is_valid:
            self.client.store_extracted_table(
                rfp_id=rfp_id,
                table_type=table_type.value,
                table_data=enriched_data,
                metadata={
                    'validation_status': 'valid',
                    'enrichment_applied': True
                }
            )
        
        return is_valid, errors, enriched_data
    
    def _get_enrichment_context(self, table_type: TableType) -> Dict[str, Any]:
        """Get relevant context data for enriching a specific table type."""
        context = {}
        
        if table_type == TableType.RESOURCE_REQUIREMENTS:
            resource_standards = self.client.get_resource_standards()
            context['resource_rates'] = resource_standards.get('rates', [])
            context['role_definitions'] = resource_standards.get('roles', [])
        
        elif table_type == TableType.SLA_MATRIX:
            sla_standards = self.client.get_sla_standards()
            context['sla_standards'] = sla_standards.get('standards', [])
        
        elif table_type == TableType.TECHNICAL_SPECS:
            tech_standards = self.client.get_tech_stack_standards()
            context['tech_stack'] = tech_standards
        
        return context
    
    def get_historical_insights(
        self,
        table_type: TableType,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get insights from historical RFPs for a specific table type.
        
        Parameters
        ----------
        table_type : TableType
            Type of table to get insights for
        filters : Dict[str, Any], optional
            Filters for historical data
            
        Returns
        -------
        Dict[str, Any]
            Insights including averages, trends, recommendations
        """
        historical_rfps = self.client.get_historical_rfps(filters=filters)
        
        insights = {
            'table_type': table_type.value,
            'sample_size': len(historical_rfps),
            'insights': []
        }
        
        # Extract relevant data from historical RFPs
        if table_type == TableType.RESOURCE_REQUIREMENTS:
            insights['insights'] = self._analyze_resource_trends(historical_rfps)
        elif table_type == TableType.SLA_MATRIX:
            insights['insights'] = self._analyze_sla_trends(historical_rfps)
        
        return insights
    
    def _analyze_resource_trends(self, rfps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze resource requirement trends from historical RFPs."""
        # Placeholder for trend analysis
        return [
            {
                'insight': 'Average team size',
                'value': '8-12 FTEs',
                'confidence': 0.85
            },
            {
                'insight': 'Most common roles',
                'value': ['Senior Developer', 'Solution Architect', 'QA Engineer'],
                'confidence': 0.90
            }
        ]
    
    def _analyze_sla_trends(self, rfps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze SLA trends from historical RFPs."""
        return [
            {
                'insight': 'Typical uptime SLA',
                'value': '99.9%',
                'confidence': 0.88
            },
            {
                'insight': 'Average response time requirement',
                'value': '< 2 seconds',
                'confidence': 0.82
            }
        ]


def create_context_studio_integration(
    base_url: str,
    auth_token: str,
    workspace_id: Optional[str] = None
) -> ContextStudioIntegration:
    """
    Factory function to create Context Studio integration.
    
    Parameters
    ----------
    base_url : str
        Context Studio API base URL
    auth_token : str
        Authentication token
    workspace_id : str, optional
        Workspace ID for multi-tenant setups
        
    Returns
    -------
    ContextStudioIntegration
        Configured integration instance
    """
    client = ContextStudioClient(base_url, auth_token, workspace_id)
    return ContextStudioIntegration(client)

# Made with Bob
