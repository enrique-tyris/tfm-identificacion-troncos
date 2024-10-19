from PIL import Image
import numpy as np
import os

def combine_channels_to_rgb(meanint_path, maxint_path, density_path, output_path):
    """
    Combina tres imágenes PNG (meanint, maxint, density) en una imagen RGB.
    
    Parameters:
    meanint_path (str): Ruta de la imagen PNG para el canal 'meanint'.
    maxint_path (str): Ruta de la imagen PNG para el canal 'maxint'.
    density_path (str): Ruta de la imagen PNG para el canal 'density'. Actualmente es negro.
    output_path (str): Ruta de la imagen PNG de salida.
    """
    # Abrir cada uno de los canales
    meanint_img = Image.open(meanint_path).convert('L')  # Convertir a escala de grises
    maxint_img = Image.open(maxint_path).convert('L')
    density_img = Image.open(density_path).convert('L')  # En negro por ahora
    
    # Crear la imagen RGB
    rgb_image = Image.merge("RGB", (meanint_img, maxint_img, density_img))
    
    # Guardar la imagen combinada
    rgb_image.save(output_path)
    print(f"Imagen RGB guardada: {output_path}")

# Ejemplo de uso en el main o en un notebook
# combine_channels_to_rgb("data/png_channels/meanint/image1.png", 
#                         "data/png_channels/maxint/image1.png", 
#                         "data/density_black.png", 
#                         "data/rgb_images/image1_rgb.png")