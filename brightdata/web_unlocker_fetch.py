

import argparse
import html
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


# -----------------------------
# Helpers
# -----------------------------
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
    u = video_url.strip()
    if re.fullmatch(r"\d{6,}", u):
        return u
    parsed = urlparse(u)
    parts = [p for p in parsed.path.split("/") if p]
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
        parsed = urlparse(video_url)
        base = f"{parsed.netloc}_{parsed.path.strip('/') or 'root'}"
        base = re.sub(r"[^A-Za-z0-9._-]", "_", base)
        return f"vimeo_{base}_{mode}"
    return f"vimeo_{vid}_{mode}"


def brd_request(api_key: str, zone: str, target_url: str, timeout: int = 90) -> Tuple[int, bytes, str]:
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


def fetch_vimeo_json(api_key: str, zone: str, video_url: str, mode: str) -> Tuple[str, dict]:
    """
    Returns (effective_mode, parsed_json). If mode='auto', tries player then oembed.
    Raises RuntimeError on failure.
    """
    if mode in ("player", "oembed"):
        api_url = build_vimeo_api_url(video_url, mode)
        status, content, text = brd_request(api_key, zone, api_url)
        if 200 <= status < 300 and content:
            try:
                return mode, json.loads(content.decode("utf-8", errors="ignore"))
            except Exception as e:
                raise RuntimeError(f"{mode} JSON parse failed: {e}. Body head: {text[:200]}")
        raise RuntimeError(f"{mode} fetch failed (HTTP {status}). Body: {text[:200]}")

    # auto
    for m in ("player", "oembed"):
        try:
            api_url = build_vimeo_api_url(video_url, m)
        except Exception:
            continue
        status, content, text = brd_request(api_key, zone, api_url)
        if 200 <= status < 300 and content:
            try:
                return m, json.loads(content.decode("utf-8", errors="ignore"))
            except Exception:
                continue
    raise RuntimeError("auto mode: both player and oembed attempts failed or returned invalid JSON")


# -----------------------------
# Normalization
# -----------------------------
def _first_or_none(d: dict, keys: List[str]) -> Optional[str]:
    for k in keys:
        v = d.get(k)
        if v:
            return v
    return None


def _pick_thumb_from_player(data: dict) -> Optional[str]:
    thumbs = data.get("video", {}).get("thumbs") or {}
    if isinstance(thumbs, dict) and thumbs:
        try:
            candidates = sorted(thumbs.items(), key=lambda kv: float(kv[0]), reverse=True)
        except Exception:
            candidates = list(thumbs.items())
        return candidates[0][1]
    sizes = data.get("video", {}).get("pictures", {}).get("sizes", [])
    if isinstance(sizes, list) and sizes:
        return sizes[-1].get("link")
    return None


def normalize_vimeo_json(mode: str, raw: dict, url: str) -> dict:
    if mode == "oembed":
        title = _first_or_none(raw, ["title"])
        desc = _first_or_none(raw, ["description"])
        thumb = _first_or_none(raw, ["thumbnail_url", "thumbnail_url_with_play_button"])
        return {
            "source": "brightdata:web_unlocker:oembed",
            "url": url,
            "title": html.unescape(title or "").strip(),
            "description": html.unescape((desc or "").strip()),
            "thumbnail": thumb,
        }
    # mode == "player"
    video = raw.get("video", {})
    title = _first_or_none(video, ["title", "name"])
    desc = _first_or_none(video, ["description"])
    thumb = _pick_thumb_from_player(raw)
    return {
        "source": "brightdata:web_unlocker:player",
        "url": url,
        "title": html.unescape(title or "").strip(),
        "description": html.unescape((desc or "").strip()),
        "thumbnail": thumb,
    }


# -----------------------------
# CLI
# -----------------------------
def main():
    p = argparse.ArgumentParser(description="Fetch Vimeo JSON via Bright Data Web Unlocker and normalize it.")
    p.add_argument("--url", action="append", help="Vimeo video URL or numeric id. Can be repeated.")
    p.add_argument("--url-file", help="File with Vimeo URLs (one per line).")
    p.add_argument("--zone", default="web_unlocker1", help="Web Unlocker zone (default: web_unlocker1)")
    p.add_argument("--mode", default="auto", choices=["auto", "player", "oembed"],
                   help="Endpoint choice: player, oembed, or auto (default: auto)")
    p.add_argument("--out-dir", default="./datasets", help="Output directory (default: ./datasets)")
    p.add_argument("--api-key-env", default="BRIGHTDATA_API_KEY",
                   help="Env var with API key (default: BRIGHTDATA_API_KEY)")
    p.add_argument("--save-raw", action="store_true",
                   help="Also save original API response to ./datasets/raw/<name>.raw.json")
    p.add_argument("--quiet", action="store_true", help="Minimize console logs")
    args = p.parse_args()

    api_key = require_env(args.api_key_env)
    urls = load_urls(args.url or [], args.url_file)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / "raw"
    if args.save_raw:
        raw_dir.mkdir(parents=True, exist_ok=True)

    for u in urls:
        if not args.quiet:
            print(f"Fetching: {u} (mode: {args.mode}, zone: {args.zone})")

        try:
            eff_mode, raw_json = fetch_vimeo_json(api_key, args.zone, u, args.mode)
            normalized = normalize_vimeo_json(eff_mode, raw_json, u)
        except Exception as e:
            print(f"ERROR: {u} -> {e}", file=sys.stderr)
            continue

        # Save normalized
        name = safe_outname(u, eff_mode) + ".json"
        out_path = out_dir / name
        out_path.write_text(json.dumps(normalized, ensure_ascii=False, indent=2), encoding="utf-8")

        # Optionally save raw
        if args.save_raw:
            (raw_dir / (safe_outname(u, eff_mode) + ".raw.json")).write_text(
                json.dumps(raw_json, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        if not args.quiet:
            print(f"Saved normalized JSON to {out_path}")

    if not args.quiet:
        print("Done.")


if __name__ == "__main__":
    main()
