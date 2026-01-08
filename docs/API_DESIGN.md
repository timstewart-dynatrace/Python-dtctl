# dtctl API Design

A kubectl-inspired CLI tool for managing Dynatrace platform resources.

## Design Principles

### kubectl-like User Experience
- **Verb-noun pattern**: `dtctl <verb> <resource> [options]`
- **Consistent flags**: Same flags work across similar operations
- **Multiple output formats**: Table (human), JSON, YAML
- **Declarative configuration**: Apply YAML/JSON files to create/update resources
- **Context management**: Switch between environments easily

### Name Resolution
- Commands accept both resource IDs and names
- Automatic disambiguation when multiple resources match
- Interactive selection for ambiguous names (disabled with `--plain`)

## Command Structure

### Core Verbs

```
get         - List or retrieve resources
describe    - Show detailed information about a resource
create      - Create a resource from file
delete      - Delete resources
edit        - Edit a resource interactively
apply       - Apply configuration from file (create or update)
logs        - Print logs for executions
query       - Execute a DQL query
exec        - Execute a workflow, analyzer, or copilot
```

### Syntax Pattern

```bash
dtctl [verb] [resource-type] [resource-name] [flags]

# Examples:
dtctl get dashboards
dtctl get workflows --name "my-workflow"
dtctl describe dashboard "Production Dashboard"
dtctl delete workflow my-workflow-id
dtctl apply -f workflow.yaml
dtctl query "fetch logs | limit 10"
```

### Global Flags

```
--context string      # Use a specific context
-o, --output string   # Output format: json|yaml|table|wide|csv
--plain               # Plain output for machine processing
-v, --verbose         # Verbose output
--dry-run             # Print what would be done without doing it
```

## Resource Types

### Workflows

```bash
# Resource name: workflow/workflows (short: wf)
dtctl get workflows                              # List all workflows
dtctl get workflow <id>                          # Get specific workflow
dtctl describe workflow <id>                     # Detailed view
dtctl edit workflow <id>                         # Edit in $EDITOR
dtctl delete workflow <id>                       # Delete workflow
dtctl apply -f workflow.yaml                     # Create or update

# Workflow execution
dtctl exec workflow <id>                         # Run workflow
dtctl exec workflow <id> --param key=value       # Run with parameters
dtctl exec workflow <id> --wait                  # Run and wait

# Workflow Executions
dtctl get executions                             # List all executions
dtctl get executions --workflow <workflow-id>    # Filter by workflow
dtctl describe execution <execution-id>          # Execution details
dtctl logs <execution-id>                        # View execution logs
```

### Dashboards & Notebooks

```bash
# Dashboards
dtctl get dashboards                             # List all dashboards
dtctl get dashboard <id>                         # Get specific dashboard
dtctl describe dashboard <id>                    # Detailed view
dtctl edit dashboard <id>                        # Edit in $EDITOR
dtctl delete dashboard <id>                      # Delete dashboard
dtctl create dashboard -f dashboard.yaml         # Create new
dtctl apply -f dashboard.yaml                    # Create or update

# Notebooks (same pattern)
dtctl get notebooks
dtctl describe notebook <id>
dtctl edit notebook <id>

# Sharing
dtctl share dashboard <id> --user <email>        # Share with user
dtctl share dashboard <id> --group <group-id>    # Share with group
```

### SLOs

```bash
dtctl get slos                                   # List all SLOs
dtctl describe slo <id>                          # SLO details
dtctl create slo -f slo-definition.yaml          # Create SLO
dtctl delete slo <id>                            # Delete SLO
dtctl apply -f slo-definition.yaml               # Create or update
```

### Settings

```bash
# Settings Schemas
dtctl get schemas                                # List all schemas
dtctl describe schema <schema-id>                # Schema definition

# Settings Objects
dtctl get settings --schema <schema-id>          # List settings
dtctl get settings <object-id>                   # Get specific
dtctl create settings -f value.yaml --schema <schema-id> --scope environment
dtctl delete settings <object-id>                # Delete
```

### Additional Resources

```bash
# Buckets
dtctl get buckets
dtctl describe bucket <bucket-name>
dtctl create bucket -f bucket-config.yaml
dtctl delete bucket <bucket-name>

# Apps
dtctl get apps
dtctl describe app <app-id>
dtctl delete app <app-id>

# Users & Groups (read-only)
dtctl get users
dtctl get groups
dtctl describe user <user-id>
dtctl describe group <group-id>

# Notifications
dtctl get notifications
dtctl delete notification <id>

# EdgeConnect
dtctl get edgeconnects
dtctl create edgeconnect -f config.yaml
dtctl delete edgeconnect <id>

# OpenPipeline
dtctl get openpipelines
dtctl describe openpipeline <id>
```

### DQL Queries

```bash
# Inline queries
dtctl query "fetch logs | limit 10"
dtctl query "fetch logs | filter status='ERROR' | limit 100"

# File-based queries
dtctl query -f query.dql

# With template variables
dtctl query -f query.dql --set host=my-host --set timerange=2h

# Output formats
dtctl query "fetch logs | limit 10" -o json
dtctl query "fetch logs | limit 10" -o yaml
dtctl query "fetch logs | limit 10" -o table
```

### Davis AI

```bash
# Analyzers
dtctl get analyzers                              # List analyzers
dtctl describe analyzer <name>                   # Analyzer details
dtctl exec analyzer <name> -f input.json         # Execute analyzer

# CoPilot
dtctl get copilot-skills                         # List skills
dtctl exec copilot "What is DQL?"                # Chat
dtctl exec nl2dql "show error logs"              # NL to DQL
```

## Configuration Management

### Configuration File

Location (XDG compliant):
- **Linux**: `~/.config/dtctl/config`
- **macOS**: `~/Library/Application Support/dtctl/config`
- **Windows**: `%LOCALAPPDATA%\dtctl\config`

```yaml
apiVersion: v1
kind: Config
current-context: prod

contexts:
- name: dev
  context:
    environment: https://dev.apps.dynatrace.com
    token-ref: dev-token

- name: prod
  context:
    environment: https://prod.apps.dynatrace.com
    token-ref: prod-token

tokens:
- name: dev-token
  token: dt0s16.***

- name: prod-token
  token: dt0s16.***

preferences:
  output: table
  editor: vim
```

### Config Commands

```bash
dtctl config view                                # View full config
dtctl config get-contexts                        # List contexts
dtctl config current-context                     # Show current
dtctl config use-context prod                    # Switch context
dtctl config set-context dev --environment https://...
dtctl config set-credentials dev-token --token dt0s16.***
dtctl config delete-context dev
```

## Output Formats

### Table (default)
```bash
dtctl get workflows
# ID            TITLE              OWNER
# wf-123        Health Check       me
# wf-456        Alert Handler      team-sre
```

### JSON
```bash
dtctl get workflow wf-123 -o json
```

### YAML
```bash
dtctl get workflow wf-123 -o yaml
```

### Wide
```bash
dtctl get workflows -o wide
# Shows more columns
```

### CSV
```bash
dtctl get workflows -o csv > workflows.csv
```

## Error Handling

### Exit Codes
- `0`: Success
- `1`: General error
- `2`: Usage error (invalid flags/arguments)

### Error Output
```
Error: workflow "my-workflow" not found
  Run 'dtctl get workflows' to list available workflows
```
