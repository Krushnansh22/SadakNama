from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_, func
from typing import List, Optional
from app.database import get_db
from app.models import Project, RoadSegment, ProjectStatus, RoadType
from app.schemas.project import (
    ProjectResponse,
    ProjectDetailResponse,
    ProjectListItem,
    ProjectSearchResult,
    RoadSegmentInProject
)
from app.schemas.common import PaginatedResponse
from app.core.cache import get_cache, set_cache
from geoalchemy2.shape import to_shape
from shapely.geometry import mapping
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/search", response_model=ProjectSearchResult)
def search_projects(
    q: Optional[str] = Query(None, description="Search query (name, district, city, pincode)"),
    district: Optional[str] = Query(None),
    city: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    pincode: Optional[str] = Query(None),
    status: Optional[ProjectStatus] = Query(None),
    road_type: Optional[RoadType] = Query(None),
    db: Session = Depends(get_db)
):
    """
    Search projects and return as GeoJSON for map display
    """
    # Build cache key
    cache_key = f"search:{q}:{district}:{city}:{state}:{pincode}:{status}:{road_type}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    
    # Build query
    query = db.query(Project).options(
        joinedload(Project.road_segments),
        joinedload(Project.contractor),
        joinedload(Project.maintenance_firm)
    )
    
    # Apply filters
    if q:
        search_filter = or_(
            Project.name.ilike(f"%{q}%"),
            Project.district.ilike(f"%{q}%"),
            Project.city.ilike(f"%{q}%"),
            Project.pincode.ilike(f"%{q}%")
        )
        query = query.filter(search_filter)
    
    if district:
        query = query.filter(Project.district.ilike(f"%{district}%"))
    if city:
        query = query.filter(Project.city.ilike(f"%{city}%"))
    if state:
        query = query.filter(Project.state.ilike(f"%{state}%"))
    if pincode:
        query = query.filter(Project.pincode == pincode)
    if status:
        query = query.filter(Project.status == status)
    if road_type:
        query = query.filter(Project.road_type == road_type)
    
    projects = query.limit(100).all()
    
    # Convert to GeoJSON
    features = []
    for project in projects:
        for segment in project.road_segments:
            # Convert PostGIS geometry to GeoJSON
            geom = to_shape(segment.geometry)
            
            features.append({
                "type": "Feature",
                "id": project.id,
                "geometry": mapping(geom),
                "properties": {
                    "project_id": project.id,
                    "project_name": project.name,
                    "status": project.status.value,
                    "road_type": project.road_type.value,
                    "district": project.district,
                    "city": project.city,
                    "contractor": project.contractor.name if project.contractor else None,
                    "sanctioned_cost": float(project.sanctioned_cost),
                    "segment_name": segment.segment_name
                }
            })
    
    result = {
        "type": "FeatureCollection",
        "features": features
    }
    
    # Cache for 30 minutes
    set_cache(cache_key, result, ttl=1800)
    
    return result


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project_detail(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Get full project details including accountability chain and related data
    """
    cache_key = f"project:{project_id}"
    cached = get_cache(cache_key)
    if cached:
        return cached
    
    project = db.query(Project).options(
        joinedload(Project.minister),
        joinedload(Project.approving_official),
        joinedload(Project.contractor),
        joinedload(Project.maintenance_firm),
        joinedload(Project.road_segments)
    ).filter(Project.id == project_id).first()
    
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get counts
    reports_count = len(project.reports)
    disbursements_count = len(project.disbursements)
    documents_count = len(project.documents)
    
    # Convert road segments to GeoJSON
    road_segments = []
    for segment in project.road_segments:
        geom = to_shape(segment.geometry)
        road_segments.append({
            "id": segment.id,
            "segment_name": segment.segment_name,
            "length_km": segment.length_km,
            "start_point": segment.start_point,
            "end_point": segment.end_point,
            "geometry": mapping(geom)
        })
    
    response = ProjectDetailResponse(
        **project.__dict__,
        road_segments=road_segments,
        reports_count=reports_count,
        disbursements_count=disbursements_count,
        documents_count=documents_count
    )
    
    # Cache for 15 minutes
    set_cache(cache_key, response.dict(), ttl=900)
    
    return response


@router.get("/", response_model=PaginatedResponse[ProjectListItem])
def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[ProjectStatus] = None,
    road_type: Optional[RoadType] = None,
    district: Optional[str] = None,
    state: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List projects with pagination and filters
    """
    query = db.query(Project).options(joinedload(Project.contractor))
    
    # Apply filters
    if status:
        query = query.filter(Project.status == status)
    if road_type:
        query = query.filter(Project.road_type == road_type)
    if district:
        query = query.filter(Project.district.ilike(f"%{district}%"))
    if state:
        query = query.filter(Project.state.ilike(f"%{state}%"))
    
    # Get total count
    total = query.count()
    
    # Paginate
    offset = (page - 1) * page_size
    projects = query.order_by(Project.created_at.desc()).offset(offset).limit(page_size).all()
    
    # Convert to list items
    items = [
        ProjectListItem(
            id=p.id,
            name=p.name,
            slug=p.slug,
            status=p.status,
            road_type=p.road_type,
            district=p.district,
            city=p.city,
            sanctioned_cost=p.sanctioned_cost,
            contractor_name=p.contractor.name if p.contractor else "N/A",
            created_at=p.created_at
        )
        for p in projects
    ]
    
    return PaginatedResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )