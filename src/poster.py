import os
import time
import random
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

THREADS_USER_ID = os.getenv("THREADS_USER_ID", "")
THREADS_ACCESS_TOKEN = os.getenv("THREADS_ACCESS_TOKEN", "")
DAILY_POST_LIMIT = int(os.getenv("DAILY_POST_LIMIT", "3"))
POST_DELAY_MIN = int(os.getenv("POST_DELAY_MIN", "30"))
POST_DELAY_MAX = int(os.getenv("POST_DELAY_MAX", "120"))

GRAPH_API = "https://graph.threads.net/v1.0"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _create_container(text: str) -> str:
    resp = requests.post(
        f"{GRAPH_API}/{THREADS_USER_ID}/threads",
        data={
            "media_type": "TEXT",
            "text": text,
            "access_token": THREADS_ACCESS_TOKEN,
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def _publish_container(container_id: str) -> str:
    resp = requests.post(
        f"{GRAPH_API}/{THREADS_USER_ID}/threads_publish",
        data={
            "creation_id": container_id,
            "access_token": THREADS_ACCESS_TOKEN,
        },
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()["id"]


def post_item(item: dict) -> dict:
    text = item["formatted"]
    container_id = _create_container(text)
    time.sleep(5)
    thread_id = _publish_container(container_id)
    return {**item, "thread_id": thread_id, "posted_at": _now()}


def post_items(items: list[dict], today_count: int = 0) -> list[dict]:
    posted = []
    for item in items:
        if today_count + len(posted) >= DAILY_POST_LIMIT:
            print(f"[poster] Daily limit ({DAILY_POST_LIMIT}) reached. Stopping.")
            break
        try:
            result = post_item(item)
            posted.append(result)
            print(f"[poster] Posted: {item['title'][:60]}")
        except Exception as e:
            print(f"[poster] Failed to post '{item['title'][:40]}': {e}")

        if len(posted) < len(items):
            delay = random.randint(POST_DELAY_MIN, POST_DELAY_MAX)
            time.sleep(delay)

    return posted
