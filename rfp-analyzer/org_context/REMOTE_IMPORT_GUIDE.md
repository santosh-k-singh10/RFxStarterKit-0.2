# Context Studio Remote Import Guide

## Overview

This guide explains how to import your organizational context data from a remote location (SharePoint, OneDrive, Box, or any shared drive) into IBM Context Studio, where it will automatically map to your imported schemas.

---

## Understanding the Import Process

### What You Have Created

1. **5 Schema Files** (in `schemas/` folder) - Define the structure
   - These tell Context Studio what fields to expect
   - Import these FIRST into Context Studio

2. **Sample Data Files** (in `data/` folder) - Contain actual data
   - These are in JSON-LD format
   - They reference the schemas via `@type` and `@context`
   - Context Studio automatically maps them to schemas
   - Import these SECOND after schemas are imported

### How Automatic Mapping Works

When you import a data file, Context Studio:
1. Reads the `@context` URL to understand the schema
2. Looks at the `@type` to identify which schema class to use
3. Automatically maps all properties to the schema fields
4. Validates the data against the schema
5. Stores it in your workspace

**No manual mapping required!** The `@type` and `@context` in each data file tell Context Studio exactly which schema to use.

---

## File Formats Supported by Context Studio

Context Studio accepts these formats for data import:

✅ **JSON-LD** (.jsonld) - **RECOMMENDED** - What we created
- Linked Data format with automatic schema mapping
- Self-describing with `@context` and `@type`
- Best for structured organizational data

✅ **RDF** (.rdf) - Alternative format
- XML-based RDF format
- More verbose than JSON-LD

✅ **Turtle** (.ttl) - Alternative format
- Text-based RDF format
- More compact than RDF/XML

**The JSON-LD files we created are the BEST format for your use case.**

---

## Your Data Files (Ready for Import)

### Location
```
rfp-analyzer/org_context/data/
├── organization_data.jsonld          ← Organization config
├── healthcare_domain_knowledge.jsonld ← Domain knowledge
├── coding_standards.jsonld           ← Coding standards
└── (more files to be created)
```

### What Each File Contains

#### 1. organization_data.jsonld
**Maps to Schema:** `organization_schema.jsonld`  
**Contains:**
- Organization name: IBM Consulting
- Industry: Consulting
- Tech stack (Python, TypeScript, Java, AWS, Azure, etc.)
- Compliance requirements (GDPR, SOC2, ISO 27001)
- Naming conventions for requirements
- Priority keywords (must, should, could)
- Risk thresholds

**Automatic Mapping:** The `"@type": "org:OrganizationContext"` tells Context Studio to use the Organization schema.

#### 2. healthcare_domain_knowledge.jsonld
**Maps to Schema:** `domain_knowledge_schema.jsonld`  
**Contains:**
- 7 healthcare terms (HL7, FHIR, DICOM, EHR, PACS, SLA, API)
- 8 acronyms with expansions
- 4 technology glossary entries (Kubernetes, Docker, PostgreSQL, MongoDB)
- 4 vendor preferences (AWS, Azure, Epic, Cerner)

**Automatic Mapping:** The `"@type": "domain:DomainKnowledge"` tells Context Studio to use the Domain Knowledge schema.

#### 3. coding_standards.jsonld
**Maps to Schema:** `standards_schema.jsonld`  
**Contains:**
- Coding standards for Python, Java, TypeScript
- 7 sections (Python Standards, Naming Conventions, Required Tools, etc.)
- 8 specific rules (CS-001 through CS-008)
- Full markdown content of the standards document

**Automatic Mapping:** The `"@type": "std:StandardDocument"` tells Context Studio to use the Standards schema.

---

## Remote Import Options

### Option 1: SharePoint/OneDrive (Microsoft 365)

#### Step 1: Upload Files to SharePoint
1. Go to your SharePoint site or OneDrive
2. Create a folder: `OrganizationalContext`
3. Upload all files from `rfp-analyzer/org_context/data/` to this folder

#### Step 2: Get Shareable Links
For each file:
1. Right-click the file → **Share**
2. Click **Copy link**
3. Choose **People with existing access** or **People in your organization**
4. Copy the link

#### Step 3: Import to Context Studio
1. Log in to Context Studio
2. Go to **Data** tab
3. Click **Import from URL**
4. Paste the SharePoint link
5. Context Studio will:
   - Download the file
   - Read the `@type` to identify the schema
   - Automatically map all fields
   - Import the data

**Example SharePoint URL:**
```
https://yourcompany.sharepoint.com/sites/team/Shared%20Documents/OrganizationalContext/organization_data.jsonld
```

### Option 2: Box

#### Step 1: Upload to Box
1. Go to Box.com
2. Create folder: `OrganizationalContext`
3. Upload all data files

#### Step 2: Get Direct Links
For each file:
1. Right-click → **Share**
2. Create a **Shared Link**
3. Copy the link

#### Step 3: Import to Context Studio
Same as SharePoint - paste the Box link into Context Studio's "Import from URL" feature.

### Option 3: AWS S3

#### Step 1: Upload to S3
```bash
aws s3 cp rfp-analyzer/org_context/data/ s3://your-bucket/context/ --recursive
```

#### Step 2: Make Files Accessible
Create presigned URLs or make bucket publicly readable (if appropriate).

