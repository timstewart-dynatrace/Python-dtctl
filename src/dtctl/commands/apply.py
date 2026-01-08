"""Apply command for declarative resource management (create or update)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

import typer
from rich.console import Console

from dtctl.client import create_client_from_config, Client
from dtctl.config import load_config
from dtctl.output import Printer, OutputFormat
from dtctl.utils.format import parse_content
from dtctl.utils.template import parse_set_values, render_dict

app = typer.Typer(invoke_without_command=True)
console = Console()


def get_output_format() -> OutputFormat:
    """Get output format from CLI state."""
    from dtctl.cli import state
    return state.output


def is_plain_mode() -> bool:
    """Check if plain mode is enabled."""
    from dtctl.cli import state
    return state.plain


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


def detect_resource_type(data: dict[str, Any]) -> str | None:
    """Detect resource type from manifest content."""
    # Check for explicit kind field
    kind = data.get("kind", "").lower()
    if kind:
        return kind

    # Heuristics based on fields
    if "tasks" in data and "trigger" in data:
        return "workflow"
    if "target" in data and "warning" in data:
        return "slo"
    if "schemaId" in data:
        return "settings"
    if "bucketName" in data:
        return "bucket"
    if "hostnamePatterns" in data:
        return "edgeconnect"

    return None


def apply_workflow(client: Client, data: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    """Apply a workflow (create or update)."""
    from dtctl.resources.workflow import WorkflowHandler

    handler = WorkflowHandler(client)
    workflow_id = data.get("id")

    if dry_run:
        console.print("[yellow]Dry run - would apply workflow[/yellow]")
        return data

    if workflow_id and handler.exists(workflow_id):
        console.print(f"Updating workflow: {workflow_id}")
        return handler.update(workflow_id, data)
    else:
        console.print("Creating new workflow")
        return handler.create(data)


def apply_slo(client: Client, data: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    """Apply an SLO (create or update)."""
    from dtctl.resources.slo import SLOHandler

    handler = SLOHandler(client)
    slo_id = data.get("id")

    if dry_run:
        console.print("[yellow]Dry run - would apply SLO[/yellow]")
        return data

    if slo_id and handler.exists(slo_id):
        console.print(f"Updating SLO: {slo_id}")
        return handler.update(slo_id, data)
    else:
        console.print("Creating new SLO")
        return handler.create(data)


def apply_settings(client: Client, data: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    """Apply settings (create or update)."""
    from dtctl.resources.settings import SettingsHandler

    handler = SettingsHandler(client)
    object_id = data.get("objectId")
    schema_id = data.get("schemaId")
    scope = data.get("scope", "environment")
    value = data.get("value", data)

    if dry_run:
        console.print("[yellow]Dry run - would apply settings[/yellow]")
        return data

    if object_id:
        console.print(f"Updating settings: {object_id}")
        return handler.update_object(object_id, value)
    else:
        console.print(f"Creating settings for schema: {schema_id}")
        return handler.create_object(schema_id, scope, value)


def apply_bucket(client: Client, data: dict[str, Any], dry_run: bool) -> dict[str, Any]:
    """Apply a bucket (create or update)."""
    from dtctl.resources.bucket import BucketHandler

    handler = BucketHandler(client)
    bucket_name = data.get("bucketName")

    if dry_run:
        console.print("[yellow]Dry run - would apply bucket[/yellow]")
        return data

    if bucket_name and handler.exists(bucket_name):
        console.print(f"Updating bucket: {bucket_name}")
        return handler.update(bucket_name, data)
    else:
        console.print("Creating new bucket")
        return handler.create(data)


def apply_document(
    client: Client,
    data: dict[str, Any],
    doc_type: str,
    dry_run: bool,
) -> dict[str, Any]:
    """Apply a document (create or update)."""
    from dtctl.resources.document import DocumentHandler

    handler = DocumentHandler(client, doc_type=doc_type)  # type: ignore
    doc_id = data.get("id")
    name = data.get("name", "Untitled")
    content = data.get("content", data)

    if dry_run:
        console.print(f"[yellow]Dry run - would apply {doc_type}[/yellow]")
        return data

    if doc_id:
        console.print(f"Updating {doc_type}: {doc_id}")
        return handler.update(doc_id, content, name=name)
    else:
        console.print(f"Creating new {doc_type}")
        return handler.create(
            name=name,
            doc_type=doc_type,  # type: ignore
            content=content,
            is_private=data.get("isPrivate", True),
        )


@app.callback(invoke_without_command=True)
def apply_resource(
    ctx: typer.Context,
    file: Path = typer.Option(..., "--file", "-f", help="Path to manifest file"),
    set_values: Optional[list[str]] = typer.Option(
        None, "--set", help="Set template variables (key=value)"
    ),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """Apply a resource configuration from file (create or update).

    The resource type is auto-detected from the manifest content.

    Examples:
        dtctl apply -f workflow.yaml
        dtctl apply -f slo.yaml --set target=99.9
        dtctl apply -f dashboard.json --dry-run
    """
    if ctx.invoked_subcommand is not None:
        return

    if not file.exists():
        console.print(f"[red]Error:[/red] File not found: {file}")
        raise typer.Exit(1)

    content = file.read_text()
    data = parse_content(content)

    if not isinstance(data, dict):
        console.print("[red]Error:[/red] Manifest must be a dictionary/object")
        raise typer.Exit(1)

    # Apply template variables
    if set_values:
        variables = parse_set_values(set_values)
        data = render_dict(data, variables)

    # Detect resource type
    resource_type = detect_resource_type(data)
    if not resource_type:
        console.print("[red]Error:[/red] Could not detect resource type from manifest")
        console.print("Add a 'kind' field or ensure the manifest has recognizable fields")
        raise typer.Exit(1)

    console.print(f"Detected resource type: {resource_type}")

    dry_run = is_dry_run()
    if dry_run:
        console.print("[yellow]Running in dry-run mode[/yellow]")
        printer = Printer(format=OutputFormat.YAML, plain=is_plain_mode())
        printer.print(data)
        return

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())

    # Apply based on type
    appliers = {
        "workflow": apply_workflow,
        "slo": apply_slo,
        "settings": apply_settings,
        "bucket": apply_bucket,
        "dashboard": lambda c, d, dr: apply_document(c, d, "dashboard", dr),
        "notebook": lambda c, d, dr: apply_document(c, d, "notebook", dr),
    }

    applier = appliers.get(resource_type)
    if not applier:
        console.print(f"[red]Error:[/red] Unsupported resource type: {resource_type}")
        raise typer.Exit(1)

    result = applier(client, data, dry_run)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    console.print(f"[green]Applied {resource_type}[/green]")
    printer.print(result)
