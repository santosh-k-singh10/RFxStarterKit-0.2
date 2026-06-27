"""
outputs/html_exporter.py
------------------------
Exports RFP analysis results to a rich, interactive HTML format.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from html import escape

import structlog

from core.schemas import Category, Priority, Requirement

log = structlog.get_logger()


def export_html(
    requirements: list[Requirement],
    out_path: str,
    rfp_title: str = "RFP Analysis",
) -> str:
    """Export requirements to an interactive HTML report."""
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Calculate statistics
    stats = {
        "total": len(requirements),
        "ambiguous": sum(1 for r in requirements if r.ambiguity_flag),
        "by_category": {},
        "by_priority": {},
    }
    
    for cat in Category:
        cat_reqs = [r for r in requirements if r.category == cat]
        stats["by_category"][cat.value] = len(cat_reqs)
    
    for priority in Priority:
        stats["by_priority"][priority.value] = sum(
            1 for r in requirements if r.priority == priority
        )
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{escape(rfp_title)}</title>
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
            border-radius: 20px 20px 0 0;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
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
            color: #667eea;
        }}
        .stat-card .label {{ color: #666; font-size: 0.9em; }}
        .requirements {{ padding: 40px; }}
        .category-section {{
            margin-bottom: 40px;
        }}
        .category-header {{
            background: #667eea;
            color: white;
            padding: 20px;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0;
        }}
        .category-header h3 {{
            font-size: 1.5em;
            margin: 0;
        }}
        .category-count {{
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .requirement-card {{
            background: white;
            border-left: 5px solid #667eea;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        .req-title {{ font-size: 1.3em; font-weight: 600; color: #2c3e50; margin-bottom: 10px; }}
        .req-id {{
            font-family: 'Courier New', monospace;
            background: #e8eaf6;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.9em;
            display: inline-block;
            margin-bottom: 10px;
        }}
        .badges {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 15px; }}
        .badge {{
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.85em;
            font-weight: 600;
        }}
        .badge-functional {{ background: #D6EAF8; color: #1976d2; }}
        .badge-non_functional {{ background: #D5F5E3; color: #27AE60; }}
        .badge-compliance {{ background: #FDEBD0; color: #F39C12; }}
        .badge-ambiguity {{ background: #FDEDEC; color: #E74C3C; }}
        .badge-risk {{ background: #F9EBEA; color: #E67E22; }}
        .badge-must {{ background: #ffebee; color: #c62828; }}
        .badge-should {{ background: #fff3e0; color: #e65100; }}
        .badge-could {{ background: #e3f2fd; color: #1976d2; }}
        .badge-wont {{ background: #f5f5f5; color: #757575; }}
        .req-description {{ color: #555; margin-bottom: 15px; line-height: 1.7; }}
        .req-meta {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 0.9em;
            color: #666;
            padding-top: 15px;
            border-top: 1px solid #eee;
        }}
        .clarification-box {{
            background: #fff8e1;
            border-left: 4px solid #ffa726;
            padding: 15px;
            margin-top: 15px;
            border-radius: 4px;
        }}
        .related-ids {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }}
        .related-id {{
            background: #e8eaf6;
            color: #3f51b5;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.85em;
            font-family: 'Courier New', monospace;
        }}
        @media print {{
            body {{ background: white; padding: 0; }}
            .container {{ box-shadow: none; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 {escape(rfp_title)}</h1>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="number">{stats['total']}</div>
                <div class="label">Total Requirements</div>
            </div>
            <div class="stat-card">
                <div class="number">{stats['by_priority'].get('must', 0)}</div>
                <div class="label">Must Have</div>
            </div>
            <div class="stat-card">
                <div class="number">{stats['ambiguous']}</div>
                <div class="label">Need Clarification</div>
            </div>
            <div class="stat-card">
                <div class="number">{stats['by_category'].get('functional', 0)}</div>
                <div class="label">Functional</div>
            </div>
        </div>
        
        <div class="requirements">
            <h2 style="margin-bottom: 30px; color: #333;">Requirements by Category</h2>
"""
    
    # Group requirements by category
    grouped_reqs = {}
    for req in requirements:
        cat = req.category.value
        if cat not in grouped_reqs:
            grouped_reqs[cat] = []
        grouped_reqs[cat].append(req)
    
    # Add each category section
    for category in Category:
        cat_value = category.value
        if cat_value not in grouped_reqs:
            continue
            
        cat_reqs = grouped_reqs[cat_value]
        cat_name = cat_value.replace('_', ' ').title()
        
        # Category colors
        cat_colors = {
            'functional': '#3498DB',
            'non_functional': '#27AE60',
            'compliance': '#F39C12',
            'ambiguity': '#E74C3C',
            'risk': '#E67E22',
        }
        cat_color = cat_colors.get(cat_value, '#667eea')
        
        html += f"""
            <div class="category-section">
                <div class="category-header" style="background: {cat_color};">
                    <h3>{cat_name}</h3>
                    <span class="category-count">{len(cat_reqs)} Requirements</span>
                </div>
"""
        
        for req in cat_reqs:
            cat_class = req.category.value
            pri_class = req.priority.value
            
            html += f"""
            <div class="requirement-card">
                <div class="req-id">{escape(req.id)}</div>
                <div class="req-title">{escape(req.title)}</div>
                <div class="badges">
                    <span class="badge badge-{cat_class}">{req.category.value.replace('_', ' ').title()}</span>
                    <span class="badge badge-{pri_class}">{req.priority.value.upper()}</span>
                    <span class="badge" style="background: #f3e5f5; color: #7b1fa2;">{req.confidence:.0%} Confidence</span>
"""
            
            if req.ambiguity_flag:
                html += '                    <span class="badge" style="background: #fff3e0; color: #e65100;">⚠ Ambiguous</span>\n'
            
            html += '                </div>\n'
            html += f'                <div class="req-description">{escape(req.description)}</div>\n'
            
            if req.clarification_question:
                html += f"""
                <div class="clarification-box">
                    <strong>⚠ Clarification Needed:</strong> {escape(req.clarification_question)}
                </div>
"""
            
            html += f"""
                <div class="req-meta">
                    <span><strong>Section:</strong> {escape(req.source_section)}</span>
                    <span><strong>Page:</strong> {req.page_ref or 'N/A'}</span>
"""
            
            # Add SAP modules if present
            if hasattr(req, 'sap_modules') and req.sap_modules:
                sap_modules = req.sap_modules
                html += '                    <span><strong>SAP Modules:</strong> '
                for sap_mod in sap_modules:
                    html += f'<span style="background: #0078D4; color: white; padding: 2px 8px; border-radius: 4px; margin-right: 4px; font-size: 0.9em;">{escape(sap_mod)}</span>'
                html += '</span>\n'
            
            if req.related_ids:
                html += '                    <span><strong>Related:</strong> '
                for rel_id in req.related_ids:
                    html += f'<span class="related-id">{escape(rel_id)}</span> '
                html += '</span>\n'
            
            html += '                </div>\n'
            html += '            </div>\n'
        
        html += '            </div>\n'  # Close category-section
    
    html += """
        </div>
    </div>
</body>
</html>"""
    
    # Write to file
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    
    log.info("html_exported", path=out_path, count=len(requirements))
    return str(Path(out_path).resolve())