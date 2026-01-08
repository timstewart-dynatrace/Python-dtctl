# dtctl Architecture

## Executive Summary

This document describes the Python-based architecture for `dtctl`, a kubectl-inspired CLI for managing Dynatrace platform resources. Python provides excellent CLI tooling, cross-platform compatibility, and a mature ecosystem for building robust command-line applications.

## Technology Stack

### Core Language: Python 3.10+

**Rationale:**
- **Modern Python**: Type hints, dataclasses, and modern async support
- **Cross-platform**: Works on Linux, macOS, Windows without compilation
- **Rich ecosystem**: Excellent libraries for CLI development, HTTP clients, and data validation
- **Developer familiarity**: Python is widely known in DevOps/SRE communities
- **Rapid development**: Quick iteration and easy maintenance

### CLI Framework: Typer

**Repository**: https://github.com/tiangolo/typer

**Features:**
- Built on Click with automatic type inference
- Automatic help generation from type hints
- Shell completion (bash, zsh, fish, powershell)
- Rich integration for beautiful output
- Subcommand support for hierarchical commands
- **Used by**: Many modern Python CLIs

**Usage:**
```python
import typer

app = typer.Typer()

@app.command()
def get(
    resource: str,
    name: str = typer.Argument(None),
    output: str = typer.Option("table", "-o", "--output"),
):
    """Get/list resources."""
    ...
```

### Data Validation: Pydantic v2

**Repository**: https://github.com/pydantic/pydantic

**Features:**
- Data validation using Python type hints
- JSON/YAML serialization with aliases
- Automatic documentation generation
- Fast validation (Rust core in v2)

**Usage:**
```python
from pydantic import BaseModel, Field

class Context(BaseModel):
    environment: str
    token_ref: str = Field(alias="token-ref")

    model_config = {"populate_by_name": True}
```

### HTTP Client: httpx

**Repository**: https://github.com/encode/httpx

**Features:**
- Modern, async-capable HTTP client
- Connection pooling
- Automatic retries (with tenacity)
- Request/response middleware
- Timeout configuration
- HTTP/2 support

**Usage:**
```python
import httpx

client = httpx.Client(
    base_url=base_url,
    headers={"Authorization": f"Bearer {token}"},
    timeout=30.0,
)
response = client.get("/api/v1/resources")
```

### Output Formatting: Rich

**Repository**: https://github.com/Textualize/rich

**Features:**
- Beautiful terminal output
- Tables with alignment and styling
- Syntax highlighting
- Progress bars
- Markdown rendering
- Color support with graceful degradation

**Usage:**
```python
from rich.console import Console
from rich.table import Table

console = Console()
table = Table(show_header=True)
table.add_column("ID")
table.add_column("Name")
table.add_row("123", "My Resource")
console.print(table)
```

### Configuration: PyYAML + platformdirs

**Packages:**
- `pyyaml` for YAML parsing
- `platformdirs` for XDG-compliant paths

**Features:**
- YAML configuration files
- Cross-platform config directories
- Environment variable overrides

**XDG Directory Structure:**
- **Linux**: `$XDG_CONFIG_HOME/dtctl` (default: `~/.config/dtctl`)
- **macOS**: `~/Library/Application Support/dtctl`
- **Windows**: `%LOCALAPPDATA%\dtctl`

### Template Engine: Jinja2

**Repository**: https://github.com/pallets/jinja

**Features:**
- Template variable substitution
- Default values with filters
- Familiar syntax: `{{ variable }}`

---

## Project Structure

```
dtctl/
├── src/dtctl/
│   ├── __init__.py              # Package version
│   ├── cli.py                   # Main CLI entry point (Typer app)
│   ├── client.py                # HTTP client with retry/auth
│   ├── config.py                # Configuration management (Pydantic)
│   ├── output.py                # Output formatters
│   │
│   ├── commands/                # CLI command modules
│   │   ├── __init__.py
│   │   ├── config.py            # Config management commands
│   │   ├── get.py               # Get/list resources
│   │   ├── describe.py          # Detailed resource info
│   │   ├── create.py            # Create from manifests
│   │   ├── delete.py            # Delete resources
│   │   ├── apply.py             # Apply (create/update)
│   │   ├── edit.py              # Interactive editing
│   │   ├── query.py             # DQL queries
│   │   ├── execute.py           # Workflow/analyzer execution
│   │   ├── logs.py              # Execution logs
│   │   └── share.py             # Document sharing
│   │
│   ├── resources/               # API resource handlers
│   │   ├── __init__.py
│   │   ├── base.py              # Base handler classes
│   │   ├── workflow.py          # Workflows & executions
│   │   ├── document.py          # Dashboards & notebooks
│   │   ├── slo.py               # SLOs
│   │   ├── settings.py          # Settings & schemas
│   │   ├── bucket.py            # Grail buckets
│   │   ├── app.py               # App Engine apps
│   │   ├── iam.py               # Users & groups
│   │   ├── notification.py      # Notifications
│   │   ├── analyzer.py          # Davis analyzers
│   │   ├── copilot.py           # Davis CoPilot
│   │   ├── openpipeline.py      # OpenPipeline
│   │   ├── edgeconnect.py       # EdgeConnect
│   │   └── query.py             # DQL execution
│   │
│   └── utils/                   # Utility modules
│       ├── __init__.py
│       ├── template.py          # Jinja2 templates
│       ├── format.py            # YAML/JSON conversion
│       └── resolver.py          # Name-to-ID resolution
│
├── tests/                       # Test suite
│   └── __init__.py
│
├── docs/                        # Documentation
│   ├── API_DESIGN.md
│   ├── ARCHITECTURE.md
│   ├── DESIGN_PRINCIPLES.md
│   ├── IMPLEMENTATION_STATUS.md
│   ├── INSTALLATION.md
│   └── QUICK_START.md
│
├── pyproject.toml               # Project configuration
├── README.md
├── AGENTS.md                    # Claude Code guidance
└── CLAUDE.md                    # Points to AGENTS.md
```

