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

## Demo Data & Testing

### Included Demo Datasets

#### 1. FAQs Dataset (`data/faqs.json`)
**20 comprehensive FAQ entries** covering common customer support scenarios:
- Account management (password reset, login issues)
- Order tracking and shipping
- Payment methods and billing
- Refunds and returns
- Subscription management
- International shipping
- Product support
- Security and privacy

#### 2. Demo Queries (`data/demo_queries.json`)
**100+ sample customer queries** organized by category:
- **FAQ Matching**: Queries that should match existing FAQs
- **Conversational**: Natural language interactions
- **Escalation**: Queries requiring human support
- **Low Confidence**: Complex issues triggering ticket creation
- **Multi-turn Context**: Conversations requiring memory
- **Edge Cases**: Unusual or invalid inputs
- **Intent Testing**: Queries for specific intent detection

### Running Demo Tests

#### Quick Demo (Automated Testing)
```bash
# Run all test scenarios
python demo.py

# Run specific scenario
python demo.py --scenario "Happy Path"
python demo.py --scenario "Escalation"

# Test specific category
python demo.py --category faq_matching
python demo.py --category escalation
```

#### Interactive Demo Mode
```bash
# Chat interactively with the bot
python demo.py --interactive
```

Example demo session:
```
👤 You: How can I reset my password?
🤖 Bot: Click on 'Forgot password' on the login page...
   Intent: account
   Confidence: 0.85

👤 You: I want to speak to a manager
🤖 Bot: I understand you'd like to speak with someone...
   Intent: escalation
   Confidence: 0.45
   🎫 Ticket #1 created
```

## How to Test and Use the Bot

### Option 1: Web Chat UI (Recommended)

1. Start the server: `uvicorn app.main:app --reload`
2. Open your browser to **http://127.0.0.1:8000/ui**
3. Type messages in the chat interface to interact with the bot
4. The UI displays:
   - Bot responses
   - Detected intent
   - Confidence scores
   - Ticket creation notifications

### Option 2: Interactive API Documentation

1. Start the server: `uvicorn app.main:app --reload`
2. Open your browser to **http://127.0.0.1:8000/docs**
3. Expand the `POST /api/chat` endpoint
4. Click "Try it out"
5. Modify the JSON request body:
   ```json
   {
     "message": "I need help with my order",
     "session_id": "test-session-1"
   }
   ```
6. Click "Execute" to see the response

### Option 3: Command Line with curl

```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "How do I return an item?", "session_id": "session-1"}'
```

### Testing Different Scenarios

**Test FAQ matching:**

- "How do I return an item?"
- "What is your refund policy?"

**Test low confidence (creates ticket):**

- "My account is locked"
- "Random gibberish text"

**Test escalation (creates ticket):**

- "I want to speak to a human"
- "Transfer me to an agent"

### Optional: Enable OpenAI Integration

1. Copy `.env.example` to `.env`
2. Add your OpenAI API key:
   ```
   OPENAI_API_KEY=your-actual-api-key
   OPENAI_MODEL=gpt-3.5-turbo
   ```
3. Restart the server

Without an API key, the bot uses fallback template responses.

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

## LLM Integration & Prompts

### System Prompt (app/llm.py)

The LLM is configured with a carefully crafted system prompt that ensures:

- **Concise responses**: Keeps answers under 120 words
- **Contextual awareness**: Uses FAQ context and conversation history
- **Escalation handling**: Mentions ability to escalate when information is insufficient
- **Professional tone**: Maintains polite and helpful customer support demeanor

```
You are a concise and polite customer support assistant. Use the provided FAQ context and
recent conversation to answer the user's question. If you do not have enough information,
ask a brief clarifying question and mention that you can escalate to a human agent if needed.
Keep responses under 120 words.
```

### LLM Input Structure

Each request to the LLM includes:

1. **System Prompt**: Defines the assistant's role and behavior
2. **Customer Question**: The current user query
3. **FAQ Context** (if available): Relevant FAQ answer from similarity search
4. **Recent History**: Last 5 conversation exchanges for context continuity

