import os
import sys
import json
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from src.db import init_db, mark_posted, log_scrape, get_last_scrape, get_today_post_count
from src.scraper import scrape_all, scrape_hn, scrape_devto, scrape_reddit
from src.filter import filter_items
from src.formatter import format_items
from src.poster import post_items

MEMORY_DIR = Path(__file__).parent.parent / "memory"
PENDING_FILE = MEMORY_DIR / "pending.json"
APPROVED_FILE = MEMORY_DIR / "approved.json"
REJECTED_FILE = MEMORY_DIR / "rejected.json"
POSTED_FILE = MEMORY_DIR / "posted.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _load_json(path: Path) -> list:
    if path.exists():
        return json.loads(path.read_text())
    return []


def _save_json(path: Path, data: list):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))


def cmd_scrape(source=None, limit: int = None):
    limit = limit or int(os.getenv("SCRAPE_LIMIT", 10))
    init_db()
    if source == "hn":
        raw = scrape_hn(limit)
    elif source == "devto":
        raw = scrape_devto(limit)
    elif source == "reddit":
        raw = scrape_reddit(limit)
    else:
        raw = scrape_all(limit)

    filtered = filter_items(raw)
    _save_json(PENDING_FILE, filtered)

    scraped_at = _now()
    log_scrape(source or "all", scraped_at, len(filtered))

    print(f"[scrape] Collected {len(raw)} items → {len(filtered)} after filtering")
    print(f"[scrape] Saved to {PENDING_FILE}")


def cmd_format():
    pending = _load_json(PENDING_FILE)
    if not pending:
        print("[format] No pending items.")
        return

    top = sorted(pending, key=lambda x: x.get("score", 0), reverse=True)[:1]
    formatted = format_items(top)
    _save_json(PENDING_FILE, formatted)
    print(f"[format] Formatted {len(formatted)} items → {PENDING_FILE}")


def cmd_review():
    pending = _load_json(PENDING_FILE)
    if not pending:
        print("[review] No pending items.")
        return

    approved = _load_json(APPROVED_FILE)
    rejected = _load_json(REJECTED_FILE)

    print(f"\n[review] {len(pending)} items to review\n")
    for i, item in enumerate(pending):
        print(f"{'─' * 60}")
        print(f"[{i+1}/{len(pending)}] {item['title']}")
        print(f"Source : {item['source']}  |  Score: {item['score']}")
        print(f"URL    : {item['url']}")
        print(f"\n--- Threads Preview ---\n{item['formatted']}\n")

        while True:
            choice = input("(y)approve / (n)reject / (q)quit: ").strip().lower()
            if choice in ("y", "n", "q"):
                break

        if choice == "y":
            approved.append(item)
            print("✓ Approved")
        elif choice == "n":
            rejected.append(item)
            print("✗ Rejected")
        elif choice == "q":
            print("[review] Quit early.")
            break

    _save_json(APPROVED_FILE, approved)
    _save_json(REJECTED_FILE, rejected)
    _save_json(PENDING_FILE, [])
    print(f"\n[review] Done. Approved: {len(approved)}  Rejected: {len(rejected)}")


def cmd_post():
    approved = _load_json(APPROVED_FILE)
    if not approved:
        print("[post] No approved items.")
        return

    today_count = get_today_post_count(_today())
    posted = post_items(approved, today_count)

    for item in posted:
        mark_posted(item["url"], item["title"], item["source"], item["posted_at"])

    existing_posted = _load_json(POSTED_FILE)
    _save_json(POSTED_FILE, existing_posted + posted)
    _save_json(APPROVED_FILE, [])

    print(f"[post] Posted {len(posted)} items.")


def cmd_status():
    init_db()
    pending = _load_json(PENDING_FILE)
    approved = _load_json(APPROVED_FILE)
    today_count = get_today_post_count(_today())
    posted = _load_json(POSTED_FILE)
    last_post = posted[-1]["posted_at"][:16] if posted else "—"

    print("=== trick-or-treat status ===")
    print(f"Last scrape (HN)    : {get_last_scrape('hn') or '—'}")
    print(f"Last scrape (Dev.to): {get_last_scrape('devto') or '—'}")
    print(f"Last scrape (Reddit): {get_last_scrape('reddit') or '—'}")
    print(f"Pending    : {len(pending)}  |  Approved: {len(approved)}")
    print(f"Posted today: {today_count} / 10")
    print(f"Last post  : {last_post}")


def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python -m src.main <scrape|format|review|post|status> [options]")
        return

    cmd = args[0]

    if cmd == "scrape":
        source = None
        limit = None
        for i, arg in enumerate(args[1:]):
            if arg == "--source" and i + 2 < len(args):
                source = args[i + 2]
            if arg == "--limit" and i + 2 < len(args):
                limit = int(args[i + 2])
        cmd_scrape(source, limit)

    elif cmd == "format":
        cmd_format()

    elif cmd == "review":
        cmd_review()

    elif cmd == "post":
        cmd_post()

    elif cmd == "status":
        cmd_status()

    else:
        print(f"Unknown command: {cmd}")


if __name__ == "__main__":
    main()
