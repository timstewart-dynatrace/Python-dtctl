# dtctl - Dynatrace CLI

> **⚠️ DISCLAIMER**: This tool is **not produced, endorsed, or supported by Dynatrace**. It is an independent, community-driven project. **Use at your own risk.** The authors assume no liability for any issues arising from its use. Always test in non-production environments first.

A kubectl-inspired CLI for managing Dynatrace platform resources.

## Features

- **Multi-context configuration** - Manage multiple Dynatrace environments
- **Resource management** - CRUD operations for workflows, dashboards, SLOs, and more
- **DQL queries** - Execute Dynatrace Query Language queries
- **Template support** - Use variables in manifests and queries
- **Multiple output formats** - Table, JSON, YAML, CSV
- **AI-friendly** - Plain mode for automation and AI agents
- **Bulk operations** - Apply, delete, or execute multiple resources from files
- **Export capabilities** - Export resources and query results to files
- **Caching** - In-memory cache to reduce API calls
- **OAuth2 support** - Optional OAuth2 authentication for automation (in addition to bearer tokens)

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

### Bulk operations

```bash
# Apply multiple resources from a file
dtctl bulk apply -f resources.yaml

# Create multiple workflows
dtctl bulk create-workflows -f workflows.yaml

# Delete multiple resources
dtctl bulk delete -f ids.csv --type workflow

# Execute multiple workflows
dtctl bulk exec-workflows -f workflows.csv
```

### Export resources

```bash
# Export all resources
dtctl export all -o ./backup

# Export specific resource types
dtctl export all -i workflows,slos

# Export a single workflow
dtctl export workflow my-workflow -o workflow.yaml

# Export query results
dtctl export query-results "fetch logs | limit 100" -o results.csv
```

### Cache management

```bash
# View cache statistics
dtctl cache stats

# Clear all cache
dtctl cache clear

# Clear cache by prefix
dtctl cache clear --prefix workflows
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
| `bulk` | Bulk operations on resources |
| `export` | Export resources to files |
| `cache` | Manage API response cache |

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

## OAuth2 Authentication (Optional)

In addition to bearer tokens, dtctl supports OAuth2 client credentials for automated systems:

```yaml
# Context with OAuth2 (alternative to token-ref)
contexts:
  - name: automated
    context:
      environment: https://abc12345.apps.dynatrace.com
      oauth-client-id: dt0s02.XXXXX
      oauth-client-secret: dt0s02.XXXXX.YYYYY
      oauth-resource-urn: urn:dtenvironment:abc12345
```

OAuth2 features:
- Automatic token refresh before expiry
- Token caching to minimize SSO calls
- Required for some automation scenarios

**Note:** Most users should use bearer tokens (platform tokens). OAuth2 is optional and primarily useful for service-to-service automation.

**Functions NOT available without OAuth2:** None - all dtctl functions work with bearer tokens. OAuth2 is simply an alternative authentication method for automation scenarios where self-refreshing tokens are beneficial.

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

## Disclaimer

This tool is **not produced, endorsed, or supported by Dynatrace**. It is an independent, community-driven project provided "as-is" without warranty of any kind. **Use at your own risk.**

- This is not official Dynatrace software
- No support is provided by Dynatrace
- The authors assume no liability for any issues arising from its use
- Always test thoroughly in non-production environments before use
- Review all operations before executing them against production systems

## License

MIT
