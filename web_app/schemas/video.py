"""
Video related schemas.
"""
from pydantic import BaseModel


class VideoInfoRequest(BaseModel):
    url: str


class PPTRequest(BaseModel):
    summary: str
