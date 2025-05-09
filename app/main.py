from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routes import (
    camaras,
    detecciones,
    placas,
    alertas,
    vehiculo
)
from app.db.database import engine, Base
from app.core.config import settings
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Detección de Placas",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json"
)

# Permitir solicitudes desde http://localhost:4200
app.mount("/static", StaticFiles(directory="static"), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],  # o usa ['*'] para permitir todas las solicitudes (no recomendado en producción)
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos HTTP (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permitir todos los encabezados
)


app.include_router(camaras.router)
app.include_router(detecciones.router)
app.include_router(placas.router)
app.include_router(alertas.router)
app.include_router(vehiculo.router)  

@app.get("/")
def root():
    return {"status": "Plate detection system is running"}