"""Subprocess and Docker execution engine for agent skills."""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import uuid
from pathlib import Path
from typing import Optional

from core.indexer import SkillWiki
from core.models import ExecutionResult, SkillMetadata

logger = logging.getLogger("skillforge.executor")


def _is_docker_enabled() -> bool:
    """Check if Docker isolation is enabled via environment."""
    val = os.environ.get("SKILLFORGE_USE_DOCKER", "false").lower()
    return val in ("1", "true", "yes", "on")


def _build_command(
    runner: str,
    script_path: Path,
    params_json: str,
    run_dir: Path,
    use_docker: bool = False,
) -> list[str]:
    """Construct command line arguments for subprocess or docker."""
    if use_docker:
        docker_image = os.environ.get("SKILLFORGE_DOCKER_IMAGE", "python:3.11-slim")
        # Mount run_dir into /workspace; drop network access for safety
        cmd = [
            "docker",
            "run",
            "--rm",
            "--network", "none",
            "-v", f"{run_dir.resolve()}:/workspace",
            "-w", "/workspace",
            "-e", "SKILL_OUTPUT_DIR=/workspace/output",
            docker_image,
        ]
        if runner == "python":
            cmd.extend(["python", "/workspace/run.py", params_json])
            return cmd
        elif runner == "blender":
            blender_bin = os.environ.get("BLENDER_BIN", "blender")
            cmd.extend([blender_bin, "--background", "--python", "/workspace/run.py", "--", params_json])
            return cmd
        else:
            raise ValueError(f"Unsupported runner for Docker: {runner}")

    # Native host runner execution
    if runner == "python":
        return [sys.executable, str(script_path), params_json]
    if runner == "blender":
        blender_bin = os.environ.get("BLENDER_BIN", "blender")
        return [blender_bin, "--background", "--python", str(script_path), "--", params_json]

    raise ValueError(f"Unknown runner '{runner}'")


async def execute_code(
    code: str,
    runner: str,
    params: dict,
    timeout_s: int = 120,
    runs_dir: Path | None = None,
    use_docker: bool | None = None,
) -> ExecutionResult:
    """Run code in an isolated per-run directory with timeout and artifact capture."""
    runs_root = Path(runs_dir or os.environ.get("SKILLFORGE_RUNS", "runs"))
    run_id = uuid.uuid4().hex[:12]
    run_dir = (runs_root / run_id).resolve()
    out_dir = run_dir / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    script = run_dir / "run.py"
    script.write_text(code, encoding="utf-8")

    params_json = json.dumps(params or {})
    docker_flag = _is_docker_enabled() if use_docker is None else use_docker

    try:
        cmd = _build_command(runner, script, params_json, run_dir, use_docker=docker_flag)
    except Exception as exc:
        return ExecutionResult(
            success=False,
            return_code=1,
            stderr=f"Failed constructing runner command: {exc}",
            run_dir=str(run_dir),
        )

    env = {**os.environ, "SKILL_OUTPUT_DIR": str(out_dir)}
    logger.debug("Executing [%s] (docker=%s) in %s", runner, docker_flag, run_dir)

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=run_dir,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
    except FileNotFoundError as err:
        logger.error("Runner executable not found: %s", err)
        return ExecutionResult(
            success=False,
            return_code=127,
            stderr=f"Runner executable not found (code 127): {err}",
            run_dir=str(run_dir),
        )

    try:
        stdout_bytes, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=timeout_s)
    except asyncio.TimeoutError:
        logger.warning("Process timed out after %ds in %s", timeout_s, run_dir)
        try:
            proc.kill()
            await proc.wait()
        except Exception:
            pass
        return ExecutionResult(
            success=False,
            return_code=124,
            stderr=f"Execution timed out after {timeout_s}s",
            run_dir=str(run_dir),
        )

    return_code = proc.returncode if proc.returncode is not None else 0
    stdout_text = stdout_bytes.decode(errors="replace")
    stderr_text = stderr_bytes.decode(errors="replace")

    # Discover generated output artifacts
    artifacts = sorted(str(p.resolve()) for p in out_dir.rglob("*") if p.is_file())
    logger.debug("Execution completed with code %d, artifacts: %d", return_code, len(artifacts))

    return ExecutionResult(
        success=(return_code == 0),
        return_code=return_code,
        stdout=stdout_text,
        stderr=stderr_text,
        output_artifacts=artifacts,
        run_dir=str(run_dir),
    )


async def run_skill(
    wiki: SkillWiki,
    skill_id: str,
    params: dict | None = None,
    allow_draft: bool = False,
    use_docker: bool | None = None,
) -> ExecutionResult:
    """Execute a skill from the wiki, validating status and recording telemetry."""
    bundle = wiki.load(skill_id)
    meta: SkillMetadata = bundle.metadata

    if meta.status != "validated" and not allow_draft:
        logger.warning("Refusing to execute unvalidated skill '%s' (status: %s)", skill_id, meta.status)
        return ExecutionResult(
            success=False,
            return_code=2,
            stderr=f"Skill '{skill_id}' is '{meta.status}'; re-validate it first or pass allow_draft=True",
        )

    merged_params = {**meta.example_params, **(params or {})}
    logger.info("Running skill '%s' (%s)", skill_id, meta.runner)
    result = await execute_code(
        code=bundle.code_payload,
        runner=meta.runner,
        params=merged_params,
        timeout_s=meta.timeout_s,
        use_docker=use_docker,
    )

    # Record telemetry stats in SQLite
    wiki.record_run(skill_id, result.success)
    return result
