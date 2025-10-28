from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from app.database import Base


class RoadSegment(Base):
    __tablename__ = "road_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Geospatial data (stored as WKT or GeoJSON)
    # SRID 4326 is WGS84 (standard for GPS coordinates)
    geometry = Column(Geometry(geometry_type='LINESTRING', srid=4326), nullable=False)
    
    # Additional metadata
    segment_name = Column(String(255))
    length_km = Column(Integer)  # Length in kilometers
    start_point = Column(String(255))  # Human-readable start location
    end_point = Column(String(255))  # Human-readable end location
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="road_segments")
    
    def __repr__(self):
        return f"<RoadSegment {self.segment_name} - Project {self.project_id}>"