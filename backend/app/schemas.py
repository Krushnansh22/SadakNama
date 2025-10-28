from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from .models import RoadType # Import the enum

# --- Firm Schemas ---
class FirmBase(BaseModel):
    name: str
    contact_email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    is_blacklisted: bool = False

class FirmCreate(FirmBase):
    pass

class Firm(FirmBase):
    id: int
    performance_rating: Optional[Decimal] = None

    class Config:
        orm_mode = True

# --- Minister Schemas ---
class MinisterBase(BaseModel):
    name: str
    party: Optional[str] = None
    constituency: Optional[str] = None

class MinisterCreate(MinisterBase):
    pass

class Minister(MinisterBase):
    id: int
    term_start: Optional[datetime] = None
    term_end: Optional[datetime] = None

    class Config:
        orm_mode = True

# --- Project Schemas ---
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    district: str
    pincode: Optional[str] = None
    road_type: RoadType
    total_cost: Decimal

class ProjectCreate(ProjectBase):
    # When creating, we just need the IDs
    contractor_id: int
    maintenance_firm_id: int
    minister_id: int

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # On read, we can nest the full objects
    contractor: Firm
    maintenance_firm: Firm
    minister: Minister
    
    # We can add documents, etc. here later
    # documents: List = [] 
    # reports: List = []

    class Config:
        orm_mode = True # Tells Pydantic to read data from ORM models