"""
outputs/html_exporter_by_module.py
----------------------------------
Exports RFP analysis results grouped by business module/feature with COLLAPSIBLE sections.
Uses intelligent keyword matching to categorize requirements.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from html import escape

import structlog

from core.schemas import Category, Priority, Requirement

log = structlog.get_logger()


def infer_module(requirement: Requirement) -> str:
    """Infer business module from requirement content using keyword matching."""
    text = (requirement.title + " " + requirement.description + " " + requirement.source_section).lower()
    
    # Define module keywords (with emojis for visual appeal)
    modules = {
        "👤 User Management": ["user", "authentication", "login", "signup", "profile", "account", "password", "credential", "registration"],
        "💳 Payment Processing": ["payment", "transaction", "billing", "invoice", "checkout", "purchase", "refund", "pricing"],
        "📊 Reporting & Analytics": ["report", "dashboard", "analytics", "chart", "export", "statistics", "metrics", "visualization"],
        "💾 Data Management": ["data", "database", "storage", "backup", "migration", "import", "export data", "archival"],
        "🔒 Security & Compliance": ["security", "encryption", "access control", "firewall", "audit", "gdpr", "compliance", "privacy"],
        "🔗 Integration & APIs": ["api", "integration", "webhook", "third-party", "external", "connector", "interface"],
        "📱 Mobile Application": ["mobile", "ios", "android", "app", "smartphone", "tablet"],
        "🌐 Web Interface": ["web", "browser", "frontend", "ui", "interface", "website"],
        "⚙️ System Configuration": ["configuration", "settings", "setup", "admin", "system", "parameter"],
        "📧 Notifications": ["notification", "email", "sms", "alert", "message", "communication"],
        "🔍 Search & Discovery": ["search", "filter", "query", "find", "discovery", "lookup"],
        "📝 Content Management": ["content", "document", "file", "upload", "download", "cms"],
    }
    
    for module, keywords in modules.items():
        if any(keyword in text for keyword in keywords):
            return module
    
    # Fallback to source section if no module matched
    return f"📋 {requirement.source_section}"


def export_html_by_module(
    requirements: list[Requirement],
    out_path: str,
    rfp_title: str = "RFP Analysis",
) -> str:
    """Export requirements to an interactive HTML report grouped by business module with COLLAPSIBLE sections."""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Group requirements by module
    grouped_reqs = {}
    for req in requirements:
        module = infer_module(req)
        if module not in grouped_reqs:
            grouped_reqs[module] = []
        grouped_reqs[module].append(req)
    
    # Calculate statistics
    stats = {
        "total": len(requirements),
        "ambiguous": sum(1 for r in requirements if r.ambiguity_flag),
        "modules": len(grouped_reqs),
        "must_have": sum(1 for r in requirements if r.priority == Priority.MUST),
    }
    
    # Generate HTML with collapsible sections
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(rfp_title)} - By Module</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            line-height: 1.6;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        .header {{
            background: linear-gradient(135deg, #27AE60 0%, #229954 100%);
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 20px 20px 0 0;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header .subtitle {{ font-size: 1.1em; opacity: 0.9; margin-top: 10px; }}
        .controls {{
            padding: 20px 40px;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
            display: flex;
            gap: 10px;
            justify-content: center;
            flex-wrap: wrap;
        }}
        .btn {{
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 0.9em;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        .btn-expand {{ background: #27AE60; color: white; }}
        .btn-collapse {{ background: #95a5a6; color: white; }}
        .btn:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 40px;
            background: #f8f9fa;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        .stat-card .number {{
            font-size: 2.5em;
            font-weight: bold;
            color: #27AE60;
        }}
        .stat-card .label {{ color: #666; font-size: 0.9em; }}
        .requirements {{ padding: 40px; }}
        .module-section {{
            margin-bottom: 20px;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .module-header {{
            background: linear-gradient(135deg, #27AE60 0%, #229954 100%);
            color: white;
            padding: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
            user-select: none;
            transition: all 0.3s ease;
        }}
        .module-header:hover {{
            background: linear-gradient(135deg, #229954 0%, #1e8449 100%);
            transform: translateX(5px);
        }}
        .module-header h3 {{
            font-size: 1.5em;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .toggle-icon {{
            font-size: 1.2em;
            transition: transform 0.3s ease;
            display: inline-block;
        }}
        .module-header.collapsed .toggle-icon {{
            transform: rotate(-90deg);
        }}
        .module-count {{
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .module-content {{
            background: white;
            max-height: 10000px;
            overflow: hidden;
            transition: max-height 0.5s ease-in-out, padding 0.5s ease;
            padding: 20px;
        }}
        .module-content.collapsed {{
            max-height: 0;
            padding: 0 20px;
        }}
        .requirement-card {{
            background: #f8f9fa;
            border-left: 5px solid #27AE60;
            padding: 20px;
            margin-bottom: 15px;
            border-radius: 8px;
            transition: all 0.3s ease;
        }}
        .requirement-card:hover {{
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .requirement-card:last-child {{ margin-bottom: 0; }}
        .req-title {{ font-size: 1.3em; font-weight: 600; color: #2c3e50; margin-bottom: 10px; }}
        .req-id {{
            font-family: 'Courier New', monospace;
            background: #e8