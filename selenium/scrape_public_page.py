import argparse, json, sys, time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

def safe_find_text(driver, by, selector):
    try:
        el = driver.find_element(by, selector)
        return el.text.strip()
    except NoSuchElementException:
        return None

def main():
    ap = argparse.ArgumentParser(description="Scrape public Vimeo page metadata using Selenium (no login).")
    ap.add_argument("--url", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    opts = Options()
    opts.add_argument("--headless=new")
    driver = webdriver.Chrome(options=opts)
    driver.get(args.url)
    time.sleep(3)  # allow some rendering

    # Try to accept cookie banners
    try:
        for text in ("Accept", "I Accept", "Agree"):
            buttons = driver.find_elements(By.XPATH, f"//button[contains(., '{text}')]")
            if buttons:
                buttons[0].click()
                break
    except Exception:
        pass

    title = safe_find_text(driver, By.TAG_NAME, "h1")
    description = None
    try:
        # Possible description containers
        for sel in [
            "//*[@data-testid='video-description']",
            "//*[@class='clip_content']//div[contains(@class,'description')]",
            "//*[@class='video_description']",
        ]:
            el = driver.find_element(By.XPATH, sel)
            if el and el.text.strip():
                description = el.text.strip()
                break
    except Exception:
        pass

    # OpenGraph fallback
    og_title = driver.execute_script('return document.querySelector("meta[property=\'og:title\']")?.content') or None
    og_desc = driver.execute_script(
        'return document.querySelector("meta[property=\'og:description\']")?.content') or None
    og_image = driver.execute_script('return document.querySelector("meta[property=\'og:image\']")?.content') or None

    data = {
        "source": "selenium",
        "url": args.url,
        "title": title or og_title,
        "description": description or og_desc,
        "thumbnail": og_image,
    }
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[selenium] wrote {args.out}")
    driver.quit()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        sys.exit(1)
