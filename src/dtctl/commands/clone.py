"""Clone command for duplicating resources.

Supports cloning workflows, dashboards, and notebooks with new names.
"""

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


def is_dry_run() -> bool:
    """Check if dry run mode is enabled."""
    from dtctl.cli import state

    return state.dry_run


@app.command("workflow")
@app.command("wf")
def clone_workflow(
    identifier: str = typer.Argument(..., help="Source workflow ID or name"),
    name: str = typer.Option(..., "--name", "-n", help="New workflow name"),
    description: str | None = typer.Option(None, "--description", "-d", help="New description"),
    undeploy: bool = typer.Option(
        True, "--undeploy/--keep-deployed", help="Set cloned workflow to undeployed"
    ),
    output: OutputFormat | None = typer.Option(None, "-o", "--output"),
) -> None:
    """Clone a workflow with a new name.

    Creates a copy of the specified workflow with a new name.
    By default, the cloned workflow is set to undeployed state.

    Examples:
        dtctl clone workflow my-workflow --name "My Workflow Copy"
        dtctl clone workflow abc123 --name "New Name" --description "Cloned workflow"
        dtctl clone workflow my-wf --name "Copy" --keep-deployed
    """
    from dtctl.resources.workflow import WorkflowHandler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = WorkflowHandler(client)
    resolver = ResourceResolver(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    # Resolve source workflow
    workflow_id = resolver.resolve_workflow(identifier)
    source = handler.get(workflow_id)

    # Prepare clone
    clone_data = source.copy()

    # Remove fields that should not be copied
    for field in ["id", "owner", "modificationInfo", "lastExecution"]:
        clone_data.pop(field, None)

    # Set new values
    clone_data["title"] = name
    if description is not None:
        clone_data["description"] = description
    if undeploy:
        clone_data["isDeployed"] = False

    if is_dry_run():
        console.print("[yellow]Dry run:[/yellow] Would create cloned workflow:")
        printer.print(clone_data)
        return

    # Create the clone
    result = handler.create(clone_data)

    if not is_plain_mode():
        console.print(f"[green]Cloned workflow '{source.get('title')}' to '{name}'[/green]")

    printer.print(result)


@app.command("dashboard")
@app.command("dash")
def clone_dashboard(
    identifier: str = typer.Argument(..., help="Source dashboard ID or name"),
    name: str = typer.Option(..., "--name", "-n", help="New dashboard name"),
    description: str | None = typer.Option(None, "--description", "-d", help="New description"),
    private: bool = typer.Option(True, "--private/--public", help="Make cloned dashboard private"),
    output: OutputFormat | None = typer.Option(None, "-o", "--output"),
) -> None:
    """Clone a dashboard with a new name.

    Creates a copy of the specified dashboard with a new name.
    By default, the cloned dashboard is private.

    Examples:
        dtctl clone dashboard my-dashboard --name "My Dashboard Copy"
        dtctl clone dashboard abc123 --name "New Dashboard" --public
    """
    from dtctl.resources.document import create_dashboard_handler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_dashboard_handler(client)
    resolver = ResourceResolver(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    # Resolve source dashboard
    doc_id = resolver.resolve_document(identifier, "dashboard")
    source = handler.get(doc_id)

    # Extract content from source
    content = source.get("content", source)
    source_description = source.get("description", "")

    if is_dry_run():
        console.print(
            f"[yellow]Dry run:[/yellow] Would clone dashboard '{source.get('name')}' to '{name}'"
        )
        return

    # Create the clone
    result = handler.create(
        name=name,
        doc_type="dashboard",
        content=content,
        description=description if description is not None else source_description,
        is_private=private,
    )

    if not is_plain_mode():
        console.print(f"[green]Cloned dashboard '{source.get('name')}' to '{name}'[/green]")

    printer.print(result)


@app.command("notebook")
@app.command("nb")
def clone_notebook(
    identifier: str = typer.Argument(..., help="Source notebook ID or name"),
    name: str = typer.Option(..., "--name", "-n", help="New notebook name"),
    description: str | None = typer.Option(None, "--description", "-d", help="New description"),
    private: bool = typer.Option(True, "--private/--public", help="Make cloned notebook private"),
    output: OutputFormat | None = typer.Option(None, "-o", "--output"),
) -> None:
    """Clone a notebook with a new name.

    Creates a copy of the specified notebook with a new name.
    By default, the cloned notebook is private.

    Examples:
        dtctl clone notebook my-notebook --name "My Notebook Copy"
        dtctl clone notebook abc123 --name "New Notebook" --public
    """
    from dtctl.resources.document import create_notebook_handler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_notebook_handler(client)
    resolver = ResourceResolver(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    # Resolve source notebook
    doc_id = resolver.resolve_document(identifier, "notebook")
    source = handler.get(doc_id)

    # Extract content from source
    content = source.get("content", source)
    source_description = source.get("description", "")

    if is_dry_run():
        console.print(
            f"[yellow]Dry run:[/yellow] Would clone notebook '{source.get('name')}' to '{name}'"
        )
        return

    # Create the clone
    result = handler.create(
        name=name,
        doc_type="notebook",
        content=content,
        description=description if description is not None else source_description,
        is_private=private,
    )

    if not is_plain_mode():
        console.print(f"[green]Cloned notebook '{source.get('name')}' to '{name}'[/green]")

    printer.print(result)


@app.command("slo")
def clone_slo(
    identifier: str = typer.Argument(..., help="Source SLO ID or name"),
    name: str = typer.Option(..., "--name", "-n", help="New SLO name"),
    description: str | None = typer.Option(None, "--description", "-d", help="New description"),
    disabled: bool = typer.Option(
        True, "--disabled/--enabled", help="Create cloned SLO as disabled"
    ),
    output: OutputFormat | None = typer.Option(None, "-o", "--output"),
) -> None:
    """Clone an SLO with a new name.

    Creates a copy of the specified SLO with a new name.
    By default, the cloned SLO is disabled.

    Examples:
        dtctl clone slo my-slo --name "My SLO Copy"
        dtctl clone slo abc123 --name "New SLO" --enabled
    """
    from dtctl.resources.slo import SLOHandler
    from dtctl.utils.resolver import ResourceResolver

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = SLOHandler(client)
    resolver = ResourceResolver(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    # Resolve source SLO
    slo_id = resolver.resolve_slo(identifier)
    source = handler.get(slo_id)

    # Prepare clone
    clone_data = source.copy()

    # Remove fields that should not be copied
    for field in ["id", "status", "evaluatedPercentage", "errorBudget", "relatedOpenProblems"]:
        clone_data.pop(field, None)

    # Set new values
    clone_data["name"] = name
    if description is not None:
        clone_data["description"] = description
    if disabled:
        clone_data["enabled"] = False

    if is_dry_run():
        console.print("[yellow]Dry run:[/yellow] Would create cloned SLO:")
        printer.print(clone_data)
        return

    # Create the clone
    result = handler.create(clone_data)

    if not is_plain_mode():
        console.print(f"[green]Cloned SLO '{source.get('name')}' to '{name}'[/green]")

    printer.print(result)
