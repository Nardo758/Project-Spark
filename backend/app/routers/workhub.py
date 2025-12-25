"""
Workhub API Router
Manages collections, tags, and saved opportunities for the Workhub feature.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.models.user import User
from app.models.workspace import Collection, Tag, SavedOpportunity, SavedOpportunityTag
from app.models.opportunity import Opportunity
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/workhub", tags=["Workhub"])


class CollectionCreate(BaseModel):
    name: str
    description: Optional[str] = None
    color: Optional[str] = "#667eea"
    icon: Optional[str] = "folder"


class CollectionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None


class CollectionResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    color: str
    icon: str
    is_default: bool
    sort_order: int
    opportunity_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class TagCreate(BaseModel):
    name: str
    color: Optional[str] = "#10b981"


class TagResponse(BaseModel):
    id: int
    name: str
    color: str
    created_at: datetime

    class Config:
        from_attributes = True


class SaveOpportunityRequest(BaseModel):
    opportunity_id: int
    collection_id: Optional[int] = None
    notes: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class UpdateSavedOpportunityRequest(BaseModel):
    collection_id: Optional[int] = None
    notes: Optional[str] = None
    lifecycle_state: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class OpportunityBrief(BaseModel):
    id: int
    title: str
    category: str
    severity: int
    market_size: Optional[str]
    validation_count: int

    class Config:
        from_attributes = True


class SavedOpportunityResponse(BaseModel):
    id: int
    opportunity_id: int
    collection_id: Optional[int]
    notes: Optional[str]
    lifecycle_state: str
    created_at: datetime
    updated_at: datetime
    opportunity: OpportunityBrief
    tags: List[TagResponse]

    class Config:
        from_attributes = True


@router.get("/collections", response_model=List[CollectionResponse])
async def get_collections(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all collections for the current user."""
    collections = db.query(Collection).filter(
        Collection.user_id == current_user.id
    ).order_by(Collection.sort_order, Collection.name).all()
    
    result = []
    for col in collections:
        count = db.query(SavedOpportunity).filter(
            SavedOpportunity.collection_id == col.id
        ).count()
        result.append(CollectionResponse(
            id=col.id,
            name=col.name,
            description=col.description,
            color=col.color,
            icon=col.icon,
            is_default=col.is_default,
            sort_order=col.sort_order,
            opportunity_count=count,
            created_at=col.created_at
        ))
    
    return result