---

## Core Implementation Patterns

### 1. Command Pattern

```python
# src/dtctl/commands/get.py
import typer
from dtctl.client import create_client_from_config
from dtctl.config import load_config
from dtctl.output import Printer

app = typer.Typer()

@app.command("workflows")
@app.command("wf")  # Alias
def get_workflows(
    identifier: str = typer.Argument(None),
    output: str = typer.Option("table", "-o", "--output"),
):
    """List or get workflows."""
    config = load_config()
    client = create_client_from_config(config)
    handler = WorkflowHandler(client)

    if identifier:
        result = handler.get(identifier)
    else:
        result = handler.list()

    printer = Printer(format=output)
    printer.print(result)
```

### 2. Resource Handler Pattern

```python
# src/dtctl/resources/base.py
from abc import ABC, abstractmethod
from dtctl.client import Client

class CRUDHandler(ABC):
    def __init__(self, client: Client):
        self.client = client

    @property
    @abstractmethod
    def api_path(self) -> str:
        pass

    def list(self, **params) -> list[dict]:
        response = self.client.get(self.api_path, params=params)
        return response.json().get("results", [])

    def get(self, resource_id: str) -> dict:
        response = self.client.get(f"{self.api_path}/{resource_id}")
        return response.json()

    def create(self, data: dict) -> dict:
        response = self.client.post(self.api_path, json=data)
        return response.json()

    def delete(self, resource_id: str) -> bool:
        self.client.delete(f"{self.api_path}/{resource_id}")
        return True
```

### 3. Output Formatting Pattern

```python
# src/dtctl/output.py
from abc import ABC, abstractmethod
from rich.table import Table
import json
import yaml

class Formatter(ABC):
    @abstractmethod
    def format(self, data, columns=None) -> str:
        pass

class TableFormatter(Formatter):
    def format(self, data, columns=None) -> str:
        table = Table()
        for col in columns:
            table.add_column(col.header)
        for row in data:
            table.add_row(*[col.get_value(row) for col in columns])
        return table

class JSONFormatter(Formatter):
    def format(self, data, columns=None) -> str:
        return json.dumps(data, indent=2)
```

### 4. Configuration Pattern

```python
# src/dtctl/config.py
from pydantic import BaseModel, Field
from platformdirs import user_config_dir
import yaml

class Config(BaseModel):
    api_version: str = Field(default="v1", alias="apiVersion")
    current_context: str = Field(default="", alias="current-context")
    contexts: list[NamedContext] = []
    tokens: list[NamedToken] = []

    model_config = {"populate_by_name": True}

def load_config() -> Config:
    config_path = Path(user_config_dir("dtctl")) / "config"
    if config_path.exists():
        data = yaml.safe_load(config_path.read_text())
        return Config.model_validate(data)
    return Config()
```

### 5. HTTP Client Pattern

```python
# src/dtctl/client.py
import httpx
import time

class Client:
    def __init__(self, base_url: str, token: str):
        self._client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {token}"},
            timeout=30.0,
        )

    def request(self, method: str, path: str, **kwargs) -> httpx.Response:
        for attempt in range(3):
            response = self._client.request(method, path, **kwargs)
            if response.status_code != 429:
                return response
            time.sleep(2 ** attempt)
        return response
```

---

## Dependency Management

### pyproject.toml

```toml
[project]
name = "dtctl"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "typer[all]>=0.9.0",
    "httpx>=0.27.0",
    "pyyaml>=6.0",
    "pydantic>=2.0",
    "rich>=13.0",
    "platformdirs>=4.0",
    "jinja2>=3.1",
]

[project.scripts]
dtctl = "dtctl.cli:main"
```

---

## Build & Distribution

### Installation

```bash
# Development install
pip install -e .

# With dev dependencies
pip install -e ".[dev]"

# Production install
pip install dtctl
```

### Shell Completion

```bash
# Bash
dtctl --install-completion bash

# Zsh
dtctl --install-completion zsh

# Fish
dtctl --install-completion fish
```

### Package Managers

- **PyPI**: `pip install dtctl`
- **pipx**: `pipx install dtctl` (isolated install)
- **Docker**: Container image for CI/CD usage

---

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=dtctl

# Type checking
mypy src/dtctl
```

---

## Security Considerations

### Token Storage
- Tokens stored in config file with restricted permissions
- Support for environment variable overrides
- Consider keyring integration for future versions

### TLS Configuration
- httpx uses system CA certificates by default
- Support for custom CA certificates if needed

### Input Validation
- Pydantic validates all configuration
- Resource IDs validated before API calls

---

## Summary

This architecture provides:

✅ **Pythonic**: Leverages modern Python features and ecosystem
✅ **Maintainable**: Clear project structure with separation of concerns
✅ **Type-safe**: Full type hints with Pydantic validation
✅ **Cross-platform**: Works on Linux, macOS, Windows
✅ **Extensible**: Easy to add new resources and commands
✅ **User-friendly**: Rich output formatting and helpful errors
✅ **AI-ready**: Plain mode and structured output for automation
