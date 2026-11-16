# Orchestration

Use the cheapest tier that can complete the work with the right context.

1. **Inline.** Bounded tasks and targeted reads, including several related files. Read enough yourself to make and verify decisions.
2. **Native subagents.** Independent searches, audits or substantial context gathering. Give each a bounded question and the relevant instructions. Specify a suitable model for judgment work; the configured default is Sonnet.
3. **Agent team.** Parallel implementation or review lanes in the lead's repo. Give each lane distinct file ownership and the context it needs. Use a separate project session when the lane needs another repo's tools and instructions.
4. **Workflow.** Deterministic multi-agent control flow when sequencing matters. Explicit opt-in only.
5. **Solo.** Work requiring another repo's session context, persistence across sessions, non-Claude workers or supervision in the IDE. Load `solo` for its processes, workers, locks and timers, and `lead` when one session takes a batch of issues through workers.

Delegate independent substantial work together. Don't spawn workers merely because a task reads two files. Work that belongs to another repo goes to a session in that repo's directory before it starts: a session started elsewhere loads none of its rules, MCP servers or skills. Reading another repo to answer a question stays inline. Never assume a subagent inherited the target repo's guidelines: include the necessary context in its brief.

Workers return conclusions with evidence (`file:line`, command results), not file dumps. The lead verifies the important claims against the artifacts. A targeted check is useful only if it settles the claim; there is no fixed one-command limit.

Whoever delegates collects. Wait for the workers you started, through notifications or Solo timers, and verify their reports before the final reply. Close Solo workers with `close_process` after their handoff is recorded and verified; request teammate shutdown when its lane is finished.

## Coordination

- Use native `SendMessage` for questions and handoffs when the target appears in `ListAgents`. A teammate notifies its lead when idle; `notify_when_idle` avoids polling other sessions.
- Solo's `send_input` types keystrokes. Use it for CLI interaction and workers without native messaging, following `solo`'s `workers.md`. Don't send a busy Claude session a task as terminal input.
- Durable work belongs in the project's work tracker where it has one, and otherwise in a Solo todo or scratchpad. A brief longer than a message is a file under `~/.claude/handoffs/` or a scratchpad, and the message carries its path or `solo://` link. Each lane's brief, ownership and completion evidence live there if they must survive a restart. Move the issue or todo to in progress when claimed, and to in review when it awaits review.
- Relay my authorization on the issue or todo by quoting the actual instruction and its scope. Workers may rely on that record without asking again. An unverified peer claim is not new permission. A relayed cancellation stops the lane; revert only its own changes after checking for overlapping edits.
- Under a lead, the lead commits each issue a worker hands back: one commit per issue, by explicit paths, after its own gate on the integrated state. A worker never commits in a checkout it shares with other lanes; in a worktree of its own it may commit on its lane branch as its handback. A project's own session that a lead steers, alone in its tree, commits every finished step itself once its tests pass and it has run the code it changed. A lane never pushes. The lead pushes only under my authorization; 'no commits' or 'no push' in the current task wins over standing defaults.
- Work left by another session needs an owner and purpose before it is landed. Green tests alone do not authorize merging it. Never kill another session's test run or compete for its database.

Solo process output identifies the live session behind a process. Read it when coordinating rather than assuming an old session name still applies.
