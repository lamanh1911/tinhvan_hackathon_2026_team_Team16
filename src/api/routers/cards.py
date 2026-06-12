import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from src.api.config import get_settings
from src.api.database import get_db
from src.api.exceptions import invalid_status, not_found, validation_error
from src.api.models.business_card import BusinessCard
from src.api.models.customer import Customer
from src.api.schemas.cards import (
    REQUIRED_FIELDS,
    CardConfirmResponse,
    CardFieldUpdateRequest,
    CardFields,
    CardScanResponse,
)
from src.api.services.card_scanner import _CARD_TYPE_MESSAGES, _compute_validity, make_card_scanner

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cards", tags=["cards"])


def _get_scanner():
    settings = get_settings()
    return make_card_scanner(use_mocks=settings.use_mocks, settings=settings)


def _fields_to_schema(fields_json: dict) -> CardFields:
    return CardFields(**fields_json)


def _card_to_response(card: BusinessCard) -> CardScanResponse:
    fields_json: dict = card.fields_json or {}
    card_type: str = card.card_type or "business_card"

    if card_type != "business_card":
        return CardScanResponse(
            id=card.id,
            status=card.status,
            card_type=card_type,
            fields=_fields_to_schema(fields_json),
            is_valid_card=False,
            error_message=_CARD_TYPE_MESSAGES.get(card_type, _CARD_TYPE_MESSAGES["other"]),
            created_at=card.created_at,
        )

    is_valid_card, error_message = _compute_validity(fields_json)
    return CardScanResponse(
        id=card.id,
        status=card.status,
        card_type=card_type,
        fields=_fields_to_schema(fields_json),
        is_valid_card=is_valid_card,
        error_message=error_message,
        created_at=card.created_at,
    )


@router.post("/scan", response_model=CardScanResponse, status_code=201)
async def scan_card(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    logger.info("[scan_card] received upload: filename=%s content_type=%s", file.filename, file.content_type)
    image_bytes = await file.read()
    scanner = _get_scanner()
    result = await scanner.scan(
        image_bytes,
        file.filename or "card.jpg",
        content_type=file.content_type or "image/jpeg",
    )

    card_type: str = result["card_type"]
    logger.info("[scan_card] card_type=%s is_valid_card=%s", card_type, result["is_valid_card"])

    card = BusinessCard(
        image_ref=result["image_ref"],
        raw_ocr_text=result["raw_ocr_text"],
        card_type=card_type,
        fields_json=result["fields"],
        status="rejected" if card_type != "business_card" else "pending",
    )
    db.add(card)
    db.commit()
    db.refresh(card)

    return _card_to_response(card)


@router.get("/{card_id}", response_model=CardScanResponse)
def get_card(card_id: uuid.UUID, db: Session = Depends(get_db)):
    card = db.get(BusinessCard, card_id)
    if not card:
        raise not_found("Business card")
    return _card_to_response(card)


@router.patch("/{card_id}", response_model=CardScanResponse)
def update_card_fields(
    card_id: uuid.UUID,
    body: CardFieldUpdateRequest,
    db: Session = Depends(get_db),
):
    card = db.get(BusinessCard, card_id)
    if not card:
        raise not_found("Business card")
    if card.status == "confirmed":
        raise invalid_status("Cannot edit a confirmed card")
    if card.card_type and card.card_type != "business_card":
        raise invalid_status("Cannot edit a rejected card")

    fields: dict = dict(card.fields_json)
    for field_name, new_value in body.model_dump(exclude_none=True).items():
        if field_name in fields:
            fields[field_name] = {
                "value": new_value,
                "confidence": 1.0,
                "flagged": False,
            }

    card.fields_json = fields
    card.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(card)
    return _card_to_response(card)


@router.post("/{card_id}/confirm", response_model=CardConfirmResponse, status_code=201)
def confirm_card(card_id: uuid.UUID, db: Session = Depends(get_db)):
    card = db.get(BusinessCard, card_id)
    if not card:
        raise not_found("Business card")
    if card.status == "confirmed":
        raise invalid_status("Card is already confirmed")
    if card.card_type and card.card_type != "business_card":
        raise invalid_status("Cannot confirm a rejected card")

    fields: dict = card.fields_json

    for field_name in REQUIRED_FIELDS:
        field = fields.get(field_name, {})
        if not field.get("value") or field.get("flagged"):
            raise validation_error(
                f"Field '{field_name}' is required and must not be flagged before confirming"
            )

    customer = Customer(
        name=fields["name"]["value"],
        company=fields["company"]["value"],
        email=fields["email"]["value"],
        phone=fields.get("phone", {}).get("value"),
        title=fields.get("job_title", {}).get("value"),
        address=fields.get("address", {}).get("value"),
    )
    db.add(customer)
    db.flush()

    card.customer_id = customer.id
    card.status = "confirmed"
    card.updated_at = datetime.now(timezone.utc)
    db.commit()

    return CardConfirmResponse(id=card.id, customer_id=customer.id, status=card.status)
