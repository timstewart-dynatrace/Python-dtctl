# AGENTS.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

> **⚠️ DISCLAIMER**: This tool is **not produced, endorsed, or supported by Dynatrace**. It is an independent, community-driven project. **Use at your own risk.** The authors assume no liability for any issues arising from its use.

## Project Overview

`dtctl` is a kubectl-like CLI tool for interacting with the Dynatrace REST API. The tool follows kubectl's design patterns:
- Resource-oriented commands (get, describe, create, delete, edit, apply, exec)
- Support for multiple output formats (JSON, YAML, table, CSV)
- Configuration management via config files
- Context switching between environments

**Important**: Use kubectl naming conventions (e.g., `exec` not `execute`). Exclude classic-environment v1 and v2 APIs.

## Architecture

### Project Structure

```
src/dtctl/
├── cli.py               # Main CLI entry point (Typer app)
├── client.py            # HTTP client with retry/auth
├── config.py            # Multi-context configuration (Pydantic)
├── output.py            # Output formatters (Rich tables, JSON, YAML)
├── commands/            # CLI command modules
│   ├── config.py        # Configuration management
│   ├── get.py           # List/retrieve resources (incl. limits, environments)
│   ├── describe.py      # Detailed resource info
│   ├── create.py        # Create from manifests
│   ├── delete.py        # Delete resources
│   ├── apply.py         # Declarative create/update
│   ├── edit.py          # Interactive editing
│   ├── query.py         # DQL query execution
│   ├── execute.py       # Workflow/analyzer execution
│   ├── logs.py          # Execution logs
│   ├── share.py         # Document sharing
│   ├── cache.py         # Cache management commands
│   ├── bulk.py          # Bulk operations (apply, delete, execute)
│   ├── export.py        # Export resources to files
│   ├── clone.py         # Clone/duplicate resources
│   └── template.py      # Template rendering and validation
├── resources/           # API resource handlers
│   ├── base.py          # Base handler classes (CRUDHandler)
│   ├── workflow.py      # Workflows & executions
│   ├── document.py      # Dashboards & notebooks
│   ├── slo.py           # SLOs
│   ├── settings.py      # Settings objects & schemas
│   ├── bucket.py        # Grail storage buckets
│   ├── app.py           # App Engine apps
│   ├── iam.py           # Users, groups, policies, bindings, boundaries (read-only)
│   ├── notification.py  # Event notifications
│   ├── analyzer.py      # Davis AI analyzers
│   ├── copilot.py       # Davis CoPilot
│   ├── openpipeline.py  # OpenPipeline configurations
│   ├── edgeconnect.py   # EdgeConnect configurations
│   ├── limits.py        # Account limits & quotas
│   └── query.py         # DQL query execution
└── utils/               # Utility modules
    ├── template.py      # Jinja2 template rendering
    ├── format.py        # YAML/JSON conversion
    ├── resolver.py      # Name-to-ID resolution
    ├── cache.py         # In-memory caching with TTL
    └── auth.py          # OAuth2 authentication (optional)
```

### Core Components

**CLI Framework (cli.py)**: Uses Typer for command handling with global state for shared options (context, output format, verbose, plain, dry-run).

**HTTP Client (client.py)**: Built on httpx with:
- Automatic retry with exponential backoff
- Rate limit handling (429 status)
- Bearer token authentication
- Configurable timeout (30s default)

**Configuration (config.py)**: Pydantic models for:
- Multi-context support (like kubectl)
- XDG Base Directory compliance (~/.config/dtctl/config)
- Token storage and retrieval
- Optional OAuth2 authentication support
- Environment variable overrides (DTCTL_CONTEXT, DTCTL_OUTPUT, DTCTL_VERBOSE)

**Output (output.py)**: Pluggable formatters:
- TableFormatter (Rich tables)
- JSONFormatter (indented JSON)
- YAMLFormatter (PyYAML)
- CSVFormatter
- PlainFormatter (machine-readable JSON)

**Resource Handlers (resources/)**: Each resource type extends `CRUDHandler` or `ResourceHandler` base class with:
- list(), get(), create(), update(), delete() methods
- Consistent error handling
- API path configuration

### Key Design Patterns

**Handler Pattern**: Each resource type has a handler class that encapsulates API operations.

**Factory Functions**: `create_client_from_config()` creates configured clients from context settings.

**Resolver Pattern**: `ResourceResolver` converts human-readable names to API IDs.

**Template Pattern**: Jinja2 templates with `--set key=value` substitution for manifests and queries.

