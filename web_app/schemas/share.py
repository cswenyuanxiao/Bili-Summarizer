"""
Share related schemas.
"""
from pydantic import BaseModel
from typing import Optional


class ShareRequest(BaseModel):
    title: Optional[str] = None
    summary: str
    transcript: Optional[str] = None
    mindmap: Optional[str] = None


class ShareCardRequest(BaseModel):
    title: str
    summary: str
    thumbnail_url: Optional[str] = None
    template: str = "default"
