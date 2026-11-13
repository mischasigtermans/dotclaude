# Second opinions

Four channels. Reach for them unprompted when the work matches.

- **Persona review loop.** Before committing non-trivial Laravel work: taylor-otwell reviews the diff, taylor fixes its own findings, then a fresh taylor pass reviews the fixes. Never skip the second pass. Same shape with david-tolnay for Rust, raymond-hettinger for Python, steve-jobs for product and UX calls.
- **Parley peer consult.** When a change makes claims in another project's domain, ask that project as a peer. The peer holds the domain context, the asking session holds the change.
- **Parley gathering.** At an architecture fork, or when the question is whether the approach itself is right, gather 2-3 personas in one Parley room (`parley_gather`) instead of asking them one by one. Round 1 is blind, later rounds let each advisor answer the others, and the room converges when everyone passes. When the question is about a codebase, add that project as grounder: it checks the advisors' factual claims against its own code before they argue. One persona's taste is a data point; a room of differently-flavoured advisors that converges is signal. Report where they agreed, where they split and why, then your own read.
- **Panel of agents.** When several agents write one report together, it's final only when every one of them signs it without reservation. A disagreement that survives stands in the report as contested, with both sides in words each side would sign, never as a dissent footnote.

Every review question carries the same gates, verbatim in the ask:

- Report a finding only above 80% confidence.
- Each finding cites the exact line, names the input and the bad outcome, and was checked against the callers and tests.
- Defend the severity. A style preference is not a bug.
- Zero findings is a valid review. Don't manufacture findings to look rigorous.

A forked session isn't registered with parley: every `parley_ask` fails and only a restart fixes it. There, run the review as an Opus subagent primed with the persona's knowledge modules (`~/.claude/plugins/cache/by-mischa/<persona>/*/skills/search-knowledge/`) and say the real persona was unreachable. When the opinion is load-bearing, ask me to run it from an unforked session.

Another model's output (Codex, Grok, a persona, a subagent) is a lead, not a finding. Re-run its numbers, paths, line references and 'still true on HEAD' verdicts before they enter a plan or a doc, and say which parts you verified.

Personas and peer consults both route through parley, so plugin usage counters under-report them. Don't read a zero there as disuse.
