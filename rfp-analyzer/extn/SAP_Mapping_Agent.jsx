import { useState, useCallback } from "react";

const SAMPLE_MARKDOWN = `# RFP Requirements — Enterprise ERP Implementation

## Functional Requirements

### Finance & Accounting
FR-001: The system shall manage accounts payable including invoice processing, payment runs, and vendor reconciliation
FR-002: The system shall support general ledger accounting with real-time postings and period-end closing
FR-003: The system shall handle fixed asset accounting including acquisition, depreciation calculation, and disposal
FR-004: The system shall support cost center accounting and internal order management with variance analysis
FR-005: The system shall generate financial statements including P&L, balance sheet, and cash flow statement

### Procurement
FR-006: The system shall manage purchase requisitions with multi-level approval workflows
FR-007: The system shall support request for quotation (RFQ) and supplier bid comparison and evaluation
FR-008: The system shall handle purchase order creation, goods receipt, and 3-way invoice matching
FR-009: The system shall manage vendor master data including onboarding, qualification, and rating
FR-010: The system shall support contract management, blanket purchase orders, and scheduling agreements

### Sales & Order Management
FR-011: The system shall manage customer master data, credit limits, and dunning procedures
FR-012: The system shall support sales order processing including pricing conditions and ATP check
FR-013: The system shall handle delivery processing, picking, packing, shipping, and goods issue
FR-014: The system shall manage customer invoicing, billing plans, and accounts receivable
FR-015: The system shall support returns processing, credit memo management, and debit memos

### Inventory & Warehouse
FR-016: The system shall manage material master data across multiple plants and storage locations
FR-017: The system shall support bin management, transfer orders, and put-away strategies
FR-018: The system shall handle goods movements including receipts, transfers, and issues
FR-019: The system shall support inventory valuation (FIFO, moving average) and physical inventory
FR-020: The system shall manage batch and serial number tracking for regulated materials

### Human Resources
FR-021: The system shall manage employee master data, org structure, positions, and job families
FR-022: The system shall support payroll processing including statutory deductions, taxes, and bank transfers
FR-023: The system shall handle leave management, time recording, and absence quota management
FR-024: The system shall support performance management, goal setting, and 360-degree feedback

## Non-Functional Requirements
NFR-001: The system shall achieve 99.9% availability during business hours with planned maintenance windows
NFR-002: The system shall support 500 concurrent users with page response times under 3 seconds
NFR-003: The system shall comply with SOX, GDPR, and local statutory tax reporting requirements
NFR-004: The system shall integrate with the existing legacy HR system via REST APIs during transition
NFR-005: All data must be encrypted at rest (AES-256) and in transit (TLS 1.3)
NFR-006: The solution must be deployable on Microsoft Azure cloud infrastructure in the EU region
NFR-007: The system shall support single sign-on via Microsoft Azure Active Directory using SAML 2.0`;

const MODULE_META = {
  FI:    { name: "Financial Accounting",        color: "#185FA5", bg: "#E6F1FB", text: "#0C447C" },
  CO:    { name: "Controlling",                 color: "#0C447C", bg: "#D0E8F7", text: "#042C53" },
  MM:    { name: "Materials Management",        color: "#854F0B", bg: "#FAEEDA", text: "#633806" },
  SD:    { name: "Sales & Distribution",        color: "#0F6E56", bg: "#E1F5EE", text: "#085041" },
  PP:    { name: "Production Planning",         color: "#534AB7", bg: "#EEEDFE", text: "#3C3489" },
  QM:    { name: "Quality Management",          color: "#3C3489", bg: "#E5E4FC", text: "#26215C" },
  PM:    { name: "Plant Maintenance",           color: "#993C1D", bg: "#FAECE7", text: "#712B13" },
  WM:    { name: "Warehouse Management",        color: "#633806", bg: "#FFF0D9", text: "#412402" },
  EWM:   { name: "Extended Warehouse Mgmt",     color: "#854F0B", bg: "#FAEEDA", text: "#633806" },
  PS:    { name: "Project System",              color: "#712B13", bg: "#FDECEA", text: "#4A1B0C" },
  HCM:   { name: "Human Capital Management",    color: "#993556", bg: "#FBEAF0", text: "#72243E" },
  SF:    { name: "SuccessFactors",              color: "#D4537E", bg: "#F9D5E5", text: "#993556" },
  BTP:   { name: "Business Technology Platform",color: "#444441", bg: "#F1EFE8", text: "#2C2C2A" },
  IS:    { name: "Integration Suite",           color: "#5F5E5A", bg: "#E8E7E3", text: "#444441" },
  SAC:   { name: "SAP Analytics Cloud",         color: "#3B6D11", bg: "#EAF3DE", text: "#27500A" },
  ARIBA: { name: "SAP Ariba",                   color: "#185FA5", bg: "#E6F1FB", text: "#0C447C" },
  CX:    { name: "SAP Customer Experience",     color: "#1D9E75", bg: "#D8F3EA", text: "#0F6E56" },
};

