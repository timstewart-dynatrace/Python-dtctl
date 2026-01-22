# Architecture

## Project Structure

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
│   ├── template.py      # Template rendering and validation
│   ├── wait.py          # Wait for DQL conditions
│   ├── history.py       # View version history
│   ├── restore.py       # Restore to previous versions
│   ├── auth.py          # Authentication operations
│   ├── completion.py    # Shell completion generation
│   └── chown.py         # Change ownership of documents
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
│   ├── query.py         # DQL query execution
│   └── lookup.py        # Lookup tables
└── utils/               # Utility modules
    ├── template.py      # Jinja2 template rendering
    ├── format.py        # YAML/JSON conversion
    ├── resolver.py      # Name-to-ID resolution
    ├── cache.py         # In-memory caching with TTL
    └── auth.py          # OAuth2 authentication (optional)
```

## Core Components

### CLI Framework (cli.py)
Uses Typer for command handling with global state for shared options (context, output format, verbose, plain, dry-run).

### HTTP Client (client.py)
Built on httpx with:
- Automatic retry with exponential backoff
- Rate limit handling (429 status)
- Bearer token authentication
- Configurable timeout (30s default)

### Configuration (config.py)
Pydantic models for:
- Multi-context support (like kubectl)
- XDG Base Directory compliance (~/.config/dtctl/config)
- Token storage and retrieval
- Optional OAuth2 authentication support
- Environment variable overrides (DTCTL_CONTEXT, DTCTL_OUTPUT, DTCTL_VERBOSE)

### Output (output.py)
Pluggable formatters:
- TableFormatter (Rich tables)
- JSONFormatter (indented JSON)
- YAMLFormatter (PyYAML)
- CSVFormatter
- PlainFormatter (machine-readable JSON)

### Resource Handlers (resources/)
Each resource type extends `CRUDHandler` or `ResourceHandler` base class with:
- list(), get(), create(), update(), delete() methods
- Consistent error handling
- API path configuration

## Key Design Patterns

### Handler Pattern
Each resource type has a handler class that encapsulates API operations.

### Factory Functions
`create_client_from_config()` creates configured clients from context settings.

### Resolver Pattern
`ResourceResolver` converts human-readable names to API IDs.

### Template Pattern
Jinja2 templates with `--set key=value` substitution for manifests and queries.

### Caching Pattern
In-memory singleton cache with TTL for reducing API calls. The `@cached` decorator enables transparent caching on handler methods.

### Clone Pattern
Resource handlers support cloning by fetching, modifying, and creating new resources with updated names/properties.
