import sqlite3
import json

# Create database and table
conn = sqlite3.connect('projects.db')
cursor = conn.cursor()

# Drop table if exists (for clean setup)
cursor.execute('DROP TABLE IF EXISTS projects')

# Create projects table
cursor.execute('''
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    road_name TEXT NOT NULL,
    contractor TEXT NOT NULL,
    approving_official TEXT NOT NULL,
    total_cost TEXT NOT NULL,
    minister_involved TEXT NOT NULL,
    maintenance_firm TEXT NOT NULL,
    status TEXT NOT NULL,
    start_date TEXT,
    completion_date TEXT,
    district TEXT,
    issues_reported INTEGER DEFAULT 0,
    description TEXT,
    geometry TEXT NOT NULL
)
''')

# Demo data - 6 realistic projects with GeoJSON geometries
demo_projects = [
    {
        'road_name': 'NH-44 Widening (Nagpur South)',
        'contractor': 'L&T Infrastructure Pvt Ltd',
        'approving_official': 'Rajesh Kumar (Chief Engineer, NHAI)',
        'total_cost': '₹125 Crores',
        'minister_involved': 'Nitin Gadkari (Union Minister, Road Transport)',
        'maintenance_firm': 'IRB Infrastructure',
        'status': 'Completed',
        'start_date': '2022-01-15',
        'completion_date': '2024-03-20',
        'district': 'Nagpur',
        'issues_reported': 2,
        'description': '4-lane to 6-lane widening project covering 12.5 km stretch',
        'geometry': json.dumps({
            "type": "LineString",
            "coordinates": [[79.0882, 21.1458], [79.0950, 21.1380], [79.1020, 21.1300]]
        })
    },
    {
        'road_name': 'Ring Road Phase 2 (East Section)',
        'contractor': 'Ashoka Buildcon Ltd',
        'approving_official': 'Priya Sharma (Executive Engineer, PWD)',
        'total_cost': '₹85 Crores',
        'minister_involved': 'Devendra Fadnavis (Deputy CM, Maharashtra)',
        'maintenance_firm': 'NCC Limited',
        'status': 'Under Construction',
        'start_date': '2023-06-01',
        'completion_date': '2025-12-31',
        'district': 'Nagpur',
        'issues_reported': 5,
        'description': 'New 8 km ring road to reduce city traffic congestion',
        'geometry': json.dumps({
            "type": "LineString",
            "coordinates": [[79.1200, 21.1500], [79.1280, 21.1450], [79.1350, 21.1420], [79.1420, 21.1400]]
        })
    },
    {
        'road_name': 'Mumbai-Nagpur Expressway Connector',
        'contractor': 'GMR Infrastructure',
        'approving_official': 'Amit Deshmukh (Superintendent Engineer, MSRDC)',
        'total_cost': '₹340 Crores',
        'minister_involved': 'Eknath Shinde (Chief Minister, Maharashtra)',
        'maintenance_firm': 'Sadbhav Engineering',
        'status': 'Delayed',
        'start_date': '2021-11-10',
        'completion_date': '2024-06-30',
        'district': 'Nagpur',
        'issues_reported': 12,
        'description': 'Critical connector road linking NH-44 to Samruddhi Expressway',
        'geometry': json.dumps({
            "type": "LineString",
            "coordinates": [[79.0700, 21.1600], [79.0780, 21.1550], [79.0850, 21.1500]]
        })
    },
    {
        'road_name': 'Airport-MIHAN Link Road',
        'contractor': 'Dilip Buildcon Ltd',
        'approving_official': 'Suresh Patil (Deputy Executive Engineer)',
        'total_cost': '₹42 Crores',
        'minister_involved': 'Nitin Raut (Cabinet Minister, PWD)',
        'maintenance_firm': 'PNC Infratech',
        'status': 'Completed',
        'start_date': '2022-08-01',
        'completion_date': '2023-11-15',
        'district': 'Nagpur',
        'issues_reported': 0,
        'description': 'High-speed corridor connecting airport to MIHAN SEZ',
        'geometry': json.dumps({
            "type": "LineString",
            "coordinates": [[79.0500, 21.0920], [79.0580, 21.0950], [79.0650, 21.0980]]
        })
    },
    {
        'road_name': 'Outer Ring Road (West Bypass)',
        'contractor': 'KNR Constructions',
        'approving_official': 'Deepak Rao (Chief Project Manager, NMC)',
        'total_cost': '₹95 Crores',
        'minister_involved': 'Devendra Fadnavis (Deputy CM, Maharashtra)',
        'maintenance_firm': 'Hindustan Construction Co',
        'status': 'Under Construction',
        'start_date': '2024-02-01',
        'completion_date': '2026-01-31',
        'district': 'Nagpur',
        'issues_reported': 3,
        'description': 'New bypass to divert heavy vehicle traffic from city center',
        'geometry': json.dumps({
            "type": "LineString",
            "coordinates": [[79.0400, 21.1400], [79.0450, 21.1350], [79.0500, 21.1280]]
        })
    },
    {
        'road_name': 'Smart City Road Network - Zone A',
        'contractor': 'Megha Engineering (MEIL)',
        'approving_official': 'Anjali Verma (Project Director, Smart City)',
        'total_cost': '₹68 Crores',
        'minister_involved': 'Nitin Gadkari (Union Minister, Road Transport)',
        'maintenance_firm': 'Tata Projects Ltd',
        'status': 'Delayed',
        'start_date': '2023-01-15',
        'completion_date': '2024-08-31',
        'district': 'Nagpur',
        'issues_reported': 8,
        'description': 'Smart roads with LED lighting and intelligent traffic management',
        'geometry': json.dumps({
            "type": "LineString",
            "coordinates": [[79.1100, 21.1550], [79.1150, 21.1520], [79.1200, 21.1480]]
        })
    }
]

# Insert demo data
for project in demo_projects:
    cursor.execute('''
        INSERT INTO projects (
            road_name, contractor, approving_official, total_cost,
            minister_involved, maintenance_firm, status, start_date,
            completion_date, district, issues_reported, description, geometry
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        project['road_name'],
        project['contractor'],
        project['approving_official'],
        project['total_cost'],
        project['minister_involved'],
        project['maintenance_firm'],
        project['status'],
        project['start_date'],
        project['completion_date'],
        project['district'],
        project['issues_reported'],
        project['description'],
        project['geometry']
    ))

conn.commit()
conn.close()

print("✅ Database setup complete!")
print(f"✅ Inserted {len(demo_projects)} demo projects")
print("✅ Run 'python main.py' to start the server")