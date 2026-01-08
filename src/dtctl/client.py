"""HTTP client for Dynatrace API interactions.

Provides a robust HTTP client with:
- Automatic retry with exponential backoff
- Rate limit handling (429)
- Bearer token authentication
- Configurable timeout
- Debug/verbose logging
"""

from __future__ import annotations

import logging
import time
from typing import Any
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel

from dtctl.config import Config, load_config

logger = logging.getLogger(__name__)


class APIError(Exception):
    """Exception raised for API errors."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


class RetryConfig(BaseModel):
    """Configuration for retry behavior."""

    max_retries: int = 3
    retry_statuses: list[int] = [429, 500, 502, 503, 504]
    initial_delay: float = 1.0
    max_delay: float = 10.0
    exponential_base: float = 2.0


class Client:
    """HTTP client for Dynatrace API with retry and auth handling."""

    def __init__(
        self,
        base_url: str,
        token: str,
        timeout: float = 30.0,
        retry_config: RetryConfig | None = None,
        verbose: bool = False,
    ):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.retry_config = retry_config or RetryConfig()
        self.verbose = verbose

        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "User-Agent": "dtctl/0.1.0",
            },
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def _should_retry(self, status_code: int) -> bool:
        """Check if request should be retried based on status code."""
        return status_code in self.retry_config.retry_statuses

    def _get_retry_delay(self, attempt: int, response: httpx.Response | None = None) -> float:
        """Calculate delay before next retry attempt."""
        # Check for Retry-After header (rate limiting)
        if response is not None and "Retry-After" in response.headers:
            try:
                return float(response.headers["Retry-After"])
            except ValueError:
                pass

        # Exponential backoff
        delay = self.retry_config.initial_delay * (
            self.retry_config.exponential_base**attempt
        )
        return min(delay, self.retry_config.max_delay)

    def _log_request(self, method: str, url: str, **kwargs: Any) -> None:
        """Log request details in verbose mode."""
        if self.verbose:
            logger.debug(f"Request: {method} {url}")
            if "json" in kwargs:
                logger.debug(f"Body: {kwargs['json']}")

    def _log_response(self, response: httpx.Response) -> None:
        """Log response details in verbose mode."""
        if self.verbose:
            logger.debug(f"Response: {response.status_code}")
            logger.debug(f"Body: {response.text[:500]}...")

    def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an HTTP request with retry logic.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: API path (will be joined with base_url)
            **kwargs: Additional arguments passed to httpx

        Returns:
            httpx.Response object

        Raises:
            APIError: If request fails after all retries
        """
        url = path if path.startswith("http") else path

        self._log_request(method, url, **kwargs)

        last_exception: Exception | None = None
        last_response: httpx.Response | None = None

        for attempt in range(self.retry_config.max_retries + 1):
            try:
                response = self._client.request(method, url, **kwargs)
                self._log_response(response)

                if response.is_success:
                    return response

                if not self._should_retry(response.status_code):
                    raise APIError(
                        f"Request failed: {response.status_code} {response.reason_phrase}",
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                last_response = response

            except httpx.RequestError as e:
                last_exception = e
                if attempt == self.retry_config.max_retries:
                    raise APIError(f"Request failed: {e}") from e

            # Calculate retry delay
            if attempt < self.retry_config.max_retries:
                delay = self._get_retry_delay(attempt, last_response)
                if self.verbose:
                    logger.debug(f"Retrying in {delay:.1f}s (attempt {attempt + 1})")
                time.sleep(delay)

        # All retries exhausted
        if last_response is not None:
            raise APIError(
                f"Request failed after {self.retry_config.max_retries} retries: "
                f"{last_response.status_code}",
                status_code=last_response.status_code,
                response_body=last_response.text,
            )

        raise APIError(
            f"Request failed after {self.retry_config.max_retries} retries: {last_exception}"
        )

    def get(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make a GET request."""
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make a POST request."""
        return self.request("POST", path, **kwargs)

    def put(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make a PUT request."""
        return self.request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make a PATCH request."""
        return self.request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs: Any) -> httpx.Response:
        """Make a DELETE request."""
        return self.request("DELETE", path, **kwargs)


def create_client_from_config(
    config: Config | None = None,
    context_name: str | None = None,
    verbose: bool = False,
) -> Client:
    """Create a client from configuration.

    Args:
        config: Configuration object (loads from file if not provided)
        context_name: Override context name (uses current-context if not provided)
        verbose: Enable verbose logging

    Returns:
        Configured Client instance

    Raises:
        RuntimeError: If no context or token is configured
    """
    if config is None:
        config = load_config()

    # Determine which context to use
    ctx_name = context_name or config.current_context
    if not ctx_name:
        raise RuntimeError(
            "No context configured. Use 'dtctl config set-context' to create one."
        )

    context = config.get_context(ctx_name)
    if not context:
        raise RuntimeError(f"Context '{ctx_name}' not found in configuration.")

    token = config.get_token(context.token_ref)
    if not token:
        raise RuntimeError(
            f"Token '{context.token_ref}' not found. "
            "Use 'dtctl config set-credentials' to add it."
        )

    return Client(
        base_url=context.environment,
        token=token,
        verbose=verbose,
    )
