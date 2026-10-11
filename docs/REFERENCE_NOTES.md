# Resource2Skill Reference Study Notes

This document summarizes findings from an in-depth code study of the **Resource2Skill** repository (`https://github.com/hungdaimedia-gif/Resource2Skill.git`, official Microsoft open-source release corresponding to arXiv:2606.29538). These findings are based strictly on the inspected source code.

---

## 1. Skill Representation

In Resource2Skill, skills are organized across two main directories in the repository:
1. `skills_wiki/<domain>/<skill_id>/`: Structured wiki storage containing human- and agent-readable documentation, visual references, and metadata.
2. `skills_library/<domain>/`: Executable code assets, archetypes, and shells consumed by domain-specific runners.

### Modality Decomposition (The 4-Part Bundle)
Inside each wiki entry (`skills_wiki/<domain>/<skill_id>/`), the skill is split into four canonical components:

- **Metadata (`meta.json`)**:
  - `skill_id`: Unique alphanumeric identifier (e.g. `3d_chocolate_chip_cookie_scene_e39b1dcc`).
  - `skill_name`: Human-readable title (e.g. `"3D Chocolate Chip Cookie Scene"`).
  - `category_path`: List of taxonomic category strings (e.g. `["uncategorized"]` or `["modeling", "geometry"]`).
  - `tier`: Granularity classification from `T1` to `T5`:
    - `T1`: Tokens, palettes, format presets, themes (reference only).
    - `T2`: Formulas, snippets, cell techniques (reference only).
    - `T3`: Reusable components (e.g. cookie scene, charts).
    - `T4`: Whole slide/sheet shells with parameter slots.
    - `T5`: Full workbook or deck archetypes.
  - `applicability`: Explanatory text indicating when the agent should select this skill.
  - `exec_ok`: Tri-state boolean (`true`, `false`, or `null`), indicating whether execution has succeeded without error.
  - `license`: Source license status (e.g. `"youtube_review_pending"`, `"mit"`).
  - `modalities_present`: List of modalities present in the skill directory (`["visual", "text", "code"]`).
  - `source`: Dictionary containing source provenance:
    - `type`: `"youtube"`, `"github"`, `"article"`, or `"manual"`.
    - `url`: Direct link to original resource.
    - `channel` or `author`: Source creator name.
  - `tags`: List of searchable keyword tags.
  - `wash_version` & `wash_run_at`: Timestamp and version of the validation/wash pipeline.

- **Executable Code (`code/skill.py`)**:
  - Self-contained Python script or function.
  - In Blender: creates collections, meshes, shaders, lights, and render settings using `bpy` and `mathutils`.
  - In PPT/Web/Excel: provides procedural layout construction or API manipulation routines.
  - Receives parameters with explicit defaults, returning a completion status.

- **Structured Text (`text/overview.md`)**:
  - **Section 1: High-level Design Pattern Extraction**: Core visual mechanism, rationale, applicability, and value addition.
  - **Section 2: Technical Breakdown**: Geometry/topology, materials/shading, lighting, and rendering context.
  - **Section 3: Reproduction Code & Method Table**: Rationales for selected APIs and feasibility assessment score (~95%).

- **Visual Assets (`visual/`)**:
  - Keyframe images extracted from tutorial videos or headless render passes (e.g. `frame_00_stage_20pct.jpg`).
  - Used for visual similarity scoring and multimodal agent inspection.

### Unified Schemas (`core/extraction/schemas.py`)
For modern domain pipelines (e.g. PowerPoint v2), skills are formally classified into three kinds via Pydantic v2:
- `shell`: Parameterized layouts with named `Slot` definitions (`text`, `bullet_list`, `image`, `icon`, `chart`, `accent_block`) constrained by theme typography/color tokens.
- `snippet`: Atomic functional code primitives.
- `inspiration`: Visual-only references (frames + palette + layout notes).

---

## 2. Extraction & Distillation Pipeline

The extraction pipeline converts raw multimodal human tutorials into structured, executable skills:

