"""Bulk operations for dtctl resources."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import typer
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from dtctl.client import create_client_from_config
from dtctl.config import load_config
from dtctl.output import OutputFormat, Printer
from dtctl.utils.template import render_template

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


def is_dry_run() -> bool:
    """Check if dry-run mode is enabled."""
    from dtctl.cli import state

    return state.dry_run


def get_output_format() -> OutputFormat:
    """Get output format from CLI state."""
    from dtctl.cli import state

    return state.output


def is_plain_mode() -> bool:
    """Check if plain mode is enabled."""
    from dtctl.cli import state

    return state.plain


def load_input_file(file_path: Path, variables: dict[str, str] | None = None) -> list[dict[str, Any]]:
    """Load data from a file (JSON, YAML, or CSV).

    Args:
        file_path: Path to the input file
        variables: Optional template variables for substitution

    Returns:
        List of dictionaries with the data
    """
    suffix = file_path.suffix.lower()
    content = file_path.read_text()

    # Apply template variables if provided
    if variables:
        content = render_template(content, variables)

    if suffix == ".json":
        data = json.loads(content)
        return data if isinstance(data, list) else [data]
    elif suffix in (".yaml", ".yml"):
        data = yaml.safe_load(content)
        if data is None:
            return []
        return data if isinstance(data, list) else [data]
    elif suffix == ".csv":
        reader = csv.DictReader(content.splitlines())
        return list(reader)
    else:
        raise ValueError(f"Unsupported file format: {suffix}. Use .json, .yaml, .yml, or .csv")


@app.command("apply")
def bulk_apply(
    file: Path = typer.Option(..., "--file", "-f", help="File with resource definitions (JSON or YAML)"),
    set_vars: list[str] = typer.Option(
        [], "--set", "-s", help="Set template variables (key=value)"
    ),
    continue_on_error: bool = typer.Option(False, "--continue-on-error", help="Continue processing on errors"),
) -> None:
    """Apply multiple resources from a file.

    Processes each resource definition in the file, creating or updating as needed.
    Supports workflow, dashboard, notebook, and SLO resources.

    JSON/YAML example (list of resources):
        - kind: workflow
          title: "My Workflow"
          description: "..."
        - kind: dashboard
          title: "My Dashboard"
    """
    from dtctl.resources.workflow import WorkflowHandler
    from dtctl.resources.document import DashboardHandler, NotebookHandler
    from dtctl.resources.slo import SLOHandler

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    # Parse template variables
    variables = {}
    for var in set_vars:
        if "=" in var:
            key, value = var.split("=", 1)
            variables[key.strip()] = value.strip()

    try:
        records = load_input_file(file, variables)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to read file: {e}")
        raise typer.Exit(1)

    if not records:
        console.print("[yellow]Warning:[/yellow] No records found in file.")
        return

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())

    # Map kinds to handlers
    handlers = {
        "workflow": WorkflowHandler(client),
        "dashboard": DashboardHandler(client),
        "notebook": NotebookHandler(client),
        "slo": SLOHandler(client),
    }

    try:
        console.print(f"Found {len(records)} resources to apply")

        if is_dry_run():
            console.print("[yellow]Dry-run mode:[/yellow] Would apply the following resources:")
            for record in records:
                kind = record.get("kind", "unknown")
                title = record.get("title", record.get("name", "unnamed"))
                console.print(f"  - {kind}: {title}")
            return

        # Process applications
        results: dict[str, list[Any]] = {"success": [], "failed": []}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Applying resources...", total=len(records))

            for record in records:
                kind = record.get("kind", "").lower()
                title = record.get("title", record.get("name", "unnamed"))

                if kind not in handlers:
                    results["failed"].append({
                        "resource": f"{kind}/{title}",
                        "error": f"Unknown resource kind: {kind}. Supported: {', '.join(handlers.keys())}",
                    })
                    if not continue_on_error:
                        console.print(f"[red]Error:[/red] Unknown kind: {kind}")
                        raise typer.Exit(1)
                    progress.advance(task)
                    continue

                try:
                    handler = handlers[kind]
                    # Remove kind field before sending to API
                    data = {k: v for k, v in record.items() if k != "kind"}

                    # Check if resource exists by ID
                    resource_id = data.get("id")
                    if resource_id:
                        existing = handler.get(resource_id)
                        if existing:
                            handler.update(resource_id, data)
                            results["success"].append(f"{kind}/{title} (updated)")
                        else:
                            result = handler.create(data)
                            results["success"].append(f"{kind}/{title} (created)")
                    else:
                        result = handler.create(data)
                        results["success"].append(f"{kind}/{title} (created)")

                except Exception as e:
                    results["failed"].append({"resource": f"{kind}/{title}", "error": str(e)})
                    if not continue_on_error:
                        console.print(f"[red]Error:[/red] Failed to apply '{title}': {e}")
                        raise typer.Exit(1)

                progress.advance(task)

        # Print summary
        console.print()
        console.print(f"[green]Successfully applied:[/green] {len(results['success'])} resources")
        if results["failed"]:
            console.print(f"[red]Failed:[/red] {len(results['failed'])} resources")
            for failure in results["failed"]:
                console.print(f"  - {failure['resource']}: {failure['error']}")

    finally:
        client.close()


@app.command("delete")
def bulk_delete(
    file: Path = typer.Option(..., "--file", "-f", help="File with resource identifiers (JSON, YAML, or CSV)"),
    resource_type: str = typer.Option(..., "--type", "-t", help="Resource type (workflow, dashboard, notebook, slo)"),
    id_field: str = typer.Option("id", "--id-field", "-i", help="Field name containing resource ID"),
    continue_on_error: bool = typer.Option(False, "--continue-on-error", help="Continue processing on errors"),
    force: bool = typer.Option(False, "--force", "-F", help="Skip confirmation"),
) -> None:
    """Delete multiple resources from a file.

    The file should contain resource identifiers (IDs or names).

    JSON/YAML example:
        - id: "workflow-123"
        - id: "workflow-456"

    CSV example:
        id
        workflow-123
        workflow-456
    """
    from dtctl.resources.workflow import WorkflowHandler
    from dtctl.resources.document import DashboardHandler, NotebookHandler
    from dtctl.resources.slo import SLOHandler

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    try:
        records = load_input_file(file)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to read file: {e}")
        raise typer.Exit(1)

    if not records:
        console.print("[yellow]Warning:[/yellow] No records found in file.")
        return

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())

    # Map types to handlers
    handlers = {
        "workflow": WorkflowHandler(client),
        "dashboard": DashboardHandler(client),
        "notebook": NotebookHandler(client),
        "slo": SLOHandler(client),
    }

    if resource_type.lower() not in handlers:
        console.print(f"[red]Error:[/red] Unknown resource type: {resource_type}")
        console.print(f"Supported types: {', '.join(handlers.keys())}")
        raise typer.Exit(1)

    handler = handlers[resource_type.lower()]

    try:
        # Extract IDs
        ids_to_delete = []
        for record in records:
            resource_id = record.get(id_field)
            if resource_id:
                ids_to_delete.append(resource_id.strip())
            else:
                console.print(f"[yellow]Warning:[/yellow] Record missing '{id_field}' field: {record}")

        if not ids_to_delete:
            console.print("[red]Error:[/red] No valid resource IDs found.")
            raise typer.Exit(1)

        console.print(f"Found {len(ids_to_delete)} {resource_type}s to delete")

        if is_dry_run():
            console.print("[yellow]Dry-run mode:[/yellow] Would delete the following resources:")
            for resource_id in ids_to_delete:
                console.print(f"  - {resource_id}")
            return

        if not force:
            confirm = typer.confirm(f"Delete {len(ids_to_delete)} {resource_type}s?")
            if not confirm:
                console.print("Aborted.")
                raise typer.Exit(0)

        # Process deletions
        results: dict[str, list[Any]] = {"success": [], "failed": []}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Deleting resources...", total=len(ids_to_delete))

            for resource_id in ids_to_delete:
                try:
                    handler.delete(resource_id)
                    results["success"].append(resource_id)
                except Exception as e:
                    results["failed"].append({"id": resource_id, "error": str(e)})
                    if not continue_on_error:
                        console.print(f"[red]Error:[/red] Failed to delete '{resource_id}': {e}")
                        raise typer.Exit(1)

                progress.advance(task)

        # Print summary
        console.print()
        console.print(f"[green]Successfully deleted:[/green] {len(results['success'])} {resource_type}s")
        if results["failed"]:
            console.print(f"[red]Failed:[/red] {len(results['failed'])} {resource_type}s")
            for failure in results["failed"]:
                console.print(f"  - {failure['id']}: {failure['error']}")

    finally:
        client.close()


@app.command("create-workflows")
def bulk_create_workflows(
    file: Path = typer.Option(..., "--file", "-f", help="File with workflow definitions (JSON or YAML)"),
    set_vars: list[str] = typer.Option(
        [], "--set", "-s", help="Set template variables (key=value)"
    ),
    continue_on_error: bool = typer.Option(False, "--continue-on-error", help="Continue processing on errors"),
) -> None:
    """Create multiple workflows from a file.

    JSON/YAML example:
        - title: "Workflow A"
          description: "Description for Workflow A"
          tasks: {...}
        - title: "Workflow B"
          description: "Description for Workflow B"
    """
    from dtctl.resources.workflow import WorkflowHandler

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    # Parse template variables
    variables = {}
    for var in set_vars:
        if "=" in var:
            key, value = var.split("=", 1)
            variables[key.strip()] = value.strip()

    try:
        records = load_input_file(file, variables)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to read file: {e}")
        raise typer.Exit(1)

    if not records:
        console.print("[yellow]Warning:[/yellow] No records found in file.")
        return

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = WorkflowHandler(client)

    try:
        # Validate records have title
        valid_workflows = []
        for record in records:
            if "title" not in record:
                console.print(f"[yellow]Warning:[/yellow] Record missing 'title' field: {record}")
                continue
            valid_workflows.append(record)

        if not valid_workflows:
            console.print("[red]Error:[/red] No valid workflow definitions found.")
            raise typer.Exit(1)

        console.print(f"Found {len(valid_workflows)} workflows to create")

        if is_dry_run():
            console.print("[yellow]Dry-run mode:[/yellow] Would create the following workflows:")
            for wf in valid_workflows:
                console.print(f"  - {wf['title']}")
            return

        # Process creations
        results: dict[str, list[Any]] = {"success": [], "failed": []}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Creating workflows...", total=len(valid_workflows))

            for wf_def in valid_workflows:
                try:
                    result = handler.create(wf_def)
                    results["success"].append(result.get("title", wf_def["title"]))
                except Exception as e:
                    results["failed"].append({"title": wf_def["title"], "error": str(e)})
                    if not continue_on_error:
                        console.print(f"[red]Error:[/red] Failed to create '{wf_def['title']}': {e}")
                        raise typer.Exit(1)

                progress.advance(task)

        # Print summary
        console.print()
        console.print(f"[green]Successfully created:[/green] {len(results['success'])} workflows")
        if results["failed"]:
            console.print(f"[red]Failed:[/red] {len(results['failed'])} workflows")
            for failure in results["failed"]:
                console.print(f"  - {failure['title']}: {failure['error']}")

    finally:
        client.close()


@app.command("exec-workflows")
def bulk_exec_workflows(
    file: Path = typer.Option(..., "--file", "-f", help="File with workflow identifiers (JSON, YAML, or CSV)"),
    id_field: str = typer.Option("id", "--id-field", "-i", help="Field name containing workflow ID"),
    wait: bool = typer.Option(False, "--wait", "-w", help="Wait for execution to complete"),
    continue_on_error: bool = typer.Option(False, "--continue-on-error", help="Continue processing on errors"),
) -> None:
    """Execute multiple workflows from a file.

    JSON/YAML example:
        - id: "workflow-123"
          params:
            key1: value1
        - id: "workflow-456"
    """
    from dtctl.resources.workflow import WorkflowHandler

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    try:
        records = load_input_file(file)
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to read file: {e}")
        raise typer.Exit(1)

    if not records:
        console.print("[yellow]Warning:[/yellow] No records found in file.")
        return

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = WorkflowHandler(client)

    try:
        # Extract workflow specs
        workflows_to_exec = []
        for record in records:
            wf_id = record.get(id_field)
            if wf_id:
                workflows_to_exec.append({
                    "id": wf_id.strip(),
                    "params": record.get("params", {}),
                })
            else:
                console.print(f"[yellow]Warning:[/yellow] Record missing '{id_field}' field: {record}")

        if not workflows_to_exec:
            console.print("[red]Error:[/red] No valid workflow IDs found.")
            raise typer.Exit(1)

        console.print(f"Found {len(workflows_to_exec)} workflows to execute")

        if is_dry_run():
            console.print("[yellow]Dry-run mode:[/yellow] Would execute the following workflows:")
            for wf in workflows_to_exec:
                console.print(f"  - {wf['id']}")
            return

        # Process executions
        results: dict[str, list[Any]] = {"success": [], "failed": []}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Executing workflows...", total=len(workflows_to_exec))

            for wf in workflows_to_exec:
                try:
                    execution = handler.execute(wf["id"], params=wf["params"], wait=wait)
                    exec_id = execution.get("id", "")
                    results["success"].append({"workflow": wf["id"], "execution": exec_id})
                except Exception as e:
                    results["failed"].append({"id": wf["id"], "error": str(e)})
                    if not continue_on_error:
                        console.print(f"[red]Error:[/red] Failed to execute '{wf['id']}': {e}")
                        raise typer.Exit(1)

                progress.advance(task)

        # Print summary
        console.print()
        console.print(f"[green]Successfully executed:[/green] {len(results['success'])} workflows")
        for success in results["success"]:
            console.print(f"  - {success['workflow']} -> execution: {success['execution']}")
        if results["failed"]:
            console.print(f"[red]Failed:[/red] {len(results['failed'])} workflows")
            for failure in results["failed"]:
                console.print(f"  - {failure['id']}: {failure['error']}")

    finally:
        client.close()
