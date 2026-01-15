"""Affiliate Tools API router for managing and serving tool recommendations."""
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.database import get_db
from app.models.user import User
from app.models.affiliate_tool import AffiliateTool, AffiliateClick
from app.core.dependencies import get_current_user, get_current_user_optional

router = APIRouter(prefix="/affiliate-tools", tags=["Affiliate Tools"])


class ToolResponse(BaseModel):
    id: int
    name: str
    category: str
    description: str | None
    url: str
    price_display: str | None
    best_for: str | None
    logo_url: str | None
    
    class Config:
        from_attributes = True


class ToolCreateRequest(BaseModel):
    name: str
    category: str
    description: str | None = None
    base_url: str
    affiliate_url: str | None = None
    affiliate_code: str | None = None
    commission_rate: float | None = None
    commission_type: str | None = None
    price_display: str | None = None
    best_for: str | None = None
    logo_url: str | None = None
    priority: int = 0
    is_active: bool = True


class ToolUpdateRequest(BaseModel):
    name: str | None = None
    category: str | None = None
    description: str | None = None
    base_url: str | None = None
    affiliate_url: str | None = None
    affiliate_code: str | None = None
    commission_rate: float | None = None
    commission_type: str | None = None
    price_display: str | None = None
    best_for: str | None = None
    logo_url: str | None = None
    priority: int | None = None
    is_active: bool | None = None


class AdminToolResponse(BaseModel):
    id: int
    name: str
    category: str
    description: str | None
    base_url: str
    affiliate_url: str | None
    affiliate_code: str | None
    commission_rate: float | None
    commission_type: str | None
    price_display: str | None
    best_for: str | None
    logo_url: str | None
    is_active: bool
    priority: int
    click_count: int
    conversion_count: int
    created_at: datetime | None
    
    class Config:
        from_attributes = True


class ClickTrackRequest(BaseModel):
    tool_id: int
    opportunity_id: int | None = None
    workspace_id: int | None = None
    source: str | None = None


@router.get("/categories")
async def get_tool_categories(db: Session = Depends(get_db)) -> List[str]:
    """Get all available tool categories."""
    categories = db.query(AffiliateTool.category).filter(
        AffiliateTool.is_active == True
    ).distinct().all()
    return [c[0] for c in categories]


@router.get("/", response_model=List[ToolResponse])
async def get_tools(
    category: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = Query(default=20, le=50),
    db: Session = Depends(get_db)
):
    """Get active tools, optionally filtered by category or search term."""
    query = db.query(AffiliateTool).filter(AffiliateTool.is_active == True)
    
    if category:
        query = query.filter(AffiliateTool.category == category)
    
    if search:
        search_term = f"%{search}%"
        query = query.filter(or_(
            AffiliateTool.name.ilike(search_term),
            AffiliateTool.description.ilike(search_term),
            AffiliateTool.best_for.ilike(search_term)
        ))
    
    tools = query.order_by(AffiliateTool.priority.desc(), AffiliateTool.name).limit(limit).all()
    
    return [
        ToolResponse(
            id=t.id,
            name=t.name,
            category=t.category,
            description=t.description,
            url=t.affiliate_url or t.base_url,
            price_display=t.price_display,
            best_for=t.best_for,
            logo_url=t.logo_url
        )
        for t in tools
    ]


@router.get("/for-opportunity")
async def get_tools_for_opportunity(
    opportunity_category: str,
    stage: str = "building",
    limit: int = Query(default=10, le=20),
    db: Session = Depends(get_db)
) -> dict:
    """Get recommended tools based on opportunity category and stage."""
    stage_categories = {
        "researching": ["marketing", "project"],
        "validating": ["marketing", "design", "nocode"],
        "planning": ["project", "financial", "nocode"],
        "building": ["development", "nocode", "design", "talent"],
        "launched": ["financial", "marketing", "project"]
    }
    
    relevant_categories = stage_categories.get(stage, ["development", "nocode"])
    
    tools_by_category = {}
    for cat in relevant_categories:
        tools = db.query(AffiliateTool).filter(
            AffiliateTool.is_active == True,
            AffiliateTool.category == cat
        ).order_by(AffiliateTool.priority.desc()).limit(3).all()
        
        if tools:
            tools_by_category[cat] = [
                ToolResponse(
                    id=t.id,
                    name=t.name,
                    category=t.category,
                    description=t.description,
                    url=t.affiliate_url or t.base_url,
                    price_display=t.price_display,
                    best_for=t.best_for,
                    logo_url=t.logo_url
                )
                for t in tools
            ]
    
    return {
        "stage": stage,
        "opportunity_category": opportunity_category,
        "recommendations": tools_by_category
    }


