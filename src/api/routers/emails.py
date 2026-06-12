import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.config import get_settings
from src.api.database import get_db
from src.api.exceptions import invalid_status, not_found, validation_error
from src.api.models.customer import Customer
from src.api.models.email_draft import EmailDraft
from src.api.models.meeting import Meeting
from src.api.models.meeting_minutes import MeetingMinutes
from src.api.schemas.emails import (
    EmailDraftResponse,
    EmailUpdateRequest,
    FollowUpEmailRequest,
    ThankYouEmailRequest,
)
from src.api.services.email_template import inject, load_template, parse_subject_body
from src.api.services.graph_client import make_graph_client
from src.api.services.llm_client import MockLLMClient, OpenRouterLLMClient

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/emails", tags=["emails"])

_EDITABLE_STATUSES = {"draft"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_settings():
    return get_settings()


def _get_llm():
    settings = _get_settings()
    if settings.use_mocks:
        return MockLLMClient()
    return OpenRouterLLMClient(settings.openrouter_api_key, settings.openrouter_model)


def _email_to_response(email: EmailDraft) -> EmailDraftResponse:
    return EmailDraftResponse(
        id=email.id,
        meeting_id=email.meeting_id,
        type=email.type,
        subject=email.subject,
        body=email.body,
        status=email.status,
        created_at=email.created_at,
        updated_at=email.updated_at,
    )


def _get_email(db: Session, email_id: uuid.UUID) -> EmailDraft:
    email = db.get(EmailDraft, email_id)
    if not email:
        raise not_found("Email draft")
    return email


def _transition(email: EmailDraft, from_statuses: set[str], to_status: str) -> None:
    if email.status not in from_statuses:
        allowed = " or ".join(sorted(from_statuses))
        raise invalid_status(
            f"Email must be in '{allowed}' status to perform this action (current: '{email.status}')"
        )
    email.status = to_status
    email.updated_at = datetime.now(timezone.utc)


# ---------------------------------------------------------------------------
# FR-02: Thank-you Email
# ---------------------------------------------------------------------------

@router.post("/thank-you", response_model=EmailDraftResponse, status_code=201)
async def create_thank_you(
    body: ThankYouEmailRequest,
    db: Session = Depends(get_db),
):
    meeting = db.get(Meeting, body.meeting_id)
    if not meeting:
        raise not_found("Meeting")
    if not meeting.customer_id:
        raise validation_error("Meeting must have a linked customer to generate a thank-you email")

    customer = db.get(Customer, meeting.customer_id)
    if not customer:
        raise not_found("Customer")

    logger.info("[thank-you] generating draft for meeting_id=%s", body.meeting_id)

    settings = _get_settings()
    graph_client = make_graph_client(use_mocks=settings.use_mocks)
    event = await graph_client.get_event(meeting.graph_event_id)

    template = load_template("thank_you_email.txt")
    subject_tpl, body_tpl = parse_subject_body(template)

    # customer.name is PII — injected into template but never logged
    data = {
        "customer_name": customer.name,
        "event_name": event["event_name"],
        "meeting_date": event["meeting_date"],
    }
    subject = inject(subject_tpl, data)
    email_body = inject(body_tpl, data)

    email = EmailDraft(
        meeting_id=meeting.id,
        type="thank_you",
        subject=subject,
        body=email_body,
        status="draft",
    )
    db.add(email)
    db.commit()
    db.refresh(email)

    logger.info("[thank-you] created email_id=%s status=draft", email.id)
    return _email_to_response(email)


# ---------------------------------------------------------------------------
# FR-06: Follow-up Email
# ---------------------------------------------------------------------------

@router.post("/follow-up", response_model=EmailDraftResponse, status_code=201)
async def create_follow_up(
    body: FollowUpEmailRequest,
    db: Session = Depends(get_db),
):
    minutes = db.scalars(
        select(MeetingMinutes).where(MeetingMinutes.meeting_id == body.meeting_id)
    ).first()
    if not minutes:
        raise not_found("Meeting minutes")
    if minutes.status != "approved":
        raise invalid_status("MOM must be approved before generating a follow-up email")

    mom = {
        "summary": minutes.summary,
        "language": minutes.language,
        "action_items": [
            {
                "description": a.description,
                "owner": a.owner,
                "deadline": a.deadline.isoformat() if a.deadline else None,
            }
            for a in minutes.action_items
        ],
    }

    llm = _get_llm()
    result = await llm.generate_follow_up_email(mom)

    email = EmailDraft(
        meeting_id=minutes.meeting_id,
        type="follow_up",
        subject=result.get("subject"),
        body=result.get("body"),
        status="draft",
    )
    db.add(email)
    db.commit()
    db.refresh(email)
    return _email_to_response(email)


# ---------------------------------------------------------------------------
# List / Get / Edit
# ---------------------------------------------------------------------------

@router.get("", response_model=list[EmailDraftResponse])
def list_emails(db: Session = Depends(get_db)):
    emails = db.scalars(
        select(EmailDraft).order_by(EmailDraft.created_at.desc())
    ).all()
    return [_email_to_response(e) for e in emails]


@router.get("/{email_id}", response_model=EmailDraftResponse)
def get_email(email_id: uuid.UUID, db: Session = Depends(get_db)):
    return _email_to_response(_get_email(db, email_id))


@router.patch("/{email_id}", response_model=EmailDraftResponse)
def update_email(
    email_id: uuid.UUID,
    body: EmailUpdateRequest,
    db: Session = Depends(get_db),
):
    email = _get_email(db, email_id)
    if email.status not in _EDITABLE_STATUSES:
        raise invalid_status(
            f"Only a draft email can be edited (current status: '{email.status}')"
        )

    if body.subject is not None:
        email.subject = body.subject
    if body.body is not None:
        email.body = body.body

    email.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(email)
    return _email_to_response(email)


# ---------------------------------------------------------------------------
# Status transitions
# ---------------------------------------------------------------------------

@router.post("/{email_id}/submit", response_model=EmailDraftResponse)
def submit_email(email_id: uuid.UUID, db: Session = Depends(get_db)):
    """draft → in_review"""
    email = _get_email(db, email_id)
    _transition(email, {"draft"}, "in_review")
    db.commit()
    db.refresh(email)
    return _email_to_response(email)


@router.post("/{email_id}/approve", response_model=EmailDraftResponse)
def approve_email(email_id: uuid.UUID, db: Session = Depends(get_db)):
    """in_review → approved"""
    email = _get_email(db, email_id)
    _transition(email, {"in_review"}, "approved")
    db.commit()
    db.refresh(email)
    return _email_to_response(email)


@router.post("/{email_id}/send", response_model=EmailDraftResponse)
def send_email(email_id: uuid.UUID, db: Session = Depends(get_db)):
    """approved → sent. No real email is sent; only records the status change."""
    email = _get_email(db, email_id)
    _transition(email, {"approved"}, "sent")
    db.commit()
    db.refresh(email)
    logger.info("[send] email_id=%s marked as sent", email_id)
    return _email_to_response(email)


@router.post("/{email_id}/reject", response_model=EmailDraftResponse)
def reject_email(email_id: uuid.UUID, db: Session = Depends(get_db)):
    """draft | in_review → rejected"""
    email = _get_email(db, email_id)
    _transition(email, {"draft", "in_review"}, "rejected")
    db.commit()
    db.refresh(email)
    return _email_to_response(email)


@router.post("/{email_id}/reopen", response_model=EmailDraftResponse)
def reopen_email(email_id: uuid.UUID, db: Session = Depends(get_db)):
    """rejected → draft"""
    email = _get_email(db, email_id)
    _transition(email, {"rejected"}, "draft")
    db.commit()
    db.refresh(email)
    return _email_to_response(email)


# ---------------------------------------------------------------------------
# Kept for backward compatibility — not guarded, not removed yet
# ---------------------------------------------------------------------------

@router.post("/{email_id}/mark-sent", response_model=EmailDraftResponse)
def mark_sent(email_id: uuid.UUID, db: Session = Depends(get_db)):
    """Backward-compat alias for /send. Requires approved status."""
    email = _get_email(db, email_id)
    _transition(email, {"approved"}, "sent")
    db.commit()
    db.refresh(email)
    logger.info("[mark-sent] email_id=%s marked as sent", email_id)
    return _email_to_response(email)
