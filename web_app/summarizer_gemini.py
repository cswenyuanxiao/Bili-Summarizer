
import os
from pathlib import Path
import sys
import time
from typing import Optional

import google.generativeai as genai
from dotenv import load_dotenv


def upload_to_gemini(file_path: Path, progress_callback=None):
    """
    独立上传文件到 Gemini，供后续步骤复用。
    """
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found.")
    
    genai.configure(api_key=api_key)
    
    # MIME 类型映射
    mime_mapping = {
        '.mp4': 'video/mp4',
        '.mkv': 'video/x-matroska',
        '.webm': 'video/webm',
        '.mov': 'video/quicktime',
        '.avi': 'video/x-msvideo',
        '.mp3': 'audio/mpeg',
        '.m4a': 'audio/mp4',
        '.wav': 'audio/wav',
        '.aac': 'audio/aac',
        '.flac': 'audio/flac'
    }
    
    ext = file_path.suffix.lower()
    mime_type = mime_mapping.get(ext, 'application/octet-stream')
    
    print(f"正在上传媒体文件: {file_path.name} (类型: {mime_type})")
    if progress_callback:
        progress_callback(f"Uploading file to Google AI (Mime: {mime_type})...")
    
    try:
        media_file = genai.upload_file(path=str(file_path), mime_type=mime_type)
    except Exception as e:
        # 如果还是报错，尝试不带 mime_type 让它自适应（虽然通常这就是报错原因）
        print(f"带MIME上传失败，尝试自动探测: {e}")
        media_file = genai.upload_file(path=str(file_path))
    
    # 等待文件处理完成
    while media_file.state.name == "PROCESSING":
        time.sleep(2)
        media_file = genai.get_file(media_file.name)
        if progress_callback:
             progress_callback(f"Cloud processing: {media_file.state.name}")
    
    if media_file.state.name == "FAILED":
        raise Exception("Google AI File Processing Failed")
        
    print(f"上传完成: {media_file.name}")
    return media_file

def delete_gemini_file(file_obj):
    """安全删除云端文件"""
    try:
        if hasattr(file_obj, 'name'):
            genai.delete_file(file_obj.name)
            print(f"已清理云端文件: {file_obj.name}")
    except Exception as e:
        print(f"清理云端文件失败 (并不影响结果): {e}")

# 配置一个模块级 Logger
import logging
logger = logging.getLogger("summarizer_gemini")


def extract_ai_transcript(file_path: Path, progress_callback=None, uploaded_file=None, retry_count=0) -> str:
    """
    使用 Gemini AI 从视频/音频中提取语音转录。
    支持传入已上传的 file 对象 (uploaded_file) 以避免重复上传。
    
    内置重试机制，最多重试 2 次。
    """
    MAX_RETRIES = 2
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("GOOGLE_API_KEY not found, cannot extract transcript")
        return ""
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")
        
        # 如果 uploaded_file 存在，说明是并行模式，main.py 已经发送了统一的进度消息
        if progress_callback and not uploaded_file:
            progress_callback("Extracting transcript with AI...")
        
        # 1. 确定使用的媒体文件对象
        media_file = uploaded_file
        file_owned = False # 标记是否是在本函数内上传的（如果是，则负责删除）

        if not media_file:
            # 使用统一的上传逻辑以处理 MIME 类型
            media_file = upload_to_gemini(file_path, progress_callback)
            file_owned = True
        
        # 2. 使用专门的转录提示词
        transcript_prompt = """请仔细听取这个视频/音频中的所有语音内容，并生成完整的转录文本。

要求：
1. 逐句转录所有语音内容，不要遗漏
2. 每一句话前都添加时间戳，时间戳间隔尽量在 2-5 秒内，不要跳 30 秒以上
3. 时间戳格式统一为 [mm:ss] 或 [hh:mm:ss]（不要毫秒）
4. 保持原始语言（中文内容用中文，英文用英文）
5. 如果有多个说话者，尽量区分标注
6. 只输出转录内容，不要添加总结或分析

示例格式：
[00:00] 大家好，欢迎来到今天的视频...
[00:03] 今天我们要讨论的话题是...
[00:07] 首先让我们来看第一个观点...
"""
        
        response = model.generate_content(
            [transcript_prompt, media_file],
            request_options={"timeout": 600}
        )
        
        # 3. 清理（仅清理自己上传的文件，传入的文件由调用者负责清理）
        if file_owned:
            try:
                genai.delete_file(media_file.name)
            except:
                pass
        
        if response.parts:
            logger.info("AI Transcript generated successfully.")
            return response.text
        logger.warning("AI Transcript returned empty parts.")
        return ""
        
    except Exception as e:
        logger.error(f"AI转录提取失败 (尝试 {retry_count + 1}/{MAX_RETRIES + 1}): {e}")
        
        # 重试机制
        if retry_count < MAX_RETRIES:
            logger.info(f"正在重试转录... (第 {retry_count + 2} 次)")
            if progress_callback:
                progress_callback(f"Transcript failed, retrying... ({retry_count + 2}/{MAX_RETRIES + 1})")
            time.sleep(2)  # 等待2秒再重试
            return extract_ai_transcript(file_path, progress_callback, uploaded_file, retry_count + 1)
        
        logger.error(f"AI转录最终失败，已重试 {MAX_RETRIES} 次: {e}")
        return ""


