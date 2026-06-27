# GSE Questionnaire - Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Start the Server

```bash
# From the project root directory
python run.py
```

The server will start on `http://localhost:8000`

### Step 2: Access the Form

Open your browser and navigate to:
```
http://localhost:8000/GSE
```

### Step 3: Fill Out the Questionnaire

Navigate through the 9 sections using the tabs or Previous/Next buttons:

1. **Application Scope** - Select SAP S/4HANA and relevant modules
2. **Geographical Scope** - Enter organizational metrics
3. **Process Scope** - Select business processes (L1/L2/L3)
4. **Application Development** - Define WRICEF and Fiori scope
5. **Data Conversion** - Specify data migration needs
6. **Testing** - Configure testing requirements
7. **Infrastructure** - Set up security and infrastructure
8. **Change Management** - Define OCM and training scope
9. **Implementation** - Set project timeline and rollout plan

Click **Submit Questionnaire** on the final section.

## 📋 Sample Data for Testing

### Section 1: Application Scope
- Standard Applications: ✓ SAP S/4HANA
- Module Scope: ✓ FI, ✓ CO, ✓ SD, ✓ MM

### Section 2: Geographical Scope
- No. of Countries: `5`
- No. of Company Codes: `10`
- No. of Plants: `15`
- No. of Divisions: `3`
- Company Revenue: `$1B-$5B USD`
- Core Users: `2000`
- Project Language: `English`
- Rollout In Scope: `Yes`

### Section 3: Process Scope
- BPH Model: `IMPACT BPH`
- IBM Impact Solution - Primary: `SAP S/4HANA Finance`
- L1 Processes: ✓ Record to Report, ✓ Order To Cash

### Section 4: Application Development
- WRICEF In Scope: `Yes`
- Pilot Scope:
  - S/4 Reports: `15`
  - S/4 Interfaces: `10`
  - BTP Interfaces: `25`
  - Conversions: `20`
  - Enhancements: `25`
  - Forms: `20`
- Integration Layer Type: `BTP`

### Section 5: Data Conversion
- Data Conversion In Scope: `Yes`
- Data Migration Tool: `DMC`
- No. of Data Objects: `50`
- No. of Load Cycles: `4`
- No. of Source Systems: `1`

### Section 6: Testing
- Automation Testing In Scope: `Yes`
  - Test Scenarios - SAP GUI: `50`
  - Test Scenarios - Web/Fiori: `25`
- SIT Testing In Scope: `Yes`
  - Test Scenarios - Creation: `500`
  - SIT Cycles: `2`

### Section 7: Infrastructure
- Security In Scope: `Yes`
  - No. of End Users: `2000`
  - No. of L3 Processes: `50`

### Section 8: Change Management
- Change Management In Scope: `Yes`
  - IBM Involvement: `Full`
- Training In Scope: `Yes`
  - Training Approach: `Train The Trainer [TTT]`
  - Target Trainees: `500`

### Section 9: Implementation
- Project Start Date: `2026-02-01`
- Timeline Given by Client: `Yes`
- Rollout Type: `Geographical`
- No. of Rollouts Planned: `5`

## 🔍 Viewing Saved Questionnaires

### Via API

```bash
# List all questionnaires
curl http://localhost:8000/api/GSE/questionnaires

# Get specific questionnaire
curl http://localhost:8000/api/GSE/questionnaire/GSE_20260608_120000
```

### Via File System

Questionnaires are saved in:
```
outputs/GSE-questionnaires/GSE_YYYYMMDD_HHMMSS.json
```

## 🧪 Testing the API

### Using cURL

```bash
# Submit a questionnaire
curl -X POST http://localhost:8000/api/GSE/submit \
  -H "Content-Type: application/json" \
  -d '{
    "application_scope": {
      "standard_applications": ["SAP S/4HANA"],
      "module_scope": ["FI", "CO"]
    },
    "geographical_scope": {
      "no_of_countries": 5,
      "no_of_company_codes": 10,
      "core_users": 2000,
      "company_revenue": "$1B-$5B USD",
      "project_language": "English",
      "rollout_in_scope": false
    }
  }'
```

### Using Python

```python
import requests

data = {
    "application_scope": {
        "standard_applications": ["SAP S/4HANA"],
        "module_scope": ["FI", "CO", "SD"]
    },
    "geographical_scope": {
        "no_of_countries": 5,
        "no_of_company_codes": 10,
        "core_users": 2000,
        "company_revenue": "$1B-$5B USD",
        "project_language": "English",
        "rollout_in_scope": True
    },
    # ... other sections
}

response = requests.post(
    "http://localhost:8000/api/GSE/submit",
    json=data
)

print(response.json())
```

## 📊 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/GSE` | Serve the questionnaire form |
| POST | `/api/GSE/submit` | Submit completed questionnaire |
| GET | `/api/GSE/questionnaire/{id}` | Retrieve specific questionnaire |
| GET | `/api/GSE/questionnaires` | List all questionnaires |
| GET | `/api/GSE/dropdown-options` | Get dropdown options |

## 🎯 Key Features

### Conditional Logic
- Fields automatically show/hide based on selections
- Example: WRICEF fields only appear when "WRICEF In Scope" = Yes

### Real-time Calculations
- Pilot WRICEF total updates as you enter values
- Automatic field validation

### Navigation
- Tab-based navigation between sections
- Previous/Next buttons
- Direct section access via tabs

### Validation
- Required fields marked with red asterisk (*)
- Numeric fields validate min/max values
- Form prevents submission until all required fields are filled

## 🐛 Troubleshooting

### Form Not Loading
- Check that the server is running: `python run.py`
- Verify the URL: `http://localhost:8000/GSE`
- Check browser console for errors (F12)

### Submission Fails
- Ensure all required fields are filled
- Check network tab in browser dev tools
- Verify API is accessible: `http://localhost:8000/docs`

### Data Not Saving
- Check `outputs/GSE-questionnaires/` directory exists
- Verify write permissions
- Check server logs for errors

## 📚 Additional Resources

- **Full Documentation**: See `README.md`
- **API Documentation**: `http://localhost:8000/docs`
- **Excel Template**: `Book6.xlsx` (reference)
- **Data Models**: `models.py`

## 💡 Tips

1. **Save Progress**: The form doesn't auto-save. Complete all sections before submitting.
2. **Required Fields**: Look for the red asterisk (*) to identify mandatory fields.
3. **Conditional Fields**: Some fields only appear based on your selections.
4. **Calculations**: WRICEF totals calculate automatically as you type.
5. **Navigation**: Use tabs to jump between sections quickly.

## 🎓 Next Steps

After submitting a questionnaire:

1. **Review Saved Data**: Check the JSON file in `outputs/GSE-questionnaires/`
2. **Integrate with Estimation**: Use the data for effort estimation
3. **Generate Reports**: Export to PDF or Excel (future enhancement)
4. **Track Changes**: Version control for questionnaire updates

## 📞 Support

For issues or questions:
- Check the main `README.md` for detailed documentation
- Review API docs at `/docs`
- Inspect saved questionnaires in `outputs/GSE-questionnaires/`