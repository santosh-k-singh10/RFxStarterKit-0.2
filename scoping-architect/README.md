# RFP Analyzer - Architecture API v1.2

AI-powered architecture design tool that transforms RFP requirements into detailed technical architectures with story point estimation and requirement traceability.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Option A: Using the setup script (Linux/Mac)
chmod +x setup.sh
./setup.sh

# Option B: Manual installation
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Your `.env` file is already configured with IBM Services Essentials. The system will automatically use:

- **API Base:** IBM Services Essentials (OpenAI-compatible)
- **Model:** `global/anthropic.claude-sonnet-4-5-20250929-v1:0`
- **Port:** 8000

### 3. Start the Server

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Run the server
python run.py
```

### 4. Access the Application

- **Main Form:** http://localhost:8000/
- **API Documentation:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## 📋 Features

### 🎨 Interactive Web Interface
- **3-step wizard** for collecting architecture preferences
- Step 1: Solution type (build approach, deployment model)
- Step 2: Technology & constraints (compliance, channels, integration style)
- Step 3: Review & confirm with live preview
- File upload for requirements with real-time architecture generation
- Comprehensive results display with metrics, components, and risks

### 🔄 Automatic Requirement Enrichment (Phase 1.5)
- **Built-in enrichment**: Automatically enriches markdown requirements
- No manual enrichment step required
- Adds module grouping, implementation types, and actor mapping
- Powered by `RequirementEnricher` class

### 🏗️ Architecture Generation (Phase 2)

#### **Auto-Enriched Path: `POST /api/analyze`** ⭐ (Recommended)
- Accepts markdown requirements + preferences
- **Automatically enriches** requirements before analysis
- Returns full architecture with story points and traceability
- Simplest way to get started

#### **Pre-Enriched Path: `POST /api/analyze/enriched`**
- For when you have pre-enriched module data
- Direct control over module structure
- Same rich output as auto-enriched path

### 📤 Export Functionality
- **Markdown export**: `POST /api/export/markdown`
  - Comprehensive document with all architecture details
  - Story points, traceability, risk register
  - Ready for documentation or review
- **JSON export**: `POST /api/export/json`
  - Formatted JSON with proper indentation
  - Easy integration with other tools

### 🧪 Comprehensive Test Suite
- 15+ unit tests for data models
- Pytest fixtures for easy testing
- Mock LLM responses (no API key needed for tests)
- Run with: `pytest` or `pytest --cov=architecture_designer`

## 🔧 Configuration

The system uses your `.env` file for all LLM communications:

```env
# IBM Services Essentials (OpenAI-compatible)
OPENAI_API_BASE=https://servicesessentials.ibm.com/apis/v3
OPENAI_API_KEY=your-key-here
MODEL_ID=global/anthropic.claude-sonnet-4-5-20250929-v1:0

# Server
PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Fallback to Anthropic Direct API

If you want to use Anthropic's API directly instead, just set:

```env
ANTHROPIC_API_KEY=sk-ant-api03-...
```

The system will automatically detect and use the appropriate configuration.

## 📖 API Usage

### 1. Collect Preferences

```bash
curl -X POST http://localhost:8000/api/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "approach": "greenfield",
    "deployment": "cloud",
    "cloud": "aws",
    "compliance": ["gdpr", "hipaa"],
    "channels": ["web", "mobile_native"]
  }'
```

### 2. Analyze Architecture

```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "preferences": {
      "approach": "greenfield",
      "deployment": "cloud",
      "cloud": "aws"
    },
    "requirements": "FR-001: User authentication...",
    "project_name": "E-commerce Platform"
  }'
```

### 3. Analyze with Enriched Requirements (Recommended)

```bash
curl -X POST http://localhost:8000/api/analyze/enriched \
  -H "Content-Type: application/json" \
  -d '{
    "project_name": "E-commerce Platform",
    "deployment": "cloud",
    "cloud_provider": "AWS",
    "domain_context": "ecommerce",
    "compliance": ["PCI DSS", "GDPR"],
    "timeline": "Fixed deadline",
    "extra_constraints": ["React + Node.js preferred"],
    "modules": {
      "identity_access": [
        {
          "id": "FR-001",
          "type": "FR",
          "title": "User authentication",
          "module": "identity_access",
          "impl_type": "custom_build",
          "actors": ["Customer", "Admin"]
        }
      ],
      "cart_checkout": [
        {
          "id": "FR-010",
          "type": "FR",
          "title": "Shopping cart management",
          "module": "cart_checkout",
          "impl_type": "custom_build",
          "actors": ["Customer"]
        }
      ]
    }
  }'
```

### 4. Health Check

```bash
curl http://localhost:8000/api/health
```

## 🏗️ Project Structure

