# Vimeo Scraping (2025) — Python Approaches

This repo contains **compliant** ways to collect Vimeo data for research and AI training **when you have permission**.
It implements four approaches:

1. **oEmbed** (no auth)
2. **Vimeo API v3**
3. **Playwright**
4. **Bright Data Web unlocker** 

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # then edit with your tokens
```

### Playwright browsers
```bash
python -m playwright install
```

## Running the scripts

- **oEmbed**:
  ```bash
  python oembed/fetch_oembed.py --url https://vimeo.com/76979871 --out datasets/oembed_sample.json
  ```

- **Vimeo API v3 (metadata)**:
  ```bash
  python api_v3/fetch_video_metadata.py --video-id 76979871 --out datasets/api_video_76979871.json
  ```

- **Vimeo API v3 (text tracks)** *(requires ownership/permissions)*:
  ```bash
  python api_v3/fetch_text_tracks.py --video-id 76979871 --out datasets/api_tracks_76979871.jsonl
  ```

- **Playwright (public page scrape)**:
  ```bash
  python playwright/scrape_public_page.py --url https://vimeo.com/76979871 --out datasets/playwright_76979871.json
  ```

  ```

- **Bright Data (keyword search)**:
  ```bash
  python web_unlocker_fetch.py \
  --url-file urls.txt \
  --zone "YOUR_UNLOCKER_ZONE" \
  --mode auto \
  --save-raw
  ```

- **Unify to CSV/Parquet**:
  ```bash
  python datasets/unify_records.py --inputs datasets/*.json --csv datasets/combined.csv --parquet datasets/combined.parquet
  ```

## Responsible use
- Respect Vimeo's Terms of Service and robots.txt.
- Only fetch **public** data you are allowed to collect; do **not** bypass access controls.
- For AI training, ensure you have appropriate **rights/consent** to use transcripts, thumbnails, and metadata.

---
*This starter is for educational purposes. You are responsible for your own compliance.*
