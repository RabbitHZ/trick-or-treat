# No Posting Without Approval

## Rule

**Under no circumstances should anything be posted to Threads without explicit user approval.**

## Approval Flow

1. `/scrape` → saves results to `memory/pending.json`
2. `/review` → user approves items → saved to `memory/approved.json`
3. `/post` → only items in `approved.json` may be posted

## Validation

- `poster-agent` checks for the existence of `approved.json` and item inclusion before posting
- `hooks/pre-post.sh` performs a second independent validation of approval status
- On validation failure: stop immediately and log the error

## No Exceptions

- The scheduler cannot bypass this rule
- Never write code that skips the approval step
