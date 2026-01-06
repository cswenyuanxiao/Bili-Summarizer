import json
import logging
import os
import re
import time
import hashlib
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable, Optional
from urllib.parse import urlparse, urlunparse

import httpx

logger = logging.getLogger(__name__)

DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

DEBUG_REPORT_PATH = Path(__file__).resolve().parent.parent / "DOUYIN_DEBUG_REPORT.md"

DOWNLOAD_URL_CANDIDATES = [
    "data.nwm_video_url",
    "data.video_url",
    "data.video.play_addr.url_list[0]",
    "data.video.nwm_video_url",
    "data.urls[0]",
]

TITLE_CANDIDATES = ["data.title", "data.desc", "data.video.title"]
AUTHOR_CANDIDATES = ["data.author.nickname", "data.author", "data.video.author"]
COVER_CANDIDATES = ["data.cover", "data.cover_url", "data.video.cover.url_list[0]"]
DURATION_CANDIDATES = ["data.duration", "data.video.duration"]

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg")
AUDIO_EXTS = (".mp3", ".m4a", ".aac", ".wav", ".flac")


def is_douyin_url(url: str) -> bool:
    lower = (url or "").lower()
    return any(
        host in lower
        for host in ("douyin.com", "v.douyin.com", "iesdouyin.com", "snssdk.com")
    )


def extract_aweme_id(url: str) -> Optional[str]:
    match = re.search(r"/video/(\d+)", url or "")
    return match.group(1) if match else None


def build_cache_key(url: str, aweme_id: Optional[str]) -> str:
    if aweme_id:
        return f"douyin_{aweme_id}"
    url_hash = hashlib.sha256((url or "").encode("utf-8")).hexdigest()[:16]
    return f"douyin_{url_hash}"


def normalize_duration(value: Any) -> Optional[int]:
    if value is None:
        return None
    try:
        duration = float(value)
    except (TypeError, ValueError):
        return None
    if duration > 10000:
        duration = duration / 1000
    return int(duration)


def _parse_path(path: str) -> list[tuple[str, Optional[int]]]:
    tokens: list[tuple[str, Optional[int]]] = []
    for part in path.split("."):
        if "[" in part and part.endswith("]"):
            name, idx = part[:-1].split("[", 1)
            tokens.append((name, int(idx)))
        else:
            tokens.append((part, None))
    return tokens


def get_by_path(data: Any, path: str) -> Any:
    current = data
    for key, idx in _parse_path(path):
        if isinstance(current, dict):
            current = current.get(key)
        else:
            return None
        if idx is not None:
            if isinstance(current, list) and 0 <= idx < len(current):
                current = current[idx]
            else:
                return None
    return current


def iter_strings(data: Any) -> Iterable[str]:
    if isinstance(data, dict):
        for value in data.values():
            yield from iter_strings(value)
    elif isinstance(data, list):
        for item in data:
            yield from iter_strings(item)
    elif isinstance(data, str):
        yield data


def is_video_url(url: str) -> bool:
    if not url.startswith("http"):
        return False
    lower = url.lower()
    if any(ext in lower for ext in IMAGE_EXTS) or any(ext in lower for ext in AUDIO_EXTS):
        return False
    if ".mp4" in lower or "mime=video" in lower or "video" in lower:
        return True
    return False


