from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    BLOB_CONNECTION_STRING: str
    CONTAINER_NAME: str
    ENVIRONMENT: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
    
settings = Settings()
