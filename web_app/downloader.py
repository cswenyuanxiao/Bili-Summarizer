
import os
import sys
import re
from pathlib import Path
from typing import Optional
import yt_dlp
import subprocess
import glob
import urllib.request
import time
import hashlib

from .douyin_resolver import (
    Evil0ctalBackend,
    DouyinHttpConfig,
    is_douyin_url,
    extract_aweme_id,
    build_cache_key,
    extract_download_url,
    extract_metadata,
)

# 定义视频存储目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
VIDEOS_DIR = PROJECT_ROOT / "videos"

def extract_audio_for_transcript(video_path: Path) -> Optional[Path]:
    """
    从视频中提取轻量音频用于转录（16kHz/mono）。
    失败时返回 None。
    """
    try:
        audio_path = video_path.with_suffix(".transcript.m4a")
        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(video_path),
            "-vn",
            "-ac",
            "1",
            "-ar",
            "16000",
            "-b:a",
            "64k",
            str(audio_path)
        ]
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if audio_path.exists():
            return audio_path
        return None
    except Exception as e:
        print(f"音频提取失败: {e}", file=sys.stderr)
        return None

def _normalize_douyin_url(url: str) -> str:
    """Resolve Douyin short links and convert to canonical format."""
    if "douyin.com" not in url:
        return url
        
    try:
        # 1. Resolve short links (v.douyin.com)
        if "v.douyin.com" in url:
            print(f"Resolving short URL: {url}")
            req = urllib.request.Request(
                url, 
                headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
            )
            with urllib.request.urlopen(req) as response:
                url = response.geturl()
                print(f"Resolved Douyin URL: {url}")
        
        # 2. Convert to canonical /video/ format if it is an iesdouyin/share link
        match = re.search(r'/video/(\d+)', url)
        if match:
            video_id = match.group(1)
            new_url = f"https://www.douyin.com/video/{video_id}"
            if new_url != url:
                print(f"Normalized to canonical URL: {new_url}")
            return new_url
            
    except Exception as e:
        print(f"Warning: URL normalization failed: {e}", file=sys.stderr)
        
    return url


