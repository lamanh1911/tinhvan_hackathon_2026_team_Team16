import asyncio
import base64
import json
from typing import Protocol

import httpx

from src.api.exceptions import integration_error

_CARD_VALIDATION_PROMPT = """You are a business card validation assistant.

Analyze the uploaded image and determine whether it is a valid business card/name card.

Return JSON only with this schema:
{
  "is_business_card": true/false,
  "confidence": 0-1,
  "quality": {
    "readable": true/false,
    "issues": []
  },
  "extracted_fields": {
    "person_name": "",
    "company_name": "",
    "job_title": "",
    "email": "",
    "phone": "",
    "website": "",
    "address": ""
  },
  "validation": {
    "has_identity": true/false,
    "has_contact_info": true/false,
    "valid_email_format": true/false,
    "valid_phone_format": true/false
  },
  "decision": "valid | invalid | unclear",
  "reasons": []
}

Rules:
- A valid business card must contain identity information and at least one contact method.
- If the image is too blurry, cropped, dark, or text is unreadable, return "unclear".
- Do not guess missing fields.

Return JSON only. No markdown fences. No explanation outside the JSON."""


_WRONG_CARD_KEYWORDS = frozenset({
    "bank", "credit", "debit", "atm", "visa", "mastercard", "jcb", "amex",
    "membership", "member", "loyalty", "student", "id card", "identity",
    "gift card", "shopping card",
})


def _map_new_schema(raw: dict) -> dict:
    """Convert new LLM validation schema to the internal {is_valid_card, error_code, error_message, fields} format."""
    decision = (raw.get("decision") or "invalid").strip().lower()
    confidence: float = float(raw.get("confidence") or 0.0)

    if decision == "valid":
        ef = raw.get("extracted_fields") or {}
        fields = {
            "name":      {"value": ef.get("person_name") or None,  "confidence": confidence},
            "company":   {"value": ef.get("company_name") or None,  "confidence": confidence},
            "job_title": {"value": ef.get("job_title") or None,     "confidence": confidence},
            "email":     {"value": ef.get("email") or None,         "confidence": confidence},
            "phone":     {"value": ef.get("phone") or None,         "confidence": confidence},
            "address":   {"value": ef.get("address") or None,       "confidence": confidence},
            "website":   {"value": ef.get("website") or None,       "confidence": confidence},
        }
        # Treat empty strings as None
        for f in fields.values():
            if f["value"] == "":
                f["value"] = None
        return {"is_valid_card": True, "error_code": None, "error_message": None, "fields": fields}

    if decision == "unclear":
        reasons = raw.get("reasons") or []
        msg = reasons[0] if reasons else "The image is too blurry or unclear to read. Please take a clearer photo in good lighting."
        return {"is_valid_card": False, "error_code": "POOR_QUALITY", "error_message": msg, "fields": None}

    # decision == "invalid"
    reasons = raw.get("reasons") or []
    reasons_text = " ".join(reasons).lower()
    if any(kw in reasons_text for kw in _WRONG_CARD_KEYWORDS):
        code = "WRONG_CARD_TYPE"
        msg = reasons[0] if reasons else "This appears to be a bank, membership, or identity card. Please upload a business card or name card."
    else:
        code = "INVALID_CARD_TYPE"
        msg = reasons[0] if reasons else "This does not appear to be a business card. Please upload a name card or contact card."
    return {"is_valid_card": False, "error_code": code, "error_message": msg, "fields": None}

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
                    "X-No-Log": "true",
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
            raw = _parse_json_content(content)
            return _map_new_schema(raw)


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
            "X-No-Log": "true",
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
