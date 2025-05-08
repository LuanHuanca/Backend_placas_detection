from fastapi import FastAPI
from app.routes import (
    camaras,
    detecciones,
    placas,
    alertas,
    vehiculo
)
from app.db.database import engine, Base
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Detección de Placas",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json"
)

app.include_router(camaras.router)
app.include_router(detecciones.router)
app.include_router(placas.router)
app.include_router(alertas.router)
app.include_router(vehiculo.router)  

@app.get("/")
def root():
    return {"status": "Sistema operativo"}