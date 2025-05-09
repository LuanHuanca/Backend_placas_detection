import cv2
import numpy as np
import tempfile
from fastapi import UploadFile
from app.services.ocr_service import extract_plate_text 
from app.db.models import Deteccion, Placa
from datetime import datetime
from ultralytics import YOLO
import easyocr
import re
import base64
from ultralytics import YOLO
from app.utils.resources import model, reader


async def process_video(file: UploadFile, camara_id: int, db):
    results = []

    # Guardar el archivo temporalmente para poder usarlo con OpenCV
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    # Abrir el video
    cap = cv2.VideoCapture(tmp_path)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Detección con YOLO
        detections = model(frame)

        for detection in detections:
            for box in detection.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                plate_img = frame[y1:y2, x1:x2]

                # Preprocesamiento
                gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
                gray = cv2.equalizeHist(gray)

                # OCR con EasyOCR
                ocr_result = reader.readtext(gray)
                plate_text = ""
                for result in ocr_result:
                    text = result[1]
                    clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())
                    if len(clean_text) > 2:
                        plate_text += clean_text + " "

                if plate_text:
                    # Convertir imagen a base64
                    _, buffer = cv2.imencode('.jpg', plate_img)
                    image_base64 = base64.b64encode(buffer).decode('utf-8')

                    # # Guardar placa
                    # placa = Placa(
                    #     texto=plate_text.strip(),
                    #     imagen_base64=image_base64,
                    #     fecha_hora=datetime.now()
                    # )
                    # db.add(placa)
                    # db.commit()
                    # db.refresh(placa)

                    # # Guardar detección
                    # deteccion = Deteccion(
                    #     placa_id=placa.id,
                    #     camara_id=camara_id,
                    #     fecha_hora=datetime.now(),
                    #     confianza=float(box.conf[0])
                    # )
                    # db.add(deteccion)
                    # db.commit()

                    # # Agregar a resultados
                    results.append({
                        "placa": plate_text.strip(),
                        "confianza": float(box.conf[0]),
                        "timestamp": datetime.now().isoformat()
                    })

                    print(f"📸 Placa detectada: {plate_text.strip()} (Confianza: {float(box.conf[0]):.2f})")

    cap.release()
    return results
