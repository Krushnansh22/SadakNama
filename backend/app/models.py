from sqlalchemy import (Boolean, Column, ForeignKey, Integer, String, 
                        Text, DateTime, func, Enum, Decimal)
from sqlalchemy.orm import relationship
from .database import Base
import enum

# Define Enums from your plan
class RoadType(enum.Enum):
    NATIONAL_HIGHWAY = "NATIONAL_HIGHWAY"
    STATE_HIGHWAY = "STATE_HIGHWAY"
    DISTRICT_ROAD = "DISTRICT_ROAD"

class DocumentType(enum.Enum):
    APPROVAL_LETTER = "APPROVAL_LETTER"
    COMPLETION_CERT = "COMPLETION_CERT"
    PHOTO = "PHOTO"

class Firm(Base):
    __tablename__ = "firms"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    contact_email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(Text)
    performance_rating = Column(Decimal(3, 2))
    is_blacklisted = Column(Boolean, default=False)
    
    # Relationships
    construction_projects = relationship("Project", back_populates="contractor", foreign_keys="[Project.contractor_id]")
    maintenance_projects = relationship("Project", back_populates="maintenance_firm", foreign_keys="[Project.maintenance_firm_id]")

class Minister(Base):
    __tablename__ = "ministers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    party = Column(String)
    constituency = Column(String)
    term_start = Column(DateTime)
    term_end = Column(DateTime)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    district = Column(String, index=True)
    pincode = Column(String, index=True)
    road_type = Column(Enum(RoadType))
    total_cost = Column(Decimal(12, 2))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Foreign Keys
    contractor_id = Column(Integer, ForeignKey("firms.id"))
    maintenance_firm_id = Column(Integer, ForeignKey("firms.id"))
    minister_id = Column(Integer, ForeignKey("ministers.id"))
    
    # Relationships
    contractor = relationship("Firm", back_populates="construction_projects", foreign_keys=[contractor_id])
    maintenance_firm = relationship("Firm", back_populates="maintenance_projects", foreign_keys=[maintenance_firm_id])
    minister = relationship("Minister")
    documents = relationship("ProjectDocument", back_populates="project")
    disbursements = relationship("Disbursement", back_populates="project")
    reports = relationship("PublicReport", back_populates="project")

class ProjectDocument(Base):
    __tablename__ = "project_documents"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    document_type = Column(Enum(DocumentType))
    file_url = Column(String, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    
    project = relationship("Project", back_populates="documents")

class Disbursement(Base):
    __tablename__ = "disbursements"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    amount = Column(Decimal(12, 2))
    disbursement_date = Column(DateTime)
    recipient = Column(String)
    description = Column(Text)
    
    project = relationship("Project", back_populates="disbursements")

class PublicReport(Base):
    __tablename__ = "public_reports"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    reporter_contact = Column(String)
    photo_url = Column(String)
    description = Column(Text)
    upvotes_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    project = relationship("Project", back_populates="reports")