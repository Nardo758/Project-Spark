"""
AI Report Generator Service

Uses Anthropic Claude to generate intelligent, opportunity-specific report content.
Leverages Replit AI Integrations for Anthropic access (no API key required).
"""
import os
import logging
from typing import Dict, Any, Optional, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception

logger = logging.getLogger(__name__)

AI_INTEGRATIONS_ANTHROPIC_API_KEY = os.environ.get("AI_INTEGRATIONS_ANTHROPIC_API_KEY")
AI_INTEGRATIONS_ANTHROPIC_BASE_URL = os.environ.get("AI_INTEGRATIONS_ANTHROPIC_BASE_URL")


def is_rate_limit_error(exception: BaseException) -> bool:
    """Check if the exception is a rate limit or quota violation error."""
    error_msg = str(exception)
    return (
        "429" in error_msg
        or "RATELIMIT_EXCEEDED" in error_msg
        or "quota" in error_msg.lower()
        or "rate limit" in error_msg.lower()
        or (hasattr(exception, "status_code") and exception.status_code == 429)
    )


def get_anthropic_client():
    """Get configured Anthropic client using Replit AI Integrations."""
    from anthropic import Anthropic
    
    if not AI_INTEGRATIONS_ANTHROPIC_API_KEY or not AI_INTEGRATIONS_ANTHROPIC_BASE_URL:
        logger.warning("Anthropic AI integration not configured")
        return None
    
    return Anthropic(
        api_key=AI_INTEGRATIONS_ANTHROPIC_API_KEY,
        base_url=AI_INTEGRATIONS_ANTHROPIC_BASE_URL
    )


