"""Workflow resource handler.

Manages Dynatrace Automation workflows including CRUD operations,
execution, and execution logs.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from dtctl.client import Client, APIError
from dtctl.resources.base import CRUDHandler


class Workflow(BaseModel):
    """Workflow resource model."""

    id: str = ""
    title: str = ""
    description: str = ""
    owner: str = ""
    is_deployed: bool = Field(default=False, alias="isDeployed")
    is_private: bool = Field(default=True, alias="isPrivate")
    tasks: dict[str, Any] = Field(default_factory=dict)
    trigger: dict[str, Any] = Field(default_factory=dict)
    schema_version: int = Field(default=3, alias="schemaVersion")

    model_config = {"populate_by_name": True}


class WorkflowExecution(BaseModel):
    """Workflow execution model."""

    id: str = ""
    workflow: str = ""
    title: str = ""
    state: str = ""
    started_at: datetime | None = Field(default=None, alias="startedAt")
    ended_at: datetime | None = Field(default=None, alias="endedAt")
    runtime: str | None = None
    trigger_type: str = Field(default="", alias="triggerType")

    model_config = {"populate_by_name": True}


class TaskExecution(BaseModel):
    """Task execution within a workflow."""

    name: str = ""
    state: str = ""
    started_at: datetime | None = Field(default=None, alias="startedAt")
    ended_at: datetime | None = Field(default=None, alias="endedAt")
    result: Any = None
    log: str = ""


class WorkflowHandler(CRUDHandler[Workflow]):
    """Handler for workflow operations."""

    @property
    def resource_name(self) -> str:
        return "workflow"

    @property
    def api_path(self) -> str:
        return "/platform/automation/v1/workflows"

    @property
    def list_key(self) -> str:
        return "results"

    def list(self, **params: Any) -> list[dict[str, Any]]:
        """List workflows with optional filtering."""
        return super().list(**params)

    def get_raw(self, workflow_id: str) -> dict[str, Any]:
        """Get workflow in raw format suitable for editing."""
        return self.get(workflow_id)

    def deploy(self, workflow_id: str) -> dict[str, Any]:
        """Deploy a workflow (enable trigger).

        Args:
            workflow_id: Workflow ID

        Returns:
            Updated workflow
        """
        workflow = self.get(workflow_id)
        workflow["isDeployed"] = True
        return self.update(workflow_id, workflow)

    def undeploy(self, workflow_id: str) -> dict[str, Any]:
        """Undeploy a workflow (disable trigger).

        Args:
            workflow_id: Workflow ID

        Returns:
            Updated workflow
        """
        workflow = self.get(workflow_id)
        workflow["isDeployed"] = False
        return self.update(workflow_id, workflow)


class ExecutionHandler:
    """Handler for workflow execution operations."""

    def __init__(self, client: Client):
        self.client = client
        self.base_path = "/platform/automation/v1"

    def list_executions(
        self,
        workflow_id: str | None = None,
        state: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """List workflow executions.

        Args:
            workflow_id: Filter by workflow ID
            state: Filter by state (RUNNING, COMPLETED, FAILED, etc.)
            limit: Maximum number of results

        Returns:
            List of execution dictionaries
        """
        params: dict[str, Any] = {"limit": limit}
        if workflow_id:
            params["workflow"] = workflow_id
        if state:
            params["state"] = state

        response = self.client.get(f"{self.base_path}/executions", params=params)
        data = response.json()
        return data.get("results", [])

    def get_execution(self, execution_id: str) -> dict[str, Any]:
        """Get execution details.

        Args:
            execution_id: Execution ID

        Returns:
            Execution dictionary with task details
        """
        response = self.client.get(f"{self.base_path}/executions/{execution_id}")
        return response.json()

    def get_task_executions(self, execution_id: str) -> list[dict[str, Any]]:
        """Get task execution details for an execution.

        Args:
            execution_id: Execution ID

        Returns:
            List of task execution dictionaries
        """
        response = self.client.get(
            f"{self.base_path}/executions/{execution_id}/tasks"
        )
        data = response.json()
        return data.get("results", [])

    def execute(
        self,
        workflow_id: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute a workflow.

        Args:
            workflow_id: Workflow ID to execute
            params: Optional execution parameters

        Returns:
            Execution response with execution ID
        """
        body: dict[str, Any] = {}
        if params:
            body["params"] = params

        response = self.client.post(
            f"{self.base_path}/workflows/{workflow_id}/run",
            json=body if body else None,
        )
        return response.json()

    def wait_for_completion(
        self,
        execution_id: str,
        timeout: int = 300,
        poll_interval: int = 5,
    ) -> dict[str, Any]:
        """Wait for an execution to complete.

        Args:
            execution_id: Execution ID
            timeout: Maximum wait time in seconds
            poll_interval: Polling interval in seconds

        Returns:
            Final execution state
        """
        import time

        start_time = time.time()
        terminal_states = {"SUCCESS", "ERROR", "CANCELLED", "FAILED"}

        while time.time() - start_time < timeout:
            execution = self.get_execution(execution_id)
            state = execution.get("state", "")

            if state in terminal_states:
                return execution

            time.sleep(poll_interval)

        raise TimeoutError(
            f"Execution {execution_id} did not complete within {timeout} seconds"
        )

    def get_logs(self, execution_id: str) -> str:
        """Get execution logs.

        Args:
            execution_id: Execution ID

        Returns:
            Log content as string
        """
        response = self.client.get(f"{self.base_path}/executions/{execution_id}/log")
        return response.text

    def cancel(self, execution_id: str) -> bool:
        """Cancel a running execution.

        Args:
            execution_id: Execution ID

        Returns:
            True if cancelled successfully
        """
        try:
            self.client.post(f"{self.base_path}/executions/{execution_id}/cancel")
            return True
        except APIError:
            return False