**Caching Pattern**: In-memory singleton cache with TTL for reducing API calls. The `@cached` decorator enables transparent caching on handler methods.

**Clone Pattern**: Resource handlers support cloning by fetching, modifying, and creating new resources with updated names/properties.

## Development Conventions

### Technology Stack
- **Language**: Python 3.10+
- **CLI Framework**: Typer (Click-based, type hints)
- **HTTP Client**: httpx (async-capable, modern)
- **Data Models**: Pydantic v2 (validation, serialization)
- **Output**: Rich (tables, formatting, colors)
- **Configuration**: PyYAML, platformdirs (XDG paths)
- **Templates**: Jinja2

### Code Style
- Type hints on all functions
- Docstrings for public APIs
- Use `from __future__ import annotations` for forward references
- Follow PEP 8 with 100 char line limit
- Use Ruff for linting/formatting

### Adding New Resources

1. Create handler in `src/dtctl/resources/<resource>.py`:
```python
from dtctl.resources.base import CRUDHandler

class MyResourceHandler(CRUDHandler):
    @property
    def resource_name(self) -> str:
        return "myresource"

    @property
    def api_path(self) -> str:
        return "/platform/api/v1/myresources"
```

2. Add commands in `src/dtctl/commands/get.py`, `delete.py`, etc.

3. Define columns in `src/dtctl/output.py` for table output.

### Adding New Commands

1. Create command module in `src/dtctl/commands/<command>.py`
2. Register in `src/dtctl/cli.py` with `app.add_typer()`
3. Use helper functions for shared state access:
   - `get_context()` - context override
   - `get_output_format()` - output format
   - `is_verbose()` - verbose mode
   - `is_plain_mode()` - plain mode
   - `is_dry_run()` - dry-run mode

### Resource Naming
Follow kubectl conventions:
- Singular resource names in commands
- Abbreviations/aliases (e.g., `wf` for `workflow`, `dash` for `dashboard`)
- Use `@app.command()` decorator multiple times for aliases

### Error Handling
- Use `typer.Exit(1)` for errors
- Print errors with `[red]Error:[/red]` prefix using Rich
- Provide actionable error messages
- Include API error details when relevant

### Testing
```bash
# Run tests
pytest

# Run with coverage
pytest --cov=dtctl

# Type checking
mypy src/dtctl
```

## Common Tasks

### Build and Install
```bash
pip install -e .           # Development install
pip install -e ".[dev]"    # With dev dependencies
```

### Run CLI
```bash
dtctl --help
dtctl config view
dtctl get workflows
dtctl get limits
dtctl get environments
dtctl clone workflow my-wf --name "Copy"
dtctl template render -f manifest.yaml --set env=prod
```

### Format Code
```bash
ruff format src/
ruff check src/ --fix
```

## Available Commands

| Command | Description |
|---------|-------------|
| `config` | Manage configuration contexts and credentials |
| `get` | List or get resources (workflows, dashboards, slos, limits, environments, etc.) |
| `describe` | Show detailed resource information |
| `create` | Create resources from manifests |
| `delete` | Delete resources |
| `apply` | Apply configuration (create or update) |
| `edit` | Edit resources in your editor |
| `query` | Execute DQL queries |
| `exec` | Execute workflows, analyzers, copilot |
| `logs` | View execution logs |
| `share` | Share documents |
| `unshare` | Remove document sharing |
| `bulk` | Bulk operations on resources |
| `export` | Export resources to files |
| `cache` | Manage API response cache |
| `clone` | Clone/duplicate resources |
| `template` | Render and validate templates |

## Supported Resources

- **Workflows** (`workflows`, `wf`)
- **Executions** (`executions`, `exec`)
- **Dashboards** (`dashboards`, `dash`)
- **Notebooks** (`notebooks`, `nb`)
- **SLOs** (`slos`, `slo`)
- **Settings** (`settings`)
- **Settings Schemas** (`schemas`)
- **Buckets** (`buckets`)
- **Apps** (`apps`)
- **Users** (`users`)
- **Groups** (`groups`)
- **Policies** (`policies`)
- **Bindings** (`bindings`)
- **Boundaries** (`boundaries`)
- **Effective Permissions** (`effective-permissions`)
- **Notifications** (`notifications`)
- **Analyzers** (`analyzers`)
- **CoPilot Skills** (`copilot-skills`)
- **EdgeConnect** (`edgeconnects`, `ec`)
- **OpenPipeline** (`openpipelines`, `op`)
- **Limits** (`limits`)
- **Environments** (`environments`, `env`)
