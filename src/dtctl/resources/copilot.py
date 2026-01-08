"""CoPilot resource handler.

Manages Davis CoPilot interactions and skills.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from dtctl.client import Client
from dtctl.resources.base import ResourceHandler


class CoPilotSkill(BaseModel):
    """CoPilot skill model."""

    name: str = ""
    description: str = ""
    enabled: bool = True

    model_config = {"populate_by_name": True}


class CoPilotHandler(ResourceHandler[CoPilotSkill]):
    """Handler for CoPilot operations."""

    @property
    def resource_name(self) -> str:
        return "copilot"

    @property
    def api_path(self) -> str:
        return "/platform/davis/copilot/v1"

    def list_skills(self, **params: Any) -> list[dict[str, Any]]:
        """List CoPilot skills.

        Returns:
            List of skill dictionaries
        """
        response = self.client.get(f"{self.api_path}/skills", params=params)
        data = response.json()
        return data.get("skills", [])

    def get_skill(self, skill_name: str) -> dict[str, Any]:
        """Get a skill by name.

        Args:
            skill_name: Skill name

        Returns:
            Skill dictionary
        """
        response = self.client.get(f"{self.api_path}/skills/{skill_name}")
        return response.json()

    def chat(
        self,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Send a chat message to CoPilot.

        Args:
            message: User message
            context: Optional context for the conversation

        Returns:
            CoPilot response
        """
        data: dict[str, Any] = {"message": message}
        if context:
            data["context"] = context

        response = self.client.post(f"{self.api_path}/chat", json=data)
        return response.json()

    def nl2dql(self, question: str) -> dict[str, Any]:
        """Convert natural language to DQL.

        Args:
            question: Natural language question

        Returns:
            Generated DQL query
        """
        response = self.client.post(
            f"{self.api_path}/nl2dql",
            json={"question": question},
        )
        return response.json()
