import cv2
import numpy as np
from fastapi import UploadFile
from app.services.ocr_service import extract_plate_text
from app.db.models import Deteccion, Placa
from datetime import datetime

async def process_video(file: UploadFile, camara_id: int, db):
    results = []
    
    # Convertir video a frames
    content = await file.read()
    nparr = np.frombuffer(content, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # Simulación de detección
    placa_text = "ABC123"
    confianza = 0.95
    
    # Guardar en DB
    placa = Placa(
        texto=placa_text,
        imagen_base64="base64_simulado",
        fecha_hora=datetime.now()
    )
    db.add(placa)
    db.commit()
    
    deteccion = Deteccion(
        placa_id=placa.id,
        camara_id=camara_id,
        fecha_hora=datetime.now(),
        confianza=confianza
    )
    db.add(deteccion)
    db.commit()
    
    results.append({
        "placa": placa_text,
        "confianza": confianza,
        "timestamp": datetime.now().isoformat()
    })
    
    return results