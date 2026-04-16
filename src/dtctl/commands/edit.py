"""Edit command for interactive resource editing."""

from __future__ import annotations

import os
import subprocess
import tempfile

import typer
from rich.console import Console

from dtctl.client import create_client_from_config
from dtctl.config import load_config
from dtctl.utils.format import parse_content, to_json, to_yaml

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


def get_editor() -> str:
    """Get the editor to use."""
    config = load_config()
    return os.environ.get("EDITOR", config.preferences.editor)


def edit_in_editor(content: str, suffix: str = ".yaml") -> str | None:
    """Open content in external editor and return modified content.

    Returns None if content was not modified.
    """
    editor = get_editor()

    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=suffix,
        delete=False,
    ) as f:
        f.write(content)
        temp_path = f.name

    try:
        # Open editor
        result = subprocess.run([editor, temp_path])
        if result.returncode != 0:
            console.print(f"[red]Editor exited with error code {result.returncode}[/red]")
            return None

        # Read modified content
        with open(temp_path) as f:
            modified = f.read()

        if modified == content:
            return None  # No changes

        return modified
    finally:
        os.unlink(temp_path)


@app.command("workflow")
@app.command("wf")
def edit_workflow(
    identifier: str = typer.Argument(..., help="Workflow ID or name"),
    format: str = typer.Option("yaml", "--format", "-f", help="Edit format (yaml or json)"),
) -> None:
    """Edit a workflow in your default editor."""
    from dtctl.resources.workflow import WorkflowHandler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = WorkflowHandler(client)
    resolver = ResourceResolver(client)

    workflow_id = resolver.resolve_workflow(identifier)
    workflow = handler.get(workflow_id)

    # Convert to edit format
    if format == "json":
        content = to_json(workflow)
        suffix = ".json"
    else:
        content = to_yaml(workflow)
        suffix = ".yaml"

    console.print(f"Opening workflow in {get_editor()}...")

    modified = edit_in_editor(content, suffix)
    if modified is None:
        console.print("No changes made.")
        return

    # Parse and update
    try:
        data = parse_content(modified)
    except ValueError as e:
        console.print(f"[red]Error parsing modified content:[/red] {e}")
        raise typer.Exit(1) from None

    result = handler.update(workflow_id, data)
    console.print(f"[green]Updated workflow:[/green] {result.get('id')}")


@app.command("dashboard")
@app.command("dash")
def edit_dashboard(
    identifier: str = typer.Argument(..., help="Dashboard ID or name"),
    format: str = typer.Option("yaml", "--format", "-f", help="Edit format (yaml or json)"),
) -> None:
    """Edit a dashboard in your default editor."""
    from dtctl.resources.document import create_dashboard_handler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_dashboard_handler(client)
    resolver = ResourceResolver(client)

    doc_id = resolver.resolve_document(identifier, "dashboard")
    document = handler.get(doc_id)

    if format == "json":
        content = to_json(document)
        suffix = ".json"
    else:
        content = to_yaml(document)
        suffix = ".yaml"

    console.print(f"Opening dashboard in {get_editor()}...")

    modified = edit_in_editor(content, suffix)
    if modified is None:
        console.print("No changes made.")
        return

    try:
        data = parse_content(modified)
    except ValueError as e:
        console.print(f"[red]Error parsing modified content:[/red] {e}")
        raise typer.Exit(1) from None

    version = document.get("version")
    result = handler.update(doc_id, data, optimistic_locking_version=version)
    console.print(f"[green]Updated dashboard:[/green] {result.get('id')}")


@app.command("notebook")
@app.command("nb")
def edit_notebook(
    identifier: str = typer.Argument(..., help="Notebook ID or name"),
    format: str = typer.Option("yaml", "--format", "-f", help="Edit format (yaml or json)"),
) -> None:
    """Edit a notebook in your default editor."""
    from dtctl.resources.document import create_notebook_handler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_notebook_handler(client)
    resolver = ResourceResolver(client)

    doc_id = resolver.resolve_document(identifier, "notebook")
    document = handler.get(doc_id)

    if format == "json":
        content = to_json(document)
        suffix = ".json"
    else:
        content = to_yaml(document)
        suffix = ".yaml"

    console.print(f"Opening notebook in {get_editor()}...")

    modified = edit_in_editor(content, suffix)
    if modified is None:
        console.print("No changes made.")
        return

    try:
        data = parse_content(modified)
    except ValueError as e:
        console.print(f"[red]Error parsing modified content:[/red] {e}")
        raise typer.Exit(1) from None

    version = document.get("version")
    result = handler.update(doc_id, data, optimistic_locking_version=version)
    console.print(f"[green]Updated notebook:[/green] {result.get('id')}")


@app.command("slo")
def edit_slo(
    identifier: str = typer.Argument(..., help="SLO ID or name"),
    format: str = typer.Option("yaml", "--format", "-f", help="Edit format (yaml or json)"),
) -> None:
    """Edit an SLO in your default editor."""
    from dtctl.resources.slo import SLOHandler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = SLOHandler(client)
    resolver = ResourceResolver(client)

    slo_id = resolver.resolve_slo(identifier)
    slo = handler.get(slo_id)

    if format == "json":
        content = to_json(slo)
        suffix = ".json"
    else:
        content = to_yaml(slo)
        suffix = ".yaml"

    console.print(f"Opening SLO in {get_editor()}...")

    modified = edit_in_editor(content, suffix)
    if modified is None:
        console.print("No changes made.")
        return

    try:
        data = parse_content(modified)
    except ValueError as e:
        console.print(f"[red]Error parsing modified content:[/red] {e}")
        raise typer.Exit(1) from None

    result = handler.update(slo_id, data)
    console.print(f"[green]Updated SLO:[/green] {result.get('id')}")
