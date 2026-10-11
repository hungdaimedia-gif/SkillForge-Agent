"""Minimal LLM interface with Anthropic client and protocol for testing."""
from __future__ import annotations

import logging
import os
from typing import Protocol

logger = logging.getLogger("skillforge.llm")


class LLMClient(Protocol):
    """Protocol for LLM completions."""

    def complete(self, system: str, user: str) -> str:
        ...


class AnthropicLLM:
    """Production Anthropic Claude client."""

    def __init__(self, model: str | None = None, max_tokens: int = 4096):
        import anthropic  # pip install anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        self.model = model or os.environ.get("SKILLFORGE_MODEL", "claude-sonnet-5-5")
        self.max_tokens = max_tokens
        logger.info("Initialized AnthropicLLM with model: %s", self.model)

    def complete(self, system: str, user: str) -> str:
        logger.debug("Prompting %s (user payload: %d chars)", self.model, len(user))
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
        )
        response_text = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
        logger.debug("Received response (%d chars)", len(response_text))
        return response_text