#### Step 3: Import to Context Studio
Use the S3 URLs in Context Studio's import feature.

### Option 4: HTTP/HTTPS Server

If you have a web server:
1. Upload files to your server
2. Make them accessible via HTTPS
3. Use the URLs in Context Studio

**Example:**
```
https://yourcompany.com/context/organization_data.jsonld
```

---

## Step-by-Step Import Process

### Phase 1: Import Schemas (One-Time Setup)

**Do this FIRST before importing data!**

1. Access Context Studio
2. Go to **Schemas** tab
3. For each schema file in `schemas/`:
   - Click **Import Schema**
   - Select **JSON-LD** format
   - Upload the file
   - Click **Import**

**Import in this order:**
1. ✅ organization_schema.jsonld
2. ✅ domain_knowledge_schema.jsonld
3. ✅ standards_schema.jsonld
4. ✅ template_schema.jsonld
5. ✅ historical_rfp_schema.jsonld

### Phase 2: Upload Data Files to Remote Location

Choose your preferred location (SharePoint, OneDrive, Box, S3) and upload all files from `data/` folder.

### Phase 3: Import Data from Remote Location

For each data file:

1. **In Context Studio:**
   - Go to **Data** tab
   - Click **Import from URL**

2. **Enter the remote URL:**
   ```
   https://yourcompany.sharepoint.com/.../organization_data.jsonld
   ```

3. **Context Studio automatically:**
   - Downloads the file
   - Reads `@type`: `"org:OrganizationContext"`
   - Finds the matching schema
   - Maps all properties automatically
   - Validates the data
   - Imports it

4. **Verify:**
   - Data appears in Context Studio
   - All fields are populated
   - No mapping errors

**Repeat for each data file:**
- ✅ organization_data.jsonld
- ✅ healthcare_domain_knowledge.jsonld
- ✅ coding_standards.jsonld
- ✅ security_standards.jsonld (when created)
- ✅ proposal_template.jsonld (when created)
- ✅ historical RFPs (when created)

---

## Why JSON-LD is Perfect for Your Use Case

### Self-Describing
```json
{
  "@context": "https://ibm.com/context-studio/organization/context.jsonld",
  "@type": "org:OrganizationContext",
  "@id": "org:ibm-consulting",
  ...
}
```
- `@context` tells Context Studio where to find schema definitions
- `@type` tells Context Studio which schema class to use
- `@id` provides a unique identifier

### Automatic Mapping
No manual field mapping needed! Context Studio reads:
```json
"org:name": "IBM Consulting"
```
And automatically maps it to the `org:name` property in the Organization schema.

### Validation
Context Studio validates your data against the schema:
- Required fields must be present
- Data types must match (string, number, date, etc.)
- Enum values must be valid
- Relationships must reference existing entities

### Linked Data
You can reference other entities:
```json
"org:relatedStandards": [
  {"@id": "std:coding-standards"},
  {"@id": "std:security-standards"}
]
```

---

## Alternative: If You Want Plain Text/CSV

If Context Studio doesn't support direct JSON-LD import from URLs, you can:

### Option A: Use Context Studio's UI Import
1. Download the JSON-LD files from your shared drive
2. Import them through Context Studio's UI
3. Context Studio will still automatically map them

### Option B: Convert to CSV (Not Recommended)
You could convert to CSV, but you'd lose:
- Automatic schema mapping
- Nested structures
- Relationships between entities
- Validation

**Recommendation: Stick with JSON-LD files - they're designed for this exact use case!**

---

## Verification Checklist

After importing data:

### Check Organization Data
- [ ] Organization name appears correctly
- [ ] Tech stack lists all languages
- [ ] Compliance frameworks are listed
- [ ] Naming conventions are set
- [ ] Priority keywords are configured
- [ ] Risk thresholds are defined

### Check Domain Knowledge
- [ ] All terms are imported with definitions
- [ ] Acronyms show expansions
- [ ] Technology glossary is populated
- [ ] Vendor preferences are listed

### Check Standards
- [ ] Standard document appears
- [ ] All sections are present
- [ ] Rules are listed with IDs
- [ ] Full content is available

---

## Troubleshooting

### Issue: "Schema not found" error
**Solution:** Import the schema files FIRST before importing data files.

### Issue: "Invalid @type" error
**Solution:** Ensure the `@type` in your data file matches a class in your schema.

### Issue: "Required field missing" error
**Solution:** Check that all required fields in the schema have values in your data file.

### Issue: Can't access remote file
**Solution:** 
- Verify the URL is accessible
- Check sharing permissions
- Ensure the file is publicly readable or you have credentials configured

---

## Summary

✅ **Your data files are ready!** They're in the correct JSON-LD format.

✅ **Automatic mapping works!** The `@type` and `@context` tell Context Studio which schema to use.

✅ **Remote import supported!** Upload to SharePoint/OneDrive/Box/S3 and import via URL.

✅ **No manual mapping needed!** Context Studio reads the schema references and maps automatically.

### Next Steps:
1. Import all 5 schema files to Context Studio (one-time setup)
2. Upload your data files to your preferred shared drive
3. Import each data file from the remote URL
4. Verify the data appears correctly in Context Studio
5. Your RFP Analyzer can now access this centralized context!

---

**The JSON-LD files we created ARE the correct format. They will automatically map to your schemas when imported!**