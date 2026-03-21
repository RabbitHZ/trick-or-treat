# trick-or-treat

A CLI agent that automatically collects dev/IT news from Reddit, Hacker News, and Dev.to, and posts curated content to Meta Threads — with human-in-the-loop approval before every post.

## Features

- Scrapes top dev/IT news from 3 sources (Reddit, Hacker News, Dev.to)
- Filters out duplicates and low-quality content automatically
- Formats posts to fit Threads' style and character limit
- **Requires manual approval before posting** — nothing goes live without you
- Human-like random delays between posts to avoid account restrictions
- Scheduled auto-runs with daily posting limits

## Pipeline

```
[Scrape] → [Filter] → [Format] → [Approve] → [Post]
Reddit       dedupe     Threads    CLI review   Meta Threads
HN           quality    format     (you)
Dev.to       filter
```

## Project Structure

```
trick-or-treat/
├── CLAUDE.md              # Project context & AI behavior rules
├── README.md
├── commands/              # Custom slash commands
│   ├── scrape.md          # /scrape — collect news
│   ├── review.md          # /review — approve/reject items
│   ├── post.md            # /post — post to Threads
│   └── status.md          # /status — pipeline status
├── agents/                # Sub-agent definitions
│   ├── scraper-agent.md
│   ├── filter-agent.md
│   ├── formatter-agent.md
│   └── poster-agent.md
├── rules/                 # Always-applied constraints
│   ├── python-style.md
│   ├── no-post-without-approval.md
│   ├── api-safety.md
│   └── threads-safety.md
├── hooks/                 # Event-driven shell hooks
│   ├── pre-post.sh        # Validates before every post
│   ├── post-scrape.sh     # Logs after scraping
│   └── on-approval.sh     # Triggers after approval
├── prompts/               # Reusable prompt templates
│   ├── summarize.md       # News summarization prompt
│   └── threads-tone.md    # Tone & style guide
├── memory/                # Agent memory (post history, state)
├── tests/                 # Test suite
└── .claude/
    └── settings.json      # Hook bindings & Claude settings
```

## Setup

### 1. Clone & install dependencies

```bash
git clone https://github.com/RabbitHZ/trick-or-treat.git
cd trick-or-treat
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
# Fill in your API keys
```

Required keys in `.env`:

```
REDDIT_CLIENT_ID=
REDDIT_CLIENT_SECRET=
REDDIT_USER_AGENT=
DEVTO_API_KEY=
THREADS_API_KEY=
THREADS_USER_ID=
```

### 3. Run

```bash
# Collect news
python main.py scrape

# Review & approve
python main.py review

# Post approved items to Threads
python main.py post

# Check pipeline status
python main.py status
```

## Slash Commands (Claude Code)

| Command | Description |
|---------|-------------|
| `/scrape` | Collect latest news from all sources |
| `/review` | Interactively approve or reject pending items |
| `/post` | Post approved items to Threads |
| `/status` | Show current pipeline state |

## Safety

- **No post without approval** — the approval step cannot be bypassed
- **Pre-post hook** verifies approval status, API keys, and daily limits before every post
- **Human-like delays** — random 30min~2hr gaps between posts
- **Daily limit** — max 10 posts per day to avoid Threads restrictions
- API keys are never hardcoded — always loaded from `.env`

## Sources

| Source | Criteria |
|--------|----------|
| Reddit | score ≥ 100, within 24h |
| Hacker News | score ≥ 50, within 48h |
| Dev.to | reactions ≥ 20, within 72h |

## Tech Stack

- **Python 3.11+**
- **PRAW** — Reddit API
- **requests** — HN & Dev.to API
- **APScheduler** — scheduled runs
- **SQLite** — post history & deduplication
- **Meta Graph API** — Threads posting
