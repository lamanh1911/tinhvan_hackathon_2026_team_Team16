import logging
import uuid
from datetime import date, datetime, time, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.config import get_settings
from src.api.database import get_db
from src.api.exceptions import invalid_status, not_found
from src.api.models.member import Member
from src.api.models.schedule_proposal import ScheduleProposal
from src.api.schemas.schedule import (
    AttendeeSlotStatus,
    ScheduleOfflineRequest,
    ScheduleOnlineRequest,
    ScheduleProposalResponse,
    SlotApproveRequest,
    SlotProposal,
)
from src.api.services.graph_client import make_graph_client
from src.api.services.maps_client import make_maps_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/schedule", tags=["schedule"])

_SLOT_HOURS = [9, 11, 14, 16]  # candidate start hours (business hours)
_DURATION_MINUTES = 60
_TARGET_SLOT_COUNT = 4
_MAX_SEARCH_DAYS = 20

_MOCK_MEMBERS = [
    {"name": "Alice Nguyen", "email": "alice@relay.app"},
    {"name": "Bob Tran", "email": "bob@relay.app"},
]


def _next_business_days(start: date, count: int) -> list[date]:
    days = []
    current = start
    while len(days) < count:
        if current.weekday() < 5:  # Mon–Fri
            days.append(current)
        current += timedelta(days=1)
    return days


def _has_conflict(
    slot_start: datetime,
    slot_end: datetime,
    member_emails: list[str],
    busy_blocks: dict[str, list[dict]],
) -> bool:
    for email in member_emails:
        for block in busy_blocks.get(email, []):
            block_start = datetime.fromisoformat(block["start"])
            block_end = datetime.fromisoformat(block["end"])
            if slot_start < block_end and slot_end > block_start:
                return True
    return False


def _needs_travel_buffer(
    slot_start: datetime,
    member_emails: list[str],
    busy_blocks: dict[str, list[dict]],
    buffer_minutes: int,
) -> bool:
    """BR-11: Reject slot if a prior busy block ends too close to slot_start."""
    buffer = timedelta(minutes=buffer_minutes)
    for email in member_emails:
        for block in busy_blocks.get(email, []):
            block_end = datetime.fromisoformat(block["end"])
            # A prior appointment ends before the slot; check travel gap
            if block_end <= slot_start and slot_start - block_end < buffer:
                return True
    return False


async def _find_slots(
    member_emails: list[str],
    member_names: list[str],
    start_date: date,
    graph_client,
    travel_buffer_minutes: int | None = None,
) -> list[dict]:
    search_end = datetime.combine(
        start_date + timedelta(days=_MAX_SEARCH_DAYS),
        time(18, 0),
        tzinfo=timezone.utc,
    )
    search_start = datetime.combine(start_date, time(0, 0), tzinfo=timezone.utc)

    busy_blocks = await graph_client.get_free_busy(member_emails, search_start, search_end)

    slots: list[dict] = []
    current = start_date
    days_checked = 0

    while len(slots) < _TARGET_SLOT_COUNT and days_checked < _MAX_SEARCH_DAYS:
        if current.weekday() < 5:
            for hour in _SLOT_HOURS:
                if len(slots) >= _TARGET_SLOT_COUNT:
                    break
                slot_start = datetime.combine(current, time(hour, 0), tzinfo=timezone.utc)
                slot_end = slot_start + timedelta(minutes=_DURATION_MINUTES)

                if _has_conflict(slot_start, slot_end, member_emails, busy_blocks):
                    continue

                if travel_buffer_minutes and _needs_travel_buffer(
                    slot_start, member_emails, busy_blocks, travel_buffer_minutes
                ):
                    continue

                slot: dict = {
                    "start": slot_start.isoformat(),
                    "end": slot_end.isoformat(),
                    "attendees": [
                        {"name": name, "email": email, "status": "free"}
                        for name, email in zip(member_names, member_emails)
                    ],
                }
                if travel_buffer_minutes is not None:
                    slot["travel_buffer_minutes"] = travel_buffer_minutes
                slots.append(slot)

        current += timedelta(days=1)
        days_checked += 1

    return slots


def _resolve_members(db: Session, member_ids: list[uuid.UUID] | None):
    if member_ids:
        members = db.query(Member).filter(Member.id.in_(member_ids)).all()
    else:
        members = db.query(Member).all()

    if members:
        return [m.email for m in members], [m.name for m in members]
    return (
        [m["email"] for m in _MOCK_MEMBERS],
        [m["name"] for m in _MOCK_MEMBERS],
    )