@router.post("/collections", response_model=CollectionResponse)
async def create_collection(
    data: CollectionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new collection."""
    existing = db.query(Collection).filter(
        Collection.user_id == current_user.id,
        Collection.name == data.name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Collection with this name already exists")
    
    collection = Collection(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        color=data.color or "#667eea",
        icon=data.icon or "folder"
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    return CollectionResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        color=collection.color,
        icon=collection.icon,
        is_default=collection.is_default,
        sort_order=collection.sort_order,
        opportunity_count=0,
        created_at=collection.created_at
    )


@router.patch("/collections/{collection_id}", response_model=CollectionResponse)
async def update_collection(
    collection_id: int,
    data: CollectionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a collection."""
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    if data.name is not None:
        collection.name = data.name
    if data.description is not None:
        collection.description = data.description
    if data.color is not None:
        collection.color = data.color
    if data.icon is not None:
        collection.icon = data.icon
    
    db.commit()
    db.refresh(collection)
    
    count = db.query(SavedOpportunity).filter(
        SavedOpportunity.collection_id == collection.id
    ).count()
    
    return CollectionResponse(
        id=collection.id,
        name=collection.name,
        description=collection.description,
        color=collection.color,
        icon=collection.icon,
        is_default=collection.is_default,
        sort_order=collection.sort_order,
        opportunity_count=count,
        created_at=collection.created_at
    )


@router.delete("/collections/{collection_id}")
async def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a collection."""
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.user_id == current_user.id
    ).first()
    
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")
    
    if collection.is_default:
        raise HTTPException(status_code=400, detail="Cannot delete default collection")
    
    db.delete(collection)
    db.commit()
    
    return {"deleted": True}


@router.get("/tags", response_model=List[TagResponse])
async def get_tags(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all tags for the current user."""
    tags = db.query(Tag).filter(Tag.user_id == current_user.id).order_by(Tag.name).all()
    return tags


@router.post("/tags", response_model=TagResponse)
async def create_tag(
    data: TagCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new tag."""
    existing = db.query(Tag).filter(
        Tag.user_id == current_user.id,
        Tag.name == data.name
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Tag with this name already exists")
    
    tag = Tag(
        user_id=current_user.id,
        name=data.name,
        color=data.color or "#10b981"
    )
    db.add(tag)
    db.commit()
    db.refresh(tag)
    
    return tag


@router.delete("/tags/{tag_id}")
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a tag."""
    tag = db.query(Tag).filter(
        Tag.id == tag_id,
        Tag.user_id == current_user.id
    ).first()
    
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    db.delete(tag)
    db.commit()
    
    return {"deleted": True}


@router.get("/saved", response_model=List[SavedOpportunityResponse])
async def get_saved_opportunities(
    collection_id: Optional[int] = Query(None),
    tag_id: Optional[int] = Query(None),
    lifecycle_state: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get saved opportunities with optional filters."""
    query = db.query(SavedOpportunity).filter(
        SavedOpportunity.user_id == current_user.id
    ).options(
        joinedload(SavedOpportunity.opportunity),
        joinedload(SavedOpportunity.tags).joinedload(SavedOpportunityTag.tag)
    )
    
    if collection_id is not None:
        query = query.filter(SavedOpportunity.collection_id == collection_id)
    
    if lifecycle_state:
        query = query.filter(SavedOpportunity.lifecycle_state == lifecycle_state)
    
    if tag_id is not None:
        query = query.join(SavedOpportunityTag).filter(SavedOpportunityTag.tag_id == tag_id)
    
    saved_opps = query.order_by(SavedOpportunity.updated_at.desc()).all()
    
    result = []
    for so in saved_opps:
        opp = so.opportunity
        tags = [TagResponse(
            id=sot.tag.id,
            name=sot.tag.name,
            color=sot.tag.color,
            created_at=sot.tag.created_at
        ) for sot in so.tags]
        
        result.append(SavedOpportunityResponse(
            id=so.id,
            opportunity_id=so.opportunity_id,
            collection_id=so.collection_id,
            notes=so.notes,
            lifecycle_state=so.lifecycle_state,
            created_at=so.created_at,
            updated_at=so.updated_at,
            opportunity=OpportunityBrief(
                id=opp.id,
                title=opp.title,
                category=opp.category,
                severity=opp.severity,
                market_size=opp.market_size,
                validation_count=opp.validation_count
            ),
            tags=tags
        ))
    
    return result


@router.post("/save", response_model=SavedOpportunityResponse)
async def save_opportunity(
    data: SaveOpportunityRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Save an opportunity to the Workhub."""
    opportunity = db.query(Opportunity).filter(Opportunity.id == data.opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    existing = db.query(SavedOpportunity).filter(
        SavedOpportunity.user_id == current_user.id,
        SavedOpportunity.opportunity_id == data.opportunity_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Opportunity already saved")
    
    if data.collection_id:
        collection = db.query(Collection).filter(
            Collection.id == data.collection_id,
            Collection.user_id == current_user.id
        ).first()
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")
    
    saved_opp = SavedOpportunity(
        user_id=current_user.id,
        opportunity_id=data.opportunity_id,
        collection_id=data.collection_id,
        notes=data.notes,
        lifecycle_state="saved"
    )
    db.add(saved_opp)
    db.commit()
    db.refresh(saved_opp)
    
    if data.tag_ids:
        for tag_id in data.tag_ids:
            tag = db.query(Tag).filter(
                Tag.id == tag_id,
                Tag.user_id == current_user.id
            ).first()
            if tag:
                sot = SavedOpportunityTag(
                    saved_opportunity_id=saved_opp.id,
                    tag_id=tag_id
                )
                db.add(sot)
        db.commit()
    
    saved_opp = db.query(SavedOpportunity).options(
        joinedload(SavedOpportunity.opportunity),
        joinedload(SavedOpportunity.tags).joinedload(SavedOpportunityTag.tag)
    ).filter(SavedOpportunity.id == saved_opp.id).first()
    
    opp = saved_opp.opportunity
    tags = [TagResponse(
        id=sot.tag.id,
        name=sot.tag.name,
        color=sot.tag.color,
        created_at=sot.tag.created_at
    ) for sot in saved_opp.tags]
    
    return SavedOpportunityResponse(
        id=saved_opp.id,
        opportunity_id=saved_opp.opportunity_id,
        collection_id=saved_opp.collection_id,
        notes=saved_opp.notes,
        lifecycle_state=saved_opp.lifecycle_state,
        created_at=saved_opp.created_at,
        updated_at=saved_opp.updated_at,
        opportunity=OpportunityBrief(
            id=opp.id,
            title=opp.title,
            category=opp.category,
            severity=opp.severity,
            market_size=opp.market_size,
            validation_count=opp.validation_count
        ),
        tags=tags
    )


@router.patch("/saved/{saved_id}", response_model=SavedOpportunityResponse)
async def update_saved_opportunity(
    saved_id: int,
    data: UpdateSavedOpportunityRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a saved opportunity."""
    saved_opp = db.query(SavedOpportunity).filter(
        SavedOpportunity.id == saved_id,
        SavedOpportunity.user_id == current_user.id
    ).first()
    
    if not saved_opp:
        raise HTTPException(status_code=404, detail="Saved opportunity not found")
    
    if data.collection_id is not None:
        if data.collection_id == 0:
            saved_opp.collection_id = None
        else:
            collection = db.query(Collection).filter(
                Collection.id == data.collection_id,
                Collection.user_id == current_user.id
            ).first()
            if not collection:
                raise HTTPException(status_code=404, detail="Collection not found")
            saved_opp.collection_id = data.collection_id
    
    if data.notes is not None:
        saved_opp.notes = data.notes
    
    if data.lifecycle_state is not None:
        saved_opp.lifecycle_state = data.lifecycle_state
    
    if data.tag_ids is not None:
        db.query(SavedOpportunityTag).filter(
            SavedOpportunityTag.saved_opportunity_id == saved_id
        ).delete()
        
        for tag_id in data.tag_ids:
            tag = db.query(Tag).filter(
                Tag.id == tag_id,
                Tag.user_id == current_user.id
            ).first()
            if tag:
                sot = SavedOpportunityTag(
                    saved_opportunity_id=saved_id,
                    tag_id=tag_id
                )
                db.add(sot)
    
    db.commit()
    
    saved_opp = db.query(SavedOpportunity).options(
        joinedload(SavedOpportunity.opportunity),
        joinedload(SavedOpportunity.tags).joinedload(SavedOpportunityTag.tag)
    ).filter(SavedOpportunity.id == saved_id).first()
    
    opp = saved_opp.opportunity
    tags = [TagResponse(
        id=sot.tag.id,
        name=sot.tag.name,
        color=sot.tag.color,
        created_at=sot.tag.created_at
    ) for sot in saved_opp.tags]
    
    return SavedOpportunityResponse(
        id=saved_opp.id,
        opportunity_id=saved_opp.opportunity_id,
        collection_id=saved_opp.collection_id,
        notes=saved_opp.notes,
        lifecycle_state=saved_opp.lifecycle_state,
        created_at=saved_opp.created_at,
        updated_at=saved_opp.updated_at,
        opportunity=OpportunityBrief(
            id=opp.id,
            title=opp.title,
            category=opp.category,
            severity=opp.severity,
            market_size=opp.market_size,
            validation_count=opp.validation_count
        ),
        tags=tags
    )


@router.delete("/saved/{saved_id}")
async def unsave_opportunity(
    saved_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove an opportunity from the Workhub."""
    saved_opp = db.query(SavedOpportunity).filter(
        SavedOpportunity.id == saved_id,
        SavedOpportunity.user_id == current_user.id
    ).first()
    
    if not saved_opp:
        raise HTTPException(status_code=404, detail="Saved opportunity not found")
    
    db.delete(saved_opp)
    db.commit()
    
    return {"deleted": True}


@router.get("/check/{opportunity_id}")
async def check_if_saved(
    opportunity_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Check if an opportunity is saved."""
    saved = db.query(SavedOpportunity).filter(
        SavedOpportunity.user_id == current_user.id,
        SavedOpportunity.opportunity_id == opportunity_id
    ).first()
    
    return {
        "is_saved": saved is not None,
        "saved_id": saved.id if saved else None,
        "collection_id": saved.collection_id if saved else None
    }


@router.get("/stats")
async def get_workhub_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get Workhub statistics."""
    total_saved = db.query(SavedOpportunity).filter(
        SavedOpportunity.user_id == current_user.id
    ).count()
    
    total_collections = db.query(Collection).filter(
        Collection.user_id == current_user.id
    ).count()
    
    total_tags = db.query(Tag).filter(
        Tag.user_id == current_user.id
    ).count()
    
    by_state = {}
    states = ["saved", "analyzing", "planning", "executing", "launched", "paused", "archived"]
    for state in states:
        count = db.query(SavedOpportunity).filter(
            SavedOpportunity.user_id == current_user.id,
            SavedOpportunity.lifecycle_state == state
        ).count()
        by_state[state] = count
    
    return {
        "total_saved": total_saved,
        "total_collections": total_collections,
        "total_tags": total_tags,
        "by_lifecycle_state": by_state
    }
