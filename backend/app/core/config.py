import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "Drug Interaction Predictor"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # DATABASE
    # Using absolute path to prevent CWD-related issues between backend and debug scripts
    DATABASE_URL: str = f"sqlite:///{os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'drug_interaction.db')}"
    
    # AUTHENTICATION
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
