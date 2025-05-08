from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.schemas import Deteccion
from app.services.video_processor import process_video

router = APIRouter(prefix="/detecciones", tags=["detecciones"])

@router.post("/procesar-video")
async def procesar_video(
    file: UploadFile,
    camara_id: int,
    db: Session = Depends(get_db)
):
    if not file.content_type.startswith("video/"):
        raise HTTPException(400, "Formato de archivo no válido")
    
    resultados = await process_video(file, camara_id, db)
    return {"detecciones": resultados}

@router.get("/", response_model=list[Deteccion])
def get_detecciones(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(Deteccion).offset(skip).limit(limit).all()