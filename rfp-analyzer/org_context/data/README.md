# Context Studio Sample Data Files

This directory contains sample data files in JSON-LD format, ready to import into IBM Context Studio.

## 📦 Available Data Files

### 1. organization_data.jsonld
**Schema:** organization_schema.jsonld  
**Size:** 89 lines  
**Contains:**
- Organization: IBM Consulting
- Industry: Consulting
- Tech Stack: Python, TypeScript, Java, AWS, Azure, PostgreSQL, MongoDB, FastAPI, React, Django
- Compliance: GDPR, SOC2, ISO 27001, OWASP Top 10
- Naming Conventions: IBM-FR-001, NFR-001, CR-001, etc.
- Priority Keywords: must, should, could
- Risk Thresholds: AI/ML, blockchain, real-time indicators

**Automatic Mapping:** `"@type": "org:OrganizationContext"` → organization_schema.jsonld

---

### 2. healthcare_domain_knowledge.jsonld
**Schema:** domain_knowledge_schema.jsonld  
**Size:** 175 lines  
**Contains:**
- **7 Healthcare Terms:** HL7, FHIR, DICOM, EHR, PACS, SLA, API
- **8 Acronyms:** HL7, FHIR, DICOM, ICD-10, CPT, HIPAA, CI/CD, SSO
- **4 Technologies:** Kubernetes, Docker, PostgreSQL, MongoDB (with versions and usage)
- **4 Vendors:** AWS, Azure, Epic Systems, Oracle Cerner

**Automatic Mapping:** `"@type": "domain:DomainKnowledge"` → domain_knowledge_schema.jsonld

---

### 3. coding_standards.jsonld
**Schema:** standards_schema.jsonld  
**Size:** 177 lines  
**Contains:**
- **Standard Type:** Coding
- **Version:** 2.0
- **7 Sections:** Python, Java, TypeScript standards, naming conventions, required tools, code review, documentation
- **8 Rules:** CS-001 through CS-008 (type hints, line length, naming, docstrings, coverage, logging, exceptions, config)
- **Full Content:** Complete coding standards document in markdown
- **Applicable Languages:** Python, Java, TypeScript, JavaScript
- **Compliance:** OWASP Top 10, ISO 27001

**Automatic Mapping:** `"@type": "std:StandardDocument"` → standards_schema.jsonld

---

### 4. security_standards.jsonld
**Schema:** standards_schema.jsonld  
**Size:** 244 lines  
**Contains:**
- **Standard Type:** Security
- **Version:** 3.0
- **8 Sections:** Security Framework, Authentication, Data Protection, Network Security, Application Security, Vulnerability Management, Incident Response, Compliance
- **10 Rules:** SEC-001 through SEC-010 (MFA, encryption, TLS, passwords, patching, rate limiting, logging, input validation, secrets, training)
- **Full Content:** Complete security standards document in markdown
- **Compliance:** SOC 2 Type II, ISO 27001, GDPR, HIPAA, PCI DSS, OWASP Top 10

**Automatic Mapping:** `"@type": "std:StandardDocument"` → standards_schema.jsonld

---

### 5. proposal_response_template.jsonld
**Schema:** template_schema.jsonld  
**Size:** 318 lines  
**Contains:**
- **Template Type:** Proposal Response
- **Version:** 1.0
- **12 Sections:** Document Control, Executive Summary, Company Profile, Requirements Understanding, Technical Approach, Implementation Methodology, Team Composition, Timeline, Pricing, Support, Terms, Appendices
- **10 Placeholders:** RFP number, client name, dates, project name, costs, team names, technologies
- **Full Content:** Complete proposal template in markdown
- **Applicable Industries:** Technology, Consulting, Healthcare, Finance

**Automatic Mapping:** `"@type": "tmpl:Template"` → template_schema.jsonld

---

### 6. historical_rfps/sample_healthcare_portal_rfp.jsonld
**Schema:** historical_rfp_schema.jsonld  
**Size:** 289 lines  
**Contains:**
- **RFP ID:** RFP-2024-HEALTHCARE-PORTAL-001
- **Title:** Patient Portal and EHR Integration System
- **Client:** Metropolitan Healthcare System
- **Industry:** Healthcare
- **Outcome:** Won
- **Project Value:** $2.5M USD
- **Duration:** 9 months
- **Team Size:** 12 people
- **Technologies:** React, TypeScript, Python, FastAPI, PostgreSQL, AWS, HL7 FHIR, OAuth 2.0, Docker, Kubernetes
- **Key Requirements:** 12 major requirements (HIPAA, FHIR integration, SSO, scheduling, messaging, etc.)
- **Challenges:** 6 challenges faced
- **Lessons Learned:** 6 lessons
- **Success Factors:** 8 factors that led to winning
- **Analysis:** 45 functional, 18 non-functional, 12 compliance requirements, complexity score 0.82
- **Full Content:** Complete RFP document with all sections

**Automatic Mapping:** `"@type": "hist:HistoricalRFP"` → historical_rfp_schema.jsonld

---

## 🚀 How to Import to Context Studio

### Prerequisites
1. ✅ All 5 schemas must be imported FIRST
2. ✅ You have Context Studio access
3. ✅ You have API credentials or UI access

### Option 1: Import from Local Files

1. **Access Context Studio**
   - Go to: https://servicesessentials.ibm.com/agenticapps
   - Navigate to **Platform Settings** → **Context Studio**

