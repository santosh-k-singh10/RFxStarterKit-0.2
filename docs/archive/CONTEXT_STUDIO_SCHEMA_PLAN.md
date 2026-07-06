
# Context Studio Schema Migration Plan

## Overview

This document provides the complete plan for migrating organizational context from local files to IBM Context Studio using JSON-LD schemas.

**Migration Strategy:**
1. Create separate JSON-LD schemas for each context type
2. Generate sample data files from existing content
3. Import schemas into Context Studio
4. Import data files into Context Studio

---

## Schema Definitions

### 1. Organization Configuration Schema

**File:** `organization_schema.jsonld`

**Purpose:** Defines organizational configuration including tech stack, compliance requirements, naming conventions, priority mappings, and risk thresholds.

```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "rfp": "https://ibm.com/context-studio/rfp-analyzer/",
    "org": "https://ibm.com/context-studio/organization/",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },
  "@graph": [
    {
      "@id": "org:OrganizationContext",
      "@type": "rdfs:Class",
      "rdfs:label": "Organization Context",
      "rdfs:comment": "Complete organizational context for RFP analysis",
      "rdfs:subClassOf": "schema:Organization"
    },
    {
      "@id": "org:name",
      "@type": "rdf:Property",
      "rdfs:label": "Organization Name",
      "rdfs:domain": "org:OrganizationContext",
      "rdfs:range": "xsd:string",
      "schema:required": true
    },
    {
      "@id": "org:industry",
      "@type": "rdf:Property",
      "rdfs:label": "Industry Sector",
      "rdfs:domain": "org:OrganizationContext",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "org:description",
      "@type": "rdf:Property",
      "rdfs:label": "Organization Description",
      "rdfs:domain": "org:OrganizationContext",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "org:TechStack",
      "@type": "rdfs:Class",
      "rdfs:label": "Technology Stack",
      "rdfs:comment": "Organization's technology preferences and standards"
    },
    {
      "@id": "org:techStack",
      "@type": "rdf:Property",
      "rdfs:label": "Technology Stack",
      "rdfs:domain": "org:OrganizationContext",
      "rdfs:range": "org:TechStack"
    },
    {
      "@id": "org:preferredLanguages",
      "@type": "rdf:Property",
      "rdfs:label": "Preferred Programming Languages",
      "rdfs:domain": "org:TechStack",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "org:cloudProviders",
      "@type": "rdf:Property",
      "rdfs:label": "Approved Cloud Providers",
      "rdfs:domain": "org:TechStack",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "org:databases",
      "@type": "rdf:Property",
      "rdfs:label": "Preferred Database Systems",
      "rdfs:domain": "org:TechStack",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "org:frameworks",
      "@type": "rdf:Property",
      "rdfs:label": "Preferred Frameworks",
      "rdfs:domain": "org:TechStack",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "org:architecturePatterns",
      "@type": "rdf:Property",
      "rdfs:label": "Architecture Patterns",
      "rdfs:domain": "org:TechStack",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "org:ComplianceRequirements",
      "@type": "rdfs:Class",
      "rdfs:label": "Compliance Requirements",
      "rdfs:comment": "Regulatory and compliance frameworks"
    },
    {
      "@id": "org:compliance",
      "@type": "rdf:Property",
      "rdfs:label": "Compliance Requirements",
      "rdfs:domain": "org:OrganizationContext",
      "rdfs:range": "org:ComplianceRequirements"
    },
    {
      "@id": "org:complianceFrameworks",
      "@type": "rdf:Property",
      "rdfs:label": "Compliance Frameworks",
      "rdfs:domain": "org:ComplianceRequirements",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true,
      "schema:description": "Required compliance frameworks (GDPR, HIPAA, SOC2, etc.)"
    },
    {
      "@id": "org:certifications",
      "@type": "rdf:Property",
      "rdfs:label": "Required Certifications",
      "rdfs:domain": "org:ComplianceRequirements",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "org:standards",
      "@type": "rdf:Property",
      "rdfs:label": "Industry Standards",
      "rdfs:domain": "org:ComplianceRequirements",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "org:NamingConventions",
      "@type": "rdfs:Class",
      "rdfs:label": "Naming Conventions",
      "rdfs:comment": "Requirement ID naming conventions"
    },
    {
      "@id": "org:namingConventions",
      "@type": "rdf:Property",
      "rdfs:label": "Naming Conventions",
      "rdfs:domain": "org:OrganizationContext",
      "rdfs:range": "org:NamingConventions"
    },
    {
      "@id": "org:requirementPrefix",
      "@type": "rdf:Property",
      "rdfs:label": "Requirement Prefix",
      "rdfs:domain": "org:NamingConventions",
      "rdfs:range": "xsd:string",
      "schema:defaultValue": "REQ"
    },
    {
      "@id": "org:functionalPrefix",
      "@type": "rdf:Property",
      "rdfs:label": "Functional Requirement Prefix",
      "rdfs:domain": "org:NamingConventions",
      "rdfs:range": "xsd:string",
      "schema:defaultValue": "FR"
    },
    {
      "@id": "org:nonFunctionalPrefix",
      "@type": "rdf:Property",
      "rdfs:label": "Non-Functional Requirement Prefix",
      "rdfs:domain": "org:NamingConventions",
      "rdfs:range": "xsd:string",
      "schema:defaultValue": "NFR"
    },
    {
      "@id": "org:compliancePrefix",
      "@type": "rdf:Property",
      "rdfs:label": "Compliance Requirement Prefix",
      "rdfs:domain": "org:NamingConventions",
      "rdfs:range": "xsd:string",
      "schema:defaultValue": "CR"
    },
    {
      "@id": "org:separator",
      "@type": "rdf:Property",
      "rdfs:label": "ID Separator",
      "rdfs:domain": "org:NamingConventions",
      "rdfs:range": "xsd:string",
      "schema:defaultValue": "-"
    },
    {
      "@id": "org:padding",
      "@type": "rdf:Property",
      "rdfs:label": "Number Padding",
      "rdfs:domain": "org:NamingConventions",
      "rdfs:range": "xsd:integer",
      "schema:defaultValue": 3
    },
    {
      "@id": "org:PriorityMapping",
      "@type": "rdfs:Class",
      "rdfs:label": "Priority Mapping",
      "rdfs:comment": "Keywords for automatic priority detection"
    },
    {
      "@id": "org:priorityMapping",
      "@type": "rdf:Property",
      "rdfs:label": "Priority Mapping",
      "rdfs:domain": "org:OrganizationContext",
      "rdfs:range": "org:PriorityMapping"
    },
    {
      "@id": "org:mustKeywords",
      "@type": "rdf:Property",
      "rdfs:label": "MUST Priority Keywords",
      "rdfs:domain": "org:PriorityMapping",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "org:shouldKeywords",
      "@type": "rdf:Property",
      "rdfs:label": "SHOULD Priority Keywords",
      "rdfs:domain": "org:PriorityMapping",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "org:couldKeywords",
      "@type": "rdf:Property",
      "rdfs:label": "COULD Priority Keywords",
      "rdfs:domain": "org:PriorityMapping",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "org:RiskThresholds",
      "@type": "rdfs:Class",
      "rdfs:label": "Risk Thresholds",
      "rdfs:comment": "Risk assessment thresholds and indicators"
    },
    {
      "@id": "org:riskThresholds",
      "@type": "rdf:Property",
      "rdfs:label": "Risk Thresholds",
      "rdfs:domain": "org:OrganizationContext",
      "rdfs:range": "org:RiskThresholds"
    },
    {
      "@id": "org:highComplexityIndicators",
      "@type": "rdf:Property",
      "rdfs:label": "High Complexity Indicators",
      "rdfs:domain": "org:RiskThresholds",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "org:timelineRedFlags",
      "@type": "rdf:Property",
      "rdfs:label": "Timeline Red Flags",
      "rdfs:domain": "org:RiskThresholds",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "org:resourceConstraints",
      "@type": "rdf:Property",
      "rdfs:label": "Resource Constraint Indicators",
      "rdfs:domain": "org:RiskThresholds",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "org:highRiskScoreThreshold",
      "@type": "rdf:Property",
      "rdfs:label": "High Risk Score Threshold",
      "rdfs:domain": "org:RiskThresholds",
      "rdfs:range": "xsd:decimal",
      "schema:minValue": 0.0,
      "schema:maxValue": 1.0
    }
  ]
}
```

