import base64
import json
from typing import Protocol

import httpx

_CARD_VALIDATION_PROMPT = """You are a business card validator and OCR extractor.

Step 1 — Is this a business card (name card / visiting card)?
A valid business card contains: person name, company name, job title/role, and at least one contact method (email, phone, website, or address), with a business-style layout.
If YES → skip to Step 3.

Step 2 — Is this a different type of card?
Check if the image is any of the following non-business cards:
- Bank card, credit card, debit card (16-digit card number, Visa/Mastercard/JCB/AMEX logo)
- Loyalty card, membership card, points card, reward card
- Gift card, prepaid card, store card
- ID card, driver's license, passport, employee badge
If YES → return IMMEDIATELY:
{
  "is_valid_card": false,
  "error_code": "WRONG_CARD_TYPE",
  "error_message": "Uploaded image appears to be a bank card or membership card, not a business card",
  "fields": null
}

If the image is something else entirely (selfie, photo, landscape, food, receipt, invoice, blank, handwritten memo, unrelated document) → return IMMEDIATELY:
{
  "is_valid_card": false,
  "error_code": "INVALID_CARD_TYPE",
  "error_message": "Uploaded image is not a valid business card",
  "fields": null
}

Step 3 — Extract fields from the business card.
Rules:
- Do not hallucinate — extract only visible text
- Return null for any field you cannot read with reasonable certainty
- confidence is 0.0–1.0 reflecting certainty

Return this exact JSON:
{
  "is_valid_card": true,
  "error_code": null,
  "error_message": null,
  "fields": {
    "name":      {"value": "string|null", "confidence": 0.0},
    "company":   {"value": "string|null", "confidence": 0.0},
    "email":     {"value": "string|null", "confidence": 0.0},
    "phone":     {"value": "string|null", "confidence": 0.0},
    "job_title": {"value": "string|null", "confidence": 0.0},
    "address":   {"value": "string|null", "confidence": 0.0},
    "website":   {"value": "string|null", "confidence": 0.0}
  }
}

Return JSON only. No markdown. No explanation."""

_MOCK_FIELDS: dict = {
    "name":      {"value": "Nguyen Van A",    "confidence": 0.95},
    "company":   {"value": "ABC Corporation", "confidence": 0.92},
    "job_title": {"value": "Sales Manager",   "confidence": 0.88},
    "email":     {"value": "nva@abc.com",     "confidence": 0.95},
    "phone":     {"value": "090-1234-567",    "confidence": 0.90},
    "address":   {"value": None,              "confidence": 0.0},
    "website":   {"value": "abc.com",         "confidence": 0.85},
}


class LLMClientProtocol(Protocol):
    async def extract_from_image(self, image_bytes: bytes, content_type: str) -> dict:
        """
        Returns dict with keys:
          is_valid_card: bool
          error_code: str | None
          error_message: str | None
          fields: dict | None  — None when is_valid_card is False
        """
        ...


class MockLLMClient:
    async def extract_from_image(self, image_bytes: bytes, content_type: str) -> dict:
        return {
            "is_valid_card": True,
            "error_code": None,
            "error_message": None,
            "fields": dict(_MOCK_FIELDS),
        }


class GeminiVisionClient:
    """Single-call card validation + field extraction via vision model on OpenRouter."""

    _BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, model: str = "google/gemini-2.5-flash") -> None:
        self._api_key = api_key
        self._model = model

    async def extract_from_image(self, image_bytes: bytes, content_type: str) -> dict:
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
                                    "text": _CARD_VALIDATION_PROMPT,
                                },
                            ],
                        }
                    ],
                    "response_format": {"type": "json_object"},
                },
            )
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            return json.loads(content)
