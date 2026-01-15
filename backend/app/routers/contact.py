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


class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    company: Optional[str] = None
    subject: str = "general"
    message: str


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


SUBJECT_LABELS = {
    "general": "General Inquiry",
    "sales": "Sales & Enterprise",
    "support": "Technical Support",
    "partnership": "Partnership Opportunity",
    "press": "Press & Media"
}


@router.post("", response_model=ContactResponse)
async def submit_contact_form(req: ContactRequest):
    """
    Submit a general contact form inquiry.
    Sends notification email to the appropriate team.
    """
    try:
        import resend
        
        resend_api_key = os.environ.get("RESEND_API_KEY")
        subject_label = SUBJECT_LABELS.get(req.subject, "General Inquiry")
        
        if not resend_api_key:
            logger.warning("RESEND_API_KEY not configured, skipping email notification")
        else:
            resend.api_key = resend_api_key
            
            to_email = "hello@oppgrid.com"
            if req.subject == "sales":
                to_email = "sales@oppgrid.com"
            elif req.subject == "support":
                to_email = "support@oppgrid.com"
            elif req.subject == "press":
                to_email = "press@oppgrid.com"
            
            resend.Emails.send({
                "from": "OppGrid Contact <noreply@oppgrid.com>",
                "to": [to_email],
                "reply_to": req.email,
                "subject": f"[{subject_label}] Contact from {req.name}",
                "html": f"""
                <h2>New Contact Form Submission</h2>
                <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #eee; width: 120px;"><strong>Name:</strong></td>
                        <td style="padding: 12px; border-bottom: 1px solid #eee;">{req.name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #eee;"><strong>Email:</strong></td>
                        <td style="padding: 12px; border-bottom: 1px solid #eee;"><a href="mailto:{req.email}">{req.email}</a></td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #eee;"><strong>Company:</strong></td>
                        <td style="padding: 12px; border-bottom: 1px solid #eee;">{req.company or '(not provided)'}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; border-bottom: 1px solid #eee;"><strong>Subject:</strong></td>
                        <td style="padding: 12px; border-bottom: 1px solid #eee;">{subject_label}</td>
                    </tr>
                    <tr>
                        <td style="padding: 12px; vertical-align: top;"><strong>Message:</strong></td>
                        <td style="padding: 12px; white-space: pre-wrap;">{req.message}</td>
                    </tr>
                </table>
                <p style="margin-top: 20px; color: #666; font-size: 12px;">
                    Reply directly to this email to respond to {req.name}.
                </p>
                """,
            })
            logger.info(f"Contact form email sent from {req.email}")

        return ContactResponse(
            success=True,
            message="Thank you for your message. We'll get back to you within 1-2 business days."
        )

    except Exception as e:
        logger.error(f"Failed to send contact form email: {e}")
        logger.error(f"Contact data (for manual follow-up): name={req.name}, email={req.email}, subject={req.subject}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send your message. Please try again or email us directly at hello@oppgrid.com"
        )


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
