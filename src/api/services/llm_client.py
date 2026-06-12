import asyncio
import base64
import json
from typing import Protocol

import httpx

from src.api.exceptions import integration_error

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
    "raw_text": "Nguyen Van A\nSales Manager\nABC Corporation\nEmail: nva@abc.com\nTel: 090-1234-567\nwww.abc.com",
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
    """Card scanning — single-call OCR + field extraction from an image."""

    async def extract_from_image(
        self, image_bytes: bytes, content_type: str
    ) -> tuple[str, dict]: ...


class TextLLMClientProtocol(Protocol):
    """Text generation — MOM summarization and follow-up email drafting."""

    async def summarize_transcript(self, transcript_text: str) -> dict: ...
    async def generate_follow_up_email(self, mom: dict) -> dict: ...


class MockLLMClient:
    async def extract_from_image(
        self, image_bytes: bytes, content_type: str
    ) -> tuple[str, dict]:
        raw_text = _MOCK_FIELDS["raw_text"]
        fields = {k: v for k, v in _MOCK_FIELDS.items() if k != "raw_text"}
        return raw_text, fields

    async def summarize_transcript(self, transcript_text: str) -> dict:
        return dict(_MOCK_MOM)

    async def generate_follow_up_email(self, mom: dict) -> dict:
        return dict(_MOCK_FOLLOW_UP)


class GeminiVisionClient:
    """Single-call OCR + field extraction via vision model on OpenRouter."""

    _BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

    def __init__(self, api_key: str, model: str = "google/gemini-2.5-flash") -> None:
        self._api_key = api_key
        self._model = model

    async def extract_from_image(
        self, image_bytes: bytes, content_type: str
    ) -> tuple[str, dict]:
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
