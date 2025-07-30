import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    default_project_id: str = "default"
    api_key: str = os.getenv("API_KEY", "your-secret-api-key")
    data_dir: str = os.getenv("DATA_DIR", "/app/data")
    
    class Config:
        env_file = ".env"

settings = Settings()