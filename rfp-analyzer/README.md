# RFP Analyzer - Multi-Agent System

An intelligent RFP (Request for Proposal) analysis system built with LangGraph and Claude AI that automatically extracts and categorizes requirements from proposal documents.

## Features

- **Multi-Agent Architecture**: Specialized agents for different requirement types
- **Semantic Chunking**: Intelligent document parsing that respects section structure
- **5 Specialized Agents**:
  - Functional Requirements Extractor
  - Non-Functional Requirements Extractor
  - Compliance & Regulatory Requirements Extractor
  - Ambiguity Detector
  - Risk Assessor
- **Comprehensive Output**: Markdown reports with traceability matrix
- **Confidence Scoring**: Each requirement includes a confidence score
- **Clarification Questions**: Automatically generates questions for ambiguous requirements
- **Organizational Context**: Customize analysis with your organization's standards, tech stack, and compliance requirements
- **Remote Context Loading**: Load organizational context from SharePoint, OneDrive, Box, S3, or HTTP

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     RFP Document (DOCX)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          Stage 1: Ingestion & Chunking                       │
│          ├─ Parse DOCX                                       │
│          └─ Semantic Section Detection                       │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          Stage 2: Orchestrator Agent (ReAct)                 │
│          ├─ Analyze each chunk                               │
│          └─ Route to appropriate sub-agents                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          Stage 3: Specialized Sub-Agents                     │
│          ├─ Functional Requirements                          │
│          ├─ Non-Functional Requirements                      │
│          ├─ Compliance Requirements                          │
│          ├─ Ambiguity Detection                              │
│          └─ Risk Assessment                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          Stage 4: Synthesis & Validation                     │
│          ├─ Deduplication                                    │
│          ├─ Cross-linking                                    │
│          └─ Confidence Validation                            │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│          Output: Markdown Report + Traceability Matrix       │
└─────────────────────────────────────────────────────────────┘
```

## Installation

1. **Install dependencies**
```bash
pip install -r requirements.txt
```

2. **Set up environment variables**

Create a `.env` file with your Anthropic API key:
```bash
cp .env.example .env
```

Edit `.env` and add your key:
```
ANTHROPIC_API_KEY=sk-ant-...
```

## Entry Points

| File | Purpose | How to run |
|------|---------|------------|
| **`web_app.py`** | ✅ **Production web UI** — upload RFP documents and review results in the browser | `uvicorn web_app:app --reload --port 8080` |
| `main.py` | CLI companion — batch / scripted analysis runs | `python main.py analyze rfp.pdf` |

**The single production entry point is `web_app.py`.**

```bash
# Start the web interface
uvicorn web_app:app --reload --port 8080
# Then open: http://localhost:8080
```

## Usage

### Web Interface (recommended)

```bash
uvicorn web_app:app --reload --port 8080
```

Open http://localhost:8080, upload your RFP document, and review the results.

### CLI (batch / scripted runs)

```bash
python main.py analyze path/to/rfp.pdf
python main.py analyze path/to/rfp.pdf --output-dir ./results --title "Project Alpha"
python main.py analyze path/to/rfp.pdf --no-excel --no-markdown
python main.py analyze path/to/rfp.pdf --thread-id my-run-1   # resume interrupted run
```

### Using Organizational Context

Customize the analysis with your organization's standards:

```bash
# Local context file
python main.py rfp.pdf --org-context org_context/config/org_config.yaml

# Remote context from SharePoint
python main.py rfp.pdf --org-context "https://company.sharepoint.com/sites/team/Shared Documents/org_config.yaml"

# Remote context from OneDrive
python main.py rfp.pdf --org-context "https://company-my.sharepoint.com/personal/user/Documents/org_config.yaml"
```

Set up credentials for remote loading:

```bash
# SharePoint
export SHAREPOINT_CLIENT_ID="your-client-id"
export SHAREPOINT_CLIENT_SECRET="your-client-secret"
export SHAREPOINT_TENANT_ID="your-tenant-id"

# OneDrive
export ONEDRIVE_ACCESS_TOKEN="your-access-token"

# Box
export BOX_ACCESS_TOKEN="your-access-token"

# S3
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```

For detailed setup instructions, see [REMOTE_CONTEXT_GUIDE.md](REMOTE_CONTEXT_GUIDE.md).


### Programmatic Usage

```python
from rfp_analyzer import analyze_rfp

