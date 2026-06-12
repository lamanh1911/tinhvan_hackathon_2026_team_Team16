import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.api.config import get_settings
from src.api.database import get_db
from src.api.exceptions import invalid_status, not_found, validation_error
from src.api.models.action_item import ActionItem
from src.api.models.meeting import Meeting
from src.api.models.meeting_minutes import MeetingMinutes
from src.api.schemas.meetings import (
    ActionItemSchema,
    MeetingListItem,
    MOMDraftResponse,
    MOMUpdateRequest,
)
from src.api.services.mom_summarizer import make_mom_summarizer
from src.api.services.transcript_parser import parse_transcript

router = APIRouter(prefix="/meetings", tags=["meetings"])


def _get_summarizer():
    settings = get_settings()
    return make_mom_summarizer(use_mocks=settings.use_mocks, settings=settings)


def _action_to_schema(item: ActionItem) -> ActionItemSchema:
    return ActionItemSchema(
        id=item.id,
        description=item.description,
        owner=item.owner,
        deadline=item.deadline,
    )


def _mom_to_response(minutes: MeetingMinutes) -> MOMDraftResponse:
    return MOMDraftResponse(
        id=minutes.id,
        meeting_id=minutes.meeting_id,
        summary=minutes.summary,
        language=minutes.language,
        status=minutes.status,
        incomplete_warning=minutes.incomplete_warning,
        action_items=[_action_to_schema(a) for a in minutes.action_items],
        created_at=minutes.created_at,
    )


def _get_minutes_for_meeting(db: Session, meeting_id: uuid.UUID) -> MeetingMinutes:
    minutes = db.scalars(
        select(MeetingMinutes).where(MeetingMinutes.meeting_id == meeting_id)
    ).first()
    if not minutes:
        raise not_found("Meeting minutes")
    return minutes


@router.post("/mom", response_model=MOMDraftResponse, status_code=201)
async def create_mom(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    raw = await file.read()
    # Parse + summarize. The transcript text stays in memory only and is discarded
    # after MOM generation (NFR-SEC-03) — never logged, never persisted.
    transcript_text = parse_transcript(raw, file.filename or "transcript.txt")
    summarizer = _get_summarizer()
    mom = await summarizer.summarize(transcript_text)

    # Auto-create an internal meeting to anchor the MOM (and any follow-up email).
    meeting = Meeting(mode="online")
    db.add(meeting)
    db.flush()

    minutes = MeetingMinutes(
        meeting_id=meeting.id,
        summary=mom["summary"],
        language=mom["language"],
        status="draft",
        incomplete_warning=mom["incomplete_warning"],
    )
    db.add(minutes)
    db.flush()

    for action in mom["action_items"]:
        db.add(
            ActionItem(
                minutes_id=minutes.id,
                description=action["description"],
                owner=action["owner"],
                deadline=action["deadline"],
            )
        )

    db.commit()
    db.refresh(minutes)
    return _mom_to_response(minutes)


@router.get("", response_model=list[MeetingListItem])
def list_meetings(db: Session = Depends(get_db)):
    meetings = db.scalars(
        select(Meeting).where(Meeting.deleted_at.is_(None)).order_by(Meeting.created_at.desc())
    ).all()

    items: list[MeetingListItem] = []
    for meeting in meetings:
        minutes = meeting.minutes[0] if meeting.minutes else None
        items.append(
            MeetingListItem(
                meeting_id=meeting.id,
                minutes_id=minutes.id if minutes else None,
                status=minutes.status if minutes else None,
                summary=minutes.summary if minutes else None,
                incomplete_warning=minutes.incomplete_warning if minutes else False,
                action_item_count=len(minutes.action_items) if minutes else 0,
                created_at=meeting.created_at,
            )
        )
    return items


@router.get("/{meeting_id}/mom", response_model=MOMDraftResponse)
def get_mom(meeting_id: uuid.UUID, db: Session = Depends(get_db)):
    minutes = _get_minutes_for_meeting(db, meeting_id)
    return _mom_to_response(minutes)


@router.patch("/{meeting_id}/mom", response_model=MOMDraftResponse)
def update_mom(
    meeting_id: uuid.UUID,
    body: MOMUpdateRequest,
    db: Session = Depends(get_db),
):
    minutes = _get_minutes_for_meeting(db, meeting_id)
    if minutes.status == "approved":
        raise invalid_status("Cannot edit an approved MOM")

    if body.summary is not None:
        minutes.summary = body.summary

    if body.action_items is not None:
        # Replace the full set of action items with the provided list.
        for existing in list(minutes.action_items):
            db.delete(existing)
        db.flush()
        for action in body.action_items:
            db.add(
                ActionItem(
                    minutes_id=minutes.id,
                    description=action.description,
                    owner=action.owner,
                    deadline=action.deadline,
                )
            )

    minutes.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(minutes)
    return _mom_to_response(minutes)


@router.post("/{meeting_id}/mom/approve", response_model=MOMDraftResponse)
def approve_mom(meeting_id: uuid.UUID, db: Session = Depends(get_db)):
    minutes = _get_minutes_for_meeting(db, meeting_id)
    if minutes.status == "approved":
        raise invalid_status("MOM is already approved")

    if not (minutes.summary or "").strip():
        raise validation_error("Summary is required before approving the MOM")
    if not minutes.action_items:
        raise validation_error("At least one action item is required before approving")
    for action in minutes.action_items:
        if not action.owner or not action.deadline:
            raise validation_error(
                f"Action item '{action.description}' must have an owner and a deadline"
            )

    minutes.status = "approved"
    minutes.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(minutes)
    return _mom_to_response(minutes)
