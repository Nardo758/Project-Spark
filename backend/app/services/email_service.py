"""
Email Service

Service for sending transactional emails using Resend integration.
"""

import os
import httpx
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


async def get_resend_credentials() -> Dict[str, str]:
    """Fetch Resend API credentials from Replit connector."""
    hostname = os.getenv("REPLIT_CONNECTORS_HOSTNAME")
    repl_identity = os.getenv("REPL_IDENTITY")
    web_repl_renewal = os.getenv("WEB_REPL_RENEWAL")
    
    if repl_identity:
        x_replit_token = f"repl {repl_identity}"
    elif web_repl_renewal:
        x_replit_token = f"depl {web_repl_renewal}"
    else:
        raise ValueError("X_REPLIT_TOKEN not found for repl/depl")
    
    if not hostname:
        raise ValueError("REPLIT_CONNECTORS_HOSTNAME not set")
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"https://{hostname}/api/v2/connection?include_secrets=true&connector_names=resend",
            headers={
                "Accept": "application/json",
                "X_REPLIT_TOKEN": x_replit_token,
            }
        )
        resp.raise_for_status()
        data = resp.json()
        
    items = data.get("items", [])
    if not items:
        raise ValueError("Resend not connected")
    
    settings = items[0].get("settings", {})
    api_key = settings.get("api_key")
    from_email = settings.get("from_email", "noreply@oppgrid.com")
    
    if not api_key:
        raise ValueError("Resend API key not found")
    
    return {"api_key": api_key, "from_email": from_email}


