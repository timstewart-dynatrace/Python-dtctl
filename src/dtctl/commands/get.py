"""Get command for listing and retrieving resources."""

from __future__ import annotations

from typing import Optional

import typer
from rich.console import Console

from dtctl.client import create_client_from_config
from dtctl.config import load_config
from dtctl.output import (
    Printer,
    OutputFormat,
    workflow_columns,
    execution_columns,
    document_columns,
    slo_columns,
    settings_columns,
    bucket_columns,
    app_columns,
    user_columns,
    group_columns,
)

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


@app.command("workflows")
@app.command("wf")
def get_workflows(
    identifier: Optional[str] = typer.Argument(None, help="Workflow ID or name"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Filter by name"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get workflows."""
    from dtctl.resources.workflow import WorkflowHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = WorkflowHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if identifier:
        # Get single workflow
        from dtctl.utils.resolver import ResourceResolver
        resolver = ResourceResolver(client)
        workflow_id = resolver.resolve_workflow(identifier)
        result = handler.get(workflow_id)
        printer.print(result)
    else:
        # List workflows
        results = handler.list()
        if name:
            results = [w for w in results if name.lower() in w.get("title", "").lower()]
        printer.print(results, workflow_columns())


@app.command("executions")
@app.command("exec")
def get_executions(
    identifier: Optional[str] = typer.Argument(None, help="Execution ID"),
    workflow: Optional[str] = typer.Option(None, "--workflow", "-w", help="Filter by workflow"),
    state_filter: Optional[str] = typer.Option(None, "--state", "-s", help="Filter by state"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get workflow executions."""
    from dtctl.resources.workflow import ExecutionHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = ExecutionHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if identifier:
        result = handler.get_execution(identifier)
        printer.print(result)
    else:
        results = handler.list_executions(workflow_id=workflow, state=state_filter)
        printer.print(results, execution_columns())


@app.command("dashboards")
@app.command("dash")
def get_dashboards(
    identifier: Optional[str] = typer.Argument(None, help="Dashboard ID or name"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Filter by name"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get dashboards."""
    from dtctl.resources.document import create_dashboard_handler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_dashboard_handler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if identifier:
        from dtctl.utils.resolver import ResourceResolver
        resolver = ResourceResolver(client)
        doc_id = resolver.resolve_document(identifier, "dashboard")
        result = handler.get(doc_id)
        printer.print(result)
    else:
        results = handler.list(name_filter=name)
        printer.print(results, document_columns())


@app.command("notebooks")
@app.command("nb")
def get_notebooks(
    identifier: Optional[str] = typer.Argument(None, help="Notebook ID or name"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Filter by name"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get notebooks."""
    from dtctl.resources.document import create_notebook_handler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = create_notebook_handler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if identifier:
        from dtctl.utils.resolver import ResourceResolver
        resolver = ResourceResolver(client)
        doc_id = resolver.resolve_document(identifier, "notebook")
        result = handler.get(doc_id)
        printer.print(result)
    else:
        results = handler.list(name_filter=name)
        printer.print(results, document_columns())


@app.command("slos")
@app.command("slo")
def get_slos(
    identifier: Optional[str] = typer.Argument(None, help="SLO ID or name"),
    name: Optional[str] = typer.Option(None, "--name", "-n", help="Filter by name"),
    enabled: bool = typer.Option(False, "--enabled", help="Only show enabled SLOs"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get SLOs."""
    from dtctl.resources.slo import SLOHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = SLOHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if identifier:
        from dtctl.utils.resolver import ResourceResolver
        resolver = ResourceResolver(client)
        slo_id = resolver.resolve_slo(identifier)
        result = handler.get(slo_id)
        printer.print(result)
    else:
        results = handler.list(enabled_only=enabled, name_filter=name)
        printer.print(results, slo_columns())


@app.command("settings")
def get_settings(
    object_id: Optional[str] = typer.Argument(None, help="Settings object ID"),
    schema: Optional[str] = typer.Option(None, "--schema", "-s", help="Filter by schema ID"),
    scope: Optional[str] = typer.Option(None, "--scope", help="Filter by scope"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get settings objects."""
    from dtctl.resources.settings import SettingsHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = SettingsHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if object_id:
        result = handler.get_object(object_id)
        printer.print(result)
    else:
        results = handler.list_objects(schema_id=schema, scope=scope)
        printer.print(results, settings_columns())


@app.command("schemas")
def get_schemas(
    schema_id: Optional[str] = typer.Argument(None, help="Schema ID"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get settings schemas."""
    from dtctl.resources.settings import SettingsHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = SettingsHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if schema_id:
        result = handler.get_schema(schema_id)
        printer.print(result)
    else:
        results = handler.list_schemas()
        printer.print(results)


@app.command("buckets")
def get_buckets(
    bucket_name: Optional[str] = typer.Argument(None, help="Bucket name"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get Grail buckets."""
    from dtctl.resources.bucket import BucketHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = BucketHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if bucket_name:
        result = handler.get(bucket_name)
        printer.print(result)
    else:
        results = handler.list()
        printer.print(results, bucket_columns())


@app.command("apps")
def get_apps(
    app_id: Optional[str] = typer.Argument(None, help="App ID"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get installed apps."""
    from dtctl.resources.app import AppHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = AppHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if app_id:
        result = handler.get(app_id)
        printer.print(result)
    else:
        results = handler.list()
        printer.print(results, app_columns())


@app.command("users")
def get_users(
    user_id: Optional[str] = typer.Argument(None, help="User ID or email"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get users."""
    from dtctl.resources.iam import IAMHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = IAMHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if user_id:
        result = handler.get_user(user_id)
        printer.print(result)
    else:
        results = handler.list_users()
        printer.print(results, user_columns())


@app.command("groups")
def get_groups(
    group_id: Optional[str] = typer.Argument(None, help="Group UUID"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get groups."""
    from dtctl.resources.iam import IAMHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = IAMHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if group_id:
        result = handler.get_group(group_id)
        printer.print(result)
    else:
        results = handler.list_groups()
        printer.print(results, group_columns())


@app.command("notifications")
def get_notifications(
    notification_id: Optional[str] = typer.Argument(None, help="Notification ID"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get notifications."""
    from dtctl.resources.notification import NotificationHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = NotificationHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if notification_id:
        result = handler.get(notification_id)
        printer.print(result)
    else:
        results = handler.list()
        printer.print(results)


@app.command("analyzers")
def get_analyzers(
    analyzer_name: Optional[str] = typer.Argument(None, help="Analyzer name"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get Davis analyzers."""
    from dtctl.resources.analyzer import AnalyzerHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = AnalyzerHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if analyzer_name:
        result = handler.get(analyzer_name)
        printer.print(result)
    else:
        results = handler.list()
        printer.print(results)


@app.command("copilot-skills")
def get_copilot_skills(
    skill_name: Optional[str] = typer.Argument(None, help="Skill name"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get CoPilot skills."""
    from dtctl.resources.copilot import CoPilotHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = CoPilotHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if skill_name:
        result = handler.get_skill(skill_name)
        printer.print(result)
    else:
        results = handler.list_skills()
        printer.print(results)


@app.command("edgeconnects")
@app.command("ec")
def get_edgeconnects(
    config_id: Optional[str] = typer.Argument(None, help="EdgeConnect configuration ID"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get EdgeConnect configurations."""
    from dtctl.resources.edgeconnect import EdgeConnectHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = EdgeConnectHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if config_id:
        result = handler.get(config_id)
        printer.print(result)
    else:
        results = handler.list()
        printer.print(results)


@app.command("openpipelines")
@app.command("op")
def get_openpipelines(
    pipeline_id: Optional[str] = typer.Argument(None, help="Pipeline ID"),
    output: Optional[OutputFormat] = typer.Option(None, "-o", "--output"),
) -> None:
    """List or get OpenPipeline configurations."""
    from dtctl.resources.openpipeline import OpenPipelineHandler

    config = load_config()
    client = create_client_from_config(config, get_context(), is_verbose())
    handler = OpenPipelineHandler(client)

    fmt = output or get_output_format()
    printer = Printer(format=fmt, plain=is_plain_mode())

    if pipeline_id:
        result = handler.get(pipeline_id)
        printer.print(result)
    else:
        results = handler.list()
        printer.print(results)
