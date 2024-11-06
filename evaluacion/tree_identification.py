import json
import os
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from tqdm import tqdm
from PIL import Image

def create_heatmap(json_dir, image_dir, min_level=None, max_level=None, show=False):
    """
    Crea un heatmap acumulativo de detecciones de árboles a partir de archivos JSON.
    
    Parameters:
    json_dir (str): Directorio que contiene los archivos JSON de detecciones.
    image_dir (str): Directorio que contiene las imágenes para determinar el tamaño del heatmap.
    min_level (int, optional): Nivel mínimo de archivos JSON a procesar.
    max_level (int, optional): Nivel máximo de archivos JSON a procesar.
    show (bool): Si True, muestra el heatmap.
    """
    def get_image_shape(image_dir):
        image_files = [f for f in os.listdir(image_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff'))]
        if not image_files:
            raise ValueError("No se encontraron imágenes en el directorio proporcionado.")
        
        first_image_path = os.path.join(image_dir, image_files[0])
        with Image.open(first_image_path) as img:
            return img.size[::-1]  # PIL retorna (ancho, altura), pero lo invertimos a (altura, ancho)
    
    image_shape = get_image_shape(image_dir)
    coverage_grid = np.zeros(image_shape, dtype=int)
    json_files = [f for f in os.listdir(json_dir) if f.endswith('.json')]

    # Filtrar archivos JSON por nivel si min_level y/o max_level están definidos
    if min_level is not None or max_level is not None:
        json_files = [
            json_file for json_file in json_files 
            if min_level <= int(json_file.split('_')[1]) <= max_level
        ]

    for json_file in tqdm(json_files, desc="Procesando niveles", unit="nivel"):
        json_path = os.path.join(json_dir, json_file)
        with open(json_path, 'r') as f:
            detections = json.load(f)

        temp_grid = np.zeros(image_shape, dtype=int)
        for detection in detections:
            x_center = detection['x_center']
            y_center = detection['y_center']
            width = detection['width']
            height = detection['height']

            x_min = int(x_center - (width / 2))
            y_min = int(y_center - (height / 2))
            x_max = int(x_center + (width / 2))
            y_max = int(y_center + (height / 2))

            x_min = max(0, x_min)
            y_min = max(0, y_min)
            x_max = min(image_shape[1], x_max)
            y_max = min(image_shape[0], y_max)

            temp_grid[y_min:y_max, x_min:x_max] = 1

        coverage_grid += temp_grid
    
    if show:
        plt.figure(figsize=(10, 8))
        plt.imshow(coverage_grid, cmap='hot', interpolation='nearest')
        plt.colorbar(label='Frecuencia de Cobertura (filtrado)')
        plt.title('Heatmap Filtrado')
        plt.gca().invert_yaxis()  # Invertir eje Y
        plt.show()
        
    return coverage_grid

def filter_heatmap(heatmap, min_percentage=0.1, show=False):
    """
    Filtra un heatmap eliminando valores menores a un porcentaje del valor máximo.
    
    Parameters:
    heatmap (numpy.ndarray): Heatmap acumulativo a filtrar.
    min_percentage (float): Porcentaje del valor máximo para conservar en el heatmap (entre 0 y 1).
    show (bool): Si True, muestra el heatmap filtrado.
    """
    # Calcular el valor mínimo basado en el porcentaje del valor máximo del heatmap
    max_value = heatmap.max()
    min_value = max_value * min_percentage
    
    # Filtrar el heatmap aplicando el valor mínimo
    filtered_heatmap = np.where(heatmap >= min_value, heatmap, 0)
    
    # Visualizar el heatmap si se especifica
    if show:
        plt.figure(figsize=(10, 8))
        plt.imshow(filtered_heatmap, cmap='hot', interpolation='nearest')
        plt.colorbar(label='Frecuencia de Cobertura (filtrado)')
        plt.title('Heatmap Filtrado')
        plt.gca().invert_yaxis()  # Invertir eje Y
        plt.show()
        
    return filtered_heatmap

def apply_dbscan(filtered_heatmap, eps=3, min_samples=5, show=False):
    """
    Aplica el algoritmo DBSCAN en los píxeles no nulos del heatmap filtrado,
    excluyendo el ruido (etiqueta -1) en los resultados finales.
    
    Parameters:
    filtered_heatmap (numpy.ndarray): Heatmap filtrado.
    eps (float): Máxima distancia entre puntos en el mismo cluster en DBSCAN.
    min_samples (int): Número mínimo de muestras en un cluster para DBSCAN.
    show (bool): Si True, muestra los clusters encontrados sin el ruido.
    """
    non_zero_coords = np.argwhere(filtered_heatmap > 0)
    if len(non_zero_coords) == 0:
        print("No se encontraron píxeles después del filtrado.")
        return non_zero_coords, np.array([])

    # Aplicar DBSCAN en las coordenadas no nulas
    clustering = DBSCAN(eps=eps, min_samples=min_samples).fit(non_zero_coords)
    
    # Filtrar los puntos de ruido (etiqueta -1)
    mask = clustering.labels_ != -1
    filtered_coords = non_zero_coords[mask]
    filtered_labels = clustering.labels_[mask]
    
    if show:
        plt.figure(figsize=(6, 5))
        plt.scatter(filtered_coords[:, 1], filtered_coords[:, 0], c=filtered_labels, cmap='tab20b', s=10)
        plt.gca().invert_yaxis()
        plt.title('Clustering de Detección de Árboles (DBSCAN) - Sin Ruido')
        plt.colorbar(label='Etiqueta de Cluster')
        plt.gca().invert_yaxis()  # Invertir eje Y
        plt.show()
        
    return filtered_coords, filtered_labels

def calculate_cluster_centers(filtered_heatmap, non_zero_coords, labels, show=False):
    """
    Calcula el centro ponderado de cada cluster.
    
    Parameters:
    filtered_heatmap (numpy.ndarray): Heatmap filtrado.
    non_zero_coords (numpy.ndarray): Coordenadas no nulas en el heatmap filtrado.
    labels (numpy.ndarray): Etiquetas de cluster para las coordenadas no nulas.
    show (bool): Si True, muestra los centros de los clusters en el heatmap.
    """
    unique_labels = set(labels)
    centers = []
    
    for label in unique_labels:
        if label == -1:  # Ignorar el ruido
            continue
        
        cluster_coords = non_zero_coords[labels == label]
        cluster_values = filtered_heatmap[cluster_coords[:, 0], cluster_coords[:, 1]]
        
        total_weight = np.sum(cluster_values)
        center_x = int(np.sum(cluster_coords[:, 1] * cluster_values) / total_weight)
        center_y = int(np.sum(cluster_coords[:, 0] * cluster_values) / total_weight)
        
        centers.append((center_x, center_y))
    
    if show:
        plt.figure(figsize=(6, 5))
        plt.imshow(filtered_heatmap, cmap='hot', interpolation='nearest')
        plt.scatter([c[0] for c in centers], [c[1] for c in centers], color='blue', marker='x', s=100, label='Centro de Árbol')
        plt.gca().invert_yaxis()
        plt.title('Centros de los Árboles Detectados')
        plt.legend()
        plt.show()
        
    return centers

def detect_trees_from_heatmap(json_dir, image_dir, output_path=None, min_percentage=0.105, dbscan_eps=50, dbscan_min_samples=200, min_level=None, max_level=None, show_steps=False):
    """
    Detecta árboles en un heatmap utilizando filtrado, clustering y cálculo de centros.

    Parameters:
    json_dir (str): Directorio de detecciones JSON.
    image_dir (str): Directorio de imágenes de referencia para el tamaño del heatmap.
    output_path (str, optional): Ruta para guardar la lista de centros detectados. Si es None, no guarda.
    min_percentage (float): Porcentaje mínimo para el filtrado en relación al valor máximo del heatmap.
    dbscan_eps (float): Máxima distancia entre puntos en el mismo cluster en DBSCAN.
    dbscan_min_samples (int): Número mínimo de muestras en un cluster para DBSCAN.
    min_level (int, optional): Nivel mínimo de archivos JSON a procesar.
    max_level (int, optional): Nivel máximo de archivos JSON a procesar.
    show_steps (bool): Si True, muestra los resultados de cada paso.
    """
    heatmap = create_heatmap(json_dir, image_dir, min_level=min_level, max_level=max_level, show=show_steps)
    filtered_heatmap = filter_heatmap(heatmap, min_percentage=min_percentage, show=show_steps)
    non_zero_coords, labels = apply_dbscan(filtered_heatmap, eps=dbscan_eps, min_samples=dbscan_min_samples, show=show_steps)
    centers = calculate_cluster_centers(filtered_heatmap, non_zero_coords, labels, show=show_steps)

    # Guardar los centros detectados si se especifica output_path
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(centers, f, indent=4)
        print(f"Centros de árboles guardados en: {output_path}")

    return centers

# Ejemplo de uso:
# centers = detect_trees_from_heatmap("data/finca/detections/remapped_detections", "data/finca/rgb_images", "data/finca/detections/tree_centers.json", min_percentage=0.105, dbscan_eps=5, dbscan_min_samples=10, min_level=100, max_level=250, show_steps=True)