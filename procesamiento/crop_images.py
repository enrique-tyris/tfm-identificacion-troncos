import os
from PIL import Image
import math
from tqdm import tqdm

def crop_images(input_dir, output_dir, image_size=640):
    """
    Corta todas las imágenes en un directorio en múltiples crops de tamaño image_size x image_size,
    con solapamiento calculado automáticamente para que los recortes sean uniformes.

    Parameters:
    input_dir (str): Directorio de entrada que contiene las imágenes RGB.
    output_dir (str): Directorio de salida donde se guardarán los crops.
    image_size (int): Tamaño de los crops (ancho y alto). Default: 640.
    """
    # Listar todos los archivos en el directorio de entrada
    image_files = [f for f in os.listdir(input_dir) if f.endswith('.png')]

    # Crear el directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Asumir que todas las imágenes tienen el mismo tamaño, usar la primera para calcular el stride
    if image_files:
        sample_image_path = os.path.join(input_dir, image_files[0])
        img = Image.open(sample_image_path)
        img_width, img_height = img.size

        # Calcular el número de recortes necesario para ancho y alto
        num_crops_x = math.ceil(img_width / image_size)
        num_crops_y = math.ceil(img_height / image_size)

        # Calcular el solapamiento necesario para asegurar que los recortes sean uniformes
        overlap_x = (num_crops_x * image_size - img_width) / num_crops_x
        overlap_y = (num_crops_y * image_size - img_height) / num_crops_y

        # Calcular el stride (avance) basado en el solapamiento
        stride_x = int(image_size - overlap_x)
        stride_y = int(image_size - overlap_y)

        print(f"Calculado overlap X: {overlap_x}, Y: {overlap_y}")
        print(f"Calculado stride X: {stride_x}, Y: {stride_y}")

        # Procesar cada imagen con el stride calculado, usando tqdm para mostrar el progreso
        for image_file in tqdm(image_files, desc="Procesando imágenes", unit="imagen"):
            input_image_path = os.path.join(input_dir, image_file)
            image_base_name = os.path.splitext(image_file)[0]
            crop_image_with_stride(input_image_path, output_dir, image_base_name, image_size, stride_x, stride_y)

def crop_image_with_stride(input_image_path, output_dir, image_base_name, image_size=640, stride_x=640, stride_y=640):
    """
    Corta una imagen grande en múltiples crops de tamaño image_size x image_size y los guarda
    con nombres secuenciales en el directorio de salida, con un avance de 'stride_x' y 'stride_y'.

    Parameters:
    input_image_path (str): Ruta de la imagen de entrada.
    output_dir (str): Directorio de salida donde se guardarán los crops.
    image_base_name (str): Nombre base para los crops.
    image_size (int): Tamaño de los crops (ancho y alto). Default: 640.
    stride_x (int): Tamaño del avance entre los recortes en el eje X.
    stride_y (int): Tamaño del avance entre los recortes en el eje Y.
    """
    img = Image.open(input_image_path)
    img_width, img_height = img.size

    # Contador para los nombres de los crops
    crop_count = 1

    # Iterar sobre la imagen y generar crops con el stride calculado
    for y in range(0, img_height, stride_y):
        for x in range(0, img_width, stride_x):
            # Ajustar para que el último recorte tenga el tamaño correcto si nos pasamos del borde
            if x + image_size > img_width:
                x = img_width - image_size
            if y + image_size > img_height:
                y = img_height - image_size

            # Definir el área de recorte
            crop = img.crop((x, y, x + image_size, y + image_size))

            # Definir el nombre del archivo de salida
            crop_file_name = f"{image_base_name}_{x}_{y}.png"
            crop_output_path = os.path.join(output_dir, crop_file_name)

            # Guardar el crop
            crop.save(crop_output_path)
            crop_count += 1
            print(f"Guardado crop: {crop_output_path}")

# Ejemplo de uso en el main o en un notebook
# crop_images("data/P28/rgb_images", "data/P28/crop_images", image_size=640)