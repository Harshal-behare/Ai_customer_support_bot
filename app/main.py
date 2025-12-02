from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from . import db
from .config import DEFAULT_LOW_CONFIDENCE_THRESHOLD, FAQ_PATH, STATIC_DIR

from . import db
from .config import DEFAULT_LOW_CONFIDENCE_THRESHOLD, FAQ_PATH
from .faq import FAQService
from .intent import detect_intent
from .llm import generate_response
from .schemas import (
    ChatRequest,
    ChatResponse,
    ChatHistoryItem,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    TicketResponse,
)

app = FastAPI(title="AI Customer Support Bot", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

faq_service = FAQService(FAQ_PATH)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.on_event("startup")
def startup_event() -> None:
    db.init_db()
    faq_service.load()


@app.get("/")
def root() -> dict[str, str]:
    return {
        "message": "AI Customer Support Bot is running",
        "docs": "/docs",
        "health": "/api/health",
        "ui": "/ui",
    }


@app.get("/ui", response_class=HTMLResponse)
def chat_ui() -> HTMLResponse:
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(index_path.read_text(encoding="utf-8"))
    raise HTTPException(status_code=404, detail="UI not found")


    }


@app.get("/api/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", message="Service is healthy")


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest) -> ChatResponse:
    intent, intent_score = detect_intent(payload.message)
    faq_answer, faq_score = faq_service.best_match(payload.message)
    history_rows = db.recent_chat_history(payload.session_id, limit=5)
    history_payload = [dict(row) for row in history_rows]

    if faq_answer and faq_score >= 0.5:
        bot_response = faq_answer
        confidence = faq_score
    else:
        bot_response = generate_response(
            payload.message,
            context=faq_answer,
            history=history_payload,
        )
        confidence = max(intent_score, faq_score, 0.35)

    chat_log_id = db.insert_chat_log(
        payload.message,
        bot_response,
        intent,
        confidence,
        payload.session_id,
    )

    should_create_ticket = intent == "escalation" or confidence < DEFAULT_LOW_CONFIDENCE_THRESHOLD
    created_ticket = False
    ticket_id = None

    if should_create_ticket:
        ticket_id = db.insert_ticket(payload.message, priority="normal", bot_confidence=confidence)
        created_ticket = True

    return ChatResponse(
        response=bot_response,
        intent=intent,
        confidence=round(confidence, 2),
        created_ticket=created_ticket,
        ticket_id=ticket_id,
        chat_log_id=chat_log_id,
        session_id=payload.session_id,
        context_summary=faq_answer,
    )


@app.get("/api/chat/history/{session_id}", response_model=list[ChatHistoryItem])
def chat_history(session_id: str, limit: int = 10) -> list[ChatHistoryItem]:
    rows = db.recent_chat_history(session_id, limit=limit)
    return [
        ChatHistoryItem(
            id=row["id"],
            user_message=row["user_message"],
            bot_response=row["bot_response"],
            created_at=row["created_at"],
        )
        for row in rows
    ]


@app.post("/api/feedback", response_model=FeedbackResponse)
def feedback_endpoint(payload: FeedbackRequest) -> FeedbackResponse:
    if payload.rating not in {"up", "down"}:
        raise HTTPException(status_code=422, detail="Rating must be 'up' or 'down'")

    feedback_id = db.insert_feedback(payload.chat_log_id, payload.rating, payload.comment)
    return FeedbackResponse(feedback_id=feedback_id)


@app.get("/api/tickets", response_model=list[TicketResponse])
def tickets_endpoint() -> list[TicketResponse]:
    rows = db.list_tickets()
    return [
        TicketResponse(
            id=row["id"],
            user_message=row["user_message"],
            status=row["status"],
            priority=row["priority"],
            created_at=row["created_at"],
            bot_confidence=row["bot_confidence"],
        )
        for row in rows
    ]
