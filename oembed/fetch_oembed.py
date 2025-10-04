import argparse, json, requests, sys
from pathlib import Path

OEMBED_ENDPOINT = "https://vimeo.com/api/oembed.json"

def main():
    p = argparse.ArgumentParser(description="Fetch Vimeo oEmbed metadata for a public video URL.")
    p.add_argument("--url", required=True, help="Vimeo video URL, e.g. https://vimeo.com/76979871")
    p.add_argument("--out", required=True, help="Output JSON file path")
    args = p.parse_args()

    resp = requests.get(OEMBED_ENDPOINT, params={"url": args.url}, timeout=20)
    resp.raise_for_status()
    data = resp.json()

    # Keep a focused subset plus raw
    subset = {
        "source": "oembed",
        "video_url": args.url,
        "title": data.get("title"),
        "author_name": data.get("author_name"),
        "author_url": data.get("author_url"),
        "thumbnail_url": data.get("thumbnail_url"),
        "upload_date": data.get("upload_date"),
        "duration": data.get("duration"),
        "raw": data,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(subset, f, ensure_ascii=False, indent=2)
    print(f"[oembed] wrote {args.out}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