---

### 2. Domain Knowledge Schema

**File:** `domain_knowledge_schema.jsonld`

**Purpose:** Defines industry-specific terminology, acronyms, and technology glossaries.

```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "rfp": "https://ibm.com/context-studio/rfp-analyzer/",
    "domain": "https://ibm.com/context-studio/domain/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "skos": "http://www.w3.org/2004/02/skos/core#"
  },
  "@graph": [
    {
      "@id": "domain:DomainKnowledge",
      "@type": "rdfs:Class",
      "rdfs:label": "Domain Knowledge",
      "rdfs:comment": "Industry-specific knowledge and terminology",
      "rdfs:subClassOf": "skos:ConceptScheme"
    },
    {
      "@id": "domain:industryDomain",
      "@type": "rdf:Property",
      "rdfs:label": "Industry Domain",
      "rdfs:domain": "domain:DomainKnowledge",
      "rdfs:range": "xsd:string",
      "schema:description": "Industry sector (Healthcare, Finance, Retail, etc.)"
    },
    {
      "@id": "domain:version",
      "@type": "rdf:Property",
      "rdfs:label": "Version",
      "rdfs:domain": "domain:DomainKnowledge",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "domain:lastUpdated",
      "@type": "rdf:Property",
      "rdfs:label": "Last Updated",
      "rdfs:domain": "domain:DomainKnowledge",
      "rdfs:range": "xsd:date"
    },
    {
      "@id": "domain:Term",
      "@type": "rdfs:Class",
      "rdfs:label": "Industry Term",
      "rdfs:comment": "Industry-specific term with definition",
      "rdfs:subClassOf": "skos:Concept"
    },
    {
      "@id": "domain:term",
      "@type": "rdf:Property",
      "rdfs:label": "Term",
      "rdfs:domain": "domain:Term",
      "rdfs:range": "xsd:string",
      "schema:required": true
    },
    {
      "@id": "domain:definition",
      "@type": "rdf:Property",
      "rdfs:label": "Definition",
      "rdfs:domain": "domain:Term",
      "rdfs:range": "xsd:string",
      "schema:required": true
    },
    {
      "@id": "domain:category",
      "@type": "rdf:Property",
      "rdfs:label": "Category",
      "rdfs:domain": "domain:Term",
      "rdfs:range": "xsd:string",
      "schema:description": "Category or domain area (e.g., Healthcare IT, Security, Cloud)"
    },
    {
      "@id": "domain:aliases",
      "@type": "rdf:Property",
      "rdfs:label": "Aliases",
      "rdfs:domain": "domain:Term",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "domain:relatedTerms",
      "@type": "rdf:Property",
      "rdfs:label": "Related Terms",
      "rdfs:domain": "domain:Term",
      "rdfs:range": "domain:Term",
      "schema:multipleValues": true
    },
    {
      "@id": "domain:Acronym",
      "@type": "rdfs:Class",
      "rdfs:label": "Acronym",
      "rdfs:comment": "Acronym with expansion and context"
    },
    {
      "@id": "domain:acronym",
      "@type": "rdf:Property",
      "rdfs:label": "Acronym",
      "rdfs:domain": "domain:Acronym",
      "rdfs:range": "xsd:string",
      "schema:required": true
    },
    {
      "@id": "domain:expansion",
      "@type": "rdf:Property",
      "rdfs:label": "Expansion",
      "rdfs:domain": "domain:Acronym",
      "rdfs:range": "xsd:string",
      "schema:required": true
    },
    {
      "@id": "domain:context",
      "@type": "rdf:Property",
      "rdfs:label": "Context",
      "rdfs:domain": "domain:Acronym",
      "rdfs:range": "xsd:string",
      "schema:description": "Context where acronym is used"
    },
    {
      "@id": "domain:TechnologyGlossary",
      "@type": "rdfs:Class",
      "rdfs:label": "Technology Glossary Entry",
      "rdfs:comment": "Technology term with explanation and usage"
    },
    {
      "@id": "domain:technology",
      "@type": "rdf:Property",
      "rdfs:label": "Technology Name",
      "rdfs:domain": "domain:TechnologyGlossary",
      "rdfs:range": "xsd:string",
      "schema:required": true
    },
    {
      "@id": "domain:explanation",
      "@type": "rdf:Property",
      "rdfs:label": "Explanation",
      "rdfs:domain": "domain:TechnologyGlossary",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "domain:usageContext",
      "@type": "rdf:Property",
      "rdfs:label": "Usage Context",
      "rdfs:domain": "domain:TechnologyGlossary",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "domain:preferredVersion",
      "@type": "rdf:Property",
      "rdfs:label": "Preferred Version",
      "rdfs:domain": "domain:TechnologyGlossary",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "domain:VendorPreference",
      "@type": "rdfs:Class",
      "rdfs:label": "Vendor Preference",
      "rdfs:comment": "Preferred vendor or partner"
    },
    {
      "@id": "domain:vendorName",
      "@type": "rdf:Property",
      "rdfs:label": "Vendor Name",
      "rdfs:domain": "domain:VendorPreference",
      "rdfs:range": "xsd:string",
      "schema:required": true
    },
    {
      "@id": "domain:category",
      "@type": "rdf:Property",
      "rdfs:label": "Vendor Category",
      "rdfs:domain": "domain:VendorPreference",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "domain:preferenceLevel",
      "@type": "rdf:Property",
      "rdfs:label": "Preference Level",
      "rdfs:domain": "domain:VendorPreference",
      "rdfs:range": "xsd:string",
      "schema:enumValues": ["preferred", "approved", "acceptable"]
    }
  ]
}
```

