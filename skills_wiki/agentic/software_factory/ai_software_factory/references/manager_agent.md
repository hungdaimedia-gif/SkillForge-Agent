# The Manager Watchdog Agent

## Purpose & Motivation
In an autonomous multi-agent environment with 10–20 parallel worktrees, agents work in isolation. Without a global observer:
- Deadlocks occur when dependent tasks stall.
- Crashed or timed-out worker containers leave stale git locks.
- Builder and Reviewer agents can enter circular review debates ("fix this" vs "already fixed").
- Unmonitored failures waste API tokens in endless repair loops.

The **Manager Agent** is the meta-supervisor running on a recurring cadence (every 60–180 minutes) that surveys the holistic health of the factory.

## Watchdog Runbook & Tasks
1. **Heartbeat & Zombie Detection**:
   - Inspects all active worktree directories. If a worker process has had no I/O for > 30 minutes, terminate the process, unlock the branch, and reset the ticket label to `status:ready`.
2. **Retry Budget Audit**:
   - Checks the attempt counter on active PRs. If attempt count >= 3, flag the ticket as `status:stalled`, remove it from active queue, and compile a diagnostic bundle.
3. **Dependency Unblocking**:
   - When PR #101 merges into `staging`, find all tickets with `blocked-by:#101` and update them to `status:ready` for immediate worker claiming.
4. **Human Escalation**:
   - Generates an actionable markdown notification to the developer (via Slack, Discord, or IDE notification) summarizing:
     - Number of tickets merged to Staging in the cycle.
     - Blocked tickets requiring human clarification.
     - Token spend & lap duration statistics.
