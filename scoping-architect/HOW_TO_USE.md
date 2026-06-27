# How to Use the Architecture Generator

## Quick Start

### 1. Start the Server

```bash
python run.py
```

The server will start on `http://localhost:8000`

## Ways to Generate and View Architecture

### Option 1: Web UI (Easiest)

1. **Open your browser** and go to: `http://localhost:8000`

2. **Fill out the 3-step form:**
   - Step 1: Solution type (deployment, cloud provider, etc.)
   - Step 2: Technology & constraints (compliance, channels, integration)
   - Step 3: Review and submit

3. **Upload your requirements markdown file**
   - After submitting preferences, you'll see an upload section
   - Upload a `.md` file with your requirements
   - Click "Generate architecture"

4. **View the results on the same page:**
   - Architecture summary
   - System context with actors and integrations
   - Component breakdown with story points
   - Risk analysis
   - Raw JSON response

### Option 2: API Docs (Interactive)

1. **Open Swagger UI**: `http://localhost:8000/docs`

2. **Try the endpoints:**
   - `POST /api/preferences` - Submit preferences
   - `POST /api/analyze` - Generate architecture from flat requirements
   - `POST /api/analyze/enriched` - Generate from Phase 1.5 enriched requirements

3. **Click "Try it out"** on any endpoint to test it interactively

4. **View the response** directly in the browser

### Option 3: Direct API Calls (Programmatic)

#### Using curl:

```bash
# Step 1: Submit preferences
curl -X POST http://localhost:8000/api/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "approach": "greenfield",
    "deployment": "cloud",
    "cloud": "aws",
    "compliance": ["gdpr"],
    "channels": ["web", "mobile_native"],
    "integration": "rest",
    "timeline": "phased"
  }'

# Step 2: Generate architecture
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "approach": "greenfield",
      "deployment": "cloud",
      "cloud": "aws",
      "compliance": ["gdpr"],
      "channels": ["web", "mobile_native"]
    },
    "requirements": "# Requirements\n\n## FR-001: User Login\nUsers must be able to login...",
    "project_name": "My Project"
  }' > architecture_output.json
```

#### Using Python:

```python
import requests
import json

# Submit preferences
prefs_response = requests.post(
    "http://localhost:8000/api/preferences",
    json={
        "approach": "greenfield",
        "deployment": "cloud",
        "cloud": "aws",
        "compliance": ["gdpr"],
        "channels": ["web", "mobile_native"]
    }
)
preferences = prefs_response.json()

# Generate architecture
arch_response = requests.post(
    "http://localhost:8000/api/analyze",
    json={
        "preferences": preferences,
        "requirements": """
# Requirements

## FR-001: User Authentication
Users must be able to register and login.

## FR-002: Product Catalog
Display searchable product catalog.
        """,
        "project_name": "E-Commerce Platform"
    }
)

# Save to file
architecture = arch_response.json()
with open("architecture_output.json", "w") as f:
    json.dump(architecture, f, indent=2)

print(f"Architecture generated!")
print(f"Components: {architecture['summary']['component_count']}")
print(f"Domains: {architecture['summary']['domain_count']}")
```

### Option 4: Using the Test Script

```bash
python test_architecture_flow.py
```

This will:
- Test the complete flow
- Display results in the console
- Show all logging output in the server terminal

## Output Format

The generated architecture includes:

### 1. Summary
```json
{
  "summary": {
    "domain_count": 4,
    "actor_count": 3,
    "component_count": 12,
    "avg_complexity": "Medium",
    "compliance_components": 5,
    "total_story_points_mid": 156
  }
}
```

### 2. Domains
```json
{
  "domains": [
    {
      "name": "User Management",
      "requirements": ["FR-001", "FR-002"],
      "count": 2,
      "color": "blue"
    }
  ]
}
```

### 3. System Context
```json
{
  "system_context": {
    "description": "The system is a cloud-based e-commerce platform...",
    "actors": [
      {
        "name": "End User",
        "type": "human",
        "description": "Customers browsing and purchasing products"
      }
    ],
    "integrations": [
      "Payment Gateway (Stripe/PayPal)",
      "Email Service (SendGrid)"
    ]
  }
}
```

### 4. Architecture Pattern
```json
{
  "architecture": {
    "recommended": "Microservices with API Gateway",
    "rationale": "Given the need for scalability...",
    "key_principles": [
      "API-first design",
      "Event-driven communication",
      "Stateless services"
    ]
  }
}
```

### 5. Components
```json
{
  "components": [
    {
      "name": "User Service",
      "type": "Backend Service",
      "description": "Handles user authentication and profile management",
      "complexity": "Medium",
      "story_point_range": {
        "low": 8,
        "mid": 13,
        "high": 21
      },
      "dependencies": ["Auth Service", "Database"],
      "source_requirements": ["FR-001", "FR-002"]
    }
  ]
}
```

### 6. Risks
```json
{
  "risks": [
    {
      "risk": "Payment integration complexity",
      "level": "High",
      "mitigation": "Use established payment gateway SDKs..."
    }
  ]
}
```

## Viewing Logs

All processing logs appear in the terminal where you ran `python run.py`:

```
======================================================================
POST /api/analyze - Starting architecture analysis
======================================================================
Project: E-Commerce Platform
Requirements length: 536 characters
...
→ Calling IBM Services Essentials API
  - Model: global/anthropic.claude-sonnet-4-5-20250929-v1:0
  - Input tokens: 816
  - Output tokens: 4255
[OK] Architecture generated successfully
  - Components: 12
  - Domains: 4
  - Risks: 3
======================================================================
```

## Saving Output

### From Web UI
- Copy the JSON from the "Raw architecture response" section
- Or use browser DevTools to capture the response

### From API
- Redirect output to a file: `curl ... > output.json`
- Or save programmatically in your code

### Export Formats
The architecture can be exported to:
- **JSON**: Full structured data
- **Markdown**: Human-readable report (use exporters in code)

## Troubleshooting

### "LLM not configured" error
Set your credentials in `.env`:
```
OPENAI_API_BASE=https://servicesessentials.ibm.com/apis/v3
OPENAI_API_KEY=your_key_here
MODEL_ID=global/anthropic.claude-sonnet-4-5-20250929-v1:0
```

### "Invalid JSON" error
- Check the logs for the exact error
- The LLM response may have formatting issues
- Try with simpler requirements first

### Timeout errors
- Increase timeout in your client
- Check network connectivity
- Verify LLM service is responding

## Next Steps

1. **Try the web UI first** - easiest way to get started
2. **Check the logs** - understand what's happening
3. **Use the API** - integrate into your workflow
4. **Customize** - modify prompts or add new features