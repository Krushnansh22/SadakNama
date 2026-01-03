import json
from database import get_db_connection, init_db_pool, create_tables, close_db_pool
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample project data for Nagpur
SAMPLE_PROJECTS = [
    {
  "road_name": "Hindu Hrudaysamrat Balasaheb Thackeray Maharashtra Samruddhi Mahamarg",
  "contractor": "Multiple (Megha Engg, Afcons, L&T, NCC, PNC Infratech, Reliance Infra, etc.)",
  "approving_official": "Vice Chairman & Managing Director, MSRDC",
  "total_cost": "₹55,335 Crore",
  "minister_involved": "Minister of Public Works (Public Undertakings), Maharashtra",
  "maintenance_firm": "MSRDC (Infrastructure Management Department)",
  "status": "Completed",
  "start_date": "2019-01-01",
  "completion_date": "2025-06-05",
  "district": "Multiple (Nagpur, Wardha, Amravati, Washim, Buldhana, Jalna, Aurangabad, Nashik, Ahmednagar, Thane)",
  "issues_reported": 0,
  "description": "A 701 km long, 6-lane access-controlled expressway connecting Nagpur and Mumbai. It is designed for speeds up to 150 km/h and reduces travel time to ~8 hours. Features include wildlife overpasses and Krushi Samruddhi Nagar townships.",
  "geometry": {
    "type": "LineString",
    "coordinates": [
      [78.9900, 21.0200],
      [78.1998, 21.0314],
      [77.6500, 20.5800],
      [77.6400, 20.5500],
      [77.1670, 20.3270],
      [76.0600, 19.9400],
      [74.6700, 19.8700],
      [74.0006, 19.8531],
      [73.5200, 19.6000],
      [73.0672, 19.3872]
    ]
  }
},
    {
        "road_name": "Wardha Road Widening",
        "contractor": "L&T Construction",
        "approving_official": "Chief Engineer, PWD Nagpur",
        "total_cost": "₹450 Crore",
        "minister_involved": "Public Works Minister Maharashtra",
        "maintenance_firm": "MSRDC Maintenance Division",
        "status": "Completed",
        "start_date": "2022-01-15",
        "completion_date": "2024-06-30",
        "district": "Nagpur",
        "issues_reported": 0,
        "description": "Major widening project of Wardha Road from 4-lane to 6-lane to reduce traffic congestion. Includes footpaths, drainage, and street lighting.",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [79.0882, 21.1458],
                [79.0950, 21.1480],
                [79.1020, 21.1500],
                [79.1100, 21.1530]
            ]
        }
    },
    {
        "road_name": "Kamptee Road Extension",
        "contractor": "Shapoorji Pallonji",
        "approving_official": "Executive Engineer, NHAI Zone 3",
        "total_cost": "₹320 Crore",
        "minister_involved": "Road Transport Minister",
        "maintenance_firm": "JP Infrastructure",
        "status": "Under Construction",
        "start_date": "2023-03-20",
        "completion_date": "2025-12-31",
        "district": "Nagpur",
        "issues_reported": 2,
        "description": "New bypass road connecting Kamptee to outer ring road. Reducing travel time by 30 minutes.",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [79.1200, 21.2200],
                [79.1300, 21.2250],
                [79.1400, 21.2280],
                [79.1500, 21.2300]
            ]
        }
    },
    {
        "road_name": "Outer Ring Road Phase 2",
        "contractor": "NCC Limited",
        "approving_official": "Additional Chief Secretary, PWD",
        "total_cost": "₹850 Crore",
        "minister_involved": "Deputy Chief Minister Maharashtra",
        "maintenance_firm": "Nagpur Metro Rail Corporation",
        "status": "Under Construction",
        "start_date": "2023-08-10",
        "completion_date": "2026-08-10",
        "district": "Nagpur",
        "issues_reported": 5,
        "description": "Critical ring road project to decongest city center. 35 km elevated and ground-level expressway with smart traffic management.",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [79.0500, 21.1000],
                [79.0600, 21.0900],
                [79.0750, 21.0850],
                [79.0900, 21.0900],
                [79.1000, 21.1000]
            ]
        }
    },
    {
        "road_name": "Amravati Road Repair",
        "contractor": "Pratibha Industries",
        "approving_official": "Superintending Engineer, Circle 2",
        "total_cost": "₹180 Crore",
        "minister_involved": "Local MLA Nagpur West",
        "maintenance_firm": "Regional Maintenance Unit",
        "status": "Delayed",
        "start_date": "2022-10-01",
        "completion_date": "2024-03-31",
        "district": "Nagpur",
        "issues_reported": 12,
        "description": "Major repair and resurfacing of 15km stretch. Project delayed due to land acquisition issues and contractor disputes.",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [79.0400, 21.1600],
                [79.0300, 21.1650],
                [79.0200, 21.1700],
                [79.0100, 21.1750]
            ]
        }
    },
    {
        "road_name": "Seminary Hills Flyover",
        "contractor": "Gammon India",
        "approving_official": "Director, Municipal Corporation",
        "total_cost": "₹275 Crore",
        "minister_involved": "Urban Development Minister",
        "maintenance_firm": "Nagpur Municipal Corporation",
        "status": "Completed",
        "start_date": "2021-05-15",
        "completion_date": "2023-11-30",
        "district": "Nagpur",
        "issues_reported": 1,
        "description": "Four-lane flyover to ease traffic at Seminary Hills junction. Includes pedestrian walkways and green belt development.",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [79.0650, 21.1350],
                [79.0700, 21.1380],
                [79.0750, 21.1400],
                [79.0800, 21.1420]
            ]
        }
    },
    {
        "road_name": "Hingna-Kanhan Road",
        "contractor": "Dilip Buildcon",
        "approving_official": "Chief Engineer, Rural Roads",
        "total_cost": "₹210 Crore",
        "minister_involved": "Rural Development Minister",
        "maintenance_firm": "Zilla Parishad Nagpur",
        "status": "Delayed",
        "start_date": "2023-01-20",
        "completion_date": "2024-07-20",
        "district": "Nagpur",
        "issues_reported": 8,
        "description": "Connecting rural areas to city. Delayed due to monsoon damage and material shortage. Quality concerns raised by locals.",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [79.1800, 21.0800],
                [79.1900, 21.0750],
                [79.2000, 21.0700],
                [79.2100, 21.0680]
            ]
        }
    },
    {
        "road_name": "VCA Stadium Access Road",
        "contractor": "Sadbhav Engineering",
        "approving_official": "Deputy Commissioner, Sports Dept",
        "total_cost": "₹95 Crore",
        "minister_involved": "Sports & Youth Affairs Minister",
        "maintenance_firm": "VCA Infrastructure Wing",
        "status": "Completed",
        "start_date": "2022-06-01",
        "completion_date": "2023-09-30",
        "district": "Nagpur",
        "issues_reported": 0,
        "description": "Dedicated access roads and parking infrastructure for VCA Stadium. Completed ahead of schedule for international matches.",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [79.0850, 21.1180],
                [79.0880, 21.1200],
                [79.0900, 21.1220]
            ]
        }
    },
    {
        "road_name": "Airport-Metro Link Road",
        "contractor": "Larsen & Toubro",
        "approving_official": "Airport Authority Director",
        "total_cost": "₹520 Crore",
        "minister_involved": "Civil Aviation & Transport Minister",
        "maintenance_firm": "MIHAN Development Authority",
        "status": "Under Construction",
        "start_date": "2023-11-15",
        "completion_date": "2026-05-15",
        "district": "Nagpur",
        "issues_reported": 3,
        "description": "High-speed corridor connecting Dr. Babasaheb Ambedkar International Airport to Metro stations. Includes smart toll system.",
        "geometry": {
            "type": "LineString",
            "coordinates": [
                [79.0450, 21.0920],
                [79.0500, 21.0950],
                [79.0600, 21.1000],
                [79.0700, 21.1050]
            ]
        }
    }
]

