# Context Studio Schema Files

This directory contains JSON-LD schema files for importing your organizational context into IBM Context Studio.

## Schema Files

### 1. organization_schema.jsonld
**Purpose:** Defines organizational configuration structure  
**Contains:**
- Organization basic info (name, industry, description)
- Technology stack (languages, cloud providers, databases, frameworks)
- Compliance requirements (frameworks, certifications, standards)
- Naming conventions (requirement ID prefixes and formats)
- Priority mapping (keywords for MUST, SHOULD, COULD priorities)
- Risk thresholds (complexity indicators, timeline red flags)

### 2. domain_knowledge_schema.jsonld
**Purpose:** Defines industry-specific knowledge structure  
**Contains:**
- Industry terms with definitions
- Acronyms with expansions
- Technology glossary entries
- Vendor preferences

### 3. standards_schema.jsonld
**Purpose:** Defines organizational standards documents  
**Contains:**
- Standard document metadata (title, version, status)
- Standard types (coding, security, architecture, testing)
- Sections and rules
- Applicable languages and technologies

### 4. template_schema.jsonld
**Purpose:** Defines reusable document templates  
**Contains:**
- Template metadata (name, type, version)
- Template content with placeholders
- Sections structure
- Applicable industries

### 5. historical_rfp_schema.jsonld
**Purpose:** Defines historical RFP records  
**Contains:**
- RFP metadata (ID, title, client, industry)
- Project details (value, duration, team size)
- Outcome and success factors
- Analysis results (requirements counts, complexity score)

## How to Import to Context Studio

### Step 1: Access Context Studio
1. Go to: https://servicesessentials.ibm.com/agenticapps
2. Navigate to **Platform Settings** → **Context Studio**
3. Select your workspace

### Step 2: Import Each Schema
For each `.jsonld` file in this directory:

1. Click **"Import Schema"** button
2. Select **"JSON-LD"** as the format
3. Upload the schema file
4. Review the schema preview
5. Click **"Import"**
6. Verify it appears in the schemas list

### Import Order (Recommended)
Import in this order to avoid dependency issues:

1. ✅ `organization_schema.jsonld`
2. ✅ `domain_knowledge_schema.jsonld`
3. ✅ `standards_schema.jsonld`
4. ✅ `template_schema.jsonld`
5. ✅ `historical_rfp_schema.jsonld`

### Step 3: Verify Import
After importing each schema:
- Go to **"Schemas"** tab in Context Studio
- Verify the schema appears with status "Active"
- Click on it to view the structure
- Confirm all classes and properties are present

## Next Steps

After importing schemas:

1. **Convert Your Data**
   - Run the conversion script: `python convert_to_jsonld.py`
   - This will create data files in the `../data/` directory

2. **Import Data**
   - Import the generated data files into Context Studio
   - Match each data file to its corresponding schema

3. **Configure Integration**
   - Update your `.env` file with Context Studio credentials
   - Test the integration with your RFP Analyzer

## Troubleshooting

### Schema Import Failed
- **Check JSON syntax:** Validate the file with a JSON-LD validator
- **Verify permissions:** Ensure you have schema creation rights
- **Check Context URLs:** Ensure `@context` URLs are accessible

### Schema Validation Errors
- Review the error message in Context Studio
- Check that all required fields are present
- Verify data types match the schema definitions

## Support

For detailed instructions, see:
- **Migration Guide:** `../CONTEXT_STUDIO_MIGRATION_GUIDE.md`
- **Quick Start:** `../CONTEXT_STUDIO_QUICK_START.md`
- **Schema Plan:** `../CONTEXT_STUDIO_SCHEMA_PLAN.md`

## Schema Validation

To validate a schema file before importing:

```bash
# Using Python
python -c "import json; json.load(open('organization_schema.jsonld'))"

# Using jq (if installed)
jq . organization_schema.jsonld
```

## File Information

- **Format:** JSON-LD (JSON for Linked Data)
- **Encoding:** UTF-8
- **Compatible with:** IBM Context Studio, RDF stores, semantic web tools
- **Version:** 1.0
- **Last Updated:** 2026-05-13

---

**Ready to import?** Follow the steps above to get your organizational context into Context Studio!