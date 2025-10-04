# playwright_scrape.py
import argparse, json, sys, asyncio
from pathlib import Path
from playwright.async_api import async_playwright

async def scrape(url: str):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="vimeo-scraping-2025/1.0 (+docs)",
            viewport={"width": 1280, "height": 800},
        )

        # Optional: block heavy assets to speed things up
        async def route_handler(route):
            if route.request.resource_type in {"media", "font"}:
                return await route.abort()
            await route.continue_()
        await context.route("**/*", route_handler)

        page = await context.new_page()

        # Load page and wait for network to settle
        await page.goto(url, wait_until="networkidle", timeout=45_000)

        # Try to accept a cookie banner quietly if present
        try:
            btn = page.get_by_role("button", name="Accept")
            await btn.wait_for(state="visible", timeout=2_000)
            await btn.click()
        except Exception:
            pass

        # Heuristic selectors; Vimeo UI can change
        title = None
        try:
            title = await page.locator("h1").first.text_content()
            if title:
                title = title.strip()
        except Exception:
            pass

        desc_loc = page.locator(
            "[data-testid='video-description'], .clip_content .description, .video_description"
        )
        description = None
        try:
            if await desc_loc.count() > 0:
                raw = await desc_loc.first.text_content()
                description = raw.strip() if raw else None
        except Exception:
            pass

        # Meta tag fallbacks
        async def meta(name: str):
            sel = page.locator(f"meta[property='{name}']")
            if await sel.count():
                return await sel.first.get_attribute("content")
            return None

        og_title = await meta("og:title")
        og_desc = await meta("og:description")
        og_image = await meta("og:image")

        # Always close cleanly
        try:
            await context.close()
        finally:
            await browser.close()

        return {
            "source": "playwright",
            "url": url,
            "title": (title or og_title) or None,
            "description": (description or og_desc) or None,
            "thumbnail": og_image or None,
        }

def main():
    ap = argparse.ArgumentParser(description="Scrape public Vimeo page metadata using Playwright (no login).")
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    result = asyncio.run(scrape(args.url))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[playwright] wrote {args.out}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
