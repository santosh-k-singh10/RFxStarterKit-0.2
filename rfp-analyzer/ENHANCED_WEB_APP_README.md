# RFP Analyzer - Enhanced Web Application

## 🚀 Overview

This is the enhanced web application for the RFP Analyzer, featuring a full-featured FastAPI backend with REST API endpoints for interactive requirement review, editing, architecture generation, and solution mapping.

## ✨ Key Features

### 1. **Document Analysis**
- Upload PDF, DOCX, or TXT RFP documents
- Automatic extraction of functional, non-functional, compliance, ambiguity, and risk requirements
- Background processing with progress tracking
- Session-based state management

### 2. **Interactive Review Interface**
- **CRUD Operations**: Edit requirements inline (title, description, category, priority)
- **Review Workflow**: Accept, modify, or reject requirements
- **Filtering**: Filter by category, priority, review status, confidence
- **Search**: Full-text search across titles and descriptions
- **Bulk Operations**: Accept/reject multiple requirements at once

### 3. **Clarification Management**
- Submit answers to ambiguous requirements
- Track clarification sources (e.g., Corrigendum No. 1)
- Automatic re-analysis trigger (optional)

### 4. **Architecture Generation** (Claude API)
- Generate Mermaid.js architecture diagrams from accepted requirements
- Identify system components with type classification
- Cache results for performance

### 5. **Solution Mapping** (Claude API)
- Map requirements to target solutions (SAP, Oracle, Salesforce, etc.)
- Coverage analysis: native | configuration | customisation | gap
- Solution comparison with summary statistics

### 6. **Export Capabilities**
- **Excel**: Color-coded requirements with summary sheets
- **Markdown**: Structured report format
- **JSON**: Machine-readable format with metadata
- **Solution Map**: Detailed mapping export

---

## 📁 Architecture

```
rfp-analyzer/
├── app/                              # Enhanced web application
│   ├── main.py                       # FastAPI app entry point
│   ├── session_store.py              # Session management
│   ├── routers/                      # API endpoints
│   │   ├── analysis.py               # Upload & analyze
│   │   ├── requirements.py           # CRUD operations
│   │   ├── clarifications.py         # Clarification handling
│   │   ├── architecture.py           # Architecture generation
│   │   ├── solution_mapping.py       # Solution mapping
│   │   └── exports.py                # Export endpoints
│   └── services/                     # Business logic
│       ├── pipeline_service.py       # LangGraph pipeline wrapper
│       ├── claude_service.py         # Claude API calls
│       └── export_service.py         # Export functions wrapper
│
├── core/                             # Core analysis engine
│   ├── schemas.py                    # Extended with review fields
│   ├── state.py                      # LangGraph state management
│   └── ingestor.py                   # Document ingestion
│
├── agents/                           # Extraction agents
│   ├── functional.py
│   ├── nonfunctional.py
│   ├── compliance.py
│   ├── ambiguity.py
│   ├── risk.py
│   └── synthesizer.py
│
└── outputs/                          # Export functionality
    └── exporter.py
```

---

## 🔧 Installation

### 1. Install Dependencies

```bash
cd rfp-analyzer
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file:

```env
# Required: OpenAI API Key (for embeddings and LLM calls)
OPENAI_API_KEY=sk-...

# Required: Anthropic API Key (for Claude Sonnet 4)
ANTHROPIC_API_KEY=sk-ant-...

# Optional: Redis (for production session storage)
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## 🚀 Running the Application

### Development Mode

```bash
# From rfp-analyzer directory
python app/main.py
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --reload --port 8000
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The server will start on **http://localhost:8000**

---

## 📚 API Documentation

Once the server is running, visit:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔌 API Endpoints

### Analysis

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Upload and analyze RFP document |
| GET | `/api/status/{session_id}` | Get analysis progress/status |

### Requirements

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/requirements` | Get filtered requirements |
| PATCH | `/api/requirements/{req_id}` | Update a requirement |
| POST | `/api/requirements/bulk` | Bulk update requirements |
| DELETE | `/api/requirements/{req_id}` | Soft delete requirement |

### Clarifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/clarifications/{req_id}/answer` | Submit clarification answer |

### Architecture

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/architecture/diagram` | Generate Mermaid diagram |
| POST | `/api/architecture/components` | Identify system components |

### Solution Mapping

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/solution-mapping` | Map requirements to solutions |

### Exports

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/export/excel` | Export to Excel |
| GET | `/api/export/markdown` | Export to Markdown |
| GET | `/api/export/json` | Export to JSON |
| GET | `/api/export/solution-map` | Export solution mapping |

---

## 📋 Usage Examples

### 1. Upload and Analyze RFP

```bash
curl -X POST "http://localhost:8000/api/analyze" \
  -F "file=@rfp_document.pdf" \
  -F "title=Project Alpha RFP" \
  -F "domain=Healthcare" \
  -F "min_confidence=0.7"
