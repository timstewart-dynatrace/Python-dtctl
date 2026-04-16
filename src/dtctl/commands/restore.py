"""Restore command for reverting resources to previous versions."""

from __future__ import annotations

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


def is_dry_run() -> bool:
    """Check if dry-run mode is enabled."""
    from dtctl.cli import state

    return state.dry_run


@app.command("workflow")
@app.command("wf")
def restore_workflow(
    identifier: str = typer.Argument(..., help="Workflow ID or name"),
    version: str = typer.Argument(..., help="Version ID to restore"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    output: OutputFormat | None = typer.Option(None, "-o", "--output"),
) -> None:
    """Restore a workflow to a previous version.

    This will revert the workflow to the specified version. The current
    version will be preserved in the version history.

    Examples:
        dtctl restore workflow my-workflow v1
        dtctl restore wf my-workflow abc123 --force
    """
    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())

    # Resolve name to ID if needed
    resolver = ResourceResolver(client)
    workflow_id = resolver.resolve_workflow(identifier)

    if is_verbose():
        console.print(f"[dim]Restoring workflow {workflow_id} to version {version}[/dim]")

    # Get the version to restore
    try:
        response = client.get(f"/platform/automation/v1/workflows/{workflow_id}/versions/{version}")
        version_data = response.json()
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to get version {version}: {e}")
        raise typer.Exit(1) from None

    if is_dry_run():
        console.print("[yellow]Dry run:[/yellow] Would restore workflow to version:")
        fmt = output or get_output_format()
        printer = Printer(format=fmt, plain=is_plain_mode())
        printer.print(version_data)
        return

    # Confirm unless forced
    if not force and not is_plain_mode():
        confirm = typer.confirm(f"Restore workflow '{identifier}' to version '{version}'?")
        if not confirm:
            console.print("Cancelled.")
            raise typer.Exit(0)

    try:
        # Restore by posting to the restore endpoint
        response = client.post(
            f"/platform/automation/v1/workflows/{workflow_id}/versions/{version}/restore"
        )
        result = response.json()
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to restore workflow: {e}")
        raise typer.Exit(1) from None

    if not is_plain_mode():
        console.print(
            f"[green]Success:[/green] Restored workflow '{identifier}' to version '{version}'"
        )

    fmt = output or get_output_format()
    if fmt in (OutputFormat.JSON, OutputFormat.YAML):
        printer = Printer(format=fmt, plain=is_plain_mode())
        printer.print(result)


@app.command("dashboard")
@app.command("dash")
def restore_dashboard(
    identifier: str = typer.Argument(..., help="Dashboard ID or name"),
    snapshot: str = typer.Argument(..., help="Snapshot ID to restore"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    create_snapshot: bool = typer.Option(
        True,
        "--create-snapshot/--no-create-snapshot",
        help="Create a snapshot before restoring (default: true)",
    ),
    output: OutputFormat | None = typer.Option(None, "-o", "--output"),
) -> None:
    """Restore a dashboard to a previous snapshot.

    By default, creates a snapshot of the current state before restoring
    to allow recovery if needed.

    Examples:
        dtctl restore dashboard my-dashboard snap123
        dtctl restore dash my-dashboard snap123 --no-create-snapshot
    """
    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())

    # Resolve name to ID if needed
    resolver = ResourceResolver(client)
    doc_id = resolver.resolve_document(identifier, "dashboard")

    if is_verbose():
        console.print(f"[dim]Restoring dashboard {doc_id} to snapshot {snapshot}[/dim]")

    if is_dry_run():
        console.print(
            f"[yellow]Dry run:[/yellow] Would restore dashboard '{identifier}' "
            f"to snapshot '{snapshot}'"
        )
        if create_snapshot:
            console.print("[dim]  (would create pre-restore snapshot)[/dim]")
        return

    # Confirm unless forced
    if not force and not is_plain_mode():
        confirm = typer.confirm(f"Restore dashboard '{identifier}' to snapshot '{snapshot}'?")
        if not confirm:
            console.print("Cancelled.")
            raise typer.Exit(0)

    # Optionally create a pre-restore snapshot
    if create_snapshot:
        try:
            if not is_plain_mode():
                console.print("[dim]Creating pre-restore snapshot...[/dim]")
            client.post(
                f"/platform/document/v1/documents/{doc_id}/snapshots",
                json={"description": "Pre-restore snapshot"},
            )
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Failed to create pre-restore snapshot: {e}")

    try:
        # Restore by posting to the restore endpoint
        response = client.post(
            f"/platform/document/v1/documents/{doc_id}/snapshots/{snapshot}/restore"
        )
        result = response.json() if response.text else {}
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to restore dashboard: {e}")
        raise typer.Exit(1) from None

    if not is_plain_mode():
        console.print(
            f"[green]Success:[/green] Restored dashboard '{identifier}' to snapshot '{snapshot}'"
        )

    fmt = output or get_output_format()
    if fmt in (OutputFormat.JSON, OutputFormat.YAML) and result:
        printer = Printer(format=fmt, plain=is_plain_mode())
        printer.print(result)


