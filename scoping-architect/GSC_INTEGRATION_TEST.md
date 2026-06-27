# GSE Integration Testing Guide

## Overview
This document provides test commands for the GSE (GreenStar Estimation Engine Input) pre-fill integration.

## Prerequisites
- Server running: `python run.py` (default port: 8000)
- Sample enriched JSON file with scoping_metadata

## Test Commands

### 1. Test GSE Pre-fill Endpoint

**Endpoint:** `POST /api/GSE/prefill`

**Description:** Accepts enriched JSON with scoping_metadata and returns GSE field mappings with confidence levels.

**Sample cURL Command:**

```bash
curl -X POST http://localhost:8000/api/GSE/prefill \
  -H "Content-Type: application/json" \
  -d @outputs/20260608_120308_the_system/architecture_enriched.json
```

**Expected Response Structure:**

```json
{
  "fields": {
    "no_of_countries": "3",
    "no_of_company_codes": "5",
    "no_of_plants": "12",
    "core_users": "250",
    "wricef_in_scope": "Yes",
    "pilot_s4_reports": "8",
    "data_conversion_in_scope": "Yes"
  },
  "confidence": {
    "no_of_countries": "auto",
    "no_of_company_codes": "auto",
    "no_of_plants": "estimated",
    "core_users": "needs-input",
    "wricef_in_scope": "auto",
    "pilot_s4_reports": "estimated",
    "data_conversion_in_scope": "auto"
  },
  "fill_summary": {
    "total_fields": 50,
    "auto_filled": 25,
    "estimated": 15,
    "needs_input": 10,
    "fill_rate_pct": 80.0
  }
}
```

### 2. Test Full Pipeline with Scoping Metadata

**Step 1: Analyze RFP (generates scoping_metadata)**

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "test_system",
    "requirements_text": "We need SAP S/4HANA implementation across 3 countries with 5 company codes. The system should support 250 core users. We require custom reports, data migration from legacy systems, and integration with external MES system.",
    "preferences": {
      "deployment_target": "cloud",
      "compliance_scope": ["GxP"],
      "integration_complexity": "medium"
    }
  }'
```

**Step 2: Extract scoping_metadata from response**

The response will include a `scoping_metadata` block that can be used for GSE pre-fill.

**Step 3: Use enriched JSON for GSE pre-fill**

```bash
# Save the enriched JSON from step 1 to a file
curl -X POST http://localhost:8000/api/GSE/prefill \
  -H "Content-Type: application/json" \
  -d @architecture_enriched.json
```

### 3. Test with Minimal JSON (Legacy Path)

If the JSON doesn't have scoping_metadata, the system falls back to pattern matching:

```bash
curl -X POST http://localhost:8000/api/GSE/prefill \
  -H "Content-Type: application/json" \
  -d '{
    "modules": {
      "Finance": [
        {
          "id": "FR-001",
          "title": "Multi-currency support",
          "description": "System must support 3 countries with different currencies",
          "type": "FR",
          "impl_type": "configuration"
        }
      ]
    }
  }'
```

### 4. Test Bridge HTML Application

**Open in Browser:**

```
file:///path/to/RFP_to_GSE_Bridge_v2.html
```

**Or serve via Python:**

```bash
cd /path/to/project
python -m http.server 8080
# Then open: http://localhost:8080/RFP_to_GSE_Bridge_v2.html
```

**Usage:**
1. Drag and drop an enriched JSON file
2. Review auto-filled fields (green), estimated fields (amber), and fields needing input (red)
3. Fill in missing fields
4. Export as JSON or open pre-filled form

## Validation Tests

### Test 1: Verify Scoping Metadata Extraction

```bash
# Check that /api/analyze includes scoping_metadata in response
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d @test_rfp.json | jq '.scoping_metadata'
```

**Expected:** Should return a structured object with geography, users, applications, etc.

### Test 2: Verify GSE Field Mapping

```bash
# Check that GSE endpoint returns proper field structure
curl -X POST http://localhost:8000/api/GSE/prefill \
  -H "Content-Type: application/json" \
  -d @architecture_enriched.json | jq '.fields | keys'
```

**Expected:** Should return array of GSE field names.

### Test 3: Verify Confidence Levels

```bash
# Check confidence distribution
curl -X POST http://localhost:8000/api/GSE/prefill \
  -H "Content-Type: application/json" \
  -d @architecture_enriched.json | jq '.fill_summary'
```

**Expected:** Should show fill_rate_pct > 0 and breakdown of auto/estimated/needs-input counts.

## Error Handling Tests

### Test Invalid JSON

```bash
curl -X POST http://localhost:8000/api/GSE/prefill \
  -H "Content-Type: application/json" \
  -d '{"invalid": "structure"}'
```

**Expected:** Should return 422 validation error or handle gracefully.

### Test Empty JSON

```bash
curl -X POST http://localhost:8000/api/GSE/prefill \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Expected:** Should return default/empty field mappings with needs-input confidence.

## Integration Workflow

**Complete End-to-End Test:**

```bash
# 1. Generate preferences
curl -X POST http://localhost:8000/api/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "deployment_target": "cloud",
    "compliance_scope": ["GxP"],
    "integration_complexity": "medium"
  }' > preferences.json

# 2. Analyze RFP with preferences
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "pharma_erp",
    "requirements_text": "SAP S/4HANA for pharmaceutical company across 3 countries...",
    "preferences": '$(cat preferences.json)'
  }' > architecture_enriched.json

# 3. Generate GSE pre-fill data
curl -X POST http://localhost:8000/api/GSE/prefill \
  -H "Content-Type: application/json" \
  -d @architecture_enriched.json > GSE_prefill.json

# 4. Review results
cat GSE_prefill.json | jq '.fill_summary'
```

## API Documentation

Once the server is running, access interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

Look for the "GSE Questionnaire" tag to see all GSE-related endpoints.

## Troubleshooting

### Issue: scoping_metadata not present in response

**Solution:** Ensure you're using the latest version of the enrichment pipeline. The scoping_metadata is added during Phase 1.5 enrichment.

### Issue: Low fill rate (<50%)

**Solution:** 
- Check that the input JSON has sufficient detail in requirements
- Use the Quick Fill modal in the bridge HTML to manually provide key fields
- Verify scoping_metadata block is present and populated

### Issue: Bridge HTML not loading JSON

**Solution:**
- Check browser console for errors
- Verify JSON is valid (use `jq . < file.json`)
- Ensure file has .json extension

## Success Criteria

✅ **Integration is working correctly if:**
1. `/api/analyze` returns enriched JSON with `scoping_metadata` block
2. `/api/GSE/prefill` accepts enriched JSON and returns field mappings
3. Fill rate is >70% for typical RFPs with scoping_metadata
4. Bridge HTML successfully loads and displays extracted fields
5. Confidence levels accurately reflect extraction quality

## Next Steps

After successful testing:
1. Integrate with actual GSE questionnaire system
2. Calibrate extraction patterns based on real RFP data
3. Add custom field mappings for organization-specific GSE fields
4. Set up automated testing in CI/CD pipeline