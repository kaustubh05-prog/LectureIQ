import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.api import auth, lectures, study

# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.app_debug else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create all DB tables on startup."""
    logger.info("Starting LectureIQ API...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified.")
    yield
    logger.info("Shutting down LectureIQ API.")


app = FastAPI(
    title="LectureIQ API",
    description="AI-powered lecture-to-learning-system",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS — allow frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(lectures.router, prefix="/api/lectures", tags=["Lectures"])
app.include_router(study.router, prefix="/api/lectures", tags=["Study Tools"])


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "env": settings.app_env}
