from sqlalchemy.orm import Session
from . import models, schemas

# --- Project CRUD ---
def get_project(db: Session, project_id: int):
    return db.query(models.Project).filter(models.Project.id == project_id).first()

def get_projects(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Project).offset(skip).limit(limit).all()

def create_project(db: Session, project: schemas.ProjectCreate):
    db_project = models.Project(**project.model_dump())
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

# --- Firm CRUD ---
def get_firm(db: Session, firm_id: int):
    return db.query(models.Firm).filter(models.Firm.id == firm_id).first()

def create_firm(db: Session, firm: schemas.FirmCreate):
    db_firm = models.Firm(**firm.model_dump())
    db.add(db_firm)
    db.commit()
    db.refresh(db_firm)
    return db_firm

# --- Minister CRUD ---
def create_minister(db: Session, minister: schemas.MinisterCreate):
    db_minister = models.Minister(**minister.model_dump())
    db.add(db_minister)
    db.commit()
    db.refresh(db_minister)
    return db_minister