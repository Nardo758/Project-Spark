"""
Content Moderation Router

Endpoints for reporting content and admin moderation
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional
from datetime import datetime, timedelta

from app.db.database import get_db
from app.models.user import User
from app.models.report import Report, ReportStatus, ContentType, ReportReason
from app.models.opportunity import Opportunity
from app.models.comment import Comment
from app.schemas.moderation import (
    ReportCreate,
    ReportResponse,
    ReportResolve,
    ReportDismiss,
    ModerationStats,
    ModerationLogResponse,
    ContentModerationResult
)
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.services.moderation import moderation_service

router = APIRouter()


@router.post("/report", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
def create_report(
    report_data: ReportCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Report content for moderation"""
    # Validate content type
    try:
        content_type = ContentType(report_data.content_type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid content type: {report_data.content_type}"
        )

    # Validate reason
    try:
        reason = ReportReason(report_data.reason)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid report reason: {report_data.reason}"
        )

    # Verify content exists
    if content_type == ContentType.OPPORTUNITY:
        content = db.query(Opportunity).filter(Opportunity.id == report_data.content_id).first()
    elif content_type == ContentType.COMMENT:
        content = db.query(Comment).filter(Comment.id == report_data.content_id).first()
    elif content_type == ContentType.USER:
        content = db.query(User).filter(User.id == report_data.content_id).first()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    # Don't allow reporting your own content
    if content_type == ContentType.OPPORTUNITY and content.author_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot report your own opportunity"
        )
    elif content_type == ContentType.COMMENT and content.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot report your own comment"
        )
    elif content_type == ContentType.USER and content.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot report yourself"
        )

    # Check for duplicate reports
    existing_report = db.query(Report).filter(
        Report.reporter_id == current_user.id,
        Report.content_type == content_type,
        Report.content_id == report_data.content_id,
        Report.status.in_([ReportStatus.PENDING, ReportStatus.REVIEWING])
    ).first()

    if existing_report:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reported this content"
        )

    # Create report
    report = moderation_service.create_report(
        db=db,
        reporter_id=current_user.id,
        content_type=content_type,
        content_id=report_data.content_id,
        reason=reason,
        description=report_data.description
    )

    return report


@router.get("/reports", response_model=List[ReportResponse])
def list_reports(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    status_filter: Optional[str] = Query(None),
    content_type_filter: Optional[str] = Query(None),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """List moderation reports (admin only)"""
    query = db.query(Report)

    # Apply filters
    if status_filter:
        try:
            status_enum = ReportStatus(status_filter)
            query = query.filter(Report.status == status_enum)
        except ValueError:
            pass

    if content_type_filter:
        try:
            content_type_enum = ContentType(content_type_filter)
            query = query.filter(Report.content_type == content_type_enum)
        except ValueError:
            pass

    # Order by created_at desc
    reports = query.order_by(desc(Report.created_at)).offset(skip).limit(limit).all()

    return reports


@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report(
    report_id: int,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get report details (admin only)"""
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report not found"
        )

    return report


@router.post("/reports/{report_id}/resolve", response_model=ReportResponse)
def resolve_report(
    report_id: int,
    resolve_data: ReportResolve,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Resolve a report by taking action (admin only)"""
    try:
        report = moderation_service.resolve_report(
            db=db,
            report_id=report_id,
            moderator_id=admin_user.id,
            action_taken=resolve_data.action_taken,
            moderator_notes=resolve_data.moderator_notes
        )
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.post("/reports/{report_id}/dismiss", response_model=ReportResponse)
def dismiss_report(
    report_id: int,
    dismiss_data: ReportDismiss,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Dismiss a report as invalid (admin only)"""
    try:
        report = moderation_service.dismiss_report(
            db=db,
            report_id=report_id,
            moderator_id=admin_user.id,
            moderator_notes=dismiss_data.moderator_notes
        )
        return report
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.get("/stats", response_model=ModerationStats)
def get_moderation_stats(
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get moderation statistics (admin only)"""
    pending = db.query(Report).filter(Report.status == ReportStatus.PENDING).count()
    reviewing = db.query(Report).filter(Report.status == ReportStatus.REVIEWING).count()

    today = datetime.utcnow().date()
    resolved_today = db.query(Report).filter(
        Report.status == ReportStatus.RESOLVED,
        func.date(Report.reviewed_at) == today
    ).count()

    total = db.query(Report).count()

    # Get top reported content
    top_reported = db.query(
        Report.content_type,
        Report.content_id,
        func.count(Report.id).label('report_count')
    ).filter(
        Report.status == ReportStatus.PENDING
    ).group_by(
        Report.content_type,
        Report.content_id
    ).order_by(
        desc('report_count')
    ).limit(10).all()

    top_reported_list = [
        {
            "content_type": str(item.content_type.value),
            "content_id": item.content_id,
            "report_count": item.report_count
        }
        for item in top_reported
    ]

    return {
        "pending_reports": pending,
        "reviewing_reports": reviewing,
        "resolved_reports_today": resolved_today,
        "total_reports": total,
        "top_reported_content": top_reported_list
    }


@router.post("/check-content", response_model=ContentModerationResult)
def check_content(
    text: str,
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Run automated moderation checks on text (admin only)"""
    result = moderation_service.moderate_content(
        text=text,
        author_id=admin_user.id,
        db=db
    )

    return result


@router.get("/user/{user_id}/report-history")
def get_user_report_history(
    user_id: int,
    days: int = Query(30, ge=1, le=365),
    admin_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    """Get report history for a user (admin only)"""
    report_count = moderation_service.get_user_report_count(db, user_id, days)

    # Get actual reports
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Reports about user's opportunities
    opportunity_ids = [opp.id for opp in db.query(Opportunity).filter(
        Opportunity.author_id == user_id
    ).all()]

    opp_reports = db.query(Report).filter(
        Report.content_type == ContentType.OPPORTUNITY,
        Report.content_id.in_(opportunity_ids) if opportunity_ids else False,
        Report.created_at >= cutoff
    ).all() if opportunity_ids else []

    # Reports about user's comments
    comment_ids = [c.id for c in db.query(Comment).filter(
        Comment.user_id == user_id
    ).all()]

    comment_reports = db.query(Report).filter(
        Report.content_type == ContentType.COMMENT,
        Report.content_id.in_(comment_ids) if comment_ids else False,
        Report.created_at >= cutoff
    ).all() if comment_ids else []

    # Reports about user directly
    user_reports = db.query(Report).filter(
        Report.content_type == ContentType.USER,
        Report.content_id == user_id,
        Report.created_at >= cutoff
    ).all()

    all_reports = opp_reports + comment_reports + user_reports

    return {
        "user_id": user_id,
        "total_reports": report_count,
        "days": days,
        "reports": [
            {
                "id": r.id,
                "content_type": str(r.content_type.value),
                "content_id": r.content_id,
                "reason": str(r.reason.value),
                "status": str(r.status.value),
                "created_at": r.created_at
            }
            for r in all_reports
        ]
    }
