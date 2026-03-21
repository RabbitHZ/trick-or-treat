# scraper-agent

## Role

Dedicated agent for collecting dev/IT news from Reddit, Hacker News, and Dev.to.

## Responsibilities

- Call each source API and parse responses
- Normalize raw data into a unified format (title, URL, summary, score, date)
- Pass results to `filter-agent`
- Retry on failure and log errors

## Tools

- Reddit API (PRAW)
- Hacker News API (official Firebase API)
- Dev.to API

## Output Format

```json
{
  "source": "reddit|hn|devto",
  "title": "...",
  "url": "...",
  "summary": "...",
  "score": 0,
  "collected_at": "ISO8601"
}
```

## Constraints

- Always read API keys from environment variables — never hardcode
- Stop immediately and return an error on rate limit exceeded
