import boto3
import logging
from botocore.exceptions import ClientError
from app.config import settings

logger = logging.getLogger(__name__)

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.aws_access_key_id,
    aws_secret_access_key=settings.aws_secret_access_key,
    region_name=settings.aws_region,
)


def upload_file_to_s3(file_bytes: bytes, s3_key: str, content_type: str) -> str:
    """Upload bytes to S3, return the S3 key."""
    try:
        s3_client.put_object(
            Bucket=settings.s3_bucket_name,
            Key=s3_key,
            Body=file_bytes,
            ContentType=content_type,
            ServerSideEncryption="AES256",
        )
        logger.info(f"Uploaded to S3: {s3_key}")
        return s3_key
    except ClientError as e:
        logger.error(f"S3 upload failed: {e}")
        raise


def get_presigned_url(s3_key: str, expiry: int = 3600) -> str:
    """Generate a presigned URL for temporary access."""
    return s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket_name, "Key": s3_key},
        ExpiresIn=expiry,
    )


def delete_file_from_s3(s3_key: str) -> None:
    """Delete a file from S3."""
    try:
        s3_client.delete_object(Bucket=settings.s3_bucket_name, Key=s3_key)
        logger.info(f"Deleted from S3: {s3_key}")
    except ClientError as e:
        logger.error(f"S3 delete failed: {e}")
        raise


def download_file_from_s3(s3_key: str, local_path: str) -> None:
    """Download a file from S3 to local path."""
    try:
        s3_client.download_file(settings.s3_bucket_name, s3_key, local_path)
        logger.info(f"Downloaded from S3: {s3_key} → {local_path}")
    except ClientError as e:
        logger.error(f"S3 download failed: {e}")
        raise
