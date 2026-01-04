"""
Summarize related schemas.
"""
from pydantic import BaseModel
from typing import List, Optional


class SummarizeRequest(BaseModel):
    url: str
    mode: str = "smart"  # "smart" or "video"
    focus: str = "default"  # "default", "study", "gossip", "business"
    skip_cache: bool = False
    output_language: str = "zh"  # "zh", "en", "ja", "ko", "es", "fr"
    enable_cot: bool = False  # Enable Chain of Thought display


class BatchSummarizeRequest(BaseModel):
    urls: List[str]
    mode: str = "smart"
    focus: str = "default"


class HistoryItem(BaseModel):
    id: Optional[str] = None
    video_url: str
    video_title: Optional[str] = None
    video_thumbnail: Optional[str] = None
    mode: str
    focus: str
    summary: str
    transcript: Optional[str] = None
    mindmap: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