2. **Import Each Data File**
   - Go to **Data** tab
   - Click **Import Data**
   - Select the appropriate schema (Context Studio will auto-detect from `@type`)
   - Upload the `.jsonld` file
   - Click **Import**

3. **Verify Import**
   - Check that data appears in Context Studio
   - Verify all fields are populated
   - No mapping errors

### Option 2: Import from Remote URL (SharePoint/OneDrive/Box)

1. **Upload Files to Shared Drive**
   - Upload all files from this directory to SharePoint/OneDrive/Box
   - Get shareable links for each file

2. **Import from URL**
   - In Context Studio → **Data** tab
   - Click **Import from URL**
   - Paste the remote URL
   - Context Studio automatically:
     - Downloads the file
     - Reads `@type` to identify schema
     - Maps all fields automatically
     - Imports the data

3. **Example URLs:**
   ```
   https://yourcompany.sharepoint.com/.../organization_data.jsonld
   https://yourcompany.sharepoint.com/.../healthcare_domain_knowledge.jsonld
   https://yourcompany.sharepoint.com/.../coding_standards.jsonld
   https://yourcompany.sharepoint.com/.../security_standards.jsonld
   https://yourcompany.sharepoint.com/.../proposal_response_template.jsonld
   https://yourcompany.sharepoint.com/.../sample_healthcare_portal_rfp.jsonld
   ```

---

## 📋 Import Checklist

### Data Files to Import
- [ ] organization_data.jsonld
- [ ] healthcare_domain_knowledge.jsonld
- [ ] coding_standards.jsonld
- [ ] security_standards.jsonld
- [ ] proposal_response_template.jsonld
- [ ] historical_rfps/sample_healthcare_portal_rfp.jsonld

### Verification Steps
- [ ] All data appears in Context Studio
- [ ] Fields are correctly populated
- [ ] No validation errors
- [ ] Can query the data via API
- [ ] RFP Analyzer can access the context

---

## 🔍 How Automatic Mapping Works

Each data file contains special fields that tell Context Studio which schema to use:

```json
{
  "@context": "https://ibm.com/context-studio/organization/context.jsonld",
  "@type": "org:OrganizationContext",
  "@id": "org:ibm-consulting",
  ...
}
```

- **`@context`**: Points to the schema definition
- **`@type`**: Identifies which schema class to use
- **`@id`**: Unique identifier for this data

Context Studio reads these fields and **automatically maps** all properties to the correct schema fields. **No manual mapping required!**

---

## 📊 Data Statistics

| File | Lines | Schema | Type | Status |
|------|-------|--------|------|--------|
| organization_data.jsonld | 89 | organization_schema | Organization Config | ✅ Ready |
| healthcare_domain_knowledge.jsonld | 175 | domain_knowledge_schema | Domain Knowledge | ✅ Ready |
| coding_standards.jsonld | 177 | standards_schema | Coding Standards | ✅ Ready |
| security_standards.jsonld | 244 | standards_schema | Security Standards | ✅ Ready |
| proposal_response_template.jsonld | 318 | template_schema | Proposal Template | ✅ Ready |
| sample_healthcare_portal_rfp.jsonld | 289 | historical_rfp_schema | Historical RFP | ✅ Ready |
| **Total** | **1,292** | **5 schemas** | **6 data files** | **✅ Complete** |

---

## 🎯 What This Data Enables

### Organization Data Enables:
✅ Centralized tech stack management  
✅ Compliance framework tracking  
✅ Consistent requirement naming across all RFPs  
✅ Automated priority detection in requirements  
✅ Risk assessment automation  

### Domain Knowledge Enables:
✅ Healthcare terminology lookup for RFP analysis  
✅ Acronym expansion in documents  
✅ Technology glossary for proposals  
✅ Vendor preference tracking  

### Standards Enable:
✅ Coding standards reference in proposals  
✅ Security standards compliance checking  
✅ Rule-based validation  
✅ Compliance framework mapping  

### Template Enables:
✅ Consistent proposal structure  
✅ Reusable content sections  
✅ Placeholder management  
✅ Industry-specific customization  

### Historical RFP Enables:
✅ Win/loss analysis  
✅ Lessons learned repository  
✅ Success factor identification  
✅ Similar RFP comparison  
✅ Complexity estimation for new RFPs  

---

## 🔧 Troubleshooting

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

## 📚 Additional Resources

- **REMOTE_IMPORT_GUIDE.md** - Detailed remote import instructions
- **SCHEMA_FILES_SUMMARY.md** - Overview of all schemas
- **CONTEXT_STUDIO_MIGRATION_GUIDE.md** - Complete migration process
- **CONTEXT_STUDIO_QUICK_START.md** - 30-minute quick start

---

## ✨ Summary

You have **6 production-ready data files** containing:

1. **Organization Configuration** - Complete IBM Consulting setup
2. **Healthcare Domain Knowledge** - 7 terms, 8 acronyms, 4 technologies, 4 vendors
3. **Coding Standards** - 7 sections, 8 rules, full documentation
4. **Security Standards** - 8 sections, 10 rules, full documentation
5. **Proposal Template** - 12 sections, 10 placeholders, full template
6. **Historical RFP** - Complete healthcare portal RFP with outcome data

**Total:** 1,292 lines of structured, validated, ready-to-import data!

**Ready to import?** Upload to your shared drive and import via Context Studio! 🚀