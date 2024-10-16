import os
from PIL import Image
import numpy as np

def merge_channels_to_rgb(red_channel_path, green_channel_path, blue_channel_path, output_path):
    # Open the images
    red_channel = Image.open(red_channel_path).convert("L")
    green_channel = Image.open(green_channel_path).convert("L")
    blue_channel = Image.open(blue_channel_path).convert("L")

    # Calculate the min and max for each channel
    red_min, red_max = np.min(red_channel), np.max(red_channel)
    green_min, green_max = np.min(green_channel), np.max(green_channel)
    blue_min, blue_max = np.min(blue_channel), np.max(blue_channel)

    print(f"Image: {os.path.basename(output_path)}")
    print(f"Red Channel  - Min: {red_min}, Max: {red_max}")
    print(f"Green Channel - Min: {green_min}, Max: {green_max}")
    print(f"Blue Channel  - Min: {blue_min}, Max: {blue_max}")
    print("-" * 50)

    # Merge the channels into an RGB image
    rgb_image = Image.merge("RGB", (red_channel, green_channel, blue_channel))

    # Save the RGB image
    rgb_image.save(output_path, "PNG")

    print(f"RGB image saved as {output_path}\n")

# Directorios base
source_images_dir = "./310596_tfm/images/train"
labels_dir = "./310596_tfm/labels/train"
other_channels_dir = "./other2channels_png"
output_images_dir = "./310596_tfm_rgb/images/train"
output_labels_dir = "./310596_tfm_rgb/labels/train"

# Crear los directorios de salida si no existen
os.makedirs(output_images_dir, exist_ok=True)
os.makedirs(output_labels_dir, exist_ok=True)

# Procesar cada archivo de imagen en el directorio de imágenes de entrenamiento
for file_name in os.listdir(source_images_dir):
    if file_name.lower().endswith('.png'):
        base_name = os.path.splitext(file_name)[0]
        
        # Remover el prefijo '969973_P28_' para encontrar los homónimos
        stripped_base_name = base_name.replace('969973_P28_', '')

        # Definir rutas para los canales rojo, verde y azul
        red_channel_path = os.path.join(other_channels_dir, "1cm_density", f"{stripped_base_name}.png")
        green_channel_path = os.path.join(other_channels_dir, "1cm_maxint", f"{stripped_base_name}.png")
        blue_channel_path = os.path.join(source_images_dir, file_name)  # meanint is the original blue channel

        # Verificar que todos los canales existen
        missing_channels = []
        if not os.path.exists(red_channel_path):
            missing_channels.append('red (density)')
        if not os.path.exists(green_channel_path):
            missing_channels.append('green (maxint)')
        
        if missing_channels:
            print(f"Skipping {file_name} due to missing channels: {', '.join(missing_channels)}")
            continue

        # Ruta de salida para la imagen RGB, manteniendo el nombre original
        output_image_path = os.path.join(output_images_dir, f"{base_name}.png")

        # Fusionar las imágenes en una RGB y mostrar rangos de valores
        merge_channels_to_rgb(red_channel_path, green_channel_path, blue_channel_path, output_image_path)

        # Copiar las anotaciones al nuevo dataset, manteniendo el nombre original
        label_source_path = os.path.join(labels_dir, f"{base_name}.txt")
        label_output_path = os.path.join(output_labels_dir, f"{base_name}.txt")
        if os.path.exists(label_source_path):
            with open(label_source_path, 'r') as label_source:
                label_content = label_source.read()
            with open(label_output_path, 'w') as label_output:
                label_output.write(label_content)

print("Processing completed.")

