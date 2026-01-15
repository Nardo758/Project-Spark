from fastapi import APIRouter, Query
from typing import Optional, List, Dict
from app.services.sba_service import sba_service, US_STATES, LOAN_CATEGORIES

router = APIRouter(tags=["sba"])


@router.get("/loan-programs")
async def get_loan_programs(
    category: Optional[str] = Query(None, description="Loan category to filter")
) -> List[Dict]:
    return await sba_service.get_loan_programs(category=category)


@router.get("/courses")
async def get_courses(
    business_stage: Optional[str] = Query(None, description="Business stage filter"),
    financing_only: bool = Query(False, description="Only return financing-related courses")
) -> List[Dict]:
    if financing_only:
        return await sba_service.get_financing_courses(business_stage=business_stage)
    return await sba_service.get_all_courses(business_stage=business_stage)


@router.get("/lender-match-url")
async def get_lender_match_url() -> Dict:
    url = await sba_service.get_lender_match_url()
    return {"url": url}


@router.get("/states")
async def get_states() -> List[Dict]:
    return US_STATES


@router.get("/loan-categories")
async def get_loan_categories() -> List[str]:
    return LOAN_CATEGORIES


@router.get("/top-lenders")
async def get_top_lenders() -> List[Dict]:
    return await sba_service.get_top_sba_lenders()