@router.post("/track-click")
async def track_click(
    request: ClickTrackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional)
):
    """Track an affiliate link click."""
    tool = db.query(AffiliateTool).filter(AffiliateTool.id == request.tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    tool.click_count = (tool.click_count or 0) + 1
    
    click = AffiliateClick(
        tool_id=request.tool_id,
        user_id=current_user.id if current_user else None,
        opportunity_id=request.opportunity_id,
        workspace_id=request.workspace_id,
        source=request.source or "workhub"
    )
    db.add(click)
    db.commit()
    
    return {"success": True, "redirect_url": tool.affiliate_url or tool.base_url}


@router.get("/admin/all", response_model=List[AdminToolResponse])
async def admin_get_all_tools(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin: Get all tools including inactive ones."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    tools = db.query(AffiliateTool).order_by(
        AffiliateTool.category, 
        AffiliateTool.priority.desc()
    ).all()
    
    return tools


@router.post("/admin/create", response_model=AdminToolResponse)
async def admin_create_tool(
    request: ToolCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin: Create a new affiliate tool."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    tool = AffiliateTool(
        name=request.name,
        category=request.category,
        description=request.description,
        base_url=request.base_url,
        affiliate_url=request.affiliate_url,
        affiliate_code=request.affiliate_code,
        commission_rate=request.commission_rate,
        commission_type=request.commission_type,
        price_display=request.price_display,
        best_for=request.best_for,
        logo_url=request.logo_url,
        priority=request.priority,
        is_active=request.is_active
    )
    db.add(tool)
    db.commit()
    db.refresh(tool)
    
    return tool


@router.patch("/admin/{tool_id}", response_model=AdminToolResponse)
async def admin_update_tool(
    tool_id: int,
    request: ToolUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin: Update an affiliate tool."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    tool = db.query(AffiliateTool).filter(AffiliateTool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    update_data = request.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(tool, key, value)
    
    db.commit()
    db.refresh(tool)
    
    return tool


@router.delete("/admin/{tool_id}")
async def admin_delete_tool(
    tool_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin: Delete an affiliate tool."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    tool = db.query(AffiliateTool).filter(AffiliateTool.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    db.delete(tool)
    db.commit()
    
    return {"success": True}


@router.post("/admin/seed-defaults")
async def admin_seed_default_tools(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Admin: Seed default tools from the hardcoded list."""
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    default_tools = {
        "design": [
            {"name": "Figma", "base_url": "https://figma.com", "description": "Collaborative design tool for UI/UX", "price_display": "Free - $15/mo", "best_for": "Professional design, team collaboration"},
            {"name": "Canva", "base_url": "https://canva.com", "description": "Easy graphic design for non-designers", "price_display": "Free - $13/mo", "best_for": "Marketing materials, social media"},
            {"name": "Framer", "base_url": "https://framer.com", "description": "Design to production websites", "price_display": "Free - $20/mo", "best_for": "Landing pages, marketing sites"},
        ],
        "development": [
            {"name": "Replit", "base_url": "https://replit.com", "description": "AI-powered development platform", "price_display": "Free - $25/mo", "best_for": "Full-stack apps, rapid prototyping"},
            {"name": "Vercel", "base_url": "https://vercel.com", "description": "Frontend deployment platform", "price_display": "Free - $20/mo", "best_for": "Next.js, React apps"},
            {"name": "Supabase", "base_url": "https://supabase.com", "description": "Open source Firebase alternative", "price_display": "Free - $25/mo", "best_for": "Database, auth, real-time"},
            {"name": "Firebase", "base_url": "https://firebase.google.com", "description": "Google's app development platform", "price_display": "Pay as you go", "best_for": "Mobile apps, real-time features"},
        ],
        "talent": [
            {"name": "Upwork", "base_url": "https://upwork.com", "description": "Large freelancer marketplace", "price_display": "Commission-based", "best_for": "Budget-friendly, variety of skills"},
            {"name": "Toptal", "base_url": "https://toptal.com", "description": "Top 3% of freelancers", "price_display": "Premium rates", "best_for": "High-quality, vetted talent"},
            {"name": "Contra", "base_url": "https://contra.com", "description": "Commission-free freelancing", "price_display": "No fees", "best_for": "Direct relationships, portfolios"},
            {"name": "Fiverr", "base_url": "https://fiverr.com", "description": "Quick, affordable gigs", "price_display": "Starting at $5", "best_for": "Small tasks, quick turnaround"},
        ],
        "nocode": [
            {"name": "Bubble", "base_url": "https://bubble.io", "description": "Full-featured no-code web apps", "price_display": "Free - $32/mo", "best_for": "Complex web applications"},
            {"name": "Webflow", "base_url": "https://webflow.com", "description": "Visual website builder", "price_display": "Free - $24/mo", "best_for": "Marketing sites, CMS"},
            {"name": "Zapier", "base_url": "https://zapier.com", "description": "Automate workflows between apps", "price_display": "Free - $20/mo", "best_for": "Integrations, automation"},
            {"name": "Airtable", "base_url": "https://airtable.com", "description": "Spreadsheet-database hybrid", "price_display": "Free - $20/mo", "best_for": "Data management, simple apps"},
        ],
        "marketing": [
            {"name": "Mailchimp", "base_url": "https://mailchimp.com", "description": "Email marketing platform", "price_display": "Free - $13/mo", "best_for": "Email campaigns, newsletters"},
            {"name": "Buffer", "base_url": "https://buffer.com", "description": "Social media scheduling", "price_display": "Free - $6/mo", "best_for": "Social media management"},
            {"name": "SEMrush", "base_url": "https://semrush.com", "description": "SEO and marketing toolkit", "price_display": "$120/mo+", "best_for": "SEO, competitor analysis"},
        ],
        "project": [
            {"name": "Notion", "base_url": "https://notion.so", "description": "All-in-one workspace", "price_display": "Free - $10/mo", "best_for": "Docs, wikis, project management"},
            {"name": "Linear", "base_url": "https://linear.app", "description": "Modern issue tracking", "price_display": "Free - $8/mo", "best_for": "Software development teams"},
            {"name": "Trello", "base_url": "https://trello.com", "description": "Visual kanban boards", "price_display": "Free - $10/mo", "best_for": "Simple task management"},
        ],
        "financial": [
            {"name": "QuickBooks", "base_url": "https://quickbooks.intuit.com", "description": "Small business accounting", "price_display": "$30/mo+", "best_for": "Full accounting, invoicing"},
            {"name": "Wave", "base_url": "https://waveapps.com", "description": "Free accounting software", "price_display": "Free", "best_for": "Freelancers, small businesses"},
            {"name": "Stripe", "base_url": "https://stripe.com", "description": "Payment processing", "price_display": "2.9% + 30¢/txn", "best_for": "Online payments, subscriptions"},
            {"name": "Mercury", "base_url": "https://mercury.com", "description": "Startup banking", "price_display": "Free", "best_for": "Business bank account, startups"},
        ],
    }
    
    added = 0
    for category, tools in default_tools.items():
        for idx, tool_data in enumerate(tools):
            existing = db.query(AffiliateTool).filter(
                AffiliateTool.name == tool_data["name"],
                AffiliateTool.category == category
            ).first()
            
            if not existing:
                tool = AffiliateTool(
                    category=category,
                    priority=len(tools) - idx,
                    is_active=True,
                    **tool_data
                )
                db.add(tool)
                added += 1
    
    db.commit()
    
    return {"success": True, "tools_added": added}
