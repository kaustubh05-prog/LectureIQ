# LectureIQ — Backend

FastAPI backend with async Celery task processing, OpenAI Whisper transcription, Groq LLM generation, and PostgreSQL storage.

---

## Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app, CORS, routers, lifespan
│   ├── config.py            # Settings via pydantic-settings (.env)
│   ├── database.py          # SQLAlchemy engine, session, Base
│   ├── celery_app.py        # Celery instance + config
│   │
│   ├── api/                 # Route handlers (thin — call services)
│   │   ├── auth.py          # POST /api/auth/register, /login
│   │   ├── lectures.py      # CRUD + upload + status
│   │   └── study.py         # Quiz submit
│   │
│   ├── models/              # SQLAlchemy ORM models
│   │   ├── user.py
│   │   ├── lecture.py       # ProcessingStatus enum lives here
│   │   ├── transcript.py
│   │   ├── note.py
│   │   ├── flashcard.py
│   │   ├── mcq.py
│   │   ├── resource.py
│   │   └── quiz_attempt.py
│   │
│   ├── schemas/             # Pydantic request/response schemas
│   │   ├── auth.py
│   │   ├── lecture.py
│   │   └── study.py
│   │
│   ├── services/            # Business logic (pure functions)
│   │   ├── transcriber.py   # Whisper wrapper (openai → faster fallback)
│   │   ├── generator.py     # Groq: notes, flashcards, MCQs
│   │   ├── resource_linker.py  # YouTube + docs + practice links
│   │   └── storage.py       # S3 upload/download/delete
│   │
│   ├── tasks/               # Celery tasks
│   │   └── process_lecture.py  # Main pipeline task
│   │
│   └── utils/               # Shared helpers
│       ├── auth.py          # JWT encode/decode, get_current_user
│       └── s3.py            # Boto3 helpers
│
├── tests/
│   ├── test_auth.py
│   ├── test_upload.py
│   └── test_pipeline.py
│
├── .env                     # Local secrets (git-ignored)
├── .env.example             # Template for env vars
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your actual keys

# Start Postgres + Redis (from root)
docker-compose up -d

# Run development server
uvicorn app.main:app --reload
```

### Running the Celery Worker

The worker must run separately from the API server. Open a new terminal:

```bash
# Activate venv first
source venv/bin/activate

# Start worker — listens on 'lectures' queue
celery -A app.celery_app worker --loglevel=info -Q lectures

# Monitor tasks (optional)
celery -A app.celery_app flower
```

---

## API Endpoints

### Auth

| Method | Endpoint               | Description      | Auth Required |
|--------|------------------------|------------------|---------------|
| POST   | `/api/auth/register`   | Create account   | No            |
| POST   | `/api/auth/login`      | Get JWT token    | No            |

### Lectures

| Method | Endpoint                    | Description               | Auth Required |
|--------|-----------------------------|---------------------------|---------------|
| POST   | `/api/lectures/upload`      | Upload audio file         | Yes           |
| GET    | `/api/lectures`             | List user's lectures      | Yes           |
| GET    | `/api/lectures/{id}`        | Get full lecture detail   | Yes           |
| GET    | `/api/lectures/{id}/status` | Poll processing status    | Yes           |
| DELETE | `/api/lectures/{id}`        | Delete lecture + S3 file  | Yes           |

### Study Tools

| Method | Endpoint                          | Description          | Auth Required |
|--------|-----------------------------------|----------------------|---------------|
| POST   | `/api/lectures/{id}/quiz/submit`  | Submit quiz answers  | Yes           |

---

## Database Models

```
users           id, email, password_hash, name, created_at
lectures        id, user_id, title, s3_key, status, progress,
                error_message, uploaded_at, processed_at
transcripts     id, lecture_id, full_text, segments (JSON), language
notes           id, lecture_id, content (markdown), key_concepts (JSON)
flashcards      id, lecture_id, question, answer, order
mcqs            id, lecture_id, question, options (JSON),
                correct_index, explanation, order
resources       id, lecture_id, type, title, url, thumbnail_url, topic
quiz_attempts   id, user_id, lecture_id, score, total, answers (JSON)
```

---

## Whisper Backend

The transcription service (`app/services/transcriber.py`) auto-selects:

| Priority | Backend          | Status                             |
|----------|------------------|------------------------------------|
| Primary  | `openai-whisper` | Preferred                          |
| Fallback | `faster-whisper` | Auto-activates if openai fails     |

To check which is active:

```python
from app.services.transcriber import get_whisper_backend
print(get_whisper_backend())  # "openai" or "faster"
```

---

## Running Tests

```bash
pytest tests/ -v
pytest tests/test_auth.py -v     # Auth tests only
pytest tests/ -v --tb=short      # Short tracebacks
```

---

## Deployment (Render.com)

1. Connect GitHub repo to Render
2. **Web Service** — `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Background Worker** — `celery -A app.celery_app worker --loglevel=info -Q lectures`
4. Set all env vars in the Render dashboard
5. Render uses `Dockerfile` automatically if present