def seed_database():
    """Populate database with sample projects"""
    try:
        logger.info("🌱 Starting database seeding...")
        
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                # Check if data already exists
                cursor.execute("SELECT COUNT(*) FROM projects")
                count = cursor.fetchone()[0]
                
                if count > 0:
                    logger.info(f"⚠️  Database already contains {count} projects")
                    response = input("Do you want to clear and reseed? (yes/no): ")
                    if response.lower() != 'yes':
                        logger.info("Seeding cancelled")
                        return
                    
                    cursor.execute("DELETE FROM projects")
                    logger.info("🗑️  Existing data cleared")
                
                # Insert sample projects
                insert_query = """
                INSERT INTO projects (
                    road_name, contractor, approving_official, total_cost,
                    minister_involved, maintenance_firm, status, start_date,
                    completion_date, district, issues_reported, description, geometry
                ) VALUES (
                    %(road_name)s, %(contractor)s, %(approving_official)s, %(total_cost)s,
                    %(minister_involved)s, %(maintenance_firm)s, %(status)s, %(start_date)s,
                    %(completion_date)s, %(district)s, %(issues_reported)s, %(description)s,
                    %(geometry)s::jsonb
                )
                """
                
                for project in SAMPLE_PROJECTS:
                    project['geometry'] = json.dumps(project['geometry'])
                    cursor.execute(insert_query, project)
                
                logger.info(f"✅ Successfully seeded {len(SAMPLE_PROJECTS)} projects")
                
                # Display summary
                cursor.execute("""
                    SELECT status, COUNT(*) as count 
                    FROM projects 
                    GROUP BY status
                """)
                
                logger.info("\n📊 Database Summary:")
                for row in cursor.fetchall():
                    logger.info(f"   {row[0]}: {row[1]} projects")
                
    except Exception as e:
        logger.error(f"❌ Failed to seed database: {e}")
        raise

if __name__ == "__main__":
    try:
        init_db_pool()
        create_tables()
        seed_database()
        logger.info("\n🎉 Database setup complete!")
    except Exception as e:
        logger.error(f"Setup failed: {e}")
    finally:
        close_db_pool()