from typing import Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: str = Field("default", min_length=1, description="Conversation/session identifier")


class ChatResponse(BaseModel):
    response: str
    intent: str
    confidence: float
    created_ticket: bool = False
    ticket_id: Optional[int] = None
    chat_log_id: int
    session_id: str
    context_summary: Optional[str] = None


class FeedbackRequest(BaseModel):
    chat_log_id: int
    rating: str = Field(..., regex="^(up|down)$")
    comment: Optional[str] = None


class FeedbackResponse(BaseModel):
    feedback_id: int


class TicketResponse(BaseModel):
    id: int
    user_message: str
    status: str
    priority: str
    created_at: str
    bot_confidence: Optional[float]


class HealthResponse(BaseModel):
    status: str
    message: str
