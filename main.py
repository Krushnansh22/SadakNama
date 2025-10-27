from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlite3
import json
from pathlib import Path

app = FastAPI(title="RoadTrack API")

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect('projects.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the index.html file"""
    html_path = Path("index.html")
    if html_path.exists():
        return FileResponse("index.html")
    return HTMLResponse(content="<h1>index.html not found. Please create it.</h1>", status_code=404)

@app.get("/api/projects")
async def get_projects():
    """Get all projects with their details"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                id, road_name, contractor, approving_official,
                total_cost, minister_involved, maintenance_firm,
                status, start_date, completion_date, district,
                issues_reported, description, geometry
            FROM projects
        ''')
        
        projects = []
        for row in cursor.fetchall():
            project = {
                'id': row['id'],
                'road_name': row['road_name'],
                'contractor': row['contractor'],
                'approving_official': row['approving_official'],
                'total_cost': row['total_cost'],
                'minister_involved': row['minister_involved'],
                'maintenance_firm': row['maintenance_firm'],
                'status': row['status'],
                'start_date': row['start_date'],
                'completion_date': row['completion_date'],
                'district': row['district'],
                'issues_reported': row['issues_reported'],
                'description': row['description'],
                'geometry': json.loads(row['geometry'])  # Parse JSON string to object
            }
            projects.append(project)
        
        conn.close()
        return {'success': True, 'projects': projects, 'count': len(projects)}
    
    except Exception as e:
        return {'success': False, 'error': str(e), 'projects': []}

@app.get("/api/health")
async def health_check():
    """Simple health check endpoint"""
    return {'status': 'healthy', 'message': 'RoadTrack API is running'}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting RoadTrack API...")
    print("📍 Frontend: http://localhost:8000")
    print("📍 API: http://localhost:8000/api/projects")
    uvicorn.run(app, host="0.0.0.0", port=8000)