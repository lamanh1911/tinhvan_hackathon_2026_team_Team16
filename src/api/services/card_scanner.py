from src.api.schemas.cards import CONFIDENCE_THRESHOLD
from src.api.services.llm_client import LLMClientProtocol
from src.api.services.storage_client import StorageClientProtocol, make_card_key
from src.api.services.vision_client import VisionClientProtocol


def _build_fields(raw: dict) -> dict:
    result = {}
    for field in ("name", "company", "title", "email", "phone", "address"):
        raw_field = raw.get(field) or {}
        value: str | None = raw_field.get("value")
        confidence: float | None = raw_field.get("confidence")
        flagged = value is None or confidence is None or confidence < CONFIDENCE_THRESHOLD
        result[field] = {"value": value, "confidence": confidence, "flagged": flagged}
    return result


class CardScannerService:
    def __init__(
        self,
        storage: StorageClientProtocol,
        vision: VisionClientProtocol,
        llm: LLMClientProtocol,
    ) -> None:
        self._storage = storage
        self._vision = vision
        self._llm = llm

    async def scan(self, image_bytes: bytes, filename: str) -> dict:
        key = make_card_key(filename)
        image_ref = await self._storage.upload(key, image_bytes, "image/jpeg")
        ocr_text = await self._vision.extract_text(image_bytes)
        raw_fields = await self._llm.extract_card_fields(ocr_text)
        fields = _build_fields(raw_fields)
        return {"image_ref": image_ref, "raw_ocr_text": ocr_text, "fields": fields}


def make_card_scanner(use_mocks: bool, settings=None) -> CardScannerService:
    if use_mocks:
        from src.api.services.llm_client import MockLLMClient
        from src.api.services.storage_client import MockStorageClient
        from src.api.services.vision_client import MockVisionClient

        return CardScannerService(MockStorageClient(), MockVisionClient(), MockLLMClient())

    from src.api.services.llm_client import OpenRouterLLMClient
    from src.api.services.storage_client import S3StorageClient
    from src.api.services.vision_client import GoogleVisionClient

    return CardScannerService(
        S3StorageClient(settings),
        GoogleVisionClient(settings.google_vision_api_key),
        OpenRouterLLMClient(settings.openrouter_api_key),
    )
