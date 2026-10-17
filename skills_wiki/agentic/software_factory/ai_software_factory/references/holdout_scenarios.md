# Holdout Scenarios: Preventing Agent Sycophancy & Overfitting

## The Problem: AI Sycophancy in TDD
When LLM coding agents are provided with unit tests or evaluation criteria upfront:
1. **Test-Specific Hacks**: The agent tends to write `if input == "edge_case": return "expected_output"` or mock away subsystems instead of implementing proper domain models.
2. **False Confidence**: Public test suites pass 100%, but the software fails immediately upon first real user interaction.

## The Solution: Quarantined Holdout Scenarios
A **Holdout Scenario** is an acceptance test or behavioral assertion designed before implementation that is **strictly hidden from the Builder Agent**.

### Quarantine Protocol
1. **Creation**: The human engineer or Architect Agent specifies holdout scenarios in a secured directory (e.g. `.factory/holdouts/` or a separate repo/environment).
2. **Isolation**: The `Builder Agent` running in a Git Worktree has its `.gitignore` or filesystem sandbox restricted such that holdout files are completely invisible.
3. **Execution**: After the builder claims completion and passes all internal tests, the **Validation Agent** mounts the holdout scenarios in a temporary testing container.
4. **Evaluation**: If holdout tests fail, the Validation Agent translates the failure into high-level behavioral feedback (e.g., *"When submitting a form with accented characters, the backend crashed with a 500 error instead of properly encoding UTF-8"*), without leaking the exact test code or asserts.
