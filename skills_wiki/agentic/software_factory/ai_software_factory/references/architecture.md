# Architecture Deep-Dive: The AI Software Factory

## Overview
The AI Software Factory replaces the monolithic "single-prompt dark factory" with a distributed, fault-tolerant assembly line.

```
+-----------------------------------------------------------------------------------+
|                                  HUMAN DEVELOPER                                  |
|   1. Creates Scoped PRD (10-20 tickets) & Holdout Scenarios                       |
|   2. Batch Verifies Staging Deployments                                           |
|   3. Receives Escalations from Manager Agent                                      |
+-----------------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------------+
|                             RELEASE SCOPING & PLANNING                            |
|  - Epic PRD & Out-of-Scope boundaries                                             |
|  - Dependency Mapping Engine (DAG of issues)                                      |
|  - Quarantined Holdout Test Manifest                                              |
+-----------------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------------+
|                        PARALLEL DISPATCH (GIT WORKTREES)                          |
|   Worktree 1 (Issue #101)    Worktree 2 (Issue #102)     Worktree N (Issue #N)   |
|   +---------------------+    +---------------------+     +--------------------+   |
|   |  Triage (Fast/Deep) |    |  Triage (Fast/Deep) |     |  Triage            |   |
|   |  Builder Agent      |    |  Builder Agent      |     |  Builder Agent     |   |
|   |  Validation Agent   |    |  Validation Agent   |     |  Validation Agent  |   |
|   |  Reviewer Agent     |    |  Reviewer Agent     |     |  Reviewer Agent    |   |
|   +---------------------+    +---------------------+     +--------------------+   |
+-----------------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------------+
|                          MANAGER WATCHDOG AGENT (Every 2-3h)                       |
|  - Health checks & heartbeat monitoring                                           |
|  - Deadlock & circular review resolution                                          |
|  - Orphan worktree & lock cleanup                                                 |
|  - Human escalation alerts                                                        |
+-----------------------------------------------------------------------------------+
                                    |
                                    v
+-----------------------------------------------------------------------------------+
|                             STAGING & DEPLOYMENT                                  |
|  - Continuous Integration (CI) Green Gate                                         |
|  - Automatic Deployment to Staging Environment                                    |
|  - Human Intent Verification Loop                                                 |
|  - Production Promotion                                                           |
+-----------------------------------------------------------------------------------+
```

## Architectural Tenets
1. **Bounded Context**: Each agent only has access to the minimal context needed for its role.
2. **Deterministic Governance**: Agents cannot modify their own execution constraints or security policies (`mission.md`, `engineering.md`).
3. **Graceful Degradation**: When an agent hits an unrecoverable edge case (max retries exceeded), the issue is quarantined, the lock released, and the manager alerts the team without stalling other parallel lanes.
