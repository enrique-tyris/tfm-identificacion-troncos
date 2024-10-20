import os
from PIL import Image
import tifffile

def create_blank_density_image(input_dir, output_path):
    """
    Crea una imagen en blanco para el canal de density con el mismo tamaño que las imágenes
    TIFF de la carpeta de entrada y la guarda en la ruta especificada. Si el directorio
    de salida no existe, lo crea.
    
    Parameters:
    input_dir (str): Directorio de entrada que contiene las imágenes de referencia (típicamente .tif).
    output_path (str): Ruta donde se guardará la imagen de density en blanco.
    """
    # Verificar que haya archivos TIFF en el directorio
    tiff_files = [f for f in os.listdir(input_dir) if f.endswith('.tif')]
    if not tiff_files:
        raise ValueError(f"No se encontraron archivos .tif en la carpeta: {input_dir}")

    # Usar el tamaño de la primera imagen TIFF como referencia
    first_tiff_path = os.path.join(input_dir, tiff_files[0])
    with tifffile.TiffFile(first_tiff_path) as tiff:
        # Obtener el tamaño de la imagen (width, height)
        height, width = tiff.pages[0].shape
    
    # Crear el directorio de salida si no existe
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Crear una imagen en blanco del mismo tamaño
    blank_image = Image.new('L', (width, height), 0)  # 'L' para modo de escala de grises (0 = negro)
    blank_image.save(output_path)
    print(f"Imagen de density en blanco creada: {output_path}")

# Ejemplo de uso
# create_blank_density_image("data/1cm_meanint", "data/1cm_density/density_blank.png")