import os
from PIL import Image
import numpy as np
import tifffile
from tqdm import tqdm

def convert_tiff_to_png(input_dir, output_dir):
    """
    Convierte todas las imágenes .tif de una carpeta a .png y las guarda en la carpeta especificada.
    Convierte a formato uint8 para asegurarse de que las imágenes sean compatibles con PNG.
    
    Parameters:
    input_dir (str): Directorio de entrada que contiene las imágenes .tif.
    output_dir (str): Directorio de salida donde se guardarán las imágenes .png.
    """
    # Verificar que el directorio de salida exista, si no, crearlo
    os.makedirs(output_dir, exist_ok=True)
    
    # Listar todos los archivos .tif en el directorio de entrada
    tiff_files = [f for f in os.listdir(input_dir) if f.endswith('.tif')]
    
    # Iterar sobre los archivos .tif con tqdm para mostrar el progreso
    for tiff_file in tqdm(tiff_files, desc="Convirtiendo TIFF a PNG", unit="archivo"):
        # Ruta completa al archivo .tif
        tiff_path = os.path.join(input_dir, tiff_file)
        
        # Leer la imagen .tif y convertirla a uint8
        img = tifffile.imread(tiff_path).astype(np.uint8)
        
        # Convertir la imagen a un objeto PIL
        pil_img = Image.fromarray(img)
        
        # Nombre del archivo .png de salida
        png_file = os.path.splitext(tiff_file)[0] + ".png"
        png_path = os.path.join(output_dir, png_file)
        
        # Guardar la imagen en formato .png
        pil_img.save(png_path, "PNG")

# Uso en el main o en notebook
# convert_tiff_to_png("data/1cm_meanint", "data/png_channels/meanint")
# convert_tiff_to_png("data/1cm_maxint", "data/png_channels/maxint")