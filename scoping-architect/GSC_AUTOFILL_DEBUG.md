# GSE Auto-Fill Debugging Guide

## Issue
When clicking "Open Pre-filled GSE Form" from RFP_to_GSE_Bridge_v3.html, the GSE form at `http://localhost:8000/GSE` opens but data is not being populated.

## How It Should Work

### Data Flow
1. **RFP_to_GSE_Bridge_v3.html** (Upload & Extract)
   - User uploads enriched JSON with `scoping_metadata`
   - JavaScript extracts 47 fields from the JSON
   - Stores data in `localStorage` with key `GSE_prefill_data`

2. **Open GSE Form**
   - Opens `http://localhost:8000/GSE` in new tab
   - GSE form reads from `localStorage` on page load
   - Auto-fills all fields with extracted data
   - Shows success notification

3. **questionnaire_form.html** (Auto-Fill)
   - `window.addEventListener('DOMContentLoaded', applyPrefillData)` (line 697)
   - Reads `localStorage.getItem('GSE_prefill_data')` (line 504)
   - Populates form fields
   - Adds confidence badges
   - Clears localStorage after successful load (line 626)

## Debugging Steps

### Step 1: Verify Server is Running
```bash
# Check if server is running on port 8000
curl http://localhost:8000/GSE
```

Expected: HTML content of the GSE form

### Step 2: Check Browser Console
1. Open `RFP_to_GSE_Bridge_v3.html` in browser
2. Upload an enriched JSON file
3. Open Browser DevTools (F12)
4. Go to Console tab
5. Check for any JavaScript errors

### Step 3: Verify localStorage
After uploading JSON but BEFORE clicking "Open Pre-filled GSE Form":

1. Open Browser DevTools (F12)
2. Go to Application tab (Chrome) or Storage tab (Firefox)
3. Expand "Local Storage"
4. Click on the current domain
5. Look for key: `GSE_prefill_data`
6. Verify it contains JSON data with `data` and `confidence` properties

**Expected localStorage structure:**
```json
{
  "data": {
    "standard_applications": ["SAP S/4HANA"],
    "no_of_countries": 5,
    "no_of_company_codes": 5,
    ...
  },
  "confidence": {
    "standard_applications": "auto",
    "no_of_countries": "auto",
    ...
  },
  "timestamp": "2026-06-16T..."
}
```

### Step 4: Check GSE Form Console
After clicking "Open Pre-filled GSE Form":

1. In the NEW tab that opens (http://localhost:8000/GSE)
2. Open Browser DevTools (F12)
3. Go to Console tab
4. Look for these messages:
   - `🚀 Auto-filling GSE form with RFP data...` (line 512)
   - `✅ Auto-filled X fields from RFP analysis` (line 631)

### Step 5: Check for Cross-Origin Issues
If localStorage is not accessible, it might be a cross-origin issue:

**Problem:** `RFP_to_GSE_Bridge_v3.html` is opened as `file:///` but GSE form is at `http://localhost:8000/GSE`

**Solution:** Serve the Bridge HTML from the same server:

1. Copy `RFP_to_GSE_Bridge_v3.html` to a web-accessible location
2. Access it via `http://localhost:8000/bridge` instead of opening as a file

## Common Issues & Solutions

### Issue 1: localStorage is Empty
**Symptom:** No `GSE_prefill_data` key in localStorage after upload

**Causes:**
- JavaScript error during extraction
- JSON file doesn't have `scoping_metadata` section
- Browser blocking localStorage (privacy mode)

**Solution:**
- Check browser console for errors
- Verify JSON structure has `scoping_metadata` at root level
- Disable privacy/incognito mode

### Issue 2: Cross-Origin localStorage Access
**Symptom:** localStorage exists in Bridge but not accessible in GSE form

**Cause:** Bridge opened as `file:///` and GSE at `http://localhost:8000` are different origins

**Solution:** Serve Bridge from the same server

Add this route to `app.py`:
```python
@app.get("/bridge", response_class=HTMLResponse, include_in_schema=False)
async def serve_bridge() -> HTMLResponse:
    bridge_path = Path("RFP_to_GSE_Bridge_v3.html")
    if bridge_path.exists():
        return HTMLResponse(content=bridge_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Bridge not found</h1>", status_code=404)
```

Then access via: `http://localhost:8000/bridge`

### Issue 3: Data Clears Too Quickly
**Symptom:** localStorage is cleared before GSE form can read it

**Cause:** Line 626 in questionnaire_form.html clears localStorage immediately after reading

**Solution:** This is intentional (prevents stale data), but if debugging, comment out line 626 temporarily:
```javascript
// localStorage.removeItem('GSE_prefill_data');  // TEMP: Comment for debugging
```

### Issue 4: Field Names Don't Match
**Symptom:** Some fields populate, others don't

**Cause:** Field name mismatch between Bridge extraction and GSE form

**Solution:** Check field name mapping in both files:
- Bridge: Lines 164-290 in RFP_to_GSE_Bridge_v3.html
- GSE Form: Lines 560-623 in questionnaire_form.html

## Quick Fix: Serve Bridge from Server

The most reliable solution is to serve the Bridge HTML from the same server as the GSE form:

1. **Add route to app.py** (after line 879):
```python
# Serve RFP to GSE Bridge
@app.get("/bridge", response_class=HTMLResponse, include_in_schema=False)
async def serve_bridge() -> HTMLResponse:
    bridge_path = Path("RFP_to_GSE_Bridge_v3.html")
    if bridge_path.exists():
        return HTMLResponse(content=bridge_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>Bridge not found</h1>", status_code=404)
```

2. **Restart the server**:
```bash
# Stop current server (Ctrl+C)
# Start again
uvicorn app:app --reload --port 8000
```

3. **Access Bridge via server**:
```
http://localhost:8000/bridge
```

4. **Upload JSON and click "Open Pre-filled GSE Form"**
   - Both pages now share the same origin
   - localStorage will work correctly

## Testing the Fix

1. Navigate to `http://localhost:8000/bridge`
2. Upload your enriched JSON file (with `scoping_metadata`)
3. Verify stats show: X auto-filled, Y estimated, Z needs input
4. Click "🚀 Open Pre-filled GSE Form"
5. New tab opens at `http://localhost:8000/GSE`
6. Should see green notification: "✅ Auto-Fill Complete! X fields populated from RFP analysis"
7. Navigate through sections to verify data is populated
8. Look for colored confidence badges next to field labels:
   - Green (AUTO) = High confidence from RFP
   - Amber (ESTIMATED) = Calculated/derived value
   - Red (NEEDS-INPUT) = Missing from RFP

## Verification Checklist

- [ ] Server running on port 8000
- [ ] Can access `http://localhost:8000/GSE` directly
- [ ] Can access `http://localhost:8000/bridge` (after adding route)
- [ ] Upload JSON shows extraction stats
- [ ] localStorage contains `GSE_prefill_data` after upload
- [ ] GSE form opens in new tab
- [ ] Console shows "🚀 Auto-filling GSE form..."
- [ ] Console shows "✅ Auto-filled X fields..."
- [ ] Green notification appears on GSE form
- [ ] Fields are populated with data
- [ ] Confidence badges appear next to labels
- [ ] Conditional sections show/hide correctly

## Contact

If issue persists after following these steps, provide:
1. Browser console errors (from both Bridge and GSE form)
2. localStorage content (Application/Storage tab)
3. Network tab showing the /GSE request
4. Browser and version being used