# RFxStarterKit

> ⚠️ **Pilot branch — `pilot-no-scoping-architect`**
> This branch is a scoping-architect-free variant of RFxStarterKit v0.2.0. The `scoping-architect` module (port 8001, architecture generation) has been fully removed. Only the **RFP Analyzer** service is present. See `CHANGELOG.md` for details. The full release with scoping-architect lives on `master`.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI Pipeline](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF)](https://github.com/santosh-k-singh10/RFxStarterKit-0.2/actions)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED)](https://www.docker.com/)

> **AI-powered RFP analysis toolkit (pilot — scoping-architect removed)**

Transform RFP documents into actionable requirements using multi-agent AI systems.

> 🔒 **IBM Internal Tool.** This kit is built for use with **IBM Services Essentials** (an internal, OpenAI-compatible LLM gateway). It is not intended for use with a personal/external OpenAI account, and is shared for internal pilot testing only — please don't redistribute outside IBM.

---

## 🎯 Overview

RFxStarterKit is a comprehensive toolkit for analyzing Request for Proposals (RFPs) and generating solution architectures. It combines multiple AI agents to extract requirements, detect compliance issues, assess risks, and create detailed scoping documents.

### Key Capabilities

- 🤖 **Multi-Agent Analysis** - Specialized AI agents for different requirement types
- 📄 **Multi-Document Support** - Process complete RFP packages simultaneously
- 🔍 **Intelligent Extraction** - Automatic requirement extraction with confidence scoring
- ⚠️ **Conflict Detection** - Identify contradictions across multiple documents
- 📊 **Multiple Export Formats** - Excel, JSON, Markdown, and interactive HTML
- 🔗 **Source Traceability** - Every requirement links back to source documents
- 🎨 **SAP Module Mapping** - Optional SAP-specific analysis for SAP opportunities

---

## ✨ Features

### RFP Analyzer
- **Functional Requirements** - Extract user stories, features, and capabilities
- **Non-Functional Requirements** - Identify performance, security, scalability needs
- **Compliance Requirements** - Detect regulatory and compliance obligations
- **Ambiguity Detection** - Flag unclear or contradictory statements
- **Risk Assessment** - Identify project risks and mitigation strategies

### Phase 0 Document Router
- **Document Classification** - Automatically categorize document types
- **Semantic Chunking** - Break documents into meaningful sections
- **Conflict Detection** - Find contradictions across documents
- **Source Traceability** - Maintain document provenance
- **Confidence Scoring** - Quality metrics for extracted information

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/santosh-k-singh10/RFxStarterKit-0.2.git
cd RFxStarterKit-0.2

# 2. Configure environment
cp common/.env.template common/.env
# Edit common/.env with your API keys

# 3. Start with Docker
docker-compose up --build

# 4. Access the service
# RFP Analyzer: http://localhost:8080
```

### Option 2: Local Installation

```bash
# 1. Clone the repository
git clone https://github.com/santosh-k-singh10/RFxStarterKit-0.2.git
cd RFxStarterKit-0.2

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp common/.env.template common/.env
# Edit common/.env with your API keys

# 4. Start the application
# Windows (PowerShell):
.\START_ALL.ps1

# Windows (Command Prompt):
START_ALL.bat
```

### Option 3: Quick Test

```bash
# Run with Python directly
cd rfp-analyzer
python web_app.py
```

---

## 📋 Prerequisites

- **Python 3.8+**
- **IBM Services Essentials API key** (required) — this is what `OPENAI_API_KEY` refers to throughout this repo and `common/.env.template`. It is **not** a personal/external OpenAI key. Request access via your team's onboarding process.
- **Anthropic API Key** (optional, only needed if you want to bypass Services Essentials and call Anthropic directly for Phase 0 multi-document processing)
- **4GB RAM minimum** (8GB recommended)
- **Docker** (optional, for containerized deployment)

> ⚠️ If you paste in a real OpenAI-issued key (`sk-...`) instead of a Services Essentials token, requests will fail with an auth error against `servicesessentials.ibm.com` — the variable name is historical, not a hint about which provider to use.

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Quick Start](docs/QUICK_START.md) | Installation, running, and troubleshooting |
| [Architecture](docs/ARCHITECTURE.md) | System design, data-flow diagrams, repo structure |
| [API Reference](docs/API_REFERENCE.md) | REST endpoints for RFP Analyzer and Phase 0 |
| [Docker Guide](docs/DOCKER_GUIDE.md) | Docker and Docker Compose deployment |
| [ADR log](docs/adr/) | Architecture Decision Records — the *why* behind key choices |
| [Contributing](CONTRIBUTING.md) | Contribution guidelines |
| [Changelog](CHANGELOG.md) | Version history |

---

## 💻 Usage Examples

### Web Interface

1. **Upload Documents**
   - Single or multiple files
   - Supported formats: PDF, DOCX, TXT, MD, XLSX, CSV

2. **Configure Analysis**
   - Set confidence threshold
   - Enable/disable Phase 0 processing
   - Enable SAP module mapping (if needed)

3. **Review Results**
   - Interactive web viewer
   - Download in multiple formats
   - Source traceability for all requirements

### Command Line

```bash
# Analyze single document
python rfp-analyzer/main.py analyze path/to/rfp.pdf

# With options
python rfp-analyzer/main.py analyze path/to/rfp.pdf \
  --output-dir ./results \
  --title "Healthcare System RFP" \
  --min-confidence 0.7
```

### Programmatic API

```python
from rfp_analyzer.main import run_analysis

# Run analysis
result = run_analysis(
    file_path="path/to/rfp.pdf",
    title="My RFP Analysis",
    min_confidence=0.7
)

# Access results
requirements = result["requirements"]
excel_path = result["excel_path"]
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│                 Web Interface                    │
│            (FastAPI + HTML/JS)                   │
└────────────────┬────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
    ▼                         ▼
┌─────────────────┐   ┌──────────────────┐
│  Phase 0 Router │   │   RFP Analyzer   │
│  (Multi-Doc)    │   │  (Single Doc)    │
└────────┬────────┘   └────────┬─────────┘
         │                     │
         ▼                     ▼
┌─────────────────────────────────────────┐
│        Multi-Agent System                │
│  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │Functional│  │Compliance│  │  Risk  ││
│  │  Agent   │  │  Agent   │  │ Agent  ││
│  └──────────┘  └──────────┘  └────────┘│
└─────────────────┬───────────────────────┘
                  │
                  ▼
         ┌────────────────────┐
         │  Export Results    │
         │ (Excel/JSON/HTML)  │
         └────────────────────┘
```

---

## 📊 Output Formats

### Excel Spreadsheet
- Filterable columns
- Category grouping
- Priority levels
- Source traceability
- SAP module mapping

### JSON
- Machine-readable
- API integration
- Custom processing
- Complete metadata

### Markdown
- Human-readable
- Version control friendly
- Easy sharing
- Documentation ready

### HTML
- Interactive viewer
- Collapsible sections
- Search and filter
- Source links

---

## 🔧 Configuration

### Environment Variables

There is **one** `.env` file at `common/.env`. Both services read from it — you do not need separate `.env` files per module.

```bash
# LLM Provider — IBM Services Essentials (OpenAI-compatible)
OPENAI_API_KEY=your_services_essentials_key_here
OPENAI_API_BASE=https://servicesessentials.ibm.com/apis/v3
MODEL_ID=global/anthropic.claude-sonnet-4-5-20250929-v1:0

# Optional: bypass Services Essentials and call Anthropic directly (Phase 0 only)
ANTHROPIC_API_KEY=

# Application Settings
LOG_LEVEL=INFO

# Phase 0 Settings
PHASE0_CONFIDENCE_THRESHOLD=0.70
PHASE0_MAX_CHUNKS_PER_DOC=80

# Feature Flags
ENABLE_SAP_MAPPING=true
ENABLE_RISK_ASSESSMENT=true
```

See [`common/.env.template`](common/.env.template) for the complete, commented list of options, including optional Context Studio, observability (Arize Phoenix), and MCP gateway settings.

---

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific tests
pytest tests/unit/
pytest tests/integration/

# Run with markers
pytest -m "not slow"
```

---

## 🐳 Docker Deployment

```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

See [Docker Guide](docs/DOCKER_GUIDE.md) for detailed instructions.

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy pre-commit

# Install pre-commit hooks
pre-commit install

# Run code quality checks
black .
flake8 .
mypy .
```

---

## 📈 Roadmap

- [ ] Enhanced test coverage (>80%)
- [ ] Multi-language support
- [ ] Advanced visualization features
- [ ] PDF password protection support
- [ ] Real-time collaboration features
- [ ] Cloud deployment templates
- [ ] Integration with project management tools

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Anthropic Claude** - Language model powering all agents (via IBM Services Essentials)
- **LangChain** - LLM orchestration framework
- **FastAPI** - Modern web framework
- **All Contributors** - Thank you for your contributions!

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/santosh-k-singh10/RFxStarterKit-0.2/issues)
- **Discussions**: [GitHub Discussions](https://github.com/santosh-k-singh10/RFxStarterKit-0.2/discussions)

---

## 📊 Project Stats

- **Version**: 0.2.0
- **Status**: Internal Pilot
- **Last Updated**: 2026-07-06
- **Python**: 3.8+
- **License**: MIT

---

<div align="center">

**[Documentation](docs/)** • **[Quick Start](docs/QUICK_START.md)** • **[Contributing](CONTRIBUTING.md)** • **[Changelog](CHANGELOG.md)**

Made with ❤️ by the RFxStarterKit team

</div>
