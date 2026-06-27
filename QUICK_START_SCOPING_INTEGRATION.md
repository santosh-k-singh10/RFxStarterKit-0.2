# Quick Start: Scoping Architect Integration

## Prerequisites

1. Both services must be running:
   - **RFP Analyzer**: Port 8000
   - **Scoping Architect**: Port 8001

## Starting the Services

### Terminal 1: Start Scoping Architect
```bash
cd scoping-architect
uvicorn app:create_app --factory --reload --port 8001
```

### Terminal 2: Start RFP Analyzer
```bash
cd rfp-analyzer/analyzer
python web_app.py
```

## Testing the Integration

### 1. Access RFP Analyzer
Open your browser to: `http://localhost:8000`

### 2. Test Scoping Questionnaire Tab
1. Click on the **"🏗️ Scoping Questionnaire"** tab
2. You should see the Scoping Architect homepage embedded in an iframe
3. The form should be fully interactive within the RFP Analyzer interface

**Expected Result:**
- The Scoping Architect preferences form loads inside the RFP Analyzer
- You can fill out architecture preferences without leaving the page
- All form interactions work normally

### 3. Test Generate Scope Tab
1. First, upload and analyze an RFP document in the Home tab
2. Click on the **"🔍 Generate Scope"** tab
3. You'll see two buttons:
   - **"🌉 Open RFP-to-GSE Bridge"** - Opens bridge in new window
   - **"🚀 Generate Architecture Scope"** - Generates scope from requirements

**Expected Result:**
- Bridge button opens `http://localhost:8001/bridge` in a new window
- Generate Scope button calls the scoping-architect API
- Results display with component count and risk assessment

## Troubleshooting

### Issue: Iframe shows "Connection Refused"
**Solution:**
```bash
# Check if scoping-architect is running
curl http://localhost:8001/

# If not running, start it:
cd scoping-architect
uvicorn app:create_app --factory --reload --port 8001
```

### Issue: Generate Scope button shows error
**Solution:**
1. Ensure you've analyzed an RFP first (currentJobId must be set)
2. Check that scoping-architect API is accessible:
```bash
curl http://localhost:8001/api/health
```

### Issue: CORS errors in browser console
**Solution:**
Both services have CORS enabled for `*` origins. If you still see errors:
1. Check browser console for specific error
2. Verify both services are running on correct ports
3. Try accessing each service directly to confirm they're working

## Verification Checklist

- [ ] Scoping Architect running on port 8001
- [ ] RFP Analyzer running on port 8000
- [ ] Can access http://localhost:8000
- [ ] Can access http://localhost:8001
- [ ] Scoping Questionnaire tab shows embedded form
- [ ] Form is interactive and responsive
- [ ] Bridge button opens new window
- [ ] Generate Scope button works after RFP analysis

## API Endpoints

### RFP Analyzer Proxy Endpoints
- `GET /api/scoping/health` - Check scoping-architect availability
- `POST /api/scoping/analyze` - Generate architecture scope
- `POST /api/scoping/preferences` - Validate preferences
- `GET /api/scoping/bridge/{job_id}` - Get bridge data

### Direct Scoping Architect Endpoints
- `GET http://localhost:8001/` - Homepage (embedded in iframe)
- `GET http://localhost:8001/bridge` - RFP-to-GSE Bridge
- `POST http://localhost:8001/api/analyze` - Architecture analysis
- `GET http://localhost:8001/docs` - API documentation

## Next Steps

After verifying the integration works:

1. **Upload a real RFP** and test the full workflow
2. **Configure architecture preferences** in the Scoping Questionnaire tab
3. **Generate scope** and review the results
4. **Use the bridge** to transfer data to GSE template

## Support

For detailed integration documentation, see:
- `SCOPING_ARCHITECT_INTEGRATION.md` - Complete integration guide
- `scoping-architect/README.md` - Scoping Architect documentation
- `rfp-analyzer/README.md` - RFP Analyzer documentation