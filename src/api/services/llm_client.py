import base64
import json
from typing import Protocol

import httpx

_EXTRACTION_PROMPT = """You are a business card OCR assistant.
Look at this business card image carefully and extract all text and fields.

Return ONLY valid JSON with this exact structure:
{
  "raw_text": "full verbatim text from the card",
  "name":      {"value": string|null, "confidence": float},
  "company":   {"value": string|null, "confidence": float},
  "job_title": {"value": string|null, "confidence": float},
  "email":     {"value": string|null, "confidence": float},
  "phone":     {"value": string|null, "confidence": float},
  "address":   {"value": string|null, "confidence": float},
  "website":   {"value": string|null, "confidence": float}
}

Rules:
- confidence is 0.0–1.0 reflecting how certain you are
- Set value to null and confidence to 0.0 if a field is not found
- For phone: include country code if visible
- For website: include domain only (strip http/https)
- raw_text: copy all visible text exactly as it appears"""

_MOCK_FIELDS: dict = {
    "raw_text": "Nguyen Van A\nSales Manager\nABC Corporation\nEmail: nva@abc.com\nTel: 090-1234-567\nwww.abc.com",
    "name":      {"value": "Nguyen Van A",    "confidence": 0.95},
    "company":   {"value": "ABC Corporation", "confidence": 0.92},
    "job_title": {"value": "Sales Manager",   "confidence": 0.88},
    "email":     {"value": "nva@abc.com",     "confidence": 0.95},
    "phone":     {"value": "090-1234-567",    "confidence": 0.90},
    "address":   {"value": None,              "confidence": 0.0},
    "website":   {"value": "abc.com",         "confidence": 0.85},
}


class LLMClientProtocol(Protocol):
    async def extract_from_image(self, image_bytes: bytes, content_type: str) -> tuple[str, dict]: ...


class MockLLMClient:
    async def extract_from_image(self, image_bytes: bytes, content_type: str) -> tuple[str, dict]:
        raw_text = _MOCK_FIELDS["raw_text"]
        fields = {k: v for k, v in _MOCK_FIELDS.items() if k != "raw_text"}
        return raw_text, fields


class GeminiVisionClient:
    """Single-call OCR + field extraction via vision model on OpenRouter."""

    _BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, model: str = "google/gemini-2.5-flash") -> None:
        self._api_key = api_key
        self._model = model

    async def extract_from_image(self, image_bytes: bytes, content_type: str) -> tuple[str, dict]:
        encoded = base64.b64encode(image_bytes).decode()
        data_url = f"data:{content_type};base64,{encoded}"

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                self._BASE_URL,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "HTTP-Referer": "https://relay.app",
                    "X-Title": "Relay Card Scanner",
                },
                json={
                    "model": self._model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": data_url},
                                },
                                {
                                    "type": "text",
                                    "text": _EXTRACTION_PROMPT,
                                },
                            ],
                        }
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            data = json.loads(content)

        raw_text: str = data.pop("raw_text", "")
        return raw_text, data
