# Scoping Architect Integration Guide

## Overview

This document describes the integration between the RFP Analyzer and Scoping Architect systems. The integration enables seamless workflow from RFP analysis to architecture scoping and GSE (Global Scoping Calculator) template population.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      RFP Analyzer (Port 8000)                    │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Home Tab   │  │Requirements  │  │   Scoping    │          │
│  │  (Upload)    │→ │     Tab      │→ │ Questionnaire│          │
│  └──────────────┘  └──────────────┘  │     Tab      │          │
│                                       │  (iframe to  │          │
│                                       │   port 8001) │          │
│                                       └──────┬───────┘          │
│                                              │                   │
│                    ┌─────────────────────────┘                  │
│                    ↓                                             │
│           ┌──────────────────┐                                  │
│           │  Generate Scope  │                                  │
│           │       Tab        │                                  │
│           │                  │                                  │
│           │  • Bridge Button │                                  │
│           │  • Generate Arch │                                  │
│           │  • Map Solutions │                                  │
│           └────────┬─────────┘                                  │
└────────────────────┼──────────────────────────────────────────┘
                     │
                     │ HTTP Proxy
                     ↓
┌─────────────────────────────────────────────────────────────────┐
│                 Scoping Architect (Port 8001)                    │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Homepage   │  │  GSE Bridge  │  │  API Routes  │          │
│  │      /       │  │   /bridge    │  │  /api/*      │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

## Integration Points

### 1. Scoping Questionnaire Tab

**Location:** RFP Analyzer → Scoping Questionnaire Tab

**Implementation:**
- Embeds Scoping Architect homepage via iframe
- URL: `http://localhost:8001/`
- Allows users to configure architecture preferences directly within RFP Analyzer

**File:** `rfp-analyzer/analyzer/app/templates/unified.html` (lines 153-162)

```html
<iframe id="scopingArchitectFrame" 
        src="http://localhost:8001/" 
        style="width: 100%; height: 800px; border: 1px solid var(--border); border-radius: 8px;">
</iframe>
```

### 2. Generate Scope Tab

**Location:** RFP Analyzer → Generate Scope Tab

**Features:**
1. **RFP-to-GSE Bridge Button**
   - Opens bridge interface in new window
   - URL: `http://localhost:8001/bridge`
   - Allows manual transfer of requirements to GSE template

2. **Generate Architecture Scope Button**
   - Calls Scoping Architect API with analyzed requirements
   - Endpoint: `POST /api/scoping/analyze`
   - Returns architecture components, risks, and artifacts

3. **Solution Mapping**
   - Maps requirements to selected solutions (SAP, Oracle, Salesforce, etc.)
   - Provides visual feedback on mapping results

**File:** `rfp-analyzer/analyzer/app/templates/unified.html` (lines 160-216)

### 3. API Proxy Routes

**Location:** `rfp-analyzer/analyzer/web_app.py` (lines 1859-1977)

#### Health Check
```
GET /api/scoping/health
```
Checks if Scoping Architect service is available.

#### Architecture Analysis
```
POST /api/scoping/analyze
```
Proxies architecture generation requests to Scoping Architect.

**Request Body:**
```json
{
  "job_id": "uuid",
  "project_name": "RFP Analysis",
  "requirements": [...],
  "preferences": {
    "approach": "greenfield",
    "deployment": "cloud",
    "cloud_provider": "aws"
  }
}
```

#### Preferences Validation
```
POST /api/scoping/preferences
```
Validates and processes architecture preferences.

#### Bridge Data
```
GET /api/scoping/bridge/{job_id}
```
Returns formatted RFP analysis data for GSE bridge.

**Response:**
```json
{
  "job_id": "uuid",
  "title": "RFP Analysis",
  "requirements": [...],
  "metadata": {
    "total_requirements": 50,
    "completed_at": "2026-06-20T14:00:00Z",
    "file_count": 1,
    "file_names": ["rfp.pdf"]
  }
}
```

## Configuration

### Environment Variables

**RFP Analyzer (.env):**
```bash
# Scoping Architect service URL
SCOPING_ARCHITECT_URL=http://localhost:8001
```

### Port Configuration

- **RFP Analyzer:** Port 8000
- **Scoping Architect:** Port 8001

## Dependencies

### RFP Analyzer

Added to `rfp-analyzer/analyzer/requirements.txt`:
```
httpx>=0.24.0  # HTTP client for scoping-architect integration
```

### Installation

```bash
# Install RFP Analyzer dependencies
cd rfp-analyzer/analyzer
pip install -r requirements.txt

# Install Scoping Architect dependencies
cd ../../scoping-architect
pip install -r requirements.txt
```

## Running the Integrated System

### Option 1: Manual Start

**Terminal 1 - Scoping Architect:**
```bash
cd scoping-architect
uvicorn app:create_app --factory --reload --port 8001
```

**Terminal 2 - RFP Analyzer:**
```bash
cd rfp-analyzer/analyzer
python web_app.py
# or
uvicorn web_app:app --reload --port 8000
```

### Option 2: Using Start Scripts

**Windows:**
```bash
cd rfp-analyzer/analyzer
START_INTEGRATED.bat
```

**Linux/Mac:**
```bash
cd rfp-analyzer/analyzer
./START_INTEGRATED.sh
```

## User Workflow

### Complete Integration Flow

1. **Upload RFP** (Home Tab)
   - Upload RFP document (PDF, DOCX, TXT)
   - Configure analysis settings
   - Click "Analyze RFP"

2. **Review Requirements** (Requirements Tab)
   - Review extracted requirements
   - Accept, modify, or reject requirements
   - Apply filters and bulk actions

3. **Configure Architecture** (Scoping Questionnaire Tab)
   - Fill out architecture preferences in embedded form
   - Select build approach, deployment model, compliance requirements
   - Submit preferences

4. **Generate Scope** (Generate Scope Tab)
   - **Option A:** Click "Open RFP-to-GSE Bridge" for manual GSE population
   - **Option B:** Click "Generate Architecture Scope" for automated architecture generation
   - **Option C:** Select solutions and click "Map to Solutions"

5. **Export Results** (Export Tab)
   - Download requirements in Excel, Markdown, or JSON format
   - Export includes architecture scope if generated

## API Integration Examples

### JavaScript - Generate Architecture Scope

```javascript
async function generateScope() {
    const response = await fetch('http://localhost:8000/api/scoping/analyze', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            project_name: 'My RFP Analysis',
            requirements: window.currentRequirements,
            preferences: {
                approach: 'greenfield',
                deployment: 'cloud',
                cloud_provider: 'aws'
            }
        })
    });
    
    const data = await response.json();
    console.log('Architecture generated:', data);
}
```

### Python - Check Service Health

```python
import httpx

async def check_scoping_health():
    async with httpx.AsyncClient() as client:
        response = await client.get('http://localhost:8000/api/scoping/health')
        return response.json()
```

## Troubleshooting

### Issue: Scoping Questionnaire Tab Shows Error

**Solution:**
- Ensure Scoping Architect is running on port 8001
- Check CORS settings in both applications
- Verify `SCOPING_ARCHITECT_URL` environment variable

### Issue: Generate Scope Button Fails

**Solution:**
- Check that RFP analysis is completed first
- Verify Scoping Architect API is accessible
- Check browser console for detailed error messages
- Ensure `httpx` is installed in RFP Analyzer environment

### Issue: Bridge Opens But No Data

**Solution:**
- Ensure job_id is valid and analysis is completed
- Check `/api/scoping/bridge/{job_id}` endpoint response
- Verify requirements are properly stored in analysis_jobs

## Future Enhancements

1. **Real-time Sync**
   - WebSocket connection for live updates between systems
   - Automatic refresh when requirements change

2. **Enhanced Bridge**
   - Drag-and-drop requirement mapping
   - Visual requirement-to-GSE field mapping
   - Bulk import/export capabilities

3. **Unified Authentication**
   - Single sign-on across both systems
   - Shared user sessions and preferences

4. **Advanced Analytics**
   - Cross-system reporting
   - Requirement traceability from RFP to architecture
   - Effort estimation integration

## Support

For issues or questions:
- Check logs in `rfp-analyzer/analyzer/logs/web_app.log`
- Review Scoping Architect logs
- Verify both services are running and accessible
- Check network connectivity between services

## Version History

- **v1.0.0** (2026-06-20): Initial integration
  - Iframe embedding of Scoping Architect homepage
  - API proxy routes for architecture generation
  - Bridge button for GSE template population
  - Solution mapping functionality