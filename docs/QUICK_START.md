# dtctl Quick Start Guide

This guide provides practical examples for using dtctl to manage your Dynatrace environment.

> **Note**: This guide assumes dtctl is already installed. If you need to install dtctl, see [INSTALLATION.md](INSTALLATION.md) first.

## Table of Contents

1. [Configuration](#configuration)
2. [Workflows](#workflows)
3. [Dashboards & Notebooks](#dashboards--notebooks)
4. [DQL Queries](#dql-queries)
5. [Service Level Objectives (SLOs)](#service-level-objectives-slos)
6. [Settings](#settings)
7. [Davis AI](#davis-ai)
8. [Output Formats](#output-formats)
9. [Tips & Tricks](#tips--tricks)

---

## Configuration

### Initial Setup

Set up your first Dynatrace environment:

```bash
# Create a context with your environment details
dtctl config set-context my-env \
  --environment "https://abc12345.apps.dynatrace.com" \
  --token-ref my-token

# Store your platform token securely
dtctl config set-credentials my-token \
  --token "dt0s16.XXXXXXXXXXXXXXXXXXXXXXXX"

# Verify your configuration
dtctl config view
```

**Creating a Platform Token:**

To create a platform token in Dynatrace:
1. Navigate to **Identity & Access Management > Access Tokens**
2. Select **Generate new token** and choose **Platform token**
3. Give it a descriptive name (e.g., "dtctl-token")
4. Add the required scopes based on what you'll manage
5. Copy the token immediately - it's only shown once!

**Required Token Scopes by Resource:**
- **Workflows**: `automation:workflows:read`, `automation:workflows:write`, `automation:workflows:execute`
- **Documents** (dashboards/notebooks): `document:documents:read`, `document:documents:write`
- **DQL Queries**: `storage:logs:read`, `storage:events:read`, `storage:metrics:read`
- **SLOs**: `slo:read`, `slo:write`
- **Settings**: `settings:objects:read`, `settings:objects:write`, `settings:schemas:read`

### Multiple Environments

Manage multiple Dynatrace environments:

```bash
# Set up dev environment
dtctl config set-context dev \
  --environment "https://dev.apps.dynatrace.com" \
  --token-ref dev-token

dtctl config set-credentials dev-token \
  --token "dt0s16.DEV_TOKEN_HERE"

# Set up prod environment
dtctl config set-context prod \
  --environment "https://prod.apps.dynatrace.com" \
  --token-ref prod-token

# List all contexts
dtctl config get-contexts

# Switch between environments
dtctl config use-context dev
dtctl config use-context prod

# Check current context
dtctl config current-context
```

### One-Time Context Override

Use a different context without switching:

```bash
# Execute a command in prod while dev is active
dtctl get workflows --context prod
```

---

## Workflows

### List and View Workflows

```bash
# List all workflows
dtctl get workflows

# List with more details
dtctl get workflows -o wide

# Get a specific workflow by ID
dtctl get workflow workflow-123

# View detailed information
dtctl describe workflow workflow-123

# Describe by name
dtctl describe workflow "My Workflow"

# Output as JSON
dtctl get workflow workflow-123 -o json
```

### Edit Workflows

```bash
# Edit in YAML format (default)
dtctl edit workflow workflow-123

# Edit by name
dtctl edit workflow "My Workflow"

# Edit in JSON format
dtctl edit workflow workflow-123 --format=json
```

### Create Workflows

```bash
# Create from a file
dtctl create workflow -f my-workflow.yaml

# Apply (create or update if exists)
dtctl apply -f my-workflow.yaml
```

**Example workflow file** (`my-workflow.yaml`):

```yaml
title: Daily Health Check
description: Runs a health check every day at 9 AM
trigger:
  schedule:
    rule: "0 9 * * *"
    timezone: "UTC"
tasks:
  check_errors:
    action: dynatrace.automations:run-javascript
    input:
      script: |
        export default async function () {
          console.log("Running health check...");
          return { status: "ok" };
        }
```

### Execute Workflows

```bash
# Execute a workflow
dtctl exec workflow workflow-123

# Execute with parameters
dtctl exec workflow workflow-123 \
  --param environment=production \
  --param severity=high

# Execute and wait for completion
dtctl exec workflow workflow-123 --wait
```

### View Executions

```bash
# List all recent executions
dtctl get executions

# List executions for a specific workflow
dtctl get executions --workflow workflow-123

# Get details of a specific execution
dtctl describe execution exec-456

# View execution logs
dtctl logs exec-456
```

### Delete Workflows

```bash
# Delete by ID
dtctl delete workflow workflow-123

# Delete by name (prompts for confirmation)
dtctl delete workflow "Old Workflow"

# Skip confirmation prompt
dtctl delete workflow "Old Workflow" --force
```

---

## Dashboards & Notebooks

### List and View Documents

```bash
# List all dashboards
dtctl get dashboards

# List all notebooks
dtctl get notebooks

# Filter by name
dtctl get dashboards --name "production"

# Describe by name
dtctl describe dashboard "Production Overview"
```

### Edit Documents

```bash
# Edit a dashboard
dtctl edit dashboard dash-123

# Edit by name
dtctl edit dashboard "Production Overview"

# Edit in JSON format
dtctl edit notebook nb-456 --format=json
```

### Create and Apply Documents

```bash
# Create a new dashboard from file
dtctl create dashboard -f dashboard.yaml

# Apply (create or update)
dtctl apply -f dashboard.yaml
```

### Share Documents

```bash
# Share with a user (read access)
dtctl share dashboard dash-123 --user user@example.com

# Share with write access
dtctl share dashboard dash-123 \
  --user user@example.com \
  --access read-write

# Share with a group
dtctl share notebook nb-456 --group "Platform Team"
```

---

## DQL Queries

### Simple Queries

```bash
# Execute an inline query
dtctl query "fetch logs | limit 10"

# Filter logs by status
dtctl query "fetch logs | filter status='ERROR' | limit 100"

# Summarize data
dtctl query "fetch logs | summarize count(), by: {status}"
```

### File-Based Queries

```bash
# Execute from file
dtctl query -f queries/errors.dql

# Save output to file
dtctl query -f queries/errors.dql -o json > results.json
```

**Example query file** (`queries/errors.dql`):

```dql
fetch logs
| filter status = 'ERROR'
| filter timestamp > now() - 1h
| summarize count(), by: {log.source}
| sort count desc
| limit 10
```

### Template Queries

Use templates with variables for flexible queries:

```bash
# Query with variable substitution
dtctl query -f queries/logs-by-host.dql --set host=my-server

# Override multiple variables
dtctl query -f queries/logs-by-host.dql \
  --set host=my-server \
  --set timerange=24h
```

**Example template** (`queries/logs-by-host.dql`):

```dql
fetch logs
| filter host = "{{ host }}"
| filter timestamp > now() - {{ timerange | default("1h") }}
| limit {{ limit | default(100) }}
```

---

## Service Level Objectives (SLOs)

### List and View SLOs

```bash
# List all SLOs
dtctl get slos

# Get a specific SLO
dtctl get slo slo-123

# Detailed view
dtctl describe slo slo-123
```

### Create and Apply SLOs

```bash
# Create from file
dtctl create slo -f slo-definition.yaml

# Apply (create or update)
dtctl apply -f slo-definition.yaml
```

### Delete SLOs

```bash
dtctl delete slo slo-123
dtctl delete slo slo-123 --force
```

---

## Settings

### List Settings Schemas

```bash
# List all available settings schemas
dtctl get schemas

# View schema details
dtctl describe schema builtin:alerting.profile
```

### List and View Settings

```bash
# List settings for a specific schema
dtctl get settings --schema builtin:alerting.profile

# Get a specific settings object
dtctl get settings object-789
```

### Create and Apply Settings

```bash
# Create settings from file
dtctl create settings \
  -f alerting-profile.yaml \
  --schema builtin:alerting.profile \
  --scope environment

# Apply (create or update)
dtctl apply -f settings.yaml
```

---

## Davis AI

### Davis Analyzers

```bash
# List all available analyzers
dtctl get analyzers

# Get a specific analyzer definition
dtctl get analyzer dt.statistics.GenericForecastAnalyzer

# Execute an analyzer
dtctl exec analyzer dt.statistics.GenericForecastAnalyzer -f input.json

# Execute with inline data
dtctl exec analyzer dt.statistics.GenericForecastAnalyzer \
  --data '{"query": "timeseries avg(dt.host.cpu.usage)"}'
```

### Davis CoPilot

```bash
# List CoPilot skills
dtctl get copilot-skills

# Chat with CoPilot
dtctl exec copilot "What is DQL?"

# Natural language to DQL
dtctl exec nl2dql "show me error logs from the last hour"
```

---

## Output Formats

All `get` and `query` commands support multiple output formats:

```bash
# Table format (default)
dtctl get workflows

# JSON format
dtctl get workflows -o json

# YAML format
dtctl get workflows -o yaml

# Wide format (more columns)
dtctl get workflows -o wide

# CSV format
dtctl get workflows -o csv

# Plain output (no colors, for scripts)
dtctl get workflows --plain
```

---

## Tips & Tricks

### Name Resolution

Use resource names instead of memorizing IDs:

```bash
dtctl describe workflow "My Workflow"
dtctl edit dashboard "Production Overview"
dtctl delete notebook "Old Analysis"
```

### Export and Backup

```bash
# Export all workflows
dtctl get workflows -o yaml > workflows-backup.yaml

# Export all dashboards
dtctl get dashboards -o json > dashboards-backup.json
```

### Dry Run

Preview changes before applying:

```bash
dtctl apply -f workflow.yaml --dry-run
dtctl delete workflow "Test Workflow" --dry-run
```

### Verbose Output

Debug issues with verbose mode:

```bash
dtctl get workflows -v
```

### Environment Variables

```bash
# Set default output format
export DTCTL_OUTPUT=json

# Set default context
export DTCTL_CONTEXT=production
```

### Pipeline Commands

Combine dtctl with standard Unix tools:

```bash
# Count workflows
dtctl get workflows -o json | jq '. | length'

# Filter and format
dtctl query "fetch logs | limit 100" -o json | \
  jq '.records[] | select(.status=="ERROR")'
```

---

## Troubleshooting

### "config file not found"

Run the configuration setup:

```bash
dtctl config set-context my-env \
  --environment "https://YOUR_ENV.apps.dynatrace.com" \
  --token-ref my-token

dtctl config set-credentials my-token --token "dt0s16.YOUR_TOKEN"
```

### API errors

Enable verbose mode to see HTTP details:

```bash
dtctl get workflows -v
```

---

## Next Steps

- **API Reference**: See [API_DESIGN.md](API_DESIGN.md) for complete command reference
- **Architecture**: Read [ARCHITECTURE.md](ARCHITECTURE.md) for implementation details
- **Design Principles**: Check [DESIGN_PRINCIPLES.md](DESIGN_PRINCIPLES.md) for design philosophy
