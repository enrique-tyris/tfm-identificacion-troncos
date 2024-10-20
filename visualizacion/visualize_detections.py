import json
import cv2
import os
from tqdm import tqdm

def draw_all_detections(image_dir, json_dir, output_dir):
    """
    Itera sobre todas las imágenes y sus JSON correspondientes para dibujar las BBoxes.
    
    Parameters:
    image_dir (str): Directorio que contiene las imágenes RGB.
    json_dir (str): Directorio que contiene los archivos JSON de detecciones.
    output_dir (str): Directorio donde se guardarán las imágenes con BBoxes dibujadas.
    """
    # Crear el directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Listar todas las imágenes en el directorio de imágenes
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]

    # Procesar cada imagen con una barra de progreso
    for image_file in tqdm(image_files, desc="Procesando imágenes y JSONs", unit="imagen"):
        # Construir la ruta completa de la imagen y el archivo JSON correspondiente
        image_path = os.path.join(image_dir, image_file)
        json_file = image_file.replace('.png', '.json')
        json_path = os.path.join(json_dir, json_file)
        
        # Verificar que el archivo JSON correspondiente exista
        if os.path.exists(json_path):
            # Construir la ruta de salida para la imagen con BBoxes dibujadas
            output_path = os.path.join(output_dir, image_file)
            
            # Dibujar las BBoxes y guardar la imagen
            plot_detections_with_opencv(image_path, json_path, output_path)
        else:
            print(f"Archivo JSON no encontrado para la imagen: {image_file}")

def plot_detections_with_opencv(image_path, json_path, output_path):
    """
    Muestra una imagen RGB y dibuja todas las bounding boxes (BBoxes) a partir de un archivo JSON utilizando OpenCV.
    
    Parameters:
    image_path (str): Ruta de la imagen RGB.
    json_path (str): Ruta del archivo JSON que contiene las detecciones.
    output_path (str): Ruta para guardar la imagen con las BBoxes dibujadas.
    """
    # Cargar la imagen con OpenCV
    img = cv2.imread(image_path)
    
    # Cargar las detecciones desde el archivo JSON
    with open(json_path, 'r') as f:
        detections = json.load(f)

    # Dibujar cada BBox
    for detection in detections:
        x_center = detection['x_center']
        y_center = detection['y_center']
        width = detection['width']
        height = detection['height']
        confidence = detection['confidence']

        # Calcular las esquinas del BBox
        x_min = int(x_center - (width / 2))
        y_min = int(y_center - (height / 2))
        x_max = int(x_center + (width / 2))
        y_max = int(y_center + (height / 2))

        # Dibujar el rectángulo del BBox
        cv2.rectangle(img, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)  # Rojo

        # Añadir el texto de la confianza
        label = f"Conf: {confidence:.2f}"
        cv2.putText(img, label, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2, cv2.LINE_AA)

    # Guardar la imagen con las BBoxes dibujadas
    cv2.imwrite(output_path, img)
    print(f"Imagen con BBoxes guardada en: {output_path}")

# Ejemplo de uso:
# draw_all_detections("data/P28/rgb_images", "data/P28/remapped_detections", "data/P28/output")