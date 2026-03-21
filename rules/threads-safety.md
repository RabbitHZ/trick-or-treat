# Threads Account Safety Rules

## Background

Threads enforces strict policies against automated bots and spammy content.
Posting too frequently or repeating identical content risks account suspension.

## Post Interval (Human-like Delay)

- **Minimum interval**: 30 minutes
- **Maximum interval**: 2 hours
- **Method**: randomized — use `random.uniform(1800, 7200)` seconds
- Never use a fixed interval — varying delays help avoid pattern detection

## Daily Posting Limit

- **Maximum per day**: 10 posts
- Stop automatically when limit is reached; resume the next day
- Track today's count via `memory/posted.json`

## Content Rules

- Never repeat identical or near-identical content
- No hashtag spam — maximum 3 hashtags per post
- Always include the original source link

## API Compliance

- Always check the official Meta Graph API rate limits before implementation
- Respect `retry-after` headers in API responses
- Review Threads API guidelines: https://developers.facebook.com/docs/threads

## Monitoring

- Stop immediately if posting fails in a way that suggests account restriction
- After 3 consecutive failures: pause for 24 hours and alert the user
