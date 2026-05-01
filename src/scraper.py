import os
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "trick-or-treat/1.0")
REDDIT_SUBREDDITS = os.getenv("REDDIT_SUBREDDITS", "programming,webdev,devops").split(",")
DEVTO_API_KEY = os.getenv("DEVTO_API_KEY", "")
def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _limit(default: int = 10) -> int:
    return int(os.getenv("SCRAPE_LIMIT", default))


def scrape_hn(limit: int = None) -> list[dict]:
    limit = limit or _limit()
    top_ids = requests.get(
        "https://hacker-news.firebaseio.com/v0/topstories.json", timeout=10
    ).json()

    items = []
    for story_id in top_ids[:limit * 2]:
        data = requests.get(
            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=10
        ).json()
        if not data or data.get("type") != "story" or not data.get("url"):
            continue
        items.append({
            "title": data.get("title", ""),
            "url": data.get("url", ""),
            "score": data.get("score", 0),
            "source": "hn",
            "scraped_at": _now(),
        })
        if len(items) >= limit:
            break
    return items


def scrape_devto(limit: int = None) -> list[dict]:
    limit = limit or _limit()
    headers = {"api-key": DEVTO_API_KEY} if DEVTO_API_KEY else {}
    resp = requests.get(
        "https://dev.to/api/articles",
        params={"per_page": limit, "top": 1},
        headers=headers,
        timeout=10,
    )
    resp.raise_for_status()

    items = []
    for article in resp.json():
        items.append({
            "title": article.get("title", ""),
            "url": article.get("url", ""),
            "score": article.get("positive_reactions_count", 0),
            "source": "devto",
            "scraped_at": _now(),
        })
    return items


def _fetch_top_comments(permalink: str, headers: dict, limit: int = 5) -> str:
    try:
        resp = requests.get(
            f"https://www.reddit.com{permalink}.json",
            params={"limit": limit, "depth": 1},
            headers=headers,
            timeout=10,
        )
        if resp.status_code != 200:
            return ""
        children = resp.json()[1]["data"]["children"]
        comments = []
        for c in children:
            body = c.get("data", {}).get("body", "")
            if body and body != "[deleted]" and body != "[removed]":
                comments.append(body.strip())
        return "\n\n".join(comments[:limit])
    except Exception:
        return ""


def scrape_reddit(limit: int = None) -> list[dict]:
    limit = limit or _limit()
    per_sub = max(limit, 5)
    headers = {"User-Agent": REDDIT_USER_AGENT}
    items = []

    for subreddit in REDDIT_SUBREDDITS:
        resp = requests.get(
            f"https://www.reddit.com/r/{subreddit.strip()}/rising.json",
            params={"limit": per_sub},
            headers=headers,
            timeout=10,
        )
        if resp.status_code != 200:
            continue
        for post in resp.json().get("data", {}).get("children", []):
            d = post.get("data", {})
            if d.get("is_self") or not d.get("url"):
                continue
            permalink = d.get("permalink", "")
            comments = _fetch_top_comments(permalink, headers) if permalink else ""
            items.append({
                "title": d.get("title", ""),
                "url": d.get("url", ""),
                "score": d.get("score", 0),
                "source": f"reddit/{subreddit.strip()}",
                "comments": comments,
                "scraped_at": _now(),
            })

    return items


def scrape_all(limit: int = None) -> list[dict]:
    limit = limit or _limit()
    results = []
    for fn in (scrape_hn, scrape_devto, scrape_reddit):
        try:
            results.extend(fn(limit))
        except Exception as e:
            print(f"[scraper] {fn.__name__} failed: {e}")
    return results
