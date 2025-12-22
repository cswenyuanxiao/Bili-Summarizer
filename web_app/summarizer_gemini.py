
import os
from pathlib import Path
import sys
import time

import google.generativeai as genai
from dotenv import load_dotenv


def extract_ai_transcript(file_path: Path, progress_callback=None) -> str:
    """
    使用 Gemini AI 从视频/音频中提取语音转录。
    
    Args:
        file_path: 视频或音频文件路径
        progress_callback: 进度回调函数
        
    Returns:
        str: 带时间戳的转录文本
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        return ""
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")
        
        if progress_callback:
            progress_callback("Extracting transcript with AI...")
        
        # 上传文件
        media_file = genai.upload_file(path=str(file_path))
        
        # 等待处理完成
        while media_file.state.name == "PROCESSING":
            time.sleep(2)
            media_file = genai.get_file(media_file.name)
        
        if media_file.state.name == "FAILED":
            return ""
        
        # 使用专门的转录提示词
        transcript_prompt = """请仔细听取这个视频/音频中的所有语音内容，并生成完整的转录文本。

要求：
1. 逐句转录所有语音内容，不要遗漏
2. 每隔30秒左右添加一个时间戳标记，格式如：[00:30]、[01:00]、[01:30]
3. 保持原始语言（中文内容用中文，英文用英文）
4. 如果有多个说话者，尽量区分标注
5. 只输出转录内容，不要添加总结或分析

