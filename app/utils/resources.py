# app/utils/resources.py
from ultralytics import YOLO
import easyocr

# Cargar una sola vez
model = YOLO("app/models/license_plate_detector.pt")
reader = easyocr.Reader(['en'])

print("📦 Modelo y lector OCR cargados exitosamente")
