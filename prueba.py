from ultralytics import YOLO
import cv2
import easyocr
import re


# Carga el modelo de detección de placas
model = YOLO("app/models/license_plate_detector.pt")

# Inicializa el lector OCR
reader = easyocr.Reader(['en'])

# Carga la imagen
img = cv2.imread("auto3.jpeg")

# Detecta las placas
results = model(img)

# Crea una copia de la imagen para dibujar los resultados
output_img = img.copy()

# Procesa cada placa detectada
for result in results:
    for box in result.boxes:
        # Obtiene las coordenadas de la placa
        x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
        
        # Recorta la región de la placa
        plate_img = img[y1:y2, x1:x2]
        
        # Preprocesamiento para OCR
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        
        # Aplica OCR
        ocr_result = reader.readtext(gray)
        
        # Procesa el texto detectado
        plate_text = ""
        for detection in ocr_result:
            text = detection[1]
            # Limpia el texto (solo letras mayúsculas y números)
            clean_text = re.sub(r'[^A-Z0-9]', '', text.upper())
            if len(clean_text) > 2:  # Ignora textos muy cortos
                plate_text += clean_text + " "
        
        # Dibuja el rectángulo y el texto en la imagen de salida
        cv2.rectangle(output_img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        if plate_text:
            cv2.putText(output_img, plate_text.strip(), (x1, y1-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

# Muestra los resultados
cv2.imshow("Detección y reconocimiento", output_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

# Imprime los textos reconocidos en consola
print("\nTextos reconocidos en las placas:")
for i, result in enumerate(results):
    for box in result.boxes:
        plate_img = img[int(box.xyxy[0][1]):int(box.xyxy[0][3]), 
                    int(box.xyxy[0][0]):int(box.xyxy[0][2])]
        gray = cv2.cvtColor(plate_img, cv2.COLOR_BGR2GRAY)
        ocr_result = reader.readtext(gray)
        print(f"Placa {i+1}:")
        for detection in ocr_result:
            print(f"  - Texto: {detection[1]} (confianza: {detection[2]:.2f})")