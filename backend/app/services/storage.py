import logging
import os
import tempfile
from pathlib import Path
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)
UPLOAD_DIR = Path("uploads")


def _is_supabase_configured() -> bool:
    key    = settings.aws_access_key_id       # reused for Supabase anon key
    secret = settings.aws_secret_access_key   # reused for Supabase secret
    placeholders = {"", "your_aws_access_key", "YOUR_ACCESS_KEY",
                    "your_aws_secret_key",  "YOUR_SECRET_KEY"}
    return (bool(key) and bool(secret) and
            key not in placeholders and secret not in placeholders)


class StorageService:
    """
    Dual-backend storage:
    ┌─────────────────┬────────────────────────────────────────┐
    │ supabase        │ SUPABASE_URL set in .env               │
    │ local (default) │ dev / no credentials                   │
    └─────────────────┴────────────────────────────────────────┘
    """

    def __init__(self):
        supabase_url = getattr(settings, "supabase_url", None)
        if supabase_url and _is_supabase_configured():
            self.backend = "supabase"
            import boto3
            # Supabase Storage is S3-compatible
            self._s3 = boto3.client(
                "s3",
                endpoint_url=f"{supabase_url}/storage/v1/s3",
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name="auto",
            )
            self._bucket = settings.s3_bucket_name
            logger.info("StorageService → Supabase Storage (bucket: %s)", self._bucket)
        else:
            self.backend = "local"
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            logger.info("StorageService → LOCAL backend (%s)", UPLOAD_DIR.resolve())

    # ── Write ──────────────────────────────────────────────────────────
    def save_audio(self, file_bytes: bytes, lecture_id: str, extension: str) -> str:
        ext = extension.lstrip(".").lower()
        if self.backend == "supabase":
            key = f"lectures/{lecture_id}.{ext}"
            self._s3.put_object(
                Bucket=self._bucket,
                Key=key,
                Body=file_bytes,
                ContentType=f"audio/{ext}",
            )
            logger.info("Saved to Supabase Storage: %s", key)
            return key
        # local
        path = UPLOAD_DIR / f"{lecture_id}.{ext}"
        path.write_bytes(file_bytes)
        logger.info("Saved locally: %s", path)
        return str(path.resolve())

    # ── Read ───────────────────────────────────────────────────────────
    def get_local_path(self, storage_key: str) -> str:
        if self.backend == "local":
            p = Path(storage_key)
            if not p.exists():
                raise FileNotFoundError(f"Audio file not found: {storage_key}")
            return str(p)
        # Download from Supabase to temp file
        suffix = Path(storage_key).suffix or ".mp3"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.close()
        try:
            self._s3.download_file(self._bucket, storage_key, tmp.name)
            logger.info("Supabase → temp: %s → %s", storage_key, tmp.name)
            return tmp.name
        except Exception as e:
            os.unlink(tmp.name)
            logger.error("Supabase download failed: %s", e)
            raise

    # ── Delete ─────────────────────────────────────────────────────────
    def delete_audio(self, storage_key: str) -> None:
        if self.backend == "supabase":
            try:
                self._s3.delete_object(Bucket=self._bucket, Key=storage_key)
                logger.info("Deleted from Supabase Storage: %s", storage_key)
            except Exception as e:
                logger.warning("Supabase delete failed (non-fatal): %s", e)
        else:
            path = Path(storage_key)
            if path.exists():
                path.unlink()
                logger.info("Deleted local: %s", storage_key)

    def get_backend(self) -> str:
        return self.backend


storage_service = StorageService()
