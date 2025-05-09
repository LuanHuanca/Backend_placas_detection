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
    img = preprocess_for_detection(img)
    output_img = img.copy()
    detected_texts = []

    # Detección de placas
    results = model(img, imgsz=1280, conf=0.5, iou=0.4)

    for result in results:
        for box in result.boxes:
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            plate_img = img[y1:y2, x1:x2]
            
            # Preprocesamiento específico para placas oscuras
            processed_plate = enhance_plate_details(plate_img)
            
            # OCR mejorado
            ocr_result = reader.readtext(processed_plate, paragraph=True, 
                                       allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789',
                                       contrast_ths=0.2, adjust_contrast=0.6)
            
            plate_text = "".join([det[1] for det in ocr_result]).strip()
            clean_text = re.sub(r'[^A-Z0-9]', '', plate_text.upper())
            
            if 6 <= len(clean_text) <= 8:
                detected_texts.append(clean_text)
                cv2.rectangle(output_img, (x1, y1), (x2, y2), (30, 180, 30), 3)
                cv2.putText(output_img, clean_text, (x1, y1-15), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.9, (30, 180, 30), 2)

    # Guardar resultados
    output_path = tempfile.mktemp(suffix="_processed.jpg")
    cv2.imwrite(output_path, output_img)
    os.unlink(tmp_path)

    return {
        "processed_image": output_path,
        "detected_texts": detected_texts
    }

def preprocess_for_detection(img):
    # 1. Ajuste de luminosidad selectivo
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Mejorar contraste en áreas oscuras
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    
    # Combinar canales
    lab = cv2.merge((l, a, b))
    img = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
    
    # 2. Escalado inteligente
    img = cv2.resize(img, None, fx=1.3, fy=1.3, interpolation=cv2.INTER_CUBIC)
    
    # 3. Enfoque selectivo para texto
    kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    img = cv2.filter2D(img, -1, kernel)
    
    return img

def enhance_plate_details(plate_img):
    # 1. Convertir a escala de grises
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    
    # 2. Ecualización adaptativa para baja iluminación
    adaptive = cv2.adaptiveThreshold(gray, 255, 
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                   cv2.THRESH_BINARY_INV, 11, 4)
    
    # 3. Mezcla con imagen original
    _, thresh_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    combined = cv2.addWeighted(adaptive, 0.7, thresh_otsu, 0.3, 0)
    
    # 4. Reducción de ruido preservando bordes
    denoised = cv2.fastNlMeansDenoising(combined, None, h=8, templateWindowSize=7, searchWindowSize=21)
    
    # 5. Realce final de bordes
    edges = cv2.Canny(denoised, 50, 150)
    result = cv2.addWeighted(denoised, 0.9, edges, 0.1, 0)
    
    return result