def _get_env_int(key: str, default: int) -> int:
    try:
        return int(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


def _get_env_float(key: str, default: float) -> float:
    try:
        return float(os.getenv(key, default))
    except (TypeError, ValueError):
        return default


def _get_douyin_cache_path(cache_key: str) -> Path:
    cache_dir = VIDEOS_DIR / "douyin_cache"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / f"{cache_key}.mp4"


def _is_cache_valid(path: Path, ttl_seconds: int) -> bool:
    if not path.exists():
        return False
    if ttl_seconds <= 0:
        return True
    age = time.time() - path.stat().st_mtime
    if age <= ttl_seconds:
        return True
    try:
        path.unlink()
    except Exception:
        pass
    return False


def _download_via_evil0ctal(url: str, output_dir: Path, progress_callback=None) -> tuple[Optional[Path], Optional[str]]:
    """
    使用 Evil0ctal 自建解析服务下载抖音视频。
    Returns: (file_path, error_message)
    """
    try:
        base_url = os.getenv("DOUYIN_API_BASE", "http://localhost:8001").rstrip("/")
        timeout_connect = _get_env_float("DOUYIN_HTTP_TIMEOUT_CONNECT", 5.0)
        timeout_read = _get_env_float("DOUYIN_HTTP_TIMEOUT_READ", 60.0)
        max_retries = _get_env_int("DOUYIN_HTTP_MAX_RETRIES", 2)
        user_agent = os.getenv(
            "DOUYIN_USER_AGENT",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        cache_ttl = _get_env_int("DOUYIN_CACHE_TTL_SECONDS", 86400)
        min_bytes = _get_env_int("DOUYIN_MIN_BYTES", 51200)

        resolver = Evil0ctalBackend(
            DouyinHttpConfig(
                base_url=base_url,
                timeout_connect=timeout_connect,
                timeout_read=timeout_read,
                max_retries=max_retries,
                user_agent=user_agent
            )
        )

        normalized_url = resolver.resolve_url(url)
        if progress_callback:
            progress_callback("Douyin: 解析作品信息...")
        video_data = resolver.fetch_video_data(normalized_url)
        metadata = extract_metadata(video_data)
        aweme_id = extract_aweme_id(normalized_url)
        cache_key = build_cache_key(normalized_url, aweme_id)
        cache_path = _get_douyin_cache_path(cache_key)

        if _is_cache_valid(cache_path, cache_ttl):
            if progress_callback:
                progress_callback("Douyin: 命中缓存，直接复用视频...")
            return cache_path, None

        if progress_callback:
            progress_callback("Douyin: 解析下载链接...")
        download_data = resolver.fetch_download_data(normalized_url)
        download_url = extract_download_url(download_data)
        if not download_url:
            return None, "Evil0ctal 返回中未找到可用下载链接"

        if progress_callback:
            progress_callback("Douyin: 开始下载视频...")
        resolver.download_file(download_url, cache_path, progress_callback)

        if not cache_path.exists() or cache_path.stat().st_size < min_bytes:
            return None, "下载文件体积异常"

        if metadata.get("title"):
            print(f"Douyin 下载成功: {metadata['title']}")
        return cache_path, None

    except Exception as e:
        return None, f"Evil0ctal 下载流程异常: {e}"

def _download_via_savetik(url: str, output_dir: Path, progress_callback=None) -> tuple[Optional[Path], Optional[str]]:
    """
    使用 savetik.co 下载抖音视频 (Subprocess + Playwright 方案)。
    将 Playwright 隔离在独立进程中，避免与 FastAPI 事件循环冲突。
    Returns: (file_path, error_message)
    """
    import urllib.request
    import uuid
    import subprocess
    import json
    import sys
    
    try:
        if progress_callback:
            progress_callback("启动 Playwright scraper (subprocess)...")
            
        # 定义 scraper 脚本路径
        scraper_script = Path(__file__).parent / "scraper_savetik.py"
        
        # 调用子进程 (使用 'lowest' 画质以提高速度)
        cmd = [sys.executable, str(scraper_script), url, "--mode", "download", "--quality", "lowest"]
        
        if progress_callback:
            progress_callback("正在解析下载链接 (优先低画质以提速)...")

        # 运行子进程，传递环境变量
        # Timeout=300s (5 min) to handle large video files (e.g. 132MB)
        import os
        env = os.environ.copy()
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=300, env=env)
        
        # Print stderr for debugging
        if process.stderr:
            print(f"[Scraper stderr]: {process.stderr}",file=sys.stderr)
        
        if process.returncode != 0:
            err = f"Scraper process failed (code {process.returncode}): {process.stderr}"
            print(err, file=sys.stderr)
            return None, err
            
        try:
            result = json.loads(process.stdout)
        except json.JSONDecodeError:
            err = f"Scraper returned invalid JSON: {process.stdout[:500]}"
            print(err, file=sys.stderr)
            return None, err
            
        if not result.get("success"):
            err = f"Scraper reported failure: {result.get('error')}"
            print(err, file=sys.stderr)
            return None, err
            
        # Check if scraper returned a file path (new behavior) or URL (old behavior)
        if "file_path" in result["data"]:
            # Scraper already downloaded the file
            temp_file = Path(result["data"]["file_path"])
            if not temp_file.exists():
                return None, f"Downloaded file not found: {temp_file}"
            
            # Move to output directory with a proper name
            import shutil
            video_id = str(uuid.uuid4())[:8]
            output_path = output_dir / f"savetik_{video_id}.mp4"
            shutil.move(str(temp_file), str(output_path))
            
            if progress_callback:
                progress_callback("Download complete!")
            
            print(f"SaveTik 下载成功: {output_path}")
            return output_path, None
            
        # Old behavior: scraper returned URL (kept for compatibility)
        download_link = result["data"].get("url")
        
        if not download_link:
            return None, "No download link or file path in response"
            
        if progress_callback:
            progress_callback("获取链接成功，开始下载...")
            
        # 下载文件
        video_id = str(uuid.uuid4())[:8]
        output_path = output_dir / f"savetik_{video_id}.mp4"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        # 使用更大的 Block Size 和更长的 Timeout
        req = urllib.request.Request(download_link, headers=headers)
        
        # 10分钟超时 (600s), 1MB buffer
        with urllib.request.urlopen(req, timeout=600) as response:
            with open(output_path, 'wb') as f:
                total_size = response.getheader('Content-Length')
                downloaded = 0
                block_size = 1024 * 1024 # 1MB Chunk
                while True:
                    chunk = response.read(block_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size and progress_callback:
                        percent = int(downloaded / int(total_size) * 100)
                        progress_callback(f"SaveTik: Downloading {percent}%")
        
        if output_path.exists() and output_path.stat().st_size > 0:
            print(f"SaveTik 下载成功: {output_path}")
            return output_path, None
            
    except Exception as e:
        err = f"SaveTik 下载流程异常: {e}"
        print(err, file=sys.stderr)
        return None, err
    
    return None, "Unknown failure"

def get_douyin_metadata_via_savetik(url: str) -> dict:
    """
    使用 savetik.co 获取抖音视频的元数据 (Subprocess 方案)。
    """
    import subprocess
    import json
    import sys
    import os
    
    try:
        scraper_script = Path(__file__).parent / "scraper_savetik.py"
        cmd = [sys.executable, str(scraper_script), url, "--mode", "metadata"]
        
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if process.returncode != 0:
            print(f"Metadata Scraper failed: {process.stderr}", file=sys.stderr)
            return None
            
        try:
            result = json.loads(process.stdout)
        except json.JSONDecodeError:
            return None
            
        if not result.get("success"):
            return None
            
        return result["data"]

    except Exception as e:
        print(f"SaveTik Metadata 流程失败: {e}", file=sys.stderr)
        return None

def download_content(url: str, mode: str = "smart", progress_callback=None) -> tuple[Path, str, str]:
    """
    下载内容：
    - smart模式: 优先下载字幕，其次视频, 最后音频。
    - video模式: 直接下载视频。
    
    Returns:
        (file_path, media_type)
        media_type: 'subtitle', 'audio', 'video'
    """
    # Pre-process URL
    url = _normalize_douyin_url(url)
    print(f"准备智能处理: {url}")
    VIDEOS_DIR.mkdir(exist_ok=True)

    if is_douyin_url(url):
        provider = (os.getenv("DOUYIN_RESOLVER_PROVIDER") or "evil0ctal").lower()
        transcript_text = ""
        if provider == "savetik":
            video_path, err = _download_via_savetik(url, VIDEOS_DIR, progress_callback)
        else:
            video_path, err = _download_via_evil0ctal(url, VIDEOS_DIR, progress_callback)
        if err:
            raise Exception(f"抖音下载失败：{err}")
        if not video_path:
            raise Exception("抖音下载失败：未获取到视频文件")
        return video_path, "video", transcript_text

    def yt_dlp_progress_hook(d):
        if d['status'] == 'downloading':
            p = d.get('_percent_str', '0%').replace('%', '')
            try:
                percent = float(p)
                if progress_callback:
                    progress_callback(f"Downloading: {percent}%")
            except ValueError:
                pass
        elif d['status'] == 'finished':
            if progress_callback:
                progress_callback("Download complete, processing...")

    # --- Helper: Parse Subtitle ---
    def parse_transcript(file_path: Path) -> str:
        content = ""
        try:
            try:
                content = file_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    content = file_path.read_text(encoding='gbk')
                except UnicodeDecodeError:
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
            if not content.strip():
                return ""

            suffix = file_path.suffix.lower()
            lines = content.splitlines()
            cleaned_lines = []
            current_timestamp = ""

            def format_timestamp(ts: str) -> str:
                ts = ts.strip()
                if not ts:
                    return ""
                ts = ts.replace(',', '.')
                parts = ts.split(':')
                try:
                    if len(parts) == 3:
                        hours = int(parts[0])
                        minutes = int(parts[1])
                        seconds = int(float(parts[2]))
                    elif len(parts) == 2:
                        hours = 0
                        minutes = int(parts[0])
                        seconds = int(float(parts[1]))
                    else:
                        return ""
                except ValueError:
                    return ""

                total_seconds = max(0, hours * 3600 + minutes * 60 + seconds)
                hours = total_seconds // 3600
                minutes = (total_seconds % 3600) // 60
                seconds = total_seconds % 60
                if hours > 0:
                    return f"[{hours:02d}:{minutes:02d}:{seconds:02d}]"
                return f"[{minutes:02d}:{seconds:02d}]"

            def push_line(ts: str, text: str) -> None:
                text = text.strip()
                if not text:
                    return
                if ts:
                    cleaned_lines.append(f"{ts} {text}")
                else:
                    cleaned_lines.append(text)

            if suffix in ['.ttml', '.xml']:
                for match in re.finditer(r'<p[^>]*begin="([^"]+)"[^>]*>(.*?)</p>', content, re.DOTALL | re.IGNORECASE):
                    ts = format_timestamp(match.group(1))
                    text = re.sub(r'<[^>]+>', '', match.group(2))
                    push_line(ts, text)
                return "\n".join(cleaned_lines) or content.strip()

            if suffix == '.ass':
                for line in lines:
                    if not line.startswith('Dialogue:'):
                        continue
                    parts = line.split(',', 9)
                    if len(parts) < 10:
                        continue
                    ts = format_timestamp(parts[1])
                    text = parts[9].replace('\\N', ' ')
                    push_line(ts, text)
                return "\n".join(cleaned_lines) or content.strip()

            def fallback_clean(raw_text: str) -> str:
                sanitized = re.sub(r'<[^>]+>', '', raw_text)
                cleaned = []
                for raw_line in sanitized.splitlines():
                    line = raw_line.strip()
                    if not line or line.isdigit() or '-->' in line:
                        continue
                    if line.startswith('WEBVTT') or line.startswith('X-TIMESTAMP') or line.startswith('NOTE'):
                        continue
                    cleaned.append(line)
                return "\n".join(cleaned).strip()

            for line in lines:
                line = re.sub(r'<[^>]+>', '', line).strip()
                # Skip empty lines, numbered lines (SRT), and header info
                if not line or line.isdigit() or line.startswith('WEBVTT') or line.startswith('X-TIMESTAMP') or line.startswith('NOTE'):
                    continue

                if '-->' in line:
                    start = line.split('-->')[0].strip()
                    current_timestamp = format_timestamp(start)
                    # We might want to keep timestamps in a specific format, but for now let's keep it simple text or just keep the raw content if it's too complex to parse manually without errors.
                    # actually, keeping timestamps is good for the "Transcript" tab.
                    continue
                
                push_line(current_timestamp, line)
            
            return "\n".join(cleaned_lines) or fallback_clean(content) or content.strip()
            
        except Exception as e:
            print(f"Error parsing transcript: {e}")
            return content.strip()

    transcript_text = ""

    # --- Strategy 1: Attempt Subtitles (Zero-Cost & Transcript Extraction) ---
    # Even if mode != 'smart', we try to get subtitles for the transcript feature if possible
    
    if progress_callback:
        progress_callback("Checking for subtitles/transcript...")
    
    common_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'noplaylist': True,
    }

    # 针对 Bilibili 添加特定防盗链 Header
    if "bilibili.com" in url:
        common_opts['http_headers'] = {
            'Referer': 'https://www.bilibili.com/',
            'Origin': 'https://www.bilibili.com',
        }

    # 针对 Douyin: 生成 Netscape 格式的 Cookie 文件 (比 Header 更稳定)
    douyin_cookie = (os.getenv("DOUYIN_COOKIE") or "").strip()
    youtube_cookie = (os.getenv("YOUTUBE_COOKIES") or "").strip()
    cookie_temp_file = None
    
    # 统一 Cookie 处理函数
    def create_cookie_file(cookie_str: str, domain: str) -> str:
        try:
            import tempfile
            import time
            tf = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt')
            tf.write("# Netscape HTTP Cookie File\n")
            tf.write("# This file was generated by Bili-Summarizer\n")
            
            for item in cookie_str.split(';'):
                if '=' not in item: continue
                name, value = item.strip().split('=', 1)
                # domain flag path secure expiration name value
                line = f"{domain}\tTRUE\t/\tTRUE\t{int(time.time()) + 31536000}\t{name}\t{value}\n"
                tf.write(line)
            
            tf.close()
            print(f"生成的 Cookie 文件 ({domain}): {tf.name}")
            return tf.name
        except Exception as e:
            print(f"Cookie 文件生成失败: {e}", file=sys.stderr)
            return None

    if "douyin.com" in url and douyin_cookie:
        cookie_path = create_cookie_file(douyin_cookie, ".douyin.com")
        if cookie_path:
            common_opts['cookiefile'] = cookie_path
            cookie_temp_file = cookie_path # Keep ref to cleanup if needed (though we rely on OS mostly)

    elif ("youtube.com" in url or "youtu.be" in url) and youtube_cookie:
        cookie_path = create_cookie_file(youtube_cookie, ".youtube.com")
        if cookie_path:
            common_opts['cookiefile'] = cookie_path
            cookie_temp_file = cookie_path

    # 如果没有使用 cookie file，则尝试 header 注入作为 fallback (Douyin only)
    if "douyin.com" in url and not common_opts.get('cookiefile'):
        http_headers = dict(common_opts.get('http_headers', {}))
        http_headers.update({
            'Referer': 'https://www.douyin.com/',
            'Origin': 'https://www.douyin.com',
            'Cookie': douyin_cookie,
        })
        common_opts['http_headers'] = http_headers

    sub_opts = {
        **common_opts,
        'skip_download': True,
        'writeautomaticsub': True,
        'writesubtitles': True,
        'subtitleslangs': ['zh-Hans', 'zh-Hant', 'en', 'all'], 
        'outtmpl': str(VIDEOS_DIR / '%(id)s'), # No extension here, yt-dlp adds it
    }

    try:
        with yt_dlp.YoutubeDL(sub_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get('id')
            
            # Check for generated subtitle files
            sub_files = list(VIDEOS_DIR.glob(f"{video_id}.*"))
            valid_subs = [f for f in sub_files if f.suffix in ['.vtt', '.srt', '.ttml', '.ass']]
            
            if valid_subs:
                best_sub = valid_subs[0]
                print(f"发现字幕文件: {best_sub.name}")
                transcript_text = parse_transcript(best_sub)
                
                if mode == "smart" and transcript_text.strip():
                    if progress_callback:
                        progress_callback("Subtitles found! Using for analysis.")
                    return best_sub, 'subtitle', transcript_text
                elif mode == "smart":
                    print("字幕解析为空，继续下载视频以便转录补齐")
                else:
                    # If mode is not smart (e.g. force video), we still keep the transcript but continue to download video
                     if progress_callback:
                        progress_callback("Subtitles found (saved for transcript).")

    except Exception as e:
        print(f"字幕提取尝试失败: {e}", file=sys.stderr)

    # --- Strategy 2: Low-Res Video (Visual-Rich Fallback) ---
    if progress_callback:
        progress_callback("Downloading visual content (360p)...")

    video_opts = {
        **common_opts,
        'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]/best',
        'outtmpl': str(VIDEOS_DIR / '%(id)s.%(ext)s'),
        'progress_hooks': [yt_dlp_progress_hook],
        'merge_output_format': 'mp4',
    }

    try:
        with yt_dlp.YoutubeDL(video_opts) as ydl:
            # We already have info from previous call if successful, but safer to re-extract or just download
            info = ydl.extract_info(url, download=True)
            video_id = info.get('id')
            video_file = VIDEOS_DIR / f"{video_id}.mp4"
            
            if not video_file.exists():
                for f in VIDEOS_DIR.iterdir():
                    if f.stem == video_id and f.suffix in ['.mp4', '.mkv', '.webm']:
                        video_file = f
                        break
            
            if video_file.exists():
                print(f"视频下载成功: {video_file.name}")
                return video_file, 'video', transcript_text

    except Exception as e:
        print(f"视频下载失败 (尝试纯音频模式): {e}", file=sys.stderr)
        if progress_callback:
            progress_callback("Video failed. Falling back to audio only...")

    # --- Strategy 3: Audio Only (Last Resort) ---
    audio_opts = {
        **common_opts,
        'format': 'bestaudio/best',
        'outtmpl': str(VIDEOS_DIR / '%(id)s.%(ext)s'),
        'progress_hooks': [yt_dlp_progress_hook],
    }

    try:
        with yt_dlp.YoutubeDL(audio_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            video_id = info.get('id')
            ext = info.get('ext')
            audio_file = VIDEOS_DIR / f"{video_id}.{ext}"
            
            if audio_file.exists():
                print(f"音频下载成功: {audio_file.name}")
                return audio_file, 'audio', transcript_text
                
            for f in VIDEOS_DIR.iterdir():
                if f.stem == video_id:
                   return f, 'audio', transcript_text
    except Exception as e:
        print(f"音频模式下载失败: {e}", file=sys.stderr)

    # --- Strategy 4 (Douyin Only): Fallback ---
    # 如果抖音链接走到这里（没有有效内容），尝试 SaveTik
    if "douyin.com" in url:
        print("所有 yt-dlp 策略均未返回内容，尝试 SaveTik...")
        savetik_result, error_msg = _download_via_savetik(url, VIDEOS_DIR, progress_callback)
        if savetik_result:
            return savetik_result, 'video', transcript_text
        
        # 详细报错
        raise Exception(f"抖音下载失败：yt-dlp 失败，且 SaveTik 后备方案报错: {error_msg or '未知错误'}")

    raise FileNotFoundError("无法下载有效内容。")

if __name__ == '__main__':
    test_url = "https://www.bilibili.com/video/BV12b421v7xN/" 
    try:
        def simple_cb(msg): print(f"[PROGRESS] {msg}")
        path, media_type = download_content(test_url, progress_callback=simple_cb)
        print(f"\n测试成功! 类型: {media_type}, 文件: {path}")
    except Exception as e:
        print(f"\n测试失败: {e}", file=sys.stderr)
