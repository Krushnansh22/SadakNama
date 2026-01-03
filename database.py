import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
from config import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection pool for better performance
connection_pool = None

def init_db_pool():
    """Initialize database connection pool"""
    global connection_pool
    try:
        connection_pool = SimpleConnectionPool(
            1, 20,
            host=settings.database_host,
            port=settings.database_port,
            database=settings.database_name,
            user=settings.database_user,
            password=settings.database_password
        )
        logger.info("✅ Database connection pool created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create connection pool: {e}")
        raise

def close_db_pool():
    """Close database connection pool"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        logger.info("Database connection pool closed")

@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = connection_pool.getconn()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        connection_pool.putconn(conn)

def create_tables():
    """Create database tables if they don't exist"""
    create_table_query = """
    CREATE TABLE IF NOT EXISTS projects (
        id SERIAL PRIMARY KEY,
        road_name VARCHAR(255) NOT NULL,
        contractor VARCHAR(255) NOT NULL,
        approving_official VARCHAR(255) NOT NULL,
        total_cost VARCHAR(100) NOT NULL,
        minister_involved VARCHAR(255) NOT NULL,
        maintenance_firm VARCHAR(255) NOT NULL,
        status VARCHAR(50) NOT NULL CHECK (status IN ('Completed', 'Under Construction', 'Delayed')),
        start_date VARCHAR(50) NOT NULL,
        completion_date VARCHAR(50) NOT NULL,
        district VARCHAR(100) NOT NULL,
        issues_reported INTEGER DEFAULT 0,
        description TEXT NOT NULL,
        geometry JSONB NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
    CREATE INDEX IF NOT EXISTS idx_projects_district ON projects(district);
    CREATE INDEX IF NOT EXISTS idx_projects_road_name ON projects(road_name);
    CREATE INDEX IF NOT EXISTS idx_projects_geometry ON projects USING GIN(geometry);
    """
    
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(create_table_query)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        raise

def check_db_connection():
    """Check if database connection is working"""
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False