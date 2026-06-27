"""
core/table_processor.py
-----------------------
Enhanced table processing with Context Studio integration.

This module extends the basic ingestor to:
1. Detect and classify table types
2. Parse table structure into structured data
3. Validate against Context Studio templates
4. Enrich with organizational context
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional, Tuple
import re
import structlog

from core.schemas import DocumentChunk
from org_context.table_templates import TableType, get_template_manager
from org_context.context_studio_integration import ContextStudioIntegration

log = structlog.get_logger(__name__)


class TableProcessor:
    """Processes tables extracted from RFP documents."""
    
    def __init__(self, context_studio: Optional[ContextStudioIntegration] = None):
        """
        Initialize table processor.
        
        Parameters
        ----------
        context_studio : ContextStudioIntegration, optional
            Context Studio integration for validation and enrichment
        """
        self.context_studio = context_studio
        self.template_manager = get_template_manager()
    
    def process_table_chunk(
        self,
        chunk: DocumentChunk,
        rfp_id: Optional[str] = None
    ) -> Tuple[Optional[TableType], List[Dict[str, Any]], Dict[str, Any]]:
        """
        Process a document chunk containing table data.
        
        Parameters
        ----------
        chunk : DocumentChunk
            Document chunk with [TABLE DATA] markers
        rfp_id : str, optional
            RFP identifier for Context Studio storage
            
        Returns
        -------
        Tuple[Optional[TableType], List[Dict[str, Any]], Dict[str, Any]]
            (detected_table_type, parsed_data, metadata)
        """
        # Extract table text
        table_text = self._extract_table_text(chunk.text)
        if not table_text:
            return None, [], {}
        
        # Detect table type
        table_type = self._detect_table_type(table_text, chunk.section)
        log.info("detected_table_type", type=table_type, section=chunk.section)
        
        # Parse table into structured data
        parsed_data = self._parse_table(table_text)
        
        if not parsed_data:
            log.warning("failed_to_parse_table", section=chunk.section)
            return table_type, [], {}
        
        # Validate and enrich if Context Studio is available
        metadata = {
            'section': chunk.section,
            'page': chunk.page,
            'raw_text': table_text[:500]  # First 500 chars for reference
        }
        
        if self.context_studio and table_type:
            is_valid, errors, enriched_data = self.context_studio.validate_and_enrich_table(
                table_type=table_type,
                table_data=parsed_data,
                rfp_id=rfp_id
            )
            
            metadata['validated'] = is_valid
            metadata['validation_errors'] = errors
            metadata['enriched'] = True
            
            return table_type, enriched_data, metadata
        
        return table_type, parsed_data, metadata
    
    def _extract_table_text(self, text: str) -> Optional[str]:
        """Extract text between [TABLE DATA] markers."""
        match = re.search(r'\[TABLE DATA\](.*?)\[END TABLE\]', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None
    
    def _detect_table_type(self, table_text: str, section: str) -> Optional[TableType]:
        """
        Detect the type of table based on content and section.
        
        Parameters
        ----------
        table_text : str
            Raw table text
        section : str
            Section heading where table was found
            
        Returns
        -------
        Optional[TableType]
            Detected table type or None
        """
        section_lower = section.lower()
        text_lower = table_text.lower()
        
        # Resource requirements indicators
        if any(keyword in section_lower for keyword in ['resource', 'staffing', 'team', 'personnel']):
            if any(keyword in text_lower for keyword in ['fte', 'role', 'position', 'consultant', 'developer']):
                return TableType.RESOURCE_REQUIREMENTS
        
        # SLA indicators
        if any(keyword in section_lower for keyword in ['sla', 'service level', 'performance']):
            if any(keyword in text_lower for keyword in ['uptime', 'availability', 'response time', '%']):
                return TableType.SLA_MATRIX
        
        # Timeline indicators
        if any(keyword in section_lower for keyword in ['timeline', 'schedule', 'milestone', 'phase']):
            if any(keyword in text_lower for keyword in ['date', 'week', 'month', 'quarter', 'deliverable']):
                return TableType.TIMELINE_MILESTONES
        
        # Compliance indicators
        if any(keyword in section_lower for keyword in ['compliance', 'regulatory', 'certification']):
            return TableType.COMPLIANCE_CHECKLIST
        
        # Technical specs indicators
        if any(keyword in section_lower for keyword in ['technical', 'technology', 'infrastructure', 'architecture']):
            return TableType.TECHNICAL_SPECS
        
        # Pricing indicators
        if any(keyword in section_lower for keyword in ['pricing', 'cost', 'budget', 'financial']):
            return TableType.PRICING_BREAKDOWN
        
        # Default to resource requirements if contains role-like keywords
        if any(keyword in text_lower for keyword in ['role', 'position', 'fte', 'hours']):
            return TableType.RESOURCE_REQUIREMENTS
        
        return None
    
    def _parse_table(self, table_text: str) -> List[Dict[str, Any]]:
        """
        Parse table text into structured data.
        
        This is a heuristic parser that handles common table formats.
        For production, consider using more sophisticated table parsing libraries.
        
        Parameters
        ----------
        table_text : str
            Raw table text
            
        Returns
        -------
        List[Dict[str, Any]]
            Parsed table rows as dictionaries
        """
        lines = [line.strip() for line in table_text.split('\n') if line.strip()]
        
        if len(lines) < 2:
            return []
        
        # Try to detect delimiter (|, tab, multiple spaces)
        first_line = lines[0]
        if '|' in first_line:
            return self._parse_pipe_delimited(lines)
        elif '\t' in first_line:
            return self._parse_tab_delimited(lines)
        else:
            return self._parse_space_delimited(lines)
    
    def _parse_pipe_delimited(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse pipe-delimited table (| col1 | col2 |)."""
        # Extract headers
        header_line = lines[0]
        headers = [h.strip() for h in header_line.split('|') if h.strip()]
        
        # Skip separator line if present (|---|---|)
        data_start = 2 if len(lines) > 1 and '-' in lines[1] else 1
        
        rows = []
        for line in lines[data_start:]:
            if not line or '-' in line:
                continue
            
            values = [v.strip() for v in line.split('|') if v.strip()]
            if len(values) == len(headers):
                row = dict(zip(headers, values))
                rows.append(row)
        
        return rows
    
    def _parse_tab_delimited(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse tab-delimited table."""
        headers = lines[0].split('\t')
        headers = [h.strip() for h in headers if h.strip()]
        
        rows = []
        for line in lines[1:]:
            values = line.split('\t')
            values = [v.strip() for v in values]
            if len(values) == len(headers):
                row = dict(zip(headers, values))
                rows.append(row)
        
        return rows
    
    def _parse_space_delimited(self, lines: List[str]) -> List[Dict[str, Any]]:
        """Parse space-delimited table (multiple spaces as delimiter)."""
        # Split on 2+ spaces
        headers = re.split(r'\s{2,}', lines[0])
        headers = [h.strip() for h in headers if h.strip()]
        
        rows = []
        for line in lines[1:]:
            values = re.split(r'\s{2,}', line)
            values = [v.strip() for v in values if v.strip()]
            
            # Try to match values to headers
            if len(values) >= len(headers):
                row = dict(zip(headers, values[:len(headers)]))
                rows.append(row)
            elif len(values) > 0:
                # Partial match - fill missing values with empty strings
                row = {h: values[i] if i < len(values) else '' for i, h in enumerate(headers)}
                rows.append(row)
        
        return rows
    
    def get_table_summary(
        self,
        table_type: TableType,
        table_data: List[Dict[str, Any]]
    ) -> str:
        """
        Generate a human-readable summary of table data.
        
        Parameters
        ----------
        table_type : TableType
            Type of table
        table_data : List[Dict[str, Any]]
            Parsed table data
            
        Returns
        -------
        str
            Summary text
        """
        if not table_data:
            return "Empty table"
        
        summary_parts = [f"{table_type.value.replace('_', ' ').title()} ({len(table_data)} rows)"]
        
        if table_type == TableType.RESOURCE_REQUIREMENTS:
            total_fte = sum(float(row.get('quantity', 0) or 0) for row in table_data)
            roles = [row.get('role', 'Unknown') for row in table_data]
            summary_parts.append(f"Total FTE: {total_fte}")
            summary_parts.append(f"Roles: {', '.join(roles[:3])}")
            if len(roles) > 3:
                summary_parts.append(f"... and {len(roles) - 3} more")
        
        elif table_type == TableType.SLA_MATRIX:
            sla_types = [row.get('sla_type', 'Unknown') for row in table_data]
            summary_parts.append(f"SLA Types: {', '.join(set(sla_types))}")
        
        return " | ".join(summary_parts)


def process_tables_in_chunks(
    chunks: List[DocumentChunk],
    context_studio: Optional[ContextStudioIntegration] = None,
    rfp_id: Optional[str] = None
) -> Dict[str, Any]:
    """
    Process all tables found in document chunks.
    
    Parameters
    ----------
    chunks : List[DocumentChunk]
        Document chunks from ingestion
    context_studio : ContextStudioIntegration, optional
        Context Studio integration
    rfp_id : str, optional
        RFP identifier
        
    Returns
    -------
    Dict[str, Any]
        Summary of processed tables with metadata
    """
    processor = TableProcessor(context_studio)
    
    results = {
        'tables_found': 0,
        'tables_processed': 0,
        'tables_validated': 0,
        'tables_by_type': {},
        'details': []
    }
    
    for chunk in chunks:
        # Check if chunk contains table data
        if '[TABLE DATA]' not in chunk.text:
            continue
        
        results['tables_found'] += 1
        
        table_type, parsed_data, metadata = processor.process_table_chunk(chunk, rfp_id)
        
        if parsed_data:
            results['tables_processed'] += 1
            
            if metadata.get('validated'):
                results['tables_validated'] += 1
            
            # Track by type
            if table_type:
                type_key = table_type.value
                if type_key not in results['tables_by_type']:
                    results['tables_by_type'][type_key] = []
                
                results['tables_by_type'][type_key].append({
                    'section': chunk.section,
                    'page': chunk.page,
                    'row_count': len(parsed_data),
                    'summary': processor.get_table_summary(table_type, parsed_data)
                })
            
            results['details'].append({
                'section': chunk.section,
                'page': chunk.page,
                'table_type': table_type.value if table_type else 'unknown',
                'rows': len(parsed_data),
                'validated': metadata.get('validated', False),
                'enriched': metadata.get('enriched', False)
            })
    
    log.info("table_processing_complete", **results)
    return results

# Made with Bob