```
c:/Agents/scoping-architect/
├── app.py                          # FastAPI application with 3-step wizard UI
├── run.py                          # Server startup script
├── router.py                       # API endpoints (analyze, export, preferences)
├── schemas.py                      # Pydantic request/response models
├── llm_client.py                   # LLM client (Anthropic + IBM Services Essentials)
├── config.py                       # Configuration management
├── example_usage.py                # Comprehensive usage examples
├── PIPELINE.md                     # Complete pipeline documentation
├── IMPROVEMENTS_SUMMARY.md         # Summary of all improvements
├── requirements.txt                # Python dependencies
├── pytest.ini                      # Pytest configuration
├── .env                            # Environment configuration
│
├── architecture_designer/          # Core module
│   ├── __init__.py                # Module exports
│   ├── designer.py                # ArchitectureDesigner class
│   ├── models.py                  # Data models (EnrichedModules, etc.)
│   ├── preferences.py             # User preferences handling
│   ├── prompts.py                 # LLM prompt builders
│   ├── enricher.py                # Auto-enrichment (Phase 1.5)
│   └── exporters.py               # Markdown/JSON exporters
│
└── tests/                          # Test suite
    ├── conftest.py                # Pytest fixtures and configuration
    ├── test_models.py             # Model unit tests
    └── README.md                  # Test documentation
```

## 🧪 Development & Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio pytest-cov

# Run all tests
pytest

# Run with coverage report
pytest --cov=architecture_designer --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run tests without slow tests
pytest -m "not slow"
```

### Run Examples
```bash
# Mock mode (no API key needed)
python example_usage.py --mock

# With API key
export ANTHROPIC_API_KEY=sk-ant-...
python example_usage.py

# With requirements file
python example_usage.py --requirements requirements.md
```

### Development Server
```bash
# Run with auto-reload
python run.py

# Check configuration
python -c "from config import config; print(config.get_llm_type())"
```

## 🔐 Security Notes

- Never commit `.env` file to version control
- API keys are loaded from environment variables only
- CORS origins are configurable via `ALLOWED_ORIGINS`

## 🆕 What's New in v1.2

### 🎯 High-Priority Improvements (Completed)

#### 1. Comprehensive Test Suite
- **15+ unit tests** covering all data models
- **Pytest fixtures** for easy test setup
- **Mock LLM responses** - no API key needed for testing
- **Coverage reporting** with pytest-cov
- Run with: `pytest` or `pytest --cov=architecture_designer`

#### 2. Enhanced 3-Step Wizard UI
- **Step 1**: Solution type and deployment model
- **Step 2**: Technology landscape and constraints
- **Step 3**: Review and confirm with live preview
- **File upload** for requirements markdown
- **Real-time results** with metrics, components, and risks
- Already implemented in [`app.py`](app.py)

#### 3. Export Functionality
- **Markdown exporter**: Full architecture document with story points and traceability
- **JSON exporter**: Formatted JSON for integration
- **API endpoints**: `POST /api/export/markdown` and `POST /api/export/json`
- **Exporters module**: [`architecture_designer/exporters.py`](architecture_designer/exporters.py)

#### 4. Separate Enriched Endpoint
- **Dedicated endpoint**: `POST /api/analyze/enriched`
- **Pre-enriched input**: For when you have module-grouped requirements
- **Same rich output**: Story points, traceability, actor mapping
- Already implemented in [`router.py`](router.py)

### 🔄 Automatic Enrichment Pipeline
- **Built-in enrichment**: `POST /api/analyze` now auto-enriches requirements
- **No manual step**: Markdown → Enriched → Architecture in one call
- **RequirementEnricher**: Powered by [`architecture_designer/enricher.py`](architecture_designer/enricher.py)
- **Module grouping**: Automatic categorization into functional modules
- **Implementation types**: Identifies custom builds vs integrations
- **Actor mapping**: Tracks users and systems per requirement

### 📊 Enhanced Output
- `story_point_range` on every component (low/mid/high)
- `source_requirements` list showing requirement traceability
- `module` field linking components to functional modules
- `impl_type` field (custom_build, third_party_integration, etc.)
- `actors` list per component
- `total_story_points_mid` in summary for quick estimation

### 📚 Documentation & Examples
- **PIPELINE.md**: Complete pipeline guide with examples
- **example_usage.py**: Comprehensive usage examples
- **IMPROVEMENTS_SUMMARY.md**: Detailed summary of all improvements
- **tests/README.md**: Test suite documentation

### 🔧 API Improvements
- **Auto-enrichment**: `POST /api/analyze` with automatic enrichment
- **Pre-enriched**: `POST /api/analyze/enriched` for module data
- **Export endpoints**: `/api/export/markdown` and `/api/export/json`
- **Comprehensive logging**: Detailed logs throughout the pipeline
- **Better error handling**: Enhanced JSON repair and validation
- **Increased token limit**: 8000 tokens to prevent truncation

## 📝 License

Internal use only.