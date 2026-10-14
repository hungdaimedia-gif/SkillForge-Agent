# SkillForge-Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: >=3.10](https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg)]()
[![Pydantic: v2](https://img.shields.io/badge/Pydantic-v2-red.svg)]()

> Closed-loop agent skill distillation and runtime: **Resource (tutorial / doc / code / transcript) → Extractor → Sandbox Validator (self-repair ×3) → Skills Wiki & Hybrid Index → FastMCP Runtime for Claude.**

Inspired by and building upon Microsoft's [Resource2Skill](https://github.com/microsoft/Resource2Skill) research (arXiv:2606.29538).

---

## Architecture & Closed-Loop Pipeline

```text
+--------------------------------------------------------------------------+
|                               Input Resource                             |
|       (Tutorials, API docs, code snippets, video keyframes + transcript) |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                          Extractor (core/extractor.py)                   |
| - LLM structured distillation prompt (Anthropic Claude / VLM)            |
| - Generates atomic SkillMetadata + self-contained executable code        |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                      Sandbox Validator (core/validator.py)               |
| - Executes code with example_params headlessly                           |
| - Checks exit code == 0 AND expected_artifacts exist                      |
| - Self-Repair: sends traceback to LLM on failure (up to 3 retries)       |
| - Early abort on missing runner binary (code 127)                        |
| - Sets status: "validated" (ONLY upon verified success, else "draft")    |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                       Skills Wiki & Hybrid Index (core/indexer.py)       |
| - Disk hierarchy: skills_wiki/{domain}/{category}/{skill}/               |
| - Hybrid search: Taxonomy filter + lexical BM25-style scoring            |
|   + historical reliability boost ((ok / runs) * log1p(runs) in SQLite)   |
| - Strict path traversal rejection                                        |
+--------------------------------------------------------------------------+
                                     |
                                     v
+--------------------------------------------------------------------------+
|                   FastMCP Server Runtime (runtime/mcp_server.py)         |
| Exposed tools for Claude Code / Claude Desktop:                          |
|   * search_skills        * browse_taxonomy       * get_skill_details     |
|   * run_skill            * run_chain (sequential pipeline)               |
+--------------------------------------------------------------------------+
```

---

## Attribution & Provenance

This project adopts architectural concepts, data decomposition formats (metadata, code, text, visual), and distillation prompt principles from:
- **Resource2Skill**: *Distilling Executable Agent Skills from Human-Created Multimodal Resources*  
  Authors: *Yijia Fan, Zonglin Di, Zimo Wen, Yifan Yang, Mingxi Cheng, Qi Dai, Bei Liu, Kai Qiu, Yue Dong, Ji Li, Chong Luo* (Microsoft Corporation, 2026, arXiv:2606.29538).
- Licensed under the **MIT License** (Copyright © Microsoft Corporation). See [`docs/REFERENCE_NOTES.md`](docs/REFERENCE_NOTES.md) for full extraction analysis.

---

## Quick Start

### 1. Installation

Requires **Python >= 3.10**.

```bash
git clone https://github.com/hungdaimedia-gif/SkillForge-Agent.git
cd SkillForge-Agent

# Using uv (recommended) or standard venv:
uv venv --python 3.11 .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install editable package with dev & llm optional dependencies
uv pip install -e ".[llm,dev]"
```

### 2. Environment Setup

```bash
cp .env.example .env
```

Configure your environment variables:
```bash
ANTHROPIC_API_KEY=your-api-key-here
SKILLFORGE_MODEL=claude-sonnet-5-5
SKILLFORGE_WIKI=skills_wiki
SKILLFORGE_RUNS=runs
BLENDER_BIN=blender
SKILLFORGE_USE_DOCKER=false
```

### 3. Run Offline Tests

```bash
pytest
```
All offline unit tests run against `FakeRepairLLM` without requiring an active API key or network access.

---

## Distill YouTube playlists & books into offline skills

Most knowledge in tutorials and books is *procedural* (UI steps, hotkeys, rules of
thumb), not code. `skillforge distill` turns a playlist or a book into **knowledge
skills** — `SKILL.md` + `references/` + `assets/` (keyframes) + `SOURCES.md` — that an
agent reads later **without internet**.

```bash
uv pip install -e ".[llm,youtube,books,dev]"      # + ffmpeg on PATH (whisper optional)

# 1. Cache transcripts + 720p keyframes (no LLM, re-runs are free)
skillforge fetch "https://www.youtube.com/playlist?list=..."

# 2. Distill: map (units per video, frames really sent) -> plan (skills) -> write -> gate -> quiz
skillforge distill "https://www.youtube.com/playlist?list=..." --domain cascadeur --lang vi
skillforge distill book.pdf --domain animation-principles --lang vi

# 3. Install into an agent's skill folder (never overwrites existing folders)
skillforge export cascadeur --to ~/.claude/skills
```

| Stage | What it guarantees |
|---|---|
| map | every unit carries anchors (`1:23`, `p.87`); invented/out-of-range anchors are dropped |
| plan | units grouped by *capability*, plus a hub skill (glossary, hotkey cheat sheet, routing) |
| write | every statement cited `[S3 1:23]`; long detail moved to `references/` |
| gate | kebab-case name, "Use when…" description, length, every citation/asset/link resolvable |
| eval | closed-book quiz: an agent with only the skill must answer source questions (`--min-eval 0.7`) |

**Agents:** the step-by-step operating procedure (env check, source survey, fixing draft
skills with `--redo`, review checklist, troubleshooting) is packaged as the Claude Code skill
[`.claude/skills/skillforge-distill`](.claude/skills/skillforge-distill/SKILL.md) — picked up
automatically when you open this repo in Claude Code.

LLM backend (`--llm` / `SKILLFORGE_LLM`): `api` (needs `ANTHROPIC_API_KEY`), `claude-cli`
(headless `claude -p`, uses your Claude login), or `auto`. Intermediate results live in
`work/<domain>/` so an interrupted run resumes without re-paying. Book skills only
paraphrase (`license: book_paraphrase_only`); downloaded media stays in `sources_cache/`
(git-ignored).

---

## CLI Usage (`skillforge`)

The CLI provides commands for every stage of the lifecycle:

```bash
# 1. Search existing skills in the wiki
skillforge search "slug url"

# 2. Browse taxonomy tree
skillforge tree

# 3. Execute a validated skill
skillforge run python.text.slugify --params '{"text":"Xin chào Thế Giới","separator":"-"}'

# 4. Attempt draft execution (fails unless --allow-draft is provided)
skillforge run blender.lighting.three_point --allow-draft

# 5. Ingest a new resource tutorial (distill + 3x self-repair sandbox validation)
skillforge ingest tutorial.md --domain python

# 6. Start the FastMCP stdio server
skillforge serve
```

---

## Connecting to Claude

### A. Claude Code (CLI)

Add SkillForge directly to your Claude Code project:

```bash
claude mcp add skillforge -- skillforge serve
```

Or with explicit Python virtual environment path:
```bash
claude mcp add -s project skillforge -e SKILLFORGE_WIKI="G:\SkillForge-Agent\skills_wiki" -- G:\SkillForge-Agent\.venv\Scripts\python.exe G:\SkillForge-Agent\skillforge_cli.py serve
```

Verify connection:
```bash
claude mcp get skillforge
```

### B. Claude Desktop

Add SkillForge to your `claude_desktop_config.json` (on macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`, on Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "skillforge": {
      "command": "skillforge",
      "args": ["serve"],
      "env": {
        "SKILLFORGE_WIKI": "G:/SkillForge-Agent/skills_wiki"
      }
    }
  }
}
```

### MCP Tools Reference

| Tool Name | Parameters | Description |
|---|---|---|
| `search_skills` | `query: str`, `domain: str | None`, `limit: int = 5` | Hybrid search scored by relevance and historical reliability. |
| `browse_taxonomy` | None | Returns the nested domain/category tree of available skills. |
| `get_skill_details` | `skill_id: str` | Retrieves full metadata, schema, and Python code before execution. |
| `run_skill` | `skill_id: str`, `parameters: dict | None`, `allow_draft: bool = false` | Executes skill in isolated run directory; drafts rejected by default. |
| `run_chain` | `steps: list[dict]`, `allow_draft: bool = false` | Runs sequential pipeline `[{skill_id, parameters}, ...]`, stopping on first failure. |

---

## Skill Code Contract

Every skill script (`run.py`) must adhere to this strict contract:
1. **Self-contained**: Relies only on standard library (or target host engine API, such as `bpy`).
2. **Parameters as JSON from the last argument**:
   ```python
   import json, sys
   params = json.loads(sys.argv[-1]) if len(sys.argv) > 1 and sys.argv[-1].startswith("{") else {}
   ```
3. **Safe defaults**: Every parameter must have sensible defaults; nothing is hardcoded.
4. **Output directory isolation**: All generated files must be written inside `os.environ["SKILL_OUTPUT_DIR"]`.
5. **Exit codes**: Exit with non-zero on failure. Print a one-line summary on success.

---

## Security & Docker Isolation

> [!WARNING]
> The default subprocess runner executes Python code locally on the host machine. While each execution runs in an isolated temporary directory with a timeout, **the native subprocess sandbox is NOT a security boundary**.

To safely execute untrusted or LLM-generated code in production:
1. Enable Docker execution in `.env`:
   ```bash
   SKILLFORGE_USE_DOCKER=true
   SKILLFORGE_DOCKER_IMAGE=python:3.11-slim
   ```
2. Or pass `--docker` via CLI:
   ```bash
   skillforge run python.text.slugify --docker
   ```
When enabled, the executor spins up an ephemeral container with `--network none` and mounts only the temporary run directory.
