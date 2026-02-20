import os
import logging
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Whisper Backend Detection
# Try openai-whisper first (as stated in PPT), fall back to faster-whisper
# ---------------------------------------------------------------------------

_BACKEND = None  # "openai" or "faster"
_MODEL = None


def _load_model(model_name: str = "base"):
    """Load Whisper model — tries openai-whisper first, faster-whisper second."""
    global _BACKEND, _MODEL

    if _MODEL is not None:
        return _MODEL

    # --- Primary: openai-whisper ---
    try:
        import whisper
        logger.info(f"Loading openai-whisper model '{model_name}'...")
        _MODEL = whisper.load_model(model_name)
        _BACKEND = "openai"
        logger.info("✅ openai-whisper loaded successfully")
        return _MODEL
    except ImportError:
        logger.warning("openai-whisper not installed — falling back to faster-whisper")
    except Exception as e:
        logger.warning(f"openai-whisper failed to load ({e}) — falling back to faster-whisper")

    # --- Fallback: faster-whisper ---
    try:
        from faster_whisper import WhisperModel
        logger.info(f"Loading faster-whisper model '{model_name}'...")
        _MODEL = WhisperModel(model_name, device="cpu", compute_type="int8")
        _BACKEND = "faster"
        logger.info("✅ faster-whisper loaded as fallback")
        return _MODEL
    except ImportError:
        raise RuntimeError(
            "Neither openai-whisper nor faster-whisper is installed. "
            "Run: pip install openai-whisper  OR  pip install faster-whisper"
        )


def get_whisper_backend() -> str:
    """Returns which backend is active: 'openai' or 'faster'."""
    if _BACKEND is None:
        _load_model()
    return _BACKEND


# ---------------------------------------------------------------------------
# Unified Transcription API
# ---------------------------------------------------------------------------

def transcribe_audio(audio_path: str, model_name: str = "base") -> dict:
    """
    Transcribe an audio file using Whisper.

    Returns:
        {
            "full_text": str,
            "segments": [{"start": float, "end": float, "text": str}],
            "language": str,
            "backend": "openai" | "faster"
        }

    Raises:
        RuntimeError: if transcription fails on both backends
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    model = _load_model(model_name)

    logger.info(f"Transcribing '{audio_path}' using {_BACKEND}-whisper...")

    if _BACKEND == "openai":
        return _transcribe_openai(model, audio_path)
    else:
        return _transcribe_faster(model, audio_path)


def _transcribe_openai(model, audio_path: str) -> dict:
    """Transcription using openai-whisper."""
    try:
        result = model.transcribe(
            audio_path,
            fp16=False,          # CPU-safe
            task="transcribe",
            verbose=False,
        )

        segments = [
            {
                "start": round(seg["start"], 2),
                "end": round(seg["end"], 2),
                "text": seg["text"].strip(),
            }
            for seg in result.get("segments", [])
        ]

        full_text = result.get("text", "").strip()
        language = result.get("language", "unknown")

        logger.info(f"Transcription complete — {len(segments)} segments, lang={language}")

        return {
            "full_text": full_text,
            "segments": segments,
            "language": language,
            "backend": "openai",
        }
    except Exception as e:
        logger.error(f"openai-whisper transcription failed: {e}")
        raise RuntimeError(f"Transcription failed: {e}")


def _transcribe_faster(model, audio_path: str) -> dict:
    """Transcription using faster-whisper."""
    try:
        segments_iter, info = model.transcribe(
            audio_path,
            beam_size=5,
            task="transcribe",
        )

        segments = []
        text_parts = []

        for seg in segments_iter:
            segments.append({
                "start": round(seg.start, 2),
                "end": round(seg.end, 2),
                "text": seg.text.strip(),
            })
            text_parts.append(seg.text.strip())

        full_text = " ".join(text_parts)
        language = info.language if hasattr(info, "language") else "unknown"

        logger.info(f"Transcription complete — {len(segments)} segments, lang={language}")

        return {
            "full_text": full_text,
            "segments": segments,
            "language": language,
            "backend": "faster",
        }
    except Exception as e:
        logger.error(f"faster-whisper transcription failed: {e}")
        raise RuntimeError(f"Transcription failed: {e}")
