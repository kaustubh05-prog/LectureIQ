# LectureIQ — AI Learning Co-Pilot

> Upload a lecture recording → get structured notes, flashcards, MCQs, and curated resources in under 3 minutes.

Built for **AWS AI for Bharat Hackathon 2026** by Team CodeShiksha.

---

## What It Does

Indian college students attend 4–6 hours of lectures daily but retain less than 30% without effective notes. LectureIQ automates the entire study-material creation pipeline:

1. **Upload** — Drag and drop an MP3/WAV/M4A lecture recording
2. **Transcribe** — OpenAI Whisper transcribes audio (Hindi + English)
3. **Generate** — Groq (Llama 3.1 70B) creates notes, flashcards, MCQs
4. **Discover** — YouTube API links relevant tutorial videos
5. **Study** — Interactive flashcards, quiz, and resource browser

---

## Project Structure

```
lectureiq-web/
├── backend/              # FastAPI + Celery + AI pipeline
├── frontend/             # React 18 + Vite + TailwindCSS
├── docs/                 # Architecture diagrams, screenshots
├── requirements.md       # Product requirements
├── design.md             # System design document
├── PLANNING.md           # High-level direction and scope
├── TASKS.md              # Task tracker
├── docker-compose.yml
└── README.md
```

---

## Tech Stack

| Layer         | Technology                                      |
|---------------|-------------------------------------------------|
| Frontend      | React 18, Vite, TailwindCSS, Zustand            |
| Backend       | FastAPI, Python 3.11, SQLAlchemy                |
| Task Queue    | Celery + Redis (Upstash)                        |
| Transcription | OpenAI Whisper (base) → faster-whisper fallback |
| LLM           | Groq API — Llama 3.1 70B (free)                 |
| NLP           | spaCy 3.7 (en_core_web_sm)                      |
| Resources     | YouTube Data API v3                             |
| Database      | PostgreSQL (Supabase free tier)                 |
| Audio Storage | AWS S3 (free tier, ap-south-1)                  |
| Deployment    | Render (backend) + Vercel (frontend)            |

---

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker + Docker Compose
- Git

### Quick Start

```bash
# 1. Clone
git clone https://github.com/your-org/lectureiq-web.git
cd lectureiq-web

# 2. Start Postgres + Redis
docker-compose up -d

# 3. Backend
cd backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env           # Fill in your API keys
uvicorn app.main:app --reload  # → http://localhost:8000/docs

# 4. Celery Worker (new terminal)
cd backend
source venv/bin/activate
celery -A app.celery_app worker --loglevel=info -Q lectures

# 5. Frontend (new terminal)
cd frontend
npm install
cp .env.example .env           # Set VITE_API_URL=http://localhost:8000
npm run dev                    # → http://localhost:5173
```

### Environment Variables

| File            | Copy From               |
|-----------------|-------------------------|
| `backend/.env`  | `backend/.env.example`  |
| `frontend/.env` | `frontend/.env.example` |

---

## API Documentation

Once the backend is running:

- **Swagger UI** → http://localhost:8000/docs
- **ReDoc** → http://localhost:8000/redoc
- **Health check** → http://localhost:8000/health

---

## Production Deployment

| Service     | Provider | URL                       |
|-------------|----------|---------------------------|
| Backend API | Render   | https://api.lectureiq.app |
| Frontend    | Vercel   | https://lectureiq.app     |
| Database    | Supabase | (managed)                 |
| Redis       | Upstash  | (managed)                 |
| Audio Files | AWS S3   | ap-south-1                |

---

## Cost Estimate (Hackathon Period)

| Service       | Cost            |
|---------------|-----------------|
| Whisper       | $0 (local)      |
| Groq API      | $0 (free tier)  |
| YouTube API   | $0 (free tier)  |
| AWS S3        | $0 (< 5 GB)     |
| Supabase      | $0 (< 500 MB)   |
| Upstash Redis | $0 (free tier)  |
| Hosting       | $0 (free tiers) |
| **Total**     | **~$0–5**       |

---

## Processing Pipeline

```
Upload Audio (MP3/WAV/M4A)
        ↓
S3 storage + Lecture record created
Celery task triggered
        ↓
Download audio from S3
OpenAI Whisper transcription (~1–2 min per hour)
        ↓
Segments saved to DB
spaCy topic extraction
        ↓
Groq LLM generation — notes + flashcards + MCQs (~30–60 sec)
        ↓
YouTube API resource linking (~5–10 sec)
        ↓
All results saved to PostgreSQL
Status → "completed" — Frontend renders materials
```