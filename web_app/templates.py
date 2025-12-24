"""
总结模板管理服务
支持预设模板和用户自定义模板
"""
import uuid
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

from .db import get_connection

logger = logging.getLogger(__name__)

# 预设模板定义
PRESET_TEMPLATES = [
    {
        "id": "preset_learning",
        "name": "学习笔记",
        "description": "适合教程、课程类视频，提取知识点和复习问题",
        "prompt_template": """请按照以下格式总结视频内容：

## 📚 核心知识点
（列出 3-5 个最重要的知识点，每个用 1-2 句话解释）

## 🔑 重点标记
（用 > 引用标记视频中最关键的表述）

## ❓ 复习问题
（生成 3 个可用于自测的问题）

## 📝 学习总结
（100 字以内的总体评价和学习建议）""",
        "output_format": "markdown",
        "sections": ["核心知识点", "重点标记", "复习问题", "学习总结"],
        "is_preset": True
    },
    {
        "id": "preset_meeting",
        "name": "会议纪要",
        "description": "适合访谈、讨论类视频，提取核心议题和行动项",
        "prompt_template": """请按照以下格式总结视频内容：

## 👥 参与主体与背景
（简述视频中的主要人物和讨论主题）

## 📌 核心议题
（列出讨论的 3-5 个核心议题）

## 🛠️ 行动项/结论
（总结视频得出的主要结论或建议的行动项）

## 💡 精彩观点
（摘录 2-3 个最具启发性的观点）""",
        "output_format": "markdown",
        "sections": ["参与主体与背景", "核心议题", "行动项/结论", "精彩观点"],
        "is_preset": True
    },
    {
        "id": "preset_product",
        "name": "产品分析",
        "description": "适合评测、发布会类视频，分析优缺点和市场定位",
        "prompt_template": """请按照以下格式总结产品内容：

## 📱 产品概览
（产品名称、定位和核心卖点）

## ✅ 核心优势
（列出 3 个最突出的优点）

## ❌ 存在不足
（分析可能的缺点或待改进点）

## ⚖️ 购买建议
（基于内容给出针对不同人群的购买建议）""",
        "output_format": "markdown",
        "sections": ["产品概览", "核心优势", "存在不足", "购买建议"],
        "is_preset": True
    }
]


def init_preset_templates(user_id: str):
    """为新用户初始化预设模板（如果需要持久化到数据库）"""
    pass


def get_user_templates(user_id: str, include_presets: bool = True) -> List[Dict[str, Any]]:
    """获取用户的模板列表"""
    templates = []
    
    if include_presets:
        templates.extend(PRESET_TEMPLATES)
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id, name, description, prompt_template, output_format, sections, is_preset, created_at, updated_at
        FROM summary_templates
        WHERE user_id = ?
        ORDER BY created_at DESC
    """, (user_id,))
    
    rows = cursor.fetchall()
    conn.close()
    
    for row in rows:
        templates.append({
            "id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "prompt_template": row["prompt_template"],
            "output_format": row["output_format"],
            "sections": json.loads(row["sections"]) if row["sections"] else [],
            "is_preset": bool(row["is_preset"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        })
    
    return templates


def get_template_by_id(template_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """根据 ID 获取模板"""
    # 检查预设模板
    for pt in PRESET_TEMPLATES:
        if pt["id"] == template_id:
            return pt
            
    # 检查数据库
    conn = get_connection()
    cursor = conn.cursor()
    
    if user_id:
        cursor.execute("SELECT * FROM summary_templates WHERE id = ? AND user_id = ?", (template_id, user_id))
    else:
        cursor.execute("SELECT * FROM summary_templates WHERE id = ?", (template_id,))
        
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return None
        
    return {
        "id": row["id"],
        "name": row["name"],
        "description": row["description"],
        "prompt_template": row["prompt_template"],
        "output_format": row["output_format"],
        "sections": json.loads(row["sections"]) if row["sections"] else [],
        "is_preset": bool(row["is_preset"]),
        "user_id": row["user_id"]
    }


def create_template(
    user_id: str,
    name: str,
    prompt_template: str,
    description: str = "",
    output_format: str = "markdown",
    sections: List[str] = None
) -> Dict[str, Any]:
    """创建自定义模板"""
    template_id = f"tmpl_{uuid.uuid4().hex[:12]}"
    now = datetime.utcnow().isoformat()
    
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO summary_templates 
        (id, user_id, name, description, prompt_template, output_format, sections, is_preset, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, FALSE, ?, ?)
    """, (
        template_id,
        user_id,
        name,
        description,
        prompt_template,
        output_format,
        json.dumps(sections or []),
        now,
        now
    ))
    
    conn.commit()
    conn.close()
    
    return {
        "id": template_id,
        "name": name,
        "prompt_template": prompt_template,
        "created_at": now
    }


def update_template(
    template_id: str,
    user_id: str,
    **updates
) -> bool:
    """更新自定义模板"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 构建更新 SQL
    set_clauses = []
    params = []
    
    for key, value in updates.items():
        if key in ["name", "description", "prompt_template", "output_format", "sections"]:
            set_clauses.append(f"{key} = ?")
            if key == "sections":
                params.append(json.dumps(value))
            else:
                params.append(value)
                
    if not set_clauses:
        return False
        
    set_clauses.append("updated_at = ?")
    params.append(datetime.utcnow().isoformat())
    
    params.append(template_id)
    params.append(user_id)
    
    cursor.execute(
        f"UPDATE summary_templates SET {', '.join(set_clauses)} WHERE id = ? AND user_id = ?",
        params
    )
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success


def delete_template(template_id: str, user_id: str) -> bool:
    """删除自定义模板"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute(
        "DELETE FROM summary_templates WHERE id = ? AND user_id = ?",
        (template_id, user_id)
    )
    
    conn.commit()
    success = cursor.rowcount > 0
    conn.close()
    return success
