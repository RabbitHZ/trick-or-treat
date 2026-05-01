# trick-or-treat

A CLI agent that collects dev/IT news from Reddit, Hacker News, and Dev.to, and automatically posts curated content to Meta Threads.

## Project Structure

```
trick-or-treat/
├── CLAUDE.md
├── agents/          # Sub-agent definitions
├── rules/           # Always-applied constraints
├── hooks/           # Event-driven hook scripts
├── prompts/         # Reusable prompt templates
├── memory/          # Agent memory (post history, state)
├── tests/           # Test suite
└── .claude/
    ├── commands/    # Custom slash commands (/scrape, /review, /post, /status)
    └── settings.json
```

## Pipeline

```
[Scrape] → [Filter] → [Format] → [Approve] → [Post]
Reddit/HN/Dev.to   dedupe/quality   Threads format   CLI review   Meta Threads
```

## Sources

- **Reddit** - r/programming, r/webdev, r/devops, etc.
- **Hacker News** - Top stories via official API
- **Dev.to** - Latest dev articles

## Posting Target

- **Meta Threads** - Approved items only

## Tech Stack

- Python 3.11+
- Scheduling: APScheduler or cron
- Storage: SQLite (post history, deduplication)
- Threads API: Meta Graph API

## Prompt Handling Rule

For every prompt entered — whether in Korean or English — first rewrite it into proper English before proceeding.

- If the prompt is in **Korean**: translate it into natural, well-structured English, then proceed with the translated version.
- If the prompt is in **English**: point out any grammatical errors and suggest improvements to make the sentence more natural, then proceed with the polished version.

Always show the rewritten English prompt before executing the task.

## Git Commit Rules

Always prefix commit messages with a Conventional Commits type:

| Type | When to use |
|---|---|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `chore` | Config, tooling, or non-code changes |
| `docs` | Documentation only |
| `refactor` | Code restructuring without behavior change |
| `test` | Adding or updating tests |
| `ci` | CI/CD pipeline changes |

Format: `<type>: <short description in lowercase>`

Example: `feat: add Reddit scraper with deduplication`

Do not include the Claude co-author line in the commit message.

```
# Do NOT include this:
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

## Token Optimization Rules

### Response Style
- Be concise. Skip preamble, summaries, and filler phrases.
- Never restate what was just done — lead with the result.
- Prefer bullet points over prose for lists of items.

### File Reading
- Read only the specific lines needed, not entire files.
- Use `offset` and `limit` parameters when reading large files.
- Before reading, check if the answer can be derived from already-visible context.

### Tool Use
- Prefer `Grep` and `Glob` over `Read` for locating code.
- Run independent tool calls in parallel, not sequentially.
- Avoid re-reading files already read in the current session.

### Agent & Subagent Use
- Only spawn subagents for tasks that genuinely benefit from isolation.
- Do not delegate simple searches to agents — use Grep/Glob directly.

### Code Generation
- Do not add comments, docstrings, or type hints to unchanged code.
- Do not generate example usage, README snippets, or boilerplate unless asked.
- Do not output code that was not modified.

### Scraping & Data Handling
- Fetch only required fields from APIs (title, url, score — not full metadata).
- Limit scrape results to the top N items (default: 10 per source).
- Skip items already in SQLite history before any further processing.

## Core Rules

- Always follow all rules defined in the `rules/` directory
- Never post without explicit user approval
- Always check `rules/threads-safety.md` before any posting action

<!-- code-review-graph MCP tools -->
## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes` or `query_graph` instead of Grep
- **Understanding impact**: `get_impact_radius` instead of manually tracing imports
- **Code review**: `detect_changes` + `get_review_context` instead of reading entire files
- **Finding relationships**: `query_graph` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview` + `list_communities`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
|------|----------|
| `detect_changes` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context` | Need source snippets for review — token-efficient |
| `get_impact_radius` | Understanding blast radius of a change |
| `get_affected_flows` | Finding which execution paths are impacted |
| `query_graph` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes` | Finding functions/classes by name or keyword |
| `get_architecture_overview` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes` for code review.
3. Use `get_affected_flows` to understand impact.
4. Use `query_graph` pattern="tests_for" to check coverage.
