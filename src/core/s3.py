import boto3
from src.core import config

# Use explicit credentials if provided (local dev), otherwise fall back to IAM role (ECS)
_credentials = {}
if config.AWS_ACCESS_KEY_ID and config.AWS_SECRET_ACCESS_KEY:
    _credentials = {
        "aws_access_key_id": config.AWS_ACCESS_KEY_ID,
        "aws_secret_access_key": config.AWS_SECRET_ACCESS_KEY,
    }

s3_client = boto3.client("s3", region_name=config.AWS_REGION, **_credentials)


def upload_file(content: bytes, s3_key: str) -> str:
    """Upload bytes to S3, return the s3_key."""
    s3_client.put_object(Bucket=config.S3_BUCKET, Key=s3_key, Body=content)
    return s3_key


def download_file(s3_key: str) -> bytes:
    """Download file from S3, return bytes."""
    response = s3_client.get_object(Bucket=config.S3_BUCKET, Key=s3_key)
    return response["Body"].read()


def delete_file(s3_key: str) -> None:
    """Delete file from S3."""
    s3_client.delete_object(Bucket=config.S3_BUCKET, Key=s3_key)
