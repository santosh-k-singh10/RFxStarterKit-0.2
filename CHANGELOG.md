# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0-pilot] - branch: pilot-no-scoping-architect

### Changed
- **env**: consolidated all `.env` files into `common/.env` as single source of truth; removed root `.env.example` and `rfp-analyzer/.env.example`; updated all `load_dotenv()` call sites to point at `common/.env`
- **deps**: rewrote root `requirements.txt` as `-r` composition file; removed `pytest`/`pytest-asyncio` from `common/requirements-base.txt` (already in `pyproject.toml [dev]`); added missing `pypdf` to `rfp-analyzer/requirements.txt`
- **docker**: fixed `docker-compose.yml` — removed unbuildable `scoping-architect` service, fixed healthcheck endpoint (`/` not `/health`), stripped dead env vars, removed orphan named volumes
- **web_app**: replaced deprecated `@app.on_event('startup')` with FastAPI `lifespan` context manager
- **docs**: updated `README.md`, `CONTRIBUTING.md`, `QUICK_START.md`, `ARCHITECTURE.md`, `API_REFERENCE.md`, `DOCKER_GUIDE.md`, `rfp-analyzer/README.md` — corrected repo URLs, env paths, API key guidance
- **scripts**: added `START_ALL.sh` (Linux/Mac); fixed env path in all launchers
- **pyproject.toml**: updated all URLs and version to `0.2.0`

### Removed
- `debug_json_error_attempt_1.txt` (×2), `github-checkin-plan.md`, `backup_20260703_195456/` (54 files)
- `rfp-analyzer/agents/sap_mapping_agent.py`, `rfp-analyzer/sap_analyzer_app.py`, `rfp-analyzer/sap_analyzer_cli.py`
- `rfp-analyzer/SAP_ANALYZER_README.md`
- `is_sap_opp` parameter removed from `web_app.py` API, functions, and UI
- Stale `.env.example` exception removed from `.gitignore`; `rfp-analyzer/app/uploads/` added

### Notes
- This is a pilot variant of v0.2.0 — the `master` branch retains the full scoping-architect integration.
- Only the **RFP Analyzer** service (port 8080) and **document-consolidator / Phase 0** remain.

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
2. Copy `common/.env.template` to `common/.env` and set `OPENAI_API_KEY` to your IBM Services Essentials token
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: See `docs/QUICK_START.md`

**Requirements:**
- Python 3.8 or higher
- IBM Services Essentials API key (required — used as `OPENAI_API_KEY`)
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

[Unreleased]: https://github.com/santosh-k-singh10/RFxStarterKit-0.2/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/santosh-k-singh10/RFxStarterKit-0.2/releases/tag/v0.2.0
[0.1.0]: https://github.com/santosh-k-singh10/RFxStarterKit-0.2/releases/tag/v0.1.0
[0.0.1]: https://github.com/santosh-k-singh10/RFxStarterKit-0.2/releases/tag/v0.0.1