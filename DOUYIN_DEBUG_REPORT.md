# Douyin Feature & Debug Report

**Date**: 2026-01-06
**Status**: Feature Implemented but Unstable (Fails in Production)
**Component**: Video Downloader (Douyin Platform)

## 1. Feature Overview

The goal is to support downloading and summarizing Douyin videos. Standard tools like `yt-dlp` currently fail for Douyin due to strict anti-bot measures ("Fresh cookies needed"), even with valid cookies provided.

To bypass this, we implemented a fallback mechanism using **Playwright** to scrape a third-party downloader site, **savetik.co**.

## 2. Architecture & Implementation

### Core Components

1.  **Entry Point**: `web_app/downloader.py`
    -   Function: `download_content(url)` -> `_download_via_savetik(url)`
    -   Logic: Tries `yt-dlp` first. If it fails (specific to Douyin), it triggers the fallback `_download_via_savetik`.

2.  **Scraper Script**: `web_app/scraper_savetik.py`
    -   **Type**: Standalone Python CLI script.
    -   **Dependencies**: `playwright`, `beautifulsoup4`.
    -   **Usage**: `python3 web_app/scraper_savetik.py <URL> --mode download --quality lowest`
    -   **Output**: JSON string to `stdout` (e.g., `{"success": true, "data": {"url": "..."}}`).

3.  **Process Isolation**:
    -   `downloader.py` uses `subprocess.run(...)` to execute `scraper_savetik.py`.
    -   **Reason**: The main FastAPI app runs an `asyncio` loop. Running Playwright (which also uses `asyncio`) directly inside the existing loop or a thread caused "event loop is already running" conflicts or instability. Process isolation solves this completely.

### Key Logic Checklist

*   **Lowest Quality Preference**: The scraper is configured to prefer non-HD links (`--quality lowest`) to save bandwidth and speed up processing (since we only need audio/visuals for AI summarization).
*   **Link Filtering**: The scraper filters `<a>` tags on Savetik to find the valid video URL:
    *   Must start with `http` (ignores relative navigation links).
    *   Must NOT contain "downloader" (prevents picking up nav menu links).
    *   Prioritizes links containing `snapcdn` or `.mp4`.

## 3. Current Bug Details

### Symptom
When triggering a summary from the Web UI, the process fails with:
```
Error: 抖音下载失败：yt-dlp 失败，且 SaveTik 后备方案报错: Scraper reported failure: No download links found
```

### The "Heisenbug" Nature
*   **Locally (Debug Script)**: Running `python3 debug_scraper.py` on the *same machine* works perfectly and returns a valid JSON with a download URL.
*   **In-App (FastAPI)**: Fails consistently with "No download links found".

This implies that even though the scraper process starts, it fails to identify the download button or the resulting download link when spawned by the server process.

### Possible Causes
1.  **Environment Differences**: The FastAPI server environment (env vars, cwd) might differ subtly from the terminal shell.
2.  **Headless Detection**: When spawned by a server process, the browser context might trigger different anti-bot protections on `savetik.co`.
3.  **Timing**: Server load might cause the page to load slower, causing timeouts (though timeouts usually report "process failed" rather than "No download links found"). "No download links found" means it parsed the HTML but found nothing interesting.

## 4. Debugging & Fixes Attempted

### 1. Fix: `asyncio` Conflict
*   **Issue**: `RuntimeError: This event loop is already running`.
*   **Fix**: Refactored from inline `asyncio` code to `subprocess`.
*   **Result**: Resolved the crash/error, but revealed the logical failure ("No download links found").

### 2. Fix: Relative Link Extraction
*   **Issue**: Scraper was picking up `/en/douyin-downloader` as the video link.
*   **Fix**: Added strict filter `if not href.startswith('http'): continue`.
*   **Result**: Scraper now correctly ignores nav links, but now finds *nothing* in the server environment.

### 3. Fix: Quality Selection
*   **Issue**: Downloads were slow (HD).
*   **Fix**: Implemented generic "lowest" logic.
*   **Result**: Verified working in local test script (~60MB/s).

## 5. Guide for Future Debugging

To resume debugging, start here:

1.  **Reproduce**:
    *   Run the app: `npm run dev` & `python -m uvicorn ...`.
    *   Request a Douyin summary.
    *   Observe failure in logs.
    *   Compare with `python3 debug_scraper.py` (which likely works).

2.  **Next Steps to Try**:
    *   **Screenshot Debugging**: Modify `scraper_savetik.py` to take a screenshot (`page.screenshot(path="debug.png")`) just before it parses links. This will reveal what the scraper *actually sees* when run from the server (e.g., is there a captcha? is the layout different?).
    *   **User Data Dir**: Try passing a persistent user data directory to Playwright to keep browser state consistent.
    *   **Verify HTML**: Dump the `soup.prettify()` to a log file inside `scraper_savetik.py` to see the raw HTML structure during a failed run.

3.  **Files of Interest**:
    *   `web_app/scraper_savetik.py`: The logic that parses the page.
    *   `web_app/downloader.py`: The caller.
