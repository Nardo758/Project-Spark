from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
import os

from anthropic import Anthropic

from app.db.database import get_db
from app.models.opportunity import Opportunity

router = APIRouter()

client = Anthropic(
    base_url=os.environ.get("AI_INTEGRATIONS_ANTHROPIC_BASE_URL"),
    api_key=os.environ.get("AI_INTEGRATIONS_ANTHROPIC_API_KEY")
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    opportunity_id: Optional[int] = None
    conversation_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    response: str
    suggestions: Optional[List[str]] = None

def get_opportunity_context(db: Session, opportunity_id: int) -> str:
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        return ""
    
    return f"""
OPPORTUNITY DETAILS:
- Title: {opportunity.title}
- Description: {opportunity.description}
- Category: {opportunity.category}
- Severity: {opportunity.severity}/5
- Market Size: {opportunity.market_size or 'Unknown'}
- Validation Count: {opportunity.validation_count}
- Growth Rate: {opportunity.growth_rate}%
- Geographic Scope: {opportunity.geographic_scope or 'Not specified'}
- Country: {opportunity.country or 'Not specified'}
- Region: {opportunity.region or 'Not specified'}
- City: {opportunity.city or 'Not specified'}
- Completion Status: {opportunity.completion_status or 'unsolved'}
"""

SYSTEM_PROMPT = """You are an AI research assistant for Katalyst, a platform that helps entrepreneurs discover validated business opportunities based on real consumer problems.

Your role is to help users analyze opportunities and provide actionable insights on:
- Market analysis and sizing
- Competitive landscape
- Go-to-market strategy
- Pricing recommendations
- MVP feature prioritization
- Geographic expansion strategy
- Risk assessment
- Business model validation

Always base your responses on the opportunity data provided. Be specific, actionable, and back up recommendations with reasoning. Use bullet points and clear formatting for readability.

When discussing geographic markets, consider:
- US National market: $8.4B, high competition, state-by-state regulations
- Southwest Region: $1.2B, +52% growth, best for launch due to business-friendly regulations
- Canada: $2.1B CAD, low competition but complex provincial regulations
- UK: £1.8B, high competition, requires trade certifications
- Australia: $1.4B AUD, low competition, emerging opportunity

Keep responses concise but thorough. If you don't have enough data, say so and suggest what additional research might help."""

@router.post("/chat", response_model=ChatResponse)
async def chat_with_ai(request: ChatRequest, db: Session = Depends(get_db)):
    try:
        messages = []
        
        for msg in request.conversation_history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        opportunity_context = ""
        if request.opportunity_id:
            opportunity_context = get_opportunity_context(db, request.opportunity_id)
        
        user_content = request.message
        if opportunity_context and not request.conversation_history:
            user_content = f"{opportunity_context}\n\nUser Question: {request.message}"
        
        messages.append({
            "role": "user",
            "content": user_content
        })
        
        response = client.messages.create(
            model="claude-sonnet-4-5-20250514",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=messages
        )
        
        ai_response = response.content[0].text
        
        suggestions = []
        if len(messages) <= 2:
            suggestions = [
                "What are the biggest risks with this business model?",
                "Where should I launch this geographically?",
                "How would you recommend pricing the product?",
                "What should the MVP feature set look like?"
            ]
        
        return ChatResponse(
            response=ai_response,
            suggestions=suggestions
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI chat error: {str(e)}"
        )

@router.get("/suggestions/{opportunity_id}")
async def get_initial_suggestions(opportunity_id: int, db: Session = Depends(get_db)):
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return {
        "greeting": f"Hi! I'm your AI research assistant. I can help you explore the '{opportunity.title}' opportunity in depth.",
        "suggestions": [
            "What are the biggest risks with this business model?",
            "Where should I launch this geographically?",
            "How would you recommend pricing the product?",
            "What should the MVP feature set look like?",
            "Who are the main competitors?",
            "What's the ideal customer profile?"
        ]
    }
