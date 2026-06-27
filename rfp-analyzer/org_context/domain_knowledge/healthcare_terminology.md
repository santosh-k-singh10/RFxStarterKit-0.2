# Healthcare Industry Terminology & Standards

## Version: 1.0
## Last Updated: 2026-04-01
## Domain: Healthcare IT

---

## Overview

This document provides healthcare-specific terminology, standards, and compliance requirements that Acme Corp encounters in healthcare IT projects. This knowledge helps in accurately interpreting RFPs from healthcare organizations.

## Healthcare IT Standards

### HL7 (Health Level 7)

#### HL7 v2.x
- **Purpose**: Electronic data exchange in healthcare
- **Common Messages**:
  - ADT (Admission, Discharge, Transfer)
  - ORM (Order Entry)
  - ORU (Observation Result)
  - SIU (Scheduling Information)
- **Format**: Pipe-delimited messages
- **Usage**: Legacy systems, lab interfaces

#### HL7 FHIR (Fast Healthcare Interoperability Resources)
- **Purpose**: Modern healthcare data exchange
- **Resources**: Patient, Observation, Medication, Encounter
- **Format**: JSON or XML over REST APIs
- **Versions**: R4 (current), R5 (upcoming)
- **Usage**: Modern EHR integrations, mobile health apps

### DICOM (Digital Imaging and Communications in Medicine)
- **Purpose**: Medical imaging data standard
- **Scope**: X-rays, CT scans, MRI, ultrasound
- **Components**: Image format, network protocol, metadata
- **Usage**: PACS systems, radiology workflows

### ICD-10 (International Classification of Diseases)
- **Purpose**: Diagnosis coding
- **Structure**: Alphanumeric codes (e.g., E11.9 for Type 2 diabetes)
- **Usage**: Medical billing, clinical documentation
- **Updates**: Annual updates from WHO

### CPT (Current Procedural Terminology)
- **Purpose**: Medical procedure coding
- **Maintained By**: American Medical Association
- **Structure**: 5-digit numeric codes
- **Usage**: Medical billing, procedure documentation

### SNOMED CT (Systematized Nomenclature of Medicine)
- **Purpose**: Clinical terminology
- **Scope**: Diseases, findings, procedures, body structures
- **Usage**: EHR systems, clinical decision support

### LOINC (Logical Observation Identifiers Names and Codes)
- **Purpose**: Laboratory and clinical observations
- **Usage**: Lab results, vital signs, clinical documents
- **Example**: 2345-7 (Glucose, serum)

## Healthcare Compliance & Regulations

### HIPAA (Health Insurance Portability and Accountability Act)

#### Privacy Rule
- **Protected Health Information (PHI)**: 18 identifiers
  - Names, addresses, dates (except year)
  - Phone numbers, email addresses
  - Medical record numbers
  - Social Security numbers
  - Biometric identifiers
  - Photos, IP addresses

#### Security Rule
- **Administrative Safeguards**:
  - Security management process
  - Workforce security
  - Information access management
  - Security awareness training

- **Physical Safeguards**:
  - Facility access controls
  - Workstation security
  - Device and media controls

- **Technical Safeguards**:
  - Access control (unique user IDs, emergency access)
  - Audit controls
  - Integrity controls
  - Transmission security (encryption)

#### Breach Notification Rule
- **Timeline**: Notify within 60 days of discovery
- **Threshold**: Breaches affecting 500+ individuals
- **Requirements**: Notify individuals, HHS, media (if applicable)

### HITECH Act
- **Purpose**: Promote EHR adoption
- **Meaningful Use**: Incentives for EHR usage
- **Breach Penalties**: Tiered penalty structure
- **Business Associate Agreements**: Required for vendors

### 21 CFR Part 11 (FDA Electronic Records)
- **Scope**: Electronic records and signatures
- **Requirements**:
  - Validation of systems
  - Audit trails
  - Electronic signatures
  - System access controls
- **Applicability**: Clinical trials, drug manufacturing

### GDPR (for EU patients)
- **Right to Access**: Patients can request their data
- **Right to Erasure**: "Right to be forgotten"
- **Data Portability**: Export data in machine-readable format
- **Consent**: Explicit consent required

## Healthcare Systems & Applications

### Electronic Health Record (EHR) Systems

