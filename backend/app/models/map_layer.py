from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class LayerType(str, enum.Enum):
    pins = "pins"
    heatmap = "heatmap"
    polygon = "polygon"


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
