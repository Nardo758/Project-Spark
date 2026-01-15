"""
AI Co-Founder API Router
Provides chat functionality with stage-aware AI assistant.
Supports BYOK (Bring Your Own Key) for users with their own Claude API keys.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional

from app.db.database import get_db
from app.models.user import User
from app.models.workspace import UserWorkspace, WorkspaceChatMessage
from app.models.opportunity import Opportunity
from app.models.affiliate_tool import AffiliateTool
from app.core.dependencies import get_current_user
from app.services.ai_cofounder import (
    chat_with_cofounder,
    chat_with_cofounder_enhanced,
    get_tool_recommendations,
    get_business_formation_guide,
    web_search,
    TOOL_RECOMMENDATIONS,
    BUSINESS_FORMATION_GUIDE
)
from app.services.encryption_service import encryption_service

router = APIRouter(prefix="/ai-cofounder", tags=["AI Co-Founder"])


class ChatRequest(BaseModel):
    message: str
    stage: Optional[str] = None

    @property
    def sanitized_message(self) -> str:
        return self.message.strip()[:4000] if self.message else ""


class ChatMessage(BaseModel):
    id: int
    role: str
    content: str
    created_at: str

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    response: str
    chat_history: List[ChatMessage]
    key_source: Optional[str] = None
    inline_cards: Optional[dict] = None


class ToolRecommendation(BaseModel):
    name: str
    url: str
    description: str
    price: str
    best_for: str


class ToolCategory(BaseModel):
    category: str
    tools: List[ToolRecommendation]


class BusinessFormationType(BaseModel):
    name: str
    best_for: str
    pros: List[str]
    cons: List[str]
    cost: str
    steps: List[str]


@router.post("/workspace/{workspace_id}/chat", response_model=ChatResponse)
async def chat_with_ai_cofounder(
    workspace_id: int,
    request: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Chat with the AI Co-Founder for a specific workspace."""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.id == workspace_id,
        UserWorkspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    message = request.sanitized_message
    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    opportunity = db.query(Opportunity).filter(
        Opportunity.id == workspace.opportunity_id
    ).first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    existing_messages = db.query(WorkspaceChatMessage).filter(
        WorkspaceChatMessage.workspace_id == workspace_id
    ).order_by(WorkspaceChatMessage.created_at).all()
    
    chat_history = [
        {"role": msg.role, "content": msg.content}
        for msg in existing_messages
    ]
    
    valid_stages = ['researching', 'validating', 'planning', 'building', 'launched', 'paused', 'archived']
    current_stage = workspace.status.value if workspace.status else "researching"
    
    if request.stage and request.stage in valid_stages and request.stage != current_stage:
        from app.models.workspace import WorkspaceStatus
        workspace.status = WorkspaceStatus(request.stage)
        current_stage = request.stage
    
    opportunity_dict = {
        "title": opportunity.title,
        "description": opportunity.description,
        "category": opportunity.category,
        "ai_problem_statement": opportunity.ai_problem_statement,
        "ai_market_size_estimate": opportunity.ai_market_size_estimate,
        "ai_competition_level": opportunity.ai_competition_level,
        "ai_target_audience": opportunity.ai_target_audience,
    }
    
    workspace_dict = {
        "status": current_stage,
        "progress_percent": workspace.progress_percent or 0,
    }
    
    user_api_key = None
    if current_user.encrypted_claude_api_key:
        user_api_key = encryption_service.decrypt(current_user.encrypted_claude_api_key)
    
    db_tools = db.query(AffiliateTool).filter(AffiliateTool.is_active == True).all()
    tools_list = [
        {
            "id": t.id,
            "name": t.name,
            "category": t.category,
            "description": t.description,
            "url": t.affiliate_url or t.base_url,
            "price": t.price_display,
            "best_for": t.best_for
        }
        for t in db_tools
    ] if db_tools else None
    
    try:
        result = await chat_with_cofounder_enhanced(
            message=message,
            stage=current_stage,
            opportunity=opportunity_dict,
            workspace=workspace_dict,
            chat_history=chat_history,
            enable_web_search=True,
            user_api_key=user_api_key,
            db_tools=tools_list
        )
        ai_response = result["response"]
        key_source = result.get("key_source", "platform")
        inline_cards = result.get("inline_cards")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
    
    user_msg = WorkspaceChatMessage(
        workspace_id=workspace_id,
        role="user",
        content=message
    )
    db.add(user_msg)
    
    assistant_msg = WorkspaceChatMessage(
        workspace_id=workspace_id,
        role="assistant",
        content=ai_response
    )
    db.add(assistant_msg)
    
    db.commit()
    db.refresh(user_msg)
    db.refresh(assistant_msg)
    
    all_messages = db.query(WorkspaceChatMessage).filter(
        WorkspaceChatMessage.workspace_id == workspace_id
    ).order_by(WorkspaceChatMessage.created_at).all()
    
    return ChatResponse(
        response=ai_response,
        chat_history=[
            ChatMessage(
                id=msg.id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at.isoformat()
            )
            for msg in all_messages
        ],
        key_source=key_source,
        inline_cards=inline_cards
    )


@router.get("/workspace/{workspace_id}/chat-history", response_model=List[ChatMessage])
async def get_chat_history(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get chat history for a workspace."""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.id == workspace_id,
        UserWorkspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    messages = db.query(WorkspaceChatMessage).filter(
        WorkspaceChatMessage.workspace_id == workspace_id
    ).order_by(WorkspaceChatMessage.created_at).all()
    
    return [
        ChatMessage(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at.isoformat()
        )
        for msg in messages
    ]


@router.delete("/workspace/{workspace_id}/chat-history")
async def clear_chat_history(
    workspace_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Clear chat history for a workspace."""
    workspace = db.query(UserWorkspace).filter(
        UserWorkspace.id == workspace_id,
        UserWorkspace.user_id == current_user.id
    ).first()
    
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    
    db.query(WorkspaceChatMessage).filter(
        WorkspaceChatMessage.workspace_id == workspace_id
    ).delete()
    
    db.commit()
    
    return {"message": "Chat history cleared"}


@router.get("/tools")
async def get_all_tool_recommendations():
    """Get all tool recommendations organized by category."""
    return get_tool_recommendations()


@router.get("/tools/{category}")
async def get_tools_by_category(category: str):
    """Get tool recommendations for a specific category."""
    valid_categories = list(TOOL_RECOMMENDATIONS.keys())
    if category not in valid_categories:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid category. Valid options: {', '.join(valid_categories)}"
        )
    return get_tool_recommendations(category)


@router.get("/business-formation")
async def get_all_business_formation_guides():
    """Get all business formation guides."""
    return get_business_formation_guide()


@router.get("/business-formation/{entity_type}")
async def get_business_formation_by_type(entity_type: str):
    """Get business formation guide for a specific entity type."""
    valid_types = list(BUSINESS_FORMATION_GUIDE.keys())
    if entity_type not in valid_types:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid entity type. Valid options: {', '.join(valid_types)}"
        )
    return get_business_formation_guide(entity_type)


class WebSearchRequest(BaseModel):
    query: str
    num_results: int = 5


@router.post("/web-search")
async def perform_web_search(
    request: WebSearchRequest,
    current_user: User = Depends(get_current_user)
):
    """Perform a web search and return results."""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    results = web_search(request.query.strip(), request.num_results)
    
    if results.get("error"):
        raise HTTPException(status_code=503, detail=results["error"])
    
    return results
