from PIL import Image
import os
from tqdm import tqdm

def combine_channels_to_rgb_batch(meanint_dir, maxint_dir, density_dir, output_dir):
    """
    Combina todas las imágenes PNG en los directorios de 'meanint', 'maxint', y 'density' en imágenes RGB.
    Si las carpetas 'meanint', 'maxint' y 'density' tienen el mismo número de archivos, se procesan en base a nombres iguales.
    Si solo 'meanint' y 'maxint' tienen la misma cantidad de archivos, se utiliza la única imagen de 'density' para todas.
    
    Parameters:
    meanint_dir (str): Directorio que contiene las imágenes PNG para el canal 'meanint'.
    maxint_dir (str): Directorio que contiene las imágenes PNG para el canal 'maxint'.
    density_dir (str): Directorio que contiene las imágenes PNG para el canal 'density'.
    output_dir (str): Directorio donde se guardarán las imágenes PNG combinadas en RGB.
    """
    # Listar archivos en cada directorio
    meanint_files = sorted([f for f in os.listdir(meanint_dir) if f.endswith('.png')])
    maxint_files = sorted([f for f in os.listdir(maxint_dir) if f.endswith('.png')])
    density_files = sorted([f for f in os.listdir(density_dir) if f.endswith('.png')])

    # Verificar que 'meanint' y 'maxint' tengan el mismo número de archivos
    if len(meanint_files) != len(maxint_files):
        raise ValueError("Las carpetas 'meanint' y 'maxint' deben tener el mismo número de archivos.")

    # Caso 1: Las tres carpetas tienen el mismo número de archivos
    if len(density_files) == len(meanint_files):
        print("Procesando con imágenes de 'density' correspondientes a cada imagen de 'meanint' y 'maxint'...")
        for meanint_file, maxint_file, density_file in tqdm(zip(meanint_files, maxint_files, density_files),
                                                            total=len(meanint_files),
                                                            desc="Procesando imágenes RGB",
                                                            unit="archivo"):
            # Verificar que los nombres coincidan
            if not (meanint_file == maxint_file == density_file):
                raise ValueError(f"Los archivos no coinciden: {meanint_file}, {maxint_file}, {density_file}")

            meanint_path = os.path.join(meanint_dir, meanint_file)
            maxint_path = os.path.join(maxint_dir, maxint_file)
            density_path = os.path.join(density_dir, density_file)

            # Guardar la imagen combinada en el directorio de salida
            output_path = os.path.join(output_dir, meanint_file.replace('.png', '_rgb.png'))
            combine_channels_to_rgb(meanint_path, maxint_path, density_path, output_path)

    # Caso 2: Solo hay una imagen en 'density'
    elif len(density_files) == 1:
        print("Procesando con una única imagen de 'density' para todas las imágenes de 'meanint' y 'maxint'...")
        density_image_path = os.path.join(density_dir, density_files[0])
        
        for meanint_file, maxint_file in tqdm(zip(meanint_files, maxint_files),
                                              total=len(meanint_files),
                                              desc="Procesando imágenes RGB",
                                              unit="archivo"):
            # Verificar que los nombres coincidan
            if not (meanint_file == maxint_file):
                raise ValueError(f"Los archivos no coinciden: {meanint_file}, {maxint_file}")

            meanint_path = os.path.join(meanint_dir, meanint_file)
            maxint_path = os.path.join(maxint_dir, maxint_file)
            density_path = density_image_path

            # Guardar la imagen combinada en el directorio de salida
            output_path = os.path.join(output_dir, meanint_file.replace('.png', '_rgb.png'))
            combine_channels_to_rgb(meanint_path, maxint_path, density_path, output_path)

    else:
        raise ValueError("La carpeta 'density' debe contener una imagen en blanco o el mismo número de archivos que las carpetas 'meanint' y 'maxint'.")

def combine_channels_to_rgb(meanint_path, maxint_path, density_path, output_path):
    """
    Combina tres imágenes PNG (meanint, maxint, density) en una imagen RGB.
    Crea la carpeta de salida si no existe antes de guardar la imagen combinada.
    
    Parameters:
    meanint_path (str): Ruta de la imagen PNG para el canal 'meanint'.
    maxint_path (str): Ruta de la imagen PNG para el canal 'maxint'.
    density_path (str): Ruta de la imagen PNG para el canal 'density'. Actualmente es negro.
    output_path (str): Ruta de la imagen PNG de salida.
    """
    # Crear el directorio de salida si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Abrir cada uno de los canales
    meanint_img = Image.open(meanint_path).convert('L')  # Convertir a escala de grises
    maxint_img = Image.open(maxint_path).convert('L')
    density_img = Image.open(density_path).convert('L')  # En negro por ahora
    
    # Crear la imagen RGB, asegurando que R=Density, G=Maxint, B=Meanint
    rgb_image = Image.merge("RGB", (density_img, maxint_img, meanint_img))
    
    # Guardar la imagen combinada
    rgb_image.save(output_path, "PNG")
    print(f"Imagen RGB guardada: {output_path}")

# Ejemplo de uso
# combine_channels_to_rgb_batch("data/png_channels/meanint", 
#                               "data/png_channels/maxint", 
#                               "data/1cm_density", 
#                               "data/rgb_images")