# Analyze an RFP document
success = analyze_rfp(
    document_path="path/to/rfp.docx",
    output_path="output.md"
)
```

## Output Format

The analyzer generates a comprehensive Markdown report with the following sections:

1. **Executive Summary**: Overview of extracted requirements
2. **Functional Requirements**: Features, integrations, user workflows
3. **Non-Functional Requirements**: Performance, security, scalability
4. **Compliance & Regulatory Requirements**: Standards, certifications, audits
5. **Ambiguities & Clarification Questions**: Issues needing clarification
6. **Risk Assessment**: Identified risks with mitigation strategies
7. **Requirements Traceability Matrix**: Complete mapping with source references

Each requirement includes:
- Unique ID for tracking
- Clear description
- Source section and page reference
- Priority level (high/medium/low)
- Confidence score (0.0-1.0)
- Ambiguity flag

## Technical Stack

- **LangGraph**: State machine for orchestrating multi-agent workflow
- **Claude 3.5 Sonnet**: LLM for intelligent requirement extraction
- **python-docx**: Document parsing
- **Pydantic**: Data validation and structured outputs

## Project Structure

```
c:/ClineVsCode/
├── rfp_analyzer.py          # Main analyzer with multi-agent system
├── create_mock_rfp.py       # Script to generate sample RFP
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variable template
├── README.md               # This file
├── sample_rfp.docx         # Generated mock RFP (after running create_mock_rfp.py)
└── rfp_analysis.md         # Generated analysis output
```

## How It Works

### Stage 1: Document Ingestion
- Parses DOCX file using python-docx
- Detects section headings through style analysis
- Creates semantic chunks with metadata (section, page, content)

### Stage 2: Orchestrator (ReAct Loop)
- Analyzes each chunk with Claude
- Determines which requirement categories apply
- Routes to appropriate specialized agents
- Avoids redundant processing

### Stage 3: Specialized Sub-Agents
Each agent has a focused system prompt and structured JSON output:
- **Functional Agent**: Extracts features, workflows, integrations
- **Non-Functional Agent**: Identifies SLAs, performance, security
- **Compliance Agent**: Detects regulatory requirements
- **Ambiguity Detector**: Flags vague language, generates clarification questions
- **Risk Scorer**: Assesses complexity, timeline, and feasibility risks

### Stage 4: Synthesis & Validation
- Deduplicates similar requirements
- Cross-references related requirements
- Validates confidence scores
- Checks for internal conflicts

## Advanced Features

### Confidence Scoring
Each requirement includes a self-assessed confidence score:
- **>0.7**: High confidence, clear requirement
- **0.5-0.7**: Medium confidence, may need review
- **<0.5**: Low confidence, flagged as ambiguous

### Ambiguity Detection
Automatically identifies:
- Vague terms ("reasonable", "as needed", "appropriate")
- Undefined acronyms or technical terms
- Contradictory statements
- Missing critical specifications
- Overly broad requirements

### Risk Assessment
Evaluates and categorizes risks:
- **Complexity**: Technical challenges, unknowns
- **Timeline**: Unrealistic deadlines, dependencies
- **Resource**: Staffing or budget constraints
- **Scope**: Open-ended or unbounded requirements
- **Dependency**: Integration or vendor dependencies

## Customization

### Modifying Agent Prompts
Edit system prompts in `rfp_analyzer.py` for each agent function:
- `extract_functional()`
- `extract_non_functional()`
- `extract_compliance()`
- `detect_ambiguity()`
- `score_risk()`

### Changing LLM Model
Update the model in `rfp_analyzer.py`:
```python
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",  # Change model here
    temperature=0,
    max_tokens=4096
)
```

### Output Format
Modify `generate_markdown_output()` to customize report structure.

## Future Enhancements

- [ ] Add Excel export with traceability matrix
- [ ] Implement RAG-based verification to reduce hallucinations
- [ ] Add embedding-based deduplication
- [ ] Support PDF input files
- [ ] Add web interface
- [ ] Include cost estimation agent
- [ ] Add multi-RFP comparison mode
- [ ] Implement human-in-the-loop review workflow
- [ ] Add checkpoint/resume capability for long documents

## Troubleshooting

### API Key Issues
```bash
# Verify your API key is set
echo $ANTHROPIC_API_KEY

# On Windows
echo %ANTHROPIC_API_KEY%
```

### Import Errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --upgrade
```

### Document Parsing Issues
- Ensure the RFP is in .docx format (not .doc)
- Check that document isn't password protected
- Verify file isn't corrupted

## License

MIT License - Feel free to use and modify for your needs.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request with clear description

## Acknowledgments

Built with:
- LangGraph by LangChain
- Claude AI by Anthropic
- python-docx library

---

**Note**: This is a production-ready implementation based on the architectural plan provided. The system uses Claude's structured output capabilities with JSON schema enforcement for reliable extraction.
