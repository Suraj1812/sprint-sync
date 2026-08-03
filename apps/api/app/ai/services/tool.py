"""Tool / function calling registry."""

import inspect
import json
from collections.abc import Awaitable, Callable
from typing import Any

from app.core.exceptions import AuthorizationError


class ToolExecutor:
    _tools: dict[str, dict[str, Any]] = {}
    _handlers: dict[str, Callable[..., Awaitable[Any]]] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        handler: Callable[..., Awaitable[Any]],
        required_permission: str | None = None,
    ) -> None:
        self._tools[name] = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": parameters,
            },
        }
        self._handlers[name] = handler
        if required_permission:
            self._tools[name]["x-required-permission"] = required_permission

    def list_schemas(self, user_permissions: set[str] | None = None) -> list[dict[str, Any]]:
        user_permissions = user_permissions or set()
        result = []
        for name, tool in self._tools.items():
            required = tool.get("x-required-permission")
            if required and required not in user_permissions:
                continue
            result.append(tool)
        return result

    async def execute(
        self,
        name: str,
        arguments: dict[str, Any],
        *,
        user_permissions: set[str] | None = None,
        timeout: float = 10.0,
    ) -> Any:
        handler = self._handlers.get(name)
        if not handler:
            raise AuthorizationError(f"Tool not found: {name}")

        tool = self._tools[name]
        required = tool.get("x-required-permission")
        if required and (not user_permissions or required not in user_permissions):
            raise AuthorizationError(f"Missing permission for tool: {name}")

        if inspect.iscoroutinefunction(handler):
            return await handler(**arguments)
        return handler(**arguments)

    async def run_tool_calls(
        self,
        calls: list[dict[str, Any]],
        *,
        user_permissions: set[str] | None = None,
    ) -> list[dict[str, Any]]:
        results = []
        for call in calls:
            name = call.get("name") or call.get("function", {}).get("name")
            arguments = call.get("arguments") or call.get("function", {}).get("arguments", {})
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            try:
                result = await self.execute(name, arguments, user_permissions=user_permissions)
            except Exception as exc:
                result = {"error": str(exc)}
            results.append({"tool": name, "result": result})
        return results


tool_executor = ToolExecutor()
