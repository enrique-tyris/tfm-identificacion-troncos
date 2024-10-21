import os
import shutil
import random
from tqdm import tqdm

def config_dataset(merged_path, output_path, val_percentage=0.2):
    """
    Configura un dataset para entrenamiento y validación, moviendo un porcentaje de las imágenes y etiquetas
    de 'train' a 'val' y generando un archivo de configuración YAML para YOLO.
    
    Parameters:
    merged_path (str): Ruta al directorio con las imágenes y etiquetas unificadas.
    output_path (str): Ruta al directorio donde se guardará el dataset configurado.
    val_percentage (float): Porcentaje de imágenes a mover de 'train' a 'val'. Default: 0.2 (20%).
    """
    
    # Rutas a los directorios de imágenes y etiquetas para 'train' y 'val'
    image_train_dir = os.path.join(merged_path, 'images/train')
    label_train_dir = os.path.join(merged_path, 'labels/train')
    image_val_dir = os.path.join(output_path, 'images/val')
    label_val_dir = os.path.join(output_path, 'labels/val')
    
    # Crear la estructura de directorios de salida
    os.makedirs(os.path.join(output_path, 'images/train'), exist_ok=True)
    os.makedirs(os.path.join(output_path, 'labels/train'), exist_ok=True)
    os.makedirs(image_val_dir, exist_ok=True)
    os.makedirs(label_val_dir, exist_ok=True)
    
    # Copiar imágenes y etiquetas de entrenamiento a la nueva estructura de directorios
    shutil.copytree(image_train_dir, os.path.join(output_path, 'images/train'), dirs_exist_ok=True)
    shutil.copytree(label_train_dir, os.path.join(output_path, 'labels/train'), dirs_exist_ok=True)
    
    # Mover un porcentaje de imágenes y etiquetas a 'val'
    move_files_to_val(
        os.path.join(output_path, 'images/train'), 
        os.path.join(output_path, 'labels/train'), 
        image_val_dir, 
        label_val_dir, 
        val_percentage
    )
    
    # Crear archivo de configuración YAML para YOLO
    create_yolo_data_config(output_path)
    print(f"{val_percentage * 100}% of the images and labels have been moved from train to val.")
    print("YOLO data_config.yaml file created.")

def move_files_to_val(image_dir, label_dir, val_image_dir, val_label_dir, val_percentage):
    """
    Mueve un subconjunto de archivos desde 'train' a 'val'.
    
    Parameters:
    image_dir (str): Directorio de imágenes de 'train'.
    label_dir (str): Directorio de etiquetas de 'train'.
    val_image_dir (str): Directorio de destino para las imágenes de 'val'.
    val_label_dir (str): Directorio de destino para las etiquetas de 'val'.
    val_percentage (float): Porcentaje de imágenes a mover de 'train' a 'val'.
    """
    # Listar todos los archivos de imágenes en el directorio de 'train'
    images = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]

    # Calcular el número de imágenes que se moverán a 'val'
    num_val_images = int(len(images) * val_percentage)

    # Seleccionar aleatoriamente las imágenes que se moverán
    val_images = random.sample(images, num_val_images)

    not_found_count = 0

    for image in tqdm(val_images, desc=f"Moving {val_percentage * 100}% of images from {image_dir} to {val_image_dir}"):
        # Mover la imagen
        shutil.move(os.path.join(image_dir, image), os.path.join(val_image_dir, image))
        
        # Mover la etiqueta correspondiente
        label = image.replace('.jpg', '.txt').replace('.png', '.txt')
        label_path = os.path.join(label_dir, label)
        
        # Verificar si el archivo de etiqueta existe antes de moverlo
        if os.path.exists(label_path):
            shutil.move(label_path, os.path.join(val_label_dir, label))
        else:
            not_found_count += 1
            print(f"Warning: Label file {label_path} not found. Skipping.")

    print(f"\nTotal warnings: {not_found_count} label files not found.")

def create_yolo_data_config(output_path):
    """
    Crea un archivo de configuración YAML para el dataset de YOLO.
    El archivo asume una sola clase llamada 'circle'.
    
    Parameters:
    output_path (str): Directorio donde se guardará el archivo 'data_config.yaml'.
    """
    train_path = os.path.join(output_path, 'images/train')
    val_path = os.path.join(output_path, 'images/val')
    data_config = (
        f"train: {train_path}\n"
        f"val: {val_path}\n\n"
        "nc: 1  # Number of classes\n"
        "names: ['circle']\n"
    )
    
    # Escribir el archivo de configuración YAML
    with open(os.path.join(output_path, 'data_config.yaml'), 'w') as f:
        f.write(data_config)

# Ejemplo de uso:
# config_dataset('./310596_tfm_rgb_cropped', './dataset', val_percentage=0.2)