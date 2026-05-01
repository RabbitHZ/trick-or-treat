import os
import sys
import logging
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

load_dotenv()

from src.main import cmd_scrape, cmd_format

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

LOCKFILE = Path("/tmp/trick-scheduler.lock")

SCRAPE_INTERVAL_HOURS = int(os.getenv("SCRAPE_INTERVAL_HOURS", "6"))


def job_scrape_and_format():
    log.info("=== scheduled run start ===")
    try:
        cmd_scrape()
        cmd_format()
        log.info("=== scheduled run done — review pending.json to approve items ===")
    except Exception as e:
        log.error("scheduled run failed: %s", e, exc_info=True)


def _acquire_lock() -> bool:
    if LOCKFILE.exists():
        pid = LOCKFILE.read_text().strip()
        try:
            os.kill(int(pid), 0)  # check if process is alive
            return False  # still running
        except (ProcessLookupError, ValueError):
            pass  # stale lock
    LOCKFILE.write_text(str(os.getpid()))
    return True


def _release_lock():
    try:
        LOCKFILE.unlink()
    except FileNotFoundError:
        pass


def main():
    if not _acquire_lock():
        log.error("another scheduler instance is already running (lock: %s). exiting.", LOCKFILE)
        sys.exit(1)

    scheduler = BlockingScheduler(timezone="UTC")
    trigger = IntervalTrigger(hours=SCRAPE_INTERVAL_HOURS)
    scheduler.add_job(
        job_scrape_and_format,
        trigger=trigger,
        id="scrape_and_format",
        next_run_time=datetime.now(timezone.utc),  # run immediately on start
    )
    log.info(
        "scheduler started — scrape+format every %d hour(s). Ctrl-C to stop.",
        SCRAPE_INTERVAL_HOURS,
    )
    log.info("NOTE: posting requires manual approval via `python -m src.main review`")
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        log.info("scheduler stopped.")
    finally:
        _release_lock()


if __name__ == "__main__":
    main()