```

Response:
```json
{
  "session_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "pending",
  "message": "Analysis started"
}
```

### 2. Check Analysis Status

```bash
curl "http://localhost:8000/api/status/123e4567-e89b-12d3-a456-426614174000"
```

Response:
```json
{
  "status": "completed",
  "progress": 100,
  "current_step": "Analysis complete",
  "requirements_count": 47
}
```

### 3. Get Requirements (with filters)

```bash
curl "http://localhost:8000/api/requirements?category=functional,non_functional&priority=must&min_confidence=0.8"
```

### 4. Update a Requirement

```bash
curl -X PATCH "http://localhost:8000/api/requirements/FR-001" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated title",
    "priority": "should",
    "review_status": "accepted",
    "reviewer_notes": "Confirmed with stakeholder"
  }'
```

### 5. Generate Architecture Diagram

```bash
curl -X POST "http://localhost:8000/api/architecture/diagram"
```

Response:
```json
{
  "mermaid_code": "graph TD\n  A[User Interface] --> B[API Gateway]\n  B --> C[Auth Service]\n  ...",
  "cached": false
}
```

### 6. Map to Solutions

```bash
curl -X POST "http://localhost:8000/api/solution-mapping" \
  -H "Content-Type: application/json" \
  -d '{
    "solutions": ["SAP S/4HANA", "Oracle ERP Cloud", "Salesforce", "Custom Build"]
  }'
```

### 7. Export to Excel

```bash
curl "http://localhost:8000/api/export/excel" --output requirements.xlsx
```

---

## 🔐 Session Management

The application uses **cookie-based sessions** for state management:

- Session cookie is automatically set on `/api/analyze`
- Cookie name: `session_id`
- TTL: 4 hours
- HttpOnly: Yes (security)

For production, configure Redis for distributed session storage.

---

## 🎨 Extended Schema Fields

The `Requirement` model has been extended with:

```python
# Review workflow
review_status: ReviewStatus  # pending | accepted | modified | rejected
reviewer_notes: Optional[str]
clarification_answer: Optional[str]
answer_source: Optional[str]
reanalysis_triggered: bool

# Architecture & Solution Mapping
system_components: list[str]
best_fit_solution: Optional[str]
solution_coverage: Optional[str]  # native | configuration | customisation | gap
solution_module: Optional[str]
solution_rationale: Optional[str]
```

---

## 🔄 Workflow

1. **Upload RFP** → Automatic analysis with LangGraph pipeline
2. **Review Requirements** → Edit, accept, or reject requirements
3. **Submit Clarifications** → Answer ambiguous items
4. **Generate Architecture** → Claude creates system diagram
5. **Map Solutions** → Claude evaluates vendor fit
6. **Export** → Download in multiple formats

---

## 🚧 Future Enhancements

The following are planned for future releases:

### Phase 6-7: Frontend (Not Yet Implemented)
- **Static Files**: CSS, JavaScript modules
- **Templates**: Jinja2 templates for home and review pages
- **Interactive UI**: Multi-tab review interface
- **Real-time Updates**: WebSocket support for progress
- **Visualization**: Mermaid diagram rendering, Chart.js for solution comparison

To add the frontend, create:
- `app/static/css/app.css`
- `app/static/js/` (api.js, home.js, tabs/*.js)
- `app/templates/` (base.html, home.html, review.html)

---

## 📊 Performance Considerations

- **Caching**: Architecture diagrams and solution mappings are cached in session
- **Background Tasks**: Analysis runs asynchronously
- **Checkpointing**: LangGraph supports resume on failure
- **Batch Operations**: Bulk update endpoint for efficiency

---

## 🐛 Troubleshooting

### Issue: "No session found"
- **Cause**: Session cookie not set or expired
- **Solution**: Re-upload document to create new session

### Issue: Claude API errors
- **Cause**: Invalid API key or rate limits
- **Solution**: Check `ANTHROPIC_API_KEY` in `.env`

### Issue: Pipeline fails
- **Cause**: Missing OpenAI API key or document ingestion error
- **Solution**: Check `OPENAI_API_KEY` and document format

---

## 📝 License

Same as parent project.

---

## 🤝 Contributing

Contributions welcome! Please ensure:
1. API endpoints follow REST conventions
2. Add proper error handling
3. Update this README
4. Test with various RFP formats

---

## 📞 Support

For issues or questions, please refer to the main project README or API documentation at `/docs`.