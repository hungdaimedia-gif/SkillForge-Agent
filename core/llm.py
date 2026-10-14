"""LLM backends: Anthropic API (SDK) and the Claude Code CLI (`claude -p`).

Every backend exposes:
  complete(system, user) -> str
  complete_json(system, user, schema, images=None) -> dict   (structured output)

`get_llm()` picks the backend from SKILLFORGE_LLM = auto | api | claude-cli.
"auto" uses the API when ANTHROPIC_API_KEY is set, otherwise the logged-in
Claude Code CLI (so a Claude subscription works without an API key).
"""
from __future__ import annotations

import base64
import json
import logging
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Protocol, Sequence

logger = logging.getLogger("skillforge.llm")

_MEDIA_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png",
                ".webp": "image/webp", ".gif": "image/gif"}


class LLMError(RuntimeError):
    pass


class LLMClient(Protocol):
    """Protocol for LLM completions."""

    def complete(self, system: str, user: str) -> str:
        ...


def parse_json_text(text: str) -> Any:
    """Parse JSON from model text, tolerating ```json fences or stray prose."""
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(1))
        except json.JSONDecodeError:
            pass
    # Outermost object: first '{' .. last '}'
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end > start:
        return json.loads(text[start:end + 1])
    raise LLMError(f"Model did not return JSON: {text[:300]}")


def complete_json(llm: Any, system: str, user: str, schema: dict,
                  images: Sequence[tuple[str, str]] | None = None) -> dict:
    """Structured call on any backend; falls back to prompt-only JSON for simple fakes."""
    if hasattr(llm, "complete_json"):
        return llm.complete_json(system, user, schema, images=images)
    hint = "\n\nReply with ONLY a JSON object matching this JSON Schema:\n" + json.dumps(schema)
    return parse_json_text(llm.complete(system + hint, user))


class AnthropicLLM:
    """Anthropic API via the official SDK (streaming, structured outputs, prompt caching)."""

    def __init__(self, model: str | None = None, max_tokens: int = 32000):
        import anthropic  # pip install anthropic

        self.client = anthropic.Anthropic()
        self.model = model or os.environ.get("SKILLFORGE_MODEL", "claude-sonnet-5-5")
        self.max_tokens = int(os.environ.get("SKILLFORGE_MAX_TOKENS", max_tokens))
        logger.info("Initialized AnthropicLLM with model: %s", self.model)

    def _create(self, system: str, content: list[dict], output_config: dict | None = None):
        kwargs: dict[str, Any] = dict(
            model=self.model,
            max_tokens=self.max_tokens,
            # System prompts are reused across every section -> cache them.
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": content}],
        )
        if output_config:
            kwargs["output_config"] = output_config
        # Long outputs (whole SKILL.md) -> stream to avoid HTTP timeouts.
        with self.client.messages.stream(**kwargs) as stream:
            msg = stream.get_final_message()
        if msg.stop_reason == "refusal":
            raise LLMError("Model refused the request")
        if msg.stop_reason == "max_tokens":
            raise LLMError(f"Output truncated at max_tokens={self.max_tokens}")
        return msg

    def complete(self, system: str, user: str) -> str:
        msg = self._create(system, [{"type": "text", "text": user}])
        return "".join(b.text for b in msg.content if b.type == "text")

    def complete_json(self, system: str, user: str, schema: dict,
                      images: Sequence[tuple[str, str]] | None = None) -> dict:
        content: list[dict] = []
        for label, path in images or []:
            p = Path(path)
            media = _MEDIA_TYPES.get(p.suffix.lower())
            if not media or not p.exists():
                continue
            content.append({"type": "text", "text": label})
            content.append({"type": "image", "source": {
                "type": "base64", "media_type": media,
                "data": base64.standard_b64encode(p.read_bytes()).decode("ascii")}})
        content.append({"type": "text", "text": user})
        msg = self._create(system, content,
                           output_config={"format": {"type": "json_schema", "schema": schema}})
        text = next((b.text for b in msg.content if b.type == "text"), "")
        return json.loads(text)


class ClaudeCLILLM:
    """Headless Claude Code (`claude -p`) — uses the user's Claude login, no API key.

    Images are handed over as file paths: the CLI's Read tool opens them, limited
    to the frame directories passed through --add-dir.
    """

    def __init__(self, model: str | None = None, timeout_s: int = 900):
        self.bin = os.environ.get("SKILLFORGE_CLAUDE_BIN") or shutil.which("claude")
        if not self.bin:
            raise LLMError("claude CLI not found on PATH (set SKILLFORGE_CLAUDE_BIN)")
        self.model = model or os.environ.get("SKILLFORGE_CLI_MODEL", "")
        self.timeout_s = timeout_s

    def _run(self, system: str, user: str, schema: dict | None,
             image_paths: Sequence[str] = ()) -> dict:
        with tempfile.TemporaryDirectory(prefix="sf_cli_") as tmp:
            sys_file = Path(tmp) / "system.md"
            sys_file.write_text(system, encoding="utf-8")
            cmd = [self.bin, "-p", "--output-format", "json", "--no-session-persistence",
                   "--system-prompt-file", str(sys_file), "--strict-mcp-config"]
            if self.model:
                cmd += ["--model", self.model]
            if schema is not None:
                cmd += ["--json-schema", json.dumps(schema)]
            if image_paths:
                cmd += ["--tools", "Read", "--allowedTools", "Read"]
                for d in sorted({str(Path(p).resolve().parent) for p in image_paths}):
                    cmd += ["--add-dir", d]
            else:
                cmd += ["--tools", ""]
            proc = subprocess.run(cmd, input=user, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=self.timeout_s)
        try:
            data = json.loads(proc.stdout)
        except json.JSONDecodeError as exc:
            raise LLMError(f"claude CLI failed (code {proc.returncode}): "
                           f"{(proc.stderr or proc.stdout)[:500]}") from exc
        if data.get("is_error"):
            raise LLMError(f"claude CLI error: {data.get('result')}")
        return data

    def complete(self, system: str, user: str) -> str:
        return str(self._run(system, user, None).get("result", ""))

    def complete_json(self, system: str, user: str, schema: dict,
                      images: Sequence[tuple[str, str]] | None = None) -> dict:
        paths = [str(Path(p).resolve()) for _, p in images or [] if Path(p).exists()]
        if paths:
            listing = "\n".join(f"- {label}: {Path(p).resolve()}"
                                for (label, p) in images or [] if Path(p).exists())
            user = ("Before answering, open EVERY image below with the Read tool and use what "
                    "you see (UI labels, hotkey overlays, values).\n" + listing + "\n\n" + user)
        data = self._run(system, user, schema, paths)
        structured = data.get("structured_output")
        if isinstance(structured, dict):
            return structured
        return parse_json_text(str(data.get("result", "")))


def get_llm(backend: str | None = None, model: str | None = None) -> Any:
    backend = (backend or os.environ.get("SKILLFORGE_LLM", "auto")).lower()
    if backend == "auto":
        backend = "api" if os.environ.get("ANTHROPIC_API_KEY") else "claude-cli"
    if backend == "api":
        return AnthropicLLM(model=model)
    if backend in ("claude-cli", "cli", "claude"):
        return ClaudeCLILLM(model=model)
    raise ValueError(f"Unknown SKILLFORGE_LLM backend: {backend}")
