import os
import numpy as np
import rasterio
import geopandas as gpd
import matplotlib.pyplot as plt
from tqdm import tqdm
import json
from tree_identification import filter_heatmap, apply_dbscan, calculate_cluster_centers

def convert_shapefile_to_image_coords(image_path, shapefile_path):
    """
    Convierte los puntos de un shapefile a coordenadas de imagen utilizando la georreferenciación del GeoTIFF.
    """
    with rasterio.open(image_path) as dataset:
        transform = dataset.transform
        crs = dataset.crs

    gdf = gpd.read_file(shapefile_path)
    if gdf.crs != crs:
        gdf = gdf.to_crs(crs)
    
    points_in_image_coords = []
    for point in gdf.geometry:
        x, y = point.x, point.y
        row, col = rasterio.transform.rowcol(transform, x, y)
        points_in_image_coords.append({"x": int(col), "y": int(row)})

    return points_in_image_coords

def accumulate_points_with_unique_count(points, coverage_grid, point_size=3):
    """
    Acumula los puntos en una capa temporal por cada nivel, incrementando el valor en una vecindad
    alrededor de cada punto, pero limitando la acumulación a +1 por cada nivel.
    """
    temp_grid = np.zeros_like(coverage_grid, dtype=int)
    
    for point in points:
        x, y = point["x"], point["y"]
        
        # Crear una ventana alrededor del punto para incrementar su valor
        x_min = max(0, x - point_size // 2)
        x_max = min(coverage_grid.shape[1], x + point_size // 2 + 1)
        y_min = max(0, y - point_size // 2)
        y_max = min(coverage_grid.shape[0], y + point_size // 2 + 1)
        
        # Marcar la vecindad en el grid temporal
        temp_grid[y_min:y_max, x_min:x_max] = 1

    # Acumular el resultado en el grid de cobertura
    coverage_grid += temp_grid

def build_heatmap_from_shapefiles(tiff_dir, shapefile_dir, min_level=None, max_level=None, point_size=3, show=False):
    """
    Construye un heatmap acumulativo a partir de shapefiles y archivos TIFF dentro de un rango de niveles.
    
    Parameters:
    tiff_dir (str): Directorio que contiene las imágenes GeoTIFF.
    shapefile_dir (str): Directorio que contiene los archivos .shp.
    min_level (int, optional): Nivel mínimo de archivos a procesar.
    max_level (int, optional): Nivel máximo de archivos a procesar.
    point_size (int): Tamaño de la vecindad alrededor de cada punto en el heatmap.
    show (bool): Si True, muestra el heatmap generado.
    
    Returns:
    numpy.ndarray: Heatmap acumulativo de los puntos.
    """
    sample_tiff = next((f for f in os.listdir(tiff_dir) if f.lower().endswith(('.tif', '.tiff'))), None)
    if sample_tiff is None:
        raise ValueError("No se encontraron archivos TIFF en el directorio especificado.")
    
    with rasterio.open(os.path.join(tiff_dir, sample_tiff)) as dataset:
        image_shape = (dataset.height, dataset.width)
    
    heatmap = np.zeros(image_shape, dtype=int)

    # Listar solo los archivos TIFF que tienen un shapefile correspondiente
    tiff_files = [
        f for f in os.listdir(tiff_dir)
        if f.lower().endswith(('.tif', '.tiff')) and os.path.exists(os.path.join(shapefile_dir, f"{os.path.splitext(f)[0]}.shp"))
    ]

    # Aplicar filtro de niveles si están definidos
    if min_level is not None or max_level is not None:
        tiff_files = [
            tiff_file for tiff_file in tiff_files
            if min_level <= int(os.path.splitext(tiff_file)[0].split('_')[1]) <= max_level
        ]

    # Procesar cada TIFF que tenga shapefile correspondiente
    for tiff_file in tqdm(tiff_files, desc="Procesando niveles", unit="nivel"):
        tiff_path = os.path.join(tiff_dir, tiff_file)
        base_name = os.path.splitext(tiff_file)[0]
        shapefile_path = os.path.join(shapefile_dir, f"{base_name}.shp")

        points = convert_shapefile_to_image_coords(tiff_path, shapefile_path)
        accumulate_points_with_unique_count(points, heatmap, point_size=point_size)
    
    if show:
        plt.figure(figsize=(10, 8))
        plt.imshow(heatmap, cmap='hot', interpolation='nearest')
        plt.colorbar(label='Frecuencia de Puntos')
        plt.title('Heatmap Acumulativo de Detección de Árboles')
        plt.xlabel('X')
        plt.ylabel('Y')
        plt.gca().invert_yaxis()
        plt.show()

    return heatmap

def create_ground_truth_tree_positions(tiff_dir, shapefile_dir, output_path=None, min_level=None, max_level=None, point_size=20, min_percentage=0.105, dbscan_eps=50, dbscan_min_samples=200, show_steps=False):
    """
    Crea posiciones de árboles de verdad de terreno (ground truth) a partir de shapefiles y archivos TIFF,
    aplicando un filtro y DBSCAN para detectar centros de árboles.
    
    Parameters:
    tiff_dir (str): Directorio que contiene las imágenes GeoTIFF.
    shapefile_dir (str): Directorio que contiene los archivos .shp.
    output_path (str, optional): Ruta para guardar los centros detectados en un archivo JSON.
    min_level (int, optional): Nivel mínimo de archivos a procesar.
    max_level (int, optional): Nivel máximo de archivos a procesar.
    point_size (int): Tamaño de la vecindad alrededor de cada punto en el heatmap.
    min_percentage (float): Porcentaje mínimo del valor máximo para el filtrado.
    dbscan_eps (float): Máxima distancia entre puntos en el mismo cluster en DBSCAN.
    dbscan_min_samples (int): Número mínimo de muestras en un cluster para DBSCAN.
    show_steps (bool): Si True, muestra los resultados de cada paso.
    
    Returns:
    List[Tuple[int, int]]: Lista de posiciones centrales (x, y) de los árboles detectados.
    """
    # Paso 1: Crear el heatmap acumulativo a partir de los shapefiles
    heatmap_gt = build_heatmap_from_shapefiles(tiff_dir, shapefile_dir, min_level=min_level, max_level=max_level, point_size=point_size, show=show_steps)
    
    # Paso 2: Filtrar el heatmap usando un porcentaje del valor máximo
    filtered_heatmap_gt = filter_heatmap(heatmap_gt, min_percentage=min_percentage, show=show_steps)
    
    # Paso 3: Aplicar DBSCAN para el clustering
    non_zero_coords_gt, labels_gt = apply_dbscan(filtered_heatmap_gt, eps=dbscan_eps, min_samples=dbscan_min_samples, show=show_steps)
    
    # Paso 4: Calcular los centros de cada cluster detectado
    centers_gt = calculate_cluster_centers(filtered_heatmap_gt, non_zero_coords_gt, labels_gt, show=show_steps)
    
    # Guardar el resultado en un archivo JSON si se proporciona una ruta de salida
    if output_path:
        with open(output_path, 'w') as f:
            json.dump(centers_gt, f, indent=4)
        print(f"Centros de árboles guardados en: {output_path}")
    
    return centers_gt

# Ejemplo de uso
if __name__ == "__main__":
    finca = 'P9'
    tiff_dir = f'/home/enrique/Desktop/VARIOS/TFM/tfm-identificacion-troncos/data/{finca}/1cm_maxint'
    shapefile_dir = f'/home/enrique/Desktop/VARIOS/TFM/tfm-identificacion-troncos/data/manual_selection/{finca}'
    output_path = f'/home/enrique/Desktop/VARIOS/TFM/tfm-identificacion-troncos/data/{finca}/results/tree_centers_ground_truth.json'
    
    # Crear el ground truth de posiciones de árboles y guardarlo en el output_path
    create_ground_truth_tree_positions(
        tiff_dir=tiff_dir,
        shapefile_dir=shapefile_dir,
        min_level=100,
        max_level=250,
        point_size=20,
        min_percentage=0.105,
        dbscan_eps=50,
        dbscan_min_samples=200,
        output_path=output_path,
        show_steps=False
    )