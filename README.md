# AI Customer Support Bot

A FastAPI-based customer support assistant that combines FAQ retrieval, intent detection, logging, and ticketing primitives. The project is designed to be extended with an LLM backend and a web chat UI.

## Getting Started

### Requirements
- Python 3.10+
- pip

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Visit `/docs` for interactive Swagger documentation.

## Available Endpoints

- `GET /api/health` — basic health check.
- `POST /api/chat` — process a user message, returning the detected intent, response, and optionally a ticket id.
- `POST /api/feedback` — capture 👍/👎 feedback for a chat response.
- `GET /api/tickets` — view created tickets.

## Project Structure

```
app/
  config.py        # Shared configuration
  db.py            # SQLite helpers and table initialization
  faq.py           # FAQ loader and similarity search
  intent.py        # Simple keyword-based intent detection
  llm.py           # Placeholder LLM-style response generator
  main.py          # FastAPI application and routes
  schemas.py       # Pydantic request/response models

data/
  faqs.json        # Sample FAQ pairs
```

The backend currently uses an in-memory similarity search over FAQs and a placeholder LLM response generator. Ticket creation is triggered on low-confidence responses or explicit escalation intents, and all chat interactions are logged to SQLite for auditing.
