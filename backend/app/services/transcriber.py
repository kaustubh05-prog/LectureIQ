import logging
import os
from pathlib import Path
from groq import Groq
from app.config import settings

logger = logging.getLogger(__name__)
_client = Groq(api_key=settings.groq_api_key)


def transcribe_audio(audio_path: str, model_name: str = "whisper-large-v3") -> dict:
    """
    Transcribe audio using Groq Whisper API.
    Returns: { full_text, segments, language, backend }
    """
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    size_mb = path.stat().st_size / (1024 * 1024)
    logger.info("Transcribing %s (%.1f MB) via Groq Whisper...", path.name, size_mb)

    with open(audio_path, "rb") as f:
        response = _client.audio.transcriptions.create(
            model="whisper-large-v3",
            file=(path.name, f),
            response_format="verbose_json",
            timestamp_granularities=["segment"],
        )

    raw_segments = getattr(response, "segments", None) or []
    segments = []
    for seg in raw_segments:
        if isinstance(seg, dict):
            segments.append({
                "start": round(float(seg.get("start", 0)), 2),
                "end":   round(float(seg.get("end",   0)), 2),
                "text":  seg.get("text", "").strip(),
            })

    full_text = (response.text or "").strip()
    language  = getattr(response, "language", "en") or "en"

    logger.info(
        "Transcription done: %d chars, %d segments, lang=%s",
        len(full_text), len(segments), language
    )
    return {
        "full_text": full_text,
        "segments":  segments,
        "language":  language,
        "backend":   "groq-whisper",
    }