async def send_email(
    to: str,
    subject: str,
    html_content: str,
    text_content: Optional[str] = None,
    from_email: Optional[str] = None,
    reply_to: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Send an email via Resend API.
    
    Args:
        to: Recipient email address
        subject: Email subject line
        html_content: HTML body of the email
        text_content: Plain text version (optional)
        from_email: Sender email (uses default if not provided)
        reply_to: Reply-to address (optional)
    
    Returns:
        dict with id and status from Resend API
    """
    try:
        creds = await get_resend_credentials()
        api_key = creds["api_key"]
        sender = from_email or creds["from_email"]
        
        payload = {
            "from": sender,
            "to": [to] if isinstance(to, str) else to,
            "subject": subject,
            "html": html_content,
        }
        
        if text_content:
            payload["text"] = text_content
        if reply_to:
            payload["reply_to"] = reply_to
        
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
            resp.raise_for_status()
            result = resp.json()
            logger.info(f"Email sent successfully to {to}: {result.get('id')}")
            return {"success": True, "id": result.get("id")}
            
    except Exception as e:
        logger.error(f"Failed to send email to {to}: {str(e)}")
        return {"success": False, "error": str(e)}


async def send_welcome_email(to: str, name: str) -> Dict[str, Any]:
    """Send welcome email to new users."""
    subject = "Welcome to OppGrid - Your AI-Powered Opportunity Intelligence Platform"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #1c1917; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
            .header {{ text-align: center; margin-bottom: 30px; }}
            .logo {{ font-size: 24px; font-weight: 700; color: #1c1917; }}
            .content {{ background: #f5f5f4; padding: 30px; border-radius: 12px; }}
            .btn {{ display: inline-block; background: #1c1917; color: white; padding: 12px 24px; text-decoration: none; border-radius: 8px; font-weight: 600; }}
            .footer {{ text-align: center; margin-top: 30px; color: #78716c; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="logo">OppGrid</div>
            </div>
            <div class="content">
                <h2>Welcome, {name}!</h2>
                <p>Thank you for joining OppGrid. We're excited to help you discover, validate, and act on business opportunities.</p>
                <p>Here's what you can do:</p>
                <ul>
                    <li><strong>Discover</strong> - Browse AI-curated market opportunities</li>
                    <li><strong>Validate</strong> - Test your business ideas with AI analysis</li>
                    <li><strong>Build</strong> - Generate reports, business plans, and pitch decks</li>
                </ul>
                <p style="text-align: center; margin-top: 30px;">
                    <a href="https://oppgrid.com/dashboard" class="btn">Get Started</a>
                </p>
            </div>
            <div class="footer">
                <p>OppGrid - AI-Powered Opportunity Intelligence</p>
            </div>
        </div>
    </body>
    </html>
    """
    return await send_email(to=to, subject=subject, html_content=html_content)


async def send_lead_nurture_email(
    to: str, 
    name: str, 
    step: int,
    opportunity_title: Optional[str] = None
) -> Dict[str, Any]:
    """Send lead nurturing sequence email based on step."""
    
    sequences = {
        1: {
            "subject": "Discover Your Next Big Opportunity",
            "content": f"""
                <h2>Hi {name},</h2>
                <p>Did you know that successful entrepreneurs spend 70% less time searching for opportunities when they use AI-powered tools?</p>
                <p>OppGrid analyzes thousands of market signals daily to surface the best opportunities for you.</p>
                <p><a href="https://oppgrid.com/discover" style="color: #1c1917; font-weight: 600;">Start Discovering →</a></p>
            """
        },
        2: {
            "subject": "Validate Your Ideas Before You Build",
            "content": f"""
                <h2>Hi {name},</h2>
                <p>The #1 reason startups fail? Building something nobody wants.</p>
                <p>Our AI Idea Engine validates your concepts against real market data, giving you confidence before you invest time and money.</p>
                <p><a href="https://oppgrid.com/idea-engine" style="color: #1c1917; font-weight: 600;">Validate Your Idea →</a></p>
            """
        },
        3: {
            "subject": "Ready to Take the Next Step?",
            "content": f"""
                <h2>Hi {name},</h2>
                <p>You've been exploring opportunities on OppGrid. Ready to go deeper?</p>
                <p>Our Pro plan gives you unlimited access to validated opportunities, detailed market reports, and AI-powered business planning tools.</p>
                <p><a href="https://oppgrid.com/pricing" style="color: #1c1917; font-weight: 600;">See Plans →</a></p>
            """
        }
    }
    
    if step not in sequences:
        return {"success": False, "error": f"Invalid sequence step: {step}"}
    
    seq = sequences[step]
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #1c1917; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
            .content {{ background: #f5f5f4; padding: 30px; border-radius: 12px; }}
            .footer {{ text-align: center; margin-top: 30px; color: #78716c; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                {seq['content']}
            </div>
            <div class="footer">
                <p>OppGrid - AI-Powered Opportunity Intelligence</p>
                <p><a href="https://oppgrid.com/unsubscribe" style="color: #78716c;">Unsubscribe</a></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return await send_email(to=to, subject=seq["subject"], html_content=html_content)


async def send_lead_status_update_email(
    to: str,
    name: str,
    old_status: str,
    new_status: str
) -> Dict[str, Any]:
    """Send notification when lead status changes."""
    subject = f"Your OppGrid Application Status Update"
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: 'Inter', Arial, sans-serif; line-height: 1.6; color: #1c1917; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 40px 20px; }}
            .content {{ background: #f5f5f4; padding: 30px; border-radius: 12px; }}
            .status {{ display: inline-block; padding: 4px 12px; border-radius: 20px; font-weight: 600; font-size: 14px; }}
            .status-qualified {{ background: #dcfce7; color: #16a34a; }}
            .status-nurturing {{ background: #dbeafe; color: #2563eb; }}
            .footer {{ text-align: center; margin-top: 30px; color: #78716c; font-size: 14px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="content">
                <h2>Hi {name},</h2>
                <p>Good news! Your status has been updated.</p>
                <p>New Status: <span class="status status-{new_status}">{new_status.upper()}</span></p>
                <p>We'll be in touch soon with more personalized recommendations based on your interests.</p>
            </div>
            <div class="footer">
                <p>OppGrid - AI-Powered Opportunity Intelligence</p>
            </div>
        </div>
    </body>
    </html>
    """
    return await send_email(to=to, subject=subject, html_content=html_content)
