# /scrape

Collect the latest dev/IT news from Reddit, Hacker News, and Dev.to.

## Behavior

1. Invoke `scraper-agent` for each source
2. Apply deduplication against `memory/posted.json`
3. Apply quality filters (score, date, language)
4. Save results to `memory/pending.json`
5. Print a collection summary

## Options

- `--source reddit|hn|devto` — collect from a specific source only
- `--limit N` — max items per source (default: 10)
