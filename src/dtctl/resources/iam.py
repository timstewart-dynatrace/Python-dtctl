"""IAM (Identity and Access Management) resource handler.

Manages Dynatrace users, groups, policies, bindings, boundaries,
and effective permissions.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from dtctl.resources.base import ResourceHandler


class User(BaseModel):
    """User resource model."""

    uid: str = ""
    email: str = ""
    name: str = ""
    groups: list[str] = Field(default_factory=list)

    model_config = {"populate_by_name": True}


class Group(BaseModel):
    """Group resource model."""

    uuid: str = ""
    name: str = ""
    description: str = ""
    owner: str = ""

    model_config = {"populate_by_name": True}


class Policy(BaseModel):
    """Policy resource model."""

    uuid: str = ""
    name: str = ""
    description: str = ""
    level_type: str = Field(default="", alias="levelType")
    level_id: str = Field(default="", alias="levelId")
    statement_query: str = Field(default="", alias="statementQuery")

    model_config = {"populate_by_name": True}


class Binding(BaseModel):
    """Policy binding resource model."""

    level_type: str = Field(default="", alias="levelType")
    level_id: str = Field(default="", alias="levelId")
    policy_uuid: str = Field(default="", alias="policyUuid")
    group_uuid: str = Field(default="", alias="groupUuid")
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"populate_by_name": True}


class Boundary(BaseModel):
    """Policy boundary resource model."""

    uuid: str = ""
    name: str = ""
    description: str = ""
    bound_query: str = Field(default="", alias="boundQuery")

    model_config = {"populate_by_name": True}


class IAMHandler(ResourceHandler[User]):
    """Handler for IAM operations (users and groups)."""

    @property
    def resource_name(self) -> str:
        return "user"

    @property
    def api_path(self) -> str:
        return "/iam/v1"

    def list_users(self, **params: Any) -> list[dict[str, Any]]:
        """List users with pagination.

        Returns:
            List of user dictionaries
        """
        all_users: list[dict[str, Any]] = []
        next_page_key: str | None = None

        while True:
            if next_page_key:
                request_params = {**params, "nextPageKey": next_page_key}
            else:
                request_params = params

            response = self.client.get(f"{self.api_path}/accounts/users", params=request_params)
            data = response.json()

            items = data.get("items", [])
            all_users.extend(items)

            next_page_key = data.get("nextPageKey")
            if not next_page_key:
                break

        return all_users

    def get_user(self, user_id: str) -> dict[str, Any]:
        """Get a user by ID.

        Args:
            user_id: User ID (uid or email)

        Returns:
            User dictionary
        """
        response = self.client.get(f"{self.api_path}/accounts/users/{user_id}")
        return response.json()

    def list_groups(self, **params: Any) -> list[dict[str, Any]]:
        """List groups with pagination.

        Returns:
            List of group dictionaries
        """
        all_groups: list[dict[str, Any]] = []
        next_page_key: str | None = None

        while True:
            if next_page_key:
                request_params = {**params, "nextPageKey": next_page_key}
            else:
                request_params = params

            response = self.client.get(f"{self.api_path}/accounts/groups", params=request_params)
            data = response.json()

            items = data.get("items", [])
            all_groups.extend(items)

            next_page_key = data.get("nextPageKey")
            if not next_page_key:
                break

        return all_groups

    def get_group(self, group_id: str) -> dict[str, Any]:
        """Get a group by ID.

        Args:
            group_id: Group UUID

        Returns:
            Group dictionary
        """
        response = self.client.get(f"{self.api_path}/accounts/groups/{group_id}")
        return response.json()

    def get_group_members(self, group_id: str) -> list[dict[str, Any]]:
        """Get members of a group with pagination.

        Args:
            group_id: Group UUID

        Returns:
            List of user dictionaries
        """
        all_members: list[dict[str, Any]] = []
        next_page_key: str | None = None

        while True:
            params = {"nextPageKey": next_page_key} if next_page_key else {}
            response = self.client.get(
                f"{self.api_path}/accounts/groups/{group_id}/users", params=params
            )
            data = response.json()

            items = data.get("items", [])
            all_members.extend(items)

            next_page_key = data.get("nextPageKey")
            if not next_page_key:
                break

        return all_members

    # =========================================================================
    # Policy Operations
    # =========================================================================

    def list_policies(
        self,
        level_type: str = "account",
        level_id: str | None = None,
        name: str | None = None,
    ) -> list[dict[str, Any]]:
        """List policies with pagination.

        Args:
            level_type: Policy level type (account, environment)
            level_id: Level ID (required for environment level)
            name: Filter by policy name

        Returns:
            List of policy dictionaries
        """
        params: dict[str, Any] = {}
        if name:
            params["name"] = name

        path = f"{self.api_path}/repo/{level_type}"
        if level_id:
            path = f"{path}/{level_id}"
        path = f"{path}/policies"

        all_policies: list[dict[str, Any]] = []
        next_page_key: str | None = None

        while True:
            if next_page_key:
                request_params = {**params, "nextPageKey": next_page_key}
            else:
                request_params = params

            response = self.client.get(path, params=request_params)
            data = response.json()

            policies = data.get("policies", [])
            all_policies.extend(policies)

            next_page_key = data.get("nextPageKey")
            if not next_page_key:
                break

        return all_policies

    def get_policy(
        self,
        policy_uuid: str,
        level_type: str = "account",
        level_id: str | None = None,
    ) -> dict[str, Any]:
        """Get a policy by UUID.

        Args:
            policy_uuid: Policy UUID
            level_type: Policy level type (account, environment)
            level_id: Level ID (required for environment level)

        Returns:
            Policy dictionary
        """
        path = f"{self.api_path}/repo/{level_type}"
        if level_id:
            path = f"{path}/{level_id}"
        path = f"{path}/policies/{policy_uuid}"

        response = self.client.get(path)
        return response.json()

    # =========================================================================
    # Binding Operations
    # =========================================================================

    def list_bindings(
        self,
        level_type: str = "account",
        level_id: str | None = None,
        group_uuid: str | None = None,
        policy_uuid: str | None = None,
    ) -> list[dict[str, Any]]:
        """List policy bindings with pagination.

        Args:
            level_type: Binding level type (account, environment)
            level_id: Level ID (required for environment level)
            group_uuid: Filter by group UUID
            policy_uuid: Filter by policy UUID

        Returns:
            List of binding dictionaries
        """
        path = f"{self.api_path}/repo/{level_type}"
        if level_id:
            path = f"{path}/{level_id}"
        path = f"{path}/bindings"

        params: dict[str, Any] = {}
        if group_uuid:
            params["groupUuid"] = group_uuid
        if policy_uuid:
            params["policyUuid"] = policy_uuid

        all_bindings: list[dict[str, Any]] = []
        next_page_key: str | None = None

        while True:
            if next_page_key:
                request_params = {**params, "nextPageKey": next_page_key}
            else:
                request_params = params

            response = self.client.get(path, params=request_params)
            data = response.json()

            bindings = data.get("policyBindings", [])
            all_bindings.extend(bindings)

            next_page_key = data.get("nextPageKey")
            if not next_page_key:
                break

        return all_bindings

    def get_binding(
        self,
        policy_uuid: str,
        group_uuid: str,
        level_type: str = "account",
        level_id: str | None = None,
    ) -> dict[str, Any]:
        """Get a specific policy binding.

        Args:
            policy_uuid: Policy UUID
            group_uuid: Group UUID
            level_type: Binding level type (account, environment)
            level_id: Level ID (required for environment level)

        Returns:
            Binding dictionary
        """
        bindings = self.list_bindings(
            level_type=level_type,
            level_id=level_id,
            group_uuid=group_uuid,
            policy_uuid=policy_uuid,
        )
        if bindings:
            return bindings[0]
        raise ValueError(f"Binding not found for policy {policy_uuid} and group {group_uuid}")

    # =========================================================================
    # Boundary Operations
    # =========================================================================

    def list_boundaries(
        self,
        level_type: str = "account",
        level_id: str | None = None,
        name: str | None = None,
    ) -> list[dict[str, Any]]:
        """List policy boundaries with pagination.

        Args:
            level_type: Boundary level type (account, environment)
            level_id: Level ID (required for environment level)
            name: Filter by boundary name

        Returns:
            List of boundary dictionaries
        """
        params: dict[str, Any] = {}
        if name:
            params["name"] = name

        path = f"{self.api_path}/repo/{level_type}"
        if level_id:
            path = f"{path}/{level_id}"
        path = f"{path}/boundaries"

        all_boundaries: list[dict[str, Any]] = []
        next_page_key: str | None = None

        while True:
            if next_page_key:
                request_params = {**params, "nextPageKey": next_page_key}
            else:
                request_params = params

            response = self.client.get(path, params=request_params)
            data = response.json()

            boundaries = data.get("boundaries", [])
            all_boundaries.extend(boundaries)

            next_page_key = data.get("nextPageKey")
            if not next_page_key:
                break

        return all_boundaries

    def get_boundary(
        self,
        boundary_uuid: str,
        level_type: str = "account",
        level_id: str | None = None,
    ) -> dict[str, Any]:
        """Get a boundary by UUID.

        Args:
            boundary_uuid: Boundary UUID
            level_type: Boundary level type (account, environment)
            level_id: Level ID (required for environment level)

        Returns:
            Boundary dictionary
        """
        path = f"{self.api_path}/repo/{level_type}"
        if level_id:
            path = f"{path}/{level_id}"
        path = f"{path}/boundaries/{boundary_uuid}"

        response = self.client.get(path)
        return response.json()

    # =========================================================================
    # Effective Permissions Operations
    # =========================================================================

    def get_effective_permissions_for_user(
        self,
        user_id: str,
        level_type: str = "account",
        level_id: str | None = None,
    ) -> dict[str, Any]:
        """Get effective permissions for a user.

        Calculates the effective permissions by evaluating all policies
        bound to groups the user belongs to.

        Args:
            user_id: User ID (uid or email)
            level_type: Level type (account, environment)
            level_id: Level ID (required for environment level)

        Returns:
            Dictionary with effective permissions
        """
        path = f"{self.api_path}/resolution/{level_type}"
        if level_id:
            path = f"{path}/{level_id}"
        path = f"{path}/effective-permissions/users/{user_id}"

        response = self.client.get(path)
        return response.json()

    def get_effective_permissions_for_group(
        self,
        group_uuid: str,
        level_type: str = "account",
        level_id: str | None = None,
    ) -> dict[str, Any]:
        """Get effective permissions for a group.

        Calculates the effective permissions by evaluating all policies
        bound to the group.

        Args:
            group_uuid: Group UUID
            level_type: Level type (account, environment)
            level_id: Level ID (required for environment level)

        Returns:
            Dictionary with effective permissions
        """
        path = f"{self.api_path}/resolution/{level_type}"
        if level_id:
            path = f"{path}/{level_id}"
        path = f"{path}/effective-permissions/groups/{group_uuid}"

        response = self.client.get(path)
        return response.json()

    def validate_permissions(
        self,
        user_id: str,
        permissions: list[str],
        level_type: str = "account",
        level_id: str | None = None,
    ) -> dict[str, Any]:
        """Validate if a user has specific permissions.

        Args:
            user_id: User ID (uid or email)
            permissions: List of permission strings to validate
            level_type: Level type (account, environment)
            level_id: Level ID (required for environment level)

        Returns:
            Dictionary with validation results
        """
        path = f"{self.api_path}/resolution/{level_type}"
        if level_id:
            path = f"{path}/{level_id}"
        path = f"{path}/validate"

        body = {
            "userId": user_id,
            "permissions": permissions,
        }

        response = self.client.post(path, json=body)
        return response.json()
