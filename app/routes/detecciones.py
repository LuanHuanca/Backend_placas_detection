import shutil
from fastapi import APIRouter, Depends, UploadFile, HTTPException, logger
from pathlib import Path
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
from app.db.database import get_db
from app.models.schemas import Deteccion
# from app.services.video_processor import process_video 
from app.services.process_image import process_image
# from app.services.process_video import process_video2 

router = APIRouter(prefix="/detecciones", tags=["detecciones"])

# @router.post("/procesar-video")
# async def procesar_video(
#     file: UploadFile,
#     camara_id: int,
#     db: Session = Depends(get_db)
# ):
#     if not file.content_type.startswith("video/"):
#         raise HTTPException(400, "Formato de archivo no válido")
    
#     resultados = await process_video(file, camara_id, db)
#     return {"detecciones": resultados}

# @router.post("/procesar-video2")
# async def procesar_video2(
#     file: UploadFile):
#     if not file.content_type.startswith("video/"):
#         raise HTTPException(400, "Formato de archivo no válido")
    
#     resultados = await process_video2(file)
#     return {
#         "video": FileResponse(resultados["processed_video"]),
#         "placas": resultados["detected_texts"]
#     }

@router.post("/procesar-imagen")
async def procesar_imagen(file: UploadFile):
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "Formato de archivo no válido")
    
    # Procesamiento de la imagen
    placas_detectadas = await process_image(file)

    # Ruta donde guardarás la imagen procesada
    processed_image_path = "static/processed_image.jpg"
    
    # Copiar la imagen procesada al directorio 'static'
    shutil.copy(placas_detectadas["processed_image"], processed_image_path)

    return {
        "image": f"/static/{Path(processed_image_path).name}",  # Ahora usa Path de pathlib
        "placas": placas_detectadas["detected_texts"]
    }

@router.get("/", response_model=list[Deteccion])
def get_detecciones(db: Session = Depends(get_db)):
    return db.query(Deteccion).all()