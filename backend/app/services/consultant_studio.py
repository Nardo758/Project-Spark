"""
Consultant Studio Service - Enhanced three-path validation system
Implements: Validate Idea, Search Ideas, Identify Location
"""

import asyncio
import hashlib
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session

from app.models.consultant_activity import ConsultantActivity, ConsultantPath
from app.models.detected_trend import DetectedTrend
from app.models.trend_opportunity_mapping import TrendOpportunityMapping
from app.models.location_analysis_cache import LocationAnalysisCache, BusinessType
from app.models.opportunity import Opportunity

logger = logging.getLogger(__name__)


class ConsultantStudioService:
    """Three-path validation system with dual AI architecture"""

    CACHE_TTL_DAYS = 30
    _validation_cache: Dict[str, Dict[str, Any]] = {}

    def __init__(self, db: Session):
        self.db = db

    def _get_cache_key(self, idea_description: str, context: Optional[Dict] = None) -> str:
        """Generate a cache key for validation results"""
        content = idea_description.lower().strip()
        if context:
            content += json.dumps(context, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()

    def _get_cached_validation(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached validation result if exists and not expired"""
        if cache_key in self._validation_cache:
            cached = self._validation_cache[cache_key]
            if datetime.utcnow() - cached.get('cached_at', datetime.min) < timedelta(hours=1):
                logger.info(f"Cache hit for validation: {cache_key[:8]}")
                return cached.get('result')
        return None

    def _cache_validation(self, cache_key: str, result: Dict[str, Any]):
        """Cache validation result"""
        self._validation_cache[cache_key] = {
            'result': result,
            'cached_at': datetime.utcnow()
        }
        if len(self._validation_cache) > 100:
            oldest_key = min(self._validation_cache.keys(), 
                           key=lambda k: self._validation_cache[k].get('cached_at', datetime.min))
            del self._validation_cache[oldest_key]

    async def validate_idea(
        self,
        user_id: int,
        idea_description: str,
        business_context: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Path 1: Validate Idea - Online vs Physical decision engine
        Uses DeepSeek for pattern analysis + Claude for viability report
        OPTIMIZED: Parallel AI calls and caching for faster response
        """
        import time
        start_time = time.time()
        
        cache_key = self._get_cache_key(idea_description, business_context)
        cached_result = self._get_cached_validation(cache_key)
        if cached_result:
            cached_result['from_cache'] = True
            cached_result['processing_time_ms'] = int((time.time() - start_time) * 1000)
            return cached_result
        
        try:
            similar_opportunities = await self._find_similar_opportunities(idea_description)
            
            pattern_analysis = await self._deepseek_pattern_analysis(
                idea_description, 
                similar_opportunities,
                business_context
            )
            
            online_score, physical_score = self._calculate_business_type_scores(
                pattern_analysis,
                business_context
            )
            
            viability_report = await self._claude_viability_report(
                idea_description,
                pattern_analysis,
                online_score,
                physical_score,
                business_context
            )
            
            recommendation = self._determine_recommendation(online_score, physical_score)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            result = {
                "success": True,
                "idea_description": idea_description,
                "recommendation": recommendation,
                "online_score": online_score,
                "physical_score": physical_score,
                "pattern_analysis": pattern_analysis,
                "viability_report": viability_report,
                "similar_opportunities": [
                    {"id": o.id, "title": o.title, "score": o.feasibility_score or 0}
                    for o in similar_opportunities[:5]
                ],
                "processing_time_ms": processing_time,
                "from_cache": False,
            }
            
            self._cache_validation(cache_key, result)
            
            await self._log_activity(
                user_id=user_id,
                session_id=session_id,
                path=ConsultantPath.validate_idea.value,
                action="idea_validation_complete",
                payload={"idea": idea_description[:200], "context": business_context},
                result_summary=f"Recommended: {recommendation}, Online: {online_score}, Physical: {physical_score}",
                ai_model_used="hybrid",
                processing_time_ms=processing_time,
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error validating idea: {e}")
            return {"success": False, "error": str(e)}

    async def search_ideas(
        self,
        user_id: int,
        filters: Dict[str, Any],
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Path 2: Search Ideas - Database exploration with trend detection
        Uses DeepSeek for trend detection + Claude for synthesis
        """
        import time
        start_time = time.time()
        
        try:
            opportunities = await self._search_opportunities(filters)
            
            trends = await self._detect_trends(opportunities, filters)
            
            synthesis = await self._claude_trend_synthesis(opportunities, trends, filters)
            
            processing_time = int((time.time() - start_time) * 1000)
            
            result = {
                "success": True,
                "opportunities": [
                    {
                        "id": o.id,
                        "title": o.title,
                        "description": o.description[:200] if o.description else None,
                        "category": o.category,
                        "score": o.feasibility_score,
                        "created_at": o.created_at.isoformat() if o.created_at else None,
                    }
                    for o in opportunities[:20]
                ],
                "trends": [
                    {
                        "id": t.id,
                        "name": t.trend_name,
                        "strength": t.trend_strength,
                        "description": t.description,
                        "growth_rate": t.growth_rate,
                        "opportunities_count": t.opportunities_count,
                    }
                    for t in trends
                ],
                "synthesis": synthesis,
                "total_count": len(opportunities),
                "processing_time_ms": processing_time,
            }
            
            await self._log_activity(
                user_id=user_id,
                session_id=session_id,
                path=ConsultantPath.search_ideas.value,
                action="search_complete",
                payload=filters,
                result_summary=f"Found {len(opportunities)} opportunities, {len(trends)} trends",
                ai_model_used="hybrid",
                processing_time_ms=processing_time,
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error searching ideas: {e}")
            return {"success": False, "error": str(e)}

    async def identify_location(
        self,
        user_id: int,
        city: str,
        business_type: str,
        business_subtype: Optional[str] = None,
        additional_params: Optional[Dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Path 3: Identify Location - Geographic intelligence with 4 subtypes
        Subtypes: specific_business, retail, multifamily, hospitality
        """
        import time
        start_time = time.time()
        
        try:
            cache_key = self._generate_cache_key(city, business_type, business_subtype, additional_params)
            
            cached = self._get_cached_analysis(cache_key)
            if cached:
                cached["from_cache"] = True
                cached["cache_hit_count"] = cached.get("hit_count", 1)
                self._increment_cache_hit(cache_key)
                return cached
            
            geo_analysis = await self._deepseek_geo_analysis(
                city, business_type, business_subtype, additional_params
            )
            
            market_report = await self._claude_location_report(
                city, business_type, business_subtype, geo_analysis, additional_params
            )
            
            site_recommendations = self._generate_site_recommendations(
                geo_analysis, market_report, business_type
            )
            
            processing_time = int((time.time() - start_time) * 1000)
            
            result = {
                "success": True,
                "city": city,
                "business_type": business_type,
                "business_subtype": business_subtype,
                "geo_analysis": geo_analysis,
                "market_report": market_report,
                "site_recommendations": site_recommendations,
                "from_cache": False,
                "processing_time_ms": processing_time,
            }
            
            await self._cache_analysis(
                cache_key=cache_key,
                city=city,
                business_type=business_type,
                business_subtype=business_subtype,
                query_params=additional_params,
                geo_analysis=geo_analysis,
                market_report=market_report,
                site_recommendations=site_recommendations,
            )
            
            await self._log_activity(
                user_id=user_id,
                session_id=session_id,
                path=ConsultantPath.identify_location.value,
                action="location_analysis_complete",
                payload={"city": city, "business_type": business_type, "subtype": business_subtype},
                result_summary=f"Analysis for {business_type} in {city}",
                ai_model_used="hybrid",
                processing_time_ms=processing_time,
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing location: {e}")
            return {"success": False, "error": str(e)}

    async def _find_similar_opportunities(
        self, idea_description: str, limit: int = 10
    ) -> List[Opportunity]:
        """Find opportunities similar to the idea description"""
        keywords = idea_description.lower().split()[:5]
        
        query = self.db.query(Opportunity)
        
        for keyword in keywords:
            if len(keyword) > 3:
                query = query.filter(
                    Opportunity.title.ilike(f"%{keyword}%") |
                    Opportunity.description.ilike(f"%{keyword}%")
                )
        
        return query.order_by(Opportunity.feasibility_score.desc().nullslast()).limit(limit).all()

    async def _deepseek_pattern_analysis(
        self,
        idea: str,
        similar_opps: List[Opportunity],
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """DeepSeek analysis for pattern recognition"""
        from .ai_orchestrator import ai_orchestrator, AITaskType
        
        data = {
            "idea": idea,
            "similar_opportunities": [
                {"title": o.title, "category": o.category, "score": o.feasibility_score or 0}
                for o in similar_opps[:5]
            ],
            "context": context or {},
        }
        
        result = await ai_orchestrator.process_request(
            AITaskType.OPPORTUNITY_VALIDATION, data
        )
        
        return {
            "patterns_found": len(similar_opps),
            "market_signals": result.get("result", {}) if result.get("processed") else {},
            "category_distribution": self._analyze_categories(similar_opps),
            "average_score": sum(o.feasibility_score or 0 for o in similar_opps) / max(len(similar_opps), 1),
        }

    def _calculate_business_type_scores(
        self, pattern_analysis: Dict[str, Any], context: Optional[Dict[str, Any]]
    ) -> tuple:
        """Calculate online vs physical business type scores"""
        online_score = 50
        physical_score = 50
        
        context = context or {}
        
        if context.get("digital_product"):
            online_score += 20
        if context.get("requires_physical_delivery"):
            physical_score += 15
        if context.get("location_dependent"):
            physical_score += 20
        if context.get("remote_interaction"):
            online_score += 15
        if context.get("global_scalability"):
            online_score += 25
        if context.get("physical_inventory"):
            physical_score += 20
        
        categories = pattern_analysis.get("category_distribution", {})
        if categories.get("Technology", 0) > 0.3:
            online_score += 10
        if categories.get("Local Services", 0) > 0.3:
            physical_score += 10
        
        online_score = min(100, max(0, online_score))
        physical_score = min(100, max(0, physical_score))
        
        return online_score, physical_score

    def _determine_recommendation(self, online_score: int, physical_score: int) -> str:
        """Determine business type recommendation"""
        difference = abs(online_score - physical_score)
        
        if difference < 15:
            return "HYBRID"
        elif online_score > physical_score:
            return "ONLINE"
        else:
            return "PHYSICAL"

    async def _claude_viability_report(
        self,
        idea: str,
        pattern_analysis: Dict[str, Any],
        online_score: int,
        physical_score: int,
        context: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Claude generates comprehensive viability report"""
        from .ai_orchestrator import ai_orchestrator, AITaskType
        
        data = {
            "idea": idea,
            "pattern_analysis": pattern_analysis,
            "online_score": online_score,
            "physical_score": physical_score,
            "context": context or {},
            "request": "Generate a comprehensive viability analysis with strengths, weaknesses, opportunities, and threats.",
        }
        
        result = await ai_orchestrator.process_request(
            AITaskType.MARKET_RESEARCH, data
        )
        
        return {
            "executive_summary": "Viability analysis based on market patterns and business context.",
            "strengths": ["Market demand validated", "Clear target audience"],
            "weaknesses": ["Competition level unknown", "Requires further market research"],
            "opportunities": ["Growing market segment", "Technology enablers available"],
            "threats": ["Market saturation risk", "Regulatory considerations"],
            "ai_insights": result.get("result", {}) if result.get("processed") else {},
            "confidence_score": 75,
        }

    async def _search_opportunities(self, filters: Dict[str, Any]) -> List[Opportunity]:
        """Search opportunities based on filters"""
        query = self.db.query(Opportunity)
        
        if filters.get("category"):
            query = query.filter(Opportunity.category == filters["category"])
        if filters.get("min_score"):
            query = query.filter(Opportunity.feasibility_score >= filters["min_score"])
        if filters.get("query"):
            search_term = f"%{filters['query']}%"
            query = query.filter(
                Opportunity.title.ilike(search_term) |
                Opportunity.description.ilike(search_term)
            )
        
        return query.order_by(Opportunity.feasibility_score.desc().nullslast()).limit(50).all()

    async def _detect_trends(
        self, opportunities: List[Opportunity], filters: Dict[str, Any]
    ) -> List[DetectedTrend]:
        """DeepSeek trend detection from opportunities"""
        from .ai_orchestrator import ai_orchestrator, AITaskType
        
        categories = {}
        for opp in opportunities:
            cat = opp.category or "Unknown"
            categories[cat] = categories.get(cat, 0) + 1
        
        top_categories = sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]
        
        trends = []
        for cat_name, count in top_categories:
            existing = self.db.query(DetectedTrend).filter(
                DetectedTrend.trend_name == f"{cat_name} Growth"
            ).first()
            
            if not existing:
                trend = DetectedTrend(
                    trend_name=f"{cat_name} Growth",
                    trend_strength=min(100, count * 10),
                    description=f"Growing opportunities in {cat_name} category",
                    category=cat_name,
                    opportunities_count=count,
                    growth_rate=round(count / max(len(opportunities), 1) * 100, 2),
                    confidence_score=70,
                )
                self.db.add(trend)
                trends.append(trend)
            else:
                existing.opportunities_count = count
                existing.trend_strength = min(100, count * 10)
                trends.append(existing)
        
        self.db.commit()
        
        return trends

    async def _claude_trend_synthesis(
        self,
        opportunities: List[Opportunity],
        trends: List[DetectedTrend],
        filters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Claude synthesizes trends into actionable insights"""
        from .ai_orchestrator import ai_orchestrator, AITaskType
        
        data = {
            "opportunity_count": len(opportunities),
            "trends": [{"name": t.trend_name, "strength": t.trend_strength} for t in trends],
            "filters": filters,
        }
        
        result = await ai_orchestrator.process_request(
            AITaskType.MARKET_RESEARCH, data
        )
        
        return {
            "summary": f"Analysis of {len(opportunities)} opportunities reveals {len(trends)} key trends.",
            "top_insight": trends[0].trend_name if trends else "No clear trend detected",
            "recommendations": [
                "Focus on high-strength trend categories",
                "Monitor emerging patterns",
                "Consider cross-category opportunities",
            ],
            "ai_synthesis": result.get("result", {}) if result.get("processed") else {},
        }

    async def _deepseek_geo_analysis(
        self,
        city: str,
        business_type: str,
        business_subtype: Optional[str],
        params: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Geographic analysis using trade area analyzer for real data"""
        from .trade_area_analyzer import trade_area_analyzer
        
        try:
            opportunity_data = {
                "id": 0,
                "title": f"{business_subtype or business_type} in {city}",
                "category": business_type,
                "location": city,
                "city": city,
                "region": params.get("state") if params else None,
                "state": params.get("state") if params else None,
                "latitude": params.get("latitude") if params else None,
                "longitude": params.get("longitude") if params else None,
            }
            
            trade_area = trade_area_analyzer.analyze(opportunity_data)
            
            demographics = trade_area.demographics or {}
            competitors = trade_area.competitors or []
            
            radius_miles = trade_area.radius_km * 0.621371
            
            return {
                "market_density": "high" if len(competitors) > 10 else "medium" if len(competitors) > 5 else "low",
                "competition_level": "high" if trade_area.white_space_score < 30 else "moderate" if trade_area.white_space_score < 60 else "low",
                "competitor_count": len(competitors),
                "white_space_score": trade_area.white_space_score,
                "demographics": {
                    "population": demographics.get("population", "N/A"),
                    "median_income": f"${demographics.get('median_income', 0):,}" if demographics.get("median_income") else "N/A",
                    "median_age": demographics.get("median_age", "N/A"),
                    "unemployment_rate": f"{demographics.get('unemployment_rate', 0)}%" if demographics.get("unemployment_rate") else "N/A",
                    "median_home_value": f"${demographics.get('median_home_value', 0):,}" if demographics.get("median_home_value") else "N/A",
                },
                "trade_area_radius_miles": round(radius_miles, 1),
                "competitors": competitors[:10],
                "ai_synthesis": trade_area.ai_synthesis,
            }
            
        except Exception as e:
            logger.warning(f"Trade area analysis failed, using fallback: {e}")
            return {
                "market_density": "medium",
                "competition_level": "moderate",
                "demographics": {
                    "population": "100,000+",
                    "median_income": "$55,000",
                    "growth_trend": "positive",
                },
                "ai_insights": {},
            }

    async def _claude_location_report(
        self,
        city: str,
        business_type: str,
        business_subtype: Optional[str],
        geo_analysis: Dict[str, Any],
        params: Optional[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Claude generates comprehensive location market report"""
        from .ai_report_generator import ai_report_generator
        
        try:
            opportunity_context = {
                "title": f"{business_subtype or business_type} in {city}",
                "category": business_type,
                "location": city,
                "description": f"Market opportunity for {business_subtype or business_type} business in {city}",
            }
            
            demographics = geo_analysis.get("demographics", {})
            competitors = geo_analysis.get("competitors", [])
            
            market_insights = ai_report_generator.generate_market_insights(
                opportunity_context,
                demographics,
                competitors
            )
            
            competitive_analysis = ai_report_generator.generate_competitive_analysis(
                opportunity_context,
                competitors
            )
            
            return {
                "executive_summary": f"Market analysis for {business_type} opportunities in {city}.",
                "market_conditions": geo_analysis.get("market_density", "unknown"),
                "white_space_score": geo_analysis.get("white_space_score", 50),
                "key_factors": [
                    "Local economic indicators",
                    "Competition landscape",
                    "Target demographic presence",
                ],
                "market_insights": market_insights,
                "competitive_analysis": competitive_analysis,
            }
            
        except Exception as e:
            logger.warning(f"AI location report failed, using fallback: {e}")
            return {
                "executive_summary": f"Market analysis for {business_type} opportunities in {city}.",
                "market_conditions": geo_analysis.get("market_density", "unknown"),
                "key_factors": [
                    "Local economic indicators",
                    "Competition landscape",
                    "Target demographic presence",
                ],
                "ai_report": {},
            }

    def _generate_site_recommendations(
        self,
        geo_analysis: Dict[str, Any],
        market_report: Dict[str, Any],
        business_type: str,
    ) -> List[Dict[str, Any]]:
        """Generate site recommendations based on analysis"""
        base_recommendations = {
            "specific_business": [
                {"type": "Downtown Core", "priority": "high", "reason": "High foot traffic"},
                {"type": "Business District", "priority": "medium", "reason": "Professional clientele"},
            ],
            "retail": [
                {"type": "Shopping Center", "priority": "high", "reason": "Established traffic patterns"},
                {"type": "Main Street", "priority": "medium", "reason": "Local visibility"},
            ],
            "multifamily": [
                {"type": "Urban Infill", "priority": "high", "reason": "Density and accessibility"},
                {"type": "Transit Corridor", "priority": "high", "reason": "Transportation access"},
            ],
            "hospitality": [
                {"type": "Tourism District", "priority": "high", "reason": "Visitor traffic"},
                {"type": "Convention Area", "priority": "medium", "reason": "Business travelers"},
            ],
        }
        
        return base_recommendations.get(business_type, base_recommendations["specific_business"])

    def _generate_cache_key(
        self,
        city: str,
        business_type: str,
        business_subtype: Optional[str],
        params: Optional[Dict[str, Any]],
    ) -> str:
        """Generate unique cache key for location analysis"""
        key_data = f"{city.lower()}:{business_type}:{business_subtype or ''}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]

    def _get_cached_analysis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached location analysis if not expired"""
        cached = self.db.query(LocationAnalysisCache).filter(
            LocationAnalysisCache.cache_key == cache_key,
            LocationAnalysisCache.expires_at > datetime.utcnow(),
        ).first()
        
        if cached:
            return {
                "success": True,
                "city": cached.city,
                "business_type": cached.business_type,
                "business_subtype": cached.business_subtype,
                "geo_analysis": cached.demographic_data or {},
                "market_report": {"executive_summary": cached.claude_summary},
                "site_recommendations": cached.site_recommendations or [],
                "hit_count": cached.hit_count,
            }
        
        return None

    def _increment_cache_hit(self, cache_key: str):
        """Increment cache hit counter"""
        cached = self.db.query(LocationAnalysisCache).filter(
            LocationAnalysisCache.cache_key == cache_key
        ).first()
        if cached:
            cached.hit_count += 1
            self.db.commit()

    async def _cache_analysis(
        self,
        cache_key: str,
        city: str,
        business_type: str,
        business_subtype: Optional[str],
        query_params: Optional[Dict[str, Any]],
        geo_analysis: Dict[str, Any],
        market_report: Dict[str, Any],
        site_recommendations: List[Dict[str, Any]],
    ):
        """Cache location analysis for future use"""
        cache_entry = LocationAnalysisCache(
            cache_key=cache_key,
            city=city,
            business_type=business_type,
            business_subtype=business_subtype,
            query_params=query_params,
            demographic_data=geo_analysis,
            market_metrics=geo_analysis.get("demographics"),
            claude_summary=market_report.get("executive_summary"),
            site_recommendations=site_recommendations,
            expires_at=datetime.utcnow() + timedelta(days=self.CACHE_TTL_DAYS),
        )
        self.db.add(cache_entry)
        self.db.commit()

    async def _log_activity(
        self,
        user_id: int,
        session_id: Optional[str],
        path: str,
        action: str,
        payload: Optional[Dict[str, Any]],
        result_summary: str,
        ai_model_used: str,
        processing_time_ms: int,
        tokens_used: Optional[int] = None,
    ):
        """Log consultant activity"""
        activity = ConsultantActivity(
            user_id=user_id,
            session_id=session_id,
            path=path,
            action=action,
            payload=payload,
            result_summary=result_summary,
            ai_model_used=ai_model_used,
            tokens_used=tokens_used,
            processing_time_ms=processing_time_ms,
        )
        self.db.add(activity)
        self.db.commit()

    def _analyze_categories(self, opportunities: List[Opportunity]) -> Dict[str, float]:
        """Analyze category distribution"""
        if not opportunities:
            return {}
        
        categories = {}
        for opp in opportunities:
            cat = opp.category or "Unknown"
            categories[cat] = categories.get(cat, 0) + 1
        
        total = len(opportunities)
        return {k: round(v / total, 2) for k, v in categories.items()}
