"""
Content Moderation Service

Automated and manual moderation tools
"""

import re
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.report import Report, ReportStatus, ContentType, ReportReason, ModerationLog
from app.models.opportunity import Opportunity
from app.models.comment import Comment
from app.models.user import User


class ModerationService:
    """Service for content moderation"""

    # Basic profanity filter (expandable)
    PROFANITY_LIST = [
        "spam", "scam", "fake", "bullshit", "ass", "damn", "shit", "fuck",
        "penis", "viagra", "crypto", "bitcoin", "nft", "airdrop"
    ]

    # Spam patterns
    SPAM_PATTERNS = [
        r"(click|visit)\s+(here|this|link)",
        r"(buy|sell)\s+(now|today)",
        r"limited\s+time\s+offer",
        r"act\s+now",
        r"free\s+(money|crypto|bitcoin)",
        r"(http|https)://.*\.(tk|ml|ga|cf|gq)",  # Suspicious TLDs
        r"(telegram|whatsapp|discord).*@",  # Social media spam
        r"\$\d+.*per\s+(day|hour|week)",  # Money spam
    ]

    @staticmethod
    def check_profanity(text: str) -> Tuple[bool, List[str]]:
        """
        Check if text contains profanity

        Returns:
            (contains_profanity, list_of_matched_words)
        """
        text_lower = text.lower()
        matched = []

        for word in ModerationService.PROFANITY_LIST:
            if word in text_lower:
                matched.append(word)

        return len(matched) > 0, matched

    @staticmethod
    def check_spam(text: str) -> Tuple[bool, List[str]]:
        """
        Check if text matches spam patterns

        Returns:
            (is_spam, list_of_matched_patterns)
        """
        matched_patterns = []

        for pattern in ModerationService.SPAM_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                matched_patterns.append(pattern)

        return len(matched_patterns) > 0, matched_patterns

    @staticmethod
    def check_duplicate_opportunity(db: Session, title: str, author_id: int) -> Optional[Opportunity]:
        """
        Check if opportunity title is too similar to existing ones from same user

        Returns:
            Duplicate opportunity if found, None otherwise
        """
        # Simple duplicate check: exact title match from same user
        existing = db.query(Opportunity).filter(
            Opportunity.title == title,
            Opportunity.author_id == author_id
        ).first()

        return existing

    @staticmethod
    def moderate_content(text: str, author_id: int, db: Session = None) -> dict:
        """
        Run automated moderation checks on content

        Returns:
            dict with moderation results
        """
        results = {
            "is_safe": True,
            "warnings": [],
            "flags": []
        }

        # Check profanity
        has_profanity, profane_words = ModerationService.check_profanity(text)
        if has_profanity:
            results["is_safe"] = False
            results["flags"].append({
                "type": "profanity",
                "matched": profane_words
            })

        # Check spam patterns
        is_spam, spam_patterns = ModerationService.check_spam(text)
        if is_spam:
            results["is_safe"] = False
            results["flags"].append({
                "type": "spam",
                "matched": spam_patterns
            })

        # Check length (too short might be spam)
        if len(text.strip()) < 10:
            results["warnings"].append("Content is very short")

        # Check for excessive caps (SHOUTING)
        caps_ratio = sum(1 for c in text if c.isupper()) / max(len(text), 1)
        if caps_ratio > 0.5 and len(text) > 20:
            results["warnings"].append("Excessive capitalization")

        # Check for excessive links
        link_count = len(re.findall(r'http[s]?://', text))
        if link_count > 3:
            results["is_safe"] = False
            results["flags"].append({
                "type": "excessive_links",
                "count": link_count
            })

        return results

    @staticmethod
    def create_report(
        db: Session,
        reporter_id: int,
        content_type: ContentType,
        content_id: int,
        reason: ReportReason,
        description: Optional[str] = None
    ) -> Report:
        """Create a content report"""
        report = Report(
            reporter_id=reporter_id,
            content_type=content_type,
            content_id=content_id,
            reason=reason,
            description=description,
            status=ReportStatus.PENDING
        )

        db.add(report)
        db.commit()
        db.refresh(report)

        return report

    @staticmethod
    def resolve_report(
        db: Session,
        report_id: int,
        moderator_id: int,
        action_taken: str,
        moderator_notes: Optional[str] = None
    ) -> Report:
        """Resolve a moderation report"""
        report = db.query(Report).filter(Report.id == report_id).first()

        if not report:
            raise ValueError("Report not found")

        report.status = ReportStatus.RESOLVED
        report.moderator_id = moderator_id
        report.action_taken = action_taken
        report.moderator_notes = moderator_notes
        report.reviewed_at = datetime.utcnow()

        db.commit()
        db.refresh(report)

        # Log the moderation action
        ModerationService.log_action(
            db=db,
            moderator_id=moderator_id,
            action=action_taken,
            content_type=str(report.content_type.value),
            content_id=report.content_id,
            reason=str(report.reason.value),
            notes=moderator_notes
        )

        return report

    @staticmethod
    def dismiss_report(
        db: Session,
        report_id: int,
        moderator_id: int,
        moderator_notes: Optional[str] = None
    ) -> Report:
        """Dismiss a report as invalid"""
        report = db.query(Report).filter(Report.id == report_id).first()

        if not report:
            raise ValueError("Report not found")

        report.status = ReportStatus.DISMISSED
        report.moderator_id = moderator_id
        report.moderator_notes = moderator_notes
        report.reviewed_at = datetime.utcnow()

        db.commit()
        db.refresh(report)

        return report

    @staticmethod
    def log_action(
        db: Session,
        moderator_id: int,
        action: str,
        content_type: str,
        content_id: int,
        reason: Optional[str] = None,
        notes: Optional[str] = None
    ) -> ModerationLog:
        """Log a moderation action"""
        log = ModerationLog(
            moderator_id=moderator_id,
            action=action,
            content_type=content_type,
            content_id=content_id,
            reason=reason,
            notes=notes
        )

        db.add(log)
        db.commit()
        db.refresh(log)

        return log

    @staticmethod
    def get_user_report_count(db: Session, user_id: int, days: int = 30) -> int:
        """Get number of reports about a user's content in recent days"""
        from datetime import timedelta

        cutoff = datetime.utcnow() - timedelta(days=days)

        # Count reports on user's opportunities
        opportunity_ids = [opp.id for opp in db.query(Opportunity).filter(
            Opportunity.author_id == user_id
        ).all()]

        opp_reports = db.query(Report).filter(
            Report.content_type == ContentType.OPPORTUNITY,
            Report.content_id.in_(opportunity_ids) if opportunity_ids else False,
            Report.created_at >= cutoff
        ).count() if opportunity_ids else 0

        # Count reports on user's comments
        comment_ids = [c.id for c in db.query(Comment).filter(
            Comment.user_id == user_id
        ).all()]

        comment_reports = db.query(Report).filter(
            Report.content_type == ContentType.COMMENT,
            Report.content_id.in_(comment_ids) if comment_ids else False,
            Report.created_at >= cutoff
        ).count() if comment_ids else 0

        # Count reports about the user directly
        user_reports = db.query(Report).filter(
            Report.content_type == ContentType.USER,
            Report.content_id == user_id,
            Report.created_at >= cutoff
        ).count()

        return opp_reports + comment_reports + user_reports


moderation_service = ModerationService()
