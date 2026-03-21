# /review

Interactively review collected news items and approve or reject each one via CLI.

## Behavior

1. Load items from `memory/pending.json`
2. Display each item one by one (title, summary, source URL, formatted Threads post preview)
3. Accept user input: `y` approve / `n` reject / `e` edit / `q` quit
4. Approved items → `memory/approved.json`
5. Rejected items → `memory/rejected.json`
6. Run `hooks/on-approval.sh` after session ends

## Notes

- Posting is blocked without approval
- `hooks/pre-post.sh` performs a second validation of approval status before every post
