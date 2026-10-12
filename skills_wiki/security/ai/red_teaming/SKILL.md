---
name: ai-red-teaming
description: Use when assessing, testing, or hardening AI and LLM systems, RAG pipelines, autonomous agents, and MCP integrations against adversarial attacks, prompt injections, and security vulnerabilities
---

# AI Red Teaming Security Audit

## Overview
Automated adversarial evaluation and prompt injection testing tool based on the **AI Red Teaming: The Complete Guide** framework (OWASP Top 10 for Agentic Applications 2026, NIST AI RMF, and MITRE ATLAS).

## Capabilities
- Detects Direct & Indirect Prompt Injection attempts (DAN, Developer Mode, Instruction Resets).
- Scans for Canary Token leakage & System Prompt disclosure attempts.
- Audits Tool Execution Privileges against an allowed tool whitelist.
- Generates structured JSON audit artifacts (`red_team_report.json`) and Markdown executive summaries (`security_summary.md`).

## Parameters
- `system_prompt` (string): The base system prompt and instructions of the AI system under test.
- `test_prompts` (list of strings): Adversarial probes and test payloads to evaluate.
- `canary_token` (string): A secret canary string embedded in the prompt to monitor exfiltration.
- `allowed_tools` (list of strings): Approved tool names for the agent under test.

## Artifacts Generated
- `red_team_report.json`: Machine-readable audit findings with severity classifications.
- `security_summary.md`: Executive summary with threat breakdown and remediation actions.
