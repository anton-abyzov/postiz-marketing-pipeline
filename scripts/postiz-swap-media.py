#!/usr/bin/env python3
"""Swap media on existing Postiz posts in-place.

Reads a list of post IDs and a target media (id + path + name), then for each post:
  1. Fetches existing post body (caption, settings, group, integration, schedule)
  2. POSTs back to /api/posts with `value[0].id = <existing>` and updated `image[]`

Schedule, caption, channel, settings are preserved. Only the `image` array changes.

Usage:
    POSTIZ_BASE_URL=https://postiz.example.com \
    POSTIZ_COOKIE_JAR=/tmp/postiz-cookies.txt \
    python3 postiz-swap-media.py \
        --post-ids cmoxb...001,cmoxb...002 \
        --media-id e841ecba-... \
        --media-path "https://postiz.example.com/uploads/2026/05/09/abc123.mp4" \
        --media-name abc123.mp4 \
        --original-name marcus-demo-45s-v8.mp4
"""
from __future__ import annotations
import argparse
import json
import os
import sys
from urllib.parse import urljoin

try:
    import requests
except ImportError:
    print("requests not installed. pip install requests", file=sys.stderr)
    sys.exit(1)

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def load_cookies(jar_path: str) -> dict:
    """Parse Netscape cookie file and return {name: value} for the auth cookie."""
    cookies = {}
    with open(jar_path, "r") as fh:
        for line in fh:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.strip().split("\t")
            if len(parts) >= 7:
                cookies[parts[5]] = parts[6]
    return cookies


def fetch_post(base_url: str, cookies: dict, post_id: str) -> dict:
    url = urljoin(base_url, f"/api/posts/{post_id}")
    r = requests.get(url, cookies=cookies, headers={"User-Agent": UA, "showorg": "true"})
    r.raise_for_status()
    return r.json()


def swap_media(
    base_url: str,
    cookies: dict,
    post: dict,
    media_id: str,
    media_path: str,
    media_name: str,
    original_name: str,
) -> dict:
    payload = {
        "type": "schedule",
        "date": post["publishDate"],
        "posts": [
            {
                "integration": {"id": post["integration"]["id"]},
                "value": [
                    {
                        "id": post["id"],
                        "content": post["content"],
                        "image": [
                            {
                                "id": media_id,
                                "path": media_path,
                                "name": media_name,
                                "originalName": original_name,
                            }
                        ],
                    }
                ],
                "group": post["group"],
                "settings": post.get("settings", {}),
            }
        ],
        "shortLink": False,
        "tags": [],
    }
    url = urljoin(base_url, "/api/posts")
    r = requests.post(
        url,
        cookies=cookies,
        headers={
            "User-Agent": UA,
            "showorg": "true",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
    )
    r.raise_for_status()
    return r.json()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--post-ids", required=True, help="Comma-separated post IDs")
    ap.add_argument("--media-id", required=True)
    ap.add_argument("--media-path", required=True)
    ap.add_argument("--media-name", required=True)
    ap.add_argument("--original-name", required=True)
    args = ap.parse_args()

    base_url = os.environ.get("POSTIZ_BASE_URL")
    jar = os.environ.get("POSTIZ_COOKIE_JAR", "/tmp/postiz-cookies.txt")
    if not base_url:
        print("POSTIZ_BASE_URL env var required", file=sys.stderr)
        sys.exit(1)

    cookies = load_cookies(jar)
    if "auth" not in cookies:
        print(f"No auth cookie in {jar}. Run postiz-login.sh.", file=sys.stderr)
        sys.exit(1)

    for post_id in args.post_ids.split(","):
        post_id = post_id.strip()
        if not post_id:
            continue
        try:
            post = fetch_post(base_url, cookies, post_id)
        except requests.HTTPError as e:
            print(f"  [skip] {post_id}: fetch failed ({e})", file=sys.stderr)
            continue
        try:
            resp = swap_media(
                base_url,
                cookies,
                post,
                args.media_id,
                args.media_path,
                args.media_name,
                args.original_name,
            )
            print(f"  [ok]   {post_id}: {resp}")
        except requests.HTTPError as e:
            print(f"  [fail] {post_id}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
