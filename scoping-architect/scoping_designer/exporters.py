"""
Exporters — v1.2

MarkdownExporter: full document with story points, traceability, and module grouping.
JsonExporter:     plain JSON pass-through.
"""

from __future__ import annotations

import html

from .models import ArchitectureOutput, RiskLevel


class MarkdownExporter:

    def export(self, output: ArchitectureOutput) -> str:
        sections = [
            self._header(output),
            self._summary(output),
            self._domains(output),
            self._system_context(output),
            self._architecture(output),
            self._components(output),
            self._risks(output),
            self._estimation(output),
        ]
        return "\n\n".join(s for s in sections if s)

    # ── Sections ──────────────────────────────────────────────────────────────

    def _header(self, o: ArchitectureOutput) -> str:
        from datetime import datetime
        enriched_flag = " · Enriched (Phase 1.5)" if o.input.is_enriched else ""
        return (
            f"# Architecture Design — {o.input.project_name}\n\n"
            f"_Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} · "
            f"Deployment: {o.input.deployment_target.label()}{enriched_flag}_"
        )

    def _summary(self, o: ArchitectureOutput) -> str:
        sp = o.total_story_points
        rows = [
            ("Architecture pattern",        o.architecture.recommended),
            ("Requirement domains",          o.summary.domain_count),
            ("Actors & systems",             o.summary.actor_count),
            ("Components to estimate",       o.summary.component_count),
            ("Open ambiguities",             o.summary.open_ambiguities),
            ("Average component complexity", o.summary.avg_complexity),
            ("Compliance-scoped components", o.summary.compliance_components),
            ("Story points — low / mid / high", f"{sp['low']} / {sp['mid']} / {sp['high']}"),
        ]
        table = "| Metric | Value |\n|---|---|\n"
        table += "\n".join(f"| {r} | {v} |" for r, v in rows)
        return f"## Summary\n\n{table}"

    def _domains(self, o: ArchitectureOutput) -> str:
        if not o.domains:
            return ""
        lines = ["## Requirement Domains\n"]
        for d in o.domains:
            lines.append(f"### {d.name} ({d.count} requirements)\n")
            for r in d.requirements:
                lines.append(f"- {r}")
            lines.append("")
        return "\n".join(lines)

    def _system_context(self, o: ArchitectureOutput) -> str:
        ctx = o.system_context
        type_labels = {
            "human": "👤 Human",
            "internal_system": "🖥 Internal system",
            "external_system": "🔌 External system",
        }
        lines = [
            "## System Context\n",
            ctx.description, "",
            "### Actors & Systems\n",
        ]
        for a in ctx.actors:
            label = type_labels.get(a.type.value, a.type.value)
            lines.append(f"**{a.name}** ({label})")
            lines.append(f"  {a.description}\n")
        if ctx.integrations:
            lines.append("### External Integrations\n")
            for i in ctx.integrations:
                lines.append(f"- {i}")
        return "\n".join(lines)

    def _architecture(self, o: ArchitectureOutput) -> str:
        arch = o.architecture
        lines = ["## Proposed Architecture\n",
                 f"**Pattern:** {arch.recommended}\n", arch.rationale]
        if arch.domain_note:
            lines += ["", f"> ⚠️ **Domain note:** {arch.domain_note}"]
        if arch.key_principles:
            lines += ["", "### Key Principles\n"]
            lines += [f"- {p}" for p in arch.key_principles]
        if arch.layers:
            lines += ["", "### Architecture Layers\n"]
            for layer in arch.layers:
                lines.append(f"**{layer.layer}:** {', '.join(layer.components)}")
        if arch.alternatives:
            lines += ["", "### Alternatives Considered\n"]
            for alt in arch.alternatives:
                lines.append(f"- **{alt.name}** — {alt.tradeoff}")
        return "\n".join(lines)

    def _components(self, o: ArchitectureOutput) -> str:
        if not o.components:
            return ""
        cx_emoji = {"Low": "🟢", "Medium": "🟡", "High": "🔴"}
        lines = ["## Component Breakdown\n"]
        lines.append("| # | Component | Type | Complexity | SP (L–M–H) | Compliance | Traces from |")
        lines.append("|---|---|---|---|---|---|---|")
        for i, c in enumerate(o.components, 1):
            sp = f"{c.story_point_range.low}–{c.story_point_range.mid}–{c.story_point_range.high}" if c.story_point_range else "—"
            comp_flag = "✅" if c.compliance_impacted else ""
            traces = ", ".join(c.source_requirements) if c.source_requirements else "—"
            lines.append(
                f"| {i} | **{c.name}** | {c.type.value} | "
                f"{cx_emoji.get(c.complexity.value,'')} {c.complexity.value} | "
                f"{sp} | {comp_flag} | {traces} |"
            )
        lines += ["", "### Component Details\n"]
        for c in o.components:
            sp = f"{c.story_point_range.low} / {c.story_point_range.mid} / {c.story_point_range.high}" if c.story_point_range else "—"
            lines += [f"#### {c.name}\n",
                      f"- **Type:** {c.type.value}",
                      f"- **Module:** {c.module or '—'}",
                      f"- **Impl type:** {c.impl_type or '—'}",
                      f"- **Complexity:** {c.complexity.value} — {c.complexity_reason}",
                      f"- **Story points (low / mid / high):** {sp}",
                      f"- **Description:** {c.description}"]
            if c.compliance_impacted:
                lines.append("- **Compliance scope:** Yes — requires compliance review, audit logging, security testing")
            if c.actors:
                lines.append(f"- **Actors:** {', '.join(c.actors)}")
            if c.source_requirements:
                lines.append(f"- **Traces from:** {', '.join(c.source_requirements)}")
            if c.dependencies:
                lines.append(f"- **Dependencies:** {', '.join(c.dependencies)}")
            if c.estimation_signals:
                lines.append("- **Estimation signals:**")
                for s in c.estimation_signals:
                    lines.append(f"  - {s}")
            lines.append("")
        return "\n".join(lines)

    def _risks(self, o: ArchitectureOutput) -> str:
        if not o.risks:
            return ""
        level_emoji = {RiskLevel.HIGH: "🔴", RiskLevel.MEDIUM: "🟡", RiskLevel.LOW: "🟢"}
        lines = ["## Architecture Risks\n"]
        for r in sorted(o.risks, key=lambda x: ["High", "Medium", "Low"].index(x.level.value)):
            emoji = level_emoji.get(r.level, "")
            ref = f" `{r.ref_id}`" if r.ref_id else ""
            mod = f" _(module: {r.module})_" if r.module else ""
            lines += [f"### {emoji} {r.risk}{ref}{mod}\n",
                      f"**Mitigation:** {r.mitigation}\n"]
        return "\n".join(lines)

    def _estimation(self, o: ArchitectureOutput) -> str:
        sp = o.total_story_points
        lines = ["## Estimation Notes\n",
                 f"**Total story points (low / mid / high): {sp['low']} / {sp['mid']} / {sp['high']}**\n",
                 "_Mid is the recommended planning figure. Use high for fixed-price contracts._\n"]
        high = o.high_complexity_components
        if high:
            lines.append(f"**High-complexity components ({len(high)}):** "
                         + ", ".join(c.name for c in high)
                         + " — estimate with extra buffer.\n")
        compliance = o.compliance_components
        if compliance:
            lines.append(f"**Compliance-scoped components ({len(compliance)}):** "
                         + ", ".join(c.name for c in compliance)
                         + " — add 20–30% overhead for audit, security testing, documentation.\n")
        if o.summary.open_ambiguities:
            lines.append(f"**Open ambiguities: {o.summary.open_ambiguities}** — "
                         "architecture assumes best-case. Resolve before finalising estimates.\n")
        return "\n".join(lines)


