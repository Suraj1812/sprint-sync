"""GitHub connector."""

from typing import Any


class GitHubConnector:
    name = "github"

    async def execute(self, config: dict[str, Any]) -> Any:
        return {"repository": config.get("repo"), "action": config.get("action")}

    async def health(self) -> dict[str, Any]:
        return {"ok": True}
