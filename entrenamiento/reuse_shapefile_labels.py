import os
import json
import rasterio
import geopandas as gpd

def convert_shapefile_to_image_coords(image_path, shapefile_path, output_json_path):
    """
    Convierte los puntos de un shapefile a coordenadas de imagen utilizando la georreferenciación del GeoTIFF.
    
    Parameters:
    image_path (str): Ruta a la imagen GeoTIFF.
    shapefile_path (str): Ruta al archivo .shp que contiene los puntos.
    output_json_path (str): Ruta para guardar el archivo JSON con las coordenadas de los puntos.
    """
    # Leer la imagen GeoTIFF
    with rasterio.open(image_path) as dataset:
        transform = dataset.transform  # Transformación geoespacial del raster
        crs = dataset.crs

    # Leer los puntos del shapefile usando geopandas
    gdf = gpd.read_file(shapefile_path)

    # Verificar si el shapefile y el GeoTIFF tienen el mismo sistema de coordenadas
    if gdf.crs != crs:
        gdf = gdf.to_crs(crs)  # Reproyectar si es necesario

    # Convertir las coordenadas de los puntos a coordenadas de píxeles
    points_in_image_coords = []
    for point in gdf.geometry:
        x, y = point.x, point.y
        row, col = ~transform * (x, y)  # Inverso de la transformación para obtener filas y columnas
        points_in_image_coords.append({"x": int(col), "y": int(row)})

    # Guardar las coordenadas en un archivo JSON
    with open(output_json_path, 'w') as json_file:
        json.dump(points_in_image_coords, json_file, indent=4)
    
    print(f"Coordenadas de los puntos guardadas en: {output_json_path}")

# Ejemplo de uso
image_path = 'path/to/your/image.tif'
shapefile_path = 'path/to/your/shapefile.shp'
output_json_path = 'path/to/output/points.json'

convert_shapefile_to_image_coords(image_path, shapefile_path, output_json_path)