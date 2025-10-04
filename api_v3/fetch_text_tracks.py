import argparse, json, os, sys, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
API_BASE = "https://api.vimeo.com"

def headers():
    token = os.getenv("VIMEO_TOKEN")
    if not token:
        raise RuntimeError("VIMEO_TOKEN not set. See .env.example")
    return {"Authorization": f"Bearer {token}"}

def list_text_tracks(video_id: str):
    r = requests.get(f"{API_BASE}/videos/{video_id}/texttracks", headers=headers(), timeout=30)
    r.raise_for_status()
    return r.json().get("data", [])

def fetch_transcript(video_id: str, track_id: str):
    # Some accounts expose a transcript endpoint; else fetch VTT and parse client-side if permitted.
    r = requests.get(f"{API_BASE}/videos/{video_id}/texttracks/{track_id}/transcript",
                     headers=headers(), timeout=60)
    if r.status_code == 404:
        return {"warning": "Transcript endpoint not available for this track/account."}
    r.raise_for_status()
    return r.json()

def main():
    p = argparse.ArgumentParser(description="Fetch text tracks/transcript (requires proper permissions/ownership).")
    p.add_argument("--video-id", required=True, help="Numeric Vimeo video ID")
    p.add_argument("--out", required=True, help="Output JSONL file path")
    args = p.parse_args()

    tracks = list_text_tracks(args.video_id)
    # Prefer subtitles/captions tracks
    chosen = [t for t in tracks if (t.get("type") in {"subtitles","captions"})]
    if not chosen:
        print("No subtitle/caption tracks found or you lack access.", file=sys.stderr)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for t in chosen:
            track_id = t.get("uri","").split("/")[-1]
            transcript = fetch_transcript(args.video_id, track_id)
            rec = {"video_id": args.video_id, "track": t, "transcript": transcript}
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"[api_v3] wrote {args.out}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
