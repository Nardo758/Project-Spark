from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.models.user_profile import ExperienceLevel, LearningStyle
from app.schemas.profile import UserProfileResponse, UserProfileUpdate
from app.services.ai_engine import ai_engine_service
from app.services.json_codec import dumps_json, loads_json


router = APIRouter()


@router.get("/me", response_model=UserProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    profile = ai_engine_service.get_or_create_profile(db, current_user)
    return UserProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        skills=loads_json(profile.skills, default=[]),
        experience_level=profile.experience_level.value if profile.experience_level else None,
        risk_tolerance=profile.risk_tolerance,
        available_capital=profile.available_capital,
        time_commitment_hours_per_week=profile.time_commitment_hours_per_week,
        past_successes=loads_json(profile.past_successes, default=None),
        failure_patterns=loads_json(profile.failure_patterns, default=None),
        learning_style=profile.learning_style.value if profile.learning_style else None,
    )


@router.put("/me", response_model=UserProfileResponse)
def update_my_profile(
    payload: UserProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    profile = ai_engine_service.get_or_create_profile(db, current_user)
    data = payload.model_dump(exclude_unset=True)

    if "skills" in data:
        profile.skills = dumps_json(data.get("skills") or [])

    if "past_successes" in data:
        profile.past_successes = dumps_json(data.get("past_successes"))

    if "failure_patterns" in data:
        profile.failure_patterns = dumps_json(data.get("failure_patterns"))

    if "experience_level" in data and data["experience_level"] is not None:
        profile.experience_level = ExperienceLevel(data["experience_level"])

    if "learning_style" in data and data["learning_style"] is not None:
        profile.learning_style = LearningStyle(data["learning_style"])

    for key in ["risk_tolerance", "available_capital", "time_commitment_hours_per_week"]:
        if key in data:
            setattr(profile, key, data.get(key))

    db.commit()
    db.refresh(profile)

    return UserProfileResponse(
        id=profile.id,
        user_id=profile.user_id,
        skills=loads_json(profile.skills, default=[]),
        experience_level=profile.experience_level.value if profile.experience_level else None,
        risk_tolerance=profile.risk_tolerance,
        available_capital=profile.available_capital,
        time_commitment_hours_per_week=profile.time_commitment_hours_per_week,
        past_successes=loads_json(profile.past_successes, default=None),
        failure_patterns=loads_json(profile.failure_patterns, default=None),
        learning_style=profile.learning_style.value if profile.learning_style else None,
    )

