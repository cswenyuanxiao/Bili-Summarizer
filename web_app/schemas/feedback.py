"""
Feedback related schemas.
"""
from pydantic import BaseModel
from typing import Optional


class FeedbackRequest(BaseModel):
    feedback_type: str
    content: str
    contact: Optional[str] = None
