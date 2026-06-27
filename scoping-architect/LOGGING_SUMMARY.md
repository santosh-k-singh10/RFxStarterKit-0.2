# Architecture Generation Flow - Logging Summary

## Overview

Comprehensive logging has been added to the entire generate-architecture flow to provide visibility into each step of the process. All logs are output to the terminal where the server is running.

## Logging Coverage

### 1. **Router Layer** (`router.py`)

#### POST /api/preferences
- Input preferences details (approach, deployment, cloud, compliance, channels, etc.)
- Processing status with PreferencesCollector
- Inferred domain context
- Number of extra constraints
- Success/failure status

#### POST /api/analyze
- Project name and requirements length
- Preferences building process
- Deployment target and domain context
- Number of constraints
- ArchitectureDesigner initialization
- Analysis completion with component/domain/risk counts

#### POST /api/analyze/enriched
- Project details and deployment info
- Module breakdown with requirement counts per module
- Total requirements across all modules
- Constraint building process
- Architecture generation results with story points

### 2. **Designer Layer** (`architecture_designer/designer.py`)

#### Analysis Methods
- **analyze_enriched()** / **analyze_enriched_async()**
  - Project, deployment, and domain information
  - Total requirements count
  - ArchitectureInput building
  - LLM call initiation
  - Response parsing
  - Traceability attachment with link counts

- **analyze()** / **analyze_async()**
  - Project name and requirements length
  - LLM call status
  - Response parsing completion

#### LLM Communication
- **_call_sync()** / **_call_async()**
  - Prompt sizes (system and user)
  - Attempt number and retry information
  - Max tokens and temperature settings
  - Token usage (input/output)
  - Success/failure status with retry delays

#### Response Parsing
- Number of domains parsed
- Component extraction
- Risk identification

### 3. **LLM Client Layer** (`llm_client.py`)

#### create_message()
- Number of messages
- System prompt presence and size
- Max tokens and temperature
- LLM provider being used (IBM Services Essentials or Anthropic)

#### IBM Services Essentials
- Model name
- Base URL
- Total messages count
- Token usage (input/output)
- Response length in characters

#### Anthropic Direct API
- Model name
- Message count
- Token usage
- Model used in response

### 4. **Preferences Layer** (`architecture_designer/preferences.py`)

#### PreferencesCollector.from_dict()
- Input keys received
- Build approach
- Domain inference process
- Inferred domain result
- Deployment type
- Compliance regime count
- Client channel count
- Extra constraints count

## Log Format

All logs follow this format:
```
YYYY-MM-DD HH:MM:SS,mmm  LEVEL  module_name  message
```

Example:
```
2026-06-06 00:05:09,093  INFO  architecture_designer.designer  Building prompts...
2026-06-06 00:05:09,093  INFO  architecture_designer.designer    - System prompt: 2764 chars
2026-06-06 00:05:09,093  INFO  architecture_designer.designer    - User prompt: 664 chars
```

## Visual Indicators

- `=` separators for major sections (70 characters wide)
- `✓` or `[OK]` for successful operations
- `✗` or `[FAIL]` for failures
- `→` for outgoing API calls
- Indentation with `-` for sub-items

## Example Flow Output

```
======================================================================
POST /api/preferences - Starting preferences collection
======================================================================
Input preferences:
  - Build approach: greenfield
  - Deployment: cloud
  - Cloud provider: aws
  - Compliance: ['gdpr']
  - Channels: ['web', 'mobile_native']
  - Integration style: rest
  - Timeline: phased
Processing preferences with PreferencesCollector...
PreferencesCollector.from_dict() called
  - Input keys: ['approach', 'deployment', 'cloud', ...]
  - Build approach: BuildApproach.GREENFIELD
Inferring domain context...
  - Inferred domain: None
✓ UserPreferences created
  - Deployment: cloud
  - Compliance regimes: 1
  - Client channels: 2
  - Extra constraints: 1
Preferences processed successfully
  - Inferred domain context: None
  - Extra constraints: 1 items
✓ Preferences collection completed successfully
======================================================================
```

## Testing

A test script `test_architecture_flow.py` is provided to verify the complete flow:

```bash
python test_architecture_flow.py
```

This will:
1. Test the health endpoint
2. Submit preferences
3. Generate architecture from sample requirements
4. Display all logging output in the server terminal

## Monitoring in Production

To monitor the flow in production:

1. **Start the server:**
   ```bash
   python run.py
   ```

2. **Watch the terminal** for real-time logging as requests come in

3. **Key metrics to monitor:**
   - Token usage (input/output)
   - Response times
   - Retry attempts
   - Component/domain counts
   - Story point estimates

## Log Levels

- **INFO**: Normal operation flow, metrics, and status updates
- **WARNING**: Retry attempts, non-fatal errors (e.g., traceability failures)
- **ERROR**: Fatal errors that prevent operation completion

## Benefits

1. **Debugging**: Quickly identify where issues occur in the pipeline
2. **Performance**: Monitor token usage and response times
3. **Validation**: Verify data transformation at each step
4. **Auditing**: Track all architecture generation requests
5. **Optimization**: Identify bottlenecks and optimization opportunities

## Files Modified

1. `router.py` - API endpoint logging
2. `architecture_designer/designer.py` - Analysis and LLM call logging
3. `llm_client.py` - LLM provider communication logging
4. `architecture_designer/preferences.py` - Preferences processing logging
5. `test_architecture_flow.py` - End-to-end test script (created)