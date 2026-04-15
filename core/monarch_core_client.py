import logging
from datetime import datetime
from typing import Any

import httpx


logger = logging.getLogger(__name__)


class MonarchCoreClient:
    """Best-effort client for syncing the legacy Monarch pipeline into monarch-core."""

    def __init__(
        self,
        base_url: str | None,
        project_slug: str,
        api_key: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._base_url = base_url.rstrip("/") if base_url else None
        self._project_slug = project_slug
        self._api_key = api_key
        self._owns_client = client is None
        self._client = client or httpx.AsyncClient(timeout=15.0)

    def _headers(self) -> dict[str, str]:
        if not self._api_key:
            return {}
        return {"X-API-Key": self._api_key}

    @property
    def enabled(self) -> bool:
        return bool(self._base_url)

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def ensure_project(self) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        response = await self._client.get(
            f"{self._base_url}/api/projects",
            params={"slug": self._project_slug},
            headers=self._headers(),
        )
        response.raise_for_status()
        items = response.json()
        if items:
            return items[0]

        logger.warning("monarch-core project '%s' not found", self._project_slug)
        return None

    async def create_idea(
        self,
        *,
        title: str,
        raw_input: str,
        business_unit_id: str | None,
        project_id: str | None,
    ) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        response = await self._client.post(
            f"{self._base_url}/api/ideas",
            headers=self._headers(),
            json={
                "title": title,
                "raw_input": raw_input,
                "source": "manual",
                "classification": "operational_task",
                "business_unit_id": business_unit_id,
                "project_id": project_id,
            },
        )
        response.raise_for_status()
        return response.json()

    async def create_task(
        self,
        *,
        project_id: str,
        title: str,
        description: str,
        status: str,
        priority: str,
        approval_required: bool,
    ) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        response = await self._client.post(
            f"{self._base_url}/api/tasks",
            headers=self._headers(),
            json={
                "project_id": project_id,
                "title": title,
                "description": description,
                "task_type": "planning",
                "status": status,
                "priority": priority,
                "owner_type": "agent",
                "owner_name": "legacy-monarch-pipeline",
                "approval_required": approval_required,
            },
        )
        response.raise_for_status()
        return response.json()

    async def update_task(
        self,
        *,
        task_id: str,
        status: str,
        priority: str | None = None,
        approval_required: bool | None = None,
    ) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        payload: dict[str, Any] = {"status": status}
        if priority is not None:
            payload["priority"] = priority
        if approval_required is not None:
            payload["approval_required"] = approval_required

        response = await self._client.patch(
            f"{self._base_url}/api/tasks/{task_id}",
            headers=self._headers(),
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    async def create_approval(
        self,
        *,
        project_id: str,
        task_id: str | None,
        title: str,
        summary: str,
    ) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        response = await self._client.post(
            f"{self._base_url}/api/approvals",
            headers=self._headers(),
            json={
                "project_id": project_id,
                "task_id": task_id,
                "title": title,
                "summary": summary,
                "status": "pending",
            },
        )
        response.raise_for_status()
        return response.json()

    async def create_execution(
        self,
        *,
        project_id: str,
        task_id: str | None,
        agent_name: str,
        execution_type: str,
        status: str,
        input_payload: str | None = None,
        output_summary: str | None = None,
        error_message: str | None = None,
        started_at: datetime | None = None,
        finished_at: datetime | None = None,
    ) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        response = await self._client.post(
            f"{self._base_url}/api/executions",
            headers=self._headers(),
            json={
                "project_id": project_id,
                "task_id": task_id,
                "agent_name": agent_name,
                "execution_type": execution_type,
                "status": status,
                "input_payload": input_payload,
                "output_summary": output_summary,
                "error_message": error_message,
                "started_at": started_at.isoformat() if started_at else None,
                "finished_at": finished_at.isoformat() if finished_at else None,
            },
        )
        response.raise_for_status()
        return response.json()

    async def update_execution(
        self,
        *,
        execution_id: str,
        status: str,
        output_summary: str | None = None,
        error_message: str | None = None,
        finished_at: datetime | None = None,
    ) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        payload: dict[str, Any] = {"status": status}
        if output_summary is not None:
            payload["output_summary"] = output_summary
        if error_message is not None:
            payload["error_message"] = error_message
        if finished_at is not None:
            payload["finished_at"] = finished_at.isoformat()

        response = await self._client.patch(
            f"{self._base_url}/api/executions/{execution_id}",
            headers=self._headers(),
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    async def decide_approval(self, *, approval_id: str, decision: str) -> dict[str, Any] | None:
        if not self.enabled:
            return None

        route = "approve" if decision == "approved" else "reject"
        response = await self._client.post(
            f"{self._base_url}/api/approvals/{approval_id}/{route}",
            headers=self._headers(),
            json={"decided_by": "legacy-monarch-pipeline"},
        )
        response.raise_for_status()
        return response.json()
