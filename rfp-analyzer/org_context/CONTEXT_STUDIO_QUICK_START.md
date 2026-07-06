# Context Studio Migration - Quick Start

## Overview

This quick start guide helps you migrate your organizational context from local files to IBM Context Studio in 30 minutes.

---

## What You'll Create

**5 Schema Files** (JSON-LD format):
1. `organization_schema.jsonld` - Org config, tech stack, compliance
2. `domain_knowledge_schema.jsonld` - Industry terms, acronyms
3. `standards_schema.jsonld` - Coding/security standards
4. `template_schema.jsonld` - Document templates
5. `historical_rfp_schema.jsonld` - Past RFP examples

**Data Files** (converted from your existing files):
- Organization configuration
- Domain knowledge documents
- Standards documents
- Templates
- Historical RFPs

---

## Prerequisites

```bash
# 1. Install dependencies
pip install pyyaml requests rdflib

# 2. Set environment variables
export CONTEXT_STUDIO_URL="https://your-context-studio.ibm.com/api/v1"
export CONTEXT_STUDIO_TOKEN="your-api-token"
export CONTEXT_STUDIO_WORKSPACE="your-workspace-id"
```

---

## Step 1: Create Schema Files (5 minutes)

### Option A: Use Code Mode (Recommended)

1. Switch to Code mode
2. Create directory: `rfp-analyzer/org_context/schemas/`
3. Copy schema definitions from the JSON-LD files in `schemas/`
4. Create 5 `.jsonld` files with the schema definitions

### Option B: Manual Creation

Create each schema file manually using the definitions in the schema plan document.

---

## Step 2: Convert Your Data (5 minutes)

### Create Conversion Script

