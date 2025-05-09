import cv2
import numpy as np
import tempfile
import os
from ultralytics import YOLO
import easyocr
import re
from app.utils.resources import model, reader


# Configuración para formato de placas de Oaxaca
PLACA_REGEX = re.compile(r'^[A-Z]{3}-?\d{3}$')  # Permite formato ABC123 o ABC-123

async def process_image(file):
    # Guardar el archivo temporalmente
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        await file.seek(0)
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    # Leer y procesar imagen
    image = cv2.imread(tmp_path)
    processed_image = image.copy()
    placas_detectadas = []

    # Detección de placas
    detections = model(image)
    
    for detection in detections:
        for box in detection.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            conf = box.conf.item()
            
            if conf < 0.5:  # Filtro de confianza
                continue

            # Dibujar rectángulo en la imagen procesada
            cv2.rectangle(processed_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Recortar área de la placa
            plate_img = image[y1:y2, x1:x2]
            
            if plate_img.size == 0:
                continue

            # Preprocesamiento para OCR
            gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Leer texto
            ocr_result = reader.readtext(thresh)
            plate_text = ""

            for result in ocr_result:
                text = re.sub(r'[^A-Z0-9-]', '', result[1].upper())
                
                # Corregir errores comunes
                replacements = {'0':'O', '1':'I', '2':'Z', '4':'A', '5':'S', '7':'Z', '8':'B'}
                text = ''.join([replacements.get(c, c) for c in text])
                
                if PLACA_REGEX.match(text):
                    plate_text = text
                    break

            if plate_text:
                # Agregar texto a la imagen
                cv2.putText(processed_image, plate_text, (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
                placas_detectadas.append(plate_text)

    # Guardar imagen procesada
    output_path = tempfile.mktemp(suffix=".jpg")
    cv2.imwrite(output_path, processed_image)
    
    # Limpiar archivos temporales
    os.unlink(tmp_path)

    return {
        "processed_image": output_path,
        "placas": placas_detectadas
    }