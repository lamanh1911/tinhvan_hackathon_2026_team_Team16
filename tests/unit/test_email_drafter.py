"""Unit tests — Email template injection and draft rules (FR-02).

Tests cover:
- template injection (inject / parse_subject_body)
- no auto-send: email always starts as draft
- event name and date present in rendered output
"""
import pytest

from src.api.services.email_template import inject, parse_subject_body


SAMPLE_TEMPLATE = """\
Subject: Thank you for our meeting — {{event_name}}

Dear {{customer_name}},

Thank you for taking the time to meet with us on {{meeting_date}}.
We appreciated the opportunity.

Best regards,
The Relay Team"""


# ---------------------------------------------------------------------------
# parse_subject_body
# ---------------------------------------------------------------------------

class TestParseSubjectBody:
    def test_splits_subject_and_body(self):
        subject, body = parse_subject_body(SAMPLE_TEMPLATE)
        assert subject == "Thank you for our meeting — {{event_name}}"
        assert "Dear {{customer_name}}" in body

    def test_raises_on_missing_subject_prefix(self):
        with pytest.raises(ValueError):
            parse_subject_body("No subject line here\n\nBody")

    def test_body_does_not_include_subject_line(self):
        subject, body = parse_subject_body(SAMPLE_TEMPLATE)
        assert "Subject:" not in body


# ---------------------------------------------------------------------------
# inject
# ---------------------------------------------------------------------------

class TestInject:
    def test_replaces_all_placeholders(self):
        data = {
            "customer_name": "Alice",
            "event_name": "Q3 Partnership Meeting",
            "meeting_date": "2026-06-15",
        }
        subject_tpl, body_tpl = parse_subject_body(SAMPLE_TEMPLATE)
        subject = inject(subject_tpl, data)
        body = inject(body_tpl, data)

        assert "Q3 Partnership Meeting" in subject
        assert "Alice" in body
        assert "2026-06-15" in body

    def test_unknown_placeholder_left_as_is(self):
        result = inject("Hello {{unknown_key}}", {})
        assert "{{unknown_key}}" in result

    def test_event_name_in_subject(self):
        subject_tpl, _ = parse_subject_body(SAMPLE_TEMPLATE)
        subject = inject(subject_tpl, {"event_name": "Q3 Review"})
        assert "Q3 Review" in subject

    def test_meeting_date_in_body(self):
        _, body_tpl = parse_subject_body(SAMPLE_TEMPLATE)
        body = inject(body_tpl, {
            "customer_name": "Bob",
            "meeting_date": "2026-07-01",
        })
        assert "2026-07-01" in body


# ---------------------------------------------------------------------------
# Draft status rule — no auto-send
# ---------------------------------------------------------------------------

class TestDraftStatusRule:
    """Verify the EmailDraft model enforces draft-first rule."""

    def test_email_draft_column_default_is_draft(self):
        # SQLAlchemy column-level default (applied at INSERT, not Python init).
        from sqlalchemy import inspect as sa_inspect
        from src.api.models.email_draft import EmailDraft
        col = sa_inspect(EmailDraft).c.status
        assert col.default.arg == "draft"

    def test_email_draft_not_auto_sent(self):
        # Confirm the status CHECK constraint allows "draft" but never defaults to sent.
        from sqlalchemy import inspect as sa_inspect
        from src.api.models.email_draft import EmailDraft
        col = sa_inspect(EmailDraft).c.status
        assert col.default.arg != "sent"
        assert col.default.arg != "approved"
