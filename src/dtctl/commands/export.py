"""Export commands for dtctl resources."""

from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import typer
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from dtctl.client import create_client_from_config
from dtctl.config import load_config

app = typer.Typer(no_args_is_help=True)
console = Console()


def get_context() -> str | None:
    """Get context override from CLI state."""
    from dtctl.cli import state

    return state.context


def is_verbose() -> bool:
    """Check if verbose mode is enabled."""
    from dtctl.cli import state

    return state.verbose


def write_data(data: list[dict[str, Any]], path: Path, format: str) -> None:
    """Write data to file in specified format.

    Args:
        data: List of dictionaries to write
        path: Output file path
        format: Output format (csv, json, yaml)
    """
    if format == "json":
        path.write_text(json.dumps(data, indent=2, default=str))
    elif format == "yaml":
        path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True))
    elif format == "csv":
        if data:
            with open(path, "w", newline="", encoding="utf-8") as f:
                # Flatten nested dicts for CSV
                flat_data = []
                for item in data:
                    flat_item = {}
                    for k, v in item.items():
                        if isinstance(v, (list, dict)):
                            flat_item[k] = json.dumps(v)
                        else:
                            flat_item[k] = v
                    flat_data.append(flat_item)

                writer = csv.DictWriter(f, fieldnames=flat_data[0].keys())
                writer.writeheader()
                writer.writerows(flat_data)
        else:
            path.write_text("")


@app.command("all")
def export_all(
    output_dir: Path = typer.Option(".", "--output", "-o", help="Output directory"),
    format: str = typer.Option("yaml", "--format", "-f", help="Output format (csv, json, yaml)"),
    prefix: str = typer.Option("dtctl", "--prefix", "-p", help="File name prefix"),
    include: Optional[str] = typer.Option(
        None,
        "--include",
        "-i",
        help="Comma-separated list of exports (workflows,dashboards,notebooks,slos,buckets)",
    ),
    timestamp_dir: bool = typer.Option(
        True, "--timestamp-dir/--no-timestamp-dir", help="Create timestamped subdirectory"
    ),
) -> None:
    """Export all resources to files.

    Exports workflows, dashboards, notebooks, SLOs, and buckets.

    Examples:
        dtctl export all                          # Export all to YAML in current dir
        dtctl export all -o ./backup -f json      # Export as JSON to backup dir
        dtctl export all -i workflows,slos        # Only export workflows and SLOs
    """
    from dtctl.resources.workflow import WorkflowHandler
    from dtctl.resources.document import DashboardHandler, NotebookHandler
    from dtctl.resources.slo import SLOHandler
    from dtctl.resources.bucket import BucketHandler

    # Determine which exports to run
    all_exports = ["workflows", "dashboards", "notebooks", "slos", "buckets"]
    if include:
        exports_to_run = [e.strip() for e in include.split(",") if e.strip() in all_exports]
    else:
        exports_to_run = all_exports

    if not exports_to_run:
        console.print("[red]Error:[/red] No valid exports specified.")
        raise typer.Exit(1)

    # Create output directory
    if timestamp_dir:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_dir = output_dir / f"{prefix}_export_{timestamp}"
    else:
        export_dir = output_dir

    export_dir.mkdir(parents=True, exist_ok=True)

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())

    # File extension
    ext = format if format in ["json", "yaml"] else "csv"

    exported_files: list[tuple[str, int, Path]] = []

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:

            # Workflows
            if "workflows" in exports_to_run:
                task = progress.add_task("Exporting workflows...", total=1)
                handler = WorkflowHandler(client)
                data = handler.list()
                file_path = export_dir / f"{prefix}_workflows.{ext}"
                write_data(data, file_path, format)
                exported_files.append(("workflows", len(data), file_path))
                progress.advance(task)

            # Dashboards
            if "dashboards" in exports_to_run:
                task = progress.add_task("Exporting dashboards...", total=1)
                handler = DashboardHandler(client)
                data = handler.list()
                file_path = export_dir / f"{prefix}_dashboards.{ext}"
                write_data(data, file_path, format)
                exported_files.append(("dashboards", len(data), file_path))
                progress.advance(task)

            # Notebooks
            if "notebooks" in exports_to_run:
                task = progress.add_task("Exporting notebooks...", total=1)
                handler = NotebookHandler(client)
                data = handler.list()
                file_path = export_dir / f"{prefix}_notebooks.{ext}"
                write_data(data, file_path, format)
                exported_files.append(("notebooks", len(data), file_path))
                progress.advance(task)

            # SLOs
            if "slos" in exports_to_run:
                task = progress.add_task("Exporting SLOs...", total=1)
                handler = SLOHandler(client)
                data = handler.list()
                file_path = export_dir / f"{prefix}_slos.{ext}"
                write_data(data, file_path, format)
                exported_files.append(("slos", len(data), file_path))
                progress.advance(task)

            # Buckets
            if "buckets" in exports_to_run:
                task = progress.add_task("Exporting buckets...", total=1)
                handler = BucketHandler(client)
                data = handler.list()
                file_path = export_dir / f"{prefix}_buckets.{ext}"
                write_data(data, file_path, format)
                exported_files.append(("buckets", len(data), file_path))
                progress.advance(task)

        # Summary
        console.print()
        console.print("[green]Export complete![/green]")
        console.print(f"Output directory: {export_dir}")
        console.print()

        for resource, count, path in exported_files:
            console.print(f"  {resource}: {count} records -> {path.name}")

    finally:
        client.close()


