# RFxStarterKit

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![CI Pipeline](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF)](https://github.com/santosh-k-singh10/RFxStarterKit-0.1/actions)
[![Docker](https://img.shields.io/badge/docker-ready-2496ED)](https://www.docker.com/)

> **AI-powered RFP analysis and solution scoping toolkit**

Transform RFP documents into actionable requirements and architectural designs using multi-agent AI systems.

---

## 🎯 Overview

RFxStarterKit is a comprehensive toolkit for analyzing Request for Proposals (RFPs) and generating solution architectures. It combines multiple AI agents to extract requirements, detect compliance issues, assess risks, and create detailed scoping documents.

### Key Capabilities

- 🤖 **Multi-Agent Analysis** - Specialized AI agents for different requirement types
- 📄 **Multi-Document Support** - Process complete RFP packages simultaneously
- 🔍 **Intelligent Extraction** - Automatic requirement extraction with confidence scoring
- ⚠️ **Conflict Detection** - Identify contradictions across multiple documents
- 📊 **Multiple Export Formats** - Excel, JSON, Markdown, and interactive HTML
- 🏗️ **Solution Scoping** - Generate architecture and component breakdowns
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

### Scoping Architect
- **Architecture Recommendations** - Suggest solution patterns
- **Component Identification** - Break down into buildable components
- **Effort Estimation** - Story point ranges for components
- **Risk Analysis** - Technical and implementation risks
- **Integration Planning** - Identify integration requirements

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# 1. Clone the repository
git clone https://github.com/santosh-k-singh10/RFxStarterKit-0.1.git
cd RFxStarterKit-0.1

# 2. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 3. Start with Docker
docker-compose up --build

# 4. Access services
# RFP Analyzer: http://localhost:8080
# Scoping Architect: http://localhost:8001
```

### Option 2: Local Installation

```bash
# 1. Clone the repository
git clone https://github.com/santosh-k-singh10/RFxStarterKit-0.1.git
cd RFxStarterKit-0.1

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Start the application
# Windows:
START_ALL.bat

# Linux/Mac:
./START_ALL.sh
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
- **OpenAI API Key** (required for RFP analysis)
- **Anthropic API Key** (optional, for Phase 0 multi-document processing)
- **4GB RAM minimum** (8GB recommended)
- **Docker** (optional, for containerized deployment)

---

## 📖 Documentation

| Document | Description |
|----------|-------------|
| [Quick Start](docs/QUICK_START.md) | Installation, running, and troubleshooting |
| [Architecture](docs/ARCHITECTURE.md) | System design, data-flow diagrams, repo structure |
| [API Reference](docs/API_REFERENCE.md) | REST endpoints for RFP Analyzer, Phase 0, and Scoping Architect |
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
         │ Scoping Architect  │
         │  (Architecture)    │
         └────────────────────┘
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

```bash
# LLM Provider (openai, anthropic, google)
LLM_PROVIDER=openai

# API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# Application Settings
LOG_LEVEL=INFO
OUTPUT_DIR=./outputs
MIN_CONFIDENCE=0.0

# Phase 0 Settings
PHASE0_CONFIDENCE_THRESHOLD=0.70
PHASE0_MAX_CHUNKS_PER_DOC=80

# Feature Flags
ENABLE_SAP_MAPPING=true
ENABLE_RISK_ASSESSMENT=true
```

See [.env.example](.env.example) for complete configuration options.

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

- **OpenAI GPT-4** - Language model for analysis
- **Anthropic Claude** - Language model for classification
- **LangChain** - LLM orchestration framework
- **FastAPI** - Modern web framework
- **All Contributors** - Thank you for your contributions!

---

## 📞 Support

- **Documentation**: [docs/](docs/)
- **Issues**: [GitHub Issues](https://github.com/santosh-k-singh10/RFxStarterKit-0.1/issues)
- **Discussions**: [GitHub Discussions](https://github.com/santosh-k-singh10/RFxStarterKit-0.1/discussions)

---

## 📊 Project Stats

- **Version**: 0.1.0
- **Status**: Production Ready ✅
- **Last Updated**: 2026-07-03
- **Python**: 3.8+
- **License**: MIT

---

<div align="center">

**[Documentation](docs/)** • **[Quick Start](QUICK_START.md)** • **[Contributing](CONTRIBUTING.md)** • **[Changelog](CHANGELOG.md)**

Made with ❤️ by the RFxStarterKit team

</div>