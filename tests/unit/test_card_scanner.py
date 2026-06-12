"""Unit tests — CardScannerService (FR-01).

Tests use MockLLMClient and MockStorageClient exclusively.
No external API calls, no database.
"""
import asyncio
import pytest

from src.api.services.card_scanner import CardScannerService, _build_fields, _compute_validity
from src.api.services.llm_client import MockLLMClient
from src.api.services.storage_client import MockStorageClient


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_scanner() -> CardScannerService:
    return CardScannerService(MockStorageClient(), MockLLMClient())


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


# ---------------------------------------------------------------------------
# _build_fields
# ---------------------------------------------------------------------------

class TestBuildFields:
    def test_high_confidence_field_not_flagged(self):
        raw = {"name": {"value": "Alice", "confidence": 0.95}}
        fields = _build_fields(raw)
        assert fields["name"]["value"] == "Alice"
        assert fields["name"]["flagged"] is False

    def test_low_confidence_field_flagged(self):
        raw = {"name": {"value": "Alice", "confidence": 0.5}}
        fields = _build_fields(raw)
        assert fields["name"]["flagged"] is True

    def test_missing_value_flagged(self):
        raw = {"name": {"value": None, "confidence": 0.9}}
        fields = _build_fields(raw)
        assert fields["name"]["flagged"] is True

    def test_absent_field_defaults_to_flagged(self):
        fields = _build_fields({})
        assert fields["name"]["value"] is None
        assert fields["name"]["flagged"] is True

    def test_all_seven_fields_present(self):
        fields = _build_fields({})
        assert set(fields.keys()) == {"name", "company", "job_title", "email", "phone", "address", "website"}

    def test_empty_string_value_not_flagged_by_confidence(self):
        # _build_fields flags only on value is None or confidence < threshold.
        # Empty string "" is not None, so confidence alone determines flagging here.
        raw = {"phone": {"value": "", "confidence": 0.9}}
        fields = _build_fields(raw)
        # Validity is caught downstream by _compute_validity (falsy value check)
        assert fields["phone"]["flagged"] is False  # confidence 0.9 >= threshold


# ---------------------------------------------------------------------------
# _compute_validity
# ---------------------------------------------------------------------------

class TestComputeValidity:
    def _full_fields(self):
        return {
            "name":      {"value": "Alice", "confidence": 0.9, "flagged": False},
            "company":   {"value": "Corp",  "confidence": 0.9, "flagged": False},
            "job_title": {"value": "CEO",   "confidence": 0.9, "flagged": False},
            "email":     {"value": "a@b.c", "confidence": 0.9, "flagged": False},
            "phone":     {"value": "090",   "confidence": 0.9, "flagged": False},
            "address":   {"value": None,    "confidence": 0.0, "flagged": True},
            "website":   {"value": None,    "confidence": 0.0, "flagged": True},
        }

    def test_valid_when_required_fields_present(self):
        is_valid, msg = _compute_validity(self._full_fields())
        assert is_valid is True
        assert msg is None

    def test_invalid_when_phone_missing(self):
        fields = self._full_fields()
        fields["phone"]["value"] = None
        is_valid, msg = _compute_validity(fields)
        assert is_valid is False
        assert "Phone" in msg

    def test_invalid_when_job_title_missing(self):
        fields = self._full_fields()
        fields["job_title"]["value"] = None
        is_valid, msg = _compute_validity(fields)
        assert is_valid is False
        assert "Job Title" in msg


# ---------------------------------------------------------------------------
# CardScannerService.scan  (MockLLMClient always returns valid card)
# ---------------------------------------------------------------------------

class TestCardScannerService:
    def test_scan_returns_expected_keys(self):
        scanner = make_scanner()
        result = run(scanner.scan(b"fake-image", "card.jpg", "image/jpeg"))
        assert "image_ref" in result
        assert "fields" in result
        assert "is_valid_card" in result

    def test_mock_scan_has_all_fields(self):
        scanner = make_scanner()
        result = run(scanner.scan(b"fake-image", "card.jpg"))
        assert set(result["fields"].keys()) == {
            "name", "company", "job_title", "email", "phone", "address", "website"
        }

    def test_mock_scan_image_ref_stored(self):
        scanner = make_scanner()
        result = run(scanner.scan(b"img", "test.jpg"))
        assert result["image_ref"].startswith("mock://")

    def test_invalid_card_raises_app_error(self):
        from src.api.exceptions import AppError
        from src.api.services.llm_client import LLMClientProtocol

        class RejectingLLM:
            async def extract_from_image(self, image_bytes, content_type):
                return {
                    "is_valid_card": False,
                    "error_code": "INVALID_CARD_TYPE",
                    "error_message": "Not a business card",
                    "fields": None,
                }

        scanner = CardScannerService(MockStorageClient(), RejectingLLM())
        with pytest.raises(AppError) as exc_info:
            run(scanner.scan(b"img", "random.jpg"))
        assert exc_info.value.code == "INVALID_CARD_TYPE"

    def test_wrong_card_type_raises_app_error(self):
        from src.api.exceptions import AppError

        class BankCardLLM:
            async def extract_from_image(self, image_bytes, content_type):
                return {
                    "is_valid_card": False,
                    "error_code": "WRONG_CARD_TYPE",
                    "error_message": "This is a bank card",
                    "fields": None,
                }

        scanner = CardScannerService(MockStorageClient(), BankCardLLM())
        with pytest.raises(AppError) as exc_info:
            run(scanner.scan(b"img", "bank.jpg"))
        assert exc_info.value.code == "WRONG_CARD_TYPE"
