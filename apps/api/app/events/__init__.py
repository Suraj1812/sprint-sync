"""Lightweight in-process event dispatcher for domain events."""

from collections.abc import Callable
from typing import Any

_subscribers: dict[str, list[Callable[..., Any]]] = {}


class Event:
    def __init__(self, name: str, payload: dict) -> None:
        self.name = name
        self.payload = payload


def subscribe(event_name: str, handler: Callable[..., Any]) -> None:
    _subscribers.setdefault(event_name, []).append(handler)


def emit(event: Event) -> None:
    for handler in _subscribers.get(event.name, []):
        handler(event)
