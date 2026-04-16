"""Share command for document sharing management."""

from __future__ import annotations

import typer
from rich.console import Console

from dtctl.client import create_client_from_config
from dtctl.config import load_config
from dtctl.output import OutputFormat, Printer

app = typer.Typer(no_args_is_help=True)
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


@app.command("dashboard")
@app.command("dash")
def share_dashboard(
    identifier: str = typer.Argument(..., help="Dashboard ID or name"),
    user: str | None = typer.Option(None, "--user", "-u", help="User SSO ID"),
    group: str | None = typer.Option(None, "--group", "-g", help="Group UUID"),
    access: str = typer.Option("read", "--access", "-a", help="Access level (read or read-write)"),
) -> None:
    """Share a dashboard with a user or group.

    Examples:
        dtctl share dashboard my-dashboard --user user@example.com
        dtctl share dashboard my-dashboard --group group-uuid --access read-write
    """
    from dtctl.resources.document import create_dashboard_handler
    from dtctl.utils.resolver import ResourceResolver

    if not user and not group:
        console.print("[red]Error:[/red] Either --user or --group is required")
        raise typer.Exit(1)

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_dashboard_handler(client)
    resolver = ResourceResolver(client)

    doc_id = resolver.resolve_document(identifier, "dashboard")

    if handler.share(doc_id, user_id=user, group_id=group, access=access):  # type: ignore
        console.print(
            f"[green]Shared dashboard with {'user ' + user if user else 'group ' + group}[/green]"
        )
    else:
        console.print("[red]Failed to share dashboard[/red]")
        raise typer.Exit(1)


@app.command("notebook")
@app.command("nb")
def share_notebook(
    identifier: str = typer.Argument(..., help="Notebook ID or name"),
    user: str | None = typer.Option(None, "--user", "-u", help="User SSO ID"),
    group: str | None = typer.Option(None, "--group", "-g", help="Group UUID"),
    access: str = typer.Option("read", "--access", "-a", help="Access level (read or read-write)"),
) -> None:
    """Share a notebook with a user or group.

    Examples:
        dtctl share notebook my-notebook --user user@example.com
        dtctl share notebook my-notebook --group group-uuid --access read-write
    """
    from dtctl.resources.document import create_notebook_handler
    from dtctl.utils.resolver import ResourceResolver

    if not user and not group:
        console.print("[red]Error:[/red] Either --user or --group is required")
        raise typer.Exit(1)

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_notebook_handler(client)
    resolver = ResourceResolver(client)

    doc_id = resolver.resolve_document(identifier, "notebook")

    if handler.share(doc_id, user_id=user, group_id=group, access=access):  # type: ignore
        console.print(
            f"[green]Shared notebook with {'user ' + user if user else 'group ' + group}[/green]"
        )
    else:
        console.print("[red]Failed to share notebook[/red]")
        raise typer.Exit(1)


def unshare_document(
    resource_type: str,
    identifier: str,
    user: str | None,
    group: str | None,
) -> None:
    """Remove sharing from a document."""
    from dtctl.resources.document import DocumentHandler
    from dtctl.utils.resolver import ResourceResolver

    if not user and not group:
        console.print("[red]Error:[/red] Either --user or --group is required")
        raise typer.Exit(1)

    doc_type = "dashboard" if resource_type in ("dashboard", "dash") else "notebook"

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = DocumentHandler(client, doc_type=doc_type)  # type: ignore
    resolver = ResourceResolver(client)

    doc_id = resolver.resolve_document(identifier, doc_type)

    if handler.unshare(doc_id, user_id=user, group_id=group):
        console.print(f"[green]Removed sharing from {doc_type}[/green]")
    else:
        console.print(f"[red]Failed to unshare {doc_type}[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_shares(
    resource_type: str = typer.Argument(..., help="Resource type (dashboard or notebook)"),
    identifier: str = typer.Argument(..., help="Resource ID or name"),
    output: OutputFormat | None = typer.Option(None, "-o", "--output"),
) -> None:
    """List shares for a document.

    Examples:
        dtctl share list dashboard my-dashboard
    """
    from dtctl.resources.document import DocumentHandler
    from dtctl.utils.resolver import ResourceResolver

    doc_type = "dashboard" if resource_type in ("dashboard", "dash") else "notebook"

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = DocumentHandler(client, doc_type=doc_type)  # type: ignore
    resolver = ResourceResolver(client)

    doc_id = resolver.resolve_document(identifier, doc_type)
    shares = handler.list_shares(doc_id)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())
    printer.print(shares)
