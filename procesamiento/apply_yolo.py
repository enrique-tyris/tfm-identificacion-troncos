import os
import json
from ultralytics import YOLO
from tqdm import tqdm

def load_yolo_model(model_path):
    """
    Carga un modelo YOLO previamente entrenado.

    Parameters:
    model_path (str): Ruta al archivo del modelo YOLO entrenado (.pt).

    Returns:
    YOLO: Modelo YOLO cargado.
    """
    model = YOLO(model_path)
    return model

def apply_yolo_to_crops(crop_dir, output_json_path, model_path):
    """
    Aplica el modelo YOLO a cada crop en un directorio y guarda los resultados en un JSON.

    Parameters:
    crop_dir (str): Directorio que contiene las imágenes de los crops.
    output_json_path (str): Ruta donde se guardará el archivo JSON con los resultados.
    model_path (str): Ruta al archivo del modelo YOLO entrenado (.pt).
    """
    # Crear la carpeta de salida si no existe
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    # Cargar el modelo YOLO
    model = load_yolo_model(model_path)

    # Listar todos los archivos en el directorio de crops
    crop_files = [f for f in os.listdir(crop_dir) if f.endswith('.png')]

    # Lista para almacenar todos los resultados
    results = []

    # Procesar cada crop con una barra de progreso
    for crop_file in tqdm(crop_files, desc="Aplicando YOLO a crops", unit="imagen"):
        crop_path = os.path.join(crop_dir, crop_file)

        # Realizar la predicción con YOLO
        preds = model(crop_path)

        # Extraer las detecciones
        for result in preds:
            boxes = result.boxes  # Las cajas detectadas

            # Recorrer cada detección y guardar la información relevante
            for box in boxes:
                # Extraer coordenadas y detalles de la detección
                x_center, y_center, width, height = box.xywh[0]  # x_center, y_center, width, height
                confidence = box.conf[0]  # Confianza de la detección
                cls = int(box.cls[0])  # Clase de la detección

                # Convertir a formato de JSON
                detection_result = {
                    "image": crop_file,
                    "x_center": float(x_center),
                    "y_center": float(y_center),
                    "width": float(width),
                    "height": float(height),
                    "confidence": float(confidence),
                    "class": cls
                }
                results.append(detection_result)

    # Guardar todos los resultados en un archivo JSON
    with open(output_json_path, 'w') as json_file:
        json.dump(results, json_file, indent=4)

    print(f"Resultados guardados en {output_json_path}")

# Ejemplo de uso
# apply_yolo_to_crops("data/P28/crop_images", "data/P28/detections/detections.json", "path/to/your/model.pt")