class JsonExporter:
    def export(self, output: ArchitectureOutput, indent: int = 2) -> str:
        return output.to_json(indent=indent)


class HtmlExporter:
    def export(self, output: ArchitectureOutput) -> str:
        title = f"Architecture Export - {output.input.project_name}"
        sections = [
            self._html_header(title),
            self._summary(output),
            self._comprehensive_architecture_diagram(output),
            self._recommended_architecture(output),
            self._components(output),
            self._risks(output),
            self._estimation(output),
            self._html_footer(),
        ]
        return "\n".join(section for section in sections if section)
    
    def _comprehensive_architecture_diagram(self, o: ArchitectureOutput) -> str:
        """Main comprehensive architecture diagram section"""
        diagram_svg = self._generate_comprehensive_architecture_diagram(o)
        
        return (
            '<section class="card">'
            "<h2>Architecture Diagram</h2>"
            '<div class="diagram-box">'
            "<p class=\"muted\">Comprehensive architecture view showing modules, components, actors, and requirements.</p>"
            f"{diagram_svg}"
            "</div>"
            "</section>"
        )

    def _html_header(self, title: str) -> str:
        safe_title = html.escape(title)
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{safe_title}</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 24px;
      color: #1f2937;
      background: #f9fafb;
      line-height: 1.5;
    }}
    h1, h2, h3, h4 {{
      color: #111827;
    }}
    .card {{
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.04);
    }}
    .muted {{
      color: #6b7280;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 12px;
    }}
    th, td {{
      border: 1px solid #d1d5db;
      padding: 8px;
      text-align: left;
      vertical-align: top;
    }}
    th {{
      background: #f3f4f6;
    }}
    ul {{
      margin-top: 8px;
    }}
    .diagram-box {{
      border: 1px dashed #9ca3af;
      border-radius: 8px;
      padding: 12px;
      background: #fcfcfd;
      margin-top: 12px;
    }}
    .pill {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 999px;
      background: #e5e7eb;
      margin-right: 6px;
      margin-bottom: 6px;
      font-size: 12px;
    }}
    .risk-high {{ color: #b91c1c; font-weight: bold; }}
    .risk-medium {{ color: #b45309; font-weight: bold; }}
    .risk-low {{ color: #15803d; font-weight: bold; }}
    code {{
      background: #f3f4f6;
      padding: 2px 4px;
      border-radius: 4px;
    }}
    svg {{
      max-width: 100%;
      height: auto;
    }}
    .svg-node {{
      cursor: pointer;
      transition: all 0.2s;
    }}
    .svg-node:hover rect {{
      fill: #dbeafe;
      stroke: #3b82f6;
      stroke-width: 2;
    }}
    .svg-node text {{
      pointer-events: none;
    }}
  </style>
</head>
<body>
  <h1>{safe_title}</h1>
"""

    def _html_footer(self) -> str:
        return "</body>\n</html>"

    def _summary(self, o: ArchitectureOutput) -> str:
        sp = o.total_story_points
        rows = [
            ("Architecture pattern", o.architecture.recommended),
            ("Requirement domains", o.summary.domain_count),
            ("Actors & systems", o.summary.actor_count),
            ("Components to estimate", o.summary.component_count),
            ("Open ambiguities", o.summary.open_ambiguities),
            ("Average component complexity", o.summary.avg_complexity),
            ("Compliance-scoped components", o.summary.compliance_components),
            ("Story points - low / mid / high", f"{sp['low']} / {sp['mid']} / {sp['high']}"),
        ]
        body = "".join(
            f"<tr><th>{html.escape(str(label))}</th><td>{html.escape(str(value))}</td></tr>"
            for label, value in rows
        )
        return (
            '<section class="card">'
            "<h2>Summary</h2>"
            f"<table>{body}</table>"
            "</section>"
        )

    def _recommended_architecture(self, o: ArchitectureOutput) -> str:
        arch = o.architecture
        principles = "".join(
            f"<li>{html.escape(p)}</li>" for p in arch.key_principles
        ) or "<li>No key principles captured.</li>"
        alternatives = "".join(
            f"<li><strong>{html.escape(a.name)}</strong> - {html.escape(a.tradeoff)}</li>"
            for a in arch.alternatives
        ) or "<li>No alternatives recorded.</li>"
        domain_note = (
            f'<p><strong>Domain note:</strong> {html.escape(arch.domain_note)}</p>'
            if arch.domain_note else ""
        )
        return (
            '<section class="card">'
            "<h2>Recommended Architecture</h2>"
            f"<p><strong>Pattern:</strong> {html.escape(arch.recommended)}</p>"
            f"<p>{html.escape(arch.rationale)}</p>"
            f"{domain_note}"
            "<h3>Key Principles</h3>"
            f"<ul>{principles}</ul>"
            "<h3>Alternatives Considered</h3>"
            f"<ul>{alternatives}</ul>"
            "</section>"
        )


    def _components(self, o: ArchitectureOutput) -> str:
        if not o.components:
            return ""
        rows = []
        for component in o.components:
            sp = (
                f"{component.story_point_range.low} / "
                f"{component.story_point_range.mid} / "
                f"{component.story_point_range.high}"
                if component.story_point_range else "-"
            )
            rows.append(
                "<tr>"
                f"<td>{html.escape(component.name)}</td>"
                f"<td>{html.escape(component.type.value)}</td>"
                f"<td>{html.escape(component.complexity.value)}</td>"
                f"<td>{html.escape(component.module or '-')}</td>"
                f"<td>{html.escape(sp)}</td>"
                f"<td>{'Yes' if component.compliance_impacted else 'No'}</td>"
                "</tr>"
            )
        return (
            '<section class="card">'
            "<h2>Components</h2>"
            "<table>"
            "<tr><th>Name</th><th>Type</th><th>Complexity</th><th>Module</th><th>Story Points</th><th>Compliance</th></tr>"
            f"{''.join(rows)}"
            "</table>"
            "</section>"
        )

    def _risks(self, o: ArchitectureOutput) -> str:
        if not o.risks:
            return ""
        items = []
        for risk in sorted(o.risks, key=lambda x: ["High", "Medium", "Low"].index(x.level.value)):
            css = f"risk-{risk.level.value.lower()}"
            ref = f" ({risk.ref_id})" if risk.ref_id else ""
            module = f" [module: {risk.module}]" if risk.module else ""
            items.append(
                "<li>"
                f"<span class=\"{css}\">{html.escape(risk.level.value)}</span> "
                f"<strong>{html.escape(risk.risk)}</strong>{html.escape(ref)}{html.escape(module)}"
                f"<br><span class=\"muted\">Mitigation: {html.escape(risk.mitigation)}</span>"
                "</li>"
            )
        return (
            '<section class="card">'
            "<h2>Risks</h2>"
            f"<ul>{''.join(items)}</ul>"
            "</section>"
        )

    def _estimation(self, o: ArchitectureOutput) -> str:
        sp = o.total_story_points
        high = ", ".join(c.name for c in o.high_complexity_components) or "None"
        compliance = ", ".join(c.name for c in o.compliance_components) or "None"
        return (
            '<section class="card">'
            "<h2>Estimation Notes</h2>"
            f"<p><strong>Total story points:</strong> {sp['low']} / {sp['mid']} / {sp['high']}</p>"
            "<p class=\"muted\">Mid is the recommended planning figure. Use high for fixed-price contracts.</p>"
            f"<p><strong>High-complexity components:</strong> {html.escape(high)}</p>"
            f"<p><strong>Compliance-scoped components:</strong> {html.escape(compliance)}</p>"
            f"<p><strong>Open ambiguities:</strong> {o.summary.open_ambiguities}</p>"
            "</section>"
        )


    def _generate_comprehensive_architecture_diagram(self, o: ArchitectureOutput) -> str:
        """
        Enhanced architecture diagram with:
        - Fixed 900px viewBox width
        - 2-column module grid with color-coded boxes
        - Title bars for modules
        - Third-party integration badges
        - Risk strip
        - Platform boundary
        - Better typography and spacing
        """
        W = 900
        MARGIN = 32
        INNER = W - 2 * MARGIN
        
        els = []
        y = MARGIN
        
        # Module color palette
        MODULE_COLORS = {
            "identity_access": {"fill": "#dbeafe", "stroke": "#3b82f6", "text": "#1e3a5f"},
            "product_catalog": {"fill": "#ccfbf1", "stroke": "#14b8a6", "text": "#0f3a32"},
            "cart_checkout": {"fill": "#fef3c7", "stroke": "#f59e0b", "text": "#451a03"},
            "content_management": {"fill": "#ede9fe", "stroke": "#8b5cf6", "text": "#2e1065"},
            "integrations": {"fill": "#fee2e2", "stroke": "#f87171", "text": "#450a0a"},
            "compliance_privacy": {"fill": "#fce7f3", "stroke": "#ec4899", "text": "#500724"},
            "platform_nfr": {"fill": "#f1f5f9", "stroke": "#94a3b8", "text": "#1e293b"},
            "default": {"fill": "#f0fdf4", "stroke": "#4ade80", "text": "#14532d"},
        }
        
        ACTOR_COLOR = {"fill": "#e0e7ff", "stroke": "#6366f1", "text": "#312e81"}
        RISK_COLOR = {"fill": "#fff1f2", "stroke": "#f43f5e", "text": "#881337"}
        
        def _slug(name: str) -> str:
            return name.lower().replace(" ", "_").replace("&", "").replace("__", "_")
        
        def _colors(slug: str):
            return MODULE_COLORS.get(slug, MODULE_COLORS["default"])
        
        # Group components by module
        raw_modules = {}
        for comp in o.components:
            key = comp.module or "Core"
            raw_modules.setdefault(key, []).append(comp)
        
        # Separate platform NFRs
        platform_nfrs = raw_modules.pop("Platform NFRs", [])
        grid_modules = {k: v for k, v in raw_modules.items() if _slug(k) != "platform_nfr"}
        
        actors = o.system_context.actors if o.system_context else []
        
        # 1. Actors row
        if actors:
            AW, AH, AGAP = 140, 52, 14
            total_aw = len(actors) * AW + (len(actors) - 1) * AGAP
            ax_start = MARGIN + (INNER - total_aw) / 2
            
            for i, actor in enumerate(actors):
                ax = ax_start + i * (AW + AGAP)
                els.append(
                    f'<rect x="{ax}" y="{y}" width="{AW}" height="{AH}" rx="8" '
                    f'fill="{ACTOR_COLOR["fill"]}" stroke="{ACTOR_COLOR["stroke"]}" stroke-width="1.5"/>'
                )
                els.append(
                    f'<text x="{ax + AW/2}" y="{y + 18}" text-anchor="middle" '
                    f'font-size="13" font-weight="600" fill="{ACTOR_COLOR["text"]}">'
                    f'{html.escape(actor.name[:20])}</text>'
                )
                actor_type = actor.type.value if hasattr(actor.type, 'value') else str(actor.type)
                els.append(
                    f'<text x="{ax + AW/2}" y="{y + 36}" text-anchor="middle" '
                    f'font-size="11" fill="#6366f1">{html.escape(actor_type[:22])}</text>'
                )
            y += AH + 28
        
        # 2. Platform boundary (will be inserted later)
        boundary_y = y - 10
        boundary_placeholder = len(els)
        
        # 3. Module grid (2 per row)
        MOD_PER_ROW = 2
        GAP = 16
        MOD_W = (INNER - GAP) // MOD_PER_ROW
        
        TITLE_H = 38
        SUBTITLE_H = 20
        BULLET_H = 18
        PAD = 12
        
        module_list = list(grid_modules.items())
        
        for row_idx in range(0, len(module_list), MOD_PER_ROW):
            row = module_list[row_idx:row_idx + MOD_PER_ROW]
            
            # Calculate row height
            row_heights = []
            for mod_name, comps in row:
                h = TITLE_H + SUBTITLE_H + PAD
                h += min(len(comps), 5) * BULLET_H
                h += PAD
                row_heights.append(max(h, 120))
            
            MOD_H = max(row_heights) if row_heights else 120
            
            for col_idx, (mod_name, comps) in enumerate(row):
                slug = _slug(mod_name)
                c = _colors(slug)
                mx = MARGIN + col_idx * (MOD_W + GAP)
                my = y
                
                # Module box
                els.append(
                    f'<rect x="{mx}" y="{my}" width="{MOD_W}" height="{MOD_H}" rx="10" '
                    f'fill="{c["fill"]}" stroke="{c["stroke"]}" stroke-width="1.5"/>'
                )
                
                # Title bar
                els.append(
                    f'<rect x="{mx}" y="{my}" width="{MOD_W}" height="{TITLE_H}" rx="10" '
                    f'fill="{c["stroke"]}22" stroke="none"/>'
                )
                els.append(
                    f'<rect x="{mx}" y="{my + TITLE_H - 6}" width="{MOD_W}" height="6" '
                    f'fill="{c["stroke"]}22" stroke="none"/>'
                )
                
                # Module title
                els.append(
                    f'<text x="{mx + MOD_W/2}" y="{my + TITLE_H/2}" text-anchor="middle" '
                    f'dominant-baseline="central" font-size="14" font-weight="700" fill="{c["text"]}">'
                    f'{html.escape(mod_name)}</text>'
                )
                
                # Requirement IDs subtitle
                req_ids = sorted({c2.source_requirements[0] for c2 in comps
                                if c2.source_requirements})[:8]
                id_str = " · ".join(req_ids) if req_ids else ""
                els.append(
                    f'<text x="{mx + MOD_W/2}" y="{my + TITLE_H + SUBTITLE_H/2 + 2}" '
                    f'text-anchor="middle" font-size="10" fill="{c["stroke"]}">'
                    f'{html.escape(id_str)}</text>'
                )
                
                # Component bullets
                by = my + TITLE_H + SUBTITLE_H + PAD
                for comp in comps[:5]:
                    els.append(
                        f'<text x="{mx + PAD + 4}" y="{by + BULLET_H/2}" text-anchor="start" '
                        f'dominant-baseline="central" font-size="12" fill="{c["text"]}">'
                        f'· {html.escape(comp.name[:50])}</text>'
                    )
                    by += BULLET_H
                
                if len(comps) > 5:
                    els.append(
                        f'<text x="{mx + PAD + 4}" y="{by + BULLET_H/2}" text-anchor="start" '
                        f'font-size="11" fill="{c["stroke"]}" font-style="italic">'
                        f'+{len(comps)-5} more</text>'
                    )
            
            y += MOD_H + GAP
        
        # 4. Platform NFR strip
        if platform_nfrs:
            y += 8
            NFR_H = 72
            c = _colors("platform_nfr")
            els.append(
                f'<rect x="{MARGIN}" y="{y}" width="{INNER}" height="{NFR_H}" rx="10" '
                f'fill="{c["fill"]}" stroke="{c["stroke"]}" stroke-width="1.5"/>'
            )
            els.append(
                f'<text x="{MARGIN + INNER/2}" y="{y + 18}" text-anchor="middle" '
                f'font-size="13" font-weight="700" fill="{c["text"]}">Platform NFR</text>'
            )
            
            nfr_names = [comp.name for comp in platform_nfrs[:6]]
            summary = "  ·  ".join(nfr_names)
            els.append(
                f'<text x="{MARGIN + INNER/2}" y="{y + 50}" text-anchor="middle" '
                f'font-size="11" fill="{c["text"]}">{html.escape(summary[:110])}</text>'
            )
            y += NFR_H + GAP
        
        # 5. Legend
        y += 8
        LBOX = 14
        LGAP = 110
        legend_items = [
            ("Custom build", "#dbeafe", "#3b82f6"),
            ("3rd party", "#fce7f3", "#ec4899"),
            ("NFR", "#f1f5f9", "#94a3b8"),
        ]
        lx = MARGIN
        for label, fill, stroke in legend_items:
            els.append(
                f'<rect x="{lx}" y="{y}" width="{LBOX}" height="{LBOX}" rx="3" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="1"/>'
            )
            els.append(
                f'<text x="{lx + LBOX + 5}" y="{y + LBOX/2}" text-anchor="start" '
                f'dominant-baseline="central" font-size="11" fill="#64748b">{label}</text>'
            )
            lx += LGAP
        
        y += LBOX + 16
        
        # 6. Architecture note
        arch_note = f"Architecture: {o.architecture.recommended}  ·  Project: {o.input.project_name}"
        els.append(
            f'<text x="{W/2}" y="{y}" text-anchor="middle" font-size="11" fill="#94a3b8">'
            f'{html.escape(arch_note)}</text>'
        )
        y += 24
        
        # 7. Insert platform boundary
        total_h = y + MARGIN
        boundary_h = total_h - boundary_y - MARGIN - 8
        boundary_rect = (
            f'<rect x="{MARGIN - 8}" y="{boundary_y}" width="{INNER + 16}" height="{boundary_h}" '
            f'rx="16" fill="none" stroke="#cbd5e1" stroke-width="1" stroke-dasharray="8 5"/>'
        )
        els.insert(boundary_placeholder, boundary_rect)
        
        # 8. Assemble SVG
        return (
            f'<svg viewBox="0 0 {W} {total_h}" width="100%" '
            f'xmlns="http://www.w3.org/2000/svg" '
            f'style="background:#ffffff;font-family:ui-sans-serif,system-ui,sans-serif;">'
            f'<defs>'
            f'<marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
            f'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
            f'<path d="M2 1L8 5L2 9" fill="none" stroke="#94a3b8" '
            f'stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>'
            f'</marker>'
            f'</defs>'
            f'{"".join(els)}'
            f'</svg>'
        )

    def _generate_context_diagram(self, project_name: str, actors) -> str:
        """Generate SVG context diagram showing system and actors"""
        # Calculate positions in a circle around the center
        center_x, center_y = 400, 250
        radius = 180
        
        svg_elements = []
        
        # Draw central system
        svg_elements.append(
            f'<rect x="330" y="200" width="140" height="100" '
            f'fill="#3b82f6" stroke="#1e40af" stroke-width="2" rx="8"/>'
        )
        svg_elements.append(
            f'<text x="400" y="245" text-anchor="middle" fill="white" '
            f'font-size="14" font-weight="bold">{html.escape(project_name)}</text>'
        )
        svg_elements.append(
            f'<text x="400" y="265" text-anchor="middle" fill="white" '
            f'font-size="12">(System)</text>'
        )
        
        # Draw actors around the system
        actor_count = len(actors)
        for i, actor in enumerate(actors):
            angle = (2 * 3.14159 * i / actor_count) - (3.14159 / 2)  # Start from top
            x = center_x + radius * (1 if i % 2 == 0 else 0.85) * (1 if angle > -1.57 and angle < 1.57 else -1) * abs(angle / 1.57)
            y = center_y + radius * (1 if i % 2 == 0 else 0.85) * (angle / 1.57)
            
            # Choose color based on actor type
            if actor.type.value == "human":
                color = "#10b981"
                icon = "👤"
            elif actor.type.value == "internal_system":
                color = "#8b5cf6"
                icon = "🖥"
            else:
                color = "#f59e0b"
                icon = "🔌"
            
            # Draw actor box
            svg_elements.append(
                f'<g class="svg-node">'
                f'<rect x="{x-60}" y="{y-30}" width="120" height="60" '
                f'fill="{color}" stroke="#374151" stroke-width="1.5" rx="6"/>'
                f'<text x="{x}" y="{y-5}" text-anchor="middle" fill="white" '
                f'font-size="20">{icon}</text>'
                f'<text x="{x}" y="{y+15}" text-anchor="middle" fill="white" '
                f'font-size="11" font-weight="bold">{html.escape(actor.name[:20])}</text>'
                f'</g>'
            )
            
            # Draw connection line
            svg_elements.append(
                f'<line x1="{x}" y1="{y}" x2="400" y2="250" '
                f'stroke="#9ca3af" stroke-width="1.5" stroke-dasharray="5,5"/>'
            )
        
        return (
            f'<svg viewBox="0 0 800 500" xmlns="http://www.w3.org/2000/svg">'
            f'{"".join(svg_elements)}'
            f'</svg>'
        )
    
    def _generate_layers_diagram(self, layers) -> str:
        """Generate SVG layered architecture diagram"""
        svg_elements = []
        layer_height = 80
        start_y = 50
        width = 700
        
        colors = ["#3b82f6", "#8b5cf6", "#10b981", "#f59e0b", "#ef4444"]
        
        for i, layer in enumerate(layers):
            y = start_y + (i * (layer_height + 20))
            color = colors[i % len(colors)]
            
            # Draw layer box
            svg_elements.append(
                f'<g class="svg-node">'
                f'<rect x="50" y="{y}" width="{width}" height="{layer_height}" '
                f'fill="{color}" stroke="#374151" stroke-width="2" rx="8"/>'
                f'<text x="70" y="{y+30}" fill="white" font-size="16" font-weight="bold">'
                f'{html.escape(layer.layer)}</text>'
            )
            
            # Add component pills inside layer
            components_text = ", ".join(layer.components[:3])
            if len(layer.components) > 3:
                components_text += f" (+{len(layer.components)-3} more)"
            
            svg_elements.append(
                f'<text x="70" y="{y+55}" fill="white" font-size="12">'
                f'{html.escape(components_text)}</text>'
                f'</g>'
            )
            
            # Draw arrow to next layer
            if i < len(layers) - 1:
                arrow_y = y + layer_height + 10
                svg_elements.append(
                    f'<line x1="400" y1="{arrow_y}" x2="400" y2="{arrow_y+10}" '
                    f'stroke="#6b7280" stroke-width="2"/>'
                    f'<polygon points="395,{arrow_y+10} 400,{arrow_y+15} 405,{arrow_y+10}" '
                    f'fill="#6b7280"/>'
                )
        
        total_height = start_y + (len(layers) * (layer_height + 20)) + 20
        
        return (
            f'<svg viewBox="0 0 800 {total_height}" xmlns="http://www.w3.org/2000/svg">'
            f'{"".join(svg_elements)}'
            f'</svg>'
        )
    
    def _generate_component_diagram(self, components) -> str:
        """Generate SVG component diagram with dependencies"""
        svg_elements = []
        
        # Group components by module
        modules = {}
        for comp in components:
            module = comp.module or "Core"
            if module not in modules:
                modules[module] = []
            modules[module].append(comp)
        
        # Layout components in a grid
        col_width = 180
        row_height = 100
        padding = 20
        x_start = 50
        y_start = 50
        
        component_positions = {}
        row = 0
        col = 0
        max_cols = 4
        
        # Complexity colors
        complexity_colors = {
            "Low": "#10b981",
            "Medium": "#f59e0b",
            "High": "#ef4444"
        }
        
        for module_name, module_comps in modules.items():
            for comp in module_comps:
                x = x_start + (col * (col_width + padding))
                y = y_start + (row * (row_height + padding))
                
                component_positions[comp.name] = (x + col_width/2, y + row_height/2)
                
                color = complexity_colors.get(comp.complexity.value, "#6b7280")
                
                # Draw component box
                svg_elements.append(
                    f'<g class="svg-node">'
                    f'<rect x="{x}" y="{y}" width="{col_width}" height="{row_height}" '
                    f'fill="{color}" stroke="#374151" stroke-width="2" rx="6"/>'
                    f'<text x="{x+col_width/2}" y="{y+35}" text-anchor="middle" fill="white" '
                    f'font-size="13" font-weight="bold">{html.escape(comp.name[:25])}</text>'
                    f'<text x="{x+col_width/2}" y="{y+55}" text-anchor="middle" fill="white" '
                    f'font-size="10">{html.escape(comp.type.value)}</text>'
                    f'<text x="{x+col_width/2}" y="{y+75}" text-anchor="middle" fill="white" '
                    f'font-size="10">{html.escape(module_name)}</text>'
                    f'</g>'
                )
                
                col += 1
                if col >= max_cols:
                    col = 0
                    row += 1
        
        # Draw dependency arrows
        for comp in components:
            if comp.dependencies:
                for dep in comp.dependencies:
                    if comp.name in component_positions and dep in component_positions:
                        x1, y1 = component_positions[comp.name]
                        x2, y2 = component_positions[dep]
                        
                        # Draw arrow
                        svg_elements.insert(0,
                            f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
                            f'stroke="#9ca3af" stroke-width="2" marker-end="url(#arrowhead)"/>'
                        )
        
        # Add arrow marker definition
        svg_elements.insert(0,
            '<defs>'
            '<marker id="arrowhead" markerWidth="10" markerHeight="10" '
            'refX="9" refY="3" orient="auto">'
            '<polygon points="0 0, 10 3, 0 6" fill="#9ca3af"/>'
            '</marker>'
            '</defs>'
        )
        
        total_height = y_start + ((row + 1) * (row_height + padding)) + 50
        total_width = 800
        
        return (
            f'<svg viewBox="0 0 {total_width} {total_height}" xmlns="http://www.w3.org/2000/svg">'
            f'{"".join(svg_elements)}'
            f'</svg>'
        )


# Made with Bob
