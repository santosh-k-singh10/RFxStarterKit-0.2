# 🚀 Quick Start - Enhanced Web Application

## Step 1: Install Dependencies

```bash
cd rfp-analyzer
pip install -r requirements.txt
```

## Step 2: Configure API Keys

Create `.env` file in `rfp-analyzer/` directory:

```env
OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

## Step 3: Start the Server

```bash
python app/main.py
```

Server starts on: **http://localhost:8000**

## Step 4: Test the API

### Option A: Use Swagger UI
Visit http://localhost:8000/docs

### Option B: Use cURL

**Upload RFP:**
```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@your_rfp.pdf" \
  -F "title=Test RFP" \
  -c cookies.txt
```

**Check Status:**
```bash
curl "http://localhost:8000/api/status/SESSION_ID_FROM_RESPONSE"
```

**Get Requirements:**
```bash
curl -b cookies.txt "http://localhost:8000/api/requirements"
```

**Export to Excel:**
```bash
curl -b cookies.txt "http://localhost:8000/api/export/excel" --output results.xlsx
```

## Step 5: Review Requirements

Use the API endpoints to:
1. Filter requirements: `GET /api/requirements?category=functional&priority=must`
2. Update requirements: `PATCH /api/requirements/FR-001`
3. Accept/reject: Use `review_status` field

## Step 6: Generate Architecture (Optional)

```bash
curl -X POST -b cookies.txt "http://localhost:8000/api/architecture/diagram"
```

## Step 7: Map to Solutions (Optional)

```bash
curl -X POST -b cookies.txt "http://localhost:8000/api/solution-mapping" \
  -H "Content-Type: application/json" \
  -d '{"solutions": ["SAP S/4HANA", "Oracle ERP Cloud"]}'
```

## 🎯 Key Differences from Old Web App

| Feature | Old (web_app_v2.py) | New (app/main.py) |
|---------|---------------------|-------------------|
| **Architecture** | Single file | Modular (routers, services, models) |
| **Edit Requirements** | ❌ No | ✅ Full CRUD with PATCH/DELETE |
| **Review Workflow** | ❌ No | ✅ Accept/Modify/Reject status |
| **Clarifications** | ❌ No | ✅ Submit answers with re-analysis |
| **Architecture Gen** | ❌ No | ✅ Claude-powered Mermaid diagrams |
| **Solution Mapping** | ❌ No | ✅ Multi-vendor comparison |
| **Session Management** | In-memory jobs | Cookie-based with Redis support |
| **API Documentation** | ❌ No | ✅ Swagger UI + ReDoc |
| **Filtering** | Basic | Advanced (category, priority, status, confidence, search) |
| **Bulk Operations** | ❌ No | ✅ Bulk accept/reject |

## 🎉 You're Ready!

The enhanced web application is now running. You can:

1. **Use the API** via Swagger UI at http://localhost:8000/docs
2. **Integrate with your tools** using the REST API endpoints
3. **Build a custom frontend** that calls these APIs
4. **Extend functionality** by adding new routers/services

## 📖 Next Steps

- Read the full documentation: `ENHANCED_WEB_APP_README.md`
- Explore API endpoints in Swagger UI
- Test with your RFP documents
- Customize for your organization's needs

## 💡 Pro Tips

1. **Use filters effectively**: Combine multiple filters for precise results
   ```bash
   /api/requirements?category=functional&priority=must&review_status=pending&min_confidence=0.8
   ```

2. **Cache is your friend**: Architecture and solution mapping results are cached per session

3. **Export early, export often**: Export at different stages of review

4. **Bulk operations save time**: Use `/api/requirements/bulk` for mass updates

5. **Session cookies**: Keep cookies.txt for CLI usage or use browser for automatic cookie handling
