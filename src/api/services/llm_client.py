import asyncio
import base64
import json
from typing import Protocol

import httpx

from src.api.exceptions import integration_error

_CARD_VALIDATION_PROMPT = """You are a business card scanner assistant.

DECISION: Is this image a clear, readable BUSINESS CARD (name card / visiting card)?

Apply these rules strictly — do not guess:
- Return YES only if the image clearly shows ALL of: person name, job title or position, company or organisation name, and at least one contact method (email, phone, website, or address).
- Return NO if you are not certain, if the image is blurry or unreadable, or if it is clearly not a business card.

---

If YES (it is a clear business card) → extract fields and return:
{
  "is_valid_card": true,
  "error_code": null,
  "error_message": null,
  "fields": {
    "name":      {"value": "...", "confidence": 0.0},
    "company":   {"value": "...", "confidence": 0.0},
    "email":     {"value": "...", "confidence": 0.0},
    "phone":     {"value": "...", "confidence": 0.0},
    "job_title": {"value": "...", "confidence": 0.0},
    "address":   {"value": "...", "confidence": 0.0},
    "website":   {"value": "...", "confidence": 0.0}
  }
}
Field rules: extract only clearly visible text; set value to null and confidence to 0.0 for any field not found.

---

If NO → identify the reason and return one of these:

Image is a BANK CARD, CREDIT CARD, DEBIT CARD, or ATM CARD (has card number, bank logo, Visa/Mastercard/JCB/AMEX):
{
  "is_valid_card": false,
  "error_code": "WRONG_CARD_TYPE",
  "error_message": "This appears to be a bank or payment card, not a business card. Please upload a name card or contact card.",
  "fields": null
}

Image is a MEMBERSHIP CARD, LOYALTY CARD, SHOPPING CARD, GIFT CARD, STUDENT CARD, or ID CARD:
{
  "is_valid_card": false,
  "error_code": "WRONG_CARD_TYPE",
  "error_message": "This appears to be a membership, student, or identity card, not a business card. Please upload a name card or contact card.",
  "fields": null
}

Image is BLURRY, TOO DARK, OVER-EXPOSED, or otherwise UNREADABLE (cannot identify card type or read text):
{
  "is_valid_card": false,
  "error_code": "POOR_QUALITY",
  "error_message": "The image is too blurry or unclear to read. Please take a clearer photo in good lighting.",
  "fields": null
}

Image is anything else (photo, selfie, receipt, document, screenshot, food, landscape, etc.):
{
  "is_valid_card": false,
  "error_code": "INVALID_CARD_TYPE",
  "error_message": "This does not appear to be a business card. Please upload a name card or contact card.",
  "fields": null
}

Return JSON only. No markdown fences. No explanation outside the JSON."""

_MOM_SYSTEM_PROMPT = """You are a meeting-minutes assistant.
Read the meeting transcript and return ONLY valid JSON with this structure:
{
  "summary": string,
  "language": string,
  "incomplete_warning": boolean,
  "next_actions": [
    {"description": string, "owner": string|null, "deadline": string|null}
  ]
}
Rules:
- "summary" captures the main discussion points.
- "language" is the ISO code of the transcript language (e.g. "en", "ja", "vi").
- "deadline" must be an ISO date (YYYY-MM-DD) or null if not stated.
- "owner" is the person/role responsible, or null if not stated.
- Set "incomplete_warning" to true if the transcript appears cut off or is missing
  key context needed to produce reliable minutes.
- Generate the output in the same language as the transcript."""

_FOLLOW_UP_SYSTEM_PROMPT = """You are a sales follow-up email assistant.
Using the approved meeting minutes, draft a follow-up email and return ONLY valid JSON:
{
  "subject": string,
  "body": string
}
Rules:
- The body must summarize the meeting discussion and list every next action.
- Write a complete, ready-to-send email body (greeting, summary, next steps, sign-off).
- Generate the email in the same language as the meeting minutes."""

_MOCK_FIELDS: dict = {
    "name":      {"value": "Nguyen Van A",    "confidence": 0.95},
    "company":   {"value": "ABC Corporation", "confidence": 0.92},
    "job_title": {"value": "Sales Manager",   "confidence": 0.88},
    "email":     {"value": "nva@abc.com",     "confidence": 0.95},
    "phone":     {"value": "090-1234-567",    "confidence": 0.90},
    "address":   {"value": None,              "confidence": 0.0},
    "website":   {"value": "abc.com",         "confidence": 0.85},
}

