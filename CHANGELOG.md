# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0-pilot] - branch: pilot-no-scoping-architect

### Removed
- **scoping-architect** module fully removed (folder, Dockerfile, docker-compose service, all proxy routes in rfp-analyzer, all UI tabs, all docs and config references).
- `Dockerfile.scoping-architect` deleted.
- `CLEANUP_SCRIPT.bat` deleted (was scoping-architect-only).
- Five `docs/archive/` files referencing the removed module deleted.
- `import httpx` removed from `rfp-analyzer/web_app.py` (was only used by scoping proxy routes).
- `🧩 Scoping Questionnaire` and `🏗️ Generate Scope` tabs removed from both UI surfaces (`web_app.py` and `rfp_analyzer_direct.html`).

### Notes
- This is a pilot variant of v0.1.0 — the `master` branch retains the full scoping-architect integration.
- Only the **RFP Analyzer** service (port 8080) and **document-consolidator / Phase 0** remain.

## [Unreleased]

### Planned
- Docker support for easier deployment
- CI/CD pipeline with GitHub Actions
- Comprehensive test suite
- API documentation improvements

## [0.1.0] - 2026-07-03

### Added
- **Initial release of RFxStarterKit**
- **RFP Analyzer** - Multi-agent system for RFP analysis
  - Functional requirements extraction
  - Non-functional requirements identification
  - Compliance checking
  - Risk assessment
  - Ambiguity detection
  - Multi-format support (PDF, DOCX, TXT, MD, XLSX, CSV)
  
- **Phase 0 Document Router** - Multi-document processing
  - Document classification by type
  - Conflict detection across documents
  - Semantic chunking
  - Source traceability
  - Confidence scoring
  
- **Scoping Architect** - Solution scoping and architecture
  - Automated scoping from requirements
  - Architecture recommendations
  - Component identification
  - Effort estimation
  - Risk analysis
  
- **Multi-LLM Support**
  - OpenAI (GPT-4, GPT-3.5-turbo)
  - Anthropic (Claude)
  - Google AI (Gemini)
  - Unified authentication via .env configuration
  
- **Web Interface**
  - Document upload and analysis
  - Real-time progress tracking
  - Multiple export formats
  - Interactive results viewer
  
- **Export Capabilities**
  - Excel spreadsheets with filtering
  - JSON for API integration
  - Markdown reports
  - HTML with collapsible sections
  - SAP module mapping (optional)
  
- **SAP Integration**
  - SAP module mapping for requirements
  - SAP-specific analysis modes
  - Module-based grouping in exports
  
- **Documentation**
  - Comprehensive README
  - Quick start guide
  - Integrated system guide
  - API documentation
  - Configuration templates

### Features
- Multi-document RFP analysis with Phase 0 router
- Automated requirement extraction with confidence scoring
- Compliance checking against multiple frameworks
- Risk assessment with mitigation strategies
- Ambiguity detection and clarification suggestions
- Source traceability back to original documents
- Conflict detection across multiple documents
- SAP module mapping for SAP opportunities
- Web-based interface for easy access
- CLI interface for automation
- Programmatic API for integration

### Technical
- Python 3.8+ support
- FastAPI-based REST API
- LangGraph for agent orchestration
- Pydantic for data validation
- Structured logging with structlog
- Checkpoint-based state management
- Async/await for performance
- Type hints throughout codebase

### Documentation
- MIT License
- Contributing guidelines
- Environment configuration template
- Comprehensive README with examples
- Quick start guide
- Architecture documentation
- API reference

### Infrastructure
- Modular architecture (rfp-analyzer, document-consolidator)
- Shared common dependencies
- Unified configuration management
- Logging and observability
- Error handling and recovery

## [0.0.1] - 2026-06-01

### Added
- Initial project structure
- Basic RFP analysis prototype
- Proof of concept for multi-agent system

---

## Release Notes

### v0.1.0 - Initial Public Release

This is the first public release of RFxStarterKit, an AI-powered toolkit for RFP analysis and solution scoping.

**Key Highlights:**
- 🤖 Multi-agent AI system for comprehensive RFP analysis
- 📄 Support for multiple document formats and multi-document RFPs
- 🔍 Automated requirement extraction with high accuracy
- 📊 Multiple export formats for different use cases
- 🌐 Web interface for easy access
- 🔧 Extensible architecture for customization

**Getting Started:**
1. Clone the repository
2. Copy `.env.example` to `.env` and configure API keys
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: See `QUICK_START.md`

**Requirements:**
- Python 3.8 or higher
- OpenAI API key (required)
- Anthropic API key (optional, for Phase 0)

**Known Limitations:**
- Large documents (>100 pages) may take several minutes to process
- PDF password-protected files not yet supported
- Limited to English language documents

**Future Roadmap:**
- Docker containerization
- CI/CD pipeline
- Enhanced test coverage
- Multi-language support
- Advanced visualization features

For detailed documentation, see the `docs/` directory and `README.md`.

---

[Unreleased]: https://github.com/santosh-k-singh10/RFxStarterKit-0.1/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/santosh-k-singh10/RFxStarterKit-0.1/releases/tag/v0.1.0
[0.0.1]: https://github.com/santosh-k-singh10/RFxStarterKit-0.1/releases/tag/v0.0.1