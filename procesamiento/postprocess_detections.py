import os
import json
from collections import defaultdict
from tqdm import tqdm

def split_detections_by_level(global_json_path, output_dir):
    """
    Divide un archivo JSON de detecciones globales en archivos JSON separados por nivel.
    Cada nivel corresponde a una imagen original de la que se derivaron los crops.

    Parameters:
    global_json_path (str): Ruta al archivo JSON que contiene todas las detecciones.
    output_dir (str): Directorio donde se guardarán los JSONs por nivel.
    """
    # Crear el directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Cargar el JSON global
    with open(global_json_path, 'r') as f:
        global_detections = json.load(f)

    # Usar un diccionario para agrupar detecciones por nivel
    detections_by_level = defaultdict(list)

    # Agrupar las detecciones por el nombre base de la imagen original
    for detection in global_detections:
        # Extraer el nombre base, eliminando las coordenadas del crop (ejemplo: "P28_323_rgb")
        crop_image_name = detection["image"]
        base_name = "_".join(crop_image_name.split("_")[:-2])  # Elimina las últimas dos partes que son las coordenadas

        # Añadir la detección a la lista correspondiente a ese nivel
        detections_by_level[base_name].append(detection)

    # Guardar cada grupo de detecciones en un archivo JSON separado
    for base_name, detections in detections_by_level.items():
        output_path = os.path.join(output_dir, f"{base_name}.json")
        with open(output_path, 'w') as f:
            json.dump(detections, f, indent=4)
        print(f"Guardado: {output_path}")

def remap_detections_to_original(json_dir, output_dir):
    """
    Ajusta las coordenadas de las detecciones en los crops para mapearlas de vuelta a la imagen original,
    manteniendo una referencia al crop original en el campo 'original_crop'.
    
    Parameters:
    json_dir (str): Directorio que contiene los archivos JSON de detecciones por nivel.
    output_dir (str): Directorio donde se guardarán los JSONs con las coordenadas remapeadas.
    image_size (int): Tamaño de los crops utilizados para las detecciones. Default: 640.
    """
    # Crear el directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Listar todos los archivos JSON en el directorio de detecciones por nivel
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]

    # Procesar cada archivo JSON con una barra de progreso
    for json_file in tqdm(json_files, desc="Remapeando detecciones", unit="archivo"):
        json_path = os.path.join(json_dir, json_file)

        # Cargar las detecciones desde el archivo JSON
        with open(json_path, 'r') as f:
            detections = json.load(f)
        
        remapped_detections = []

        # Remapear cada detección a la imagen original
        for detection in detections:
            # Extraer el nombre del archivo del crop para obtener las coordenadas del offset
            crop_file = detection["image"]
            parts = crop_file.split("_")
            x_offset = int(parts[-2])  # Segundo último elemento del nombre es el offset X
            y_offset = int(parts[-1].replace(".png", ""))  # Último elemento es el offset Y

            # Recuperar las coordenadas originales
            x_center_original = detection["x_center"] + x_offset
            y_center_original = detection["y_center"] + y_offset

            # Guardar las coordenadas remapeadas junto con los demás detalles de la detección
            remapped_detection = {
                "image": json_file.replace(".json", ""),  # Nombre de la imagen original (sin el crop)
                "original_crop": crop_file,  # Referencia al archivo del crop original
                "x_center": x_center_original,
                "y_center": y_center_original,
                "width": detection["width"],
                "height": detection["height"],
                "confidence": detection["confidence"],
                "class": detection["class"]
            }
            remapped_detections.append(remapped_detection)

        # Guardar el archivo JSON con las coordenadas remapeadas
        output_json_path = os.path.join(output_dir, json_file)
        with open(output_json_path, 'w') as f:
            json.dump(remapped_detections, f, indent=4)
        print(f"Guardado: {output_json_path}")

# Ejemplo de uso
# split_detections_by_level("data/P28/detections.json", "data/P28/level_detections")

# Ejemplo de uso
# remap_detections_to_original("data/P28/level_detections", "data/P28/remapped_detections")