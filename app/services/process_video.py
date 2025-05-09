import numpy as np
from ultralytics import YOLO
import cv2
import easyocr
import re
import tempfile
import os
import torch
from typing import List, Dict
from concurrent.futures import ThreadPoolExecutor
from app.utils.resources import model, reader


# Configuración de optimización
PROCESSING_RESOLUTION = (640, 480)  # HD reducido
FRAME_SKIP = 3                      # Procesar 1 de cada 3 frames
MODEL_IMG_SIZE = 320                # Tamaño de entrada del modelo
OCR_WORKERS = 4                     # Hilos paralelos para OCR

async def process_video2(file):
    # Configuración inicial
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    ocr_executor = ThreadPoolExecutor(max_workers=OCR_WORKERS)

    # Guardar archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        await file.seek(0)
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    # Configurar video de entrada con resolución reducida
    cap = cv2.VideoCapture(tmp_path)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, PROCESSING_RESOLUTION[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, PROCESSING_RESOLUTION[1])
    
    # Preparar video de salida
    output_path = tempfile.mktemp(suffix="_processed.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, cap.get(cv2.CAP_PROP_FPS), PROCESSING_RESOLUTION)
    
    detected_texts = []
    frame_count = 0
    last_valid_plates = {}

    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            break
            
        # Saltar frames
        if frame_count % FRAME_SKIP != 0:
            frame_count += 1
            continue
            
        # Procesamiento optimizado
        processed_frame = preprocess_for_detection(frame)
        results = model.track(
            processed_frame,
            imgsz=MODEL_IMG_SIZE,
            half=True,
            device=device,
            conf=0.6,
            iou=0.5,
            persist=True,
            verbose=False
        )
        
        # Procesar detecciones en paralelo
        futures = []
        for result in results:
            for box in result.boxes:
                if box.id is None:
                    continue
                    
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                plate_img = processed_frame[y1:y2, x1:x2]
                futures.append(ocr_executor.submit(process_plate, plate_img, box.id))
        
        # Obtener resultados OCR
        for future in futures:
            plate_text, track_id = future.result()
            if plate_text and validate_plate(plate_text):
                if track_id not in last_valid_plates:
                    detected_texts.append(plate_text)
                last_valid_plates[track_id] = plate_text
        
        # Dibujar resultados
        frame = draw_optimized_results(frame, results, last_valid_plates)
        out.write(cv2.resize(frame, PROCESSING_RESOLUTION))
        frame_count += 1

    # Liberar recursos
    cap.release()
    out.release()
    os.unlink(tmp_path)
    ocr_executor.shutdown()

    return {
        "processed_video": output_path,
        "detected_texts": list(set(detected_texts))
    }

def process_plate(plate_img, track_id):
    try:
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        ocr_result = reader.readtext(gray, detail=0, paragraph=True)
        plate_text = re.sub(r'[^A-Z0-9]', '', ''.join(ocr_result).upper())
        return plate_text, track_id
    except:
        return None, track_id

def draw_optimized_results(frame, results, last_valid_plates):
    if results is None:
        return frame
    
    for result in results:
        for box in result.boxes:
            if box.id is None:
                continue
                
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
            
            plate_text = last_valid_plates.get(int(box.id), "")
            if plate_text:
                cv2.putText(frame, plate_text, (x1, y1-10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0), 1)
    
    return frame

def preprocess_for_detection(img):
    # Reducción de resolución y mejora de contraste
    img = cv2.resize(img, PROCESSING_RESOLUTION, interpolation=cv2.INTER_LINEAR)
    
    # Solo CLAHE para optimizar rendimiento
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4,4))
    l = clahe.apply(l)
    
    return cv2.cvtColor(cv2.merge((l, a, b)), cv2.COLOR_LAB2BGR)

def validate_plate(text: str) -> bool:
    return 6 <= len(text) <= 8 and any(c.isdigit() for c in text)