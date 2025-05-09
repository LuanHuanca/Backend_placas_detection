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

# Configuración especializada
CHAR_WHITELIST = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-'
REQUIRED_LENGTH = 5  # Longitud total sin contar guiones
CHAR_REPLACEMENTS = {
    'O': '0', 'I': '1', 'Z': '2', 'S': '5',
    'B': '8', 'D': '0', 'T': '7', 'G': '6'
}

def enhance_plate_image(plate_img):
    """Mejora la imagen de la placa para OCR"""
    # Convertir a escala de grises
    gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
    
    # Reducción de ruido
    denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)
    
    # Mejora de contraste
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    contrast = clahe.apply(denoised)
    
    # Binarización adaptativa
    thresh = cv2.adaptiveThreshold(contrast, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                  cv2.THRESH_BINARY, 11, 2)
    
    # Mejorar caracteres
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
    processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return processed

def correct_ocr_text(text):
    """Corrige errores comunes de OCR"""
    # Normalización básica
    text = text.upper().replace(" ", "").replace(".", "-")
    
    # Reemplazo de caracteres
    corrected = []
    for char in text:
        corrected.append(CHAR_REPLACEMENTS.get(char, char))
    
    # Unir y limpiar
    return ''.join(corrected)

def validate_plate_format(text):
    # Limpiar y normalizar
    clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())  # Eliminar todo excepto letras y números
    
    # Longitud esperada de placas: típicamente entre 6 y 8 caracteres
    if 6 <= len(clean_text) <= 8:
        return True
    return False
