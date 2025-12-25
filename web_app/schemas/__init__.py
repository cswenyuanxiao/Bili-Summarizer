"""
Pydantic schemas for API request/response models.
Centralized model definitions to avoid duplication across routers.
"""
from .summarize import SummarizeRequest, BatchSummarizeRequest, HistoryItem
from .chat import ChatMessage, ChatRequest, ChatSimpleRequest
from .payment import PaymentRequest, PlanSubscribeRequest, RedeemInviteRequest
from .share import ShareRequest, ShareCardRequest
from .video import VideoInfoRequest, PPTRequest
from .feedback import FeedbackRequest
from .v2 import (
    FavoritesImportRequest,
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TTSRequest,
    UPSubscribeRequest,
    PushSubscriptionRequest,
    CompareRequest,
    CompareDirectRequest,
    TeamCreateRequest,
    TeamShareRequest,
    CommentCreateRequest
)

__all__ = [
    # Summarize
    "SummarizeRequest",
    "BatchSummarizeRequest",
    "HistoryItem",
    # Chat
    "ChatMessage",
    "ChatRequest",
    "ChatSimpleRequest",
    # Payment
    "PaymentRequest",
    "PlanSubscribeRequest",
    "RedeemInviteRequest",
    # Share
    "ShareRequest",
    "ShareCardRequest",
    # Video
    "VideoInfoRequest",
    "PPTRequest",
    # Feedback
    "FeedbackRequest",
    # V2 Features
    "FavoritesImportRequest",
    "TemplateCreateRequest",
    "TemplateUpdateRequest",
    "TTSRequest",
    "UPSubscribeRequest",
    "PushSubscriptionRequest",
    "CompareRequest",
    "CompareDirectRequest",
    "TeamCreateRequest",
    "TeamShareRequest",
    "CommentCreateRequest",
]
