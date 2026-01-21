from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class LayerType(str, enum.Enum):
    pins = "pins"
    heatmap = "heatmap"
    polygon = "polygon"
    custom = "custom"


class MapLayer(Base):
    __tablename__ = "map_layers"

    id = Column(Integer, primary_key=True, index=True)
    layer_name = Column(String(100), nullable=False, unique=True, index=True)
    layer_type = Column(String(50), nullable=False)
    data_source = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    style_spec = Column(JSONB, nullable=True)
    filter_rules = Column(JSONB, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True)
    display_order = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SavedMapLayer(Base):
    __tablename__ = "saved_map_layers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    opportunity_id = Column(Integer, ForeignKey("opportunities.id", ondelete="CASCADE"), nullable=True, index=True)
    
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    layer_type = Column(String(50), default="custom")
    
    viewport = Column(JSONB, nullable=True)
    layers_data = Column(JSONB, nullable=True)
    markers = Column(JSONB, nullable=True)
    polygons = Column(JSONB, nullable=True)
    datasets = Column(JSONB, nullable=True)
    summary = Column(JSONB, nullable=True)
    
    is_shared = Column(Boolean, default=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    user = relationship("User", backref="saved_map_layers")
    opportunity = relationship("Opportunity", backref="saved_map_layers")