@app.command("workflow")
def export_workflow(
    identifier: str = typer.Argument(..., help="Workflow ID or title"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    format: str = typer.Option("yaml", "--format", "-f", help="Output format (yaml, json)"),
    as_template: bool = typer.Option(False, "--as-template", "-t", help="Export as reusable template"),
) -> None:
    """Export a single workflow with its details.

    With --as-template, exports in template format with variable placeholders.
    """
    from dtctl.resources.workflow import WorkflowHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = WorkflowHandler(client)

    try:
        # Get workflow
        workflow = handler.get(identifier)

        if not workflow:
            console.print(f"[red]Error:[/red] Workflow '{identifier}' not found.")
            raise typer.Exit(1)

        workflow_title = workflow.get("title", "")

        if as_template:
            # Export as template
            export_data = {
                "description": f"Template from workflow: {workflow_title}",
                "kind": "workflow",
                "template": {
                    "title": "{{ workflow_title }}",
                    "description": workflow.get("description", "{{ description | default('') }}"),
                    "trigger": workflow.get("trigger", {}),
                    "tasks": workflow.get("tasks", {}),
                },
            }
        else:
            export_data = {
                "apiVersion": "v1",
                "kind": "Workflow",
                "metadata": {
                    "id": workflow.get("id", ""),
                    "exportedAt": datetime.now().isoformat(),
                },
                "spec": workflow,
            }

        # Output
        if format == "json":
            output = json.dumps(export_data, indent=2)
        else:
            output = yaml.dump(export_data, default_flow_style=False, allow_unicode=True)

        if output_file:
            output_file.write_text(output)
            console.print(f"[green]Exported[/green] workflow '{workflow_title}' to {output_file}")
        else:
            console.print(output)

    finally:
        client.close()


@app.command("dashboard")
def export_dashboard(
    identifier: str = typer.Argument(..., help="Dashboard ID or name"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    format: str = typer.Option("yaml", "--format", "-f", help="Output format (yaml, json)"),
) -> None:
    """Export a single dashboard with its details."""
    from dtctl.resources.document import DashboardHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = DashboardHandler(client)

    try:
        # Get dashboard
        dashboard = handler.get(identifier)

        if not dashboard:
            console.print(f"[red]Error:[/red] Dashboard '{identifier}' not found.")
            raise typer.Exit(1)

        dashboard_name = dashboard.get("name", dashboard.get("title", ""))

        export_data = {
            "apiVersion": "v1",
            "kind": "Dashboard",
            "metadata": {
                "id": dashboard.get("id", ""),
                "exportedAt": datetime.now().isoformat(),
            },
            "spec": dashboard,
        }

        # Output
        if format == "json":
            output = json.dumps(export_data, indent=2)
        else:
            output = yaml.dump(export_data, default_flow_style=False, allow_unicode=True)

        if output_file:
            output_file.write_text(output)
            console.print(f"[green]Exported[/green] dashboard '{dashboard_name}' to {output_file}")
        else:
            console.print(output)

    finally:
        client.close()


@app.command("slo")
def export_slo(
    identifier: str = typer.Argument(..., help="SLO ID or name"),
    output_file: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file"),
    format: str = typer.Option("yaml", "--format", "-f", help="Output format (yaml, json)"),
) -> None:
    """Export a single SLO with its details."""
    from dtctl.resources.slo import SLOHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = SLOHandler(client)

    try:
        # Get SLO
        slo = handler.get(identifier)

        if not slo:
            console.print(f"[red]Error:[/red] SLO '{identifier}' not found.")
            raise typer.Exit(1)

        slo_name = slo.get("name", "")

        export_data = {
            "apiVersion": "v1",
            "kind": "SLO",
            "metadata": {
                "id": slo.get("id", ""),
                "exportedAt": datetime.now().isoformat(),
            },
            "spec": slo,
        }

        # Output
        if format == "json":
            output = json.dumps(export_data, indent=2)
        else:
            output = yaml.dump(export_data, default_flow_style=False, allow_unicode=True)

        if output_file:
            output_file.write_text(output)
            console.print(f"[green]Exported[/green] SLO '{slo_name}' to {output_file}")
        else:
            console.print(output)

    finally:
        client.close()


@app.command("query-results")
def export_query_results(
    query: str = typer.Argument(..., help="DQL query to execute"),
    output_file: Path = typer.Option(..., "--output", "-o", help="Output file"),
    format: str = typer.Option("csv", "--format", "-f", help="Output format (csv, json, yaml)"),
) -> None:
    """Export DQL query results to a file.

    Executes a DQL query and saves the results.

    Example:
        dtctl export query-results "fetch logs | limit 100" -o results.csv
    """
    from dtctl.resources.query import QueryHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = QueryHandler(client)

    try:
        console.print(f"Executing query...")
        result = handler.execute(query)

        records = result.get("records", [])

        if not records:
            console.print("[yellow]Warning:[/yellow] Query returned no results.")
            output_file.write_text("[]" if format == "json" else "")
            return

        write_data(records, output_file, format)
        console.print(f"[green]Exported[/green] {len(records)} records to {output_file}")

    finally:
        client.close()
