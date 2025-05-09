from fastapi import APIRouter, Depends, UploadFile, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from app.db.database import get_db
from app.models.schemas import Deteccion
from app.services.video_processor import process_video 
from app.services.process_image import process_image 

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

@router.post("/procesar-imagen")
async def procesar_imagen(file: UploadFile):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Formato de archivo no válido")
    
    placas_detectadas = await process_image(file)
    return {
        "image": FileResponse(placas_detectadas["processed_image"]),
        "placas": placas_detectadas["detected_texts"]
    }

@router.get("/", response_model=list[Deteccion])
def get_detecciones(db: Session = Depends(get_db)):
    return db.query(Deteccion).all()