"""
app/services/export_service.py
-------------------------------
Service layer wrapping the export functions.
"""

from typing import List
from pathlib import Path
import structlog

from core.schemas import Requirement
from outputs.exporter import export_excel, export_markdown, export_json
from outputs.html_exporter import export_html

log = structlog.get_logger(__name__)


async def export_to_excel(requirements: List[Requirement], output_path: str) -> str:
    """
    Export requirements to Excel format.
    
    Args:
        requirements: List of requirements
        output_path: Output file path
    
    Returns:
        Absolute path to exported file
    """
    log.info("excel_export_start", count=len(requirements))
    try:
        path = export_excel(requirements, output_path)
        log.info("excel_export_complete", path=path)
        return path
    except Exception as e:
        log.error("excel_export_error", error=str(e))
        raise


async def export_to_markdown(requirements: List[Requirement], output_path: str, title: str = "RFP Analysis") -> str:
    """
    Export requirements to Markdown format.
    
    Args:
        requirements: List of requirements
        output_path: Output file path
        title: Report title
    
    Returns:
        Absolute path to exported file
    """
    log.info("markdown_export_start", count=len(requirements))
    try:
        path = export_markdown(requirements, output_path, rfp_title=title)
        log.info("markdown_export_complete", path=path)
        return path
    except Exception as e:
        log.error("markdown_export_error", error=str(e))
        raise


async def export_to_json(requirements: List[Requirement], output_path: str, title: str = "RFP Analysis") -> str:
    """
    Export requirements to JSON format.
    
    Args:
        requirements: List of requirements
        output_path: Output file path
        title: Report title
    
    Returns:
        Absolute path to exported file
    """
    log.info("json_export_start", count=len(requirements))
    try:
        path = export_json(requirements, output_path, rfp_title=title)
        log.info("json_export_complete", path=path)
        return path
    except Exception as e:
        log.error("json_export_error", error=str(e))
        raise


async def generate_html_preview(requirements: List[Requirement], title: str = "RFP Analysis") -> str:
    """
    Generate HTML content for inline preview (returns HTML string, not a file).
    
    Args:
        requirements: List of requirements
        title: Report title
    
    Returns:
        HTML content as string
    """
    log.info("html_preview_start", count=len(requirements))
    try:
        # Generate HTML to a temporary location to get the content
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as tmp:
            tmp_path = tmp.name
        
        # Generate the HTML file
        export_html(requirements, tmp_path, rfp_title=title)
        
        # Read the content
        with open(tmp_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Clean up temp file
        Path(tmp_path).unlink()
        
        log.info("html_preview_complete", length=len(html_content))
        return html_content
    except Exception as e:
        log.error("html_preview_error", error=str(e))
        raise