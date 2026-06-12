import logging

from src.api.schemas.cards import CONFIDENCE_THRESHOLD
from src.api.services.llm_client import LLMClientProtocol
from src.api.services.storage_client import StorageClientProtocol, make_card_key

logger = logging.getLogger(__name__)

_CARD_FIELDS = ("name", "company", "job_title", "email", "phone", "address", "website")
_REQUIRED_FOR_VALIDITY = ("phone", "job_title")


def _build_fields(raw: dict) -> dict:
    result = {}
    for field in _CARD_FIELDS:
        raw_field = raw.get(field) or {}
        value: str | None = raw_field.get("value")
        confidence: float | None = raw_field.get("confidence")
        flagged = value is None or confidence is None or confidence < CONFIDENCE_THRESHOLD
        result[field] = {"value": value, "confidence": confidence, "flagged": flagged}
    return result


def _compute_validity(fields: dict) -> tuple[bool, str | None]:
    missing = [
        f for f in _REQUIRED_FOR_VALIDITY
        if not fields.get(f, {}).get("value")
    ]
    if missing:
        labels = {"phone": "Phone", "job_title": "Job Title"}
        names = ", ".join(labels[f] for f in missing)
        return False, f"Required fields missing: {names}"
    return True, None


class CardScannerService:
    def __init__(
        self,
        storage: StorageClientProtocol,
        llm: LLMClientProtocol,
    ) -> None:
        self._storage = storage
        self._llm = llm

    async def scan(self, image_bytes: bytes, filename: str, content_type: str = "image/jpeg") -> dict:
        logger.info("[scan] file received: %s (%d bytes)", filename, len(image_bytes))

        key = make_card_key(filename)
        image_ref = await self._storage.upload(key, image_bytes, content_type)

        ocr_text, raw_fields = await self._llm.extract_from_image(image_bytes, content_type)
        logger.info("[scan] OCR raw text:\n%s", ocr_text)
        logger.info("[scan] extracted JSON: %s", raw_fields)

        fields = _build_fields(raw_fields)
        is_valid_card, error_message = _compute_validity(fields)
        logger.info("[scan] is_valid_card=%s error_message=%s", is_valid_card, error_message)

        return {
            "image_ref": image_ref,
            "raw_ocr_text": ocr_text,
            "fields": fields,
            "is_valid_card": is_valid_card,
            "error_message": error_message,
        }


def make_card_scanner(use_mocks: bool, settings=None) -> CardScannerService:
    if use_mocks:
        from src.api.services.llm_client import MockLLMClient
        from src.api.services.storage_client import MockStorageClient

        return CardScannerService(MockStorageClient(), MockLLMClient())

    from src.api.services.llm_client import GeminiVisionClient
    from src.api.services.storage_client import MockStorageClient, S3StorageClient

    storage = (
        S3StorageClient(settings)
        if settings.storage_endpoint
        else MockStorageClient()
    )

    return CardScannerService(
        storage,
        GeminiVisionClient(settings.openrouter_api_key, settings.openrouter_model),
    )
