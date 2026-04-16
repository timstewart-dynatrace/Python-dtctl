"""Configuration management for dtctl.

Handles multi-context configuration, token storage, and XDG Base Directory compliance.
Configuration is stored in YAML format at ~/.config/dtctl/config (or XDG_CONFIG_HOME).
"""

from __future__ import annotations

import os
from pathlib import Path

import yaml
from platformdirs import user_config_dir
from pydantic import BaseModel, Field


class Context(BaseModel):
    """A named context containing environment URL and token reference.

    Supports both bearer token authentication (default) and optional OAuth2.
    For OAuth2, set oauth_client_id and oauth_client_secret instead of token_ref.
    """

    environment: str = Field(description="Dynatrace environment URL")
    token_ref: str = Field(default="", alias="token-ref", description="Reference to a named token")
    # Optional OAuth2 fields (alternative to token_ref)
    oauth_client_id: str = Field(
        default="", alias="oauth-client-id", description="OAuth2 client ID"
    )
    oauth_client_secret: str = Field(
        default="", alias="oauth-client-secret", description="OAuth2 client secret"
    )
    oauth_resource_urn: str = Field(
        default="", alias="oauth-resource-urn", description="OAuth2 resource URN"
    )

    model_config = {"populate_by_name": True}

    @property
    def uses_oauth(self) -> bool:
        """Check if this context uses OAuth2 authentication."""
        return bool(self.oauth_client_id and self.oauth_client_secret)


class NamedContext(BaseModel):
    """A context with its name."""

    name: str
    context: Context


class NamedToken(BaseModel):
    """A named token entry."""

    name: str
    token: str


class Preferences(BaseModel):
    """User preferences for output and editor."""

    output: str = Field(default="table", description="Default output format")
    editor: str = Field(default="vim", description="Default editor for edit commands")


class Config(BaseModel):
    """Root configuration structure matching kubectl-style config."""

    api_version: str = Field(default="v1", alias="apiVersion")
    kind: str = Field(default="Config")
    current_context: str = Field(default="", alias="current-context")
    contexts: list[NamedContext] = Field(default_factory=list)
    tokens: list[NamedToken] = Field(default_factory=list)
    preferences: Preferences = Field(default_factory=Preferences)

    model_config = {"populate_by_name": True}

    def get_context(self, name: str) -> Context | None:
        """Get a context by name."""
        for ctx in self.contexts:
            if ctx.name == name:
                return ctx.context
        return None

    def get_current_context(self) -> Context | None:
        """Get the currently active context."""
        if not self.current_context:
            return None
        return self.get_context(self.current_context)

    def get_token(self, name: str) -> str | None:
        """Get a token by name."""
        for t in self.tokens:
            if t.name == name:
                return t.token
        return None

    def get_current_token(self) -> str | None:
        """Get the token for the current context."""
        ctx = self.get_current_context()
        if not ctx:
            return None
        return self.get_token(ctx.token_ref)

    def set_context(
        self,
        name: str,
        environment: str | None = None,
        token_ref: str | None = None,
        oauth_client_id: str | None = None,
        oauth_client_secret: str | None = None,
        oauth_resource_urn: str | None = None,
    ) -> None:
        """Create or update a context.

        Args:
            name: Context name
            environment: Dynatrace environment URL
            token_ref: Reference to a named token (for bearer auth)
            oauth_client_id: OAuth2 client ID (optional, alternative to token_ref)
            oauth_client_secret: OAuth2 client secret (optional)
            oauth_resource_urn: OAuth2 resource URN (optional)
        """
        existing = None
        for i, ctx in enumerate(self.contexts):
            if ctx.name == name:
                existing = i
                break

        if existing is not None:
            ctx = self.contexts[existing].context
            if environment:
                ctx.environment = environment
            if token_ref:
                ctx.token_ref = token_ref
            if oauth_client_id:
                ctx.oauth_client_id = oauth_client_id
            if oauth_client_secret:
                ctx.oauth_client_secret = oauth_client_secret
            if oauth_resource_urn:
                ctx.oauth_resource_urn = oauth_resource_urn
        else:
            if not environment:
                raise ValueError("New context requires environment")
            # Either token_ref OR oauth credentials required
            if not token_ref and not (oauth_client_id and oauth_client_secret):
                raise ValueError(
                    "New context requires either token-ref or OAuth2 credentials "
                    "(oauth-client-id and oauth-client-secret)"
                )
            context_data: dict[str, str] = {"environment": environment}
            if token_ref:
                context_data["token-ref"] = token_ref
            if oauth_client_id:
                context_data["oauth-client-id"] = oauth_client_id
            if oauth_client_secret:
                context_data["oauth-client-secret"] = oauth_client_secret
            if oauth_resource_urn:
                context_data["oauth-resource-urn"] = oauth_resource_urn
            self.contexts.append(
                NamedContext(
                    name=name,
                    context=Context(**context_data),
                )
            )

    def set_token(self, name: str, token: str) -> None:
        """Create or update a token."""
        for t in self.tokens:
            if t.name == name:
                t.token = token
                return
        self.tokens.append(NamedToken(name=name, token=token))

    def delete_context(self, name: str) -> bool:
        """Delete a context by name. Returns True if deleted."""
        for i, ctx in enumerate(self.contexts):
            if ctx.name == name:
                self.contexts.pop(i)
                if self.current_context == name:
                    self.current_context = ""
                return True
        return False

    def delete_token(self, name: str) -> bool:
        """Delete a token by name. Returns True if deleted."""
        for i, t in enumerate(self.tokens):
            if t.name == name:
                self.tokens.pop(i)
                return True
        return False


def get_config_dir() -> Path:
    """Get the configuration directory path (XDG compliant)."""
    return Path(user_config_dir("dtctl", appauthor=False))


def get_config_path() -> Path:
    """Get the configuration file path."""
    return get_config_dir() / "config"


def get_legacy_config_path() -> Path:
    """Get the legacy configuration path (~/.dtctl/config)."""
    return Path.home() / ".dtctl" / "config"


def migrate_legacy_config() -> bool:
    """Migrate legacy config to XDG location if needed. Returns True if migrated."""
    legacy_path = get_legacy_config_path()
    new_path = get_config_path()

    if legacy_path.exists() and not new_path.exists():
        new_path.parent.mkdir(parents=True, exist_ok=True)
        new_path.write_text(legacy_path.read_text())
        return True
    return False


def load_config() -> Config:
    """Load configuration from file, creating default if not exists."""
    migrate_legacy_config()

    config_path = get_config_path()

    if not config_path.exists():
        return Config()

    try:
        data = yaml.safe_load(config_path.read_text())
        if data is None:
            return Config()
        return Config.model_validate(data)
    except Exception as e:
        raise RuntimeError(f"Failed to load config from {config_path}: {e}") from e


def save_config(config: Config) -> None:
    """Save configuration to file."""
    config_path = get_config_path()
    config_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert to dict with proper aliases for YAML output
    data = config.model_dump(by_alias=True, exclude_none=True)

    config_path.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False))


def get_env_override(key: str) -> str | None:
    """Get environment variable override for a config key."""
    env_map = {
        "context": "DTCTL_CONTEXT",
        "output": "DTCTL_OUTPUT",
        "verbose": "DTCTL_VERBOSE",
    }
    env_var = env_map.get(key)
    if env_var:
        return os.environ.get(env_var)
    return None
