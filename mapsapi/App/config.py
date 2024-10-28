
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str  
    secret_key: str  
    algorithm: str  
    access_token_expire_minutes: int = 30 

    class Config:
        env_file = ".env"  # Load environment variables from a .env file
        env_file_encoding = 'utf-8'  # Specify encoding if necessary

settings = Settings()

