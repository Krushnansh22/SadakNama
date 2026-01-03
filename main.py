from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pathlib import Path
import json
import logging
from psycopg2.extras import RealDictCursor

from config import settings
from database import (
    init_db_pool, 
    close_db_pool, 
    create_tables, 
    get_db_connection,
    check_db_connection
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    logger.info("🚀 Starting RoadTrack API...")
    
    # Startup
    try:
        init_db_pool()
        create_tables()
        
        if check_db_connection():
            logger.info("✅ Database connection successful")
        else:
            logger.error("❌ Database connection failed")
            raise Exception("Database connection failed")
        
        logger.info(f"🌐 Server running at http://{settings.app_host}:{settings.app_port}")
        logger.info(f"📍 Frontend: http://localhost:{settings.app_port}")
        logger.info(f"📍 API: http://localhost:{settings.app_port}/api/projects")
        logger.info(f"📍 Health: http://localhost:{settings.app_port}/api/health")
        
    except Exception as e:
        logger.error(f"❌ Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down RoadTrack API...")
    close_db_pool()

app = FastAPI(
    title="RoadTrack API",
    description="Public Accountability Portal for Road Projects",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.environment == "development" else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main HTML page"""
    try:
        html_path = Path("index.html")
        if html_path.exists():
            return FileResponse("index.html")
        else:
            logger.error("index.html not found")
            return HTMLResponse(
                content="<h1>Error: index.html not found</h1>",
                status_code=404
            )
    except Exception as e:
        logger.error(f"Error serving frontend: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    try:
        db_status = check_db_connection()
        return {
            'status': 'healthy' if db_status else 'unhealthy',
            'message': 'RoadTrack API is running',
            'database': 'connected' if db_status else 'disconnected',
            'environment': settings.environment
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={
                'status': 'unhealthy',
                'message': str(e)
            }
        )

@app.get("/api/projects")
async def get_projects(
    status: str = None,
    district: str = None,
    search: str = None
):
    """
    Get all projects with optional filtering
    
    Query parameters:
    - status: Filter by project status (Completed, Under Construction, Delayed)
    - district: Filter by district name
    - search: Search in road name, contractor, or description
    """
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Build dynamic query
                query = """
                    SELECT 
                        id, road_name, contractor, approving_official,
                        total_cost, minister_involved, maintenance_firm,
                        status, start_date, completion_date, district,
                        issues_reported, description, geometry,
                        created_at, updated_at
                    FROM projects
                    WHERE 1=1
                """
                params = {}
                
                if status:
                    query += " AND status = %(status)s"
                    params['status'] = status
                
                if district:
                    query += " AND district ILIKE %(district)s"
                    params['district'] = f"%{district}%"
                
                if search:
                    query += """ AND (
                        road_name ILIKE %(search)s OR
                        contractor ILIKE %(search)s OR
                        description ILIKE %(search)s
                    )"""
                    params['search'] = f"%{search}%"
                
                query += " ORDER BY created_at DESC"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # Convert rows to list of dicts
                projects = []
                for row in rows:
                    project = dict(row)
                    # Ensure geometry is a dict, not a string
                    if isinstance(project['geometry'], str):
                        project['geometry'] = json.loads(project['geometry'])
                    projects.append(project)
                
                logger.info(f"Retrieved {len(projects)} projects")
                
                return {
                    'success': True,
                    'projects': projects,
                    'count': len(projects)
                }
    
    except Exception as e:
        logger.error(f"Error fetching projects: {e}")
        return JSONResponse(
            status_code=500,
            content={
                'success': False,
                'error': str(e),
                'projects': []
            }
        )

@app.get("/api/projects/{project_id}")
async def get_project(project_id: int):
    """Get a specific project by ID"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM projects WHERE id = %s
                """, (project_id,))
                
                row = cursor.fetchone()
                
                if not row:
                    raise HTTPException(status_code=404, detail="Project not found")
                
                project = dict(row)
                if isinstance(project['geometry'], str):
                    project['geometry'] = json.loads(project['geometry'])
                
                return {
                    'success': True,
                    'project': project
                }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_statistics():
    """Get overall statistics"""
    try:
        with get_db_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT 
                        COUNT(*) as total_projects,
                        COUNT(*) FILTER (WHERE status = 'Completed') as completed,
                        COUNT(*) FILTER (WHERE status = 'Under Construction') as under_construction,
                        COUNT(*) FILTER (WHERE status = 'Delayed') as delayed,
                        SUM(issues_reported) as total_issues,
                        COUNT(DISTINCT district) as total_districts
                    FROM projects
                """)
                
                stats = dict(cursor.fetchone())
                
                return {
                    'success': True,
                    'statistics': stats
                }
    
    except Exception as e:
        logger.error(f"Error fetching statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.environment == "development",
        log_level="info"
    )