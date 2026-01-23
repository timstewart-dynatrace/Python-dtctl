# API Token Scopes

> **⚠️ DISCLAIMER**: This tool is provided "as-is" without warranty and is **not produced, endorsed, or supported by Dynatrace**. It is an independent, community-driven project. **Use at your own risk.** The authors assume no liability for any issues arising from its use. Always test in non-production environments first. For official Dynatrace tools and support, please visit [dynatrace.com](https://www.dynatrace.com).

This document lists the API token scopes required for dtctl operations.

## Token Types

dtctl supports two authentication methods:

1. **Platform Tokens** (Bearer tokens) - Most common, created in Dynatrace UI
2. **OAuth2 Client Credentials** - For service-to-service automation

## Required Scopes by Feature

### Core Operations

| Feature | Scopes Required |
|---------|-----------------|
| Get/List Workflows | `automation:workflows:read` |
| Create/Update Workflows | `automation:workflows:write` |
| Execute Workflows | `automation:workflows:run` |
| Get/List Dashboards | `document:documents:read` |
| Create/Update Dashboards | `document:documents:write` |
| Delete Dashboards | `document:documents:delete` |
| Get/List Notebooks | `document:documents:read` |
| Create/Update Notebooks | `document:documents:write` |
| Delete Notebooks | `document:documents:delete` |

### DQL Queries

| Feature | Scopes Required |
|---------|-----------------|
| Query Logs | `storage:logs:read` |
| Query Events | `storage:events:read` |
| Query Metrics | `storage:metrics:read` |
| Query Entities | `storage:entities:read` |
| Query Spans | `storage:spans:read` |

### Settings

| Feature | Scopes Required |
|---------|-----------------|
| Get Settings Schemas | `settings:schemas:read` |
| Get Settings Objects | `settings:objects:read` |
| Create/Update Settings | `settings:objects:write` |

### Buckets & Storage

| Feature | Scopes Required |
|---------|-----------------|
| Get/List Buckets | `storage:buckets:read` |
| Create/Delete Buckets | `storage:buckets:write` |
| Get Lookup Tables | `storage:lookup-tables:read` |
| Create Lookup Tables | `storage:lookup-tables:write` |

### IAM (Identity & Access Management)

| Feature | Scopes Required |
|---------|-----------------|
| List Users | `iam:users:read` |
| List Groups | `iam:groups:read` |
| List Policies | `iam:policies:read` |
| List Bindings | `iam:bindings:read` |
| Get Effective Permissions | `iam:effective-permissions:read` |

### Additional Resources

| Feature | Scopes Required |
|---------|-----------------|
| Apps | `app-engine:apps:read` |
| SLOs | `slo:slos:read`, `slo:slos:write` |
| OpenPipeline | `openpipeline:configurations:read` |
| EdgeConnect | `edgeconnect:configurations:read` |
| Analyzers | `davis:analyzers:execute` |
| CoPilot | `davis:copilot:execute` |
| Account Limits | `account-consumption:limits:read` |
| Environments | `account:environments:read` |

## Recommended Token Scopes

### Read-Only Access

For users who only need to view resources:

```
automation:workflows:read
document:documents:read
settings:objects:read
settings:schemas:read
storage:buckets:read
storage:logs:read
storage:events:read
storage:metrics:read
iam:users:read
iam:groups:read
```

### Full Access

For users who need complete control:

```
automation:workflows:read
automation:workflows:write
automation:workflows:run
document:documents:read
document:documents:write
document:documents:delete
settings:objects:read
settings:objects:write
settings:schemas:read
storage:buckets:read
storage:buckets:write
storage:logs:read
storage:events:read
storage:metrics:read
storage:lookup-tables:read
storage:lookup-tables:write
iam:users:read
iam:groups:read
iam:policies:read
iam:bindings:read
app-engine:apps:read
slo:slos:read
slo:slos:write
openpipeline:configurations:read
account-consumption:limits:read
```

## Creating a Token

1. Go to your Dynatrace environment
2. Navigate to **Settings** > **Access tokens**
3. Click **Generate new token**
4. Enter a name for the token
5. Select the required scopes
6. Click **Generate token**
7. Copy the token immediately (it won't be shown again)

## Using the Token

```bash
# Store the token
dtctl config set-credentials my-token --token "dt0s16.XXXXXX"

# Create a context using the token
dtctl config set-context my-env \
  --environment "https://abc12345.apps.dynatrace.com" \
  --token-ref my-token

# Test authentication
dtctl auth test
```

## Security Best Practices

1. **Principle of Least Privilege** - Only grant scopes that are actually needed
2. **Separate Tokens** - Use different tokens for different environments
3. **Token Rotation** - Regularly rotate tokens
4. **Never Commit Tokens** - Keep tokens out of version control
5. **Use Environment Variables** - For CI/CD, use `DTCTL_CONTEXT` and secure secrets management

## OAuth2 Setup (Optional)

For service-to-service authentication:

1. Go to **Account Management** > **Identity & access management** > **OAuth clients**
2. Create a new OAuth client
3. Note the client ID and secret
4. Configure in dtctl:

```yaml
contexts:
  - name: automated
    context:
      environment: https://abc12345.apps.dynatrace.com
      oauth-client-id: dt0s02.XXXXX
      oauth-client-secret: dt0s02.XXXXX.YYYYY
      oauth-resource-urn: urn:dtenvironment:abc12345
```
