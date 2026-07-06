# RFP Analyzer - Quick Start Guide

## System Status

✅ **FIXED ISSUES:**
1. Embedder re-enabled (was disabled for debugging)
2. Model preloading re-enabled (was disabled for debugging)
3. Timeout fixes in place (5-minute timeout, streaming uploads)
4. PDF extraction enhanced
5. Authentication unified (using common/.env)

## Prerequisites

1. **Python 3.8+** installed
2. **Dependencies installed**:
   ```bash
   cd rfp-analyzer/analyzer
   pip install -r ../../common/requirements-base.txt
   pip install sentence-transformers faiss-cpu aiofiles
   ```

3. **Environment configured**: `common/.env` file with:
   - `OPENAI_API_BASE`
   - `OPENAI_API_KEY`
   - `MODEL_ID`

## Starting the Application

### Option 1: Using web_app.py (Recommended)
```bash
cd rfp-analyzer/analyzer
python web_app.py
```

### Option 2: Using uvicorn directly
```bash
cd rfp-analyzer/analyzer
python -m uvicorn web_app:app --host 0.0.0.0 --port 8080 --reload
```

## Expected Startup Sequence

You should see:
```
[OK] Environment loaded from: ...common\.env
[OK] Phase 0 path added: ...
application_startup_preloading_models
loading_sentence_transformer_model
sentence_transformer_model_loaded
models_preloaded_successfully
application_startup_complete
INFO:     Uvicorn running on http://0.0.0.0:8080
```

**Note**: Model loading takes 30-60 seconds on first startup. This is normal!

## Testing the Application

### 1. Health Check
Open browser: http://localhost:8080/api/health

Expected response:
```json
{
  "status": "healthy",
  "phase0_available": true
}
```

### 2. Upload Test File
1. Go to: http://localhost:8080
2. Click "Choose File"
3. Select: `rfp-analyzer/test_rfp_quick.txt`
4. Click "Analyze RFP"
5. Wait for analysis (2-3 minutes)

### 3. Expected Behavior
- ✅ Upload completes immediately (< 1 second)
- ✅ Progress bar appears and updates
- ✅ Analysis completes in 2-3 minutes
- ✅ Redirects to review page
- ✅ No timeout errors!

## Troubleshooting

### Issue: "Module not found" errors
**Solution**: Install missing dependencies
```bash
pip install sentence-transformers faiss-cpu aiofiles anthropic openai
```

### Issue: "Could not resolve authentication method"
**Solution**: Check `common/.env` has required variables:
```bash
# Verify file exists
ls common/.env

# Check contents
cat common/.env | grep OPENAI_API
```

### Issue: Timeout on file upload
**Solution**: 
1. Check server logs for errors
2. Verify model preloading completed at startup
3. Check file size (< 50MB recommended)

### Issue: Analysis fails with LLM errors
**Solution**:
1. Verify API credentials in `common/.env`
2. Check API endpoint is accessible
3. Review server logs for specific error messages

## System Architecture

```
┌─────────────────────────────────────┐
│     Browser (localhost:8080)        │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│   FastAPI Server (web_app.py)       │
│   - Model Cache (preloaded)         │
│   - File Upload (streaming)         │
│   - Background Tasks                │
└──────────────┬──────────────────────┘
               │
               ├──────────────┐
               ▼              ▼
┌──────────────────┐  ┌──────────────────┐
│  Phase 0 Router  │  │  RFP Analyzer    │
│  (Multi-doc)     │  │  (Single doc)    │
└──────────────────┘  └──────────────────┘
               │              │
               └──────┬───────┘
                      ▼
        ┌─────────────────────────┐
        │  LLM API (IBM Services) │
        │  Claude 3.5 Sonnet      │
        └─────────────────────────┘
```

## Performance Expectations

- **Startup**: 30-60 seconds (model loading)
- **File Upload**: < 1 second (immediate response)
- **Analysis**: 2-3 minutes (depends on file size and LLM)
- **Memory**: ~500MB (with model loaded)

## Next Steps

1. **Test the system**: Run `python test_system_health.py`
2. **Start the server**: `cd rfp-analyzer/analyzer && python web_app.py`
3. **Upload a test file**: Use the web interface
4. **Initialize git**: Once confirmed working, run:
   ```bash
   git init
   git add .
   git commit -m "Working RFP Analyzer with all fixes applied"
   ```

## Files Modified (Last 24 Hours)

### Re-enabled (were disabled for debugging):
- `rfp-analyzer/analyzer/core/embedder.py` - Vector embeddings
- `rfp-analyzer/analyzer/web_app.py` - Model preloading

### Created (performance improvements):
- `rfp-analyzer/analyzer/core/model_cache.py` - Model caching
- `document-consolidator/phase0_router/phase0/llm_client.py` - Unified auth

### Enhanced:
- `rfp-analyzer/analyzer/app/static/js/api.js` - 5-minute timeout
- `rfp-analyzer/analyzer/core/ingestor.py` - Better PDF extraction
- `common/.env` - Centralized configuration

## Support

If issues persist:
1. Check server logs in terminal
2. Review `TIMEOUT_ISSUE_RESOLVED.md` for details
3. Review `PDF_EXTRACTION_FIX.md` for PDF issues
4. Review `AUTHENTICATION_FIX_COMPLETE.md` for auth issues