_MOCK_MOM: dict = {
    "summary": (
        "Discussed the Q3 partnership scope, agreed on a phased rollout, and reviewed "
        "pricing tiers. The customer requested a revised proposal and a technical "
        "integration session before final sign-off."
    ),
    "language": "en",
    "incomplete_warning": False,
    "next_actions": [
        {
            "description": "Send revised pricing proposal",
            "owner": "Sales",
            "deadline": "2026-06-20",
        },
        {
            "description": "Schedule technical integration call",
            "owner": "BrSE",
            "deadline": "2026-06-25",
        },
    ],
}

_MOCK_FOLLOW_UP: dict = {
    "subject": "Follow-up: Q3 Partnership Discussion",
    "body": (
        "Dear Customer,\n\n"
        "Thank you for the productive meeting. To summarize, we discussed the Q3 "
        "partnership scope, agreed on a phased rollout, and reviewed the pricing tiers.\n\n"
        "Next steps:\n"
        "- Send revised pricing proposal (Sales, by 2026-06-20)\n"
        "- Schedule technical integration call (BrSE, by 2026-06-25)\n\n"
        "We look forward to moving forward.\n\n"
        "Best regards,\nThe Relay Team"
    ),
}


def _parse_json_content(content: str) -> dict:
    """Parse model JSON output, tolerating ```json fenced blocks some models add."""
    text = content.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1] if "\n" in text else text
        text = text.rsplit("```", 1)[0]
        if text.lstrip().startswith("json"):
            text = text.lstrip()[4:]
    return json.loads(text.strip())


class LLMClientProtocol(Protocol):
    """Card scanning — single-call validation + field extraction from an image."""

    async def extract_from_image(self, image_bytes: bytes, content_type: str) -> dict:
        """
        Returns dict with keys:
          is_valid_card: bool
          error_code: str | None
          error_message: str | None
          fields: dict | None  — None when is_valid_card is False
        """
        ...


class TextLLMClientProtocol(Protocol):
    """Text generation — MOM summarization and follow-up email drafting."""

    async def summarize_transcript(self, transcript_text: str) -> dict: ...
    async def generate_follow_up_email(self, mom: dict) -> dict: ...


class MockLLMClient:
    async def extract_from_image(self, image_bytes: bytes, content_type: str) -> dict:
        return {
            "is_valid_card": True,
            "error_code": None,
            "error_message": None,
            "fields": dict(_MOCK_FIELDS),
        }

    async def summarize_transcript(self, transcript_text: str) -> dict:
        return dict(_MOCK_MOM)

    async def generate_follow_up_email(self, mom: dict) -> dict:
        return dict(_MOCK_FOLLOW_UP)


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
            return _parse_json_content(content)


class OpenRouterLLMClient:
    """Text chat client (OpenRouter) for MOM summarization and follow-up email."""

    _BASE_URL = "https://openrouter.ai/api/v1/chat/completions"
    _DEFAULT_MODEL = "google/gemini-2.5-flash"

    def __init__(self, api_key: str, model: str | None = None) -> None:
        self._api_key = api_key
        self._model = model or self._DEFAULT_MODEL

    async def _chat(self, system_prompt: str, user_content: str) -> dict:
        payload = {
            "model": self._model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            "response_format": {"type": "json_object"},
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "HTTP-Referer": "https://relay.app",
            "X-Title": "Relay Assistant",
        }
        # Free-tier endpoints frequently return 429/5xx — retry with backoff,
        # then surface a clean INTEGRATION_ERROR rather than a 500 (rule 03).
        last_exc: Exception | None = None
        async with httpx.AsyncClient(timeout=90.0) as client:
            for attempt in range(4):
                try:
                    resp = await client.post(self._BASE_URL, headers=headers, json=payload)
                    if resp.status_code in (429, 500, 502, 503, 504):
                        last_exc = httpx.HTTPStatusError(
                            "retryable", request=resp.request, response=resp
                        )
                        await asyncio.sleep(2 * (attempt + 1))
                        continue
                    resp.raise_for_status()
                    content = resp.json()["choices"][0]["message"]["content"]
                    return _parse_json_content(content)
                except (httpx.HTTPError, KeyError, json.JSONDecodeError) as exc:
                    last_exc = exc
                    await asyncio.sleep(1)
        raise integration_error("OpenRouter") from last_exc

    async def summarize_transcript(self, transcript_text: str) -> dict:
        return await self._chat(_MOM_SYSTEM_PROMPT, transcript_text)

    async def generate_follow_up_email(self, mom: dict) -> dict:
        payload = {
            "summary": mom.get("summary"),
            "language": mom.get("language"),
            "next_actions": mom.get("action_items", []),
        }
        return await self._chat(_FOLLOW_UP_SYSTEM_PROMPT, json.dumps(payload))
