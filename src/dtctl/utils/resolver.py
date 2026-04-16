"""Name-to-ID resolver for Dynatrace resources.

Provides heuristic matching to determine if an identifier is a name or ID,
and resolves names to IDs when needed.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from dtctl.client import Client


def is_likely_id(identifier: str) -> bool:
    """Determine if an identifier looks like a UUID/ID rather than a name.

    Heuristics:
    - Matches UUID pattern (8-4-4-4-12 hex format)
    - Matches compact UUID pattern (32 hex chars)
    - Contains only hex characters and dashes in UUID-like structure

    Args:
        identifier: String to analyze

    Returns:
        True if identifier looks like an ID
    """
    # Standard UUID pattern (8-4-4-4-12)
    uuid_pattern = r"^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
    if re.match(uuid_pattern, identifier):
        return True

    # Compact UUID (32 hex characters, no dashes)
    compact_uuid_pattern = r"^[0-9a-fA-F]{32}$"
    if re.match(compact_uuid_pattern, identifier):
        return True

    # Hex string with dashes that looks like an ID (only hex chars and dashes)
    # Must be at least 20 chars and contain ONLY hex chars and dashes
    hex_id_pattern = r"^[0-9a-fA-F-]+$"
    if len(identifier) >= 20 and re.match(hex_id_pattern, identifier):
        return True

    return False


class ResourceResolver:
    """Resolves resource names to IDs."""

    def __init__(self, client: Client):
        self.client = client

    def resolve_workflow(self, identifier: str) -> str:
        """Resolve a workflow name or ID to an ID.

        Args:
            identifier: Workflow name or ID

        Returns:
            Workflow ID

        Raises:
            ValueError: If no match or multiple matches found
        """
        if is_likely_id(identifier):
            return identifier

        # Search by name
        response = self.client.get("/platform/automation/v1/workflows")
        data = response.json()
        workflows = data.get("results", [])

        matches = [w for w in workflows if w.get("title", "").lower() == identifier.lower()]

        if len(matches) == 0:
            # Try partial match
            matches = [w for w in workflows if identifier.lower() in w.get("title", "").lower()]

        if len(matches) == 0:
            raise ValueError(f"No workflow found matching '{identifier}'")
        elif len(matches) > 1:
            names = [f"  - {w['title']} ({w['id']})" for w in matches[:5]]
            raise ValueError(f"Multiple workflows match '{identifier}':\n" + "\n".join(names))

        return matches[0]["id"]

    def resolve_document(self, identifier: str, doc_type: str | None = None) -> str:
        """Resolve a document (dashboard/notebook) name or ID to an ID.

        Args:
            identifier: Document name or ID
            doc_type: Optional type filter ("dashboard" or "notebook")

        Returns:
            Document ID

        Raises:
            ValueError: If no match or multiple matches found
        """
        if is_likely_id(identifier):
            return identifier

        # Search by name
        params = {}
        if doc_type:
            params["filter"] = f'type == "{doc_type}"'

        response = self.client.get("/platform/document/v1/documents", params=params)
        data = response.json()
        documents = data.get("documents", [])

        matches = [d for d in documents if d.get("name", "").lower() == identifier.lower()]

        if len(matches) == 0:
            matches = [d for d in documents if identifier.lower() in d.get("name", "").lower()]

        if len(matches) == 0:
            raise ValueError(f"No document found matching '{identifier}'")
        elif len(matches) > 1:
            names = [f"  - {d['name']} ({d['id']})" for d in matches[:5]]
            raise ValueError(f"Multiple documents match '{identifier}':\n" + "\n".join(names))

        return matches[0]["id"]

    def resolve_slo(self, identifier: str) -> str:
        """Resolve an SLO name or ID to an ID.

        Args:
            identifier: SLO name or ID

        Returns:
            SLO ID

        Raises:
            ValueError: If no match or multiple matches found
        """
        if is_likely_id(identifier):
            return identifier

        response = self.client.get("/platform/slo/v1/slos")
        data = response.json()
        slos = data.get("slos", [])

        matches = [s for s in slos if s.get("name", "").lower() == identifier.lower()]

        if len(matches) == 0:
            matches = [s for s in slos if identifier.lower() in s.get("name", "").lower()]

        if len(matches) == 0:
            raise ValueError(f"No SLO found matching '{identifier}'")
        elif len(matches) > 1:
            names = [f"  - {s['name']} ({s['id']})" for s in matches[:5]]
            raise ValueError(f"Multiple SLOs match '{identifier}':\n" + "\n".join(names))

        return matches[0]["id"]
