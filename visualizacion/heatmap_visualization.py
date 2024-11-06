import json
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from tqdm import tqdm
from PIL import Image

def draw_coverage_heatmap(json_dir, image_dir, output_dir=None, min_level=None, max_level=None):
    """
    Crea y guarda (o muestra) un heatmap de cobertura de detecciones de BBoxes a partir de archivos JSON.
    Utiliza la primera imagen del directorio de imágenes para determinar el tamaño de la finca.
    Opcionalmente, limita el rango de niveles a procesar y ajusta el nombre del archivo de salida.
    
    Parameters:
    json_dir (str): Directorio que contiene los archivos JSON de detecciones.
    image_dir (str): Directorio que contiene las imágenes para determinar el tamaño de la finca.
    output_dir (str, optional): Directorio donde se guardará la visualización del heatmap.
                                Si es None, se mostrará en pantalla.
    min_level (int, optional): Número mínimo de nivel a procesar. Si es None, se procesan todos los niveles desde el principio.
    max_level (int, optional): Número máximo de nivel a procesar. Si es None, se procesan todos los niveles hasta el final.
    """
    def get_image_shape(image_dir):
        image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff'))]
        if not image_files:
            raise ValueError("No se encontraron imágenes en el directorio proporcionado.")
        
        # Cargar la primera imagen para obtener el tamaño
        first_image_path = os.path.join(image_dir, image_files[0])
        with Image.open(first_image_path) as img:
            return img.size[::-1]  # PIL retorna (ancho, altura), pero lo invertimos a (altura, ancho)
    
    def create_coverage_grid(json_dir, image_shape, min_level=None, max_level=None):
        coverage_grid = np.zeros(image_shape, dtype=int)
        json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]
        
        # Filtrar archivos por nivel si se han definido min_level y/o max_level
        if min_level is not None or max_level is not None:
            filtered_files = []
            for json_file in json_files:
                parts = json_file.split('_')
                try:
                    level_number = int(parts[1])  # Tomar el segundo elemento que corresponde al número
                    if (min_level is None or level_number >= min_level) and (max_level is None or level_number <= max_level):
                        filtered_files.append(json_file)
                except ValueError:
                    continue
            json_files = filtered_files

        # Procesar cada archivo JSON
        for json_file in tqdm(json_files, desc="Procesando niveles", unit="nivel"):
            json_path = os.path.join(json_dir, json_file)
            with open(json_path, 'r') as f:
                detections = json.load(f)
            
            # Crear un grid temporal para el nivel actual
            temp_grid = np.zeros(image_shape, dtype=int)

            # Marcar en el grid temporal los puntos cubiertos por BBoxes
            for detection in detections:
                x_center = detection['x_center']
                y_center = detection['y_center']
                width = detection['width']
                height = detection['height']
                
                x_min = int(x_center - (width / 2))
                y_min = int(y_center - (height / 2))
                x_max = int(x_center + (width / 2))
                y_max = int(y_center + (height / 2))
                
                # Asegurarse de que las coordenadas estén dentro de los límites de la imagen
                x_min = max(0, x_min)
                y_min = max(0, y_min)
                x_max = min(image_shape[1], x_max)
                y_max = min(image_shape[0], y_max)
                
                temp_grid[y_min:y_max, x_min:x_max] = 1

            coverage_grid += temp_grid

        return coverage_grid

    def draw_coverage_grid(coverage_grid, output_path=None):
        plt.figure(figsize=(10, 8))
        plt.imshow(coverage_grid, cmap='hot', interpolation='nearest')
        plt.colorbar(label='Frecuencia de Cobertura')
        plt.title('Heatmap de Cobertura de Detecciones')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.gca().invert_yaxis()  # Invertir eje Y
        plt.tight_layout()

        if output_path:
            plt.savefig(output_path)
            plt.close()
            print(f"Heatmap guardado en: {output_path}")
        else:
            plt.show()
            print("Heatmap mostrado en pantalla.")

    # Obtener el tamaño de la imagen desde la primera imagen del directorio
    image_shape = get_image_shape(image_dir)
    
    # Crear el grid de cobertura
    coverage_grid = create_coverage_grid(json_dir, image_shape, min_level, max_level)
    
    # Crear el nombre del archivo de salida según el rango de niveles
    if min_level is not None or max_level is not None:
        level_info = f"_minlevel_{min_level or 'min'}_maxlevel_{max_level or 'max'}"
    else:
        level_info = ""

    output_path = os.path.join(output_dir, f"detections_heatmap{level_info}.png") if output_dir else None
    
    # Guardar o representar la visualización del heatmap
    draw_coverage_grid(coverage_grid, output_path)

# Ejemplo de uso:
# draw_coverage_heatmap("data/P28/detections/remapped_detections", "data/P28/rgb_images", "data/P28/visualization/", min_level=75, max_level=185)
# O sin output_dir para mostrar el heatmap
# draw_coverage_heatmap("data/P28/detections/remapped_detections", "data/P28/rgb_images", min_level=75, max_level=185)