#### Major Vendors
- **Epic**: Enterprise EHR, large hospitals
- **Cerner**: Hospital and ambulatory EHR
- **Allscripts**: Ambulatory and hospital EHR
- **Meditech**: Community hospital EHR
- **athenahealth**: Cloud-based ambulatory EHR

#### Core EHR Functions
- Patient demographics
- Clinical documentation
- Order entry (CPOE)
- Results review
- Clinical decision support
- E-prescribing

### Practice Management Systems (PMS)
- **Functions**:
  - Scheduling
  - Registration
  - Billing
  - Claims management
  - Payment posting

### Picture Archiving and Communication System (PACS)
- **Purpose**: Store and retrieve medical images
- **Components**:
  - Image acquisition
  - Secure storage
  - Retrieval and display
  - Integration with EHR

### Laboratory Information System (LIS)
- **Functions**:
  - Test ordering
  - Specimen tracking
  - Result reporting
  - Quality control

### Pharmacy Information System
- **Functions**:
  - Medication dispensing
  - Inventory management
  - Drug interaction checking
  - E-prescribing integration

## Healthcare Workflows

### Patient Registration
1. Demographic information collection
2. Insurance verification
3. Consent forms
4. Medical history intake
5. Assignment of medical record number (MRN)

### Clinical Documentation
1. Chief complaint
2. History of present illness (HPI)
3. Review of systems (ROS)
4. Physical examination
5. Assessment and plan
6. Orders and prescriptions

### Order-to-Result Workflow
1. Provider orders test/procedure
2. Order transmitted to department (lab, radiology)
3. Procedure performed
4. Results entered into system
5. Results reviewed by provider
6. Results communicated to patient

### Medication Management
1. Provider prescribes medication
2. Drug interaction check
3. Formulary check
4. E-prescription sent to pharmacy
5. Pharmacy dispenses medication
6. Medication administration (inpatient)
7. Medication reconciliation

## Healthcare Data Types

### Clinical Data
- **Structured Data**:
  - Vital signs (BP, HR, temp, SpO2)
  - Lab results
  - Medications
  - Allergies
  - Problem list
  - Immunizations

- **Unstructured Data**:
  - Clinical notes
  - Radiology reports
  - Pathology reports
  - Discharge summaries

### Administrative Data
- Patient demographics
- Insurance information
- Appointment schedules
- Billing codes
- Claims data

### Financial Data
- Charges
- Payments
- Adjustments
- Accounts receivable
- Denials and appeals

## Healthcare Interoperability

### Integration Patterns

#### Point-to-Point Integration
- Direct connection between two systems
- Custom interfaces
- Maintenance intensive

#### Interface Engine
- **Products**: Mirth Connect, Rhapsody, Cloverleaf
- **Benefits**: Centralized integration, message transformation
- **Protocols**: HL7 v2, FHIR, DICOM

#### API-Based Integration
- RESTful APIs
- FHIR resources
- OAuth 2.0 authentication
- Modern, scalable approach

### Common Integration Scenarios
1. **EHR ↔ Lab System**: Order transmission, result delivery
2. **EHR ↔ Pharmacy**: E-prescribing, medication history
3. **EHR ↔ PACS**: Order transmission, image viewing
4. **EHR ↔ Billing**: Charge capture, claim submission
5. **EHR ↔ HIE**: Patient data exchange across organizations

## Healthcare Analytics

### Clinical Analytics
- **Quality Measures**: HEDIS, CMS quality measures
- **Population Health**: Risk stratification, care gaps
- **Clinical Decision Support**: Evidence-based alerts
- **Outcomes Analysis**: Readmission rates, mortality rates

### Operational Analytics
- **Utilization**: Bed occupancy, OR utilization
- **Efficiency**: Wait times, length of stay
- **Productivity**: Provider productivity, staff ratios
- **Financial**: Revenue cycle, denials analysis

### Predictive Analytics
- **Risk Prediction**: Readmission risk, sepsis prediction
- **Resource Planning**: Capacity planning, staffing
- **Disease Progression**: Chronic disease management
- **Cost Prediction**: High-cost patient identification

## Healthcare Security & Privacy

### Access Control
- **Role-Based Access**: Physician, nurse, admin roles
- **Break-the-Glass**: Emergency access with audit
- **Minimum Necessary**: Access only what's needed
- **Audit Logging**: All PHI access logged

### Data Encryption
- **At Rest**: AES-256 encryption
- **In Transit**: TLS 1.3
- **Backup**: Encrypted backups
- **Mobile Devices**: Full device encryption

