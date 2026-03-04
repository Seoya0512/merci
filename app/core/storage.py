import asyncio
import uuid
from functools import partial

import boto3
from botocore.config import Config

from app.core.config import settings


def get_r2_client():
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.CF_ACCOUNT_ID}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.CF_R2_ACCESS_KEY_ID,
        aws_secret_access_key=settings.CF_R2_SECRET_ACCESS_KEY,
        config=Config(signature_version="s3v4"),
        region_name="auto",
    )


def generate_presigned_url(object_key: str, content_type: str, expires_in: int = 900) -> str:
    client = get_r2_client()
    return client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": settings.CF_R2_BUCKET_NAME,
            "Key": object_key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in,
    )


async def move_object(source_key: str, dest_key: str) -> None:
    loop = asyncio.get_event_loop()
    client = get_r2_client()

    copy_source = {"Bucket": settings.CF_R2_BUCKET_NAME, "Key": source_key}

    await loop.run_in_executor(
        None,
        partial(
            client.copy_object,
            Bucket=settings.CF_R2_BUCKET_NAME,
            CopySource=copy_source,
            Key=dest_key,
        ),
    )
    await loop.run_in_executor(
        None,
        partial(
            client.delete_object,
            Bucket=settings.CF_R2_BUCKET_NAME,
            Key=source_key,
        ),
    )


async def delete_object(object_key: str) -> None:
    loop = asyncio.get_event_loop()
    client = get_r2_client()

    await loop.run_in_executor(
        None,
        partial(
            client.delete_object,
            Bucket=settings.CF_R2_BUCKET_NAME,
            Key=object_key,
        ),
    )


def generate_presigned_get_url(object_key: str, expires_in: int = 3600) -> str:
    """조회용 presigned GET URL 생성 (기본 1시간 유효)."""
    client = get_r2_client()
    return client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.CF_R2_BUCKET_NAME,
            "Key": object_key,
        },
        ExpiresIn=expires_in,
    )


def public_url(object_key: str) -> str:
    return f"{settings.CF_R2_PUBLIC_URL.rstrip('/')}/{object_key}"


def object_key_from_url(url: str) -> str:
    """저장된 URL에서 object_key를 추출한다."""
    base = settings.CF_R2_PUBLIC_URL.rstrip("/")
    return url.removeprefix(base + "/")
