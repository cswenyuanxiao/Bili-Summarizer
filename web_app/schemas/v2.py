"""
V2 features related schemas.
"""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


# Favorites
class FavoritesImportRequest(BaseModel):
    favorites_url: str
    mode: str = "smart"
    focus: str = "default"
    limit: int = 50
    selected_bvids: Optional[List[str]] = None


# Templates
class TemplateCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""
    prompt_template: str
    output_format: Optional[str] = "markdown"
    sections: Optional[List[str]] = []


class TemplateUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    prompt_template: Optional[str] = None
    output_format: Optional[str] = None
    sections: Optional[List[str]] = None


# TTS
class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = "zh-CN-XiaoxiaoNeural"


# Subscriptions
class UPSubscribeRequest(BaseModel):
    up_mid: str
    up_name: str
    up_avatar: Optional[str] = ""
    notify_methods: Optional[List[str]] = ["browser"]


class PushSubscriptionRequest(BaseModel):
    endpoint: str
    keys: Dict[str, str]


# Compare
class CompareRequest(BaseModel):
    summary_ids: List[str]  # 要对比的总结 ID 列表
    aspects: Optional[List[str]] = None  # 可选：自定义对比维度


class CompareDirectRequest(BaseModel):
    summaries: List[Dict[str, Any]]  # 直接传入总结内容
    aspects: Optional[List[str]] = None


# Teams
class TeamCreateRequest(BaseModel):
    name: str
    description: Optional[str] = ""


class TeamShareRequest(BaseModel):
    title: str
    video_url: str
    summary_content: str
    video_thumbnail: Optional[str] = ""
    transcript: Optional[str] = ""
    mindmap: Optional[str] = ""
    tags: Optional[str] = ""


class CommentCreateRequest(BaseModel):
    team_summary_id: str
    content: str
    parent_id: Optional[str] = None
