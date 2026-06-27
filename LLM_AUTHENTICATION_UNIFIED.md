# LLM Authentication Unified Across Phase 0 and RFP Analyzer

## Overview

Phase 0 and RFP Analyzer now use the **same authentication method** for LLM calls, ensuring consistency across the entire system.

## Authentication Method

Both systems use **OpenAI-compatible API** with IBM Services Essentials as the primary method, with fallback to direct Anthropic API.

### Priority Order

1. **OpenAI-compatible API (IBM Services Essentials)** - Primary method
   - Uses `OPENAI_API_BASE`, `OPENAI_API_KEY`, `MODEL_ID`
   - Provides access to Claude models through IBM's endpoint
   
2. **Direct Anthropic API** - Fallback method
   - Uses `ANTHROPIC_API_KEY`
   - Direct connection to Anthropic's API

## Configuration

### Single .env File

All configuration is now in `rfp-analyzer/.env`:

```env
# Primary: OpenAI-compatible API (IBM Services Essentials)
OPENAI_API_BASE=https://servicesessentials.ibm.com/apis/v3
OPENAI_API_KEY=your-ibm-services-essentials-api-key
MODEL_ID=global/anthropic.claude-sonnet-4-5-20250929-v1:0

# Fallback: Direct Anthropic API (optional)
ANTHROPIC_API_KEY=your-anthropic-api-key
```

## Implementation Details

### Phase 0 LLM Client

Created `document-consolidator/phase0_router/phase0/llm_client.py`:

```python
def get_anthropic_client():
    """
    Get an Anthropic client using the same authentication pattern as RFP Analyzer.
    
    Priority:
    1. OpenAI-compatible API (IBM Services Essentials)
    2. Direct Anthropic API
    """
```

### OpenAI-Compatible Wrapper

The `OpenAICompatibleAnthropicClient` class wraps the OpenAI client to provide an Anthropic-compatible interface:

- Converts between OpenAI and Anthropic message formats
- Provides `.messages.create()` method matching Anthropic's API
- Returns responses in Anthropic format with `.content[0].text`

### Updated Components

All Phase 0 agents now use the unified client:

1. **ClassifierAgent** (`classifier.py`)
   - Updated `__init__` to use `get_anthropic_client()`
   
2. **ChunkerAgent** (`chunker.py`)
   - Updated `__init__` to use `get_anthropic_client()`
   
3. **ConflictDetectorAgent** (`conflict_detector.py`)
   - Updated `__init__` to use `get_anthropic_client()`
   
4. **Phase0Router** (`router.py`)
   - Updated `__init__` to use `get_anthropic_client()`

## Benefits

### ✅ Unified Authentication
- Single `.env` file for all LLM configuration
- No need to maintain separate API keys for Phase 0

### ✅ Consistent Behavior
- Same authentication flow across all components
- Same error handling and retry logic

### ✅ Simplified Deployment
- One set of credentials to manage
- Easier to configure in production environments

### ✅ Cost Tracking
- All LLM calls go through the same endpoint
- Easier to track usage and costs

## Migration from Old Setup

### Before (Separate Authentication)
```
rfp-analyzer/.env:
  OPENAI_API_KEY=...
  OPENAI_API_BASE=...
  MODEL_ID=...

document-consolidator/phase0_router/.env:
  ANTHROPIC_API_KEY=...  # Separate key!
```

### After (Unified Authentication)
```
rfp-analyzer/.env:
  OPENAI_API_KEY=...
  OPENAI_API_BASE=...
  MODEL_ID=...
  # Phase 0 uses the same credentials!
```

## Testing

### Verify Configuration

```python
# Test that Phase 0 can access LLM
from document-consolidator.phase0_router.phase0.llm_client import get_anthropic_client

client = get_anthropic_client()
print(f"Client type: {type(client)}")
# Should print: OpenAICompatibleAnthropicClient or Anthropic
```

### Run Integration Test

```bash
cd rfp-analyzer/analyzer
python run_webapp.py
```

Upload multiple documents - Phase 0 should now work without requiring `ANTHROPIC_API_KEY`.

## Troubleshooting

### Error: "Could not resolve authentication method"

**Cause**: Neither OpenAI-compatible nor Anthropic credentials are set.

**Solution**: Add credentials to `rfp-analyzer/.env`:
```env
OPENAI_API_BASE=https://servicesessentials.ibm.com/apis/v3
OPENAI_API_KEY=your-key-here
MODEL_ID=global/anthropic.claude-sonnet-4-5-20250929-v1:0
```

### Error: "No LLM configuration found for Phase 0"

**Cause**: Phase 0 can't find the `.env` file.

**Solution**: Ensure you're running from `rfp-analyzer/analyzer` directory, or the startup scripts load the `.env` file correctly.

### Phase 0 Not Using OpenAI-Compatible API

**Check**: Look for log message at startup:
```
Using OpenAI-compatible API (IBM Services Essentials) for Phase 0
```

If you see:
```
Using direct Anthropic API for Phase 0
```

Then it's falling back to `ANTHROPIC_API_KEY`. Verify your OpenAI-compatible credentials are set correctly.

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              rfp-analyzer/.env                           │
│  OPENAI_API_BASE, OPENAI_API_KEY, MODEL_ID              │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌───────────────┐         ┌──────────────────┐
│ RFP Analyzer  │         │    Phase 0       │
│  (base.py)    │         │ (llm_client.py)  │
└───────┬───────┘         └──────┬───────────┘
        │                        │
        ▼                        ▼
┌───────────────────────────────────────┐
│   OpenAI Client                       │
│   (IBM Services Essentials)           │
└───────────────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────┐
│   Claude Models                       │
│   (via IBM endpoint)                  │
└───────────────────────────────────────┘
```

## Summary

✅ **Unified**: Single authentication method for all LLM calls  
✅ **Simplified**: One `.env` file to configure  
✅ **Consistent**: Same behavior across Phase 0 and RFP Analyzer  
✅ **Flexible**: Falls back to direct Anthropic API if needed  
✅ **Production-Ready**: Easier to deploy and manage  

The authentication is now unified! Both Phase 0 and RFP Analyzer use the same credentials from `rfp-analyzer/.env`.