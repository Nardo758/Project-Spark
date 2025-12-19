from __future__ import annotations

from typing import Any, Dict, List, Tuple
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity
from app.models.user import User
from app.models.user_profile import UserProfile
from app.models.expert import Expert

from app.services.json_codec import loads_json


_CATEGORY_REQUIRED_SKILLS: dict[str, list[str]] = {
    "Technology": ["product", "engineering", "security", "data"],
    "Health & Wellness": ["compliance", "research", "growth", "partnerships"],
    "Finance": ["compliance", "risk", "payments", "accounting"],
    "Education": ["curriculum", "community", "product", "growth"],
    "Sustainability": ["supply_chain", "regulation", "partnerships", "sales"],
    "Lifestyle": ["branding", "growth", "community", "content"],
    "B2B Services": ["sales", "operations", "product", "customer_success"],
    "Consumer Products": ["branding", "supply_chain", "retail", "growth"],
}


def _normalize_skill(s: str) -> str:
    return (s or "").strip().lower().replace(" ", "_")


def _skill_overlap(user_skills: List[str], required: List[str]) -> Tuple[float, List[str]]:
    u = {_normalize_skill(x) for x in user_skills if x}
    r = [_normalize_skill(x) for x in required if x]
    if not r:
        return 1.0, []
    matched = sum(1 for x in r if x in u)
    missing = [x for x in r if x not in u]
    return matched / max(1, len(r)), missing


def _clamp_int(v: float, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, int(round(v))))


