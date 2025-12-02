# AI Customer Support Bot

A FastAPI-based customer support assistant that combines FAQ retrieval, intent detection, logging, and ticketing primitives. The project now ships with OpenAI-powered responses and a lightweight in-browser chat playground for quick testing.

## Getting Started

### Requirements
- Python 3.10+
- pip

Install dependencies:

```bash
pip install -r requirements.txt
```

Export your OpenAI API key (and optional model) so the backend can generate replies with OpenAI Chat Completions. A safe non-OpenAI fallback message is used if the key is missing or a request fails:

```bash
export OPENAI_API_KEY="sk-..."
# Optional: override the default gpt-4o-mini model
export OPENAI_MODEL="gpt-4o"
```

Run the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. Visit `/docs` for interactive Swagger documentation.

### Running in GitHub Codespaces

- The included `.devcontainer/devcontainer.json` uses the official Python 3.11 image and auto-installs dependencies via `pip install -r requirements.txt` after the container is created.
- Start the API inside Codespaces with host binding so the forwarded port works:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Codespaces will automatically forward port 8000; accept the prompt to open the forwarded URL and use `/docs` for the Swagger UI.

## Available Endpoints

- `GET /api/health` — basic health check.
- `POST /api/chat` — process a user message, returning the detected intent, response, prior-context summary, and optionally a ticket id. Include `session_id` in the payload to maintain conversational memory across turns.
- `GET /api/chat/history/{session_id}` — fetch the most recent chat exchanges for a session (used by the playground UI to display memory).
- `POST /api/feedback` — capture 👍/👎 feedback for a chat response.
- `GET /api/tickets` — view created tickets.
- `GET /ui` — simple in-browser playground that posts to `/api/chat` and shows the server-side conversation memory.

## Project Structure

```
app/
  config.py        # Shared configuration
  db.py            # SQLite helpers and table initialization
  faq.py           # FAQ loader and similarity search
  intent.py        # Simple keyword-based intent detection
  llm.py           # OpenAI-backed response generator with safe fallback
  main.py          # FastAPI application and routes
  schemas.py       # Pydantic request/response models
  static/          # Lightweight HTML/JS playground served at /ui

data/
  faqs.json        # Sample FAQ pairs
```

The backend uses an in-memory similarity search over FAQs and the OpenAI Chat Completions API (with a graceful fallback) to craft answers. Ticket creation is triggered on low-confidence responses or explicit escalation intents, and all chat interactions are logged to SQLite for auditing.

### Conversation memory & escalation simulation

- Pass a `session_id` in `POST /api/chat` requests to thread related user messages together. The API will look up the five most recent exchanges in that session and include them in the generated response.
- The response payload echoes the `session_id` and provides a `context_summary` when an FAQ match is used so frontends can surface why a particular answer was chosen.
- Tickets are created automatically when intent is `escalation` **or** when the confidence score falls below the low-confidence threshold defined in `config.py`.

Example chat request:

```json
{
  "message": "I need help with a refund after 20 days",
  "session_id": "demo-session-1"
}
```

Example response fields:

```json
{
  "response": "Thanks for your question!...",
  "intent": "refund",
  "confidence": 0.72,
  "created_ticket": false,
  "ticket_id": null,
  "chat_log_id": 3,
  "session_id": "demo-session-1",
  "context_summary": "You can submit a refund request ..."
}
```

### Playground UI

- Start the API, then open `http://127.0.0.1:8000/ui` (or the forwarded Codespaces URL) in your browser.
- Enter a message and optional custom session id, then click **Send**. The UI calls `/api/chat`, displays the OpenAI-generated reply, and fetches recent server-side history via `/api/chat/history/{session_id}` so you can see what context is being used.
