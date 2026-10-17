# Core Loop & Dual-Review Quality Gate

## Separation of Concerns in Review
Traditional human PRs combine behavioral verification and static code review. In an AI Software Factory, mixing these roles creates blind spots. The factory strictly bifurcates quality gating into two distinct, sequential phases:

```
[ Builder Agent Completes Work ]
               │
               ▼
   [ Gate 1: App Validation ]
   - Runs application in sandbox
   - Simulates real user behavior (Playwright / API / CLI)
   - Evaluates against Holdout Scenarios
               │
      ┌────────┴────────┐
      ▼ (Pass)          ▼ (Fail)
[ Gate 2: Code Review ]  [ Feedback to Builder ]
- Analyzes code hygiene (Bounded retry, max 3)
- Checks architectural rules
- Audits simplicity & no dead code
- Scans for security flaws
      │
      ┌────────┴────────┐
      ▼ (Approve)       ▼ (Changes Requested)
[ Merge to Staging ]     [ Feedback to Builder ]
                         (Bounded retry, max 3)
```

### Gate 1: App Validation (Behavioral)
- **Tooling**: Playwright / Puppeteer for web apps, HTTP clients for microservices, subprocess runners for CLI tools.
- **Focus**: Does the feature actually work end-to-end? Can a user interact with it without console errors, crashes, or unhandled exceptions?
- **Rule**: If the app fails to start or buttons do not respond, the review does not proceed to Gate 2.

### Gate 2: Code Review (Structural & Hygiene)
- **Focus**: Maintainability, clarity, and architectural simplicity (combating Dex Horthy's "Agent Code Sprawl").
- **Checklist**:
  1. Did the agent introduce unnecessary dependencies or libraries?
  2. Are data models cleanly structured or did the agent duplicate existing types?
  3. Are there hardcoded secrets or sensitive configs?
  4. Did the agent modify any protected paths (`engineering.md`, `.github/workflows/`)?
  5. Is error handling robust and idiomatic?
