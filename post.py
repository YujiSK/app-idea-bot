import csv
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import requests


POSTS_FILE = Path("posts.csv")
MAX_POST_LENGTH = 280


@dataclass
class Post:
    post_id: str
    text: str


def load_next_post(path: Path) -> Post:
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")

    with path.open(newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            post_id = (row.get("id") or "").strip()
            text = (row.get("text") or "").strip()
            enabled = (row.get("enabled") or "true").strip().lower()
            if enabled in {"true", "1", "yes"} and post_id and text:
                return Post(post_id=post_id, text=text)

    raise RuntimeError("No enabled post found in posts.csv")


def require_env(names: Iterable[str]) -> dict[str, str]:
    values = {name: os.environ.get(name, "").strip() for name in names}
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")
    return values


def has_env(names: Iterable[str]) -> bool:
    return all(os.environ.get(name, "").strip() for name in names)


def post_to_bluesky(text: str) -> None:
    env = require_env(["BLUESKY_HANDLE", "BLUESKY_APP_PASSWORD"])
    session = requests.Session()
    login_response = session.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": env["BLUESKY_HANDLE"], "password": env["BLUESKY_APP_PASSWORD"]},
        timeout=20,
    )
    login_response.raise_for_status()
    access_jwt = login_response.json()["accessJwt"]
    did = login_response.json()["did"]

    post_response = session.post(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {access_jwt}"},
        json={
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": text,
                "createdAt": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat().replace("+00:00", "Z"),
            },
        },
        timeout=20,
    )
    post_response.raise_for_status()


def post_to_mastodon(text: str) -> None:
    env = require_env(["MASTODON_INSTANCE_URL", "MASTODON_ACCESS_TOKEN"])
    instance_url = env["MASTODON_INSTANCE_URL"].rstrip("/")
    response = requests.post(
        f"{instance_url}/api/v1/statuses",
        headers={"Authorization": f"Bearer {env['MASTODON_ACCESS_TOKEN']}"},
        data={"status": text, "visibility": os.environ.get("MASTODON_VISIBILITY", "public")},
        timeout=20,
    )
    response.raise_for_status()


def main() -> int:
    post = load_next_post(POSTS_FILE)
    if len(post.text) > MAX_POST_LENGTH:
        raise RuntimeError(f"Post {post.post_id} is {len(post.text)} chars; max is {MAX_POST_LENGTH}")

    dry_run = os.environ.get("DRY_RUN", "false").strip().lower() in {"true", "1", "yes"}
    targets = [target.strip().lower() for target in os.environ.get("POST_TARGETS", "bluesky,mastodon").split(",") if target.strip()]

    print(f"Selected post: {post.post_id}")
    print(post.text)

    available_targets = []
    skipped_targets = []

    if "bluesky" in targets:
        if has_env(["BLUESKY_HANDLE", "BLUESKY_APP_PASSWORD"]):
            available_targets.append("bluesky")
        else:
            skipped_targets.append("bluesky: missing BLUESKY_HANDLE or BLUESKY_APP_PASSWORD")

    if "mastodon" in targets:
        if has_env(["MASTODON_INSTANCE_URL", "MASTODON_ACCESS_TOKEN"]):
            available_targets.append("mastodon")
        else:
            skipped_targets.append("mastodon: missing MASTODON_INSTANCE_URL or MASTODON_ACCESS_TOKEN")

    for skipped in skipped_targets:
        print(f"Skipping {skipped}")

    if not available_targets:
        print("No configured targets are available. Nothing to post.")
        return 0

    if dry_run:
        print(f"DRY_RUN=true; would post to: {', '.join(available_targets)}")
        print("No external API calls were made.")
        return 0

    if "bluesky" in available_targets:
        post_to_bluesky(post.text)
        print("Posted to Bluesky.")

    if "mastodon" in available_targets:
        post_to_mastodon(post.text)
        print("Posted to Mastodon.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
