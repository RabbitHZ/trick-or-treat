# API Safety Rules

## API Key Management

- All API keys must be stored in `.env` only
- Never commit `.env` to git — always include in `.gitignore`
- Only key names (no values) go in `.env.example`

## Rate Limits

- Explicitly enforce each API's official rate limits in code
- On rate limit response (429): stop immediately, do not retry
- Minimum 1-second gap between requests per source

## Error Handling

- On API failure: retry up to 3 times with exponential backoff
- After 3 failures: skip that source and log the error
- On auth errors (401, 403): stop immediately, do not retry

## References

- Reddit API: https://www.reddit.com/dev/api
- HN API: https://github.com/HackerNews/API
- Dev.to API: https://developers.forem.com/api
- Threads API: always check the latest Meta Graph API documentation before implementation
