import pytesseract
import cv2
import easyocr
import re
from app.utils.resources import reader

PLACA_REGEX = re.compile(r'^[A-Z0-9]{1,2}-[A-Z0-9]{2}-[A-Z0-9]{3}$')

def extract_plate_text(image):
    # Preprocesamiento
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # OCR
    text = pytesseract.image_to_string(thresh, config="--psm 11")
    return text.strip()

# Expresión regular obligatoria: formato como AB-12-CDE

def ocr_placa_optimizado(plate_img):
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Primera pasada OCR
    ocr_results = reader.readtext(thresh)
    for result in ocr_results:
        text = result[1].upper()
        text = re.sub(r'[^A-Z0-9\-]', '', text)
        # Si no tiene los dos guiones, intenta reconstruir
        if text.count("-") != 2:
            text = text.replace(" ", "")
            if len(text) >= 7:
                text = f"{text[:2]}-{text[2:4]}-{text[4:7]}"
        if PLACA_REGEX.match(text):
            return text.strip()

    # Segunda pasada OCR
    ocr_results = reader.readtext(gray)
    for result in ocr_results:
        text = result[1].upper()
        text = re.sub(r'[^A-Z0-9\-]', '', text)
        if text.count("-") != 2:
            text = text.replace(" ", "")
            if len(text) >= 7:
                text = f"{text[:2]}-{text[2:4]}-{text[4:7]}"
        if PLACA_REGEX.match(text):
            return text.strip()

    return ""
