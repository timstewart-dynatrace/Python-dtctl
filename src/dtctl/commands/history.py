"""History command for viewing version history of resources."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from dtctl.client import create_client_from_config
from dtctl.config import load_config
from dtctl.output import OutputFormat, Printer
from dtctl.utils.resolver import ResourceResolver

app = typer.Typer()
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


@app.command("workflow")
@app.command("wf")
def workflow_history(
    identifier: str = typer.Argument(..., help="Workflow ID or name"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of versions to show"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """View version history for a workflow.

    Shows all available versions/revisions of a workflow that can be
    restored using the 'restore' command.

    Examples:
        dtctl history workflow my-workflow
        dtctl history wf my-workflow --limit 20
    """
    from dtctl.resources.workflow import WorkflowHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = WorkflowHandler(client)

    # Resolve name to ID if needed
    resolver = ResourceResolver(client)
    workflow_id = resolver.resolve_workflow(identifier)

    if is_verbose():
        console.print(f"[dim]Getting history for workflow: {workflow_id}[/dim]")

    try:
        # Get workflow versions from the versions endpoint
        response = client.get(
            f"/platform/automation/v1/workflows/{workflow_id}/versions",
            params={"limit": limit},
        )
        data = response.json()
        versions = data.get("results", [])
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to get workflow history: {e}")
        raise typer.Exit(1)

    if not versions:
        console.print(f"[yellow]No version history found for workflow {identifier}[/yellow]")
        return

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if fmt in (OutputFormat.JSON, OutputFormat.YAML):
        printer.print(versions)
    else:
        # Format as table
        console.print(f"\n[bold]Version History for Workflow: {identifier}[/bold]\n")
        for v in versions:
            version_id = v.get("id", v.get("version", "unknown"))
            modified = v.get("modifiedAt", v.get("modified", "unknown"))
            modified_by = v.get("modifiedBy", v.get("owner", "unknown"))
            console.print(f"  • Version: [cyan]{version_id}[/cyan]")
            console.print(f"    Modified: {modified}")
            console.print(f"    By: {modified_by}")
            console.print()


@app.command("dashboard")
@app.command("dash")
def dashboard_history(
    identifier: str = typer.Argument(..., help="Dashboard ID or name"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of snapshots to show"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """View snapshot history for a dashboard.

    Shows all available snapshots of a dashboard that can be restored.

    Examples:
        dtctl history dashboard my-dashboard
        dtctl history dash my-dashboard --limit 5
    """
    from dtctl.resources.document import DocumentHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = DocumentHandler(client, doc_type="dashboard")

    # Resolve name to ID if needed
    resolver = ResourceResolver(client)
    doc_id = resolver.resolve_document(identifier, "dashboard")

    if is_verbose():
        console.print(f"[dim]Getting history for dashboard: {doc_id}[/dim]")

    try:
        # Get document snapshots
        response = client.get(
            f"/platform/document/v1/documents/{doc_id}/snapshots",
            params={"page-size": limit},
        )
        data = response.json()
        snapshots = data.get("snapshots", [])
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to get dashboard history: {e}")
        raise typer.Exit(1)

    if not snapshots:
        console.print(f"[yellow]No snapshots found for dashboard {identifier}[/yellow]")
        return

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if fmt in (OutputFormat.JSON, OutputFormat.YAML):
        printer.print(snapshots)
    else:
        console.print(f"\n[bold]Snapshot History for Dashboard: {identifier}[/bold]\n")
        for s in snapshots:
            snapshot_id = s.get("id", "unknown")
            created = s.get("createdAt", s.get("created", "unknown"))
            description = s.get("description", "")
            console.print(f"  • Snapshot: [cyan]{snapshot_id}[/cyan]")
            console.print(f"    Created: {created}")
            if description:
                console.print(f"    Description: {description}")
            console.print()


@app.command("notebook")
@app.command("nb")
def notebook_history(
    identifier: str = typer.Argument(..., help="Notebook ID or name"),
    limit: int = typer.Option(10, "--limit", "-n", help="Number of snapshots to show"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """View snapshot history for a notebook.

    Shows all available snapshots of a notebook that can be restored.

    Examples:
        dtctl history notebook my-notebook
        dtctl history nb my-notebook --limit 5
    """
    from dtctl.resources.document import DocumentHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = DocumentHandler(client, doc_type="notebook")

    # Resolve name to ID if needed
    resolver = ResourceResolver(client)
    doc_id = resolver.resolve_document(identifier, "notebook")

    if is_verbose():
        console.print(f"[dim]Getting history for notebook: {doc_id}[/dim]")

    try:
        # Get document snapshots
        response = client.get(
            f"/platform/document/v1/documents/{doc_id}/snapshots",
            params={"page-size": limit},
        )
        data = response.json()
        snapshots = data.get("snapshots", [])
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to get notebook history: {e}")
        raise typer.Exit(1)

    if not snapshots:
        console.print(f"[yellow]No snapshots found for notebook {identifier}[/yellow]")
        return

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if fmt in (OutputFormat.JSON, OutputFormat.YAML):
        printer.print(snapshots)
    else:
        console.print(f"\n[bold]Snapshot History for Notebook: {identifier}[/bold]\n")
        for s in snapshots:
            snapshot_id = s.get("id", "unknown")
            created = s.get("createdAt", s.get("created", "unknown"))
            description = s.get("description", "")
            console.print(f"  • Snapshot: [cyan]{snapshot_id}[/cyan]")
            console.print(f"    Created: {created}")
            if description:
                console.print(f"    Description: {description}")
            console.print()
