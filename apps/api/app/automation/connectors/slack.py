"""Slack connector."""

from typing import Any


class SlackConnector:
    name = "slack"

    async def execute(self, config: dict[str, Any]) -> Any:
        return {"sent": True, "channel": config.get("channel")}

    async def health(self) -> dict[str, Any]:
        return {"ok": True}
