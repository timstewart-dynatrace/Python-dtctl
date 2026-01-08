"""Delete command for removing resources."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

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


def is_plain_mode() -> bool:
    """Check if plain mode is enabled."""
    from dtctl.cli import state
    return state.plain


def confirm_delete(resource_type: str, identifier: str, force: bool) -> bool:
    """Confirm deletion with user."""
    if force or is_plain_mode():
        return True
    return typer.confirm(f"Delete {resource_type} '{identifier}'?")


@app.command("workflow")
@app.command("wf")
def delete_workflow(
    identifier: str = typer.Argument(..., help="Workflow ID or name"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a workflow."""
    from dtctl.resources.workflow import WorkflowHandler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = WorkflowHandler(client)
    resolver = ResourceResolver(client)

    workflow_id = resolver.resolve_workflow(identifier)

    # Get workflow name for confirmation
    workflow = handler.get(workflow_id)
    name = workflow.get("title", workflow_id)

    if not confirm_delete("workflow", name, force):
        console.print("Aborted.")
        raise typer.Exit(0)

    if handler.delete(workflow_id):
        console.print(f"[green]Deleted workflow:[/green] {name} ({workflow_id})")
    else:
        console.print(f"[red]Failed to delete workflow:[/red] {name}")
        raise typer.Exit(1)


@app.command("dashboard")
@app.command("dash")
def delete_dashboard(
    identifier: str = typer.Argument(..., help="Dashboard ID or name"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a dashboard."""
    from dtctl.resources.document import create_dashboard_handler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_dashboard_handler(client)
    resolver = ResourceResolver(client)

    doc_id = resolver.resolve_document(identifier, "dashboard")

    # Get document name for confirmation
    doc = handler.get(doc_id, metadata_only=True)
    name = doc.get("name", doc_id)

    if not confirm_delete("dashboard", name, force):
        console.print("Aborted.")
        raise typer.Exit(0)

    if handler.delete(doc_id):
        console.print(f"[green]Deleted dashboard:[/green] {name} ({doc_id})")
    else:
        console.print(f"[red]Failed to delete dashboard:[/red] {name}")
        raise typer.Exit(1)


@app.command("notebook")
@app.command("nb")
def delete_notebook(
    identifier: str = typer.Argument(..., help="Notebook ID or name"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a notebook."""
    from dtctl.resources.document import create_notebook_handler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_notebook_handler(client)
    resolver = ResourceResolver(client)

    doc_id = resolver.resolve_document(identifier, "notebook")

    doc = handler.get(doc_id, metadata_only=True)
    name = doc.get("name", doc_id)

    if not confirm_delete("notebook", name, force):
        console.print("Aborted.")
        raise typer.Exit(0)

    if handler.delete(doc_id):
        console.print(f"[green]Deleted notebook:[/green] {name} ({doc_id})")
    else:
        console.print(f"[red]Failed to delete notebook:[/red] {name}")
        raise typer.Exit(1)


@app.command("slo")
def delete_slo(
    identifier: str = typer.Argument(..., help="SLO ID or name"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete an SLO."""
    from dtctl.resources.slo import SLOHandler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = SLOHandler(client)
    resolver = ResourceResolver(client)

    slo_id = resolver.resolve_slo(identifier)

    slo = handler.get(slo_id)
    name = slo.get("name", slo_id)

    if not confirm_delete("SLO", name, force):
        console.print("Aborted.")
        raise typer.Exit(0)

    if handler.delete(slo_id):
        console.print(f"[green]Deleted SLO:[/green] {name} ({slo_id})")
    else:
        console.print(f"[red]Failed to delete SLO:[/red] {name}")
        raise typer.Exit(1)


@app.command("settings")
def delete_settings(
    object_id: str = typer.Argument(..., help="Settings object ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a settings object."""
    from dtctl.resources.settings import SettingsHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = SettingsHandler(client)

    if not confirm_delete("settings object", object_id, force):
        console.print("Aborted.")
        raise typer.Exit(0)

    if handler.delete_object(object_id):
        console.print(f"[green]Deleted settings object:[/green] {object_id}")
    else:
        console.print(f"[red]Failed to delete settings object:[/red] {object_id}")
        raise typer.Exit(1)


@app.command("bucket")
def delete_bucket(
    bucket_name: str = typer.Argument(..., help="Bucket name"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a bucket."""
    from dtctl.resources.bucket import BucketHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = BucketHandler(client)

    if not confirm_delete("bucket", bucket_name, force):
        console.print("Aborted.")
        raise typer.Exit(0)

    if handler.delete(bucket_name):
        console.print(f"[green]Deleted bucket:[/green] {bucket_name}")
    else:
        console.print(f"[red]Failed to delete bucket:[/red] {bucket_name}")
        raise typer.Exit(1)


@app.command("app")
def delete_app(
    app_id: str = typer.Argument(..., help="App ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Uninstall an app."""
    from dtctl.resources.app import AppHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = AppHandler(client)

    if not confirm_delete("app", app_id, force):
        console.print("Aborted.")
        raise typer.Exit(0)

    if handler.uninstall(app_id):
        console.print(f"[green]Uninstalled app:[/green] {app_id}")
    else:
        console.print(f"[red]Failed to uninstall app:[/red] {app_id}")
        raise typer.Exit(1)


@app.command("notification")
def delete_notification(
    notification_id: str = typer.Argument(..., help="Notification ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete a notification."""
    from dtctl.resources.notification import NotificationHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = NotificationHandler(client)

    if not confirm_delete("notification", notification_id, force):
        console.print("Aborted.")
        raise typer.Exit(0)

    if handler.delete(notification_id):
        console.print(f"[green]Deleted notification:[/green] {notification_id}")
    else:
        console.print(f"[red]Failed to delete notification:[/red] {notification_id}")
        raise typer.Exit(1)


@app.command("edgeconnect")
@app.command("ec")
def delete_edgeconnect(
    config_id: str = typer.Argument(..., help="EdgeConnect configuration ID"),
    force: bool = typer.Option(False, "--force", "-f", help="Skip confirmation"),
) -> None:
    """Delete an EdgeConnect configuration."""
    from dtctl.resources.edgeconnect import EdgeConnectHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = EdgeConnectHandler(client)

    if not confirm_delete("EdgeConnect", config_id, force):
        console.print("Aborted.")
        raise typer.Exit(0)

    if handler.delete(config_id):
        console.print(f"[green]Deleted EdgeConnect:[/green] {config_id}")
    else:
        console.print(f"[red]Failed to delete EdgeConnect:[/red] {config_id}")
        raise typer.Exit(1)
