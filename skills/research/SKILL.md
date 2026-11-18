---
name: research
description: "Research a topic across the web and X: recent facts, primary sources, who is saying what, and the counterpoints, each finding with its URL and date. Uses the Firecrawl MCP for the web and the X MCP for posts, people and news on X. Triggers on 'research', 'find sources on', 'what's recent on', 'what are people saying about', 'what's the discourse on', 'zoek uit', 'onderzoek', 'wat zeggen mensen over', 'bronnen voor'. For a long narrative report across many sources, the deep-research skill coordinates the same tools at larger scale."
---

# Research

Find what's true and what's being said about a topic, with every claim traceable to a source a reader can open.

## Sources

| Source | Tools | Good for |
| --- | --- | --- |
| Web | The Firecrawl MCP: `firecrawl_search`, `firecrawl_scrape`, the research-paper and developer indexes | Primary sources, docs, announcements, numbers, papers |
| X | The X MCP (server `xapi`): post search, user lookup, a user's posts, news and trends | What builders and the people involved say, reactions, first-hand reports, timing |

Check which are connected before you plan. Without the X MCP, say so in one line and work from the web alone; never fill the X side from memory. Setting it up is in this skill's `x-setup.md`.

X reads cost money on X's pay-per-use plan. Keep X queries targeted: a handle, a phrase, a date range, a small result count. Report how many posts you read.

## Workflow

1. **Frame the question.** One sentence: what the reader needs to know and for what. Split a broad topic into two to four angles. A narrow question gets one pass, no split.
2. **Web first for facts.** Search, then open the pages that carry the claim: the announcement, the docs, the paper, the filing. A number is taken from its primary source or marked as secondhand.
3. **X for voices and signals.** Search the phrase and the people at the centre of it. Read threads, not single posts, when the point spans several. An X post is evidence that someone said something, on a date. It's proof of a fact only when the person is the primary source (a founder announcing their own release).
4. **Cross-check.** A claim from one source gets a second, or is marked single-source. Where sources disagree, keep both and say which is primary.
5. **Parallel lanes for broad topics.** When there are three or more angles, give each a subagent with its angle, the tools to use and the output shape below, and merge their notes. A narrow question stays inline.

## Output

```
## Key facts
1. <fact> (<source title>, <URL>, <date>)

## Voices
- <@handle or name>, <role>: '<quote, verbatim>' (<post URL>, <date>)

## Counterpoints
- <the strongest disagreement, with source>

## Open questions
- <what the sources don't settle>

Sources read: <n> pages, <n> X posts.
```

Write to a file only when asked, or when the notes feed other work (a draft, a plan); say where.

## Never

- A URL you didn't open, or a quote you didn't read verbatim.
- An X post without its URL and date.
- Engagement (likes, reposts, followers) as evidence that a claim is true.
- A fact from memory presented as found.
