from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.db.database import get_db
from app.models.map_layer import SavedMapLayer
from app.models.user import User
from app.core.dependencies import get_current_active_user

router = APIRouter()


class SavedLayerCreate(BaseModel):
    name: str
    description: Optional[str] = None
    opportunity_id: Optional[int] = None
    layer_type: str = "custom"
    viewport: Optional[dict] = None
    layers_data: Optional[list] = None
    markers: Optional[list] = None
    polygons: Optional[list] = None
    datasets: Optional[list] = None
    summary: Optional[dict] = None
    is_shared: bool = False


class SavedLayerUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    viewport: Optional[dict] = None
    layers_data: Optional[list] = None
    markers: Optional[list] = None
    polygons: Optional[list] = None
    datasets: Optional[list] = None
    summary: Optional[dict] = None
    is_shared: Optional[bool] = None


class SavedLayerResponse(BaseModel):
    id: int
    user_id: int
    opportunity_id: Optional[int]
    name: str
    description: Optional[str]
    layer_type: str
    viewport: Optional[dict]
    layers_data: Optional[list]
    markers: Optional[list]
    polygons: Optional[list]
    datasets: Optional[list]
    summary: Optional[dict]
    is_shared: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class LayerSummaryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    layer_type: str
    summary: Optional[dict]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


@router.post("/", response_model=SavedLayerResponse, status_code=status.HTTP_201_CREATED)
def create_saved_layer(
    layer_data: SavedLayerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new saved map layer"""
    new_layer = SavedMapLayer(
        user_id=current_user.id,
        opportunity_id=layer_data.opportunity_id,
        name=layer_data.name,
        description=layer_data.description,
        layer_type=layer_data.layer_type,
        viewport=layer_data.viewport,
        layers_data=layer_data.layers_data,
        markers=layer_data.markers,
        polygons=layer_data.polygons,
        datasets=layer_data.datasets,
        summary=layer_data.summary,
        is_shared=layer_data.is_shared
    )
    
    db.add(new_layer)
    db.commit()
    db.refresh(new_layer)
    
    return new_layer


@router.get("/", response_model=List[SavedLayerResponse])
def get_saved_layers(
    opportunity_id: Optional[int] = None,
    include_shared: bool = True,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get user's saved map layers"""
    query = db.query(SavedMapLayer)
    
    if include_shared:
        query = query.filter(
            (SavedMapLayer.user_id == current_user.id) | (SavedMapLayer.is_shared == True)
        )
    else:
        query = query.filter(SavedMapLayer.user_id == current_user.id)
    
    if opportunity_id:
        query = query.filter(SavedMapLayer.opportunity_id == opportunity_id)
    
    query = query.order_by(desc(SavedMapLayer.created_at))
    
    return query.offset(skip).limit(limit).all()


@router.get("/summaries", response_model=List[LayerSummaryResponse])
def get_layer_summaries(
    opportunity_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get layer summaries for AI context (lightweight version without full data)"""
    query = db.query(SavedMapLayer).filter(
        (SavedMapLayer.user_id == current_user.id) | (SavedMapLayer.is_shared == True)
    )
    
    if opportunity_id:
        query = query.filter(SavedMapLayer.opportunity_id == opportunity_id)
    
    layers = query.order_by(desc(SavedMapLayer.created_at)).limit(20).all()
    
    return layers


@router.get("/{layer_id}", response_model=SavedLayerResponse)
def get_saved_layer(
    layer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific saved layer"""
    layer = db.query(SavedMapLayer).filter(
        SavedMapLayer.id == layer_id,
        (SavedMapLayer.user_id == current_user.id) | (SavedMapLayer.is_shared == True)
    ).first()
    
    if not layer:
        raise HTTPException(status_code=404, detail="Layer not found")
    
    return layer


@router.patch("/{layer_id}", response_model=SavedLayerResponse)
def update_saved_layer(
    layer_id: int,
    layer_data: SavedLayerUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a saved layer (owner only)"""
    layer = db.query(SavedMapLayer).filter(
        SavedMapLayer.id == layer_id,
        SavedMapLayer.user_id == current_user.id
    ).first()
    
    if not layer:
        raise HTTPException(status_code=404, detail="Layer not found or not authorized")
    
    update_data = layer_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(layer, field, value)
    
    db.commit()
    db.refresh(layer)
    
    return layer


@router.delete("/{layer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_saved_layer(
    layer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete a saved layer (owner only)"""
    layer = db.query(SavedMapLayer).filter(
        SavedMapLayer.id == layer_id,
        SavedMapLayer.user_id == current_user.id
    ).first()
    
    if not layer:
        raise HTTPException(status_code=404, detail="Layer not found or not authorized")
    
    db.delete(layer)
    db.commit()
    
    return None
