# GSE - GreenStar Estimation Engine Input

A comprehensive web-based questionnaire for SAP implementation scoping and estimation, based on the GSE (GreenStar Estimation Engine Input) template.

## Overview

The GSE Questionnaire captures detailed information across 9 major sections to support accurate SAP implementation scoping and estimation:

1. **Application Scope** - Applications and modules in scope
2. **Geographical/Organization Scope** - Organizational boundaries and scale
3. **Business Process Scope** - Process hierarchies (L1/L2/L3)
4. **Application Development Scope** - WRICEF, Fiori, and Analytics
5. **Data Conversion Scope** - Data migration requirements
6. **Testing Scope** - Automation, Integration, Regression, Performance testing
7. **Infrastructure & Authorization Scope** - Infrastructure and security requirements
8. **Change Management & Training Scope** - OCM and training needs
9. **Implementation Scope** - Timeline and rollout strategy

## Files

### Core Files

- **`questionnaire_form.html`** - Interactive web form with all 9 sections
- **`models.py`** - Python data models for questionnaire structure
- **`Book6.xlsx`** - Original Excel template (reference)

### API Files

- **`GSE_template_api.py`** - FastAPI router with endpoints:
  - `POST /api/GSE/submit` - Submit completed questionnaire
  - `GET /api/GSE/questionnaire/{id}` - Retrieve saved questionnaire
  - `GET /api/GSE/questionnaires` - List all questionnaires
  - `GET /api/GSE/dropdown-options` - Get dropdown options

## Usage

### Accessing the Form

1. Start the application:
   ```bash
   python run.py
   ```

2. Open your browser to:
   ```
   http://localhost:8000/GSE
   ```

### Form Features

- **9 Tabbed Sections** - Navigate between sections using tabs or Previous/Next buttons
- **Conditional Fields** - Fields appear/hide based on selections
- **Real-time Calculations** - Automatic totals for WRICEF objects
- **Validation** - Required fields marked with red asterisk (*)
- **Responsive Design** - Works on desktop, tablet, and mobile

### API Integration

#### Submit Questionnaire

```javascript
const response = await fetch('/api/GSE/submit', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(questionnaireData)
});

const result = await response.json();
console.log('Questionnaire ID:', result.questionnaire_id);
```

#### Retrieve Questionnaire

```javascript
const response = await fetch('/api/GSE/questionnaire/GSE_20260608_120000');
const data = await response.json();
```

#### List All Questionnaires

```javascript
const response = await fetch('/api/GSE/questionnaires');
const data = await response.json();
console.log('Total questionnaires:', data.count);
```

## Data Structure

### Section 1: Application Scope

```json
{
  "standard_applications": ["SAP S/4HANA", "Salesforce Cloud"],
  "additional_applications": "Custom ERP",
  "module_scope": ["FI", "CO", "SD", "MM"]
}
```

### Section 2: Geographical Scope

```json
{
  "no_of_countries": 5,
  "no_of_company_codes": 10,
  "no_of_plants": 15,
  "core_users": 2000,
  "company_revenue": "$1B-$5B USD",
  "rollout_in_scope": true
}
```

### Section 4: WRICEF Scope

```json
{
  "wricef_in_scope": true,
  "pilot_scope": {
    "s4_reports": 15,
    "s4_abap_interfaces": 10,
    "end_to_end_btp_interfaces": 25,
    "s4_conversions": 20,
    "s4_enhancements": 25,
    "s4_forms": 20,
    "s4_workflows": 5
  }
}
```

## Field Types

- **Text** - Free text input
- **Number** - Numeric input with validation
- **Dropdown** - Single selection from predefined options
- **Multi-select** - Multiple selections (checkboxes)
- **Date** - Date picker
- **Percentage** - 0-100% with decimal support
- **Yes/No** - Boolean dropdown

## Validation Rules

### Mandatory Fields (M)

- Application Scope: Standard applications, Module scope
- Geographical Scope: Countries, Company codes, Plants, Divisions, Revenue, Core users, Language, Rollout
- Process Scope: BPH model, Impact solution primary
- Development: WRICEF in scope, Integration layer type
- Data Conversion: Data conversion in scope
- Implementation: Project start date, Timeline given by client

### Optional Fields (O)

- Most numeric counts (States, Channels, Currencies, etc.)
- Additional text descriptions
- Secondary selections

### Conditional Fields

Fields that appear based on other selections:

- **WRICEF fields** - Shown when "WRICEF In Scope" = Yes
- **Data conversion fields** - Shown when "Data Conversion In Scope" = Yes
- **Testing fields** - Shown when respective testing type = Yes
- **Security fields** - Shown when "Security In Scope" = Yes
- **OCM fields** - Shown when "Change Management In Scope" = Yes
- **Training fields** - Shown when "Training In Scope" = Yes

## Output

Submitted questionnaires are saved to:
```
outputs/GSE-questionnaires/GSE_YYYYMMDD_HHMMSS.json
```

Each file contains:
- Complete questionnaire data
- Questionnaire ID
- Submission timestamp
- All field values

## Integration with Estimation

The GSE questionnaire data can be used as input for:

1. **Effort Estimation** - WRICEF counts, testing scope, data objects
2. **Resource Planning** - User counts, team size, rollout phases
3. **Timeline Estimation** - Project start date, rollout count, phase durations
4. **Cost Estimation** - Scope complexity, compliance requirements

## Customization

### Adding New Fields

1. Update `models.py` with new data class fields
2. Add field to `questionnaire_form.html` in appropriate section
3. Update `GSE_template_api.py` Pydantic models for validation
4. Update dropdown options in `/api/GSE/dropdown-options` if needed

### Modifying Dropdown Options

Edit the `get_dropdown_options()` function in `GSE_template_api.py`:

```python
@router.get("/dropdown-options")
async def get_dropdown_options():
    return {
        "your_field": ["Option 1", "Option 2", "Option 3"]
    }
```

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Dependencies

- **Backend**: FastAPI, Pydantic
- **Frontend**: Bootstrap 5.3, Vanilla JavaScript
- **Storage**: JSON files (can be extended to database)

## Future Enhancements

- [ ] Database integration (PostgreSQL/MongoDB)
- [ ] PDF export of completed questionnaires
- [ ] Excel import/export
- [ ] Questionnaire templates
- [ ] Approval workflow
- [ ] Version control for questionnaires
- [ ] Analytics dashboard
- [ ] Integration with estimation engine

## Support

For issues or questions:
1. Check the Excel template (`Book6.xlsx`) for field definitions
2. Review API documentation at `/docs`
3. Check saved questionnaires in `outputs/GSE-questionnaires/`

## License

Internal use only - IBM Consulting