const FIT_STYLE = {
  Standard:      { bg: "#E1F5EE", color: "#0F6E56", label: "Standard" },
  Configuration: { bg: "#E6F1FB", color: "#185FA5", label: "Config" },
  Enhancement:   { bg: "#FAEEDA", color: "#854F0B", label: "Enhancement" },
  Custom:        { bg: "#FAECE7", color: "#993C1D", label: "Custom" },
};

const CONF_COLOR = { High: "#0F6E56", Medium: "#854F0B", Low: "#993C1D" };
const CONF_BG    = { High: "#E1F5EE", Medium: "#FAEEDA", Low: "#FAECE7" };

const CAT_STYLE = {
  Infrastructure: { bg: "#F1EFE8", color: "#444441" },
  Security:       { bg: "#FAECE7", color: "#993C1D" },
  Compliance:     { bg: "#FAEEDA", color: "#854F0B" },
  Integration:    { bg: "#EEEDFE", color: "#534AB7" },
  Performance:    { bg: "#E6F1FB", color: "#185FA5" },
  "UI/UX":        { bg: "#FBEAF0", color: "#993556" },
  Other:          { bg: "#F1EFE8", color: "#5F5E5A" },
};

const SYSTEM_PROMPT = `You are a Senior SAP Solution Architect with 20+ years of experience across SAP S/4HANA, SAP ECC, SAP BTP, SAP SuccessFactors, SAP Ariba, and SAP CX. You map business requirements to SAP modules and identify gaps.

SAP modules you know deeply:
- FI (Financial Accounting), CO (Controlling), MM (Materials Management), SD (Sales & Distribution)
- PP (Production Planning), QM (Quality Management), PM (Plant Maintenance), PS (Project System)
- WM / EWM (Warehouse Management), HCM (Human Capital Management)
- SF (SuccessFactors), ARIBA (SAP Ariba), CX (SAP Customer Experience / C4C)
- SAC (SAP Analytics Cloud), BTP (Business Technology Platform), IS (SAP Integration Suite)

Standard SAP business processes you reference: Procure-to-Pay (P2P), Order-to-Cash (O2C), Record-to-Report (R2R), Hire-to-Retire (H2R), Plan-to-Produce (PtP), Acquire-to-Retire (A2R), Warehouse Management, Project Management, Financial Close.

For each requirement:
1. Identify the correct SAP module and sub-area
2. Assess fit: Standard (out-of-box), Configuration (IMG/config needed), Enhancement (user-exit/BADI/exit), Custom (Z-development)
3. Confidence: High (clear SAP fit), Medium (partial or overlapping fit), Low (ambiguous or unusual)
4. Group requirements into standard SAP business process groups
5. Flag non-SAP requirements (infrastructure, security, compliance, performance, UI/UX, integration with non-SAP systems)

RULES:
- Return ONLY valid JSON, no markdown fences, no explanation text whatsoever
- Every requirement from the input must appear exactly once
- Non-functional, infrastructure, and compliance requirements go in nonSapRequirements
- fitNotes max 12 words, specific and implementation-focused
- recommendation max 12 words

JSON structure to return:
{
  "summary": {
    "totalRequirements": <int>,
    "sapMapped": <int>,
    "nonSap": <int>,
    "modules": ["FI","MM",...],
    "processGroupCount": <int>
  },
  "processGroups": [
    {
      "id": "PG-001",
      "name": "<group name>",
      "description": "<one sentence>",
      "businessProcess": "<standard SAP process name>",
      "primaryModule": "<code>",
      "primaryModuleName": "<full name>",
      "supportingModules": [{"code":"CO","name":"Controlling"}],
      "requirements": [
        {
          "id": "<req id>",
          "text": "<original text, max 140 chars>",
          "primaryModule": "<code>",
          "subModule": "<sub-area>",
          "fit": "Standard|Configuration|Enhancement|Custom",
          "fitNotes": "<max 12 words>",
          "confidence": "High|Medium|Low"
        }
      ]
    }
  ],
  "nonSapRequirements": [
    {
      "id": "<req id>",
      "text": "<original text, max 140 chars>",
      "category": "Infrastructure|Security|Compliance|Integration|Performance|UI/UX|Other",
      "recommendation": "<max 12 words>"
    }
  ]
}`;

