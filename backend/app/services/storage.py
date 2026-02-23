import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads")


def _is_s3_configured() -> bool:
    """Returns True only if real (non-placeholder) AWS credentials are set."""
    key = settings.aws_access_key_id
    secret = settings.aws_secret_access_key
    placeholders = {
        "", "your_aws_access_key", "YOUR_ACCESS_KEY",
        "your_aws_secret_key", "YOUR_SECRET_KEY",
    }
    return (
        bool(key) and bool(secret) and
        key not in placeholders and
        secret not in placeholders
    )


class StorageService:
    """
    Dual-backend storage service.

    ┌─────────────────┬──────────────────────────────────────────┐
    │ Backend         │ When                                     │
    ├─────────────────┼──────────────────────────────────────────┤
    │ local (default) │ AWS keys missing/placeholder in .env     │
    │ s3              │ Real AWS_ACCESS_KEY_ID + SECRET present  │
    └─────────────────┴──────────────────────────────────────────┘

    To switch from local → S3: add real keys to .env, restart server.
    Zero code change needed.
    """

    def __init__(self):
        if _is_s3_configured():
            self.backend = "s3"
            import boto3
            self._s3 = boto3.client(
                "s3",
                aws_access_key_id=settings.aws_access_key_id,
                aws_secret_access_key=settings.aws_secret_access_key,
                region_name=settings.aws_region,
            )
            logger.info("StorageService → S3 backend (bucket: %s)", settings.s3_bucket_name)
        else:
            self.backend = "local"
            UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
            logger.info("StorageService → LOCAL backend (%s)", UPLOAD_DIR.resolve())

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    def save_audio(self, file_bytes: bytes, lecture_id: str, extension: str) -> str:
        """
        Persist audio bytes.

        Returns a storage key:
          - S3:    "lectures/{lecture_id}.{ext}"
          - local: absolute path string
        """
        ext = extension.lstrip(".").lower()

        if self.backend == "s3":
            key = f"lectures/{lecture_id}.{ext}"
            self._upload_s3(file_bytes, key, f"audio/{ext}")
            return key

        # Local
        path = UPLOAD_DIR / f"{lecture_id}.{ext}"
        path.write_bytes(file_bytes)
        logger.info("Saved locally: %s", path)
        return str(path.resolve())

    # ------------------------------------------------------------------
    # Read — always returns a local filesystem path for Whisper
    # ------------------------------------------------------------------

    def get_local_path(self, storage_key: str) -> str:
        """
        For S3: downloads the object to a temp file, returns that path.
        For local: validates the path exists, returns it directly.
        The Celery task cleans up temp files after transcription.
        """
        if self.backend == "local":
            p = Path(storage_key)
            if not p.exists():
                raise FileNotFoundError(f"Audio file not found: {storage_key}")
            return str(p)

        # S3 — download to a named temp file
        suffix = Path(storage_key).suffix or ".mp3"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        tmp.close()
        try:
            from botocore.exceptions import ClientError
            self._s3.download_file(settings.s3_bucket_name, storage_key, tmp.name)
            logger.info("S3 → local temp: %s → %s", storage_key, tmp.name)
            return tmp.name
        except Exception as e:
            os.unlink(tmp.name)
            logger.error("S3 download failed: %s", e)
            raise

    # ------------------------------------------------------------------
    # Delete
    # ------------------------------------------------------------------

    def delete_audio(self, storage_key: str) -> None:
        if self.backend == "s3":
            try:
                self._s3.delete_object(Bucket=settings.s3_bucket_name, Key=storage_key)
                logger.info("Deleted from S3: %s", storage_key)
            except Exception as e:
                logger.warning("S3 delete failed (non-fatal): %s", e)
        else:
            path = Path(storage_key)
            if path.exists():
                path.unlink()
                logger.info("Deleted local file: %s", storage_key)

    # ------------------------------------------------------------------
    # Info
    # ------------------------------------------------------------------

    def get_backend(self) -> str:
        return self.backend

    def get_presigned_url(self, storage_key: str, expiry: int = 3600) -> Optional[str]:
        """Only available for S3 backend. Returns None for local."""
        if self.backend != "s3":
            return None
        return self._s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": settings.s3_bucket_name, "Key": storage_key},
            ExpiresIn=expiry,
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _upload_s3(self, file_bytes: bytes, key: str, content_type: str) -> None:
        try:
            self._s3.put_object(
                Bucket=settings.s3_bucket_name,
                Key=key,
                Body=file_bytes,
                ContentType=content_type,
                ServerSideEncryption="AES256",
            )
            logger.info("Uploaded to S3: %s", key)
        except Exception as e:
            logger.error("S3 upload failed: %s", e)
            raise


# Singleton — imported by API routes and Celery tasks
storage_service = StorageService()
