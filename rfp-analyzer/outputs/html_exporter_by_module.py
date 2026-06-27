"""
outputs/html_exporter_by_module.py
----------------------------------
Exports RFP analysis results grouped by business module/feature.
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
    """Export requirements to an interactive HTML report grouped by business module."""
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
    
    # Build HTML content
    title_escaped = escape(rfp_title)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title_escaped} - By Module</title>
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
            margin-bottom: 30px;
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
        .requirement-card {{
            background: white;
            border: 1px solid #E2E8F0;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.3s ease;
            position: relative;
        }}
        .requirement-card:hover {{
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        .requirement-card:last-child {{ margin-bottom: 0; }}
        
        /* Colored left-border accent based on category */
        .requirement-card.cat-compliance {{ border-left: 4px solid #667eea; }}
        .requirement-card.cat-functional {{ border-left: 4px solid #10B981; }}
        .requirement-card.cat-non_functional {{ border-left: 4px solid #10B981; }}
        .requirement-card.cat-ambiguity {{ border-left: 4px solid #F59E0B; }}
        .requirement-card.cat-risk {{ border-left: 4px solid #EF4444; }}
        
        /* Priority-based accents */
        .requirement-card.pri-must {{ border-left: 4px solid #F59E0B; }}
        .requirement-card.pri-should {{ border-left: 4px solid #3B82F6; }}
        .requirement-card.pri-could {{ border-left: 4px solid #8B5CF6; }}
        .requirement-card.pri-wont {{ border-left: 4px solid #9CA3AF; }}
        
        .req-title {{ 
            font-size: 18px; 
            font-weight: 700; 
            color: #1F2937; 
            margin-bottom: 12px;
            line-height: 1.4;
        }}
        .req-id {{
            font-family: 'Courier New', monospace;
            background: #F3F4F6;
            color: #6B7280;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
            margin-bottom: 12px;
        }}
        .badges {{ display: flex; gap: 8px; flex-wrap: wrap; margin-bottom: 15px; }}
        .badge {{
            padding: 6px 12px;
            border-radius: 9999px;
            font-size: 12px;
            font-weight: 600;
            display: inline-block;
        }}
        /* Category badges */
        .badge-functional {{ background: #DCFCE7; color: #15803D; }}
        .badge-non_functional {{ background: #DBEAFE; color: #1E40AF; }}
        .badge-compliance {{ background: #EEF2FF; color: #4338CA; }}
        .badge-ambiguity {{ background: #FEF3C7; color: #B45309; }}
        .badge-risk {{ background: #FEE2E2; color: #DC2626; }}
        
        /* Priority badges */
        .badge-must {{ background: #FFF1F2; color: #BE123C; }}
        .badge-should {{ background: #FFFBEB; color: #B45309; }}
        .badge-could {{ background: #EFF6FF; color: #1E40AF; }}
        .badge-wont {{ background: #F3F4F6; color: #6B7280; }}
        .req-description {{ 
            color: #4B5563; 
            margin-bottom: 16px; 
            line-height: 1.7;
            font-size: 15px;
        }}
        .req-meta {{
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
            font-size: 13px;
            color: #6B7280;
            padding-top: 16px;
            border-top: 1px solid #E5E7EB;
            margin-top: 8px;
        }}
        .req-meta strong {{
            color: #374151;
            font-weight: 600;
        }}
    </style>
    <script>
        function toggleModule(moduleId) {{
            const content = document.getElementById(moduleId);
            const header = content.previousElementSibling;
            
            if (content.classList.contains('collapsed')) {{
                content.classList.remove('collapsed');
                header.classList.remove('collapsed');
            }} else {{
                content.classList.add('collapsed');
                header.classList.add('collapsed');
            }}
        }}
        
        function expandAll() {{
            document.querySelectorAll('.module-content').forEach(content => {{
                content.classList.remove('collapsed');
                content.previousElementSibling.classList.remove('collapsed');
            }});
        }}
        
        function collapseAll() {{
            document.querySelectorAll('.module-content').forEach(content => {{
                content.classList.add('collapsed');
                content.previousElementSibling.classList.add('collapsed');
            }});
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📦 {title_escaped}</h1>
            <p class="subtitle">Grouped by Business Module/Feature</p>
            <p style="font-size: 0.9em; margin-top: 10px;">Generated: {timestamp}</p>
        </div>
        
        <div class="controls">
            <button class="btn btn-expand" onclick="expandAll()">▼ Expand All Modules</button>
            <button class="btn btn-collapse" onclick="collapseAll()">▶ Collapse All Modules</button>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="number">{stats['total']}</div>
                <div class="label">Total Requirements</div>
            </div>
            <div class="stat-card">
                <div class="number">{stats['modules']}</div>
                <div class="label">Business Modules</div>
            </div>
            <div class="stat-card">
                <div class="number">{stats['must_have']}</div>
                <div class="label">Must Have</div>
            </div>
            <div class="stat-card">
                <div class="number">{stats['ambiguous']}</div>
                <div class="label">Need Clarification</div>
            </div>
        </div>
        
        <div class="requirements">
            <h2 style="margin-bottom: 30px; color: #333;">📋 Requirements by Business Module</h2>
"""
    
    # Add each module section with unique IDs
    module_index = 0
    for module_name in sorted(grouped_reqs.keys()):
        module_reqs = grouped_reqs[module_name]
        module_escaped = escape(module_name)
        module_id = f"module-{module_index}"
        
        html_content += f"""
            <div class="module-section">
                <div class="module-header" onclick="toggleModule('{module_id}')">
                    <h3>
                        <span class="toggle-icon">▼</span>
                        {module_escaped}
                    </h3>
                    <span class="module-count">{len(module_reqs)} Requirements</span>
                </div>
                <div class="module-content" id="{module_id}">
"""
        module_index += 1
        
        for req in module_reqs:
            cat_class = req.category.value
            pri_class = req.priority.value
            req_id_escaped = escape(req.id)
            req_title_escaped = escape(req.title)
            req_desc_escaped = escape(req.description)
            
            html_content += f"""
                    <div class="requirement-card cat-{cat_class} pri-{pri_class}">
                        <div class="req-id">{req_id_escaped}</div>
                        <div class="req-title">{req_title_escaped}</div>
                        <div class="badges">
                            <span class="badge badge-{cat_class}">{escape(req.category.value.upper())}</span>
                            <span class="badge badge-{pri_class}">{escape(req.priority.value.upper())}</span>
"""
            
            if req.ambiguity_flag:
                html_content += '                            <span class="badge badge-ambiguity">⚠️ NEEDS CLARIFICATION</span>\n'
            
            html_content += """                        </div>
                        <div class="req-description">""" + req_desc_escaped + """</div>
                        <div class="req-meta">
                            <span><strong>Source:</strong> """ + escape(req.source_section) + """</span>
                            <span><strong>Confidence:</strong> """ + f"{req.confidence:.0%}" + """</span>
"""
            
            # Add SAP modules if present
            if hasattr(req, 'sap_modules') and req.sap_modules:
                sap_modules = req.sap_modules
                html_content += '                            <span><strong>SAP Modules:</strong> '
                for sap_mod in sap_modules:
                    html_content += f'<span style="background: #0078D4; color: white; padding: 2px 8px; border-radius: 4px; margin-right: 4px; font-size: 0.9em;">{escape(sap_mod)}</span>'
                html_content += '</span>\n'
            
            html_content += """                        </div>
                    </div>
"""
        
        html_content += """                </div>
            </div>
"""
    
    html_content += """        </div>
    </div>
</body>
</html>"""
    
    # Write to file
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    log.info("html_by_module_exported", path=out_path, modules=len(grouped_reqs))
    return out_path