"""
视频总结对比服务
"""
import json
import logging
from typing import List, Dict, Any
import google.generativeai as genai

logger = logging.getLogger(__name__)

COMPARE_PROMPT = """你是一个专业的内容分析师。请对比以下 {count} 个视频的总结内容，生成一份详细的对比分析报告。

## 视频列表

{videos_content}

## 对比维度

请从以下维度进行对比：
{aspects}

## 输出格式

请严格按照以下 JSON 格式输出：

```json
{{
  "comparison_table": {{
    "headers": ["对比维度", "视频1标题", "视频2标题", ...],
    "rows": [
      ["维度1", "视频1观点", "视频2观点", ...],
      ["维度2", "视频1观点", "视频2观点", ...]
    ]
  }},
  "key_differences": [
    {{
      "topic": "差异点主题",
      "description": "具体差异描述",
      "videos": ["视频1观点", "视频2观点"]
    }}
  ],
  "consensus_points": [
    {{
      "topic": "共识点主题",
      "description": "各视频的共同观点"
    }}
  ],
  "analysis_summary": "100字以内的总体分析结论",
  "recommendations": ["建议1", "建议2"]
}}
```

只输出 JSON，不要有其他内容。
"""

DEFAULT_ASPECTS = ["核心观点", "方法论", "优势与不足", "结论"]


async def compare_summaries(
    summaries: List[Dict[str, Any]],
    aspects: List[str] = None
) -> Dict[str, Any]:
    """
    对比多个视频总结
    """
    if len(summaries) < 2:
        raise ValueError("至少需要 2 个视频进行对比")
    
    if len(summaries) > 4:
        raise ValueError("最多支持 4 个视频对比")
    
    # 构建视频内容
    videos_content = ""
    for i, s in enumerate(summaries, 1):
        videos_content += f"""
### 视频 {i}: {s.get('title', '未知标题')}

{s.get('summary', '无总结内容')}

---
"""
    
    # 对比维度
    aspects_text = "\n".join([f"- {a}" for a in (aspects or DEFAULT_ASPECTS)])
    
    # 构建完整 prompt
    prompt = COMPARE_PROMPT.format(
        count=len(summaries),
        videos_content=videos_content,
        aspects=aspects_text
    )
    
    try:
        model = genai.GenerativeModel("gemini-3-flash-preview")
        
        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 4096,
            }
        )
        
        # 解析 JSON
        result_text = response.text
        
        # 提取 JSON 部分
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0]
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0]
        
        result = json.loads(result_text.strip())
        
        # 添加元信息
        result["video_count"] = len(summaries)
        result["video_titles"] = [s.get("title", "") for s in summaries]
        
        return result
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse compare result: {e}")
        raise ValueError("对比结果解析失败")
    except Exception as e:
        logger.error(f"Compare failed: {e}")
        raise


def get_summaries_for_compare(summary_ids: List[str], user_id: str) -> List[Dict[str, Any]]:
    """
    获取用于对比的总结内容（从 Supabase）
    """
    import os
    
    try:
        from supabase import create_client
        
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_ANON_KEY")
        
        if not supabase_url or not supabase_key:
            logger.warning("Supabase not configured for compare")
            return []
        
        supabase = create_client(supabase_url, supabase_key)
        
        summaries = []
        for sid in summary_ids:
            response = supabase.table("summaries")\
                .select("id, video_url, video_title, summary")\
                .eq("id", sid)\
                .eq("user_id", user_id)\
                .single()\
                .execute()
            
            if response.data:
                summaries.append({
                    "id": response.data["id"],
                    "video_id": response.data.get("video_url", ""),
                    "title": response.data.get("video_title") or "未知标题",
                    "summary": response.data.get("summary") or ""
                })
        
        return summaries
        
    except Exception as e:
        logger.error(f"Get summaries for compare failed: {e}")
        return []

