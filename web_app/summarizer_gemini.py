
import os
from pathlib import Path
import sys
import time

import google.generativeai as genai
from dotenv import load_dotenv



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
