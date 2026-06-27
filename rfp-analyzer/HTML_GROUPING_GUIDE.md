# HTML Output Grouping Guide

## Current Implementation
The HTML exporter currently groups requirements by **Category** (Functional, Non-Functional, Compliance, Ambiguity, Risk).

## Grouping by Module/Feature

To group requirements by business modules (e.g., "User Management", "Payment Processing", "Reporting"), you have several options:

### Option 1: Use Source Section as Module (EASIEST - Already Working!)

The `source_section` field already contains module/section information from the RFP document. You can use this to group requirements.

**To implement:** Replace the grouping logic in `html_exporter.py`:

```python
# Instead of grouping by category:
grouped_reqs = {}
for req in requirements:
    cat = req.category.value
    if cat not in grouped_reqs:
        grouped_reqs[cat] = []
    grouped_reqs[cat].append(req)

# Group by source_section (module):
grouped_reqs = {}
for req in requirements:
    module = req.source_section  # This is the document section/module
    if module not in grouped_reqs:
        grouped_reqs[cat] = []
    grouped_reqs[module].append(req)

# Then iterate through modules instead of categories
for module_name in sorted(grouped_reqs.keys()):
    module_reqs = grouped_reqs[module_name]
    # ... rest of the code
```

### Option 2: Add Module Field to Requirements Schema

1. **Update `core/schemas.py`:**
```python
class Requirement(BaseModel):
    id: str
    category: Category
    title: str
    description: str
    source_section: str
    page_ref: Optional[str] = None
    priority: Priority = Priority.SHOULD
    confidence: float = 0.0
    ambiguity_flag: bool = False
    clarification_question: str = ""
    related_ids: list[str] = Field(default_factory=list)
    module: Optional[str] = None  # ADD THIS
```

2. **Update extraction agents** to set the module field using AI or keyword matching

3. **Update HTML exporter** to group by module field

### Option 3: Infer Modules Using Keywords (Smart Grouping)

Create a helper function that automatically categorizes requirements into business modules:

```python
def infer_module(requirement: Requirement) -> str:
    """Infer business module from requirement content."""
    text = (requirement.title + " " + requirement.description).lower()
    
    # Define module keywords
    modules = {
        "👤 User Management": ["user", "authentication", "login", "signup", "profile", "account", "password", "credential"],
        "💳 Payment Processing": ["payment", "transaction", "billing", "invoice", "checkout", "purchase", "refund"],
        "📊 Reporting & Analytics": ["report", "dashboard", "analytics", "chart", "export", "statistics", "metrics"],
        "💾 Data Management": ["data", "database", "storage", "backup", "migration", "import", "export data"],
        "🔒 Security & Compliance": ["security", "encryption", "access control", "firewall", "audit", "gdpr", "compliance"],
        "🔗 Integration & APIs": ["api", "integration", "webhook", "third-party", "external", "connector"],
        "📱 Mobile": ["mobile", "ios", "android", "app", "smartphone"],
        "🌐 Web Interface": ["web", "browser", "frontend", "ui", "interface"],
        "⚙️ System Configuration": ["configuration", "settings", "setup", "admin", "system"],
    }
    
    for module, keywords in modules.items():
        if any(keyword in text for keyword in keywords):
            return module
    
    return "📋 General"  # Default module
```

### Example: Module-Based HTML Exporter

I've created a separate version for you: `outputs/html_exporter_by_module.py`

## Which Option Should You Use?

1. **Use Option 1** if your RFP documents already have clear sections (most common)
2. **Use Option 3** if you want automatic smart grouping based on content
3. **Use Option 2** if you need custom module assignment logic in your agents

## Testing

Run the test script to see the current category-based grouping:
```bash
cd rfp-analyzer
python test_html_export.py
```

The output will be in `outputs/test_html_report.html`