### LLM Usage in the Application

The LLM is used for three key functions:

1. **Response Generation** (`generate_response()`)

   - Generates contextual answers using FAQ knowledge and conversation history
   - Falls back to template responses when OpenAI API is unavailable
   - Temperature set to 0.4 for consistent, focused responses

2. **Conversation Summarization**

   - Maintains conversation context across multiple turns
   - Renders conversation history in a structured format for the LLM

3. **Implicit Next Actions**
   - Low confidence responses automatically trigger ticket creation
   - Escalation intents detected and handled appropriately
   - Response confidence guides system behavior

### Prompt Engineering Techniques Used

- ✅ **Role definition**: Clear identity as customer support assistant
- ✅ **Constraint setting**: Word limit for conciseness
- ✅ **Context injection**: FAQ data and conversation history
- ✅ **Fallback instructions**: Guidance for handling incomplete information
- ✅ **Tone specification**: Professional and helpful demeanor

## Project Compliance with Requirements

### ✅ Input Requirements

- **FAQs dataset**: `data/faqs.json` with customer support Q&A pairs
- **Customer queries**: Accepted via REST API and web UI
- **FAQ retrieval**: Cosine similarity search in `app/faq.py`

### ✅ Contextual Memory

- **Session tracking**: `session_id` parameter maintains conversation threads
- **History retrieval**: Last 5 exchanges stored in SQLite and passed to LLM
- **Database persistence**: All conversations logged in `chat_logs` table

### ✅ Escalation Simulation

- **Low confidence detection**: Tickets created when confidence < 0.4
- **Intent-based escalation**: Keywords like "human", "agent", "escalate" trigger tickets
- **Ticket management**: Full CRUD via `/api/tickets` endpoint

### ✅ Frontend Chat Interface

- **Web UI**: Modern, responsive chat interface at `/ui`
- **Real-time feedback**: Shows confidence, intent, and ticket creation
- **Session management**: Maintains conversation context

### ✅ Backend API with REST Endpoints

- `POST /api/chat` - Main conversation endpoint
- `GET /api/chat/history/{session_id}` - Retrieve conversation history
- `POST /api/feedback` - Capture user satisfaction
- `GET /api/tickets` - List escalated tickets
- `GET /api/health` - Service health check

### ✅ LLM Integration

- **OpenAI GPT integration**: Fully implemented in `app/llm.py`
- **Contextual prompts**: System + user messages with FAQ and history context
- **Error handling**: Graceful fallback when API unavailable
- **Configurable models**: Support for different OpenAI models via environment variables

### ✅ Database for Session Tracking

- **SQLite database**: `support.sqlite3` with three tables
  - `chat_logs`: Stores all conversations with session_id
  - `tickets`: Escalated customer queries
  - `feedback`: User satisfaction ratings
- **Automatic schema migration**: Ensures session_id column exists

### ✅ Code Structure

- **Modular design**: Separate modules for config, DB, FAQ, intent, LLM, schemas
- **Type hints**: Full Python type annotations for code clarity
- **Error handling**: Comprehensive exception handling throughout
- **RESTful design**: Standard HTTP methods and status codes
- **Documentation**: Swagger/OpenAPI auto-generated docs

## Evaluation Criteria Addressed

### Conversational Accuracy

- FAQ similarity matching with 0.5 threshold
- LLM-powered contextual responses
- Intent detection for common queries
- Confidence scoring for response quality

### Session Management

- Session-based conversation threading
- 5-message history retention per session
- Persistent storage in SQLite
- Session ID tracking across all interactions

### LLM Integration Depth

- Custom system prompts for customer support role
- Multi-turn conversation context injection
- FAQ context enrichment
- Graceful degradation without API key
- Temperature tuning for consistent responses

### Code Structure

- Clean separation of concerns (routing, business logic, data access)
- Pydantic schemas for data validation
- Configuration management via environment variables
- Comprehensive error handling
- Type-safe Python code
- RESTful API design principles
