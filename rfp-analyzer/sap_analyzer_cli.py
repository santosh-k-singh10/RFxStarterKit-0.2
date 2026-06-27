"""
SAP Mapping Analyzer - Standalone CLI Tool

Command-line interface for analyzing RFP requirements and mapping to SAP modules.
This runs independently from the main RFP analyzer.

Usage:
    # Analyze from text file
    python sap_analyzer_cli.py analyze requirements.txt
    
    # Analyze from RFP Analyzer JSON output
    python sap_analyzer_cli.py analyze-json output/rfp_analysis.json
    
    # Interactive mode
    python sap_analyzer_cli.py interactive
"""

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.markdown import Markdown

from agents.sap_mapping_agent import create_sap_mapping_agent

app = typer.Typer(
    name="sap-analyzer",
    help="SAP Requirements Mapping Analyzer - Standalone CLI tool",
    add_completion=False,
)

console = Console()


@app.command()
def analyze(
    input_file: str = typer.Argument(..., help="Path to requirements text file (one per line)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path (JSON)"),
    format: str = typer.Option("summary", "--format", "-f", help="Output format: summary, json, markdown"),
):
    """Analyze requirements from a text file."""
    
    input_path = Path(input_file)
    if not input_path.exists():
        console.print(f"[red]Error:[/red] File not found: {input_file}")
        raise typer.Exit(code=1)
    
    # Read requirements
    requirements = []
    with open(input_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
    
    if not requirements:
        console.print("[red]Error:[/red] No requirements found in file")
        raise typer.Exit(code=1)
    
    console.print(f"[cyan]Analyzing {len(requirements)} requirements...[/cyan]")
    
    # Analyze
    agent = create_sap_mapping_agent()
    result = agent.analyze_requirements(requirements)
    
    # Output
    if format == "summary":
        display_summary(result)
    elif format == "json":
        output_json = json.dumps(result, indent=2)
        console.print(output_json)
    elif format == "markdown":
        md = agent.generate_module_summary(result)
        console.print(Markdown(md))
    
    # Save to file if requested
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        console.print(f"\n[green]Results saved to:[/green] {output_path}")


@app.command()
def analyze_json(
    json_file: str = typer.Argument(..., help="Path to RFP Analyzer JSON output"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path (JSON)"),
):
    """Analyze requirements from RFP Analyzer JSON output."""
    
    json_path = Path(json_file)
    if not json_path.exists():
        console.print(f"[red]Error:[/red] File not found: {json_file}")
        raise typer.Exit(code=1)
    
    # Load JSON
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract requirements
    requirements = []
    if 'requirements' in data:
        for req in data['requirements']:
            desc = req.get('description') or req.get('text') or req.get('title', '')
            if desc:
                requirements.append(desc)
    else:
        console.print("[red]Error:[/red] Invalid JSON format. Expected 'requirements' field.")
        raise typer.Exit(code=1)
    
    console.print(f"[cyan]Analyzing {len(requirements)} requirements from RFP Analyzer output...[/cyan]")
    
    # Analyze
    agent = create_sap_mapping_agent()
    result = agent.analyze_requirements(requirements)
    
    # Display
    display_summary(result)
    
    # Save to file if requested
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        console.print(f"\n[green]Results saved to:[/green] {output_path}")


@app.command()
def interactive():
    """Interactive mode for analyzing requirements."""
    
    console.print(Panel.fit(
        "[bold]SAP Requirements Mapping Analyzer[/bold]\n"
        "Interactive Mode",
        border_style="blue"
    ))
    
    console.print("\n[cyan]Enter requirements (one per line). Press Ctrl+D (Unix) or Ctrl+Z (Windows) when done:[/cyan]\n")
    
    requirements = []
    try:
        while True:
            line = input()
            line = line.strip()
            if line and not line.startswith('#'):
                requirements.append(line)
    except EOFError:
        pass
    
    if not requirements:
        console.print("\n[yellow]No requirements entered.[/yellow]")
        return
    
    console.print(f"\n[cyan]Analyzing {len(requirements)} requirements...[/cyan]\n")
    
    # Analyze
    agent = create_sap_mapping_agent()
    result = agent.analyze_requirements(requirements)
    
    # Display
    display_summary(result)
    
    # Ask if user wants to save
    save = typer.confirm("\nSave results to file?")
    if save:
        output_path = typer.prompt("Output file path", default="sap_analysis.json")
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        console.print(f"[green]Results saved to:[/green] {output_path}")


def display_summary(result: dict):
    """Display analysis summary in a nice format."""
    
    coverage = result['coverage_analysis']
    modules = result['mapped_modules']
    recommendations = result['recommendations']
    gaps = result['gaps']
    
    # Coverage stats
    console.print("\n[bold]Coverage Analysis[/bold]")
    stats_table = Table(show_header=False, box=None)
    stats_table.add_row("Total Requirements:", f"[cyan]{coverage['total_requirements']}[/cyan]")
    stats_table.add_row("Mapped to SAP:", f"[green]{coverage['mapped_requirements']}[/green]")
    stats_table.add_row("Coverage:", f"[bold green]{coverage['coverage_percentage']}%[/bold green]")
    console.print(stats_table)
    
    # SAP Modules
    console.print("\n[bold]Identified SAP Modules[/bold]")
    modules_table = Table(show_header=True, header_style="bold cyan")
    modules_table.add_column("Module", style="cyan", width=12)
    modules_table.add_column("Requirements", justify="right", width=15)
    
    for module, reqs in sorted(modules.items(), key=lambda x: len(x[1]), reverse=True):
        modules_table.add_row(module, str(len(reqs)))
    
    console.print(modules_table)
    
    # Recommendations
    if recommendations:
        console.print("\n[bold]Recommendations[/bold]")
        for i, rec in enumerate(recommendations, 1):
            console.print(f"  {i}. {rec}")
    
    # Gap Analysis
    if gaps['unmapped_requirements']:
        console.print("\n[bold yellow]Gap Analysis[/bold yellow]")
        console.print(f"[yellow]{len(gaps['unmapped_requirements'])} requirement(s) may need custom development:[/yellow]")
        for req in gaps['unmapped_requirements'][:5]:  # Show first 5
            console.print(f"  • {req}")
        if len(gaps['unmapped_requirements']) > 5:
            console.print(f"  ... and {len(gaps['unmapped_requirements']) - 5} more")


@app.command()
def version():
    """Show version information."""
    console.print("[bold]SAP Requirements Mapping Analyzer[/bold]")
    console.print("Version: 1.0.0")
    console.print("Standalone tool for SAP-specific RFP analysis")


if __name__ == "__main__":
    app()