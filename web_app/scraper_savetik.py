import asyncio
import sys
import json
import argparse
import re
import os
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

# Constants
SAVETIK_URL = "https://savetik.co/en"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
DEBUG_ENABLED = os.getenv("DOUYIN_SAVETIK_DEBUG", "").lower() in ("1", "true", "yes")
DEFAULT_DEBUG_DIR = Path(__file__).resolve().parent.parent / "videos" / "savetik_debug"
DEBUG_DIR = Path(os.getenv("DOUYIN_SAVETIK_DEBUG_DIR", str(DEFAULT_DEBUG_DIR)))

async def dump_debug(page, stage: str, content: str | None = None) -> None:
    if not DEBUG_ENABLED or page is None:
        return
    try:
        DEBUG_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        screenshot_path = DEBUG_DIR / f"savetik_{stage}_{timestamp}.png"
        html_path = DEBUG_DIR / f"savetik_{stage}_{timestamp}.html"
        await page.screenshot(path=str(screenshot_path), full_page=True)
        html_payload = content or await page.content()
        html_path.write_text(html_payload, encoding="utf-8")
    except Exception as e:
        print(f"Debug dump failed: {e}", file=sys.stderr)

async def run_scraper(url: str, mode: str, quality: str = "lowest"):
    result = {"success": False, "error": None, "data": {}}
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled']
        )
        try:
            # Create context with anti-detection headers
            context = await browser.new_context(
                user_agent=USER_AGENT,
                locale="zh-CN",
                timezone_id="Asia/Shanghai"
            )
            await context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
            )
            page = await context.new_page()
            
            # 1. Navigate
            try:
                await page.goto(SAVETIK_URL, timeout=60000, wait_until="domcontentloaded")
                await page.wait_for_selector('input#s_input', timeout=30000)
            except Exception as e:
                await dump_debug(page, "load_failed")
                result["error"] = f"Failed to load SaveTik: {str(e)}"
                return result

            # 2. Submit URL
            try:
                await page.fill('input#s_input', url)
                await page.click('button.btn-red')
                
                # Wait for result
                try:
                    await page.wait_for_selector(
                        '.tik-video, .tik-video .dl-action a, a[href*="snapcdn"], a[href*=".mp4"]',
                        timeout=45000
                    )
                except:
                    # Fallback wait
                    await page.wait_for_timeout(8000)
            except Exception as e:
                await dump_debug(page, "submit_failed")
                result["error"] = f"Failed to submit URL: {str(e)}"
                return result

            # 3. Parse content
            content = await page.content()
            await dump_debug(page, "parsed", content)
            soup = BeautifulSoup(content, 'html.parser')
            
            if mode == "metadata":
                # Extract Metadata
                title = "Douyin Video"
                thumbnail = ""
                
                # Thumbnail
                img_tag = soup.select_one('.tik-video .thumbnail img')
                if img_tag and img_tag.get('src'):
                    thumbnail = img_tag['src']
                
                # Title
                info_div = soup.select_one('.tik-video .info')
                if info_div:
                    texts = [p.get_text(strip=True) for p in info_div.find_all(['p', 'h3', 'div']) if p.get_text(strip=True)]
                    if texts:
                        title = texts[0]
                
                result["success"] = True
                result["data"] = {
                    "title": title,
                    "thumbnail": thumbnail,
                    "duration": 0,
                    "uploader": "Douyin User"
                }
                
            elif mode == "download":
                # Extract Download Link
                links = soup.find_all('a', href=True)
                download_url = None
                
                # Strategy: Prefer Lowest Quality if requested
                # SaveTik usually offers "Download MP4" and "Download MP4 HD"
                
                valid_links = []

                for a in links:
                    href = a.get('href', '')
                    text = a.get_text().strip().lower()
                    data_url = a.get('data-url') or a.get('data-href') or ''
                    candidates = [href, data_url]

                    for candidate in candidates:
                        candidate = (candidate or '').strip()
                        if not candidate.startswith('http'):
                            continue
                        if "downloader" in candidate:
                            continue

                        # Strong signal: snapcdn (actual download) or .mp4
                        if "snapcdn" in candidate or ".mp4" in candidate:
                            valid_links.append({"href": candidate, "text": text, "priority": 1})
                        # Weaker signal: contains douyin but not a nav link
                        elif "douyin" in candidate and "video" in candidate:
                            valid_links.append({"href": candidate, "text": text, "priority": 2})

                if not valid_links:
                    # Fallback: regex scan full HTML (captures JS-embedded URLs)
                    for match in re.findall(r'https?://[^\s"<>]+', content):
                        candidate = match.strip()
                        if "downloader" in candidate:
                            continue
                        if "snapcdn" in candidate or ".mp4" in candidate:
                            valid_links.append({"href": candidate, "text": "", "priority": 1})
                        elif "douyin" in candidate and "video" in candidate:
                            valid_links.append({"href": candidate, "text": "", "priority": 2})
                
                if not valid_links:
                     result["error"] = "No download links found"
                     return result

                # Selection Logic
                # Sort by priority first
                valid_links.sort(key=lambda x: x["priority"])
                
                if quality == "lowest":
                    # Try to find NON-HD first among high priority links
                    for link in valid_links:
                        if "hd" not in link["text"]:
                            download_url = link["href"]
                            break
                    # Fallback
                    if not download_url:
                        download_url = valid_links[0]["href"]
                else: 
                    # Default/Best: Prefer HD
                    for link in valid_links:
                        if "hd" in link["text"]:
                            download_url = link["href"]
                            break
                    if not download_url:
                        download_url = valid_links[0]["href"]
                
                if download_url:
                    result["success"] = True
                    result["data"] = {"url": download_url}
                else:
                    result["error"] = "No suitable download link found"
            
        except Exception as e:
            result["error"] = f"Unexpected error: {str(e)}"
        finally:
            await browser.close()
            
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="Douyin Video URL")
    parser.add_argument("--mode", choices=["metadata", "download"], default="download")
    parser.add_argument("--quality", choices=["lowest", "best"], default="lowest")
    
    args = parser.parse_args()
    
    # Run loop
    try:
        data = asyncio.run(run_scraper(args.url, args.mode, args.quality))
        print(json.dumps(data))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
