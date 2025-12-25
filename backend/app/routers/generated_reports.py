from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.user import User
from app.models.generated_report import GeneratedReport, ReportType, ReportStatus
from app.schemas.generated_report import (
    GeneratedReportCreate,
    GeneratedReportUpdate,
    GeneratedReportResponse,
    GeneratedReportDetail,
    GeneratedReportList,
    ReportStats,
    UserReportStats,
)
from app.core.dependencies import get_current_user, get_current_admin_user

router = APIRouter()


@router.post("/", response_model=GeneratedReportResponse)
def create_report(
    payload: GeneratedReportCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new generated report record"""
    report = GeneratedReport(
        user_id=current_user.id,
        opportunity_id=payload.opportunity_id,
        report_type=ReportType(payload.report_type.value),
        title=payload.title,
        status=ReportStatus.PENDING,
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


@router.patch("/{report_id}", response_model=GeneratedReportResponse)
def update_report(
    report_id: int,
    payload: GeneratedReportUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a report (status, content, scores)"""
    report = db.query(GeneratedReport).filter(
        GeneratedReport.id == report_id,
        GeneratedReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    update_data = payload.model_dump(exclude_unset=True)
    
    if "status" in update_data:
        update_data["status"] = ReportStatus(update_data["status"])
        if update_data["status"] == ReportStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
    
    for key, value in update_data.items():
        setattr(report, key, value)
    
    db.commit()
    db.refresh(report)
    return report


@router.get("/", response_model=GeneratedReportList)
def list_user_reports(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    report_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    opportunity_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List current user's generated reports"""
    query = db.query(GeneratedReport).filter(GeneratedReport.user_id == current_user.id)
    
    if opportunity_id:
        query = query.filter(GeneratedReport.opportunity_id == opportunity_id)
    
    if report_type:
        try:
            query = query.filter(GeneratedReport.report_type == ReportType(report_type))
        except ValueError:
            pass
    
    if status:
        try:
            query = query.filter(GeneratedReport.status == ReportStatus(status))
        except ValueError:
            pass
    
    total = query.count()
    reports = query.order_by(desc(GeneratedReport.created_at)).offset((page - 1) * page_size).limit(page_size).all()
    
    return {
        "reports": reports,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/my-stats", response_model=UserReportStats)
def get_user_report_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get current user's report statistics"""
    now = datetime.utcnow()
    month_ago = now - timedelta(days=30)
    
    total = db.query(GeneratedReport).filter(
        GeneratedReport.user_id == current_user.id
    ).count()
    
    this_month = db.query(GeneratedReport).filter(
        GeneratedReport.user_id == current_user.id,
        GeneratedReport.created_at >= month_ago
    ).count()
    
    by_type_results = db.query(
        GeneratedReport.report_type,
        func.count(GeneratedReport.id)
    ).filter(
        GeneratedReport.user_id == current_user.id
    ).group_by(GeneratedReport.report_type).all()
    
    by_type = {r[0].value if r[0] else "unknown": r[1] for r in by_type_results}
    
    return {
        "total_reports": total,
        "reports_this_month": this_month,
        "by_type": by_type,
    }


@router.get("/stats", response_model=ReportStats)
def get_report_stats(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get platform-wide report statistics (admin only)"""
    now = datetime.utcnow()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    total = db.query(GeneratedReport).count()
    
    today = db.query(GeneratedReport).filter(
        GeneratedReport.created_at >= today_start
    ).count()
    
    this_week = db.query(GeneratedReport).filter(
        GeneratedReport.created_at >= week_ago
    ).count()
    
    this_month = db.query(GeneratedReport).filter(
        GeneratedReport.created_at >= month_ago
    ).count()
    
    by_type_results = db.query(
        GeneratedReport.report_type,
        func.count(GeneratedReport.id)
    ).group_by(GeneratedReport.report_type).all()
    
    by_type = {r[0].value if r[0] else "unknown": r[1] for r in by_type_results}
    
    by_status_results = db.query(
        GeneratedReport.status,
        func.count(GeneratedReport.id)
    ).group_by(GeneratedReport.status).all()
    
    by_status = {r[0].value if r[0] else "unknown": r[1] for r in by_status_results}
    
    avg_time = db.query(func.avg(GeneratedReport.generation_time_ms)).filter(
        GeneratedReport.generation_time_ms.isnot(None)
    ).scalar()
    
    avg_confidence = db.query(func.avg(GeneratedReport.confidence_score)).filter(
        GeneratedReport.confidence_score.isnot(None)
    ).scalar()
    
    return {
        "total_reports": total,
        "reports_today": today,
        "reports_this_week": this_week,
        "reports_this_month": this_month,
        "by_type": by_type,
        "by_status": by_status,
        "avg_generation_time_ms": float(avg_time) if avg_time else None,
        "avg_confidence_score": float(avg_confidence) if avg_confidence else None,
    }


@router.get("/{report_id}", response_model=GeneratedReportDetail)
def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a specific report with full content"""
    report = db.query(GeneratedReport).filter(
        GeneratedReport.id == report_id,
        GeneratedReport.user_id == current_user.id
    ).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return report


@router.post("/opportunity/{opportunity_id}/layer1")
def generate_layer1_report(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate Layer 1: Problem Overview Report
    
    Access: Pro tier and above, or $15 one-time purchase (via pay-per-unlock)
    
    Includes:
    - Executive Summary
    - The Problem (pain points, severity)
    - Market Snapshot (size, audience, competition)
    - Validation Signals
    - Key Risks
    - Next Steps
    """
    from app.models.opportunity import Opportunity
    from app.services.report_generator import ReportGenerator
    
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    generator = ReportGenerator(db)
    entitlement = generator.check_entitlement(current_user, ReportType.LAYER_1_OVERVIEW)
    
    if not entitlement["allowed"]:
        has_paid_unlock = False
        try:
            from app.routers.opportunities import get_opportunity_entitlements
            opp_ent = get_opportunity_entitlements(opportunity, current_user, db)
            has_paid_unlock = opp_ent.is_unlocked
        except Exception:
            pass
        
        if not has_paid_unlock:
            raise HTTPException(
                status_code=403,
                detail={
                    "message": "Layer 1 reports require Pro tier or paid opportunity unlock ($15)",
                    "required_tiers": entitlement.get("required_tiers"),
                    "user_tier": entitlement.get("user_tier"),
                    "price_cents": 1500,
                    "can_purchase": True,
                    "purchase_path": f"/opportunity/{opportunity_id}?unlock=true"
                }
            )
    
    existing = db.query(GeneratedReport).filter(
        GeneratedReport.user_id == current_user.id,
        GeneratedReport.opportunity_id == opportunity_id,
        GeneratedReport.report_type == ReportType.LAYER_1_OVERVIEW,
        GeneratedReport.status == ReportStatus.COMPLETED
    ).first()
    
    if existing:
        return {
            "report_id": existing.id,
            "status": "existing",
            "message": "Layer 1 report already exists for this opportunity",
            "report": {
                "id": existing.id,
                "title": existing.title,
                "summary": existing.summary,
                "content": existing.content,
                "confidence_score": existing.confidence_score,
                "created_at": existing.created_at.isoformat() if existing.created_at else None,
            }
        }
    
    demographics = opportunity.demographics if hasattr(opportunity, 'demographics') else None
    report = generator.generate_layer1_report(opportunity, current_user, demographics)
    
    return {
        "report_id": report.id,
        "status": "generated",
        "message": "Layer 1 report generated successfully",
        "report": {
            "id": report.id,
            "title": report.title,
            "summary": report.summary,
            "content": report.content,
            "confidence_score": report.confidence_score,
            "generation_time_ms": report.generation_time_ms,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }
    }


@router.post("/opportunity/{opportunity_id}/layer2")
def generate_layer2_report(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate Layer 2: Deep Dive Analysis Report
    
    Access: Business tier and above
    
    Includes:
    - TAM/SAM/SOM Analysis
    - Demographic Deep Dive (Census data)
    - Competitive Landscape
    - Geographic Analysis
    - Business Model Recommendations
    """
    from app.models.opportunity import Opportunity
    from app.services.report_generator import ReportGenerator
    
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    generator = ReportGenerator(db)
    entitlement = generator.check_entitlement(current_user, ReportType.LAYER_2_DEEP_DIVE)
    
    if not entitlement["allowed"]:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Layer 2 Deep Dive reports require Business tier or higher",
                "required_tiers": entitlement.get("required_tiers"),
                "user_tier": entitlement.get("user_tier"),
            }
        )
    
    existing = db.query(GeneratedReport).filter(
        GeneratedReport.user_id == current_user.id,
        GeneratedReport.opportunity_id == opportunity_id,
        GeneratedReport.report_type == ReportType.LAYER_2_DEEP_DIVE,
        GeneratedReport.status == ReportStatus.COMPLETED
    ).first()
    
    if existing:
        return {
            "report_id": existing.id,
            "status": "existing",
            "message": "Layer 2 report already exists for this opportunity",
            "report": {
                "id": existing.id,
                "title": existing.title,
                "summary": existing.summary,
                "content": existing.content,
                "confidence_score": existing.confidence_score,
                "created_at": existing.created_at.isoformat() if existing.created_at else None,
            }
        }
    
    demographics = opportunity.demographics if hasattr(opportunity, 'demographics') else None
    report = generator.generate_layer2_report(opportunity, current_user, demographics)
    
    return {
        "report_id": report.id,
        "status": "generated",
        "message": "Layer 2 Deep Dive report generated successfully",
        "report": {
            "id": report.id,
            "title": report.title,
            "summary": report.summary,
            "content": report.content,
            "confidence_score": report.confidence_score,
            "generation_time_ms": report.generation_time_ms,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }
    }


@router.post("/opportunity/{opportunity_id}/layer3")
def generate_layer3_report(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate Layer 3: Execution Package Report
    
    Access: Business tier (5/month limit) or Enterprise (unlimited)
    
    Includes:
    - Full Business Plan Summary
    - Go-to-Market Strategy (3 phases)
    - Financial Projections (3-year)
    - 90-Day Action Roadmap
    - Risk Mitigation Plan
    """
    from app.models.opportunity import Opportunity
    from app.services.report_generator import ReportGenerator
    
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    generator = ReportGenerator(db)
    entitlement = generator.check_entitlement(current_user, ReportType.LAYER_3_EXECUTION)
    
    if not entitlement["allowed"]:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "Layer 3 Execution Package requires Business tier or higher",
                "required_tiers": entitlement.get("required_tiers"),
                "user_tier": entitlement.get("user_tier"),
            }
        )
    
    user_tier = getattr(current_user, 'tier', 'free')
    if hasattr(user_tier, 'value'):
        user_tier = user_tier.value
    user_tier = str(user_tier).lower() if user_tier else 'free'
    
    if user_tier == 'business':
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        rolling_count = db.query(GeneratedReport).filter(
            GeneratedReport.user_id == current_user.id,
            GeneratedReport.report_type == ReportType.LAYER_3_EXECUTION,
            GeneratedReport.created_at >= thirty_days_ago
        ).count()
        
        if rolling_count >= 5:
            raise HTTPException(
                status_code=403,
                detail={
                    "message": "Business tier is limited to 5 Layer 3 reports per rolling 30-day period",
                    "rolling_limit": 5,
                    "used": rolling_count,
                    "upgrade_to": "enterprise",
                    "next_available": "Check again when your oldest report is 30+ days old"
                }
            )
    
    existing = db.query(GeneratedReport).filter(
        GeneratedReport.user_id == current_user.id,
        GeneratedReport.opportunity_id == opportunity_id,
        GeneratedReport.report_type == ReportType.LAYER_3_EXECUTION,
        GeneratedReport.status == ReportStatus.COMPLETED
    ).first()
    
    if existing:
        return {
            "report_id": existing.id,
            "status": "existing",
            "message": "Layer 3 Execution Package already exists for this opportunity",
            "report": {
                "id": existing.id,
                "title": existing.title,
                "summary": existing.summary,
                "content": existing.content,
                "confidence_score": existing.confidence_score,
                "created_at": existing.created_at.isoformat() if existing.created_at else None,
            }
        }
    
    demographics = opportunity.demographics if hasattr(opportunity, 'demographics') else None
    report = generator.generate_layer3_report(opportunity, current_user, demographics)
    
    return {
        "report_id": report.id,
        "status": "generated",
        "message": "Layer 3 Execution Package generated successfully",
        "report": {
            "id": report.id,
            "title": report.title,
            "summary": report.summary,
            "content": report.content,
            "confidence_score": report.confidence_score,
            "generation_time_ms": report.generation_time_ms,
            "created_at": report.created_at.isoformat() if report.created_at else None,
        }
    }
