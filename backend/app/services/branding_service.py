"""
White-Label Branding Service - January 2026

Provides branding configuration for Business Track teams.
Injects team branding into generated reports.
"""

import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.models.team import Team, TeamMember
from app.models.user import User
from app.models.subscription import SubscriptionTier

logger = logging.getLogger(__name__)

BUSINESS_TIERS = [SubscriptionTier.TEAM, SubscriptionTier.BUSINESS, SubscriptionTier.ENTERPRISE]


def is_whitelabel_eligible(user: User) -> bool:
    """Check if user is on a tier that supports white-label reports."""
    if not user.subscription:
        return False
    return user.subscription.tier in BUSINESS_TIERS


def get_user_team_branding(user: User, db: Session) -> Optional[Dict[str, Any]]:
    """
    Get team branding for a user if they are eligible for white-label reports.
    
    Returns None if:
    - User is not on a Business Track tier
    - User is not part of a team
    - Team has no branding configured
    """
    if not is_whitelabel_eligible(user):
        return None
    
    membership = db.query(TeamMember).filter(
        TeamMember.user_id == user.id,
        TeamMember.is_active == True
    ).first()
    
    if not membership:
        return None
    
    team = membership.team
    
    has_branding = team.logo_url or team.company_name or team.primary_color
    if not has_branding:
        return None
    
    return {
        "team_id": team.id,
        "team_name": team.name,
        "logo_url": team.logo_url,
        "company_name": team.company_name or team.name,
        "primary_color": team.primary_color or "#6366f1",
        "website_url": team.website_url,
    }


def inject_branding_into_report(html_content: str, branding: Dict[str, Any]) -> str:
    """
    Inject team branding into HTML report content.
    
    Adds:
    - Custom logo header
    - Company name
    - Brand color styling
    - Footer with company info
    """
    if not branding:
        return html_content
    
    logo_url = branding.get("logo_url", "")
    company_name = branding.get("company_name", "")
    primary_color = branding.get("primary_color", "#6366f1")
    website_url = branding.get("website_url", "")
    
    branding_css = f"""
    <style>
        :root {{
            --brand-primary: {primary_color};
            --brand-primary-dark: {_darken_color(primary_color)};
        }}
        .report-container {{ border-top: 4px solid var(--brand-primary); }}
        .branded-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 20px;
            background: linear-gradient(135deg, var(--brand-primary) 0%, var(--brand-primary-dark) 100%);
            color: white;
            margin-bottom: 24px;
            border-radius: 8px 8px 0 0;
        }}
        .branded-header .logo-container {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .branded-header .logo {{
            height: 40px;
            max-width: 160px;
            object-fit: contain;
        }}
        .branded-header .company-name {{
            font-size: 1.25rem;
            font-weight: 600;
        }}
        .branded-header .report-badge {{
            background: rgba(255,255,255,0.2);
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .branded-footer {{
            margin-top: 40px;
            padding: 20px;
            background: #f8fafc;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            color: #64748b;
            font-size: 0.875rem;
        }}
        .branded-footer a {{
            color: var(--brand-primary);
            text-decoration: none;
        }}
        .branded-footer a:hover {{
            text-decoration: underline;
        }}
        h2, h3, .section-title {{
            color: var(--brand-primary) !important;
        }}
        .btn-primary, .action-button {{
            background: var(--brand-primary) !important;
            border-color: var(--brand-primary) !important;
        }}
    </style>
    """
    
    logo_html = ""
    if logo_url:
        logo_html = f'<img src="{logo_url}" alt="{company_name}" class="logo" />'
    
    branded_header = f"""
    <div class="branded-header">
        <div class="logo-container">
            {logo_html}
            <span class="company-name">{company_name}</span>
        </div>
        <span class="report-badge">Business Intelligence Report</span>
    </div>
    """
    
    footer_link = ""
    if website_url:
        footer_link = f' | <a href="{website_url}" target="_blank">{website_url}</a>'
    
    branded_footer = f"""
    <div class="branded-footer">
        <p>Prepared by <strong>{company_name}</strong>{footer_link}</p>
        <p style="font-size: 0.75rem; margin-top: 8px; color: #94a3b8;">
            This report was generated using proprietary business intelligence tools.
        </p>
    </div>
    """
    
    if '<div class="report-container">' in html_content:
        html_content = html_content.replace(
            '<div class="report-container">',
            f'{branding_css}<div class="report-container">{branded_header}'
        )
    else:
        html_content = f'{branding_css}{branded_header}{html_content}'
    
    if '</div>' in html_content:
        last_div_pos = html_content.rfind('</div>')
        html_content = html_content[:last_div_pos] + branded_footer + html_content[last_div_pos:]
    else:
        html_content += branded_footer
    
    return html_content


def _darken_color(hex_color: str) -> str:
    """Darken a hex color by 20%."""
    try:
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = max(0, int(r * 0.8))
        g = max(0, int(g * 0.8))
        b = max(0, int(b * 0.8))
        
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return "#4f46e5"


def get_report_branding_preview(team: Team) -> str:
    """Generate a preview of the branded report header."""
    branding = {
        "logo_url": team.logo_url,
        "company_name": team.company_name or team.name,
        "primary_color": team.primary_color or "#6366f1",
        "website_url": team.website_url,
    }
    
    sample_content = """
    <div class="report-container">
        <h2>Sample Report Preview</h2>
        <p>This is how your branded reports will appear to clients.</p>
        <div style="padding: 20px; background: #f8fafc; border-radius: 8px; margin: 20px 0;">
            <h3>Key Insights</h3>
            <ul>
                <li>Market Size: $2.5B potential</li>
                <li>Competition: Medium</li>
                <li>Opportunity Score: 85/100</li>
            </ul>
        </div>
    </div>
    """
    
    return inject_branding_into_report(sample_content, branding)
