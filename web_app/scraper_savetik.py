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
                print(f"Filling URL: {url}", file=sys.stderr)
                
                # CRITICAL: SaveTik has anti-bot detection
                # We must simulate human input by:
                # 1. Clicking to focus the input
                # 2. Using page.type() to simulate keyboard input (not page.fill())
                
                # First, click to focus the input field
                await page.click('input#s_input', timeout=5000)
                await page.wait_for_timeout(500)  # Small delay after focus
                
                # Clear any existing content
                await page.evaluate('document.getElementById("s_input").value = ""')
                
                # Type the URL character by character to trigger input events
                # This is MUCH more human-like than page.fill()
                await page.type('input#s_input', url, delay=50)  # 50ms delay between keystrokes
                await page.wait_for_timeout(500)  # Let the site process the input
                
                print("Clicking Download button...", file=sys.stderr)
                # Use a more robust selector for the button
                download_button_selectors = [
                    'button.btn-red', 
                    'button#btn-download', 
                    'button:has-text("Download")',
                    '.input-group-append button'
                ]
                
                clicked = False
                for selector in download_button_selectors:
                    try:
                        if await page.is_visible(selector):
                            # Regular click should work after proper input
                            await page.click(selector)
                            clicked = True
                            print(f"Clicked using selector: {selector}", file=sys.stderr)
                            break
                    except:
                        continue
                
                if not clicked:
                    print("Failed to find download button via common selectors, trying keyboard Enter", file=sys.stderr)
                    await page.keyboard.press("Enter")

                # Wait for navigation or results to appear
                print("Waiting for results page to load...", file=sys.stderr)
                try:
                    # First, wait for URL to change or result container to appear
                    initial_url = page.url
                    await page.wait_for_function(
                        f'() => window.location.href !== "{initial_url}" || document.querySelector(".tik-video") || document.querySelector(".dl-action")',
                        timeout=30000
                    )
                    
                    print(f"Page changed or results appeared. Current URL: {page.url}", file=sys.stderr)
                    
                    # Then wait for specific result elements
                    await page.wait_for_selector(
                        '.tik-video, .dl-action, a[href*="snapcdn"], a[href*=".mp4"], .error, #s_result',
                        timeout=30000
                    )
                    # Small buffer for dynamic link injection
                    await page.wait_for_timeout(3000)
                    await page.wait_for_load_state("networkidle", timeout=10000)
                except Exception as e:
                    print(f"Wait for results timed out or failed: {e}", file=sys.stderr)
                    # Fallback wait
                    await page.wait_for_timeout(5000)
            except Exception as e:
                await dump_debug(page, "submit_failed")
                result["error"] = f"Failed to submit URL: {str(e)}"
                return result

            # 3. Parse content
            print("Parsing results...", file=sys.stderr)
            content = await page.content()
            await dump_debug(page, "parsed", content)
            soup = BeautifulSoup(content, 'html.parser')
            
            if mode == "metadata":
                # Extract Metadata
                title = "Douyin Video"
                thumbnail = ""
                
                # Thumbnail
                img_tag = soup.select_one('.tik-video .thumbnail img, #s_result img')
                if img_tag:
                    thumbnail = img_tag.get('src') or img_tag.get('data-src') or ""
                
                # Title
                info_div = soup.select_one('.tik-video .info, #s_result .info')
                if info_div:
                    texts = [p.get_text(strip=True) for p in info_div.find_all(['p', 'h3', 'div', 'span']) if p.get_text(strip=True)]
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
                # Expand search to all elements with href or data-url/data-href
                links = soup.find_all(['a', 'button'], href=True)
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
                        if "downloader" in candidate or "savetikpro" in candidate:
                            continue

                        # MUST be snapcdn download link - this is the actual CDN URL
                        # We do NOT want douyin.com URLs as they require authentication
                        if "snapcdn.app" in candidate:
                            valid_links.append({"href": candidate, "text": text, "priority": 1})
                        # Explicit .mp4 extension in URL (but not douyin.com)
                        elif ".mp4" in candidate and "douyin.com" not in candidate:
                            valid_links.append({"href": candidate, "text": text, "priority": 2})

                if not valid_links:
                    # Fallback: regex scan full HTML (captures JS-embedded URLs)
                    for match in re.findall(r'https?://[^\s"<>]+', content):
                        candidate = match.strip()
                        if "downloader" in candidate or "savetikpro" in candidate:
                            continue
                        if "snapcdn.app" in candidate:
                            valid_links.append({"href": candidate, "text": "", "priority": 1})
                        elif ".mp4" in candidate and "douyin.com" not in candidate:
                            valid_links.append({"href": candidate, "text": "", "priority": 2})
                
                if not valid_links:
                     result["error"] = "无法获取下载链接。可能原因：1) 该视频禁止下载 2) SaveTik暂时无法处理此视频。建议：尝试其他允许下载的视频。"
                     return result

                # Selection Logic
                # Sort by priority first (lower is better)
                valid_links.sort(key=lambda x: x["priority"])
                
                print(f"Found {len(valid_links)} download links, using priority {valid_links[0]['priority']}", file=sys.stderr)
                
                if quality == "lowest":
                    # Try to find NON-HD first among high priority links
                    for link in valid_links:
                        if "hd" not in link["text"].lower():
                            download_url = link["href"]
                            break
                    # Fallback
                    if not download_url:
                        download_url = valid_links[0]["href"]
                else: 
                    # Default/Best: Prefer HD
                    for link in valid_links:
                        if "hd" in link["text"].lower():
                            download_url = link["href"]
                            break
                    if not download_url:
                        download_url = valid_links[0]["href"]
                
                if download_url:
                    # Download the file immediately while token is still valid
                    import tempfile
                    import urllib.request
                    from pathlib import Path
                    
                    try:
                        # Create a temporary filename
                        temp_fd, temp_path = tempfile.mkstemp(suffix=".mp4", prefix="savetik_")
                        import os
                        os.close(temp_fd)
                        
                        print(f"Downloading from: {download_url[:100]}...", file=sys.stderr)
                        
                        # Download using urllib with proper headers
                        headers = {
                            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
                        }
                        req = urllib.request.Request(download_url, headers=headers)
                        
                        with urllib.request.urlopen(req, timeout=300) as response:
                            with open(temp_path, 'wb') as f:
                                total_size = response.getheader('Content-Length')
                                downloaded = 0
                                block_size = 1024 * 1024  # 1MB
                                while True:
                                    chunk = response.read(block_size)
                                    if not chunk:
                                        break
                                    f.write(chunk)
                                    downloaded += len(chunk)
                                    if total_size:
                                        percent = int(downloaded / int(total_size) * 100)
                                        if percent % 10 == 0:
                                            print(f"Download progress: {percent}%", file=sys.stderr)
                        
                        # Verify file was downloaded
                        if os.path.getsize(temp_path) > 0:
                            print(f"Download complete: {temp_path} ({os.path.getsize(temp_path)} bytes)", file=sys.stderr)
                            result["success"] = True
                            result["data"] = {"file_path": temp_path}
                        else:
                            result["error"] = "Downloaded file is empty"
                            os.unlink(temp_path)
                    except Exception as dl_error:
                        result["error"] = f"Download failed: {str(dl_error)}"
                        if os.path.exists(temp_path):
                            os.unlink(temp_path)
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