### Inputs & Ingestion Connectors (`core/sources/`)
- `YouTubeConnector`: Ingests video URLs, retrieves transcripts, samples key video frames at uniform or stage intervals, and filters via query pools.
- `GitHubConnector`: Ingests code repositories and documentation.
- `ArticleConnector`: Scrapes web tutorials and instructional documentation.
- `StaticArtifactConnector`: Ingests local files and pre-collected corpora from `_static_corpus.json`.

### Prompts & LLM Architecture (`core/extraction/distiller_shell.py`, `core/analyzer.py`)
- **Models**:
  - Multimodal Vision: Gemini 3.1 Pro / Gemini 1.5 Pro (via `google-genai` / `vertexai`) using structured output (`response_schema=ShellDistillerOutput`).
  - Reasoning/Text: Azure OpenAI `gpt-5.4`, `gpt-5.5`, `o1`/`o3` with configurable `reasoning_effort` (`low`, `medium`, `high`).
- **Prompt Structure**:
  - Strict system prompt (`_DISTILL_SYSTEM`) instructing the model to extract role, content shape, density, slots, and executable render code.
  - Enforces dependency on theme/parameter helpers (`_shell_helpers`) rather than hardcoding fonts, RGB hex values, or absolute dimensions.
  - Includes hand-written few-shot reference implementations (e.g. `_SEED_SHELL` / `bullet_card_list.py`).

### Verification & Quality Gates (`core/extraction/quality_gate.py`)
Extracted skills must pass three validation gates before becoming `active`:
1. **Execution Gate (`exec_ok`)**: Generates synthetic slot data (`make_sample_slots`) with realistic lengths and executes the render function in a headless environment. Must terminate with exit code 0.
2. **Render Gate (`render_ok`)**: Invokes a headless rendering engine (LibreOffice for PPTX, Playwright for HTML/CSS, `bpy` for Blender). Checks that output artifact exists, exceeds minimum size (e.g. ≥20 KB PNG), and contains no leftover placeholder tags.
3. **Visual Similarity Gate**: (Optional) Compares the rendered artifact against the original tutorial keyframe using CLIP or vision models.
- **Candidate Fallback**: Any skill failing validation is marked as `candidate` (or quarantined) and excluded from default retrieval until repaired.

---

## 3. Runtime Search & Execution

### Search Pipeline (`core/skill_wiki/bm25.py`, `core/skill_wiki/llm_rerank.py`)
Resource2Skill implements a two-stage retrieval pipeline:
1. **Stage 1 — Okapi BM25 Retrieval**:
   - Zero-dependency, pure-Python implementation of Okapi BM25 ($k_1=1.5, b=0.75$).
   - Tokenizes lowercased alphanumeric words (`[a-z0-9]+`) across `skill_name`, `applicability`, and `tags`.
   - Incorporates a multiplicative visual boost ($1.25\times$) for skills possessing visual preview artifacts.
   - Filters by `tier` and `category_path` prefix.
   - *Design Decision*: Replaced an earlier embedding vector search scaffold because wiki corpora (<1,000 skills per domain) run in sub-millisecond linear time without index maintenance overhead or cold-start latency.
2. **Stage 2 — LLM Reranking**:
   - Takes the top candidates from the BM25 candidate pool.
   - Queries an LLM to evaluate candidates against the user's specific context and rank the top $k$ items.

### MCP Server Runtime (`core/skill_wiki/mcp_tools.py`)
Exposes the wiki contract to LLM clients (such as Claude) via `FastMCP`:
- `list_tiers()`: Returns identifiers `T1` through `T5`.
- `list_categories(tier, category_path, depth)`: Returns the taxonomy hierarchy.
- `list_skills(tier, category_path, source_type, verified_only, limit)`: Filters skills by metadata.
- `get_skill_text(skill_id)`: Retrieves textual overview and usage guidelines.
- `get_skill_code(skill_id)`: Retrieves executable Python code.
- `get_skill_visual(skill_id)`: Retrieves image asset paths.
- `get_skill_recipe(skill_id)`: Retrieves structural composition recipe.
- `search_skills(query, tier, category_path, k)`: Runs BM25 retrieval over the wiki.
- `propose_category(tier, path, reason)`: Queues user taxonomy proposals.
- `apply_skill(skill_id, target_id, kwargs_json)`: Executes a skill against a target session.