1. Switch to Code mode
2. Create `rfp-analyzer/org_context/convert_to_jsonld.py`
3. Copy the conversion script from [`CONTEXT_STUDIO_MIGRATION_GUIDE.md`](CONTEXT_STUDIO_MIGRATION_GUIDE.md#conversion-script-specification)

### Run Conversion

```bash
cd rfp-analyzer/org_context
python convert_to_jsonld.py
```

**Expected Output:**
```
✓ Converted: data/organization_data.jsonld
✓ Converted: data/healthcare-terminology.jsonld
✓ Converted: data/coding-standards.jsonld
✓ Converted: data/security-standards.jsonld
✓ Converted: data/proposal-response-template.jsonld
✓ Converted: data/historical_rfps/sample-healthcare-portal-rfp.jsonld
```

---

## Step 3: Import Schemas to Context Studio (10 minutes)

### Access Context Studio

1. Go to: https://servicesessentials.ibm.com/agenticapps
2. Navigate to **Platform Settings** → **Context Studio**
3. Select your workspace

### Import Each Schema

For each schema file in `schemas/`:

1. Click **"Import Schema"**
2. Select **"JSON-LD"** format
3. Upload the file
4. Click **"Import"**
5. Verify it appears in the schemas list

**Import Order:**
1. ✅ `organization_schema.jsonld`
2. ✅ `domain_knowledge_schema.jsonld`
3. ✅ `standards_schema.jsonld`
4. ✅ `template_schema.jsonld`
5. ✅ `historical_rfp_schema.jsonld`

---

## Step 4: Import Data to Context Studio (10 minutes)

### Import Organization Configuration

1. Go to **"Data"** tab
2. Click **"Import Data"**
3. Select schema: **"Organization Context"**
4. Upload: `data/organization_data.jsonld`
5. Click **"Import"**

### Import Domain Knowledge

1. Select schema: **"Domain Knowledge"**
2. Upload: `data/healthcare-terminology.jsonld`
3. Click **"Import"**

### Import Standards

For each standards file:
1. Select schema: **"Standard Document"**
2. Upload the file
3. Click **"Import"**

Files to import:
- ✅ `coding-standards.jsonld`
- ✅ `security-standards.jsonld`

### Import Templates

1. Select schema: **"Template"**
2. Upload: `data/proposal-response-template.jsonld`
3. Click **"Import"**

### Import Historical RFPs

For each file in `data/historical_rfps/`:
1. Select schema: **"Historical RFP"**
2. Upload the file
3. Click **"Import"**

---

## Step 5: Configure RFP Analyzer (5 minutes)

### Update Environment Variables

Edit `rfp-analyzer/.env`:

```bash
# Context Studio Configuration
CONTEXT_STUDIO_URL=https://your-context-studio.ibm.com/api/v1
CONTEXT_STUDIO_TOKEN=your-api-token-here
CONTEXT_STUDIO_WORKSPACE=your-workspace-id
CONTEXT_STUDIO_ENABLED=true
```

### Test Integration

```bash
cd rfp-analyzer
python -c "
from org_context.context_manager import get_context_manager
cm = get_context_manager()
ctx = cm.get_context()
print(f'✓ Organization: {ctx.name}')
print(f'✓ Industry: {ctx.industry}')
print(f'✓ Tech Stack: {ctx.tech_stack.preferred_languages}')
"
```

**Expected Output:**
```
✓ Organization: IBM Consulting
✓ Industry: Consulting
✓ Tech Stack: ['Python', 'TypeScript', 'Java']
```

---

## Verification Checklist

### Schemas Imported ✅
- [ ] Organization Context schema
- [ ] Domain Knowledge schema
- [ ] Standard Document schema
- [ ] Template schema
- [ ] Historical RFP schema

### Data Imported ✅
- [ ] Organization configuration
- [ ] Domain knowledge documents
- [ ] Standards documents
- [ ] Templates
- [ ] Historical RFPs

### Integration Working ✅
- [ ] Environment variables set
- [ ] Context Manager can load from Context Studio
- [ ] RFP Analyzer can access organizational context

---

## What's Next?

### 1. Update Your Workflow

**Before (Local Files):**
```python
# Load from local YAML
context_manager = ContextManager('org_context/config/org_config.yaml')
```

**After (Context Studio):**
```python
# Load from Context Studio
context_manager = initialize_context_manager(
    config_path=os.getenv("CONTEXT_STUDIO_URL") + "/organization/ibm-consulting",
    remote_kwargs={
        "auth_token": os.getenv("CONTEXT_STUDIO_TOKEN"),
        "workspace_id": os.getenv("CONTEXT_STUDIO_WORKSPACE")
    }
)
```

### 2. Update Context Through UI

Instead of editing local files, update context through Context Studio:

1. Log in to Context Studio
2. Navigate to the data you want to update
3. Click **"Edit"**
4. Make changes
5. Click **"Save"**

Changes are immediately available to all agents!

### 3. Add New Context

To add new standards, templates, or domain knowledge:

1. Create the content in JSON-LD format
2. Import through Context Studio UI
3. Or use the API to programmatically add data

---

## Troubleshooting

### Schema Import Failed
```bash
# Validate JSON-LD syntax
python -c "import json; json.load(open('schemas/organization_schema.jsonld'))"
```

### Data Import Failed
- Verify schema was imported first
- Check that `@type` matches schema class name
- Ensure all required fields have values

### Can't Connect to Context Studio
```bash
# Test API connectivity
curl -H "Authorization: Bearer $CONTEXT_STUDIO_TOKEN" \
     $CONTEXT_STUDIO_URL/health
```

### Context Manager Returns Empty
- Verify API token is valid
- Check workspace ID is correct
- Ensure data was imported successfully

---

## File Structure After Migration

```
rfp-analyzer/org_context/
├── schemas/                          # JSON-LD schemas (import to Context Studio)
│   ├── organization_schema.jsonld
│   ├── domain_knowledge_schema.jsonld
│   ├── standards_schema.jsonld
│   ├── template_schema.jsonld
│   └── historical_rfp_schema.jsonld
│
├── data/                             # Converted data (import to Context Studio)
│   ├── organization_data.jsonld
│   ├── healthcare-terminology.jsonld
│   ├── coding-standards.jsonld
│   ├── security-standards.jsonld
│   ├── proposal-response-template.jsonld
│   └── historical_rfps/
│       └── *.jsonld
│
├── convert_to_jsonld.py             # Conversion script
├── schemas/                          # JSON-LD schema files
├── CONTEXT_STUDIO_MIGRATION_GUIDE.md # Complete migration guide
└── CONTEXT_STUDIO_QUICK_START.md    # This file
```

---

## Benefits After Migration

✅ **Centralized Context** - Single source of truth for all agents  
✅ **Real-time Updates** - Changes immediately available to all agents  
✅ **Version Control** - Track changes and rollback if needed  
✅ **Access Control** - Manage who can view/edit context  
✅ **Audit Trail** - See who changed what and when  
✅ **Collaboration** - Team can update context through UI  
✅ **Scalability** - Add new context types easily  

---

## Support Resources

- **Detailed Guide**: [`CONTEXT_STUDIO_MIGRATION_GUIDE.md`](CONTEXT_STUDIO_MIGRATION_GUIDE.md)
- **Schema Definitions**: See `schemas/` directory for all JSON-LD schema files
- **Context Studio Docs**: https://ibm.com/docs/context-studio
- **IBM ICA Support**: https://ibm.com/support/ica

---

## Summary

You've successfully migrated your organizational context to Context Studio! 🎉

**What you accomplished:**
1. ✅ Created 5 JSON-LD schemas
2. ✅ Converted existing data to JSON-LD format
3. ✅ Imported schemas to Context Studio
4. ✅ Imported data to Context Studio
5. ✅ Configured RFP Analyzer integration

Your organizational context is now centralized and accessible to all your AI agents through Context Studio!