def _proposal_to_response(proposal: ScheduleProposal) -> ScheduleProposalResponse:
    raw_slots: list[dict] = proposal.slots_json or []
    slots = [
        SlotProposal(
            index=i,
            start=datetime.fromisoformat(s["start"]),
            end=datetime.fromisoformat(s["end"]),
            attendees=[AttendeeSlotStatus(**a) for a in s.get("attendees", [])],
            travel_buffer_minutes=s.get("travel_buffer_minutes"),
        )
        for i, s in enumerate(raw_slots)
    ]
    return ScheduleProposalResponse(
        id=proposal.id,
        status=proposal.status,
        mode=proposal.mode,
        location=proposal.location,
        slots=slots,
        approved_slot_index=proposal.approved_slot_index,
        customer_id=proposal.customer_id,
        created_at=proposal.created_at,
    )


@router.post("/online", response_model=ScheduleProposalResponse, status_code=201)
async def create_schedule_proposal(
    body: ScheduleOnlineRequest,
    db: Session = Depends(get_db),
):
    settings = get_settings()
    graph_client = make_graph_client(use_mocks=settings.use_mocks)

    member_emails, member_names = _resolve_members(db, body.member_ids)

    start_date = date.today()
    if body.start_date:
        try:
            start_date = date.fromisoformat(body.start_date)
        except ValueError:
            pass

    logger.info("[schedule/online] generating slots from=%s members=%d", start_date, len(member_emails))

    slots = await _find_slots(member_emails, member_names, start_date, graph_client)

    proposal = ScheduleProposal(
        customer_id=body.customer_id,
        mode="online",
        status="draft",
        slots_json=slots,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    logger.info("[schedule/online] created proposal id=%s slots=%d", proposal.id, len(slots))
    return _proposal_to_response(proposal)


@router.post("/offline", response_model=ScheduleProposalResponse, status_code=201)
async def create_offline_schedule_proposal(
    body: ScheduleOfflineRequest,
    db: Session = Depends(get_db),
):
    settings = get_settings()
    graph_client = make_graph_client(use_mocks=settings.use_mocks)
    maps_client = make_maps_client(use_mocks=settings.use_mocks, settings=settings)

    member_emails, member_names = _resolve_members(db, body.member_ids)

    start_date = date.today()
    if body.start_date:
        try:
            start_date = date.fromisoformat(body.start_date)
        except ValueError:
            pass

    # Get travel buffer from mock (30 min) or real Maps API when available
    departure_dt = datetime.combine(start_date, time(8, 0), tzinfo=timezone.utc)
    travel_buffer = await maps_client.get_travel_time(
        origin="Office",
        destination=body.location,
        departure_time=departure_dt,
    )

    logger.info(
        "[schedule/offline] generating slots from=%s members=%d location=[redacted] buffer=%dmin",
        start_date, len(member_emails), travel_buffer,
    )

    slots = await _find_slots(
        member_emails, member_names, start_date, graph_client,
        travel_buffer_minutes=travel_buffer,
    )

    proposal = ScheduleProposal(
        customer_id=body.customer_id,
        mode="offline",
        location=body.location,
        status="draft",
        slots_json=slots,
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)

    logger.info("[schedule/offline] created proposal id=%s slots=%d", proposal.id, len(slots))
    return _proposal_to_response(proposal)


@router.get("", response_model=list[ScheduleProposalResponse])
def list_schedule_proposals(db: Session = Depends(get_db)):
    proposals = (
        db.query(ScheduleProposal)
        .order_by(ScheduleProposal.created_at.desc())
        .all()
    )
    return [_proposal_to_response(p) for p in proposals]


@router.get("/{proposal_id}", response_model=ScheduleProposalResponse)
def get_schedule_proposal(proposal_id: uuid.UUID, db: Session = Depends(get_db)):
    proposal = db.get(ScheduleProposal, proposal_id)
    if not proposal:
        raise not_found("Schedule proposal")
    return _proposal_to_response(proposal)


@router.post("/{proposal_id}/approve", response_model=ScheduleProposalResponse)
def approve_slot(
    proposal_id: uuid.UUID,
    body: SlotApproveRequest,
    db: Session = Depends(get_db),
):
    proposal = db.get(ScheduleProposal, proposal_id)
    if not proposal:
        raise not_found("Schedule proposal")
    if proposal.status == "approved":
        raise invalid_status("Proposal is already approved")

    slots: list = proposal.slots_json or []
    if body.slot_index < 0 or body.slot_index >= len(slots):
        raise invalid_status(f"slot_index {body.slot_index} is out of range")

    proposal.status = "approved"
    proposal.approved_slot_index = body.slot_index
    from datetime import datetime as _dt
    proposal.updated_at = _dt.now(timezone.utc)
    db.commit()
    db.refresh(proposal)

    logger.info("[schedule] approved proposal id=%s slot=%d", proposal.id, body.slot_index)
    return _proposal_to_response(proposal)
