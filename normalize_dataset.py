#!/usr/bin/env python3
"""
normalize_dataset.py
Unify multiple Vimeo JSON outputs into a single CSV or Parquet file.
"""

import argparse
import csv
import json
import os
from pathlib import Path
import pandas as pd  # optional, for Parquet export

FIELDS = ["url", "title", "uploader", "duration", "license", "thumbnail", "description"]


def collect_json(in_dir: Path):
    for path in in_dir.glob("*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            yield data
        except Exception as e:
            print(f"[WARN] Skipping {path}: {e}")


def normalize_record(data: dict) -> dict:
    return {
        "url": data.get("url"),
        "title": data.get("title"),
        "uploader": data.get("uploader") or data.get("author_name"),
        "duration": data.get("duration"),
        "license": data.get("license"),
        "thumbnail": data.get("thumbnail"),
        "description": data.get("description"),
    }


def main():
    p = argparse.ArgumentParser(description="Normalize scraped Vimeo JSON into CSV/Parquet.")
    p.add_argument("--in-dir", required=True, help="Directory with normalized JSON files.")
    p.add_argument("--out", required=True, help="Output file (e.g. videos.csv or videos.parquet).")
    args = p.parse_args()

    in_dir = Path(args.in_dir)
    out_path = Path(args.out)

    rows = [normalize_record(d) for d in collect_json(in_dir)]

    if out_path.suffix == ".csv":
        with out_path.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDS)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        print(f"[OK] Wrote {len(rows)} records to {out_path}")

    elif out_path.suffix == ".parquet":
        df = pd.DataFrame(rows, columns=FIELDS)
        df.to_parquet(out_path, index=False)
        print(f"[OK] Wrote {len(rows)} records to {out_path}")

    else:
        raise SystemExit("Unsupported output format. Use .csv or .parquet")


if __name__ == "__main__":
    main()
