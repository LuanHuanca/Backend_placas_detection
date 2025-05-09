from pydantic_settings import BaseSettings

# 1. Definición de la clase de configuración
class Settings(BaseSettings):
    # 2. Variables de entorno requeridas (sin valor por defecto)
    DB_HOST: str       # Host de la base de datos
    DB_USER: str       # Usuario de la base de datos
    DB_PASSWORD: str   # Contraseña de la base de datos
    DB_NAME: str       # Nombre de la base de datos
    DB_PORT: int       # Puerto de la base de datos
    
    # 3. Variables opcionales con valores por defecto
    JWT_SECRET: str = "secret-key-1234"  # Clave para JWT
    ALGORITHM: str = "HS256"             # Algoritmo para JWT
    
    # 4. Configuración adicional
    class Config:
        env_file = ".env"  # Especifica el archivo de variables de entorno

# 5. Instancia de configuración global
settings = Settings()