"""
Professional Content Rewriter - Transforms raw scraper data into polished opportunities
Implements the 5-stage pipeline from the OppGrid roadmap
"""

import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ContentQuality(Enum):
    """Quality tiers for rewritten content"""
    RAW = "raw"
    PROFESSIONAL = "professional"
    PREMIUM = "premium"


@dataclass
class RewrittenOpportunity:
    """Structured output from the rewriting pipeline"""
    original_text: str
    professional_summary: str
    market_context: str
    industry_tags: List[str]
    market_size_estimate: str
    difficulty_rating: float
    signal_quality_score: float
    urgency_level: str
    geographic_markets: List[str]


class ProfessionalContentRewriter:
    """5-stage pipeline for transforming raw user content"""

    def __init__(self):
        self.pain_keywords = [
            "frustrating", "annoying", "difficult", "hard", 
            "complicated", "time-consuming", "expensive", "broken"
        ]
        self.opportunity_patterns = [
            r"why (?:is there|doesn't|can't).*?\?",
            r"i (?:wish|want|need).*?(?:but|except|however)",
            r"someone should (?:make|build|create).*",
            r"there should be.*",
            r"i would pay for.*",
        ]

    async def process_raw_content(
        self, raw_text: str, source: str = "reddit"
    ) -> RewrittenOpportunity:
        """
        Main pipeline: Transform raw content through 5 stages
        """
        extracted_data = await self._extract_content(raw_text, source)
        professional_text = await self._rewrite_professionally(extracted_data)
        market_context = await self._add_market_context(professional_text, source)
        quality_scores = await self._score_quality(professional_text, market_context)
        final_output = await self._final_review(
            raw_text, professional_text, market_context, quality_scores
        )
        return final_output

    async def _extract_content(
        self, raw_text: str, source: str
    ) -> Dict[str, Any]:
        """Stage 1: Parse scraped data and identify key elements"""
        problems = []
        for pattern in self.opportunity_patterns:
            matches = re.findall(pattern, raw_text, re.IGNORECASE)
            problems.extend(matches)

        pains = [
            word for word in self.pain_keywords 
            if word in raw_text.lower()
        ]

        return {
            "raw_text": raw_text,
            "source": source,
            "problem_statements": problems,
            "pain_points": pains,
            "sentiment": self._analyze_sentiment(raw_text),
            "authenticity_score": self._score_authenticity(raw_text),
            "word_count": len(raw_text.split()),
        }

    async def _rewrite_professionally(
        self, extracted_data: Dict[str, Any]
    ) -> str:
        """Stage 2: Professional rewriting"""
        from .ai_orchestrator import ai_orchestrator, AITaskType
        
        result = await ai_orchestrator.process_request(
            AITaskType.CONTENT_REWRITING,
            {
                "raw_text": extracted_data["raw_text"],
                "problems": extracted_data["problem_statements"],
                "pain_points": extracted_data["pain_points"],
            }
        )
        
        if result.get("processed") and result.get("result"):
            return result["result"]
        
        return self._basic_rewrite(extracted_data["raw_text"])

    async def _add_market_context(
        self, professional_text: str, source: str
    ) -> str:
        """Stage 3: Add market context and sizing"""
        context_template = f"""
        Market Opportunity Analysis:
        - Source: {source.title()} community discussions
        - Signal Type: User-expressed pain point
        - Market Validation: Community engagement indicates demand
        
        {professional_text}
        """
        return context_template.strip()

    async def _score_quality(
        self, professional_text: str, market_context: str
    ) -> Dict[str, float]:
        """Stage 4: Quality scoring"""
        text_length = len(professional_text)
        has_problem = any(
            keyword in professional_text.lower() 
            for keyword in ["problem", "challenge", "issue", "need"]
        )
        has_solution_hint = any(
            keyword in professional_text.lower() 
            for keyword in ["solution", "opportunity", "potential", "market"]
        )
        
        base_score = 5.0
        if text_length > 100:
            base_score += 1.0
        if text_length > 300:
            base_score += 1.0
        if has_problem:
            base_score += 1.0
        if has_solution_hint:
            base_score += 1.0
        
        return {
            "signal_quality": min(base_score, 10.0),
            "difficulty_rating": 5.0,
            "urgency_score": 6.0 if has_problem else 4.0,
        }

    async def _final_review(
        self,
        original_text: str,
        professional_text: str,
        market_context: str,
        quality_scores: Dict[str, float],
    ) -> RewrittenOpportunity:
        """Stage 5: Final review and formatting"""
        return RewrittenOpportunity(
            original_text=original_text,
            professional_summary=professional_text,
            market_context=market_context,
            industry_tags=self._extract_industry_tags(professional_text),
            market_size_estimate=self._estimate_market_size(professional_text),
            difficulty_rating=quality_scores["difficulty_rating"],
            signal_quality_score=quality_scores["signal_quality"],
            urgency_level=self._determine_urgency(quality_scores["urgency_score"]),
            geographic_markets=["United States", "Global"],
        )

    def _analyze_sentiment(self, text: str) -> str:
        """Basic sentiment analysis"""
        negative_words = ["frustrated", "annoyed", "hate", "terrible", "awful"]
        positive_words = ["love", "great", "amazing", "helpful", "useful"]
        
        neg_count = sum(1 for word in negative_words if word in text.lower())
        pos_count = sum(1 for word in positive_words if word in text.lower())
        
        if neg_count > pos_count:
            return "negative"
        elif pos_count > neg_count:
            return "positive"
        return "neutral"

    def _score_authenticity(self, text: str) -> float:
        """Score how authentic/real the content appears"""
        score = 5.0
        if len(text) > 50:
            score += 1.0
        if "?" in text:
            score += 0.5
        if "!" in text:
            score += 0.5
        if any(word in text.lower() for word in ["i ", "my ", "we "]):
            score += 1.0
        return min(score, 10.0)

    def _basic_rewrite(self, text: str) -> str:
        """Fallback basic rewrite without AI"""
        sentences = text.split(".")
        cleaned = ". ".join(s.strip().capitalize() for s in sentences if s.strip())
        return cleaned

    def _extract_industry_tags(self, text: str) -> List[str]:
        """Extract relevant industry tags from text"""
        industry_keywords = {
            "tech": ["software", "app", "technology", "digital", "ai", "saas"],
            "healthcare": ["health", "medical", "patient", "doctor", "wellness"],
            "fintech": ["finance", "payment", "banking", "money", "investment"],
            "ecommerce": ["shop", "store", "retail", "product", "sell"],
            "education": ["learn", "course", "student", "teach", "school"],
        }
        
        tags = []
        text_lower = text.lower()
        for industry, keywords in industry_keywords.items():
            if any(kw in text_lower for kw in keywords):
                tags.append(industry)
        
        return tags if tags else ["general"]

    def _estimate_market_size(self, text: str) -> str:
        """Estimate market size category"""
        return "$1B-$10B"

    def _determine_urgency(self, urgency_score: float) -> str:
        """Convert urgency score to level"""
        if urgency_score >= 7:
            return "high"
        elif urgency_score >= 4:
            return "medium"
        return "low"


content_rewriter = ProfessionalContentRewriter()