def sanitize_payload(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {k: sanitize_payload(v) for k, v in payload.items()}
    if isinstance(payload, list):
        return [sanitize_payload(item) for item in payload]
    if isinstance(payload, str):
        if payload.startswith("http"):
            parsed = urlparse(payload)
            sanitized = parsed._replace(query="", fragment="")
            return urlunparse(sanitized)
        if len(payload) > 200:
            return payload[:200] + "...(truncated)"
        return payload
    return payload


def append_debug_report(title: str, url: str, payload: Any) -> None:
    try:
        timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
        DEBUG_REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        sanitized = sanitize_payload(payload)
        section = (
            "\n\n"
            f"## {title}\n\n"
            f"- Time: {timestamp}\n"
            f"- URL: {sanitize_payload(url)}\n\n"
            "```json\n"
            f"{json.dumps(sanitized, ensure_ascii=False, indent=2)}\n"
            "```\n"
        )
        existing = ""
        if DEBUG_REPORT_PATH.exists():
            existing = DEBUG_REPORT_PATH.read_text(encoding="utf-8")
        DEBUG_REPORT_PATH.write_text(existing + section, encoding="utf-8")
    except Exception as exc:
        logger.warning(f"Failed to append DOUYIN_DEBUG_REPORT: {exc}")


def extract_download_url(payload: Any) -> Optional[str]:
    for path in DOWNLOAD_URL_CANDIDATES:
        value = get_by_path(payload, path)
        if isinstance(value, str) and is_video_url(value):
            return value
        if isinstance(value, list):
            for item in value:
                if isinstance(item, str) and is_video_url(item):
                    return item
    for candidate in iter_strings(payload):
        if is_video_url(candidate):
            return candidate
    return None


def extract_metadata(payload: Any) -> dict:
    title = next(
        (value for path in TITLE_CANDIDATES if (value := get_by_path(payload, path))),
        None
    )
    author = next(
        (value for path in AUTHOR_CANDIDATES if (value := get_by_path(payload, path))),
        None
    )
    cover = next(
        (value for path in COVER_CANDIDATES if (value := get_by_path(payload, path))),
        None
    )
    duration_raw = next(
        (value for path in DURATION_CANDIDATES if (value := get_by_path(payload, path)) is not None),
        None
    )
    duration = normalize_duration(duration_raw)
    return {
        "title": title,
        "author": author,
        "cover": cover,
        "duration": duration,
    }


@dataclass
class DouyinHttpConfig:
    base_url: str
    timeout_connect: float
    timeout_read: float
    max_retries: int
    user_agent: str


class Evil0ctalBackend:
    def __init__(self, config: DouyinHttpConfig):
        self.config = config

    def _client(self) -> httpx.Client:
        timeout = httpx.Timeout(
            connect=self.config.timeout_connect,
            read=self.config.timeout_read,
            write=self.config.timeout_read,
            pool=self.config.timeout_connect,
        )
        return httpx.Client(timeout=timeout, headers={"User-Agent": self.config.user_agent})

    def resolve_url(self, url: str) -> str:
        if not is_douyin_url(url):
            return url
        try:
            with self._client() as client:
                response = client.get(url, follow_redirects=True)
                response.raise_for_status()
                return str(response.url)
        except Exception as exc:
            logger.warning(f"Douyin URL resolve failed: {exc}")
            return url

    def fetch_video_data(self, url: str) -> dict:
        endpoint = f"{self.config.base_url}/api/hybrid/video_data"
        with self._client() as client:
            response = client.get(endpoint, params={"url": url, "minimal": "false"})
            response.raise_for_status()
            data = response.json()
        append_debug_report("Evil0ctal video_data (sanitized)", url, data)
        return data

    def fetch_download_data(self, url: str) -> dict:
        endpoint = f"{self.config.base_url}/api/download"
        with self._client() as client:
            response = client.get(
                endpoint,
                params={"url": url, "prefix": "true", "with_watermark": "false"}
            )
            response.raise_for_status()
            data = response.json()
        append_debug_report("Evil0ctal download (sanitized)", url, data)
        return data

    def download_file(
        self,
        download_url: str,
        output_path: Path,
        progress_callback=None
    ) -> None:
        attempt = 0
        while True:
            try:
                with self._client() as client:
                    with client.stream("GET", download_url) as response:
                        response.raise_for_status()
                        output_path.parent.mkdir(parents=True, exist_ok=True)
                        with open(output_path, "wb") as file_handle:
                            downloaded = 0
                            total = int(response.headers.get("Content-Length", "0") or 0)
                            for chunk in response.iter_bytes(chunk_size=1024 * 1024):
                                if not chunk:
                                    continue
                                file_handle.write(chunk)
                                downloaded += len(chunk)
                                if progress_callback and total > 0:
                                    percent = int(downloaded / total * 100)
                                    progress_callback(f"Douyin: Downloading {percent}%")
                return
            except Exception as exc:
                attempt += 1
                if attempt > self.config.max_retries:
                    raise
                sleep_time = min(2 ** attempt, 8) + (0.2 * attempt)
                logger.warning(f"Download retry {attempt}/{self.config.max_retries}: {exc}")
                time.sleep(sleep_time)
