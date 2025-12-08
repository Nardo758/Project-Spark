from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.schemas.validation import Validation, ValidationCreate
from app.models.validation import Validation as ValidationModel
from app.models.opportunity import Opportunity as OpportunityModel

router = APIRouter()


@router.post("/", response_model=Validation, status_code=201)
def create_validation(
    validation: ValidationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a validation for an opportunity.
    Note: In production, get user_id from authenticated user token.
    For MVP, we'll use a placeholder user_id=1.
    """
    # Check if opportunity exists
    opportunity = db.query(OpportunityModel).filter(
        OpportunityModel.id == validation.opportunity_id
    ).first()

    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")

    # TODO: Get user_id from authenticated user
    # For now, using placeholder user_id=1
    user_id = 1

    # Check if user already validated this opportunity
    existing_validation = db.query(ValidationModel).filter(
        ValidationModel.user_id == user_id,
        ValidationModel.opportunity_id == validation.opportunity_id
    ).first()

    if existing_validation:
        raise HTTPException(
            status_code=400,
            detail="You have already validated this opportunity"
        )

    # Create validation
    db_validation = ValidationModel(
        user_id=user_id,
        opportunity_id=validation.opportunity_id,
        is_valid=validation.is_valid,
        comment=validation.comment
    )

    db.add(db_validation)

    # Update opportunity counters
    opportunity.validation_count += 1
    if validation.is_valid:
        opportunity.agree_count += 1
    else:
        opportunity.disagree_count += 1

    # Calculate friction score (simple algorithm)
    if opportunity.validation_count > 0:
        opportunity.friction_score = (opportunity.agree_count / opportunity.validation_count) * 100

    db.commit()
    db.refresh(db_validation)

    return db_validation


@router.get("/opportunity/{opportunity_id}", response_model=list[Validation])
def get_opportunity_validations(
    opportunity_id: int,
    db: Session = Depends(get_db)
):
    """Get all validations for a specific opportunity"""
    validations = db.query(ValidationModel).filter(
        ValidationModel.opportunity_id == opportunity_id
    ).all()

    return validations
