"""Generate a structured Minutes-of-Meeting (MOM) draft from transcript text.

Mirrors the card_scanner service shape: an orchestration service that calls the
LLM client and normalizes the result. The raw transcript is never returned or
stored — only the structured MOM.
"""
from datetime import date

from src.api.services.llm_client import TextLLMClientProtocol


def _parse_deadline(value) -> date | None:
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip():
        try:
            return date.fromisoformat(value.strip())
        except ValueError:
            return None
    return None


def _normalize_action(raw: dict) -> dict | None:
    description = (raw.get("description") or "").strip()
    if not description:
        return None
    owner = raw.get("owner")
    return {
        "description": description,
        "owner": owner.strip() if isinstance(owner, str) and owner.strip() else None,
        "deadline": _parse_deadline(raw.get("deadline")),
    }


def _build_mom(raw: dict) -> dict:
    summary = (raw.get("summary") or "").strip() or None
    language = raw.get("language")

    action_items: list[dict] = []
    for item in raw.get("next_actions") or []:
        if isinstance(item, dict):
            normalized = _normalize_action(item)
            if normalized:
                action_items.append(normalized)

    # BR-15: flag when the transcript looks incomplete, the summary is missing,
    # there are no action items, or any action item lacks owner/deadline.
    incomplete = bool(raw.get("incomplete_warning"))
    if not summary or not action_items:
        incomplete = True
    if any(not a["owner"] or not a["deadline"] for a in action_items):
        incomplete = True

    return {
        "summary": summary,
        "language": language,
        "incomplete_warning": incomplete,
        "action_items": action_items,
    }


class MOMSummarizerService:
    def __init__(self, llm: TextLLMClientProtocol) -> None:
        self._llm = llm

    async def summarize(self, transcript_text: str) -> dict:
        raw = await self._llm.summarize_transcript(transcript_text)
        return _build_mom(raw)


def make_mom_summarizer(use_mocks: bool, settings=None) -> MOMSummarizerService:
    if use_mocks:
        from src.api.services.llm_client import MockLLMClient

        return MOMSummarizerService(MockLLMClient())

    from src.api.services.llm_client import OpenRouterLLMClient

    return MOMSummarizerService(
        OpenRouterLLMClient(settings.openrouter_api_key, settings.openrouter_model)
    )
