"""
main.py
-------
CLI entry point for the RFP Analyzer (batch / scripted runs only).

This is the command-line companion to web_app.py — it is NOT the production
web server.  For the web UI, start web_app.py instead:
    uvicorn web_app:app --reload --port 8080

Usage
-----
    python main.py analyze path/to/rfp.pdf
    python main.py analyze path/to/rfp.pdf --output-dir ./results --title "Project Alpha"
    python main.py analyze path/to/rfp.pdf --no-excel --no-markdown
    python main.py analyze path/to/rfp.pdf --thread-id my-run-1   # resume interrupted run
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional, cast

import structlog
import typer
from dotenv import load_dotenv
from langchain_core.runnables import RunnableConfig
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

load_dotenv()

# Setup logging before anything else
from logging_config import setup_logging
setup_logging(
    log_file="./logs/rfp_analyzer.log",
    console_level="INFO",
    file_level="DEBUG"
)

log = structlog.get_logger(__name__)
console = Console()
app = typer.Typer(
    name="rfp-analyzer",
    help="AI-powered RFP analyzer — extracts functional, non-functional, compliance, ambiguity, and risk items.",
    add_completion=False,
)


# ─────────────────────────────────────────────────────────────────────────────
# CLI command
# ─────────────────────────────────────────────────────────────────────────────

@app.command()
def analyze(
    file_path: str = typer.Argument(..., help="Path to the RFP file (PDF, DOCX, or TXT)"),
    output_dir: str = typer.Option("./outputs", "--output-dir", "-o", help="Directory for output files"),
    title: str = typer.Option("RFP Analysis", "--title", "-t", help="Title for the report"),
    thread_id: str = typer.Option("rfp-run-1", "--thread-id", help="LangGraph thread ID (use same ID to resume)"),
    checkpoint_db: str = typer.Option("./logs/checkpoints.sqlite", "--checkpoint-db", help="Path to SQLite checkpoint file"),
    no_excel: bool = typer.Option(False, "--no-excel", help="Skip Excel export"),
    no_markdown: bool = typer.Option(False, "--no-markdown", help="Skip Markdown export"),
    no_json: bool = typer.Option(False, "--no-json", help="Skip JSON export"),
    min_confidence: float = typer.Option(0.0, "--min-confidence", help="Filter out requirements below this confidence (0.0–1.0)"),
    org_context: Optional[str] = typer.Option(None, "--org-context", help="Path to organizational context config file (YAML/JSON)"),
) -> None:
    """Analyze an RFP document and extract all requirements."""

    # ── Validate inputs ──────────────────────────────────────────────────────
    if not os.getenv("OPENAI_API_KEY"):
        console.print("[red]Error:[/red] OPENAI_API_KEY not set. Add it to your .env file.")
        raise typer.Exit(code=1)

    rfp_path = Path(file_path)
    if not rfp_path.exists():
        console.print(f"[red]Error:[/red] File not found: {file_path}")
        raise typer.Exit(code=1)

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    Path("./logs").mkdir(parents=True, exist_ok=True)

    stem = rfp_path.stem

    # ── Load organizational context ──────────────────────────────────────────
    from org_context import initialize_context_manager, get_context_manager
    
    if org_context:
        try:
            context_mgr = initialize_context_manager(org_context)
            org_name = context_mgr.get_context().name
            console.print(f"[green]OK[/green] Loaded organizational context: [cyan]{org_name}[/cyan]")
            log.info("org_context_loaded", path=org_context, org_name=org_name)
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Failed to load org context: {e}")
            console.print("[dim]Continuing with default context...[/dim]")
            log.warning("org_context_load_failed", error=str(e))
            context_mgr = initialize_context_manager()
    else:
        context_mgr = initialize_context_manager()
        console.print("[dim]Using default organizational context[/dim]")
    
    # ── Banner ───────────────────────────────────────────────────────────────
    org_info = f"Org: [cyan]{context_mgr.get_context().name}[/cyan]\n" if org_context else ""
    console.print(Panel.fit(
        f"[bold]RFP Analyzer[/bold]\n"
        f"{org_info}"
        f"File: [cyan]{rfp_path.name}[/cyan]\n"
        f"Thread: [dim]{thread_id}[/dim]",
        border_style="blue",
    ))

    # ── Import graph here (after validation) ────────────────────────────────
    from core.state import build_graph, cleanup_checkpoint_db
    from core.schemas import AnalysisState, AnalysisStateDict, Category
    from outputs.exporter import export_excel, export_markdown, export_json

    # Clean up old checkpoints to prevent data contamination
    console.print("[dim]Cleaning old checkpoints...[/dim]")
    cleanup_checkpoint_db(checkpoint_db)

    graph = build_graph(checkpoint_db=checkpoint_db)

    # Create initial state as AnalysisStateDict
    initial_state_model = AnalysisState(
        file_path=str(rfp_path.resolve()),
        metadata={"title": title, "file_name": rfp_path.name},
    )
    # Convert to dict and cast to AnalysisStateDict for type safety
    initial_state = cast(AnalysisStateDict, initial_state_model.model_dump())

    # Config for LangGraph with thread_id for checkpointing
    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}

    # ── Run graph ────────────────────────────────────────────────────────────
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Running analysis pipeline…", total=None)

        try:
            final_state = graph.invoke(initial_state, config)
        except Exception as exc:
            console.print(f"[red]Pipeline error:[/red] {exc}")
            log.error("pipeline_error", error=str(exc))
            raise typer.Exit(code=1)

        progress.update(task, description="Synthesis complete.")

    # ── Unwrap results ───────────────────────────────────────────────────────
    final = AnalysisState(**final_state)
    requirements = final.final_requirements

    if min_confidence > 0.0:
        requirements = [r for r in requirements if r.confidence >= min_confidence]

    if final.errors:
        for err in final.errors:
            console.print(f"[yellow]Warning:[/yellow] {err}")

    # ── Summary table ────────────────────────────────────────────────────────
    table = Table(title="Analysis Results", show_header=True, header_style="bold white on dark_blue")
    table.add_column("Category",  style="cyan",  min_width=18)
    table.add_column("Total",     justify="right", min_width=7)
    table.add_column("Must",      justify="right", min_width=7)
    table.add_column("Should",    justify="right", min_width=7)
    table.add_column("Ambiguous", justify="right", min_width=10)

    from core.schemas import Priority
    total_all = 0
    for cat in Category:
        cat_reqs  = [r for r in requirements if r.category == cat]
        musts     = sum(1 for r in cat_reqs if r.priority == Priority.MUST)
        shoulds   = sum(1 for r in cat_reqs if r.priority == Priority.SHOULD)
        ambig     = sum(1 for r in cat_reqs if r.ambiguity_flag)
        total_all += len(cat_reqs)
        style = "red" if cat.value in ("ambiguity", "risk") else ""
        table.add_row(
            cat.value.replace("_", " ").title(),
            str(len(cat_reqs)),
            str(musts),
            str(shoulds),
            str(ambig),
            style=style,
        )

    table.add_section()
    table.add_row("TOTAL", str(total_all), "", "", "", style="bold")

    console.print(table)

    # ── Export ───────────────────────────────────────────────────────────────
    outputs: list[str] = []

    if not no_excel:
        excel_path = str(out_dir / f"{stem}_analysis.xlsx")
        try:
            log.info("excel_export_starting", path=excel_path, requirements_count=len(requirements))
            path = export_excel(requirements, excel_path)
            outputs.append(f"Excel:    {path}")
            log.info("excel_export_success", path=path)
        except Exception as exc:
            error_msg = f"Excel export failed: {exc}"
            console.print(f"[yellow]Warning:[/yellow] {error_msg}")
            log.error("excel_export_failed", error=str(exc), path=excel_path, exc_info=True)
            # Continue with other exports

    if not no_markdown:
        md_path = str(out_dir / f"{stem}_analysis.md")
        try:
            log.info("markdown_export_starting", path=md_path)
            path = export_markdown(requirements, md_path, rfp_title=title)
            outputs.append(f"Markdown: {path}")
            log.info("markdown_export_success", path=path)
        except Exception as exc:
            error_msg = f"Markdown export failed: {exc}"
            console.print(f"[yellow]Warning:[/yellow] {error_msg}")
            log.error("markdown_export_failed", error=str(exc), path=md_path, exc_info=True)

    if not no_json:
        json_path = str(out_dir / f"{stem}_analysis.json")
        try:
            log.info("json_export_starting", path=json_path)
            path = export_json(requirements, json_path, rfp_title=title)
            outputs.append(f"JSON:     {path}")
            log.info("json_export_success", path=path)
        except Exception as exc:
            error_msg = f"JSON export failed: {exc}"
            console.print(f"[yellow]Warning:[/yellow] {error_msg}")
            log.error("json_export_failed", error=str(exc), path=json_path, exc_info=True)

    if outputs:
        console.print("\n[bold green]Outputs:[/bold green]")
        for o in outputs:
            console.print(f"  {o}")

    console.print(f"\n[bold]Done.[/bold] {total_all} requirements extracted.\n")


# ─────────────────────────────────────────────────────────────────────────────
# Programmatic API (import and call directly from other Python code)
# ─────────────────────────────────────────────────────────────────────────────

def run_analysis(
    file_path: str,
    output_dir: str = "./outputs",
    title: str = "RFP Analysis",
    thread_id: str = "rfp-run-1",
    checkpoint_db: str = "./logs/checkpoints.sqlite",
    min_confidence: float = 0.0,
    export_excel_flag: bool = True,
    export_markdown_flag: bool = True,
    export_json_flag: bool = True,
) -> dict:
    """
    Programmatic entry point — call this from notebooks or other scripts.

    Returns
    -------
    dict with keys:
        requirements  : list[Requirement]
        excel_path    : str | None
        markdown_path : str | None
        json_path     : str | None
        errors        : list[str]

    Example
    -------
        from main import run_analysis
        result = run_analysis("rfp.pdf", title="NHS Portal RFP")
        for req in result["requirements"]:
            print(req.id, req.title)
    """
    from core.state import build_graph, cleanup_checkpoint_db
    from core.schemas import AnalysisState, AnalysisStateDict
    from outputs.exporter import export_excel, export_markdown, export_json
    from pathlib import Path

    log.info("run_analysis_start", file_path=file_path)
    
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    Path("./logs").mkdir(parents=True, exist_ok=True)

    # Clean up old checkpoints to prevent data contamination
    log.info("cleaning_checkpoints")
    cleanup_checkpoint_db(checkpoint_db)

    log.info("building_graph")
    graph = build_graph(checkpoint_db=checkpoint_db)
    rfp_path = Path(file_path)

    # Create initial state and cast to AnalysisStateDict for type safety
    initial_state = cast(
        AnalysisStateDict,
        AnalysisState(
            file_path=str(rfp_path.resolve()),
            metadata={"title": title, "file_name": rfp_path.name},
        ).model_dump()
    )

    config: RunnableConfig = {"configurable": {"thread_id": thread_id}}
    
    log.info("invoking_graph", thread_id=thread_id)
    final_state = graph.invoke(initial_state, config)
    
    log.info("graph_invoke_complete", converting_state=True)
    final = AnalysisState(**final_state)
    
    log.info("state_converted", total_requirements=len(final.final_requirements))

    requirements = final.final_requirements
    if min_confidence > 0.0:
        requirements = [r for r in requirements if r.confidence >= min_confidence]
        log.info("filtered_by_confidence", remaining=len(requirements))

    stem = rfp_path.stem
    excel_path = md_path = json_path = None
    export_errors = list(final.errors) if final.errors else []

    if export_excel_flag:
        try:
            log.info("exporting_excel", requirements_count=len(requirements))
            excel_path = export_excel(requirements, str(Path(output_dir) / f"{stem}_analysis.xlsx"))
            log.info("excel_export_complete", path=excel_path)
        except Exception as e:
            log.error("excel_export_failed", error=str(e), exc_info=True)
            export_errors.append(f"Excel export failed: {str(e)}")
            excel_path = None

    if export_markdown_flag:
        try:
            log.info("exporting_markdown")
            md_path = export_markdown(requirements, str(Path(output_dir) / f"{stem}_analysis.md"), rfp_title=title)
            log.info("markdown_export_complete", path=md_path)
        except Exception as e:
            log.error("markdown_export_failed", error=str(e), exc_info=True)
            export_errors.append(f"Markdown export failed: {str(e)}")
            md_path = None

    if export_json_flag:
        try:
            log.info("exporting_json")
            json_path = export_json(requirements, str(Path(output_dir) / f"{stem}_analysis.json"), rfp_title=title)
            log.info("json_export_complete", path=json_path)
        except Exception as e:
            log.error("json_export_failed", error=str(e), exc_info=True)
            export_errors.append(f"JSON export failed: {str(e)}")
            json_path = None

    log.info("run_analysis_complete", requirements_count=len(requirements),
             excel_success=excel_path is not None, markdown_success=md_path is not None,
             json_success=json_path is not None)
    
    return {
        "requirements":   requirements,
        "excel_path":     excel_path,
        "markdown_path":  md_path,
        "json_path":      json_path,
        "errors":         export_errors,
    }


if __name__ == "__main__":
    app()
