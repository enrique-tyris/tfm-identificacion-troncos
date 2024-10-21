import os
import json
import rasterio
import geopandas as gpd
import cv2
from tqdm import tqdm

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
        # Convertir coordenadas geográficas a coordenadas de fila y columna de imagen
        row, col = rasterio.transform.rowcol(transform, x, y)
        points_in_image_coords.append({"x": int(col), "y": int(row)})

    # Guardar las coordenadas en un archivo JSON
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, 'w') as json_file:
        json.dump(points_in_image_coords, json_file, indent=4)
    
    print(f"Coordenadas de los puntos guardadas en: {output_json_path}")

def draw_points_on_image_opencv(png_image_path, points_json_path, output_image_path):
    """
    Dibuja puntos en una imagen PNG utilizando coordenadas guardadas en un archivo JSON con OpenCV.
    
    Parameters:
    png_image_path (str): Ruta a la imagen PNG.
    points_json_path (str): Ruta al archivo JSON que contiene las coordenadas de los puntos.
    output_image_path (str): Ruta para guardar la imagen resultante con los puntos dibujados.
    """
    # Cargar la imagen PNG con OpenCV
    img = cv2.imread(png_image_path)

    # Cargar las coordenadas de los puntos desde el archivo JSON
    with open(points_json_path, 'r') as json_file:
        points = json.load(json_file)

    # Dibujar cada punto en la imagen como un pequeño círculo rojo
    for point in points:
        x, y = point["x"], point["y"]
        cv2.circle(img, (x, y), radius=5, color=(0, 0, 255), thickness=-1)  # Rojo en formato BGR

    # Guardar la imagen resultante
    cv2.imwrite(output_image_path, img)
    print(f"Imagen con puntos guardada en: {output_image_path}")

def process_directory_and_draw_points(tiff_dir, shapefile_dir, json_output_dir, png_image_dir, output_image_dir):
    """
    Procesa una carpeta de imágenes TIFF y shapefiles, y dibuja los puntos en las imágenes PNG correspondientes.
    
    Parameters:
    tiff_dir (str): Directorio que contiene las imágenes GeoTIFF.
    shapefile_dir (str): Directorio que contiene los archivos .shp.
    json_output_dir (str): Directorio donde se guardarán los archivos JSON con las coordenadas de los puntos.
    png_image_dir (str): Directorio que contiene las imágenes PNG donde se dibujarán los puntos.
    output_image_dir (str): Directorio donde se guardarán las imágenes PNG con los puntos dibujados.
    """
    # Crear los directorios de salida si no existen
    os.makedirs(json_output_dir, exist_ok=True)
    os.makedirs(output_image_dir, exist_ok=True)

    # Listar todas las imágenes GeoTIFF en el directorio de entrada
    tiff_files = [f for f in os.listdir(tiff_dir) if f.lower().endswith(('.tif', '.tiff'))]

    # Procesar cada archivo TIFF
    for tiff_file in tqdm(tiff_files, desc="Procesando archivos", unit="archivo"):
        # Construir las rutas a los archivos de imagen y shapefile
        tiff_path = os.path.join(tiff_dir, tiff_file)
        base_name = os.path.splitext(tiff_file)[0]
        shapefile_path = os.path.join(shapefile_dir, f"{base_name}.shp")
        json_output_path = os.path.join(json_output_dir, f"{base_name}_points.json")
        png_image_path = os.path.join(png_image_dir, f"{base_name}.png")
        output_image_path = os.path.join(output_image_dir, f"{base_name}_points_overlay.png")

        # Verificar que el shapefile y la imagen PNG correspondientes existan
        if os.path.exists(shapefile_path) and os.path.exists(png_image_path):
            # Convertir puntos del shapefile a coordenadas de imagen y guardarlos en JSON
            convert_shapefile_to_image_coords(tiff_path, shapefile_path, json_output_path)
            
            # Dibujar los puntos en la imagen PNG usando las coordenadas guardadas en el JSON
            draw_points_on_image_opencv(png_image_path, json_output_path, output_image_path)
        else:
            print(f"Shapefile o imagen PNG no encontrados para {tiff_file}. Se omite este archivo.")

# Ejemplo de uso
if __name__ == "__main__":
    finca = 'P8'
    
    tiff_dir = f'/home/enrique/Desktop/VARIOS/TFM/tfm-identificacion-troncos/data/{finca}/1cm_maxint'  # Carpeta que contiene las imágenes GeoTIFF
    shapefile_dir = f'/home/enrique/Desktop/VARIOS/TFM/tfm-identificacion-troncos/data/manual_selection/{finca}'  # Carpeta que contiene los archivos .shp
    json_output_dir = f'/home/enrique/Desktop/VARIOS/TFM/tfm-identificacion-troncos/data/manual_selection/{finca}_json'  # Carpeta para guardar los archivos JSON
    png_image_dir = f'/home/enrique/Desktop/VARIOS/TFM/tfm-identificacion-troncos/data/{finca}/png_channels/maxint'  # Carpeta que contiene las imágenes PNG
    output_image_dir = f'/home/enrique/Desktop/VARIOS/TFM/tfm-identificacion-troncos/data/{finca}/tiff_painted_with_shapefile_labels'  # Carpeta para guardar las imágenes resultantes con puntos dibujados

    process_directory_and_draw_points(tiff_dir, shapefile_dir, json_output_dir, png_image_dir, output_image_dir)