---

### 3. Standards Document Schema

**File:** `standards_schema.jsonld`

**Purpose:** Defines organizational standards documents (coding, security, architecture, etc.).

```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "rfp": "https://ibm.com/context-studio/rfp-analyzer/",
    "std": "https://ibm.com/context-studio/standards/",
    "xsd": "http://www.w3.org/2001/XMLSchema#",
    "dcterms": "http://purl.org/dc/terms/"
  },
  "@graph": [
    {
      "@id": "std:StandardDocument",
      "@type": "rdfs:Class",
      "rdfs:label": "Standard Document",
      "rdfs:comment": "Organizational standard or guideline document",
      "rdfs:subClassOf": "schema:CreativeWork"
    },
    {
      "@id": "std:title",
      "@type": "rdf:Property",
      "rdfs:label": "Title",
      "rdfs:domain": "std:StandardDocument",
      "rdfs:range": "xsd:string",
      "schema:required": true
    },
    {
      "@id": "std:standardType",
      "@type": "rdf:Property",
      "rdfs:label": "Standard Type",
      "rdfs:domain": "std:StandardDocument",
      "rdfs:range": "xsd:string",
      "schema:enumValues": ["coding", "security", "architecture", "testing", "deployment", "documentation"]
    },
    {
      "@id": "std:version",
      "@type": "rdf:Property",
      "rdfs:label": "Version",
      "rdfs:domain": "std:StandardDocument",
      "rdfs:range": "xsd:string",
      "schema:required": true
    },
    {
      "@id": "std:status",
      "@type": "rdf:Property",
      "rdfs:label": "Status",
      "rdfs:domain": "std:StandardDocument",
      "rdfs:range": "xsd:string",
      "schema:enumValues": ["draft", "active", "deprecated", "archived"]
    },
    {
      "@id": "std:lastUpdated",
      "@type": "rdf:Property",
      "rdfs:label": "Last Updated",
      "rdfs:domain": "std:StandardDocument",
      "rdfs:range": "xsd:date"
    },
    {
      "@id": "std:classification",
      "@type": "rdf:Property",
      "rdfs:label": "Classification",
      "rdfs:domain": "std:StandardDocument",
      "rdfs:range": "xsd:string",
      "schema:enumValues": ["public", "internal", "confidential", "restricted"]
    },
    {
      "@id": "std:content",
      "@type": "rdf:Property",
      "rdfs:label": "Content",
      "rdfs:domain": "std:StandardDocument",
      "rdfs:range": "xsd:string",
      "schema:description": "Full content of the standard document in Markdown format"
    },
    {
      "@id": "std:summary",
      "@type": "rdf:Property",
      "rdfs:label": "Summary",
      "rdfs:domain": "std:StandardDocument",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "std:applicableLanguages",
      "@type": "rdf:Property",
      "rdfs:label": "Applicable Languages",
      "rdfs:domain": "std:StandardDocument",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true,
      "schema:description": "Programming languages this standard applies to"
    },
    {
      "@id": "std:applicableTechnologies",
      "@type": "rdf:Property",
      "rdfs:label": "Applicable Technologies",
      "rdfs:domain": "std:StandardDocument",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "std:Section",
      "@type": "rdfs:Class",
      "rdfs:label": "Standard Section",
      "rdfs:comment": "A section within a standard document"
    },
    {
      "@id": "std:sections",
      "@type": "rdf:Property",
      "rdfs:label": "Sections",
      "rdfs:domain": "std:StandardDocument",
      "rdfs:range": "std:Section",
      "schema:multipleValues": true
    },
    {
      "@id": "std:sectionTitle",
      "@type": "rdf:Property",
      "rdfs:label": "Section Title",
      "rdfs:domain": "std:Section",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "std:sectionContent",
      "@type": "rdf:Property",
      "rdfs:label": "Section Content",
      "rdfs:domain": "std:Section",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "std:sectionOrder",
      "@type": "rdf:Property",
      "rdfs:label": "Section Order",
      "rdfs:domain": "std:Section",
      "rdfs:range": "xsd:integer"
    },
    {
      "@id": "std:Rule",
      "@type": "rdfs:Class",
      "rdfs:label": "Standard Rule",
      "rdfs:comment": "A specific rule or requirement within a standard"
    },
    {
      "@id": "std:rules",
      "@type": "rdf:Property",
      "rdfs:label": "Rules",
      "rdfs:domain": "std:StandardDocument",
      "rdfs:range": "std:Rule",
      "schema:multipleValues": true
    },
    {
      "@id": "std:ruleId",
      "@type": "rdf:Property",
      "rdfs:label": "Rule ID",
      "rdfs:domain": "std:Rule",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "std:ruleDescription",
      "@type": "rdf:Property",
      "rdfs:label": "Rule Description",
      "rdfs:domain": "std:Rule",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "std:ruleSeverity",
      "@type": "rdf:Property",
      "rdfs:label": "Rule Severity",
      "rdfs:domain": "std:Rule",
      "rdfs:range": "xsd:string",
      "schema:enumValues": ["must", "should", "may"]
    },
    {
      "@id": "std:ruleExample",
      "@type": "rdf:Property",
      "rdfs:label": "Rule Example",
      "rdfs:domain": "std:Rule",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "std:relatedStandards",
      "@type": "rdf:Property",
      "rdfs:label": "Related Standards",
      "rdfs:domain": "std:StandardDocument",
      "rdfs:range": "std:StandardDocument",
      "schema:multipleValues": true
    },
    {
      "@id": "std:complianceFrameworks",
      "@type": "rdf:Property",
      "rdfs:label": "Compliance Frameworks",
      "rdfs:domain": "std:StandardDocument",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true,
      "schema:description": "External compliance frameworks this standard helps satisfy"
    }
  ]
}
```

