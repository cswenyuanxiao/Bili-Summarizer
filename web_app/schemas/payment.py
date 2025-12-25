"""
Payment related schemas.
"""
from pydantic import BaseModel


class PaymentRequest(BaseModel):
    plan_id: str
    provider: str


class PlanSubscribeRequest(BaseModel):
    plan_id: str


class RedeemInviteRequest(BaseModel):
    code: str
