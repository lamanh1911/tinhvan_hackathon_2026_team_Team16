import base64
from typing import Protocol

import httpx


class VisionClientProtocol(Protocol):
    async def extract_text(self, image_bytes: bytes) -> str: ...


class MockVisionClient:
    async def extract_text(self, image_bytes: bytes) -> str:
        return (
            "Nguyen Van A\n"
            "Sales Manager\n"
            "ABC Corporation\n"
            "Email: nva@abc.com\n"
            "Tel: 090-1234-567\n"
        )


class GoogleVisionClient:
    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def extract_text(self, image_bytes: bytes) -> str:
        encoded = base64.b64encode(image_bytes).decode()
        payload = {
            "requests": [
                {
                    "image": {"content": encoded},
                    "features": [{"type": "TEXT_DETECTION"}],
                }
            ]
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"https://vision.googleapis.com/v1/images:annotate?key={self._api_key}",
                json=payload,
            )
            resp.raise_for_status()
            data = resp.json()
        annotations = data["responses"][0].get("textAnnotations", [])
        if not annotations:
            return ""
        return annotations[0].get("description", "")