class AIReportGenerator:
    """Generates AI-powered report content using Claude."""
    
    MODEL = "claude-sonnet-4-5"
    MAX_TOKENS = 8192
    
    def __init__(self):
        self.client = get_anthropic_client()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception(is_rate_limit_error),
        reraise=True
    )
    def _generate(self, system_prompt: str, user_prompt: str) -> str:
        """Generate content using Claude with retry logic."""
        if not self.client:
            return ""
        
        try:
            message = self.client.messages.create(
                model=self.MODEL,
                max_tokens=self.MAX_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}]
            )
            return message.content[0].text if message.content else ""
        except Exception as e:
            logger.error(f"Claude generation error: {e}")
            raise
    
    def generate_executive_summary(self, opportunity: Dict[str, Any]) -> str:
        """Generate an executive summary for Layer 1 report."""
        system = """You are a business analyst generating executive summaries for market opportunities.
Write a compelling, data-driven executive summary that:
- Opens with the core opportunity in one sentence
- Highlights key market signals and validation
- Summarizes target market and size
- Outlines recommended next steps
Keep it concise (2-3 paragraphs max). Use professional business language."""
        
        prompt = f"""Generate an executive summary for this opportunity:

Title: {opportunity.get('title', 'Unknown')}
Category: {opportunity.get('category', 'Unknown')}
Location: {opportunity.get('city', '')}, {opportunity.get('region', '')}
Description: {opportunity.get('description', '')}
Market Size Estimate: {opportunity.get('market_size', 'Under analysis')}
Opportunity Score: {opportunity.get('score', 'N/A')}/100
Target Audience: {opportunity.get('target_audience', '')}
Competition Level: {opportunity.get('competition_level', '')}
"""
        return self._generate(system, prompt)
    
    def generate_problem_analysis(self, opportunity: Dict[str, Any]) -> str:
        """Generate problem analysis using Lean Canvas framework for Layer 1."""
        system = """You are a startup strategist analyzing business problems using the Lean Canvas framework.
Structure your analysis with these sections:
1. **Problem Statement** - The core pain point being addressed
2. **Existing Alternatives** - How people currently solve this problem
3. **Customer Segments** - Who experiences this problem most acutely
4. **Unique Value Proposition** - Why this opportunity is compelling
5. **Solution Direction** - High-level approach to solving the problem

Use bullet points and be specific. Reference real market dynamics."""
        
        prompt = f"""Analyze this market opportunity using Lean Canvas problem framing:

Title: {opportunity.get('title', 'Unknown')}
Category: {opportunity.get('category', 'Unknown')}  
Location: {opportunity.get('city', '')}, {opportunity.get('region', '')}
Description: {opportunity.get('description', '')}
Signals/Evidence: {opportunity.get('signals', '')}
Target Audience: {opportunity.get('target_audience', '')}
"""
        return self._generate(system, prompt)
    
    def generate_market_insights(
        self, 
        opportunity: Dict[str, Any], 
        demographics: Optional[Dict[str, Any]] = None,
        competitors: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Generate market insights for Layer 2 report with demographics and competitive data."""
        system = """You are a market research analyst providing deep-dive market insights.
Structure your analysis with:
1. **Market Overview** - Size, growth trajectory, key dynamics
2. **Demographic Fit** - How the local demographics align with the opportunity
3. **Competitive Landscape** - Key players, market gaps, positioning opportunities
4. **Trade Area Analysis** - Geographic considerations and optimal service areas
5. **Key Success Factors** - What it takes to win in this market

Use data points where available. Be specific about local market conditions."""
        
        demo_info = ""
        if demographics:
            demo_info = f"""
Demographics Data:
- Population: {demographics.get('population', 'N/A')}
- Median Income: ${demographics.get('median_income', 'N/A')}
- Median Age: {demographics.get('median_age', 'N/A')}
- Total Households: {demographics.get('total_households', 'N/A')}
- Median Rent: ${demographics.get('median_rent', 'N/A')}
"""
        
        comp_info = ""
        if competitors:
            comp_info = "Competitor Data:\n"
            for i, comp in enumerate(competitors[:10], 1):
                comp_info += f"- {comp.get('name', 'Unknown')}: Rating {comp.get('rating', 'N/A')}, {comp.get('reviews', 0)} reviews\n"
        
        prompt = f"""Provide market insights for this opportunity:

Title: {opportunity.get('title', 'Unknown')}
Category: {opportunity.get('category', 'Unknown')}
Location: {opportunity.get('city', '')}, {opportunity.get('region', '')}
Description: {opportunity.get('description', '')}
Market Size: {opportunity.get('market_size', 'Under analysis')}
{demo_info}
{comp_info}
"""
        return self._generate(system, prompt)
    
    def generate_competitive_analysis(
        self, 
        opportunity: Dict[str, Any],
        competitors: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Generate Porter's Five Forces competitive analysis for Layer 2."""
        system = """You are a strategy consultant analyzing competitive dynamics using Porter's Five Forces.
Structure your analysis with:
1. **Threat of New Entrants** - Barriers to entry, capital requirements
2. **Bargaining Power of Suppliers** - Key suppliers, switching costs
3. **Bargaining Power of Buyers** - Customer concentration, price sensitivity
4. **Threat of Substitutes** - Alternative solutions, technology disruption
5. **Competitive Rivalry** - Current players, market saturation, differentiation

Conclude with strategic positioning recommendations."""
        
        comp_info = ""
        if competitors:
            comp_info = "Known Competitors:\n"
            for comp in competitors[:10]:
                comp_info += f"- {comp.get('name', 'Unknown')}: {comp.get('rating', 'N/A')} stars, {comp.get('reviews', 0)} reviews, {comp.get('address', '')}\n"
        
        prompt = f"""Perform Porter's Five Forces analysis for:

Title: {opportunity.get('title', 'Unknown')}
Category: {opportunity.get('category', 'Unknown')}
Location: {opportunity.get('city', '')}, {opportunity.get('region', '')}
Description: {opportunity.get('description', '')}
{comp_info}
"""
        return self._generate(system, prompt)
    
    def generate_tam_sam_som(
        self, 
        opportunity: Dict[str, Any],
        demographics: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate TAM/SAM/SOM market sizing analysis for Layer 2."""
        system = """You are a market sizing analyst calculating Total Addressable Market (TAM), 
Serviceable Addressable Market (SAM), and Serviceable Obtainable Market (SOM).

Structure your analysis:
1. **TAM (Total Addressable Market)** - Global/national market for this category
2. **SAM (Serviceable Addressable Market)** - Regional/local market you could serve
3. **SOM (Serviceable Obtainable Market)** - Realistic market share in 3-5 years

Include methodology, assumptions, and dollar figures. Be realistic but optimistic."""
        
        demo_info = ""
        if demographics:
            demo_info = f"""
Local Demographics:
- Population: {demographics.get('population', 'N/A')}
- Median Income: ${demographics.get('median_income', 'N/A')}
- Total Households: {demographics.get('total_households', 'N/A')}
"""
        
        prompt = f"""Calculate TAM/SAM/SOM for:

Title: {opportunity.get('title', 'Unknown')}
Category: {opportunity.get('category', 'Unknown')}
Location: {opportunity.get('city', '')}, {opportunity.get('region', '')}
Initial Market Size Estimate: {opportunity.get('market_size', 'Under analysis')}
Target Audience: {opportunity.get('target_audience', '')}
{demo_info}
"""
        return self._generate(system, prompt)
    
    def generate_strategic_recommendations(
        self, 
        opportunity: Dict[str, Any],
        demographics: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate strategic recommendations for Layer 3 execution package."""
        system = """You are a business strategy consultant providing actionable recommendations.
Structure your recommendations:
1. **Business Model Recommendation** - Best model for this opportunity
2. **Go-to-Market Strategy** - Phase 1 (0-90 days), Phase 2 (90-180 days), Phase 3 (180-365 days)
3. **Key Partnerships** - Who to partner with and why
4. **Resource Requirements** - Initial investment, team, technology
5. **Risk Mitigation** - Top 3 risks and how to address them
6. **Success Metrics** - KPIs to track in first year

Be specific and actionable. Focus on practical next steps."""
        
        prompt = f"""Provide strategic recommendations for launching:

Title: {opportunity.get('title', 'Unknown')}
Category: {opportunity.get('category', 'Unknown')}
Location: {opportunity.get('city', '')}, {opportunity.get('region', '')}
Description: {opportunity.get('description', '')}
Market Size: {opportunity.get('market_size', 'Under analysis')}
Target Audience: {opportunity.get('target_audience', '')}
Business Model Suggestions: {opportunity.get('business_models', '')}
"""
        return self._generate(system, prompt)
    
    def generate_business_plan(self, opportunity: Dict[str, Any]) -> str:
        """Generate a comprehensive business plan for Layer 3."""
        system = """You are a business plan writer creating investor-ready business plans.
Structure the business plan:
1. **Executive Summary**
2. **Company Description** - Mission, vision, values
3. **Market Analysis** - Industry overview, target market, competition
4. **Products/Services** - What you offer, unique value proposition
5. **Marketing & Sales Strategy** - Customer acquisition, channels, pricing
6. **Operations Plan** - Key activities, resources, partners
7. **Management Team** - Required roles and expertise
8. **Financial Projections** - Revenue model, cost structure, funding needs
9. **Milestones & Timeline** - Key milestones for first 12 months

Make it professional and compelling for investors."""
        
        prompt = f"""Write a business plan for:

Title: {opportunity.get('title', 'Unknown')}
Category: {opportunity.get('category', 'Unknown')}
Location: {opportunity.get('city', '')}, {opportunity.get('region', '')}
Description: {opportunity.get('description', '')}
Market Size: {opportunity.get('market_size', 'Under analysis')}
Target Audience: {opportunity.get('target_audience', '')}
Business Model Ideas: {opportunity.get('business_models', '')}
"""
        return self._generate(system, prompt)
    
    def generate_financial_projections(self, opportunity: Dict[str, Any]) -> str:
        """Generate financial projections for Layer 3."""
        system = """You are a financial analyst creating 3-year financial projections.
Structure your projections:
1. **Revenue Model** - How money is made, pricing tiers
2. **Year 1 Projections** - Monthly breakdown of first year
3. **Year 2-3 Projections** - Quarterly projections
4. **Cost Structure** - Fixed costs, variable costs, unit economics
5. **Break-Even Analysis** - When profitability is achieved
6. **Funding Requirements** - Initial capital needed, use of funds
7. **Key Assumptions** - List all assumptions behind numbers

Include specific dollar figures and realistic growth rates."""
        
        prompt = f"""Create 3-year financial projections for:

Title: {opportunity.get('title', 'Unknown')}
Category: {opportunity.get('category', 'Unknown')}
Location: {opportunity.get('city', '')}, {opportunity.get('region', '')}
Market Size Estimate: {opportunity.get('market_size', 'Under analysis')}
Business Model: {opportunity.get('business_models', '')}
"""
        return self._generate(system, prompt)
    
    def generate_feasibility_study(self, opportunity: Dict[str, Any]) -> str:
        """Generate a feasibility study for Consultant Studio."""
        system = """You are a feasibility analyst evaluating business viability.
Structure your feasibility study:
1. **Project Overview** - What is being evaluated
2. **Technical Feasibility** - Can it be built/delivered?
3. **Market Feasibility** - Is there demand?
4. **Financial Feasibility** - Is it economically viable?
5. **Operational Feasibility** - Can it be executed?
6. **Legal/Regulatory Considerations** - Any compliance requirements?
7. **Recommendation** - Go/No-Go with justification

Use a scoring system (1-10) for each dimension. Be objective and balanced."""
        
        prompt = f"""Conduct a feasibility study for:

Title: {opportunity.get('title', 'Unknown')}
Category: {opportunity.get('category', 'Unknown')}
Location: {opportunity.get('city', '')}, {opportunity.get('region', '')}
Description: {opportunity.get('description', '')}
Market Size: {opportunity.get('market_size', 'Under analysis')}
Competition Level: {opportunity.get('competition_level', '')}
"""
        return self._generate(system, prompt)
    
    def generate_pitch_deck_content(self, opportunity: Dict[str, Any]) -> str:
        """Generate pitch deck slide content for Quick Actions."""
        system = """You are a pitch deck expert creating investor-ready presentation content.
Structure content for these slides:
1. **Title Slide** - Company name, tagline, presenter
2. **Problem** - The pain point you're solving
3. **Solution** - Your unique approach
4. **Market Size** - TAM/SAM/SOM
5. **Business Model** - How you make money
6. **Traction** - Progress, milestones, validation
7. **Competition** - Competitive landscape and your advantage
8. **Team** - Who's building this
9. **Ask** - What you're raising and use of funds
10. **Vision** - Where this goes in 5 years

For each slide, provide: Title, Key Points (3-5 bullets), and Speaker Notes."""
        
        prompt = f"""Create pitch deck content for:

Title: {opportunity.get('title', 'Unknown')}
Category: {opportunity.get('category', 'Unknown')}
Description: {opportunity.get('description', '')}
Market Size: {opportunity.get('market_size', 'Under analysis')}
Target Audience: {opportunity.get('target_audience', '')}
Business Models: {opportunity.get('business_models', '')}
"""
        return self._generate(system, prompt)


ai_report_generator = AIReportGenerator()