def summarize_content(file_path: Path, media_type: str, progress_callback=None, focus: str = "default", uploaded_file=None, custom_prompt: Optional[str] = None, output_language: str = "zh", enable_cot: bool = False) -> str:
    """
    使用 Google Gemini API 总结内容。
    支持传入 uploaded_file 以避免重复上传。
    支持传入 custom_prompt 使用自定义模板。
    支持传入 output_language 设置输出语言。
    支持传入 enable_cot 启用思维链展示。
    """
    # 语言映射
    lang_map = {
        "zh": "中文（简体）",
        "en": "English",
        "ja": "日本語",
        "ko": "한국어",
        "es": "Español",
        "fr": "Français"
    }
    
    target_language = lang_map.get(output_language, "中文（简体）")
    # 1. 加载和配置 API 密钥
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("错误: GOOGLE_API_KEY 未在 .env 文件中设置。")
    
    try:
        genai.configure(api_key=api_key)
        # 使用完整的模型名称
        model = genai.GenerativeModel(model_name="models/gemini-2.0-flash")
    except Exception as e:
        raise Exception(f"Google AI SDK 配置失败: {e}")

    # 如果提供了自定义 Prompt，则优先使用
    if custom_prompt:
        prompt_text = (
            f"{custom_prompt}\n\n"
            "要求：\n"
            "1. 如果视频有视觉画面，请结合画面信息提供更丰富的描述。\n"
            "2. 最终总结末尾必须包含一个思维导图（除非你的模板明确要求不要）。请使用标准 Markdown 无序列表，不要使用 Mermaid。\n"
            "3. 思维导图请以【思维导图】为标题，后续只输出无序列表，不要额外解释。\n"
            "4. 禁止使用客套开场（如“好的/当然/下面是/这是对视频的总结”）。\n"
            "5. 先给 2-3 句概述，再用小标题组织内容（如“关键要点/结论/建议”）。\n"
            "6. 直接使用标准 Markdown 格式。\n"
            f"7. **重要**：请用 {target_language} 输出以下所有内容（包括总结、思维导图节点文本）。"
        )
    else:
        # 根据不同的视角调整 Prompt
        focus_prompts = {
            "default": "深度分析并总结视频的核心内容、关键点和结论。",
            "study": "以学习者的视角，详细总结视频中的核心知识点、学术概念或技术细节。",
            "gossip": "以观众互动的视角，提取视频中的槽点、金句、梗以及最具娱乐性的瞬间。",
            "business": "以商业分析师视角，拆解视频背后的商业模式、市场机会或营销逻辑。"
        }
        
        selected_focus_desc = focus_prompts.get(focus, focus_prompts["default"])

        # CoT Prompt (如果启用)
        cot_instruction = ""
        if enable_cot:
            cot_instruction = (
                "\n\n## 🧠 请先展示你的分析思路\n"
                "在给出正式总结之前，请先按照以下格式输出你的思考过程：\n\n"
                "[COT_START]\n"
                "步骤 1: 内容识别\n"
                "[思考]: (请在此描述你对视频类型和主题的判断)\n\n"
                "步骤 2: 结构分析\n"
                "[思考]: (请在此描述视频的逻辑结构)\n\n"
                "步骤 3: 要点提取\n"
                "[思考]: (请在此列出最重要的信息点)\n\n"
                "步骤 4: 总结策略\n"
                "[思考]: (请在此说明你将采用什么方式总结)\n"
                "[COT_END]\n\n"
                "---\n\n"
                "完成上述思考后，请给出正式的视频总结：\n\n"
            )

        prompt_text = (
            f"你是一个专业的视频分析助手。请按照以下视角进行总结：【{selected_focus_desc}】\n\n"
            f"{cot_instruction}"
            "要求：\n"
            "1. 如果视频有视觉画面，请结合画面信息提供更丰富的描述。\n"
            "2. 摘要需要清晰、结构化且全面。\n"
            "3. 【重要】必须在总结的末尾提供一个思维导图，请使用标准 Markdown 无序列表，不要使用 Mermaid 或编号列表。\n"
            "4. 思维导图请以【思维导图】为标题，后续只输出无序列表，不要额外解释。\n"
            "5. 禁止使用客套开场（如“好的/当然/下面是/这是对视频的总结”）。\n"
            "6. 先给 2-3 句概述，再用小标题组织内容（如“关键要点/结论/建议”）。\n"
            "7. 无序列表示例：\n"
            "- 核心主题\n"
            "  - 分支1\n"
            "    - 子点1\n"
            "    - 子点2\n"
            "  - 分支2\n"
            "8. 直接使用标准 Markdown 格式。严禁使用 LaTeX 格式，表示方向请直接使用 '→' 或 '->'。\n"
            f"9. **重要**：请用 {target_language} 输出以下所有内容（包括总结、思维导图节点文本）。\n"
            "10. **数据可视化**（可选）：如果视频包含统计数据、对比或趋势，请在思维导图之后输出图表：\n"
            "```json\n"
            '{"charts": [{"type": "bar", "title": "标题", "data": {"labels": ["A"], "values": [10]}}]}\n'
            "```\n"
            "type可选: bar/pie/line。"
        )

    content_parts = [prompt_text]
    file_to_delete = None # 本地上传的文件需要删除
    
    try:
        # --- 字幕模式 (文本分析) ---
        if media_type == 'subtitle':
            print(f"正在处理字幕文件: {file_path.name}")
            if progress_callback:
                progress_callback("Reading subtitle file...")
            
            try:
                try:
                    text_content = file_path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    text_content = file_path.read_text(encoding='gbk')

                content_parts.append(f"以下是视频的字幕/文本内容:\n{text_content}")
            except Exception as e:
                raise Exception(f"无法读取字幕文件: {e}")
        
        # --- 视频/音频模式 (多模态分析) ---
        elif media_type in ['audio', 'video']:
            
            # 优先使用传入的 uploaded_file
            if uploaded_file:
                if progress_callback:
                    progress_callback(f"Using pre-uploaded file for analysis...")
                content_parts.append(uploaded_file)
                # 注意：这里我们不设置 file_to_delete，因为这是共享文件，由外部调用者负责删除
            else:
                # 使用统一的上传逻辑以处理 MIME 类型
                video_file = upload_to_gemini(file_path, progress_callback)
                file_to_delete = video_file # 标记需要删除
                content_parts.append(video_file)

        # 3. 调用模型进行总结
        # 如果 uploaded_file 存在，说明是并行模式，main.py 已经发送了统一的进度消息，这里不再重复发送
        if progress_callback and not uploaded_file:
            progress_callback("AI is analyzing content...")
            
        logger.info(f"开始 AI 分析: Model={model.model_name}, EnableCoT={enable_cot}")
        if enable_cot:
            logger.info("CoT 指令已启用，等待思考过程...")
            
        # 增加超时时间到 1200 秒
        response = model.generate_content(content_parts, request_options={"timeout": 1200})
        
        # 打印部分响应内容用于调试
        logger.info(f"AI 响应前 500 字符: {response.text[:500]}")
        
        # 同理，完成消息也只在非并行模式下发送
        if progress_callback and not uploaded_file:
            progress_callback("Analysis complete! Formatting result...")
        
        # 4. 清理 (不再自动清理，留给 main.py 统一管理或依赖 GC)
        # if file_to_delete:
        #    delete_gemini_file(file_to_delete)
        
        if not response.parts:
             raise Exception(f"AI未能生成有效回复")

        logger.info("AI Content Summary generated successfully.")
        # Extract usage metadata
        usage = {
            "prompt_tokens": response.usage_metadata.prompt_token_count,
            "completion_tokens": response.usage_metadata.candidates_token_count,
            "total_tokens": response.usage_metadata.total_token_count
        }

        # 解析 CoT 内容（如果启用）
        response_text = response.text
        if enable_cot:
            logger.info(f"CoT 解析: [COT_START]={('[COT_START]' in response_text)}, [COT_END]={('[COT_END]' in response_text)}")
            
            if "[COT_START]" in response_text and "[COT_END]" in response_text:
                try:
                    cot_start = response_text.index("[COT_START]")
                    cot_end = response_text.index("[COT_END]") + len("[COT_END]")
                    cot_content = response_text[cot_start:cot_end]
                    
                    logger.info(f"CoT 前200字符: {cot_content[:200]}")
                    
                    import re
                    # 更宽容的正则：兼容中英文冒号
                    steps = re.findall(
                        r'(?:###\s*)?步骤\s*(\d+)[:：]\s*(.+?)\n\s*\[思考\][:：]\s*(.+?)(?=\n\n|\n(?:###\s*)?步骤|\[COT_END\]|$)',
                        cot_content, re.DOTALL
                    )
                    
                    logger.info(f"正则匹配到 {len(steps)} 个步骤")
                    
                    if steps:
                        cot_steps = [{"step": int(num), "title": title.strip(), "thinking": thinking.strip()} for num, title, thinking in steps]
                        usage["cot_steps"] = cot_steps
                    else:
                        # 兜底：返回原始文本
                        raw_cot = cot_content.replace("[COT_START]", "").replace("[COT_END]", "").strip()
                        usage["cot_steps"] = [{"step": 0, "title": "AI 分析过程", "thinking": raw_cot}]
                    
                    response_text = response_text[:cot_start] + response_text[cot_end:]
                    response_text = response_text.replace("---\n\n", "").strip()
                except Exception as e:
                    logger.warning(f"CoT 解析失败: {e}")
            else:
                logger.warning("CoT 启用但未检测到标记")

        # 解析图表数据（如果存在）
        if "```json" in response_text and "charts" in response_text:
            try:
                import json
                import re
                # 提取 JSON 代码块
                json_match = re.search(r'```json\s*(\{.*?"charts".*?\})\s*```', response_text, re.DOTALL)
                if json_match:
                    chart_json = json_match.group(1)
                    chart_data = json.loads(chart_json)
                    if "charts" in chart_data and isinstance(chart_data["charts"], list):
                        usage["charts"] = chart_data["charts"]
                        # 移除 JSON 代码块
                        response_text = response_text.replace(json_match.group(0), "").strip()
            except Exception as e:
                logger.warning(f"Failed to parse chart data: {e}")

        return response_text, usage

    except Exception as e:
        logger.error(f"AI 总结最终失败: {e}")
        # Error Cleanup
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
