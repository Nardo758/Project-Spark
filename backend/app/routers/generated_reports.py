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
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """List current user's generated reports"""
    query = db.query(GeneratedReport).filter(GeneratedReport.user_id == current_user.id)
    
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
