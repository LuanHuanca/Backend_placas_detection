from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_HOST: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DB_PORT: int  
    JWT_SECRET: str = "secret-key-1234"
    ALGORITHM: str = "HS256"
    
    class Config:
        env_file = ".env"

settings = Settings()