#!/usr/bin/env python3
"""
web_unlocker_fetch.py

Fetch Vimeo JSON metadata using Bright Data Web Unlocker (/request).
Outputs JSON files to ./datasets by default.

Examples:
  export BRIGHTDATA_API_KEY="YOUR_API_KEY_FROM_DASHBOARD"
  python web_unlocker_fetch.py --url "https://vimeo.com/76979871"
  python web_unlocker_fetch.py --url-file vimeo_urls.txt --mode player
  python web_unlocker_fetch.py --url "https://vimeo.com/76979871" --out-dir ./datasets --zone web_unlocker1
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv

REQUEST_API = "https://api.brightdata.com/request"

load_dotenv()


def require_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise SystemExit(f"Missing env {key}. Set it before running.")
    return val


def load_urls(urls: List[str], url_file: Optional[str]) -> List[str]:
    out = list(urls or [])
    if url_file:
        text = Path(url_file).read_text(encoding="utf-8").splitlines()
        out.extend([t.strip() for t in text if t.strip()])
    if not out:
        raise SystemExit("Provide --url or --url-file")
    return out


def parse_vimeo_id(video_url: str) -> str:
    """
    Extracts a Vimeo video id from common URL forms.
    """
    u = video_url.strip()
    # numeric id directly
    if re.fullmatch(r"\d{6,}", u):
        return u
    parsed = urlparse(u)
    parts = [p for p in parsed.path.split("/") if p]
    # /<id> or /video/<id> or /channels/.../<id>
    for p in reversed(parts):
        if re.fullmatch(r"\d{6,}", p):
            return p
    return "unknown"


def build_vimeo_api_url(video_url: str, mode: str) -> str:
    vid = parse_vimeo_id(video_url)
    if mode == "oembed":
        return f"https://vimeo.com/api/oembed.json?url={video_url}"
    if mode == "player":
        if vid == "unknown":
            raise ValueError(f"Could not find a Vimeo video id in: {video_url}")
        return f"https://player.vimeo.com/video/{vid}/config"
    raise ValueError(f"Unsupported mode: {mode}")


def safe_outname(video_url: str, mode: str) -> str:
    vid = parse_vimeo_id(video_url)
    if vid == "unknown":
        # fallback from host + path
        parsed = urlparse(video_url)
        base = f"{parsed.netloc}_{parsed.path.strip('/') or 'root'}"
        base = re.sub(r"[^A-Za-z0-9._-]", "_", base)
        return f"vimeo_{base}_{mode}"
    return f"vimeo_{vid}_{mode}"


def brd_request(api_key: str, zone: str, target_url: str, timeout: int = 90) -> Tuple[int, bytes, str]:
    """
    Calls Bright Data /request and returns (status_code, content_bytes, text_if_any).
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    payload = {"zone": zone, "url": target_url, "format": "json"}

    resp = requests.post(REQUEST_API, headers=headers, json=payload, timeout=timeout)
    content = resp.content or b""
    text = content.decode("utf-8", errors="replace") if content else ""
    return resp.status_code, content, text


def fetch_vimeo_json(api_key: str, zone: str, video_url: str, mode: str) -> Tuple[str, bytes]:
    """
    Returns (effective_mode, content_bytes). If mode='auto', tries player then oembed.
    """
    if mode in ("player", "oembed"):
        api_url = build_vimeo_api_url(video_url, mode)
        status, content, text = brd_request(api_key, zone, api_url)
        if status >= 200 and status < 300 and content:
            return mode, content
        raise RuntimeError(f"{mode} fetch failed (HTTP {status}). Body: {text[:200]}")

    # auto: try player, then oembed
    for m in ("player", "oembed"):
        try:
            api_url = build_vimeo_api_url(video_url, m)
        except Exception:
            continue
        status, content, text = brd_request(api_key, zone, api_url)
        if 200 <= status < 300 and content:
            return m, content
    raise RuntimeError("auto mode: both player and oembed attempts failed or returned empty content")


def main():
    p = argparse.ArgumentParser(description="Fetch Vimeo JSON via Bright Data Web Unlocker (/request).")
    p.add_argument("--url", action="append", help="Vimeo video URL or numeric id. Can be repeated.")
    p.add_argument("--url-file", help="File with Vimeo URLs (one per line).")
    p.add_argument("--zone", default="web_unlocker1", help="Bright Data Web Unlocker zone (default: web_unlocker1)")
    p.add_argument("--mode", default="auto", choices=["auto", "player", "oembed"],
                   help="Endpoint choice: player, oembed, or auto (try player then oembed). Default: auto")
    p.add_argument("--out-dir", default="./datasets", help="Output directory (default: ./datasets)")
    p.add_argument("--api-key-env", default="BRIGHTDATA_API_KEY",
                   help="Env var containing Bright Data API key (default: BRIGHTDATA_API_KEY)")
    p.add_argument("--quiet", action="store_true", help="Minimize console logs")
    args = p.parse_args()

    api_key = require_env(args.api_key_env)
    urls = load_urls(args.url or [], args.url_file)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for u in urls:
        if not args.quiet:
            print(f"Fetching: {u} (mode: {args.mode})")

        try:
            eff_mode, content = fetch_vimeo_json(api_key, args.zone, u, args.mode)
        except Exception as e:
            print(f"ERROR: {u} -> {e}", file=sys.stderr)
            continue

        name = safe_outname(u, eff_mode) + ".json"
        out_path = out_dir / name
        out_path.write_bytes(content)

        # minimal sanity check: ensure it looks like JSON
        try:
            _ = json.loads(content.decode("utf-8", errors="ignore"))
        except Exception:
            print(f"WARNING: Saved response for {u} is not valid JSON (check {out_path}).", file=sys.stderr)

        if not args.quiet:
            print(f"Saved {len(content)} bytes to {out_path}")

    if not args.quiet:
        print("Done.")


if __name__ == "__main__":
    main()
