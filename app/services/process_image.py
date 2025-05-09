import numpy as np
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
    img = preprocess_for_detection(img)  # Aquí aplicas todo
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


def preprocess_for_detection(img):
    # 1. Mejorar resolución con interpolación de alta calidad
    scale_factor = 2  # Ajustar según necesidad
    img = cv2.resize(
        img, 
        None, 
        fx=scale_factor, 
        fy=scale_factor, 
        interpolation=cv2.INTER_LANCZOS4
    )

    # 2. Oscurecer la imagen usando ajuste gamma
    gamma = 1.4  # Valores >1 oscurecen
    lookup_table = np.array([
        ((i / 255.0) ** (1/gamma)) * 255 
        for i in np.arange(0, 256)
    ]).astype("uint8")
    img = cv2.LUT(img, lookup_table)

    # 3. Aumentar contraste local usando CLAHE
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    lab = cv2.merge((l, a, b))
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

    # 4. Enfoque con máscara de enfoque (unsharp mask)
    gaussian = cv2.GaussianBlur(img, (0,0), 2.0)
    img = cv2.addWeighted(img, 1.7, gaussian, -0.7, 0)

    # 5. Reducción de ruido opcional
    img = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

    return img
