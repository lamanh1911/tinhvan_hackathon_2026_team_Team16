"""Integration tests — StorageClientProtocol (FR-01).

Uses MockStorageClient — no real S3/Railway calls.
Verifies the upload contract used by CardScannerService.
"""
import asyncio

import pytest

from src.api.services.storage_client import MockStorageClient, make_card_key


def run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


class TestMockStorageClientUpload:
    def test_upload_returns_string_url(self):
        client = MockStorageClient()
        result = run(client.upload("cards/test.jpg", b"data", "image/jpeg"))
        assert isinstance(result, str)

    def test_upload_url_contains_key(self):
        client = MockStorageClient()
        result = run(client.upload("cards/abc/test.jpg", b"data", "image/jpeg"))
        assert "cards/abc/test.jpg" in result

    def test_upload_mock_prefix(self):
        client = MockStorageClient()
        result = run(client.upload("key.jpg", b"data", "image/jpeg"))
        assert result.startswith("mock://")

    def test_upload_empty_bytes_ok(self):
        client = MockStorageClient()
        result = run(client.upload("empty.jpg", b"", "image/jpeg"))
        assert "empty.jpg" in result

    def test_upload_png_content_type(self):
        client = MockStorageClient()
        result = run(client.upload("card.png", b"png-data", "image/png"))
        assert isinstance(result, str)


class TestMakeCardKey:
    def test_key_starts_with_cards_prefix(self):
        key = make_card_key("photo.jpg")
        assert key.startswith("cards/")

    def test_key_ends_with_filename(self):
        key = make_card_key("photo.jpg")
        assert key.endswith("photo.jpg")

    def test_key_has_uuid_segment(self):
        import re
        key = make_card_key("test.jpg")
        # Expect format: cards/<uuid>/test.jpg
        uuid_pattern = r"cards/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}/test\.jpg"
        assert re.match(uuid_pattern, key), f"Unexpected key format: {key}"

    def test_two_cards_get_different_keys(self):
        key1 = make_card_key("card.jpg")
        key2 = make_card_key("card.jpg")
        assert key1 != key2
