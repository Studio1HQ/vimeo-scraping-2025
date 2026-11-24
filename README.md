<div align="center">

<img src="https://raw.githubusercontent.com/Studio1HQ/Studio1HQ/main/assets/banners/vimeo-scraping-2025.webp" alt="Vimeo Data Collection with Bright Data: Four ways to collect public Vimeo data in Python" width="100%" />

<br />
<br />

# Vimeo Data Collection with Bright Data

### Four ways to collect public Vimeo data in Python

Python scripts that collect Vimeo video metadata through oEmbed, the Vimeo API v3, Playwright and Selenium, plus a Bright Data Web Unlocker fetcher and a step that unifies the output.

<br />

[![Built by Studio1](https://img.shields.io/badge/Built_by_Studio1-f97316?style=for-the-badge&logo=data%3Aimage%2Fsvg%2Bxml%3Bbase64%2CPHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxNjAgMTYwIiBmaWxsPSJub25lIj48cGF0aCBmaWxsLXJ1bGU9ImV2ZW5vZGQiIGNsaXAtcnVsZT0iZXZlbm9kZCIgZD0iTTAgMzVDMCAxNi42ODA3IDE0LjA3NDQgMS42NDg0NCAzMiAwLjEyNjk1M1YxNDFINTEuMDUyM0M1Mi40MzA4IDEzNy4zNDQgNTQuNzQ0NiAxMzMuNjg5IDU3Ljk5MzggMTMwLjAzM0M2MS4xNDQ2IDEyNi41MDggNjQuNjg5MiAxMjMuNDQgNjguNjI3NyAxMjAuODI5QzcyLjU2NjIgMTE4LjM0OSA3Ni4zNTY5IDExNi43ODIgODAgMTE2LjEyOVY4Ni43NTQ0Qzc1LjQ3MDggODcuOTI5MiA3MS4zODQ2IDg5LjY5MTkgNjcuNzQxNSA5Mi4wNDE1QzY0IDk0LjUyMjUgNjAuNzUwOCA5Ny40NiA1Ny45OTM4IDEwMC44NTRDNTYuNTM0NSAxMDIuNzIgNTUuMjU0NSAxMDQuNjU5IDU0LjE1MzkgMTA2LjY3MVYwSDEyNUMxNDQuMzMgMCAxNjAgMTUuNjY5OSAxNjAgMzVWMTI1QzE2MCAxNDQuMzMgMTQ0LjMzIDE2MCAxMjUgMTYwSDEyNFYxOEgxMDQuOTQ4QzEwMy41NjkgMjEuNjgxNiAxMDEuMjU1IDI1LjM2MjggOTguMDA2MiAyOS4wNDQ0Qzk0Ljg1NTQgMzIuNTk0MiA5MS4zMTA4IDM1LjY4NDEgODcuMzcyMyAzOC4zMTRDODMuNDMzOCA0MC44MTIgNzkuNjQzMSA0Mi4zODk2IDc2IDQzLjA0NzRWNzIuNjMwNEM4MC41MjkyIDcxLjQ0NzMgODQuNjE1NCA2OS42NzI0IDg4LjI1ODUgNjcuMzA1N0M5MiA2NC44MDc2IDk1LjI0OTIgNjEuODQ5MSA5OC4wMDYyIDU4LjQzMDdDOTkuNDY1NSA1Ni41NTEzIDEwMC43NDUgNTQuNTk4NiAxMDEuODQ2IDUyLjU3MjNWMTYwSDM1QzE1LjY3IDE2MCAwIDE0NC4zMyAwIDEyNVYzNVoiIGZpbGw9IiNmZmZmZmYiLz48L3N2Zz4K)](https://studio1hq.com)
[![Built with Bright Data](https://img.shields.io/badge/Built_with_Bright_Data-141414?style=for-the-badge)](https://brightdata.com)

[Bright Data docs](https://docs.brightdata.com) &nbsp;·&nbsp; [Bright Data](https://brightdata.com) &nbsp;·&nbsp; [More examples](https://github.com/Studio1HQ) &nbsp;·&nbsp; [studio1hq.com](https://studio1hq.com)

</div>

<br />

## Overview

Python scripts for collecting public Vimeo video data for research and AI training when you have permission. Each script uses a different approach: oEmbed, the Vimeo API v3, Playwright and Selenium page scrapes, and a Bright Data Web Unlocker fetcher. A normalization step merges the outputs into one CSV or Parquet file.

Bright Data Web Unlocker is called through the Request API (`https://api.brightdata.com/request`) with a zone name. `web_unlocker_fetch.py` can request the page, the oEmbed JSON or the player config JSON for a video, and can save the raw response.

## Features

- **oEmbed**: No authentication needed.
- **Vimeo API v3**: Video metadata, and text tracks when you own the video or have permission.
- **Playwright and Selenium**: Scrape a public page.
- **Bright Data Web Unlocker**: Fetches pages and JSON for URLs listed in a file, with `auto`, `player` and `oembed` modes.
- **Unified dataset**: `datasets/unify_records.py` combines outputs into CSV and Parquet.

## Tech stack

| Layer | Tool |
| --- | --- |
| Scraping | [Bright Data Web Unlocker](https://brightdata.com) |
| Browser automation | [Playwright](https://playwright.dev), Selenium |
| APIs | oEmbed, [Vimeo API v3](https://developer.vimeo.com) |
| Data | pandas, pyarrow |

## Getting started

### Prerequisites

- Python 3
- A [Bright Data](https://brightdata.com) account with a Web Unlocker zone (for that approach)
- A Vimeo access token (for the API v3 scripts)

### Installation

```bash
git clone https://github.com/Studio1HQ/vimeo-scraping-2025.git
cd vimeo-scraping-2025
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install
```

### Environment variables

Create a `.env` file (the repo has no `.env.example`).

| Variable | Description |
| --- | --- |
| `VIMEO_TOKEN` | Vimeo API access token for `api_v3/` scripts. |
| `BRIGHTDATA_API_KEY` | Bright Data API key for `web_unlocker_fetch.py`. Change the name with `--api-key-env`. |

### Run

```bash
# oEmbed
python oembed/fetch_oembed.py --url https://vimeo.com/76979871 --out datasets/oembed_sample.json

# Vimeo API v3: metadata
python api_v3/fetch_video_metadata.py --video-id 76979871 --out datasets/api_video_76979871.json

# Vimeo API v3: text tracks (needs ownership or permission)
python api_v3/fetch_text_tracks.py --video-id 76979871 --out datasets/api_tracks_76979871.jsonl

# Playwright public page
python playwright/scrape_public_page.py --url https://vimeo.com/76979871 --out datasets/playwright_76979871.json

# Bright Data Web Unlocker
python brightdata/web_unlocker_fetch.py --url-file urls.txt --zone "YOUR_UNLOCKER_ZONE" --mode auto --save-raw

# Unify outputs
python datasets/unify_records.py --inputs datasets/*.json --csv datasets/combined.csv --parquet datasets/combined.parquet
```

Create `urls.txt` with one Vimeo URL per line (or pass `--url`). `--zone` defaults to `web_unlocker1`.

## How it works

```text
oembed/       fetch_oembed.py
api_v3/       fetch_video_metadata.py, fetch_text_tracks.py
playwright/   scrape_public_page.py
selenium/     scrape_public_page.py
brightdata/   web_unlocker_fetch.py
datasets/     sample outputs, unify_records.py
normalize_dataset.py
```

Each approach writes JSON or JSONL; `unify_records.py` and `normalize_dataset.py` bring them to a common shape.

Responsible use:

- Respect Vimeo's Terms of Service and robots.txt.
- Fetch only public data you are allowed to collect, and do not bypass access controls.
- For AI training, make sure you have the rights or consent for transcripts, thumbnails and metadata.

This starter is for educational purposes. You are responsible for your own compliance.

## Resources

- [Bright Data docs](https://docs.brightdata.com): Web Unlocker and Request API.
- [Bright Data](https://brightdata.com): Account and zone setup.

<br />

---

<div align="center">

<a href="https://studio1hq.com">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/Studio1HQ/website/main/brand/studio1-logo-on-dark.svg" />
    <img src="https://raw.githubusercontent.com/Studio1HQ/website/main/brand/studio1-logo-on-light.svg" alt="Studio1" width="160" />
  </picture>
</a>

Built by **[Studio1](https://studio1hq.com)**, the technical content and DevRel partner for devtool teams. Made with [Bright Data](https://brightdata.com).<br />
Browse more open-source examples at [github.com/Studio1HQ](https://github.com/Studio1HQ).

[![Website](https://img.shields.io/badge/studio1hq.com-0b0807?style=for-the-badge&logo=googlechrome&logoColor=white)](https://studio1hq.com)
[![Book a call](https://img.shields.io/badge/Book_a_strategy_call-f97316?style=for-the-badge&logo=googlecalendar&logoColor=white)](https://cal.com/studio1/collab)
[![X](https://img.shields.io/badge/%40Studio1HQ-141414?style=for-the-badge&logo=x&logoColor=white)](https://x.com/Studio1HQ)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0a66c2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/company/studio1hq/)

<sub><a href="https://studio1hq.com">studio1hq.com</a> · Technical content, docs, video and DevRel for devtools</sub>

</div>