class AIEngineService:
    """
    AI Engine "Brain" service layer.

    This intentionally uses deterministic heuristics with optional enrichment
    from existing AI fields on the Opportunity record (e.g. ai_opportunity_score),
    so it works even when external model keys are not configured.
    """

    @staticmethod
    def get_or_create_profile(db: Session, user: User) -> UserProfile:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        if profile:
            return profile
        profile = UserProfile(user_id=user.id)
        db.add(profile)
        db.commit()
        db.refresh(profile)
        return profile

    @staticmethod
    def match_opportunity_to_user(db: Session, user: User, opportunity_id: int) -> Dict[str, Any]:
        opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opp:
            raise ValueError("Opportunity not found")

        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        user_skills = loads_json(profile.skills if profile else None, default=[])

        required = _CATEGORY_REQUIRED_SKILLS.get(opp.category or "", ["product", "growth"])
        overlap, missing = _skill_overlap(user_skills, required)

        # Capital/time/risk heuristics (lightweight, avoids hard requirements)
        capital_bonus = 0
        if profile and profile.available_capital is not None:
            # If user has any declared capital, small bonus (we don't know requirement here)
            capital_bonus = 5

        time_bonus = 0
        if profile and profile.time_commitment_hours_per_week is not None:
            if profile.time_commitment_hours_per_week >= 15:
                time_bonus = 5
            elif profile.time_commitment_hours_per_week >= 5:
                time_bonus = 2

        validation_signal = 0
        if opp.validation_count:
            validation_signal = min(10, int(opp.validation_count / 10))

        base_fit = 60 * overlap + capital_bonus + time_bonus + validation_signal
        fit_score = _clamp_int(base_fit, 0, 100)

        # Confidence: prefer AI score if available; otherwise based on validations.
        if opp.ai_opportunity_score is not None:
            confidence = _clamp_int(0.6 * opp.ai_opportunity_score + 0.4 * fit_score)
        else:
            confidence = _clamp_int(40 + validation_signal * 2 + overlap * 30)

        gaps = [x.replace("_", " ") for x in missing][:6]

        # Recommend experts that cover missing skills / category.
        experts = db.query(Expert).filter(Expert.is_active == True).all()
        recommended: List[dict] = []
        for ex in experts:
            ex_skills = loads_json(ex.skills, default=[])
            ex_specs = loads_json(ex.specialization, default=[])
            ex_terms = {_normalize_skill(x) for x in (ex_skills + ex_specs) if x}
            score = 0
            for g in missing:
                if _normalize_skill(g) in ex_terms:
                    score += 10
            if (opp.category or "").lower() in (x.lower() for x in ex_specs if isinstance(x, str)):
                score += 5
            if score > 0:
                recommended.append(
                    {
                        "expert_id": ex.id,
                        "name": ex.name,
                        "headline": ex.headline,
                        "pricing_model": ex.pricing_model.value if hasattr(ex.pricing_model, "value") else str(ex.pricing_model),
                        "score": score,
                    }
                )

        recommended.sort(key=lambda x: x.get("score", 0), reverse=True)
        recommended = recommended[:5]

        notes = None
        if not profile:
            notes = "No user profile yet; match is based on opportunity + weak signals."

        return {
            "fit_score": fit_score,
            "confidence": confidence,
            "gaps": gaps,
            "recommended_experts": recommended,
            "notes": notes,
        }

    @staticmethod
    def generate_roadmap(db: Session, user: User, opportunity_id: int) -> Dict[str, Any]:
        opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opp:
            raise ValueError("Opportunity not found")

        next_steps = loads_json(opp.ai_next_steps, default=[])
        key_risks = loads_json(opp.ai_key_risks, default=[])

        severity = opp.severity or 3
        feasibility = opp.feasibility_score if opp.feasibility_score is not None else 60

        # Rough timeline: higher severity + lower feasibility => longer.
        timeline_weeks = _clamp_int((severity * 3) + (100 - feasibility) / 20, 2, 26)

        milestones: List[dict] = []
        if next_steps:
            for i, step in enumerate(next_steps[:8], start=1):
                milestones.append(
                    {
                        "week": max(1, int(round(i * (timeline_weeks / max(1, min(8, len(next_steps))))))),
                        "title": f"Step {i}",
                        "description": str(step),
                    }
                )
        else:
            milestones = [
                {"week": 1, "title": "Problem validation", "description": "Interview target users and validate pain intensity."},
                {"week": 2, "title": "Solution outline", "description": "Define MVP scope, success metrics, and constraints."},
                {"week": 4, "title": "MVP build", "description": "Build the smallest testable product increment."},
                {"week": 6, "title": "Pilot launch", "description": "Run a small pilot and measure retention + willingness to pay."},
                {"week": 8, "title": "Iterate + scale", "description": "Fix top issues, improve onboarding, expand acquisition."},
            ]

        return {
            "opportunity_id": opportunity_id,
            "timeline_weeks": int(timeline_weeks),
            "milestones": milestones,
            "risks": [str(r) for r in key_risks][:8],
            "assumptions": {"severity": severity, "feasibility_score": feasibility},
        }

    @staticmethod
    def validate_opportunity(db: Session, user: User, opportunity_id: int) -> Dict[str, Any]:
        opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opp:
            raise ValueError("Opportunity not found")

        ai_score = opp.ai_opportunity_score
        if ai_score is None:
            # fallback score from signals we have
            validations = opp.validation_count or 0
            severity = opp.severity or 3
            feasibility = opp.feasibility_score if opp.feasibility_score is not None else 60
            ai_score = _clamp_int((feasibility * 0.6) + min(20, validations) + (severity * 4))

        score = _clamp_int(ai_score)
        if score >= 80:
            verdict = "fast_track"
        elif score >= 60:
            verdict = "refine"
        else:
            verdict = "pivot"

        next_steps = loads_json(opp.ai_next_steps, default=[])
        if not next_steps:
            next_steps = [
                "Define your ICP (ideal customer profile) and top 3 pain points.",
                "Validate willingness-to-pay with 10-20 target user calls.",
                "Prototype MVP and measure activation + retention.",
            ]

        risks = loads_json(opp.ai_key_risks, default=[])
        if not risks:
            risks = [
                "Unclear differentiation vs existing alternatives.",
                "Acquisition cost could exceed early pricing.",
                "Execution complexity underestimated.",
            ]

        return {
            "opportunity_id": opportunity_id,
            "validation_score": score,
            "verdict": verdict,
            "next_steps": [str(x) for x in next_steps][:8],
            "key_risks": [str(x) for x in risks][:8],
        }


ai_engine_service = AIEngineService()