---

### 4. Template Schema

**File:** `template_schema.jsonld`

**Purpose:** Defines reusable templates for proposals, responses, and documents.

```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "rfp": "https://ibm.com/context-studio/rfp-analyzer/",
    "tmpl": "https://ibm.com/context-studio/template/",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },
  "@graph": [
    {
      "@id": "tmpl:Template",
      "@type": "rdfs:Class",
      "rdfs:label": "Document Template",
      "rdfs:comment": "Reusable template for proposals and documents",
      "rdfs:subClassOf": "schema:CreativeWork"
    },
    {
      "@id": "tmpl:templateName",
      "@type": "rdf:Property",
      "rdfs:label": "Template Name",
      "rdfs:domain": "tmpl:Template",
      "rdfs:range": "xsd:string",
      "schema:required": true
    },
    {
      "@id": "tmpl:templateType",
      "@type": "rdf:Property",
      "rdfs:label": "Template Type",
      "rdfs:domain": "tmpl:Template",
      "rdfs:range": "xsd:string",
      "schema:enumValues": ["proposal_response", "technical_approach", "executive_summary", "cost_breakdown", "timeline", "team_composition"]
    },
    {
      "@id": "tmpl:version",
      "@type": "rdf:Property",
      "rdfs:label": "Version",
      "rdfs:domain": "tmpl:Template",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "tmpl:status",
      "@type": "rdf:Property",
      "rdfs:label": "Status",
      "rdfs:domain": "tmpl:Template",
      "rdfs:range": "xsd:string",
      "schema:enumValues": ["draft", "active", "archived"]
    },
    {
      "@id": "tmpl:content",
      "@type": "rdf:Property",
      "rdfs:label": "Template Content",
      "rdfs:domain": "tmpl:Template",
      "rdfs:range": "xsd:string",
      "schema:description": "Template content in Markdown format with placeholders"
    },
    {
      "@id": "tmpl:description",
      "@type": "rdf:Property",
      "rdfs:label": "Description",
      "rdfs:domain": "tmpl:Template",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "tmpl:applicableIndustries",
      "@type": "rdf:Property",
      "rdfs:label": "Applicable Industries",
      "rdfs:domain": "tmpl:Template",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "tmpl:Section",
      "@type": "rdfs:Class",
      "rdfs:label": "Template Section",
      "rdfs:comment": "A section within a template"
    },
    {
      "@id": "tmpl:sections",
      "@type": "rdf:Property",
      "rdfs:label": "Sections",
      "rdfs:domain": "tmpl:Template",
      "rdfs:range": "tmpl:Section",
      "schema:multipleValues": true
    },
    {
      "@id": "tmpl:sectionTitle",
      "@type": "rdf:Property",
      "rdfs:label": "Section Title",
      "rdfs:domain": "tmpl:Section",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "tmpl:sectionContent",
      "@type": "rdf:Property",
      "rdfs:label": "Section Content",
      "rdfs:domain": "tmpl:Section",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "tmpl:sectionOrder",
      "@type": "rdf:Property",
      "rdfs:label": "Section Order",
      "rdfs:domain": "tmpl:Section",
      "rdfs:range": "xsd:integer"
    },
    {
      "@id": "tmpl:isRequired",
      "@type": "rdf:Property",
      "rdfs:label": "Is Required",
      "rdfs:domain": "tmpl:Section",
      "rdfs:range": "xsd:boolean"
    },
    {
      "@id": "tmpl:Placeholder",
      "@type": "rdfs:Class",
      "rdfs:label": "Template Placeholder",
      "rdfs:comment": "A placeholder variable in the template"
    },
    {
      "@id": "tmpl:placeholders",
      "@type": "rdf:Property",
      "rdfs:label": "Placeholders",
      "rdfs:domain": "tmpl:Template",
      "rdfs:range": "tmpl:Placeholder",
      "schema:multipleValues": true
    },
    {
      "@id": "tmpl:placeholderName",
      "@type": "rdf:Property",
      "rdfs:label": "Placeholder Name",
      "rdfs:domain": "tmpl:Placeholder",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "tmpl:placeholderDescription",
      "@type": "rdf:Property",
      "rdfs:label": "Placeholder Description",
      "rdfs:domain": "tmpl:Placeholder",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "tmpl:placeholderType",
      "@type": "rdf:Property",
      "rdfs:label": "Placeholder Type",
      "rdfs:domain": "tmpl:Placeholder",
      "rdfs:range": "xsd:string",
      "schema:enumValues": ["text", "number", "date", "list", "table"]
    },
    {
      "@id": "tmpl:defaultValue",
      "@type": "rdf:Property",
      "rdfs:label": "Default Value",
      "rdfs:domain": "tmpl:Placeholder",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "tmpl:lastUpdated",
      "@type": "rdf:Property",
      "rdfs:label": "Last Updated",
      "rdfs:domain": "tmpl:Template",
      "rdfs:range": "xsd:date"
    },
    {
      "@id": "tmpl:createdBy",
      "@type": "rdf:Property",
      "rdfs:label": "Created By",
      "rdfs:domain": "tmpl:Template",
      "rdfs:range": "xsd:string"
    }
  ]
}
```

