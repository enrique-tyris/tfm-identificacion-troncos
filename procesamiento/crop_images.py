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

def crop_images_with_labels(input_dir, label_dir, output_image_dir, output_label_dir, image_size=640):
    """
    Recorta imágenes y ajusta las etiquetas correspondientes (BBoxes) para cada recorte.

    Parameters:
    input_dir (str): Directorio de entrada que contiene las imágenes RGB.
    label_dir (str): Directorio de entrada que contiene las etiquetas correspondientes.
    output_image_dir (str): Directorio de salida para las imágenes recortadas.
    output_label_dir (str): Directorio de salida para las etiquetas recortadas.
    image_size (int): Tamaño de los crops (ancho y alto). Default: 640.
    """
    # Crear los directorios de salida si no existen
    os.makedirs(output_image_dir, exist_ok=True)
    os.makedirs(output_label_dir, exist_ok=True)

    # Listar los archivos de imágenes en el directorio de entrada
    image_files = [f for f in os.listdir(input_dir) if f.endswith('.png')]

    # Procesar cada imagen y su etiqueta correspondiente
    for image_file in tqdm(image_files, desc="Procesando imágenes y etiquetas", unit="imagen"):
        image_base_name = os.path.splitext(image_file)[0]
        input_image_path = os.path.join(input_dir, image_file)
        label_path = os.path.join(label_dir, f"{image_base_name}.txt")

        if os.path.exists(label_path):
            crop_image_with_stride_and_labels(
                input_image_path, label_path, output_image_dir, output_label_dir, image_base_name, image_size
            )
        else:
            print(f"Etiqueta no encontrada para {image_file}. Se omite el recorte de la etiqueta.")

def crop_image_with_stride_and_labels(input_image_path, label_path, output_image_dir, output_label_dir, image_base_name, image_size=640, stride_x=640, stride_y=640):
    """
    Recorta una imagen y ajusta las etiquetas para cada recorte generado.

    Parameters:
    input_image_path (str): Ruta de la imagen de entrada.
    label_path (str): Ruta de la etiqueta de la imagen.
    output_image_dir (str): Directorio de salida para las imágenes recortadas.
    output_label_dir (str): Directorio de salida para las etiquetas recortadas.
    image_base_name (str): Nombre base para los crops.
    image_size (int): Tamaño de los crops (ancho y alto). Default: 640.
    """
    img = Image.open(input_image_path)
    img_width, img_height = img.size

    # Leer las etiquetas (BBoxes) del archivo de texto
    with open(label_path, 'r') as f:
        labels = f.readlines()

    # Recorrer la imagen y generar crops
    for y in range(0, img_height, stride_y):
        for x in range(0, img_width, stride_x):
            if x + image_size > img_width:
                x = img_width - image_size
            if y + image_size > img_height:
                y = img_height - image_size

            crop = img.crop((x, y, x + image_size, y + image_size))
            crop_file_name = f"{image_base_name}_{x}_{y}.png"
            crop_output_path = os.path.join(output_image_dir, crop_file_name)
            crop.save(crop_output_path)

            # Ajustar y guardar las etiquetas para el crop actual
            new_labels = adjust_labels_for_crop(labels, x, y, image_size, img_width, img_height)
            if new_labels:
                label_output_path = os.path.join(output_label_dir, crop_file_name.replace('.png', '.txt'))
                with open(label_output_path, 'w') as f:
                    f.writelines(new_labels)

def adjust_labels_for_crop(labels, x_offset, y_offset, crop_size, img_width, img_height):
    """
    Ajusta las etiquetas (BBoxes) para que coincidan con el crop generado.

    Parameters:
    labels (list): Lista de etiquetas originales (BBoxes) en formato YOLO.
    x_offset (int): Offset del crop en el eje X.
    y_offset (int): Offset del crop en el eje Y.
    crop_size (int): Tamaño del crop (ancho y alto).
    """
    new_labels = []
    for label in labels:
        cls, x_center, y_center, width, height = map(float, label.split())
        x_center_abs = x_center * img_width
        y_center_abs = y_center * img_height
        width_abs = width * img_width
        height_abs = height * img_height

        x1 = x_center_abs - width_abs / 2
        y1 = y_center_abs - height_abs / 2
        x2 = x_center_abs + width_abs / 2
        y2 = y_center_abs + height_abs / 2

        # Ajustar las coordenadas a los límites del crop
        x1_new = max(x1, x_offset)
        y1_new = max(y1, y_offset)
        x2_new = min(x2, x_offset + crop_size)
        y2_new = min(y2, y_offset + crop_size)

        if x1_new < x2_new and y1_new < y2_new:
            # Calcular nuevas coordenadas para el centro del BBox
            x_center_new = ((x1_new + x2_new) / 2 - x_offset) / crop_size
            y_center_new = ((y1_new + y2_new) / 2 - y_offset) / crop_size
            width_new = (x2_new - x1_new) / crop_size
            height_new = (y2_new - y1_new) / crop_size
            new_labels.append(f"{int(cls)} {x_center_new} {y_center_new} {width_new} {height_new}\n")

    return new_labels


# Ejemplo de uso:
# crop_images("data/P28/rgb_images", "data/P28/crop_images", image_size=640)