### Execution Engine (`core/executor.py`)
- Standardizes execution by injecting an async MCP client (`_MCPWrapper`) into skill execution contexts.
- Skill scripts invoke domain tools via `await mcp.call_tool(name, args)`.
- Traps tool call history, errors, and output verification feedback.

---

## 4. Commands That Actually Exist

Based directly on `cli.py` and `core/skill_wiki/cli_handlers.py`, the following commands exist:

### Main CLI Commands (`cli.py`)
- `python cli.py domains`: Lists available domains and registered categories.
- `python cli.py validate-domain --domain <name>`: Validates domain configuration and runner dependencies.
- `python cli.py collect --domain <name> [--cycles N] [--videos N] [--cycle-quota N] [--source-mix <mix>]`: Runs connector-based resource harvesting.
- `python cli.py analyze --domain <name> --video <url>`: Analyzes a single video URL.
- `python cli.py batch --domain <name> --manifest <path>`: Runs batch analysis from a manifest file.
- `python cli.py build --domain <name>`: Builds search metadata and indices.
- `python cli.py retrieve --domain <name> --query "<query>"`: Queries the skill index.
- `python cli.py plan --domain <name> --task "<task>"`: Generates an execution plan from skills.
- `python cli.py execute --domain <name> --skill <id> [--dry-run]`: Executes a single skill via MCP.
- `python cli.py agent --domain <name> --task "<task>" [--model <m>] [--reasoning <low|med|high>] [--max-iter N] [--n-skills N] [--top-k N]`: Launches the autonomous agent loop.
- `python cli.py score-skills --domain <name> [--limit N] [--model <m>]`: Headless execution and vision quality scoring.
- `python cli.py score-demos --domain <name> [--model <m>]`: Vision evaluation of generated demo artifacts.
- `python cli.py evolve --domain <name> [--dry-run]`: Analyzes quality scores and proposes domain architecture adjustments.
- `python cli.py evolve-distiller --domain <name> [--dry-run]`: Auto-refines distillation prompts based on execution tracebacks.
- `python cli.py evolve-agent --domain <name> [--dry-run]`: Extracts winning skill composition patterns.
- `python cli.py auto-collect --domain <name> [--cycles N] [--videos N] [--workers N]`: Targeted gap-filling collector.
- `python cli.py harness-loop --domain <name> [--skill-limit N] [--collect-cycles N]`: Runs the full 6-stage self-evolution loop.
- `python cli.py brand-extract --domain ppt --brand <slug> --source <path>`: Extracts PPT brand packs from slide decks.

### Wiki Subcommands (`core/skill_wiki/cli_handlers.py`)
- `python cli.py wiki-wash --domain <name> [--dry-run] [--since <iso>]`: Normalizes legacy library skills into canonical wiki entries.
- `python cli.py wiki-audit --domain <name> [--rebuild]`: Audits and rebuilds `index.json`.
- `python cli.py taxonomy-merge --domain <name> [--list] [--all] [--row-ids ...]`: Approves and merges queued taxonomy category proposals.
- `python cli.py source-stats --domain <name>`: Reports source-mix metrics (YouTube, GitHub, articles).
- `python cli.py snapshot --domain <name> --tag <tag> [--allow-dirty]`: Creates immutable hash-manifest snapshots of domain indices.
- `python cli.py budget-status --domain <name>`: Checks token and API call budget limits.
- `python cli.py wiki-backfill --domain <name> [--dry-run]`: Backfills license metadata and quarantines unlicensed skills.

---

## 5. License & Attribution Requirements

- **License**: MIT License.
- **Copyright**: `Copyright (c) Microsoft Corporation.`
- **Conditions**:
  > "The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software."
- **Attribution Policy in SkillForge-Agent**:
  - All concepts, architectural patterns, taxonomy representations, and prompts adapted from Resource2Skill are explicitly credited to Microsoft's Resource2Skill project.
  - The MIT license copyright notice is preserved in documentation and repository headers where applicable.
  - No proprietary or restrictive third-party assets from the reference dataset are incorporated without proper licensing.