---

### 5. Historical RFP Schema

**File:** `historical_rfp_schema.jsonld`

**Purpose:** Defines structure for storing historical RFP examples and outcomes.

```json
{
  "@context": {
    "@vocab": "https://schema.org/",
    "rfp": "https://ibm.com/context-studio/rfp-analyzer/",
    "hist": "https://ibm.com/context-studio/historical/",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },
  "@graph": [
    {
      "@id": "hist:HistoricalRFP",
      "@type": "rdfs:Class",
      "rdfs:label": "Historical RFP",
      "rdfs:comment": "Past RFP with analysis and outcome data",
      "rdfs:subClassOf": "schema:CreativeWork"
    },
    {
      "@id": "hist:rfpId",
      "@type": "rdf:Property",
      "rdfs:label": "RFP ID",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:string",
      "schema:required": true
    },
    {
      "@id": "hist:title",
      "@type": "rdf:Property",
      "rdfs:label": "RFP Title",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:string",
      "schema:required": true
    },
    {
      "@id": "hist:clientName",
      "@type": "rdf:Property",
      "rdfs:label": "Client Name",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "hist:industry",
      "@type": "rdf:Property",
      "rdfs:label": "Industry",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "hist:submissionDate",
      "@type": "rdf:Property",
      "rdfs:label": "Submission Date",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:date"
    },
    {
      "@id": "hist:outcome",
      "@type": "rdf:Property",
      "rdfs:label": "Outcome",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:string",
      "schema:enumValues": ["won", "lost", "no_bid", "pending"]
    },
    {
      "@id": "hist:projectValue",
      "@type": "rdf:Property",
      "rdfs:label": "Project Value",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:decimal"
    },
    {
      "@id": "hist:currency",
      "@type": "rdf:Property",
      "rdfs:label": "Currency",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "hist:projectDuration",
      "@type": "rdf:Property",
      "rdfs:label": "Project Duration (months)",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:integer"
    },
    {
      "@id": "hist:teamSize",
      "@type": "rdf:Property",
      "rdfs:label": "Team Size",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:integer"
    },
    {
      "@id": "hist:content",
      "@type": "rdf:Property",
      "rdfs:label": "RFP Content",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:string",
      "schema:description": "Full RFP document content"
    },
    {
      "@id": "hist:summary",
      "@type": "rdf:Property",
      "rdfs:label": "Summary",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:string"
    },
    {
      "@id": "hist:technologies",
      "@type": "rdf:Property",
      "rdfs:label": "Technologies",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "hist:keyRequirements",
      "@type": "rdf:Property",
      "rdfs:label": "Key Requirements",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "hist:challenges",
      "@type": "rdf:Property",
      "rdfs:label": "Challenges",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "hist:lessonsLearned",
      "@type": "rdf:Property",
      "rdfs:label": "Lessons Learned",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "hist:successFactors",
      "@type": "rdf:Property",
      "rdfs:label": "Success Factors",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true,
      "schema:description": "Factors that contributed to winning (if won)"
    },
    {
      "@id": "hist:Analysis",
      "@type": "rdfs:Class",
      "rdfs:label": "RFP Analysis",
      "rdfs:comment": "Analysis results from the RFP analyzer"
    },
    {
      "@id": "hist:analysis",
      "@type": "rdf:Property",
      "rdfs:label": "Analysis",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "hist:Analysis"
    },
    {
      "@id": "hist:functionalRequirements",
      "@type": "rdf:Property",
      "rdfs:label": "Functional Requirements Count",
      "rdfs:domain": "hist:Analysis",
      "rdfs:range": "xsd:integer"
    },
    {
      "@id": "hist:nonFunctionalRequirements",
      "@type": "rdf:Property",
      "rdfs:label": "Non-Functional Requirements Count",
      "rdfs:domain": "hist:Analysis",
      "rdfs:range": "xsd:integer"
    },
    {
      "@id": "hist:complianceRequirements",
      "@type": "rdf:Property",
      "rdfs:label": "Compliance Requirements Count",
      "rdfs:domain": "hist:Analysis",
      "rdfs:range": "xsd:integer"
    },
    {
      "@id": "hist:ambiguities",
      "@type": "rdf:Property",
      "rdfs:label": "Ambiguities Count",
      "rdfs:domain": "hist:Analysis",
      "rdfs:range": "xsd:integer"
    },
    {
      "@id": "hist:risks",
      "@type": "rdf:Property",
      "rdfs:label": "Risks Count",
      "rdfs:domain": "hist:Analysis",
      "rdfs:range": "xsd:integer"
    },
    {
      "@id": "hist:complexityScore",
      "@type": "rdf:Property",
      "rdfs:label": "Complexity Score",
      "rdfs:domain": "hist:Analysis",
      "rdfs:range": "xsd:decimal",
      "schema:minValue": 0.0,
      "schema:maxValue": 1.0
    },
    {
      "@id": "hist:tags",
      "@type": "rdf:Property",
      "rdfs:label": "Tags",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "xsd:string",
      "schema:multipleValues": true
    },
    {
      "@id": "hist:relatedRFPs",
      "@type": "rdf:Property",
      "rdfs:label": "Related RFPs",
      "rdfs:domain": "hist:HistoricalRFP",
      "rdfs:range": "hist:HistoricalRFP",
      "schema:multipleValues": true
    }
  ]
}
```

