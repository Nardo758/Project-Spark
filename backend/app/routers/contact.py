"""
Contact form endpoints for enterprise leads and general inquiries.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from typing import Optional
import os
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


class EnterpriseContactRequest(BaseModel):
    name: str
    email: EmailStr
    company: str
    teamSize: str
    message: Optional[str] = None
    source: Optional[str] = "pricing"


class ContactResponse(BaseModel):
    success: bool
    message: str


@router.post("/enterprise", response_model=ContactResponse)
async def submit_enterprise_lead(req: EnterpriseContactRequest):
    """
    Submit an enterprise contact request.
    Sends notification email to sales team.
    """
    try:
        import resend
        
        resend_api_key = os.environ.get("RESEND_API_KEY")
        if not resend_api_key:
            logger.warning("RESEND_API_KEY not configured, skipping email notification")
        else:
            resend.api_key = resend_api_key
            
            resend.Emails.send({
                "from": "OppGrid <noreply@oppgrid.com>",
                "to": ["sales@oppgrid.com"],
                "subject": f"New Enterprise Lead: {req.company}",
                "html": f"""
                <h2>New Enterprise Lead</h2>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Name:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;">{req.name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Email:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;">{req.email}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Company:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;">{req.company}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Team Size:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;">{req.teamSize}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;"><strong>Source:</strong></td>
                        <td style="padding: 8px; border-bottom: 1px solid #eee;">{req.source}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; vertical-align: top;"><strong>Message:</strong></td>
                        <td style="padding: 8px;">{req.message or '(no message provided)'}</td>
                    </tr>
                </table>
                """,
            })
            logger.info(f"Enterprise lead email sent for {req.company}")

        return ContactResponse(
            success=True,
            message="Your request has been submitted. Our team will reach out soon."
        )

    except Exception as e:
        logger.error(f"Failed to send enterprise lead email: {e}")
        logger.error(f"Lead data (for manual follow-up): name={req.name}, email={req.email}, company={req.company}, teamSize={req.teamSize}, source={req.source}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit your request. Please try again or email us directly at sales@oppgrid.com"
        )
