"""AI safety and guardrails."""

import re
from typing import Any

from app.core.exceptions import AuthorizationError


class Guardrails:
    SENSITIVE_PATTERNS = [
        re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
        re.compile(r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b"),  # Credit card
    ]
    INJECTION_MARKERS = [
        "ignore previous instructions",
        "ignore all prior",
        "disregard your instructions",
        "leak your prompt",
        "system instruction",
    ]

    def validate_input(self, text: str) -> None:
        lower = text.lower()
        for marker in self.INJECTION_MARKERS:
            if marker in lower:
                raise AuthorizationError("Input rejected by safety guardrail")

    def redact(self, text: str) -> str:
        for pattern in self.SENSITIVE_PATTERNS:
            text = pattern.sub("[REDACTED]", text)
        return text

    def filter_output(self, text: str) -> str:
        # Placeholder for content policy filtering.
        return text.strip()

    def check_rag_context(self, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
        # Filter low-relevance chunks; in production use a score threshold.
        return [c for c in chunks if c.get("score", 0) > 0.5]


guardrails = Guardrails()
