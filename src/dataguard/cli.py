from __future__ import annotations

import json
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from .config import load_config
from .demo import generate_retail_demo
from .drift import compare
from .drift import snapshot as make_snapshot
from .explain import local_explanation, openai_explanation
from .exporters import build_contract, build_dbt_schema, dump_yaml
from .gx_exporter import build_gx_expectations
from .html_report import write_html
from .models import ScanReport
from .scanner import scan_dataframe, scan_path
from .sources import load_duckdb, load_postgres

app = typer.Typer(help="DataGuard AI — data quality & governance copilot.", no_args_is_help=True)
console = Console()

def render(report: ScanReport) -> None:
    console.rule(f"[bold]DataGuard AI — {Path(report.source).name}")
    console.print(f"Rows: [bold]{report.row_count:,}[/]  Columns: [bold]{report.column_count}[/]")
    console.print(f"Quality score: [bold]{report.quality_score}/100[/]  Governance score: [bold]{report.governance_score}/100[/]")
    table = Table("Severity", "Column", "Finding", "Suggested action")
    for f in report.findings:
        table.add_row(f.severity, f.column or "—", f.message, f.remediation)
    if report.findings:
        console.print(table)
    else:
        console.print("[green]No material findings under configured rules.[/]")

@app.command()
def scan(
    path: str,
    config: str | None = typer.Option(None, "--config", "-c"),
    json_out: str | None = typer.Option(None, "--json-out"),
    html_out: str | None = typer.Option(None, "--html-out"),
):
    """Scan a CSV/JSON/Parquet dataset."""
    report = scan_path(path, config)
    render(report)
    if json_out:
        Path(json_out).write_text(report.model_dump_json(indent=2))
        console.print(f"JSON report written to {json_out}")
    if html_out:
        write_html(report, html_out)
        console.print(f"HTML report written to {html_out}")

@app.command("contract")
def contract_cmd(path: str, out: str = typer.Option("contract.yml", "--out"), config: str | None = None):
    """Generate a starter YAML data contract."""
    report = scan_path(path, config)
    Path(out).write_text(dump_yaml(build_contract(report)))
    console.print(f"Contract written to {out}")

@app.command("generate-dbt")
def generate_dbt(path: str, out: str = typer.Option("schema.yml", "--out"), config: str | None = None):
    """Generate starter dbt data tests."""
    report = scan_path(path, config)
    Path(out).write_text(dump_yaml(build_dbt_schema(report)))
    console.print(f"dbt schema written to {out}")

@app.command()
def snapshot(path: str, out: str = typer.Option("dataguard-baseline.json", "--out"), config: str | None = None):
    """Save a schema/classification baseline."""
    report = scan_path(path, config)
    Path(out).write_text(json.dumps(make_snapshot(report), indent=2))
    console.print(f"Baseline written to {out}")

@app.command()
def drift(path: str, baseline: str = typer.Option(..., "--baseline"), config: str | None = None):
    """Compare a dataset against a saved baseline."""
    report = scan_path(path, config)
    old = json.loads(Path(baseline).read_text())
    changes = compare(report, old)
    if not changes:
        console.print("[green]No schema/classification drift detected.[/]")
        raise typer.Exit()
    table = Table("Severity", "Change", "Column", "Before", "After")
    for c in changes:
        table.add_row(c["severity"], c["type"], c["column"], str(c.get("before", "—")), str(c.get("after", "—")))
    console.print(table)

@app.command()
def explain(report_file: str, provider: str = typer.Option("local", "--provider")):
    """Explain an existing JSON scan report."""
    report = ScanReport.model_validate_json(Path(report_file).read_text())
    if provider == "local":
        console.print(local_explanation(report))
    elif provider == "openai":
        console.print(openai_explanation(report))
    else:
        raise typer.BadParameter("provider must be 'local' or 'openai'")

@app.command()
def demo(rows: int = 1000, out_dir: str = ".dataguard-demo"):
    """Generate and scan synthetic retail data."""
    paths = generate_retail_demo(out_dir, rows=rows)
    console.print(f"[bold]Generated synthetic retail demo in {out_dir}[/]")
    for path in paths:
        render(scan_path(str(path)))


@app.command("generate-gx")
def generate_gx(path: str, out: str = typer.Option("gx-expectations.json", "--out"), config: str | None = None):
    """Generate portable Great Expectations expectation configuration."""
    report = scan_path(path, config)
    Path(out).write_text(json.dumps(build_gx_expectations(report), indent=2))
    console.print(f"GX expectation configuration written to {out}")

@app.command("scan-duckdb")
def scan_duckdb(database: str, table: str = typer.Option(..., "--table"), limit: int | None = None,
                config: str | None = None, json_out: str | None = None, html_out: str | None = None):
    """Scan a DuckDB table (read-only connection)."""
    df = load_duckdb(database, table, limit)
    report = scan_dataframe(df, source=f"duckdb://{database}/{table}", config=load_config(config))
    render(report)
    if json_out: Path(json_out).write_text(report.model_dump_json(indent=2))
    if html_out: write_html(report, html_out)

@app.command("scan-postgres")
def scan_postgres(url: str = typer.Option(..., "--url", envvar="DATAGUARD_POSTGRES_URL"),
                  table: str = typer.Option(..., "--table"), limit: int | None = None,
                  config: str | None = None, json_out: str | None = None, html_out: str | None = None):
    """Scan a PostgreSQL table. Prefer DATAGUARD_POSTGRES_URL to avoid credentials in shell history."""
    df = load_postgres(url, table, limit)
    report = scan_dataframe(df, source=f"postgres://{table}", config=load_config(config))
    render(report)
    if json_out: Path(json_out).write_text(report.model_dump_json(indent=2))
    if html_out: write_html(report, html_out)