---

## Sample Data Files

### Sample: Organization Configuration Data

**File:** `organization_data.jsonld`

```json
{
  "@context": "https://ibm.com/context-studio/organization/context.jsonld",
  "@type": "org:OrganizationContext",
  "@id": "org:ibm-consulting",
  "org:name": "IBM Consulting",
  "org:industry": "Consulting",
  "org:description": "IBM Consulting organizational context for RFP analysis",
  "org:techStack": {
    "@type": "org:TechStack",
    "org:preferredLanguages": ["Python", "TypeScript", "Java"],
    "org:cloudProviders": ["AWS", "Azure"],
    "org:databases": ["PostgreSQL", "MongoDB"],
    "org:frameworks": ["FastAPI", "React", "Django"],
    "org:architecturePatterns": ["Microservices", "RESTful APIs", "Event-Driven"]
  },
  "org:compliance": {
    "@type": "org:ComplianceRequirements",
    "org:complianceFrameworks": ["GDPR", "SOC2"],
    "org:certifications": ["ISO 27001"],
    "org:standards": ["OWASP Top 10"]
  },
  "org:namingConventions": {
    "@type": "org:NamingConventions",
    "org:requirementPrefix": "REQ",
    "org:functionalPrefix": "IBM-FR",
    "org:nonFunctionalPrefix": "NFR",
    "org:compliancePrefix": "CR",
    "org:separator": "-",
    "org:padding": 3
  },
  "org:priorityMapping": {
    "@type": "org:PriorityMapping",
    "org:mustKeywords": ["shall", "must", "required", "mandatory"],
    "org:shouldKeywords": ["should", "recommended", "preferred"],
    "org:couldKeywords": ["may", "could", "optional"]
  },
  "org:riskThresholds": {
    "@type": "org:RiskThresholds",
    "org:highComplexityIndicators": ["AI/ML", "machine learning", "blockchain", "real-time", "distributed system"],
    "org:timelineRedFlags": ["< 3 months", "immediate", "urgent", "ASAP"],
    "org:resourceConstraints": ["limited budget", "small team"],
    "org:highRiskScoreThreshold": 0.7
  }
}
```

### Sample: Domain Knowledge Data

**File:** `healthcare_domain_knowledge.jsonld`

```json
{
  "@context": "https://ibm.com/context-studio/domain/context.jsonld",
  "@type": "domain:DomainKnowledge",
  "@id": "domain:healthcare-it",
  "domain:industryDomain": "Healthcare IT",
  "domain:version": "1.0",
  "domain:lastUpdated": "2026-04-01",
  "domain:terms": [
    {
      "@type": "domain:Term",
      "@id": "domain:term-hl7",
      "domain:term": "HL7",
      