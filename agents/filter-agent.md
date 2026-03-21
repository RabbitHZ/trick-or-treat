# filter-agent

## Role

Evaluate the quality of collected news items and remove duplicates.

## Responsibilities

- Compare against `memory/posted.json` to remove duplicate URLs
- Apply quality filters (score, recency, language)
- Save passing items to `memory/pending.json`

## Filter Criteria

- Reddit: score ≥ 100, within 24h
- Hacker News: score ≥ 50, within 48h
- Dev.to: reactions ≥ 20, within 72h
- Deduplicate by URL and title similarity (≥ 80%)

## Constraints

- Filter thresholds must be configurable via `config`
- Always log filter results
