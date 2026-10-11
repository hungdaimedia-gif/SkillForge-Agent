"""Sandbox validation with a bounded self-repair loop (max 3 retries)."""
from __future__ import annotations

import asyncio
import fnmatch
import logging
import re
from pathlib import Path

from runtime.executor import execute_code

from .llm import LLMClient
from .models import ExecutionResult, SkillBundle, VerificationResult

logger = logging.getLogger("skillforge.validator")

REPAIR_SYSTEM = """\
You are an expert debugger fixing a failing agent skill script.
Follow the STRICT skill contract:
- Parameter JSON is read from the LAST sys.argv argument:
    params = json.loads(sys.argv[-1]) if len(sys.argv) > 1 and sys.argv[-1].startswith("{") else {}
- Provide robust defaults for all parameters.
- Write ALL output files into directory given by env var SKILL_OUTPUT_DIR.
- Exit non-zero on error.
- Return ONLY the full, corrected Python script inside a single ```python ... ``` markdown block.
Do not add conversational preamble.
"""


def _artifacts_ok(bundle: SkillBundle, res: ExecutionResult) -> bool:
    """Check if all expected artifacts (globs) are present in output_artifacts."""
    if not bundle.metadata.expected_artifacts:
        return True
    artifact_names = [Path(p).name for p in res.output_artifacts]
    for pattern in bundle.metadata.expected_artifacts:
        matched = any(fnmatch.fnmatch(name, pattern) for name in artifact_names)
        if not matched:
            logger.warning("Expected artifact pattern '%s' not found in outputs: %s",
                           pattern, artifact_names)
            return False
    return True


async def validate(
    bundle: SkillBundle,
    llm: LLMClient | None = None,
    max_retries: int = 3,
    runs_dir: Path | None = None,
    use_docker: bool = False,
) -> tuple[SkillBundle, VerificationResult]:
    """Execute skill with example_params and run self-repair loop on failure.

    Stops immediately if runner binary is missing (return code 127).
    Marks status as 'validated' ONLY on verified success.
    """
    history: list[ExecutionResult] = []
    meta = bundle.metadata
    logger.info("Validating skill '%s' (%s, runner=%s, max_retries=%d)",
                meta.name, meta.id, meta.runner, max_retries)

    for attempt in range(max_retries + 1):
        attempt_num = attempt + 1
        logger.debug("Validation attempt %d/%d for '%s'", attempt_num, max_retries + 1, meta.id)

        res = await execute_code(
            code=bundle.code_payload,
            runner=meta.runner,
            params=meta.example_params,
            timeout_s=meta.timeout_s,
            runs_dir=runs_dir,
            use_docker=use_docker,
        )
        history.append(res)

        passed = res.success and _artifacts_ok(bundle, res)
        if passed:
            logger.info("Skill '%s' successfully validated on attempt %d", meta.id, attempt_num)
            bundle.metadata.status = "validated"
            return bundle, VerificationResult(
                passed=True,
                attempts=attempt_num,
                history=history,
                reason="All checks passed and expected artifacts verified",
            )

        # Code 127 = runner binary not found (e.g. blender or docker not installed)
        if res.return_code == 127:
            logger.warning("Runner binary missing for '%s' (code 127). Aborting self-repair.", meta.id)
            break

        if attempt == max_retries or llm is None:
            logger.warning("Validation failed for '%s' after %d attempt(s). No more retries.",
                           meta.id, attempt_num)
            break

        # Prepare repair prompt
        failure_reason = res.stderr.strip()
        if not failure_reason:
            missing = [g for g in meta.expected_artifacts
                       if not any(fnmatch.fnmatch(Path(p).name, g) for p in res.output_artifacts)]
            failure_reason = f"Execution exited with code {res.return_code}, or missing expected artifacts: {missing}"

        logger.info("Self-repairing '%s' (attempt %d -> %d) due to error: %s",
                    meta.id, attempt_num, attempt_num + 1, failure_reason[:150])

        prompt = (
            f"Failing Script for skill '{meta.name}':\n"
            f"```python\n{bundle.code_payload}\n```\n\n"
            f"Parameters: {meta.example_params}\n"
            f"Expected Artifacts: {meta.expected_artifacts}\n"
            f"Error / Traceback:\n{failure_reason[-3000:]}"
        )

        try:
            fixed_response = await asyncio.to_thread(llm.complete, REPAIR_SYSTEM, prompt)
            match = re.search(r"```(?:python)?\s*(.*?)```", fixed_response, re.DOTALL)
            fixed_code = (match.group(1) if match else fixed_response).strip() + "\n"
            bundle.code_payload = fixed_code
        except Exception as exc:
            logger.error("LLM repair invocation failed for '%s': %s", meta.id, exc)
            break

    last_res = history[-1]
    reason_msg = (last_res.stderr or f"missing expected artifacts {meta.expected_artifacts}")[-500:]
    bundle.metadata.status = "draft"
    logger.info("Skill '%s' remains draft. Verification failed.", meta.id)
    return bundle, VerificationResult(
        passed=False,
        attempts=len(history),
        history=history,
        reason=reason_msg,
    )
