
import os
import sys
import re
from pathlib import Path
from typing import Optional
import yt_dlp
import subprocess
import glob
import urllib.request

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

        # 运行子进程
        process = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        
        if process.returncode != 0:
            err = f"Scraper process failed: {process.stderr}"
            print(err, file=sys.stderr)
            return None, err
            
        try:
            result = json.loads(process.stdout)
        except json.JSONDecodeError:
            err = f"Scraper returned invalid JSON: {process.stdout}"
            print(err, file=sys.stderr)
            return None, err
            
        if not result.get("success"):
            err = f"Scraper reported failure: {result.get('error')}"
            print(err, file=sys.stderr)
            return None, err
            
        download_link = result["data"].get("url")
        
        if not download_link:
            return None, "No download link in response"
            
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
    cookie_temp_file = None
    
    if "douyin.com" in url and douyin_cookie:
        try:
            import tempfile
            import time
            
            # 创建临时 cookie 文件
            cookie_temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt')
            cookie_temp_file.write("# Netscape HTTP Cookie File\n")
            cookie_temp_file.write("# This file was generated by Bili-Summarizer\n")
            
            # 解析 cookie 字符串 (key=value; key2=value2)
            # 简单的解析逻辑，假设 cookie 中没有分号
            for item in douyin_cookie.split(';'):
                if '=' not in item: continue
                name, value = item.strip().split('=', 1)
                # 构造 Netscape 格式行
                # domain flag path secure expiration name value
                # 注意: .douyin.com 是通配子域名
                line = f".douyin.com\tTRUE\t/\tTRUE\t{int(time.time()) + 31536000}\t{name}\t{value}\n"
                cookie_temp_file.write(line)
            
            cookie_temp_file.close()
            common_opts['cookiefile'] = cookie_temp_file.name
            print(f"生成的 Cookie 文件: {cookie_temp_file.name}")
            
        except Exception as e:
            print(f"Cookie 文件生成失败: {e}", file=sys.stderr)

    # 如果没有使用 cookie file，则尝试 header 注入作为 fallback (虽然 yt-dlp 对 header cookie 支持有限)
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
        'format': 'bestvideo[height<=360]+bestaudio/best[height<=360]/best',
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
