# /post

Post approved items to Meta Threads.

## Behavior

1. Load items from `memory/approved.json`
2. Run `hooks/pre-post.sh` (validates approval, API key, rate limit, daily limit)
3. Apply random delay between posts (threads-safety rules)
4. Post each item via Threads API
5. Move posted items to `memory/posted.json`
6. Log results via `hooks/post-scrape.sh`

## Notes

- Only items in `approved.json` are eligible for posting
- Stops automatically when daily limit is reached
- Always follow `rules/threads-safety.md`