### De-identification
- **Safe Harbor Method**: Remove 18 HIPAA identifiers
- **Expert Determination**: Statistical method
- **Limited Data Set**: Partial de-identification
- **Usage**: Research, analytics, training

## Healthcare Payment Models

### Fee-for-Service (FFS)
- Payment per service/procedure
- Traditional model
- Volume-based

### Value-Based Care
- **Accountable Care Organizations (ACO)**: Shared savings
- **Bundled Payments**: Single payment for episode of care
- **Pay-for-Performance**: Quality-based incentives
- **Capitation**: Per-member-per-month payment

### Medicare/Medicaid
- **Medicare**: Federal program for 65+ and disabled
- **Medicaid**: State/federal program for low-income
- **Medicare Advantage**: Private Medicare plans
- **Dual Eligible**: Qualify for both programs

## Telehealth & Remote Care

### Telehealth Modalities
- **Synchronous**: Real-time video visits
- **Asynchronous**: Store-and-forward (e.g., dermatology images)
- **Remote Patient Monitoring**: Continuous monitoring devices
- **Mobile Health (mHealth)**: Smartphone apps

### Telehealth Requirements
- HIPAA-compliant video platform
- Informed consent
- State licensure compliance
- Reimbursement policies
- Technology access for patients

## Healthcare Quality & Safety

### Quality Measures
- **HEDIS**: Healthcare Effectiveness Data and Information Set
- **CMS Star Ratings**: Medicare Advantage quality ratings
- **PQRS**: Physician Quality Reporting System
- **Core Measures**: Hospital quality measures

### Patient Safety
- **Medication Reconciliation**: Accurate medication lists
- **Fall Prevention**: Risk assessment and interventions
- **Infection Control**: Hand hygiene, isolation protocols
- **Adverse Event Reporting**: Incident reporting systems

### Clinical Decision Support (CDS)
- **Drug Interaction Alerts**: Contraindications, allergies
- **Order Sets**: Evidence-based order templates
- **Clinical Guidelines**: Best practice recommendations
- **Risk Calculators**: Cardiovascular risk, bleeding risk

## Common Healthcare Acronyms

| Acronym | Full Term | Description |
|---------|-----------|-------------|
| ADT | Admission, Discharge, Transfer | Patient movement messages |
| CCM | Chronic Care Management | Medicare program for chronic conditions |
| CCDA | Consolidated Clinical Document Architecture | Standard for clinical document exchange |
| CDS | Clinical Decision Support | Computer-based support for clinical decisions |
| CPOE | Computerized Provider Order Entry | Electronic ordering system |
| EMR | Electronic Medical Record | Digital version of paper chart |
| EHR | Electronic Health Record | Comprehensive patient record |
| HIE | Health Information Exchange | Sharing health information across organizations |
| HIS | Hospital Information System | Comprehensive hospital IT system |
| MPI | Master Patient Index | Central patient identifier database |
| PACS | Picture Archiving and Communication System | Medical imaging system |
| PHI | Protected Health Information | Individually identifiable health information |
| RCM | Revenue Cycle Management | Financial process from registration to payment |
| RPM | Remote Patient Monitoring | Monitoring patients outside clinical settings |

## Healthcare Project Considerations

### Typical Requirements
- HIPAA compliance mandatory
- High availability (99.9%+ uptime)
- Disaster recovery (RTO < 4 hours)
- Audit logging of all PHI access
- Integration with existing EHR
- User training and change management
- Validation and testing documentation

### Common Challenges
- Legacy system integration
- Data migration complexity
- Clinician workflow disruption
- Regulatory compliance burden
- Interoperability limitations
- User adoption resistance

### Success Factors
- Clinical stakeholder engagement
- Workflow analysis and optimization
- Comprehensive training program
- Phased implementation approach
- Strong project governance
- Ongoing support and optimization

---

## References

- **HL7 International**: https://www.hl7.org/
- **FHIR Specification**: https://www.hl7.org/fhir/
- **HHS HIPAA**: https://www.hhs.gov/hipaa/
- **CMS**: https://www.cms.gov/
- **ONC (Office of the National Coordinator)**: https://www.healthit.gov/

## Document Control

- **Owner**: Healthcare Practice Lead
- **Review Cycle**: Quarterly
- **Next Review**: 2026-07-01
- **Contact**: healthcare@acme.com