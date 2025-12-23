
import os
import sys
import re
from pathlib import Path
import yt_dlp
import glob

# 定义视频存储目录
PROJECT_ROOT = Path(__file__).resolve().parent.parent
VIDEOS_DIR = PROJECT_ROOT / "videos"

def download_content(url: str, mode: str = "smart", progress_callback=None) -> tuple[Path, str, str]:
    """
    下载内容：
    - smart模式: 优先下载字幕，其次视频, 最后音频。
    - video模式: 直接下载视频。
    
    Returns:
        (file_path, media_type)
        media_type: 'subtitle', 'audio', 'video'
    """
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
        try:
            content = ""
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

            for line in lines:
                line = line.strip()
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
            
            return "\n".join(cleaned_lines) or content.strip()
            
        except Exception as e:
            print(f"Error parsing transcript: {e}")
            return ""

    transcript_text = ""

    # --- Strategy 1: Attempt Subtitles (Zero-Cost & Transcript Extraction) ---
    # Even if mode != 'smart', we try to get subtitles for the transcript feature if possible
    
    if progress_callback:
        progress_callback("Checking for subtitles/transcript...")
    
    common_opts = {
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'noplaylist': True,
    }
    
    # 针对 Bilibili 添加特定防盗链 Header
    if "bilibili.com" in url:
        common_opts['http_headers'] = {
            'Referer': 'https://www.bilibili.com/',
            'Origin': 'https://www.bilibili.com',
        }

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
                
                if mode == "smart":
                    if progress_callback:
                        progress_callback("Subtitles found! Using for analysis.")
                    return best_sub, 'subtitle', transcript_text
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
        raise Exception(f"Failed to retrieve content. Error: {e}")

    raise FileNotFoundError("无法下载有效内容。")

if __name__ == '__main__':
    test_url = "https://www.bilibili.com/video/BV12b421v7xN/" 
    try:
        def simple_cb(msg): print(f"[PROGRESS] {msg}")
        path, media_type = download_content(test_url, progress_callback=simple_cb)
        print(f"\n测试成功! 类型: {media_type}, 文件: {path}")
    except Exception as e:
        print(f"\n测试失败: {e}", file=sys.stderr)