示例格式：
[00:00] 大家好，欢迎来到今天的视频...
[00:30] 今天我们要讨论的话题是...
[01:00] 首先让我们来看第一个观点...
"""
        
        response = model.generate_content(
            [transcript_prompt, media_file],
            request_options={"timeout": 600}
        )
        
        # 清理云端文件
        try:
            genai.delete_file(media_file.name)
        except:
            pass
        
        if response.parts:
            return response.text
        return ""
        
    except Exception as e:
        print(f"AI转录提取失败: {e}", file=sys.stderr)
        return ""


def summarize_content(file_path: Path, media_type: str, progress_callback=None, focus: str = "default") -> str:
    """
    使用 Google Gemini API 总结内容。
    
    Args:
        file_path: 文件路径 (音频或字幕).
        media_type: 'subtitle', 'audio', 或 'video'.
        progress_callback: 状态回调函数.
        focus: 分析视角 ('default', 'study', 'gossip', 'business').
    """
    # 1. 加载和配置 API 密钥
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("错误: GOOGLE_API_KEY 未在 .env 文件中设置。")
    
    try:
        genai.configure(api_key=api_key)
        # 使用完整的模型名称，并确保是 Gemini 3 Flash Preview
        model = genai.GenerativeModel(model_name="models/gemini-3-flash-preview")
    except Exception as e:
        raise Exception(f"Google AI SDK 配置失败: {e}")

    # 根据不同的视角调整 Prompt
    focus_prompts = {
        "default": "深度分析并总结视频的核心内容、关键点和结论。",
        "study": "以学习者的视角，详细总结视频中的核心知识点、逻辑框架、学术概念、公式或参考文献。",
        "gossip": "以观众互动的视角，提取视频中的槽点、金句、梗、弹幕热评以及最具娱乐性的瞬间。",
        "business": "以商业分析师视角，拆解视频背后的商业模式、市场机会、运营逻辑或营销手段。"
    }
    
    selected_focus_desc = focus_prompts.get(focus, focus_prompts["default"])

    prompt_text = (
        f"你是一个专业的视频分析助手。请按照以下视角进行总结：【{selected_focus_desc}】\n\n"
        "要求：\n"
        "1. 如果视频有视觉画面，请结合画面信息提供更丰富的描述。\n"
        "2. 摘要需要清晰、结构化且全面。\n"
        "3. 【重要】必须在总结的末尾提供一个 Mermaid 格式的思维导图。请使用如下格式包裹：\n"
        "```mermaid\n"
        "graph TD\n"
        "    A[核心主题] --> B(关键分支1)\n"
        "    B --> C(细分节点1)\n"
        "    A --> D(关键分支2)\n"
        "```\n"
        "4. 直接使用标准 Markdown 格式。严禁使用 LaTeX 格式（禁止使用 $ 符号），表示方向请直接使用 '→' 或 '->'。"
    )

    file_to_delete = None
    
    try:
        content_parts = [prompt_text]

        if media_type == 'subtitle':
            print(f"正在处理字幕文件: {file_path.name}")
            if progress_callback:
                progress_callback("Reading subtitle file...")
            
            try:
                # Try reading with different encodings
                try:
                    text_content = file_path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    text_content = file_path.read_text(encoding='gbk')

                content_parts.append(f"以下是视频的字幕/文本内容:\n{text_content}")
            except Exception as e:
                raise Exception(f"无法读取字幕文件: {e}")
        
        elif media_type in ['audio', 'video']:
            print(f"正在上传媒体文件: {file_path.name}")
            if progress_callback:
                progress_callback(f"Uploading {media_type} to Google AI Studio...")
            
            video_file = genai.upload_file(path=str(file_path))
            file_to_delete = video_file
            
            print("上传成功! 正在等待云端处理...")
            if progress_callback:
                progress_callback(f"{media_type.capitalize()} uploaded! Waiting for processing...")

            # 等待文件进入 ACTIVE 状态
            while video_file.state.name == "PROCESSING":
                time.sleep(2) 
                video_file = genai.get_file(video_file.name)
                if progress_callback:
                    progress_callback(f"Cloud processing: {video_file.state.name}")

            if video_file.state.name == "FAILED":
                raise Exception("错误: Google AI 服务器处理文件失败。")
            
            content_parts.append(video_file)

        # 3. 调用模型进行总结
        if progress_callback:
            progress_callback("AI is analyzing content...")
            
        print(f"AI 正在使用 {model.model_name} 分析内容...")
        # 增加超时时间到 1200 秒 (20分钟)，针对视频分析
        response = model.generate_content(content_parts, request_options={"timeout": 1200})
        
        if progress_callback:
            progress_callback("Analysis complete! Formatting result...")
        
        # 4. 清理
        if file_to_delete:
            print("正在清理云端文件...")
            if progress_callback:
                progress_callback("Clearing cloud files...")
            genai.delete_file(file_to_delete.name)
        
        if not response.parts:
             raise Exception(f"AI未能生成有效回复")

        # Extract usage metadata
        usage = {
            "prompt_tokens": response.usage_metadata.prompt_token_count,
            "completion_tokens": response.usage_metadata.candidates_token_count,
            "total_tokens": response.usage_metadata.total_token_count
        }

        return response.text, usage

    except Exception as e:
        if file_to_delete:
            try:
                genai.delete_file(file_to_delete.name)
            except:
                pass
        raise Exception(f"AI 总结失败: {e}")

import json

def generate_ppt_structure(summary_text: str) -> dict:
    """
    根据视频总结内容，生成 PPT 结构的 JSON 数据。
    使用 Gemini 模型进行转换。
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found.")
    
    genai.configure(api_key=api_key)
    # 使用较快的模型处理简单的格式转换任务
    model = genai.GenerativeModel("models/gemini-2.0-flash")
    
    prompt = """User wants to turn the following textual summary into a PowerPoint presentation.
    Please act as a Presentation Expert and structure the content into a JSON format suitable for generating slides.

    Output Rules:
    1. Language: Use the same language as the input summary (mostly Chinese).
    2. Slides count: 5 to 12 slides depending on content length.
    3. Content: Use concise bullet points.
    4. Format: STRICTLY JSON format. Do not obscure it with markdown code blocks if possible, or I will have to strip them.

    Target JSON Structure:
    {
        "title": "Presentation Title",
        "subtitle": "Subtitle or Author",
        "slides": [
            {
                "title": "Slide Title",
                "content": [
                    "Bullet point 1",
                    "Bullet point 2",
                    "Bullet point 3"
                ]
            }
        ]
    }

    --- INPUT SUMMARY START ---
    """ + summary_text + "\n--- INPUT SUMMARY END ---"

    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        
        # Clean Markdown Code Blocks
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
        
        if text.endswith("```"):
            text = text[:-3]
            
        return json.loads(text)
    except Exception as e:
        print(f"PPT Structure Generation Failed: {e}", file=sys.stderr)
        # Return a fallback structure
        return {
            "title": "自动生成失败",
            "subtitle": "请重试或检查日志",
            "slides": [
                {
                    "title": "Error",
                    "content": [str(e)]
                }
            ]
        }


if __name__ == '__main__':
    # 用于直接测试 summarizer_gemini.py 模块
    # 这个测试需要一个已下载的视频文件
    try:
        # 假设视频 'BV12b421v7xN.mp4' 已经存在于 videos 文件夹中
        PROJECT_ROOT = Path(__file__).resolve().parent.parent
        test_video_path = PROJECT_ROOT / "videos" / "BV12b421v7xN.mp4"

        if not test_video_path.exists():
            print("测试视频不存在，请先运行 downloader.py 下载视频。", file=sys.stderr)
            sys.exit(1)

        print("--- 开始测试 AI 总结模块 ---")
        summary = summarize_content(test_video_path, 'video')
        print("\n--- 视频摘要 ---")
        print(summary)
        print("\n--- 测试成功! ---")

    except Exception as e:
        print(f"\n--- 测试失败 ---", file=sys.stderr)
        print(f"{e}", file=sys.stderr)