function ModuleBadge({ code, small }) {
  const m = MODULE_META[code] || { name: code, color: "#5F5E5A", bg: "#F1EFE8", text: "#444441" };
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 4,
      background: m.bg, color: m.text,
      border: `1px solid ${m.color}33`,
      borderRadius: 6, padding: small ? "1px 7px" : "3px 9px",
      fontSize: small ? 11 : 12, fontWeight: 500, whiteSpace: "nowrap",
    }}>{code}</span>
  );
}

function FitBadge({ fit }) {
  const s = FIT_STYLE[fit] || FIT_STYLE.Standard;
  return (
    <span style={{
      background: s.bg, color: s.color,
      borderRadius: 5, padding: "1px 7px",
      fontSize: 11, fontWeight: 500, whiteSpace: "nowrap",
    }}>{s.label}</span>
  );
}

function ConfDot({ conf }) {
  return (
    <span style={{
      display: "inline-flex", alignItems: "center", gap: 4,
      fontSize: 11, color: CONF_COLOR[conf] || "#5F5E5A",
      background: CONF_BG[conf] || "#F1EFE8",
      borderRadius: 4, padding: "1px 6px", fontWeight: 500,
    }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: CONF_COLOR[conf], display: "inline-block" }} />
      {conf}
    </span>
  );
}

function CatBadge({ cat }) {
  const s = CAT_STYLE[cat] || CAT_STYLE.Other;
  return (
    <span style={{ background: s.bg, color: s.color, borderRadius: 5, padding: "1px 7px", fontSize: 11, fontWeight: 500 }}>
      {cat}
    </span>
  );
}

