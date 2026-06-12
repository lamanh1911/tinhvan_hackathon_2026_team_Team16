import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.config import get_settings
from src.api.database import get_db
from src.api.exceptions import invalid_status, not_found
from src.api.models.email_draft import EmailDraft
from src.api.models.meeting_minutes import MeetingMinutes
from src.api.schemas.emails import (
    EmailDraftResponse,
    EmailUpdateRequest,
    FollowUpEmailRequest,
)
from src.api.services.llm_client import MockLLMClient, OpenRouterLLMClient

router = APIRouter(prefix="/emails", tags=["emails"])

# Statuses in which the subject/body may still be edited.
_EDITABLE_STATUSES = {"draft"}


def _get_llm():
    settings = get_settings()
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
        raise invalid_status("Only a draft email can be edited")

    if body.subject is not None:
        email.subject = body.subject
    if body.body is not None:
        email.body = body.body

    email.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(email)
    return _email_to_response(email)


@router.post("/{email_id}/mark-sent", response_model=EmailDraftResponse)
def mark_sent(email_id: uuid.UUID, db: Session = Depends(get_db)):
    # The system never sends mail. This only records that the user copied the body
    # and sent it manually, so the draft can be tracked as handled.
    email = _get_email(db, email_id)
    if email.status == "sent":
        raise invalid_status("Email is already marked as sent")
    email.status = "sent"
    email.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(email)
    return _email_to_response(email)
