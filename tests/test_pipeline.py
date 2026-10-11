"""Comprehensive offline test suite for SkillForge-Agent using FakeLLM."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path

import pytest

from core.extractor import extract_from_file, extract_from_video, extract_skill, parse_bundle
from core.indexer import SkillWiki
from core.models import SkillBundle, SkillMetadata
from core.validator import validate
from runtime.executor import execute_code, run_skill
from runtime.mcp_server import browse_taxonomy, get_skill_details, run_chain, run_skill as mcp_run_skill, search_skills

GOOD_CODE = """\
import json, os, sys
from pathlib import Path

params = json.loads(sys.argv[-1]) if len(sys.argv) > 1 and sys.argv[-1].startswith("{") else {}
filename = params.get("filename", "out.txt")
content = params.get("content", "hello world")

out_dir = Path(os.environ["SKILL_OUTPUT_DIR"])
out_dir.mkdir(parents=True, exist_ok=True)
(out_dir / filename).write_text(content, encoding="utf-8")
print(f"Generated {filename}")
"""

BROKEN_CODE = """\
import sys
raise RuntimeError("Intentional syntax/runtime failure for self-repair verification")
"""


class FakeRepairLLM:
    """Simulates LLM: first response returns broken code; second repair response returns good code."""

    def __init__(self):
        self.calls = 0

    def complete(self, system: str, user: str) -> str:
        self.calls += 1
        if "expert debugger fixing a failing agent skill" in system:
            return f"```python\n{GOOD_CODE}\n```"

        return json.dumps({
            "metadata": {
                "name": "Write Test File",
                "taxonomy_path": "python/files/write_file",
                "description": "Writes text content into a file in SKILL_OUTPUT_DIR",
                "tags": ["files", "test", "write"],
                "params_schema": {"filename": "string", "content": "string"},
                "example_params": {"filename": "out.txt", "content": "test payload"},
                "runner": "python",
                "expected_artifacts": ["out.txt"],
                "expected_output": "out.txt",
                "source": "unit_test",
            },
            "code": BROKEN_CODE,
        })


def test_distillation_and_self_repair_loop(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test full closed-loop: extract -> fail -> LLM self-repair -> pass -> save -> search -> run."""
    monkeypatch.setenv("SKILLFORGE_RUNS", str(tmp_path / "runs"))
    monkeypatch.setenv("SKILLFORGE_WIKI", str(tmp_path / "wiki"))

    llm = FakeRepairLLM()
    bundle = extract_skill(llm, "Write a file to disk tutorial", domain_hint="python")
    assert bundle.metadata.status == "draft"

    # Validator should catch broken code, invoke repair, succeed on attempt 2
    bundle, ver = asyncio.run(validate(bundle, llm=llm, max_retries=3, runs_dir=tmp_path / "runs"))
    assert ver.passed is True
    assert ver.attempts == 2
    assert bundle.metadata.status == "validated"
    assert len(ver.history) == 2
    assert ver.history[0].success is False
    assert ver.history[1].success is True

    # Save to wiki
    wiki = SkillWiki(tmp_path / "wiki")
    saved_path = wiki.save(bundle)
    assert saved_path.exists()
    assert (saved_path / "skill.json").exists()
    assert (saved_path / "run.py").exists()

    # Search wiki
    hits = wiki.search("write test file")
    assert len(hits) >= 1
    assert hits[0].id == "python.files.write_file"
    assert hits[0].status == "validated"

    # Execute validated skill
    run_res = asyncio.run(run_skill(wiki, "python.files.write_file", {"content": "updated"}))
    assert run_res.success is True
    assert len(run_res.output_artifacts) >= 1
    artifact_content = Path(run_res.output_artifacts[0]).read_text(encoding="utf-8")
    assert artifact_content == "updated"