@app.command("notebook")
@app.command("nb")
def restore_notebook(
    identifier: str = typer.Argument(..., help="Notebook ID or name"),
    snapshot: str = typer.Argument(..., help="Snapshot ID to restore"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation prompt"),
    create_snapshot: bool = typer.Option(
        True,
        "--create-snapshot/--no-create-snapshot",
        help="Create a snapshot before restoring (default: true)",
    ),
    output: OutputFormat | None = typer.Option(None, "-o", "--output"),
) -> None:
    """Restore a notebook to a previous snapshot.

    By default, creates a snapshot of the current state before restoring
    to allow recovery if needed.

    Examples:
        dtctl restore notebook my-notebook snap123
        dtctl restore nb my-notebook snap123 --force
    """
    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())

    # Resolve name to ID if needed
    resolver = ResourceResolver(client)
    doc_id = resolver.resolve_document(identifier, "notebook")

    if is_verbose():
        console.print(f"[dim]Restoring notebook {doc_id} to snapshot {snapshot}[/dim]")

    if is_dry_run():
        console.print(
            f"[yellow]Dry run:[/yellow] Would restore notebook '{identifier}' "
            f"to snapshot '{snapshot}'"
        )
        if create_snapshot:
            console.print("[dim]  (would create pre-restore snapshot)[/dim]")
        return

    # Confirm unless forced
    if not force and not is_plain_mode():
        confirm = typer.confirm(f"Restore notebook '{identifier}' to snapshot '{snapshot}'?")
        if not confirm:
            console.print("Cancelled.")
            raise typer.Exit(0)

    # Optionally create a pre-restore snapshot
    if create_snapshot:
        try:
            if not is_plain_mode():
                console.print("[dim]Creating pre-restore snapshot...[/dim]")
            client.post(
                f"/platform/document/v1/documents/{doc_id}/snapshots",
                json={"description": "Pre-restore snapshot"},
            )
        except Exception as e:
            console.print(f"[yellow]Warning:[/yellow] Failed to create pre-restore snapshot: {e}")

    try:
        # Restore by posting to the restore endpoint
        response = client.post(
            f"/platform/document/v1/documents/{doc_id}/snapshots/{snapshot}/restore"
        )
        result = response.json() if response.text else {}
    except Exception as e:
        console.print(f"[red]Error:[/red] Failed to restore notebook: {e}")
        raise typer.Exit(1) from None

    if not is_plain_mode():
        console.print(
            f"[green]Success:[/green] Restored notebook '{identifier}' to snapshot '{snapshot}'"
        )

    fmt = output or get_output_format()
    if fmt in (OutputFormat.JSON, OutputFormat.YAML) and result:
        printer = Printer(format=fmt, plain=is_plain_mode())
        printer.print(result)
