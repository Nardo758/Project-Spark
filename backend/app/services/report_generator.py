"""
Report Generator Service

Generates tiered opportunity reports:
- Layer 1: Problem Overview ($15/Pro+) 
- Layer 2: Deep Dive Analysis (Business+)
- Layer 3: Execution Package (Business 5/mo or Enterprise)
"""
import os
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity
from app.models.generated_report import GeneratedReport, ReportType, ReportStatus
from app.models.user import User


class ReportGenerator:
    """Base class for generating opportunity reports."""
    
    TIER_REQUIREMENTS = {
        ReportType.LAYER_1_OVERVIEW: ["pro", "business", "enterprise"],
        ReportType.LAYER_2_DEEP_DIVE: ["business", "enterprise"],
        ReportType.LAYER_3_EXECUTION: ["business", "enterprise"],
    }
    
    TIER_PRICES = {
        ReportType.LAYER_1_OVERVIEW: 1500,
        ReportType.LAYER_2_DEEP_DIVE: None,
        ReportType.LAYER_3_EXECUTION: None,
    }
    
    def __init__(self, db: Session):
        self.db = db
    
    def check_entitlement(self, user: User, report_type: ReportType) -> Dict[str, Any]:
        """Check if user has access to generate this report type."""
        user_tier = getattr(user, 'tier', 'free')
        if hasattr(user_tier, 'value'):
            user_tier = user_tier.value
        user_tier = str(user_tier).lower() if user_tier else 'free'
        
        allowed_tiers = self.TIER_REQUIREMENTS.get(report_type, [])
        
        if user.is_admin:
            return {"allowed": True, "reason": "admin_access"}
        
        if user_tier in allowed_tiers:
            return {"allowed": True, "reason": "tier_access"}
        
        return {
            "allowed": False, 
            "reason": "tier_required",
            "required_tiers": allowed_tiers,
            "user_tier": user_tier,
            "price": self.TIER_PRICES.get(report_type)
        }
    
    def generate_layer1_report(self, opportunity: Opportunity, user: User) -> GeneratedReport:
        """Generate Layer 1: Problem Overview report."""
        start_time = datetime.utcnow()
        
        report = GeneratedReport(
            user_id=user.id,
            opportunity_id=opportunity.id,
            report_type=ReportType.LAYER_1_OVERVIEW,
            status=ReportStatus.GENERATING,
            title=f"Problem Overview: {opportunity.title}",
        )
        self.db.add(report)
        self.db.commit()
        
        content = self._build_layer1_content(opportunity)
        summary = self._build_layer1_summary(opportunity)
        
        report.content = content
        report.summary = summary
        report.status = ReportStatus.COMPLETED
        report.completed_at = datetime.utcnow()
        report.generation_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        report.confidence_score = opportunity.ai_opportunity_score or 75
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def _build_layer1_content(self, opp: Opportunity) -> str:
        """Build Layer 1 report content in HTML format."""
        market_size = opp.ai_market_size_estimate or opp.market_size or "Under Analysis"
        target_audience = opp.ai_target_audience or "General consumers"
        competition = opp.ai_competition_level or "Medium"
        urgency = opp.ai_urgency_level or "Medium"
        score = opp.ai_opportunity_score or opp.severity * 20
        
        problem_statement = opp.ai_problem_statement or opp.description
        pain_points = opp.ai_competitive_advantages or ["Market gap exists", "User pain point validated"]
        risks = opp.ai_key_risks or ["Market timing", "Competition"]
        
        html_content = f"""
<div class="report-layer1">
    <header class="report-header">
        <h1>Problem Overview Report</h1>
        <div class="report-meta">
            <span class="category">{opp.category}</span>
            <span class="date">Generated: {datetime.utcnow().strftime('%B %d, %Y')}</span>
        </div>
    </header>
    
    <section class="executive-summary">
        <h2>Executive Summary</h2>
        <div class="opportunity-title">{opp.title}</div>
        <p>{opp.ai_summary or opp.description[:500] if opp.description else 'Analysis in progress...'}</p>
        <div class="score-badge">
            <span class="score">{score}</span>
            <span class="label">Opportunity Score</span>
        </div>
    </section>
    
    <section class="problem-definition">
        <h2>The Problem</h2>
        <div class="problem-statement">
            <p>{problem_statement}</p>
        </div>
        <div class="pain-metrics">
            <div class="metric">
                <span class="value">{opp.ai_pain_intensity or opp.severity}/10</span>
                <span class="label">Pain Intensity</span>
            </div>
            <div class="metric">
                <span class="value capitalize">{urgency}</span>
                <span class="label">Urgency Level</span>
            </div>
            <div class="metric">
                <span class="value">{opp.validation_count}</span>
                <span class="label">Validations</span>
            </div>
        </div>
    </section>
    
    <section class="market-snapshot">
        <h2>Market Snapshot</h2>
        <div class="market-grid">
            <div class="market-card">
                <span class="label">Market Size</span>
                <span class="value">{market_size}</span>
            </div>
            <div class="market-card">
                <span class="label">Target Audience</span>
                <span class="value">{target_audience}</span>
            </div>
            <div class="market-card">
                <span class="label">Competition</span>
                <span class="value capitalize">{competition}</span>
            </div>
            <div class="market-card">
                <span class="label">Geographic Focus</span>
                <span class="value">{opp.city or opp.region or opp.country or 'National'}</span>
            </div>
        </div>
    </section>
    
    <section class="validation-signals">
        <h2>Validation Signals</h2>
        <ul class="signal-list">
            {''.join(f'<li class="signal-item positive">{point}</li>' for point in pain_points[:5])}
        </ul>
    </section>
    
    <section class="key-risks">
        <h2>Key Risks</h2>
        <ul class="risk-list">
            {''.join(f'<li class="risk-item">{risk}</li>' for risk in risks[:5])}
        </ul>
    </section>
    
    <section class="next-steps">
        <h2>Recommended Next Steps</h2>
        <ol class="steps-list">
            <li>Conduct deeper market validation through customer interviews</li>
            <li>Analyze competitive landscape for positioning opportunities</li>
            <li>Define minimum viable product (MVP) scope</li>
            <li>Upgrade to Layer 2 Deep Dive for comprehensive analysis</li>
        </ol>
    </section>
    
    <footer class="report-footer">
        <p>This report was generated by OppGrid's AI-powered analysis engine.</p>
        <p>For comprehensive market analysis and demographic insights, upgrade to Layer 2 Deep Dive.</p>
    </footer>
</div>
"""
        return html_content
    
    def _build_layer1_summary(self, opp: Opportunity) -> str:
        """Build Layer 1 report summary."""
        return f"Problem Overview for '{opp.title}' - Score: {opp.ai_opportunity_score or opp.severity * 20}/100. {opp.ai_summary[:200] if opp.ai_summary else opp.description[:200] if opp.description else 'Analysis pending'}..."
    
    def generate_layer2_report(self, opportunity: Opportunity, user: User, demographics: Optional[Dict] = None) -> GeneratedReport:
        """Generate Layer 2: Deep Dive Analysis report."""
        start_time = datetime.utcnow()
        
        report = GeneratedReport(
            user_id=user.id,
            opportunity_id=opportunity.id,
            report_type=ReportType.LAYER_2_DEEP_DIVE,
            status=ReportStatus.GENERATING,
            title=f"Deep Dive Analysis: {opportunity.title}",
        )
        self.db.add(report)
        self.db.commit()
        
        content = self._build_layer2_content(opportunity, demographics)
        summary = f"Deep Dive Analysis for '{opportunity.title}' including TAM/SAM/SOM, demographic insights, and competitive landscape."
        
        report.content = content
        report.summary = summary
        report.status = ReportStatus.COMPLETED
        report.completed_at = datetime.utcnow()
        report.generation_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        report.confidence_score = opportunity.ai_opportunity_score or 80
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def _build_layer2_content(self, opp: Opportunity, demographics: Optional[Dict] = None) -> str:
        """Build Layer 2 report content with demographics."""
        market_size = opp.ai_market_size_estimate or opp.market_size or "$1B+"
        
        pop_display = "--"
        income_display = "--"
        education_display = "--"
        households_display = "--"
        
        if demographics:
            if demographics.get('population'):
                pop = demographics['population']
                pop_display = f"{pop/1000000:.1f}M" if pop >= 1000000 else f"{pop/1000:.0f}K"
            if demographics.get('median_income'):
                income_display = f"${demographics['median_income']/1000:.0f}K"
            if demographics.get('bachelors_degree_holders') and demographics.get('population'):
                education_display = f"{(demographics['bachelors_degree_holders'] / demographics['population'] * 100):.0f}%"
            if demographics.get('total_households'):
                hh = demographics['total_households']
                households_display = f"{hh/1000:.0f}K" if hh >= 1000 else str(hh)
        
        html_content = f"""
<div class="report-layer2">
    <header class="report-header">
        <h1>Deep Dive Analysis Report</h1>
        <div class="report-meta">
            <span class="tier-badge">BUSINESS</span>
            <span class="category">{opp.category}</span>
            <span class="date">Generated: {datetime.utcnow().strftime('%B %d, %Y')}</span>
        </div>
    </header>
    
    <section class="tam-sam-som">
        <h2>Market Size Analysis (TAM/SAM/SOM)</h2>
        <div class="market-funnel">
            <div class="funnel-level tam">
                <span class="label">Total Addressable Market (TAM)</span>
                <span class="value">{market_size}</span>
                <p>Total global market for this problem space</p>
            </div>
            <div class="funnel-level sam">
                <span class="label">Serviceable Available Market (SAM)</span>
                <span class="value">~$500M</span>
                <p>Market reachable with current business model</p>
            </div>
            <div class="funnel-level som">
                <span class="label">Serviceable Obtainable Market (SOM)</span>
                <span class="value">~$50M</span>
                <p>Realistic Year 1-3 capture target</p>
            </div>
        </div>
    </section>
    
    <section class="demographic-deep-dive">
        <h2>Demographic Deep Dive</h2>
        <p class="source-note">Data source: US Census Bureau ACS 5-Year Estimates</p>
        <div class="demo-grid">
            <div class="demo-card">
                <span class="value">{pop_display}</span>
                <span class="label">Population</span>
            </div>
            <div class="demo-card">
                <span class="value">{income_display}</span>
                <span class="label">Median Income</span>
            </div>
            <div class="demo-card">
                <span class="value">{education_display}</span>
                <span class="label">College Educated</span>
            </div>
            <div class="demo-card">
                <span class="value">{households_display}</span>
                <span class="label">Households</span>
            </div>
        </div>
    </section>
    
    <section class="competitive-landscape">
        <h2>Competitive Landscape</h2>
        <div class="competition-level">
            <span class="level capitalize">{opp.ai_competition_level or 'Medium'}</span>
            <span class="description">Overall competition intensity</span>
        </div>
        <div class="advantages">
            <h3>Key Competitive Advantages</h3>
            <ul>
                {''.join(f'<li>{adv}</li>' for adv in (opp.ai_competitive_advantages or ["Market gap identified", "First-mover potential", "Underserved segment"])[:5])}
            </ul>
        </div>
    </section>
    
    <section class="geographic-analysis">
        <h2>Geographic Analysis</h2>
        <div class="geo-focus">
            <div class="primary-market">
                <span class="label">Primary Market</span>
                <span class="value">{opp.city or opp.region or 'National'}</span>
            </div>
            <div class="scope">
                <span class="label">Geographic Scope</span>
                <span class="value capitalize">{opp.geographic_scope or 'Regional'}</span>
            </div>
        </div>
    </section>
    
    <section class="business-models">
        <h2>Recommended Business Models</h2>
        <div class="model-cards">
            {''.join(f'<div class="model-card"><h4>{model}</h4><p>Viable approach based on market analysis</p></div>' for model in (opp.ai_business_model_suggestions or ["SaaS Platform", "Marketplace", "Subscription Service"])[:4])}
        </div>
    </section>
    
    <footer class="report-footer">
        <p>This comprehensive analysis was generated by OppGrid's AI engine with Census data integration.</p>
        <p>For full execution package with business plan, upgrade to Layer 3.</p>
    </footer>
</div>
"""
        return html_content
    
    def generate_layer3_report(self, opportunity: Opportunity, user: User, demographics: Optional[Dict] = None) -> GeneratedReport:
        """Generate Layer 3: Execution Package report."""
        start_time = datetime.utcnow()
        
        report = GeneratedReport(
            user_id=user.id,
            opportunity_id=opportunity.id,
            report_type=ReportType.LAYER_3_EXECUTION,
            status=ReportStatus.GENERATING,
            title=f"Execution Package: {opportunity.title}",
        )
        self.db.add(report)
        self.db.commit()
        
        content = self._build_layer3_content(opportunity, demographics)
        summary = f"Complete Execution Package for '{opportunity.title}' including business plan, go-to-market strategy, and 90-day roadmap."
        
        report.content = content
        report.summary = summary
        report.status = ReportStatus.COMPLETED
        report.completed_at = datetime.utcnow()
        report.generation_time_ms = int((datetime.utcnow() - start_time).total_seconds() * 1000)
        report.confidence_score = opportunity.ai_opportunity_score or 85
        
        self.db.commit()
        self.db.refresh(report)
        
        return report
    
    def _build_layer3_content(self, opp: Opportunity, demographics: Optional[Dict] = None) -> str:
        """Build Layer 3 Execution Package content."""
        html_content = f"""
<div class="report-layer3">
    <header class="report-header">
        <h1>Execution Package</h1>
        <div class="report-meta">
            <span class="tier-badge">ENTERPRISE</span>
            <span class="category">{opp.category}</span>
            <span class="date">Generated: {datetime.utcnow().strftime('%B %d, %Y')}</span>
        </div>
    </header>
    
    <section class="business-plan-summary">
        <h2>Business Plan Summary</h2>
        <div class="plan-overview">
            <h3>Vision Statement</h3>
            <p>To become the leading solution for {opp.ai_target_audience or 'target customers'} by addressing {opp.title.lower()}.</p>
            
            <h3>Value Proposition</h3>
            <p>{opp.ai_problem_statement or opp.description}</p>
            
            <h3>Revenue Model</h3>
            <ul>
                {''.join(f'<li>{model}</li>' for model in (opp.ai_business_model_suggestions or ["Subscription", "Transaction fees", "Premium features"])[:3])}
            </ul>
        </div>
    </section>
    
    <section class="go-to-market">
        <h2>Go-to-Market Strategy</h2>
        <div class="gtm-phases">
            <div class="phase">
                <h4>Phase 1: Foundation (Days 1-30)</h4>
                <ul>
                    <li>Finalize MVP feature set</li>
                    <li>Establish brand identity</li>
                    <li>Set up initial marketing channels</li>
                    <li>Begin beta user recruitment</li>
                </ul>
            </div>
            <div class="phase">
                <h4>Phase 2: Launch (Days 31-60)</h4>
                <ul>
                    <li>Soft launch with beta users</li>
                    <li>Gather feedback and iterate</li>
                    <li>Begin content marketing</li>
                    <li>Establish partnerships</li>
                </ul>
            </div>
            <div class="phase">
                <h4>Phase 3: Growth (Days 61-90)</h4>
                <ul>
                    <li>Public launch</li>
                    <li>Scale marketing efforts</li>
                    <li>Optimize conversion funnels</li>
                    <li>Expand to adjacent markets</li>
                </ul>
            </div>
        </div>
    </section>
    
    <section class="financial-projections">
        <h2>Financial Projections (3-Year)</h2>
        <table class="financials-table">
            <thead>
                <tr>
                    <th>Metric</th>
                    <th>Year 1</th>
                    <th>Year 2</th>
                    <th>Year 3</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Revenue</td>
                    <td>$250K</td>
                    <td>$1.2M</td>
                    <td>$3.5M</td>
                </tr>
                <tr>
                    <td>Customers</td>
                    <td>500</td>
                    <td>2,500</td>
                    <td>8,000</td>
                </tr>
                <tr>
                    <td>Gross Margin</td>
                    <td>60%</td>
                    <td>70%</td>
                    <td>75%</td>
                </tr>
                <tr>
                    <td>EBITDA</td>
                    <td>-$150K</td>
                    <td>$100K</td>
                    <td>$700K</td>
                </tr>
            </tbody>
        </table>
    </section>
    
    <section class="roadmap-90day">
        <h2>90-Day Action Roadmap</h2>
        <div class="roadmap-timeline">
            <div class="week week-1-4">
                <h4>Weeks 1-4: Research & Validate</h4>
                <ul>
                    <li>Conduct 20+ customer interviews</li>
                    <li>Analyze competitive landscape</li>
                    <li>Define MVP requirements</li>
                    <li>Select technology stack</li>
                </ul>
            </div>
            <div class="week week-5-8">
                <h4>Weeks 5-8: Build & Test</h4>
                <ul>
                    <li>Develop core MVP features</li>
                    <li>Create landing page</li>
                    <li>Begin beta testing</li>
                    <li>Iterate based on feedback</li>
                </ul>
            </div>
            <div class="week week-9-12">
                <h4>Weeks 9-12: Launch & Learn</h4>
                <ul>
                    <li>Soft launch to early adopters</li>
                    <li>Implement analytics</li>
                    <li>Optimize onboarding</li>
                    <li>Plan scaling strategy</li>
                </ul>
            </div>
        </div>
    </section>
    
    <section class="risk-mitigation">
        <h2>Risk Mitigation Plan</h2>
        <ul class="risk-items">
            {''.join(f'<li><strong>{risk}</strong><br/>Mitigation: Monitor market trends and adapt strategy accordingly.</li>' for risk in (opp.ai_key_risks or ["Market timing", "Competition", "Funding"])[:5])}
        </ul>
    </section>
    
    <footer class="report-footer">
        <p>This comprehensive execution package was generated by OppGrid's AI-powered business intelligence engine.</p>
        <p>For personalized strategy sessions, connect with our expert network.</p>
    </footer>
</div>
"""
        return html_content


report_generator = ReportGenerator
