# GSE Pre-Fill Usage Guide

## 🎯 How to Generate a Filled-in GSE Form

### Step 1: Run Your RFP Through the Pipeline

1. Start the server (if not already running):
   ```bash
   python run.py
   ```

2. Go to `http://localhost:8000/` and fill in your preferences

3. Upload your RFP JSON and click "Analyze"

4. The system will generate an **enriched JSON** file in the `outputs/` directory with a name like:
   ```
   outputs/YYYYMMDD_HHMMSS_projectname/architecture_enriched.json
   ```

### Step 2: Use the Bridge Tool to Pre-Fill GSE

1. **Open the Bridge HTML file** in your browser:
   ```
   file:///C:/Agents/scoping-architect/RFP_to_GSE_Bridge_v2.html
   ```
   
   Or simply double-click `RFP_to_GSE_Bridge_v2.html` in Windows Explorer

2. **Upload your enriched JSON**:
   - Drag and drop the `architecture_enriched.json` file onto the upload zone
   - OR click "Choose File" and select it

3. **Review the extraction**:
   - The tool will call the `/api/GSE/prefill` endpoint
   - You'll see statistics:
     - 🟢 **Auto-filled**: Fields extracted directly from your RFP
     - 🟡 **Estimated**: Fields calculated/inferred by the system
     - 🔴 **Needs Input**: Fields that require manual entry
   - A progress bar shows the overall fill rate

4. **Review and edit the form**:
   - All extracted fields are displayed in an editable form
   - Each field shows a badge indicating its source:
     - `AUTO` = Directly extracted
     - `EST` = Estimated/calculated
     - `USER` = Needs your input
   - Edit any fields as needed

5. **Export options**:
   - **Export JSON**: Download the pre-filled data as JSON
   - **Open Pre-filled Form**: Opens the full GSE questionnaire with all fields pre-populated

## 📊 What Gets Auto-Filled?

The system extracts **50+ parameters** including:

### Application Scope
- Standard applications (ECC, S/4HANA, etc.)
- Module scope (FI, CO, MM, SD, etc.)

### Geographical Scope
- Number of countries, company codes, plants
- Number of users (core and self-service)
- Languages and localization requirements

### Process Scope
- Business process hierarchy model
- Impact solutions (Greenfield, Brownfield, etc.)
- Process areas (R2R, O2C, P2P, P2M)

### Technical Scope
- Integration requirements
- Data migration scope
- Custom development needs

### Project Scope
- Timeline and phases
- Testing approach
- Training requirements

## 🔄 Complete Workflow

```
1. RFP JSON → RFP Analyzer (http://localhost:8000/)
   ↓
2. architecture_enriched.json generated
   ↓
3. Upload to Bridge Tool (RFP_to_GSE_Bridge_v2.html)
   ↓
4. System calls /api/GSE/prefill endpoint
   ↓
5. Review/edit pre-filled form
   ↓
6. Export or open full GSE questionnaire
```

## 🎨 Direct API Usage (Advanced)

If you want to call the API directly:

```bash
# Get pre-fill data from enriched JSON
curl -X POST http://localhost:8000/api/GSE/prefill \
  -H "Content-Type: application/json" \
  -d @outputs/YYYYMMDD_HHMMSS_projectname/architecture_enriched.json
```

Response includes:
```json
{
  "fields": {
    "no_of_countries": 5,
    "no_of_company_codes": 3,
    "core_users": 150,
    ...
  },
  "confidence": {
    "no_of_countries": "high",
    "no_of_company_codes": "medium",
    ...
  },
  "fill_summary": {
    "auto_filled": 35,
    "estimated": 12,
    "needs_input": 8,
    "fill_rate_pct": 85.5
  }
}
```

## 📁 Example Files

Find example enriched JSON files in:
```
outputs/20260613_231907_the_system/architecture_enriched.json
```

## 🆘 Troubleshooting

**Bridge tool not loading data?**
- Ensure the server is running at `http://localhost:8000`
- Check browser console for errors (F12)
- Verify the JSON file is a valid enriched output

**Low fill rate?**
- The system can only extract what's in your RFP
- More detailed RFPs = better extraction
- Review the "Needs Input" fields and fill them manually

**API returns 404?**
- Restart the server using `restart_server.bat`
- Verify the endpoint at `http://localhost:8000/docs`