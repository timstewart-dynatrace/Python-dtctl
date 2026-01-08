# dtctl - Dynatrace CLI

A kubectl-inspired CLI for managing Dynatrace platform resources.

## Features

- **Multi-context configuration** - Manage multiple Dynatrace environments
- **Resource management** - CRUD operations for workflows, dashboards, SLOs, and more
- **DQL queries** - Execute Dynatrace Query Language queries
- **Template support** - Use variables in manifests and queries
- **Multiple output formats** - Table, JSON, YAML, CSV
- **AI-friendly** - Plain mode for automation and AI agents

## Installation

```bash
# From source
pip install -e .

# Or with dev dependencies
pip install -e ".[dev]"
```

## Quick Start

### Configure a context

```bash
# Set up credentials
dtctl config set-credentials prod-token --token dt0s16.XXXXXX

# Create a context
dtctl config set-context prod \
  --environment https://abc12345.apps.dynatrace.com \
  --token-ref prod-token

# Switch to the context
dtctl config use-context prod
```

### List resources

```bash
# List workflows
dtctl get workflows

# List dashboards
dtctl get dashboards --name "my-dashboard"

# List SLOs
dtctl get slos --enabled
```

### Get detailed information

```bash
# Describe a workflow
dtctl describe workflow my-workflow

# Describe an execution
dtctl describe execution <execution-id>
```

### Create resources

```bash
# Create a workflow from a manifest
dtctl create workflow -f workflow.yaml

# Create with template variables
dtctl create workflow -f workflow.yaml --set environment=prod
```

### Apply resources (create or update)

```bash
# Apply a workflow
dtctl apply -f workflow.yaml

# Dry run
dtctl apply -f workflow.yaml --dry-run
```

### Execute workflows

```bash
# Execute a workflow
dtctl exec workflow my-workflow

# Execute with parameters and wait
dtctl exec workflow my-workflow --param key=value --wait
```

### Run DQL queries

```bash
# Inline query
dtctl query "fetch logs | limit 10"

# Query from file
dtctl query -f query.dql

# Query with variables
dtctl query "fetch logs | filter host == '{{ host }}'" --set host=my-host
```

### Edit resources

```bash
# Edit in your default editor
dtctl edit workflow my-workflow

# Edit as JSON
dtctl edit dashboard my-dashboard --format json
```

### Delete resources

```bash
# Delete with confirmation
dtctl delete workflow my-workflow

# Force delete (no confirmation)
dtctl delete workflow my-workflow --force
```

### Share documents

```bash
# Share a dashboard
dtctl share dashboard my-dashboard --user user@example.com

# Share with write access
dtctl share notebook my-notebook --group group-uuid --access read-write
```

## Commands

| Command | Description |
|---------|-------------|
| `config` | Manage configuration contexts and credentials |
| `get` | List or get resources |
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
- **Notifications** (`notifications`)
- **Analyzers** (`analyzers`)
- **CoPilot Skills** (`copilot-skills`)
- **EdgeConnect** (`edgeconnects`, `ec`)
- **OpenPipeline** (`openpipelines`, `op`)

## Global Options

```
--context, -c     Override the current context
--output, -o      Output format (table, wide, json, yaml, csv)
--verbose, -v     Enable verbose output
--plain           Plain mode (no colors, no prompts)
--dry-run         Preview changes without applying
--version, -V     Show version
```

## Configuration

Configuration is stored in `~/.config/dtctl/config` (XDG compliant).

Example configuration:

```yaml
apiVersion: v1
kind: Config
current-context: prod
contexts:
  - name: prod
    context:
      environment: https://abc12345.apps.dynatrace.com
      token-ref: prod-token
  - name: dev
    context:
      environment: https://dev12345.apps.dynatrace.com
      token-ref: dev-token
tokens:
  - name: prod-token
    token: dt0s16.XXXXXX
  - name: dev-token
    token: dt0s16.YYYYYY
preferences:
  output: table
  editor: vim
```

## Environment Variables

- `DTCTL_CONTEXT` - Override current context
- `DTCTL_OUTPUT` - Override output format
- `DTCTL_VERBOSE` - Enable verbose mode
- `EDITOR` - Editor for edit commands

## Template Variables

Use Jinja2-style templates in manifests and queries:

```yaml
# workflow.yaml
title: "{{ workflow_name }}"
description: "Workflow for {{ environment }}"
```

```bash
dtctl apply -f workflow.yaml --set workflow_name="My Workflow" --set environment=prod
```

## License

MIT
