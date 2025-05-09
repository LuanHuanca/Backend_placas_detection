from ultralytics import YOLO
import cv2
import easyocr
import re
import tempfile
import os
from app.utils.resources import model, reader


async def process_image(file):
    # Guardar archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        await file.seek(0)
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    # Procesamiento principal
    img = cv2.imread(tmp_path)
    output_img = img.copy()
    detected_texts = []

    # Detección de placas
    results = model(img)

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            plate_img = img[y1:y2, x1:x2]
            
            # Preprocesamiento
            gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            
            # OCR
            ocr_result = reader.readtext(gray)
            plate_text = " ".join([det[1] for det in ocr_result]).strip()
            
            # Limpiar texto
            clean_text = re.sub(r'[^A-Z0-9]', '', plate_text.upper())
            
            if clean_text:
                detected_texts.append(clean_text)
                # Dibujar resultados
                cv2.rectangle(output_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(output_img, clean_text, (x1, y1-10), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # Guardar imagen procesada
    output_path = tempfile.mktemp(suffix="_processed.jpg")
    cv2.imwrite(output_path, output_img)
    
    # Limpiar archivos temporales
    os.unlink(tmp_path)

    return {
        "processed_image": output_path,
        "detected_texts": detected_texts
    }