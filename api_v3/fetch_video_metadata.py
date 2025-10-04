import argparse, json, os, sys, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_BASE = "https://api.vimeo.com"

def headers():
    token = os.getenv("VIMEO_TOKEN")
    if not token:
        raise RuntimeError("VIMEO_TOKEN not set. See .env.example")
    return {"Authorization": f"bearer {token}"}

def get_video(video_id: str):
    r = requests.get(f"{API_BASE}/videos/{video_id}", headers=headers(), timeout=30)
    r.raise_for_status()
    return r.json()

def main():
    p = argparse.ArgumentParser(description="Fetch Vimeo video metadata via API v3 (requires token and permissions).")
    p.add_argument("--video-id", required=True, help="Numeric Vimeo video ID")
    p.add_argument("--out", required=True, help="Output JSON file path")
    args = p.parse_args()

    video = get_video(args.video_id)
    record = {
        "source": "vimeo_api",
        "video_id": args.video_id,
        "name": video.get("name"),
        "description": video.get("description"),
        "duration": video.get("duration"),
        "link": video.get("link"),
        "created_time": video.get("created_time"),
        "stats": video.get("stats"),
        "tags": [t.get("tag") for t in video.get("tags", [])],
        "pictures": video.get("pictures"),
        "license": video.get("license"),
        "uploader": {
            "name": (video.get("user") or {}).get("name"),
            "link": (video.get("user") or {}).get("link"),
        },
        "raw": video,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)
    print(f"[api_v3] wrote {args.out}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