function StatCard({ label, value, sub, accent }) {
  return (
    <div style={{
      background: "var(--color-background-secondary)",
      borderRadius: "var(--border-radius-md)",
      padding: "12px 14px",
      display: "flex", flexDirection: "column", gap: 2,
      border: accent ? `1.5px solid ${accent}` : "0.5px solid var(--color-border-tertiary)",
    }}>
      <span style={{ fontSize: 11, color: "var(--color-text-secondary)", fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.04em" }}>{label}</span>
      <span style={{ fontSize: 26, fontWeight: 500, color: accent || "var(--color-text-primary)", lineHeight: 1.1 }}>{value}</span>
      {sub && <span style={{ fontSize: 11, color: "var(--color-text-tertiary)" }}>{sub}</span>}
    </div>
  );
}

function ProcessGroupCard({ group, isOpen, onToggle }) {
  const m = MODULE_META[group.primaryModule] || { name: group.primaryModule, color: "#5F5E5A", bg: "#F1EFE8", text: "#444441" };
  return (
    <div style={{
      border: "0.5px solid var(--color-border-tertiary)",
      borderRadius: "var(--border-radius-lg)",
      overflow: "hidden",
      marginBottom: 8,
    }}>
      <button
        onClick={onToggle}
        style={{
          width: "100%", display: "flex", alignItems: "center", gap: 12,
          padding: "12px 16px", background: "var(--color-background-primary)",
          border: "none", cursor: "pointer", textAlign: "left",
        }}
      >
        <div style={{
          width: 36, height: 36, borderRadius: 8,
          background: m.bg, display: "flex", alignItems: "center", justifyContent: "center",
          border: `1px solid ${m.color}33`, flexShrink: 0,
        }}>
          <span style={{ fontSize: 11, fontWeight: 700, color: m.text }}>{group.primaryModule}</span>
        </div>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span style={{ fontSize: 14, fontWeight: 500, color: "var(--color-text-primary)" }}>{group.name}</span>
            <span style={{ fontSize: 11, color: m.color, background: m.bg, border: `1px solid ${m.color}33`, borderRadius: 4, padding: "1px 6px" }}>{group.businessProcess}</span>
          </div>
          <div style={{ fontSize: 12, color: "var(--color-text-secondary)", marginTop: 2, display: "flex", alignItems: "center", gap: 8 }}>
            <span>{group.requirements.length} requirement{group.requirements.length !== 1 ? "s" : ""}</span>
            {group.supportingModules?.length > 0 && (
              <>
                <span style={{ color: "var(--color-border-secondary)" }}>·</span>
                <span>Also: {group.supportingModules.map(s => s.code).join(", ")}</span>
              </>
            )}
          </div>
        </div>
        <i className={`ti ${isOpen ? "ti-chevron-up" : "ti-chevron-down"}`} style={{ fontSize: 16, color: "var(--color-text-tertiary)", flexShrink: 0 }} aria-hidden="true" />
      </button>

      {isOpen && (
        <div style={{ borderTop: "0.5px solid var(--color-border-tertiary)", padding: "0 0 4px" }}>
          <div style={{ padding: "8px 16px", background: "var(--color-background-secondary)" }}>
            <span style={{ fontSize: 12, color: "var(--color-text-secondary)" }}>{group.description}</span>
          </div>
          {group.requirements.map((req, i) => (
            <div key={req.id} style={{
              padding: "10px 16px",
              borderTop: i > 0 ? "0.5px solid var(--color-border-tertiary)" : "none",
              display: "grid",
              gridTemplateColumns: "64px 1fr auto",
              gap: 10, alignItems: "start",
            }}>
              <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--color-text-tertiary)", paddingTop: 2 }}>{req.id}</span>
              <div>
                <p style={{ margin: 0, fontSize: 13, color: "var(--color-text-primary)", lineHeight: 1.5 }}>{req.text}</p>
                <div style={{ display: "flex", gap: 6, marginTop: 5, flexWrap: "wrap", alignItems: "center" }}>
                  <ModuleBadge code={req.primaryModule} small />
                  {req.subModule && <span style={{ fontSize: 11, color: "var(--color-text-secondary)" }}>{req.subModule}</span>}
                  <FitBadge fit={req.fit} />
                  {req.fitNotes && <span style={{ fontSize: 11, color: "var(--color-text-tertiary)" }}>{req.fitNotes}</span>}
                </div>
              </div>
              <ConfDot conf={req.confidence} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function SAPMappingAgent() {
  const [input, setInput] = useState("");
  const [inputType, setInputType] = useState("markdown");
  const [loading, setLoading] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [openGroups, setOpenGroups] = useState({});
  const [copied, setCopied] = useState(false);
  const [activeTab, setActiveTab] = useState("groups");

  const LOADING_MSGS = [
    "Parsing requirements...",
    "Identifying SAP business processes...",
    "Mapping to SAP modules...",
    "Assessing fit types...",
    "Grouping into process flows...",
    "Flagging non-SAP items...",
    "Finalising traceability matrix...",
  ];

  const analyze = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setOpenGroups({});

    let msgIdx = 0;
    setLoadingMsg(LOADING_MSGS[0]);
    const interval = setInterval(() => {
      msgIdx = (msgIdx + 1) % LOADING_MSGS.length;
      setLoadingMsg(LOADING_MSGS[msgIdx]);
    }, 2200);

    try {
      const userContent = inputType === "json"
        ? `Map these requirements to SAP modules:\n\`\`\`json\n${trimmed}\n\`\`\``
        : `Map these requirements to SAP modules:\n\n${trimmed}`;

      const res = await fetch("https://api.anthropic.com/v1/messages", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          model: "claude-sonnet-4-20250514",
          max_tokens: 8000,
          system: SYSTEM_PROMPT,
          messages: [{ role: "user", content: userContent }],
        }),
      });

      const data = await res.json();
      const raw = data.content?.find(b => b.type === "text")?.text || "";
      const cleaned = raw.replace(/^```(?:json)?\s*/i, "").replace(/\s*```$/i, "").trim();
      const parsed = JSON.parse(cleaned);

      // Default first group open
      const initial = {};
      parsed.processGroups?.forEach((g, i) => { if (i === 0) initial[g.id] = true; });
      setOpenGroups(initial);
      setResult(parsed);
    } catch (e) {
      setError("Could not parse SAP mapping response. Check input format and try again. " + e.message);
    } finally {
      clearInterval(interval);
      setLoading(false);
    }
  }, [input, inputType]);

  const loadSample = () => {
    setInput(SAMPLE_MARKDOWN);
    setInputType("markdown");
    setResult(null);
    setError(null);
  };

  const copyJSON = () => {
    if (!result) return;
    navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const toggleGroup = (id) => setOpenGroups(p => ({ ...p, [id]: !p[id] }));
  const expandAll = () => {
    const all = {};
    result?.processGroups?.forEach(g => { all[g.id] = true; });
    setOpenGroups(all);
  };
  const collapseAll = () => setOpenGroups({});

  const moduleStats = result ? result.summary.modules.map(code => {
    const count = result.processGroups
      .filter(g => g.primaryModule === code)
      .reduce((a, g) => a + g.requirements.length, 0);
    return { code, count };
  }).filter(m => m.count > 0).sort((a, b) => b.count - a.count) : [];

  const maxModuleCount = moduleStats.reduce((a, m) => Math.max(a, m.count), 1);

  const fitCounts = result ? result.processGroups.flatMap(g => g.requirements).reduce((acc, r) => {
    acc[r.fit] = (acc[r.fit] || 0) + 1;
    return acc;
  }, {}) : {};

  return (
    <div style={{ padding: "1rem 0", maxWidth: 720 }}>
      <h2 className="sr-only">SAP Requirements Mapping Agent — paste markdown or JSON requirements to map them to SAP modules and business processes</h2>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
        <div style={{
          width: 40, height: 40, borderRadius: 10,
          background: "#E6F1FB", border: "1px solid #B5D4F4",
          display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
        }}>
          <i className="ti ti-map-2" style={{ fontSize: 20, color: "#185FA5" }} aria-hidden="true" />
        </div>
        <div>
          <p style={{ margin: 0, fontSize: 16, fontWeight: 500, color: "var(--color-text-primary)" }}>SAP Requirements Mapping Agent</p>
          <p style={{ margin: 0, fontSize: 12, color: "var(--color-text-secondary)" }}>Maps RFP traceability requirements to SAP modules, processes, and fit types</p>
        </div>
        <div style={{ marginLeft: "auto", display: "flex", gap: 6 }}>
          {["S/4HANA", "BTP", "SF"].map(tag => (
            <span key={tag} style={{
              fontSize: 10, padding: "2px 7px", borderRadius: 4, fontWeight: 500,
              background: "#E6F1FB", color: "#185FA5", border: "1px solid #B5D4F4",
            }}>{tag}</span>
          ))}
        </div>
      </div>

      {/* Input area */}
      <div style={{
        border: "0.5px solid var(--color-border-tertiary)",
        borderRadius: "var(--border-radius-lg)",
        overflow: "hidden",
        marginBottom: 12,
      }}>
        {/* Toolbar */}
        <div style={{
          display: "flex", alignItems: "center", gap: 0,
          borderBottom: "0.5px solid var(--color-border-tertiary)",
          background: "var(--color-background-secondary)",
        }}>
          {["markdown", "json"].map(t => (
            <button key={t} onClick={() => setInputType(t)} style={{
              padding: "8px 14px", border: "none", borderBottom: inputType === t ? "2px solid #185FA5" : "2px solid transparent",
              background: "transparent", cursor: "pointer",
              fontSize: 12, fontWeight: inputType === t ? 500 : 400,
              color: inputType === t ? "#185FA5" : "var(--color-text-secondary)",
              marginBottom: -1,
            }}>{t === "markdown" ? "Markdown" : "JSON"}</button>
          ))}
          <button onClick={loadSample} style={{
            marginLeft: "auto", display: "flex", alignItems: "center", gap: 5,
            padding: "6px 12px", border: "none", background: "transparent",
            cursor: "pointer", fontSize: 12, color: "var(--color-text-secondary)",
          }}>
            <i className="ti ti-file-text" style={{ fontSize: 14 }} aria-hidden="true" />
            Load sample ERP RFP
          </button>
        </div>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder={inputType === "markdown"
            ? "Paste requirements in Markdown format...\n\nFR-001: The system shall manage accounts payable...\nFR-002: The system shall support general ledger..."
            : '[\n  { "id": "FR-001", "text": "The system shall manage accounts payable..." },\n  { "id": "FR-002", "text": "..." }\n]'
          }
          style={{
            width: "100%", minHeight: 180, padding: "12px 14px",
            border: "none", background: "var(--color-background-primary)",
            fontSize: 12, fontFamily: inputType === "json" ? "var(--font-mono)" : "var(--font-sans)",
            color: "var(--color-text-primary)", resize: "vertical", outline: "none",
            boxSizing: "border-box", lineHeight: 1.6,
          }}
        />
        <div style={{
          display: "flex", justifyContent: "space-between", alignItems: "center",
          padding: "8px 12px", borderTop: "0.5px solid var(--color-border-tertiary)",
          background: "var(--color-background-secondary)",
        }}>
          <span style={{ fontSize: 11, color: "var(--color-text-tertiary)" }}>
            {input.trim() ? `${input.trim().split("\n").length} lines · ${input.trim().split(/\s+/).length} words` : "No input"}
          </span>
          <button
            onClick={analyze}
            disabled={loading || !input.trim()}
            style={{
              display: "flex", alignItems: "center", gap: 7,
              padding: "8px 18px", borderRadius: 8,
              background: loading || !input.trim() ? "var(--color-background-secondary)" : "#185FA5",
              color: loading || !input.trim() ? "var(--color-text-tertiary)" : "#fff",
              border: "0.5px solid var(--color-border-secondary)",
              cursor: loading || !input.trim() ? "not-allowed" : "pointer",
              fontSize: 13, fontWeight: 500, transition: "all 0.15s",
            }}
          >
            {loading
              ? <><i className="ti ti-loader-2" style={{ fontSize: 14, animation: "spin 1s linear infinite" }} aria-hidden="true" /> Analysing…</>
              : <><i className="ti ti-brain" style={{ fontSize: 14 }} aria-hidden="true" /> Map to SAP ↗</>
            }
          </button>
        </div>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>

      {/* Loading state */}
      {loading && (
        <div style={{
          display: "flex", alignItems: "center", gap: 10, padding: "14px 16px",
          background: "#E6F1FB", borderRadius: "var(--border-radius-md)",
          border: "0.5px solid #B5D4F4", marginBottom: 12,
        }}>
          <i className="ti ti-loader-2" style={{ fontSize: 18, color: "#185FA5", animation: "spin 1s linear infinite" }} aria-hidden="true" />
          <span style={{ fontSize: 13, color: "#185FA5" }}>{loadingMsg}</span>
        </div>
      )}

      {/* Error */}
      {error && (
        <div style={{
          padding: "12px 16px", background: "#FAECE7", border: "0.5px solid #F0997B",
          borderRadius: "var(--border-radius-md)", marginBottom: 12, fontSize: 13, color: "#993C1D",
          display: "flex", gap: 8, alignItems: "flex-start",
        }}>
          <i className="ti ti-alert-circle" style={{ fontSize: 16, flexShrink: 0, marginTop: 1 }} aria-hidden="true" />
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <>
          {/* Summary stats */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, minmax(0, 1fr))", gap: 8, marginBottom: 16 }}>
            <StatCard label="Total" value={result.summary.totalRequirements} sub="requirements" />
            <StatCard label="SAP mapped" value={result.summary.sapMapped} sub="requirements" accent="#185FA5" />
            <StatCard label="Non-SAP" value={result.summary.nonSap} sub="requirements" accent="#854F0B" />
            <StatCard label="Modules" value={result.summary.modules.length} sub="identified" />
            <StatCard label="Processes" value={result.summary.processGroupCount} sub="groups" />
          </div>

          {/* Fit breakdown */}
          {Object.keys(fitCounts).length > 0 && (
            <div style={{
              display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 12,
              padding: "10px 14px",
              background: "var(--color-background-secondary)",
              borderRadius: "var(--border-radius-md)",
              border: "0.5px solid var(--color-border-tertiary)",
              alignItems: "center",
            }}>
              <span style={{ fontSize: 11, fontWeight: 500, color: "var(--color-text-secondary)", marginRight: 4 }}>FIT BREAKDOWN</span>
              {Object.entries(fitCounts).map(([fit, count]) => {
                const s = FIT_STYLE[fit] || FIT_STYLE.Standard;
                return (
                  <span key={fit} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 12 }}>
                    <span style={{ background: s.bg, color: s.color, borderRadius: 4, padding: "1px 7px", fontWeight: 500 }}>{s.label}</span>
                    <span style={{ color: "var(--color-text-secondary)" }}>{count}</span>
                  </span>
                );
              })}
            </div>
          )}

          {/* Module coverage bars */}
          {moduleStats.length > 0 && (
            <div style={{
              padding: "12px 14px", marginBottom: 16,
              border: "0.5px solid var(--color-border-tertiary)",
              borderRadius: "var(--border-radius-lg)",
              background: "var(--color-background-primary)",
            }}>
              <p style={{ margin: "0 0 10px", fontSize: 11, fontWeight: 500, color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "0.04em" }}>Module coverage</p>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {moduleStats.map(({ code, count }) => {
                  const m = MODULE_META[code] || { name: code, color: "#5F5E5A", bg: "#F1EFE8" };
                  const pct = Math.round((count / maxModuleCount) * 100);
                  return (
                    <div key={code} style={{ display: "grid", gridTemplateColumns: "56px 1fr 24px", gap: 8, alignItems: "center" }}>
                      <span style={{ fontSize: 11, fontWeight: 600, color: m.color, fontFamily: "var(--font-mono)" }}>{code}</span>
                      <div style={{ height: 6, background: "var(--color-background-secondary)", borderRadius: 3, overflow: "hidden" }}>
                        <div style={{ height: "100%", width: `${pct}%`, background: m.color, borderRadius: 3, transition: "width 0.5s ease" }} />
                      </div>
                      <span style={{ fontSize: 11, color: "var(--color-text-tertiary)", textAlign: "right" }}>{count}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Tabs */}
          <div style={{ display: "flex", borderBottom: "0.5px solid var(--color-border-tertiary)", marginBottom: 12 }}>
            {[
              { id: "groups", label: "Process groups", icon: "ti-sitemap", count: result.processGroups.length },
              { id: "nonsap", label: "Non-SAP requirements", icon: "ti-plug-x", count: result.nonSapRequirements?.length || 0 },
            ].map(t => (
              <button key={t.id} onClick={() => setActiveTab(t.id)} style={{
                display: "flex", alignItems: "center", gap: 6,
                padding: "8px 14px", border: "none", background: "transparent",
                borderBottom: activeTab === t.id ? "2px solid #185FA5" : "2px solid transparent",
                color: activeTab === t.id ? "#185FA5" : "var(--color-text-secondary)",
                cursor: "pointer", fontSize: 13, fontWeight: activeTab === t.id ? 500 : 400,
                marginBottom: -1,
              }}>
                <i className={`ti ${t.icon}`} style={{ fontSize: 14 }} aria-hidden="true" />
                {t.label}
                <span style={{
                  fontSize: 11, padding: "0px 6px", borderRadius: 10,
                  background: activeTab === t.id ? "#E6F1FB" : "var(--color-background-secondary)",
                  color: activeTab === t.id ? "#185FA5" : "var(--color-text-secondary)",
                }}>{t.count}</span>
              </button>
            ))}
            <div style={{ marginLeft: "auto", display: "flex", gap: 4, alignItems: "center", paddingBottom: 2 }}>
              <button onClick={expandAll} style={{ fontSize: 11, color: "var(--color-text-secondary)", background: "none", border: "none", cursor: "pointer", padding: "4px 8px" }}>Expand all</button>
              <button onClick={collapseAll} style={{ fontSize: 11, color: "var(--color-text-secondary)", background: "none", border: "none", cursor: "pointer", padding: "4px 8px" }}>Collapse all</button>
              <button onClick={copyJSON} style={{
                display: "flex", alignItems: "center", gap: 5, fontSize: 11,
                padding: "4px 10px", borderRadius: 6,
                border: "0.5px solid var(--color-border-secondary)",
                background: "var(--color-background-secondary)",
                cursor: "pointer", color: "var(--color-text-secondary)",
              }}>
                <i className={`ti ${copied ? "ti-check" : "ti-copy"}`} style={{ fontSize: 12 }} aria-hidden="true" />
                {copied ? "Copied!" : "Export JSON"}
              </button>
            </div>
          </div>

          {/* Process groups */}
          {activeTab === "groups" && (
            <div>
              {result.processGroups.map(group => (
                <ProcessGroupCard
                  key={group.id}
                  group={group}
                  isOpen={!!openGroups[group.id]}
                  onToggle={() => toggleGroup(group.id)}
                />
              ))}
            </div>
          )}

          {/* Non-SAP requirements */}
          {activeTab === "nonsap" && (
            <div>
              {!result.nonSapRequirements?.length ? (
                <div style={{ padding: "24px", textAlign: "center", color: "var(--color-text-tertiary)", fontSize: 13 }}>
                  No non-SAP requirements identified.
                </div>
              ) : (
                <div style={{ border: "0.5px solid var(--color-border-tertiary)", borderRadius: "var(--border-radius-lg)", overflow: "hidden" }}>
                  {result.nonSapRequirements.map((req, i) => (
                    <div key={req.id} style={{
                      padding: "12px 16px",
                      borderTop: i > 0 ? "0.5px solid var(--color-border-tertiary)" : "none",
                      display: "grid", gridTemplateColumns: "64px 1fr auto", gap: 10, alignItems: "start",
                    }}>
                      <span style={{ fontFamily: "var(--font-mono)", fontSize: 11, color: "var(--color-text-tertiary)", paddingTop: 2 }}>{req.id}</span>
                      <div>
                        <p style={{ margin: 0, fontSize: 13, color: "var(--color-text-primary)", lineHeight: 1.5 }}>{req.text}</p>
                        {req.recommendation && (
                          <p style={{ margin: "4px 0 0", fontSize: 12, color: "var(--color-text-secondary)" }}>
                            <i className="ti ti-arrow-right" style={{ fontSize: 11, marginRight: 4, verticalAlign: "middle" }} aria-hidden="true" />
                            {req.recommendation}
                          </p>
                        )}
                      </div>
                      <CatBadge cat={req.category} />
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Legend */}
          <div style={{
            marginTop: 16, padding: "10px 14px",
            border: "0.5px solid var(--color-border-tertiary)",
            borderRadius: "var(--border-radius-md)",
            background: "var(--color-background-secondary)",
          }}>
            <p style={{ margin: "0 0 6px", fontSize: 11, fontWeight: 500, color: "var(--color-text-secondary)", textTransform: "uppercase", letterSpacing: "0.04em" }}>Fit type legend</p>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
              {[
                ["Standard", "Available out-of-box, minimal config"],
                ["Configuration", "IMG / Customising configuration needed"],
                ["Enhancement", "User-exit, BADI, or enhancement spot"],
                ["Custom", "Z-development / custom ABAP required"],
              ].map(([fit, desc]) => (
                <div key={fit} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11 }}>
                  <FitBadge fit={fit} />
                  <span style={{ color: "var(--color-text-tertiary)" }}>{desc}</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {/* Empty state */}
      {!loading && !result && !error && (
        <div style={{
          padding: "32px 16px", textAlign: "center",
          border: "0.5px dashed var(--color-border-secondary)",
          borderRadius: "var(--border-radius-lg)",
          color: "var(--color-text-secondary)",
        }}>
          <i className="ti ti-map-2" style={{ fontSize: 32, display: "block", marginBottom: 10, color: "var(--color-text-tertiary)" }} aria-hidden="true" />
          <p style={{ margin: "0 0 6px", fontSize: 14, fontWeight: 500, color: "var(--color-text-primary)" }}>Paste your RFP requirements above</p>
          <p style={{ margin: "0 0 14px", fontSize: 13 }}>Supports free-form Markdown or structured JSON. Works best with requirement IDs (FR-001, NFR-002, etc.).</p>
          <button onClick={loadSample} style={{
            display: "inline-flex", alignItems: "center", gap: 6,
            padding: "8px 16px", borderRadius: 8, cursor: "pointer",
            border: "0.5px solid var(--color-border-secondary)",
            background: "var(--color-background-secondary)",
            fontSize: 13, color: "var(--color-text-primary)",
          }}>
            <i className="ti ti-file-text" style={{ fontSize: 14 }} aria-hidden="true" />
            Try the sample ERP RFP ↗
          </button>
        </div>
      )}
    </div>
  );
}
