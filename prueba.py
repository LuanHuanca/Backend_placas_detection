import torch
import cv2
import os

# Configuración
video_path = 'video.mp4'  # Ruta al video de entrada
output_dir = 'resultados'  # Directorio para guardar resultados
os.makedirs(output_dir, exist_ok=True)

# Cargar modelo YOLOv5n preentrenado
model = torch.hub.load('ultralytics/yolov5', 'custom', path='keremberke/yolov5n-license-plate', force_reload=True)
model.conf = 0.25  # Umbral de confianza
model.iou = 0.45   # Umbral de IoU

# Abrir video
cap = cv2.VideoCapture(video_path)
frame_id = 0
plate_count = 0

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    frame_id += 1
    results = model(frame)
    detections = results.xyxy[0]  # Detecciones en formato [x1, y1, x2, y2, conf, cls]

    for *box, conf, cls in detections:
        x1, y1, x2, y2 = map(int, box)
        # Recortar placa
        plate_img = frame[y1:y2, x1:x2]
        plate_filename = os.path.join(output_dir, f'placa_{frame_id}_{plate_count}.jpg')
        cv2.imwrite(plate_filename, plate_img)

        # Recortar vehículo (área más grande alrededor de la placa)
        h, w, _ = frame.shape
        margin = 50  # Margen adicional alrededor de la placa
        vx1 = max(x1 - margin, 0)
        vy1 = max(y1 - margin, 0)
        vx2 = min(x2 + margin, w)
        vy2 = min(y2 + margin, h)
        vehicle_img = frame[vy1:vy2, vx1:vx2]
        vehicle_filename = os.path.join(output_dir, f'vehiculo_{frame_id}_{plate_count}.jpg')
        cv2.imwrite(vehicle_filename, vehicle_img)

        plate_count += 1

cap.release()
print(f'Proceso completado. Se guardaron {plate_count} placas y vehículos en "{output_dir}".')
