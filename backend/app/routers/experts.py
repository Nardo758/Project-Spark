from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.core.dependencies import get_current_admin_user
from app.db.database import get_db
from app.models.expert import Expert, ExpertPricingModel
from app.schemas.expert import ExpertCreate, ExpertUpdate, ExpertResponse
from app.services.json_codec import dumps_json, loads_json


router = APIRouter()


@router.get("/", response_model=list[ExpertResponse])
def list_experts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    active_only: bool = True,
    db: Session = Depends(get_db),
):
    q = db.query(Expert)
    if active_only:
        q = q.filter(Expert.is_active == True)
    experts = q.order_by(desc(Expert.created_at)).offset(skip).limit(limit).all()

    # Normalize JSON fields for response model
    out: list[ExpertResponse] = []
    for e in experts:
        out.append(
            ExpertResponse(
                id=e.id,
                name=e.name,
                headline=e.headline,
                bio=e.bio,
                website_url=e.website_url,
                skills=loads_json(e.skills, default=[]),
                specialization=loads_json(e.specialization, default=[]),
                pricing_model=e.pricing_model.value if hasattr(e.pricing_model, "value") else str(e.pricing_model),
                hourly_rate_cents=e.hourly_rate_cents,
                fixed_price_cents=e.fixed_price_cents,
                success_fee_bps=e.success_fee_bps,
                currency=e.currency,
                availability=loads_json(e.availability, default=None),
                is_active=e.is_active,
            )
        )
    return out


@router.post("/", response_model=ExpertResponse, status_code=status.HTTP_201_CREATED)
def create_expert(
    payload: ExpertCreate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    try:
        pricing_model = ExpertPricingModel(payload.pricing_model)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid pricing_model")

    expert = Expert(
        name=payload.name,
        headline=payload.headline,
        bio=payload.bio,
        website_url=payload.website_url,
        skills=dumps_json(payload.skills or []),
        specialization=dumps_json(payload.specialization or []),
        pricing_model=pricing_model,
        hourly_rate_cents=payload.hourly_rate_cents,
        fixed_price_cents=payload.fixed_price_cents,
        success_fee_bps=payload.success_fee_bps,
        currency=payload.currency,
        availability=dumps_json(payload.availability) if payload.availability is not None else None,
        is_active=payload.is_active,
    )
    db.add(expert)
    db.commit()
    db.refresh(expert)

    return ExpertResponse(
        id=expert.id,
        name=expert.name,
        headline=expert.headline,
        bio=expert.bio,
        website_url=expert.website_url,
        skills=loads_json(expert.skills, default=[]),
        specialization=loads_json(expert.specialization, default=[]),
        pricing_model=expert.pricing_model.value,
        hourly_rate_cents=expert.hourly_rate_cents,
        fixed_price_cents=expert.fixed_price_cents,
        success_fee_bps=expert.success_fee_bps,
        currency=expert.currency,
        availability=loads_json(expert.availability, default=None),
        is_active=expert.is_active,
    )


@router.put("/{expert_id}", response_model=ExpertResponse)
def update_expert(
    expert_id: int,
    payload: ExpertUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(get_current_admin_user),
):
    expert = db.query(Expert).filter(Expert.id == expert_id).first()
    if not expert:
        raise HTTPException(status_code=404, detail="Expert not found")

    data = payload.model_dump(exclude_unset=True)
    if "pricing_model" in data and data["pricing_model"] is not None:
        expert.pricing_model = ExpertPricingModel(data["pricing_model"])

    if "skills" in data:
        expert.skills = dumps_json(data.get("skills") or [])
    if "specialization" in data:
        expert.specialization = dumps_json(data.get("specialization") or [])
    if "availability" in data:
        expert.availability = dumps_json(data.get("availability")) if data.get("availability") is not None else None

    for key in [
        "name",
        "headline",
        "bio",
        "website_url",
        "hourly_rate_cents",
        "fixed_price_cents",
        "success_fee_bps",
        "currency",
        "is_active",
    ]:
        if key in data:
            setattr(expert, key, data.get(key))

    db.commit()
    db.refresh(expert)

    return ExpertResponse(
        id=expert.id,
        name=expert.name,
        headline=expert.headline,
        bio=expert.bio,
        website_url=expert.website_url,
        skills=loads_json(expert.skills, default=[]),
        specialization=loads_json(expert.specialization, default=[]),
        pricing_model=expert.pricing_model.value,
        hourly_rate_cents=expert.hourly_rate_cents,
        fixed_price_cents=expert.fixed_price_cents,
        success_fee_bps=expert.success_fee_bps,
        currency=expert.currency,
        availability=loads_json(expert.availability, default=None),
        is_active=expert.is_active,
    )

