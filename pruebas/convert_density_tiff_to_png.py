import os
import numpy as np
import tifffile
from PIL import Image

def convert_density_tiff_to_png(input_dir, output_dir, desired_min=0, desired_max=2):
    """
    Convierte imágenes TIFF del canal de densidad a PNG, escalando los valores entre un rango deseado.
    
    Parameters:
    input_dir (str): Directorio de entrada que contiene las imágenes TIFF de densidad.
    output_dir (str): Directorio de salida donde se guardarán las imágenes PNG procesadas.
    desired_min (float): Valor mínimo deseado para la escala de la imagen.
    desired_max (float): Valor máximo deseado para la escala de la imagen.
    """
    # Crear el directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Listar los archivos TIFF en el directorio de entrada
    tiff_files = [f for f in os.listdir(input_dir) if f.endswith('.tif')]
    
    failed_conversions = []

    for tiff_file in tiff_files:
        tiff_path = os.path.join(input_dir, tiff_file)
        png_path = os.path.join(output_dir, tiff_file.replace('.tif', '.png'))
        
        try:
            # Leer la imagen TIFF
            img = tifffile.imread(tiff_path)
            
            # Clip y escalar los valores al rango deseado
            img_clipped = np.clip(img, desired_min, desired_max)
            img_scaled = ((img_clipped - desired_min) / (desired_max - desired_min)) * 255.0
            
            # Convertir a uint8
            img_scaled = img_scaled.astype(np.uint8)
            
            # Convertir a imagen PIL y guardar como PNG
            img_png = Image.fromarray(img_scaled)
            img_png.save(png_path)
            
            print(f"Processed and saved {png_path}")
        
        except Exception as e:
            print(f"Failed to process {tiff_path}: {e}")
            failed_conversions.append(tiff_path)

    # Mostrar un resumen de los archivos que fallaron
    if failed_conversions:
        print("\nFailed to convert the following files:")
        for failed_file in failed_conversions:
            print(failed_file)
    else:
        print("\nAll files processed successfully.")

# Ejemplo de uso:
# convert_density_tiff_to_png("data/P28/1cm_density", "data/P28/png_channels/density", 0, 2)