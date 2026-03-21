# /status

Display the current state of the pipeline.

## Behavior

1. Check all files in `memory/`
2. Show today's post count and last post time
3. Show pending and approved item counts
4. Show last scrape time per source
5. Show remaining Threads API rate limit

## Example Output

```
=== trick-or-treat status ===
Last scrape : 2026-03-21 14:30
Pending     : 5  |  Approved: 2
Posted today: 3 / 10
Last post   : 2026-03-21 13:00  (next available: 14:30~)
```
