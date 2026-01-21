"""Document resource handler.

Manages Dynatrace documents (dashboards and notebooks) including
CRUD operations and sharing.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from dtctl.client import Client, APIError
from dtctl.resources.base import ResourceHandler


DocumentType = Literal["dashboard", "notebook"]


class Document(BaseModel):
    """Document resource model."""

    id: str = ""
    name: str = ""
    type: DocumentType = "dashboard"
    description: str = ""
    owner: str = ""
    is_private: bool = Field(default=True, alias="isPrivate")
    version: int = 1
    created: datetime | None = None
    modified: datetime | None = None

    model_config = {"populate_by_name": True}


class DocumentHandler(ResourceHandler[Document]):
    """Handler for document operations (dashboards and notebooks)."""

    def __init__(self, client: Client, doc_type: DocumentType | None = None):
        super().__init__(client)
        self.doc_type = doc_type

    @property
    def resource_name(self) -> str:
        return self.doc_type or "document"

    @property
    def api_path(self) -> str:
        return "/platform/document/v1/documents"

    def list(
        self,
        doc_type: DocumentType | None = None,
        name_filter: str | None = None,
        owner: str | None = None,
        **params: Any,
    ) -> list[dict[str, Any]]:
        """List documents with optional filtering.

        Args:
            doc_type: Filter by type (dashboard or notebook)
            name_filter: Filter by name (partial match)
            owner: Filter by owner
            **params: Additional query parameters

        Returns:
            List of document dictionaries
        """
        query_params: dict[str, Any] = {}

        # Build filter expression
        filters = []
        effective_type = doc_type or self.doc_type
        if effective_type:
            filters.append(f"type=='{effective_type}'")
        if name_filter:
            filters.append(f"name contains '{name_filter}'")
        if owner:
            filters.append(f"owner=='{owner}'")

        if filters:
            query_params["filter"] = " and ".join(filters)

        query_params.update(params)

        response = self.client.get(self.api_path, params=query_params)
        data = response.json()
        return data.get("documents", [])

    def get(self, document_id: str, metadata_only: bool = False) -> dict[str, Any]:
        """Get a document by ID.

        Args:
            document_id: Document ID
            metadata_only: If True, only return metadata (not content)

        Returns:
            Document dictionary
        """
        params = {"metadata-only": str(metadata_only).lower()} if metadata_only else {}
        response = self.client.get(f"{self.api_path}/{document_id}", params=params)
        return response.json()

    def get_content(self, document_id: str) -> dict[str, Any]:
        """Get document content.

        Args:
            document_id: Document ID

        Returns:
            Document content
        """
        doc = self.get(document_id, metadata_only=False)
        return doc

    def create(
        self,
        name: str,
        doc_type: DocumentType,
        content: dict[str, Any],
        description: str = "",
        is_private: bool = True,
    ) -> dict[str, Any]:
        """Create a new document.

        Args:
            name: Document name
            doc_type: Document type (dashboard or notebook)
            content: Document content
            description: Optional description
            is_private: Whether document is private

        Returns:
            Created document
        """
        import json

        # Documents API uses multipart form data
        files = {
            "file": (
                f"{name}.json",
                json.dumps(content),
                "application/json",
            ),
        }
        data = {
            "name": name,
            "type": doc_type,
            "isPrivate": str(is_private).lower(),
        }
        if description:
            data["description"] = description

        # Need to use a custom request for multipart
        response = self.client._client.post(
            self.api_path,
            data=data,
            files=files,
        )

        if response.is_error:
            raise APIError(
                f"Failed to create document: {response.status_code}",
                status_code=response.status_code,
                response_body=response.text,
            )

        return response.json()

    def update(
        self,
        document_id: str,
        content: dict[str, Any],
        name: str | None = None,
        optimistic_locking_version: int | None = None,
    ) -> dict[str, Any]:
        """Update a document.

        Args:
            document_id: Document ID
            content: Updated content
            name: Optional new name
            optimistic_locking_version: Version for optimistic locking

        Returns:
            Updated document
        """
        import json

        files = {
            "file": (
                "document.json",
                json.dumps(content),
                "application/json",
            ),
        }
        data: dict[str, str] = {}
        if name:
            data["name"] = name
        if optimistic_locking_version is not None:
            data["optimistic-locking-version"] = str(optimistic_locking_version)

        response = self.client._client.put(
            f"{self.api_path}/{document_id}",
            data=data if data else None,
            files=files,
        )

        if response.is_error:
            raise APIError(
                f"Failed to update document: {response.status_code}",
                status_code=response.status_code,
                response_body=response.text,
            )

        return response.json()

    def delete(self, document_id: str) -> bool:
        """Delete a document.

        Args:
            document_id: Document ID

        Returns:
            True if deleted successfully
        """
        try:
            self.client.delete(f"{self.api_path}/{document_id}")
            return True
        except APIError:
            return False

    def share(
        self,
        document_id: str,
        user_id: str | None = None,
        group_id: str | None = None,
        access: Literal["read", "read-write"] = "read",
    ) -> bool:
        """Share a document with a user or group.

        Args:
            document_id: Document ID
            user_id: User SSO ID
            group_id: Group UUID
            access: Access level

        Returns:
            True if shared successfully
        """
        if not user_id and not group_id:
            raise ValueError("Either user_id or group_id must be provided")

        data: dict[str, Any] = {"access": access}
        if user_id:
            data["user"] = user_id
        if group_id:
            data["group"] = group_id

        try:
            self.client.post(
                f"{self.api_path}/{document_id}/shares",
                json=data,
            )
            return True
        except APIError:
            return False

    def unshare(
        self,
        document_id: str,
        user_id: str | None = None,
        group_id: str | None = None,
    ) -> bool:
        """Remove sharing from a document.

        Args:
            document_id: Document ID
            user_id: User SSO ID
            group_id: Group UUID

        Returns:
            True if unshared successfully
        """
        if not user_id and not group_id:
            raise ValueError("Either user_id or group_id must be provided")

        params: dict[str, str] = {}
        if user_id:
            params["user"] = user_id
        if group_id:
            params["group"] = group_id

        try:
            self.client.delete(
                f"{self.api_path}/{document_id}/shares",
                params=params,
            )
            return True
        except APIError:
            return False

    def list_shares(self, document_id: str) -> list[dict[str, Any]]:
        """List shares for a document.

        Args:
            document_id: Document ID

        Returns:
            List of share entries
        """
        response = self.client.get(f"{self.api_path}/{document_id}/shares")
        data = response.json()
        return data.get("shares", [])

    def transfer_owner(
        self,
        document_id: str,
        new_owner_id: str,
        admin_access: bool = False,
    ) -> bool:
        """Transfer ownership of a document to another user.

        Args:
            document_id: Document ID
            new_owner_id: User ID of the new owner
            admin_access: Use admin access to transfer (requires document:documents:admin scope)

        Returns:
            True if ownership transferred successfully

        Note:
            The previous owner loses access to the document after transfer.
            This operation can only be performed by the document owner
            (or with admin_access=True if you have the admin scope).
        """
        params = {"admin-access": "true"} if admin_access else {}
        try:
            self.client.post(
                f"{self.api_path}/{document_id}:transfer-owner",
                json={"newOwnerId": new_owner_id},
                params=params,
            )
            return True
        except APIError:
            return False


def create_dashboard_handler(client: Client) -> DocumentHandler:
    """Create a handler specifically for dashboards."""
    return DocumentHandler(client, doc_type="dashboard")


def create_notebook_handler(client: Client) -> DocumentHandler:
    """Create a handler specifically for notebooks."""
    return DocumentHandler(client, doc_type="notebook")
