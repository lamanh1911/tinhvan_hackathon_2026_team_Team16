import json
from typing import Protocol

import httpx

_EXTRACTION_SYSTEM_PROMPT = """You are a business card OCR assistant.
Extract fields from the text below and return ONLY valid JSON with this structure:
{
  "name":    {"value": string|null, "confidence": float},
  "company": {"value": string|null, "confidence": float},
  "title":   {"value": string|null, "confidence": float},
  "email":   {"value": string|null, "confidence": float},
  "phone":   {"value": string|null, "confidence": float},
  "address": {"value": string|null, "confidence": float}
}
Confidence is 0.0–1.0 reflecting certainty. Set value to null and confidence to 0.0 if not found."""

_MOCK_FIELDS: dict = {
    "name":    {"value": "Nguyen Van A",   "confidence": 0.95},
    "company": {"value": "ABC Corporation","confidence": 0.92},
    "title":   {"value": "Sales Manager",  "confidence": 0.88},
    "email":   {"value": "nva@abc.com",    "confidence": 0.65},
    "phone":   {"value": "090-1234-567",   "confidence": 0.72},
    "address": {"value": None,             "confidence": 0.0},
}


class LLMClientProtocol(Protocol):
    async def extract_card_fields(self, ocr_text: str) -> dict: ...


class MockLLMClient:
    async def extract_card_fields(self, ocr_text: str) -> dict:
        return _MOCK_FIELDS


class OpenRouterLLMClient:
    _MODEL = "google/gemini-flash-1.5"
    _BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str) -> None:
        self._api_key = api_key

    async def extract_card_fields(self, ocr_text: str) -> dict:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                self._BASE_URL,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "HTTP-Referer": "https://relay.app",
                    "X-Title": "Relay Card Scanner",
                },
                json={
                    "model": self._MODEL,
                    "messages": [
                        {"role": "system", "content": _EXTRACTION_SYSTEM_PROMPT},
                        {"role": "user", "content": ocr_text},
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)