def test_missing_runner_code_127_stops_retry(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure missing runner executable (code 127) stops self-repair immediately without burning LLM calls."""
    monkeypatch.setenv("BLENDER_BIN", "non_existent_blender_binary_12345")
    llm = FakeRepairLLM()

    bundle = SkillBundle(
        metadata=SkillMetadata(
            name="Blender Missing Runner Test",
            taxonomy_path="blender/render/missing_runner",
            description="Tests early stop on missing binary",
            runner="blender",
            expected_artifacts=["scene.blend"],
        ),
        code_payload="import bpy\n",
    )

    bundle, ver = asyncio.run(validate(bundle, llm=llm, max_retries=3, runs_dir=tmp_path / "runs"))
    assert ver.passed is False
    # Must stop on attempt 1 because code 127 cannot be solved by script edits
    assert ver.attempts == 1
    assert bundle.metadata.status == "draft"
    assert ver.history[0].return_code == 127


def test_draft_skill_blocked_unless_allowed(tmp_path: Path) -> None:
    """Runtime must reject executing unvalidated draft skills unless allow_draft=True."""
    wiki = SkillWiki(tmp_path / "wiki")
    bundle = SkillBundle(
        metadata=SkillMetadata(
            name="Unvalidated Skill",
            taxonomy_path="python/drafts/unvalidated",
            description="Draft skill that was not validated",
            status="draft",
        ),
        code_payload=GOOD_CODE,
    )
    wiki.save(bundle)

    # Denied by default
    res = asyncio.run(run_skill(wiki, "python.drafts.unvalidated", allow_draft=False))
    assert res.success is False
    assert res.return_code == 2
    assert "re-validate" in res.stderr

    # Allowed when explicitly permitted
    res_allowed = asyncio.run(run_skill(wiki, "python.drafts.unvalidated", allow_draft=True))
    assert res_allowed.success is True


def test_path_traversal_protection(tmp_path: Path) -> None:
    """Ensure malicious skill IDs attempting directory traversal are strictly blocked."""
    wiki = SkillWiki(tmp_path / "wiki")

    with pytest.raises(ValueError):
        wiki._dir("../escape")

    with pytest.raises(ValueError):
        wiki._dir("..")

    with pytest.raises(ValueError):
        wiki._dir("/etc/passwd")

    with pytest.raises(ValueError):
        wiki._dir("python/../../root")


def test_search_reliability_boost(tmp_path: Path) -> None:
    """Historical successful runs should boost ranking in search results."""
    wiki = SkillWiki(tmp_path / "wiki")
    bundle_a = SkillBundle(
        metadata=SkillMetadata(
            name="Alpha Tool",
            taxonomy_path="python/tools/alpha",
            description="Search tool component",
            status="validated",
        ),
        code_payload=GOOD_CODE,
    )
    bundle_b = SkillBundle(
        metadata=SkillMetadata(
            name="Beta Tool",
            taxonomy_path="python/tools/beta",
            description="Search tool component",
            status="validated",
        ),
        code_payload=GOOD_CODE,
    )
    wiki.save(bundle_a)
    wiki.save(bundle_b)

    # Record 5 successful runs for beta
    for _ in range(5):
        wiki.record_run("python.tools.beta", ok=True)

    results = wiki.search("tool component")
    assert len(results) == 2
    # Beta should rank higher due to reliability boost
    assert results[0].id == "python.tools.beta"
    assert results[0].score > results[1].score


def test_mcp_server_tools(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Test FastMCP server tools: browse_taxonomy, search_skills, get_skill_details, run_skill, run_chain."""
    wiki_dir = tmp_path / "mcp_wiki"
    monkeypatch.setenv("SKILLFORGE_WIKI", str(wiki_dir))
    monkeypatch.setenv("SKILLFORGE_RUNS", str(tmp_path / "mcp_runs"))

    wiki = SkillWiki(wiki_dir)
    bundle = SkillBundle(
        metadata=SkillMetadata(
            name="Echo Payload",
            taxonomy_path="python/network/echo",
            description="Echoes JSON parameters to artifact",
            params_schema={"message": "string"},
            example_params={"message": "ping"},
            expected_artifacts=["echo.txt"],
            status="validated",
        ),
        code_payload="""\
import json, os, sys
from pathlib import Path
p = json.loads(sys.argv[-1]) if len(sys.argv) > 1 else {}
msg = p.get("message", "default")
out = Path(os.environ["SKILL_OUTPUT_DIR"]) / "echo.txt"
out.write_text(msg)
print(f"echoed: {msg}")
""",
    )
    wiki.save(bundle)

    # 1. Browse taxonomy
    tree = browse_taxonomy()
    assert "python" in tree
    assert "network" in tree["python"]
    assert "echo" in tree["python"]["network"]

    # 2. Search skills
    hits = search_skills("echo message")
    assert len(hits) >= 1
    assert hits[0]["id"] == "python.network.echo"

    # 3. Get skill details
    details = get_skill_details("python.network.echo")
    assert details["success"] is True
    assert details["metadata"]["name"] == "Echo Payload"
    assert "echoed" in details["code"]

    # 4. Run skill
    run_out = asyncio.run(mcp_run_skill("python.network.echo", {"message": "hello-mcp"}))
    assert run_out["success"] is True
    assert len(run_out["output_artifacts"]) == 1
    content = Path(run_out["output_artifacts"][0]).read_text()
    assert content == "hello-mcp"

    # 5. Run chain (stops on first failure)
    chain_steps = [
        {"skill_id": "python.network.echo", "parameters": {"message": "step1"}},
        {"skill_id": "python.network.echo", "parameters": {"message": "step2"}},
    ]
    chain_res = asyncio.run(run_chain(chain_steps))
    assert len(chain_res) == 2
    assert chain_res[0]["success"] is True
    assert chain_res[1]["success"] is True


def test_video_extraction_helper(tmp_path: Path) -> None:
    """Test video / VLM extraction helper."""
    llm = FakeRepairLLM()
    frame_dummy = tmp_path / "keyframe_01.jpg"
    frame_dummy.write_bytes(b"\xff\xd8\xff\xe0fakejpeg")

    bundle = extract_from_video(
        llm=llm,
        transcript="Step 1: Open file. Step 2: Write text.",
        source_url="https://youtube.com/watch?v=sample123",
        keyframe_paths=[frame_dummy],
        domain_hint="python",
    )
    assert bundle.metadata.name == "Write Test File"
    assert bundle.visual_asset_path == frame_dummy


def test_docker_command_building(tmp_path: Path) -> None:
    """Verify Docker command generator adds --network none, volume mounts and image."""
    from runtime.executor import _build_command
    script = tmp_path / "run.py"
    script.write_text("print(1)")

    # 1. Native command
    cmd_native = _build_command("python", script, "{}", tmp_path, use_docker=False)
    assert "python" in cmd_native[0].lower()

    # 2. Docker command
    cmd_docker = _build_command("python", script, "{}", tmp_path, use_docker=True)
    assert cmd_docker[0] == "docker"
    assert "run" in cmd_docker
    assert "--network" in cmd_docker
    assert "none" in cmd_docker
    assert any("/workspace" in arg for arg in cmd_docker)


def test_bundled_slugify_example() -> None:
    """Verify the default python.text.slugify skill in skills_wiki loads and executes properly."""
    wiki = SkillWiki("skills_wiki")
    bundle = wiki.load("python.text.slugify")
    assert bundle.metadata.status == "validated"
    assert bundle.metadata.runner == "python"

    res = asyncio.run(run_skill(wiki, "python.text.slugify", {"text": "SkillForge Agent Test", "separator": "_"}))
    assert res.success is True
    assert "skillforge_agent_test" in res.stdout

