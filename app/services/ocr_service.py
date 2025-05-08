import pytesseract
import cv2

def extract_plate_text(image):
    # Preprocesamiento
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    
    # OCR
    text = pytesseract.image_to_string(thresh, config="--psm 11")
    return text.strip()