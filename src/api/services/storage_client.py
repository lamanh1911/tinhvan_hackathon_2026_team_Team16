from typing import Protocol
from uuid import uuid4

import boto3

from src.api.config import Settings


class StorageClientProtocol(Protocol):
    async def upload(self, key: str, data: bytes, content_type: str) -> str: ...


class MockStorageClient:
    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        return f"mock://storage/{key}"


class S3StorageClient:
    def __init__(self, settings: Settings) -> None:
        self._client = boto3.client(
            "s3",
            aws_access_key_id=settings.storage_access_key,
            aws_secret_access_key=settings.storage_secret_key,
            endpoint_url=settings.storage_endpoint,
        )
        self._bucket = settings.storage_bucket
        self._endpoint = settings.storage_endpoint

    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return f"{self._endpoint}/{self._bucket}/{key}"


def make_card_key(filename: str) -> str:
    return f"cards/{uuid4()}/{filename}"
