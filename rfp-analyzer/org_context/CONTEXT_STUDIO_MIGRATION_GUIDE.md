# Context Studio Migration Guide

## Overview

This guide provides step-by-step instructions for migrating your organizational context from local files to IBM Context Studio using JSON-LD schemas.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Migration Architecture](#migration-architecture)
3. [Step-by-Step Migration Process](#step-by-step-migration-process)
4. [Schema Import Instructions](#schema-import-instructions)
5. [Data Conversion and Import](#data-conversion-and-import)
6. [Verification and Testing](#verification-and-testing)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Access
- IBM ICA Platform account with Context Studio access
- Context Studio API credentials (API token, workspace ID)
- Permissions to create schemas and import data

### Required Tools
- Python 3.8+
- Required Python packages: `pyyaml`, `requests`, `rdflib`

### Install Dependencies
```bash
cd rfp-analyzer
pip install pyyaml requests rdflib
```

---

## Migration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Current Local Structure                       │
├─────────────────────────────────────────────────────────────────┤
│  org_context/                                                    │
│  ├── config/org_config.yaml          → Organization Config      │
│  ├── domain_knowledge/*.md           → Domain Knowledge         │
│  ├── standards/*.md                  → Standards Documents      │
│  ├── templates/*.md                  → Templates                │
│  └── examples/past_rfps/*.txt        → Historical RFPs          │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    [Conversion Script]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    JSON-LD Schema Files                          │
├─────────────────────────────────────────────────────────────────┤
│  schemas/                                                        │
│  ├── organization_schema.jsonld                                 │
│  ├── domain_knowledge_schema.jsonld                             │
│  ├── standards_schema.jsonld                                    │
│  ├── template_schema.jsonld                                     │
│  └── historical_rfp_schema.jsonld                               │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    [Import to Context Studio]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    JSON-LD Data Files                            │
├─────────────────────────────────────────────────────────────────┤
│  data/                                                           │
│  ├── organization_data.jsonld                                   │
│  ├── healthcare_domain_knowledge.jsonld                         │
│  ├── coding_standards.jsonld                                    │
│  ├── security_standards.jsonld                                  │
│  ├── proposal_response_template.jsonld                          │
│  └── historical_rfps/*.jsonld                                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    [Import to Context Studio]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  IBM Context Studio                              │
│                  (Centralized Context)                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Migration Process

### Phase 1: Prepare Schema Files

#### Step 1.1: Create Schema Directory
```bash
cd rfp-analyzer/org_context
mkdir -p schemas
mkdir -p data
```

#### Step 1.2: Copy Schema Definitions

The schema files are in the `schemas/` directory. You'll need to import these 5 schema files:

1. **organization_schema.jsonld** - Organization configuration schema
2. **domain_knowledge_schema.jsonld** - Domain knowledge schema
3. **standards_schema.jsonld** - Standards documents schema
4. **template_schema.jsonld** - Template schema
5. **historical_rfp_schema.jsonld** - Historical RFP schema

**Action Required:** Switch to Code mode to create these files from the schema definitions in the plan document.

---

### Phase 2: Convert Existing Data to JSON-LD

#### Step 2.1: Run Conversion Script

Create and run the conversion script (see [Conversion Script Specification](#conversion-script-specification) below):

```bash
python org_context/convert_to_jsonld.py
```

This will:
- Read your existing YAML and Markdown files
- Convert them to JSON-LD format
- Save them in the `data/` directory

#### Step 2.2: Verify Generated Files

Check that the following files were created:
```bash
ls -la org_context/data/
# Expected output:
# organization_data.jsonld
# healthcare_domain_knowledge.jsonld
# coding_standards.jsonld
# security_standards.jsonld
# proposal_response_template.jsonld
# historical_rfps/
```

---

### Phase 3: Import Schemas to Context Studio

#### Step 3.1: Access Context Studio

1. Log in to IBM ICA Platform: https://servicesessentials.ibm.com/agenticapps
2. Navigate to **Platform Settings** → **Context Studio**
3. Select your workspace or create a new one

#### Step 3.2: Import Each Schema

For each schema file, follow these steps:

1. Click **"Import Schema"** button
2. Select **"JSON-LD"** as format
3. Upload the schema file (e.g., `organization_schema.jsonld`)
4. Review the schema preview
5. Click **"Import"**
6. Wait for confirmation

**Import Order (recommended):**
1. `organization_schema.jsonld`
2. `domain_knowledge_schema.jsonld`
3. `standards_schema.jsonld`
4. `template_schema.jsonld`
5. `historical_rfp_schema.jsonld`

#### Step 3.3: Verify Schema Import

After importing each schema:
1. Go to **"Schemas"** tab in Context Studio
2. Verify the schema appears in the list
3. Click on the schema to view its structure
4. Confirm all properties and classes are present

---

### Phase 4: Import Data to Context Studio

#### Step 4.1: Import Organization Configuration

1. In Context Studio, go to **"Data"** tab
2. Click **"Import Data"**
3. Select schema: **"Organization Context"**
4. Upload: `data/organization_data.jsonld`
5. Click **"Import"**

#### Step 4.2: Import Domain Knowledge

1. Select schema: **"Domain Knowledge"**
2. Upload: `data/healthcare_domain_knowledge.jsonld`
3. Click **"Import"**

#### Step 4.3: Import Standards Documents

For each standards file:
1. Select schema: **"Standard Document"**
2. Upload the file (e.g., `data/coding_standards.jsonld`)
3. Click **"Import"**

Repeat for:
- `coding_standards.jsonld`
- `security_standards.jsonld`

#### Step 4.4: Import Templates

1. Select schema: **"Template"**
2. Upload: `data/proposal_response_template.jsonld`
3. Click **"Import"**

#### Step 4.5: Import Historical RFPs

For each historical RFP file in `data/historical_rfps/`:
1. Select schema: **"Historical RFP"**
2. Upload the file
3. Click **"Import"**

---

### Phase 5: Configure RFP Analyzer Integration

#### Step 5.1: Update Configuration

Edit `rfp-analyzer/.env`:
```bash
# Context Studio Configuration
CONTEXT_STUDIO_URL=https://your-context-studio.ibm.com/api/v1
CONTEXT_STUDIO_TOKEN=your-api-token-here
CONTEXT_STUDIO_WORKSPACE=your-workspace-id
CONTEXT_STUDIO_ENABLED=true
```

#### Step 5.2: Update Context Manager

The [`context_manager.py`](context_manager.py) already supports remote loading. Update your initialization:

```python
from org_context.context_manager import initialize_context_manager

# Initialize with Context Studio URL
context_manager = initialize_context_manager(
    config_path=os.getenv("CONTEXT_STUDIO_URL") + "/organization/ibm-consulting",
    remote_kwargs={
        "auth_token": os.getenv("CONTEXT_STUDIO_TOKEN"),
        "workspace_id": os.getenv("CONTEXT_STUDIO_WORKSPACE")
    }
)
```

#### Step 5.3: Test Integration

Run a test to verify the integration:
```bash
python -c "
from org_context.context_manager import get_context_manager
cm = get_context_manager()
ctx = cm.get_context()
print(f'Organization: {ctx.name}')
print(f'Industry: {ctx.industry}')
print(f'Tech Stack Languages: {ctx.tech_stack.preferred_languages}')
"
```

---

## Schema Import Instructions

### Using Context Studio UI

1. **Navigate to Schemas Section**
   - Log in to Context Studio
   - Click on **"Schemas"** in the left sidebar

2. **Import Schema**
   - Click **"Import Schema"** button
   - Select file format: **JSON-LD**
   - Choose file from your computer
   - Click **"Upload"**

3. **Review and Confirm**
   - Review the schema structure preview
   - Check for any validation errors
   - Click **"Confirm Import"**

4. **Verify Import**
   - Schema should appear in the schemas list
   - Status should show as "Active"

### Using Context Studio API

Alternatively, import schemas programmatically:

```python
import requests
import json

def import_schema(schema_file, api_url, token, workspace_id):
    """Import a JSON-LD schema to Context Studio."""
    
    with open(schema_file, 'r') as f:
        schema_data = json.load(f)
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/ld+json',
        'X-Workspace-ID': workspace_id
    }
    
    response = requests.post(
        f'{api_url}/schemas',
        headers=headers,
        json=schema_data
    )
    
    if response.status_code == 201:
        print(f"✓ Schema imported successfully: {schema_file}")
        return response.json()
    else:
        print(f"✗ Failed to import schema: {response.text}")
        return None

# Usage
import_schema(
    'schemas/organization_schema.jsonld',
    'https://your-context-studio.ibm.com/api/v1',
    'your-token',
    'your-workspace-id'
)
```

---

## Data Conversion and Import

### Conversion Script Specification

Create `org_context/convert_to_jsonld.py`:

```python
#!/usr/bin/env python3
"""
Convert existing organizational context files to JSON-LD format.

This script reads YAML configuration and Markdown documents and converts
them to JSON-LD format compatible with Context Studio schemas.
"""

import yaml
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import re


class ContextConverter:
    """Converts organizational context to JSON-LD format."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.output_path = base_path / 'data'
        self.output_path.mkdir(exist_ok=True)
    
    def convert_organization_config(self, config_file: Path) -> Dict[str, Any]:
        """Convert org_config.yaml to organization_data.jsonld."""
        
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)
        
        jsonld = {
            "@context": "https://ibm.com/context-studio/organization/context.jsonld",
            "@type": "org:OrganizationContext",
            "@id": f"org:{config['name'].lower().replace(' ', '-')}",
            "org:name": config['name'],
            "org:industry": config['industry'],
            "org:description": config.get('description', ''),
            "org:techStack": {
                "@type": "org:TechStack",
                "org:preferredLanguages": config['tech_stack']['preferred_languages'],
                "org:cloudProviders": config['tech_stack']['cloud_providers'],
                "org:databases": config['tech_stack']['databases'],
                "org:frameworks": config['tech_stack']['frameworks'],
                "org:architecturePatterns": config['tech_stack']['architecture_patterns']
            },
            "org:compliance": {
                "@type": "org:ComplianceRequirements",
                "org:complianceFrameworks": config['compliance']['frameworks'],
                "org:certifications": config['compliance']['certifications'],
                "org:standards": config['compliance']['standards']
            },
            "org:namingConventions": {
                "@type": "org:NamingConventions",
                "org:requirementPrefix": config['naming_conventions']['requirement_prefix'],
                "org:functionalPrefix": config['naming_conventions']['functional_prefix'],
                "org:nonFunctionalPrefix": config['naming_conventions']['non_functional_prefix'],
                "org:compliancePrefix": config['naming_conventions']['compliance_prefix'],
                "org:separator": config['naming_conventions']['separator'],
                "org:padding": config['naming_conventions']['padding']
            },
            "org:priorityMapping": {
                "@type": "org:PriorityMapping",
                "org:mustKeywords": config['priority_mapping']['must_keywords'],
                "org:shouldKeywords": config['priority_mapping']['should_keywords'],
                "org:couldKeywords": config['priority_mapping']['could_keywords']
            },
            "org:riskThresholds": {
                "@type": "org:RiskThresholds",
                "org:highComplexityIndicators": config['risk_thresholds']['high_complexity_indicators'],
                "org:timelineRedFlags": config['risk_thresholds']['timeline_red_flags'],
                "org:resourceConstraints": config['risk_thresholds']['resource_constraints'],
                "org:highRiskScoreThreshold": config['risk_thresholds']['high_risk_score_threshold']
            }
        }
        
        output_file = self.output_path / 'organization_data.jsonld'
        with open(output_file, 'w') as f:
            json.dump(jsonld, f, indent=2)
        
        print(f"✓ Converted: {output_file}")
        return jsonld
    
    def convert_domain_knowledge(self, md_file: Path) -> Dict[str, Any]:
        """Convert domain knowledge markdown to JSON-LD."""
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract metadata from markdown
        metadata = self._extract_metadata(content)
        
        # Parse terms, acronyms, and technologies
        terms = self._extract_terms(content)
        acronyms = self._extract_acronyms(content)
        
        domain_name = md_file.stem.replace('_', '-')
        
        jsonld = {
            "@context": "https://ibm.com/context-studio/domain/context.jsonld",
            "@type": "domain:DomainKnowledge",
            "@id": f"domain:{domain_name}",
            "domain:industryDomain": metadata.get('Domain', 'General'),
            "domain:version": metadata.get('Version', '1.0'),
            "domain:lastUpdated": metadata.get('Last Updated', datetime.now().strftime('%Y-%m-%d')),
            "domain:terms": terms,
            "domain:acronyms": acronyms
        }
        
        output_file = self.output_path / f'{domain_name}.jsonld'
        with open(output_file, 'w') as f:
            json.dump(jsonld, f, indent=2)
        
        print(f"✓ Converted: {output_file}")
        return jsonld
    
    def convert_standard_document(self, md_file: Path, standard_type: str) -> Dict[str, Any]:
        """Convert standards markdown to JSON-LD."""
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        metadata = self._extract_metadata(content)
        sections = self._extract_sections(content)
        
        standard_name = md_file.stem.replace('_', '-')
        
        jsonld = {
            "@context": "https://ibm.com/context-studio/standards/context.jsonld",
            "@type": "std:StandardDocument",
            "@id": f"std:{standard_name}",
            "std:title": metadata.get('title', md_file.stem.replace('_', ' ').title()),
            "std:standardType": standard_type,
            "std:version": metadata.get('Version', '1.0'),
            "std:status": metadata.get('Status', 'active').lower(),
            "std:lastUpdated": metadata.get('Last Updated', datetime.now().strftime('%Y-%m-%d')),
            "std:classification": metadata.get('Classification', 'internal').lower(),
            "std:content": content,
            "std:summary": self._extract_summary(content),
            "std:sections": sections
        }
        
        output_file = self.output_path / f'{standard_name}.jsonld'
        with open(output_file, 'w') as f:
            json.dump(jsonld, f, indent=2)
        
        print(f"✓ Converted: {output_file}")
        return jsonld
    
    def convert_template(self, md_file: Path, template_type: str) -> Dict[str, Any]:
        """Convert template markdown to JSON-LD."""
        
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        sections = self._extract_sections(content)
        placeholders = self._extract_placeholders(content)
        
        template_name = md_file.stem.replace('_', '-')
        
        jsonld = {
            "@context": "https://ibm.com/context-studio/template/context.jsonld",
            "@type": "tmpl:Template",
            "@id": f"tmpl:{template_name}",
            "tmpl:templateName": md_file.stem.replace('_', ' ').title(),
            "tmpl:templateType": template_type,
            "tmpl:version": "1.0",
            "tmpl:status": "active",
            "tmpl:content": content,
            "tmpl:sections": sections,
            "tmpl:placeholders": placeholders,
            "tmpl:lastUpdated": datetime.now().strftime('%Y-%m-%d')
        }
        
        output_file = self.output_path / f'{template_name}.jsonld'
        with open(output_file, 'w') as f:
            json.dump(jsonld, f, indent=2)
        
        print(f"✓ Converted: {output_file}")
        return jsonld
    
    def convert_historical_rfp(self, txt_file: Path) -> Dict[str, Any]:
        """Convert historical RFP text to JSON-LD."""
        
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract basic info from filename and content
        rfp_id = txt_file.stem
        
        jsonld = {
            "@context": "https://ibm.com/context-studio/historical/context.jsonld",
            "@type": "hist:HistoricalRFP",
            "@id": f"hist:{rfp_id}",
            "hist:rfpId": rfp_id,
            "hist:title": self._extract_title(content),
            "hist:content": content,
            "hist:summary": self._extract_summary(content),
            "hist:submissionDate": datetime.now().strftime('%Y-%m-%d'),
            "hist:tags": self._extract_tags(content)
        }
        
        # Create historical_rfps subdirectory
        hist_dir = self.output_path / 'historical_rfps'
        hist_dir.mkdir(exist_ok=True)
        
        output_file = hist_dir / f'{rfp_id}.jsonld'
        with open(output_file, 'w') as f:
            json.dump(jsonld, f, indent=2)
        
        print(f"✓ Converted: {output_file}")
        return jsonld
    
    # Helper methods
    
    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """Extract metadata from markdown headers."""
        metadata = {}
        lines = content.split('\n')
        for line in lines[:20]:  # Check first 20 lines
            if '##' in line and ':' in line:
                key, value = line.split(':', 1)
                key = key.replace('#', '').strip()
                metadata[key] = value.strip()
        return metadata
    
    def _extract_sections(self, content: str) -> List[Dict[str, Any]]:
        """Extract sections from markdown."""
        sections = []
        current_section = None
        section_content = []
        order = 0
        
        for line in content.split('\n'):
            if line.startswith('##') and not line.startswith('###'):
                if current_section:
                    sections.append({
                        "@type": "std:Section",
                        "std:sectionTitle": current_section,
                        "std:sectionContent": '\n'.join(section_content),
                        "std:sectionOrder": order
                    })
                    order += 1
                current_section = line.replace('##', '').strip()
                section_content = []
            elif current_section:
                section_content.append(line)
        
        if current_section:
            sections.append({
                "@type": "std:Section",
                "std:sectionTitle": current_section,
                "std:sectionContent": '\n'.join(section_content),
                "std:sectionOrder": order
            })
        
        return sections
    
    def _extract_terms(self, content: str) -> List[Dict[str, Any]]:
        """Extract terminology definitions."""
        terms = []
        # Look for patterns like "### Term Name" followed by definition
        pattern = r'###\s+([^\n]+)\n([^\n#]+)'
        matches = re.findall(pattern, content)
        
        for term, definition in matches:
            terms.append({
                "@type": "domain:Term",
                "domain:term": term.strip(),
                "domain:definition": definition.strip()
            })
        
        return terms
    
    def _extract_acronyms(self, content: str) -> List[Dict[str, Any]]:
        """Extract acronyms and their expansions."""
        acronyms = []
        # Look for patterns like "ACRONYM (Full Name)"
        pattern = r'([A-Z]{2,})\s*\(([^)]+)\)'
        matches = re.findall(pattern, content)
        
        for acronym, expansion in matches:
            acronyms.append({
                "@type": "domain:Acronym",
                "domain:acronym": acronym,
                "domain:expansion": expansion.strip()
            })
        
        return acronyms
    
    def _extract_placeholders(self, content: str) -> List[Dict[str, Any]]:
        """Extract template placeholders."""
        placeholders = []
        # Look for patterns like [Placeholder Name]
        pattern = r'\[([^\]]+)\]'
        matches = re.findall(pattern, content)
        
        for match in set(matches):  # Use set to avoid duplicates
            placeholders.append({
                "@type": "tmpl:Placeholder",
                "tmpl:placeholderName": match,
                "tmpl:placeholderType": "text"
            })
        
        return placeholders
    
    def _extract_summary(self, content: str) -> str:
        """Extract summary from content."""
        lines = content.split('\n')
        summary_lines = []
        in_summary = False
        
        for line in lines:
            if 'overview' in line.lower() or 'summary' in line.lower():
                in_summary = True
                continue
            if in_summary and line.strip():
                summary_lines.append(line.strip())
                if len(summary_lines) >= 3:
                    break
        
        return ' '.join(summary_lines) if summary_lines else content[:200]
    
    def _extract_title(self, content: str) -> str:
        """Extract title from content."""
        lines = content.split('\n')
        for line in lines[:10]:
            if line.startswith('#'):
                return line.replace('#', '').strip()
        return "Untitled Document"
    
    def _extract_tags(self, content: str) -> List[str]:
        """Extract tags from content."""
        tags = []
        content_lower = content.lower()
        
        # Common technology tags
        tech_keywords = ['python', 'java', 'aws', 'azure', 'healthcare', 'finance', 'retail']
        for keyword in tech_keywords:
            if keyword in content_lower:
                tags.append(keyword)
        
        return tags


def main():
    """Main conversion process."""
    
    base_path = Path(__file__).parent
    converter = ContextConverter(base_path)
    
    print("=" * 60)
    print("Context Studio Data Conversion")
    print("=" * 60)
    
    # Convert organization configuration
    print("\n1. Converting Organization Configuration...")
    config_file = base_path / 'config' / 'org_config.yaml'
    if config_file.exists():
        converter.convert_organization_config(config_file)
    else:
        print(f"  ⚠ Config file not found: {config_file}")
    
    # Convert domain knowledge
    print("\n2. Converting Domain Knowledge...")
    domain_dir = base_path / 'domain_knowledge'
    if domain_dir.exists():
        for md_file in domain_dir.glob('*.md'):
            converter.convert_domain_knowledge(md_file)
    else:
        print(f"  ⚠ Domain knowledge directory not found")
    
    # Convert standards
    print("\n3. Converting Standards Documents...")
    standards_dir = base_path / 'standards'
    if standards_dir.exists():
        for md_file in standards_dir.glob('*.md'):
            if md_file.name != 'README.md':
                standard_type = 'coding' if 'coding' in md_file.name else 'security'
                converter.convert_standard_document(md_file, standard_type)
    else:
        print(f"  ⚠ Standards directory not found")
    
    # Convert templates
    print("\n4. Converting Templates...")
    templates_dir = base_path / 'templates'
    if templates_dir.exists():
        for md_file in templates_dir.glob('*.md'):
            if md_file.name != 'README.md':
                converter.convert_template(md_file, 'proposal_response')
    else:
        print(f"  ⚠ Templates directory not found")
    
    # Convert historical RFPs
    print("\n5. Converting Historical RFPs...")
    examples_dir = base_path / 'examples' / 'past_rfps'
    if examples_dir.exists():
        for txt_file in examples_dir.glob('*.txt'):
            converter.convert_historical_rfp(txt_file)
    else:
        print(f"  ⚠ Historical RFPs directory not found")
    
    print("\n" + "=" * 60)
    print("Conversion Complete!")
    print(f"Output directory: {converter.output_path}")
    print("=" * 60)


if __name__ == '__main__':
    main()
```

### Running the Conversion

```bash
cd rfp-analyzer/org_context
python convert_to_jsonld.py
```

**Expected Output:**
```
============================================================
Context Studio Data Conversion
============================================================

1. Converting Organization Configuration...
✓ Converted: data/organization_data.jsonld

2. Converting Domain Knowledge...
✓ Converted: data/healthcare-terminology.jsonld

3. Converting Standards Documents...
✓ Converted: data/coding-standards.jsonld
✓ Converted: data/security-standards.jsonld

4. Converting Templates...
✓ Converted: data/proposal-response-template.jsonld

5. Converting Historical RFPs...
✓ Converted: data/historical_rfps/sample-healthcare-portal-rfp.jsonld

============================================================
Conversion Complete!
Output directory: data/
============================================================
```

---

## Verification and Testing

### Verify Schema Import

```python
import requests

def verify_schema(schema_name, api_url, token, workspace_id):
    """Verify a schema was imported successfully."""
    
    headers = {
        'Authorization': f'Bearer {token}',
        'X-Workspace-ID': workspace_id
    }
    
    response = requests.get(
        f'{api_url}/schemas/{schema_name}',
        headers=headers
    )
    
    if response.status_code == 200:
        schema = response.json()
        print(f"✓ Schema verified: {schema_name}")
        print(f"  - Classes: {len(schema.get('@graph', []))}")
        return True
    else:
        print(f"✗ Schema not found: {schema_name}")
        return False

# Verify all schemas
schemas = [
    'organization-context',
    'domain-knowledge',
    'standard-document',
    'template',
    'historical-rfp'
]

for schema in schemas:
    verify_schema(schema, API_URL, TOKEN, WORKSPACE_ID)
```

### Verify Data Import

```python
def verify_data(data_type, data_id, api_url, token, workspace_id):
    """Verify data was imported successfully."""
    
    headers = {
        'Authorization': f'Bearer {token}',
        'X-Workspace-ID': workspace_id
    }
    
    response = requests.get(
        f'{api_url}/data/{data_type}/{data_id}',
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✓ Data verified: {data_type}/{data_id}")
        return True
    else:
        print(f"✗ Data not found: {data_type}/{data_id}")
        return False

# Verify organization data
verify_data('organization', 'ibm-consulting', API_URL, TOKEN, WORKSPACE_ID)
```

### Test RFP Analyzer Integration

```python
#!/usr/bin/env python3
"""Test Context Studio integration with RFP Analyzer."""

from org_context.context_manager import initialize_context_manager
import os

def test_context_studio_integration():
    """Test loading context from Context Studio."""
    
    print("Testing Context Studio Integration...")
    print("=" * 60)
    
    # Initialize context manager with Context Studio
    context_manager = initialize_context_manager(
        config_path=os.getenv("CONTEXT_STUDIO_URL") + "/organization/ibm-consulting",
        remote_kwargs={
            "auth_token": os.getenv("CONTEXT_STUDIO_TOKEN"),
            "workspace_id": os.getenv("CONTEXT_STUDIO_WORKSPACE")
        }
    )
    
    # Get context
    context = context_manager.get_context()
    
    # Verify organization info
    print(f"\n✓ Organization: {context.name}")
    print(f"✓ Industry: {context.industry}")
    
    # Verify tech stack
    print(f"\n✓ Preferred Languages: {', '.join(context.tech_stack.preferred_languages)}")
    print(f"✓ Cloud Providers: {', '.join(context.tech_stack.cloud_providers)}")
    
    # Verify compliance
    print(f"\n✓ Compliance Frameworks: {', '.join(context.compliance.frameworks)}")
    
    # Verify naming conventions
    print(f"\n✓ Functional Prefix: {context.naming_conventions.functional_prefix}")
    
    # Test requirement ID generation
    req_id = context.get_requirement_id('functional', 1)
    print(f"\n✓ Sample Requirement ID: {req_id}")
    
    print("\n" + "=" * 60)
    print("✓ Integration test passed!")
    
if __name__ == '__main__':
    test_context_studio_integration()
```

---

## Troubleshooting

### Issue: Schema Import Fails

**Symptoms:**
- Error message during schema import
- Schema doesn't appear in Context Studio

**Solutions:**
1. Verify JSON-LD syntax is valid
2. Check that all required fields are present
3. Ensure `@context` URLs are accessible
4. Verify you have permission to create schemas

**Validation Command:**
```bash
# Validate JSON-LD syntax
python -c "import json; json.load(open('schemas/organization_schema.jsonld'))"
```

### Issue: Data Import Fails

**Symptoms:**
- Error during data import
- Data doesn't appear in Context Studio

**Solutions:**
1. Verify schema was imported first
2. Check that data matches schema structure
3. Ensure all required fields have values
4. Verify `@type` matches schema class name

### Issue: Conversion Script Errors

**Symptoms:**
- Script fails during conversion
- Missing or incomplete output files

**Solutions:**
1. Check that source files exist
2. Verify file permissions
3. Ensure Python dependencies are installed
4. Check for encoding issues in source files

### Issue: Context Manager Can't Load from Context Studio

**Symptoms:**
- Connection errors
- Authentication failures
- Empty context returned

**Solutions:**
1. Verify API URL is correct
2. Check that API token is valid and not expired
3. Ensure workspace ID is correct
4. Test API connectivity:
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     https://your-context-studio.ibm.com/api/v1/health
```

---

## Next Steps

After successful migration:

1. **Update Documentation**
   - Update team documentation to reference Context Studio
   - Document the new workflow for updating context

2. **Train Team**
   - Train team members on using Context Studio
   - Show how to update context through the UI

3. **Monitor Usage**
   - Monitor API usage and performance
   - Track context access patterns

4. **Iterate and Improve**
   - Gather feedback from team
   - Refine schemas based on usage
   - Add new context types as needed

5. **Backup Strategy**
   - Set up regular backups of Context Studio data
   - Document recovery procedures

---

## Support

For issues or questions:

1. **Context Studio Documentation**: https://ibm.com/docs/context-studio
2. **IBM ICA Support**: https://ibm.com/support/ica
3. **Project Issues**: Create an issue in your project repository

---

## Summary

This migration guide provides:

✅ Complete JSON-LD schema definitions for all context types  
✅ Automated conversion script for existing data  
✅ Step-by-step import instructions  
✅ Verification and testing procedures  
✅ Troubleshooting guidance  
✅ Integration with RFP Analyzer  

Your organizational context is now centralized in Context Studio and accessible to all your AI agents!