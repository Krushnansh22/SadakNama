from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    database_host: str = "localhost"
    database_port: int = 5432
    database_name: str = "roadtrack_db"
    database_user: str = "roadtrack_user"
    database_password: str
    
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    environment: str = "production"
    
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()