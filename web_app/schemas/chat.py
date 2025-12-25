"""
Chat related schemas.
"""
from pydantic import BaseModel
from typing import List, Optional


class ChatMessage(BaseModel):
    role: str  # "user" | "assistant"
    content: str


class ChatRequest(BaseModel):
    summary: str
    transcript: Optional[str] = ""
    question: str
    history: List[ChatMessage] = []


class ChatSimpleRequest(BaseModel):
    question: str
    context: str  # The summary text to use as context
