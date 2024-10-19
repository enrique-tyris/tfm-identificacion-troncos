import os
import cv2
import numpy as np

# Configuración inicial
input_dir = '310596_tfm_rgb'
output_dir = '310596_tfm_rgb_cropped'
image_size = 640
overlap = 100
stride = image_size - overlap

# Crear la estructura de carpetas en el directorio de salida
for subdir in ['images/train', 'labels/train']:
    os.makedirs(os.path.join(output_dir, subdir), exist_ok=True)

# Función para recortar imágenes y ajustar labels
def process_image(image_path, label_path, output_image_dir, output_label_dir):
    # Cargar la imagen
    image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Leer PNG con transparencia si es necesario
    h, w = image.shape[:2]
    
    # Leer los labels
    with open(label_path, 'r') as f:
        labels = f.readlines()

    # Recorrer la imagen en pasos de 'stride' píxeles
    for y in range(0, h, stride):
        for x in range(0, w, stride):
            # Asegurarnos que el recorte final tenga el tamaño correcto
            if x + image_size > w:
                x = w - image_size
            if y + image_size > h:
                y = h - image_size
            
            # Definir el área de recorte
            crop = image[y:y+image_size, x:x+image_size]
            
            # Definir el nombre para la subimagen y el archivo de labels correspondiente
            base_name = os.path.basename(image_path).replace('.png', '')
            crop_name = f'{base_name}_{x}_{y}.png'
            crop_image_path = os.path.join(output_image_dir, crop_name)
            crop_label_path = os.path.join(output_label_dir, crop_name.replace('.png', '.txt'))

            # Guardar la subimagen
            cv2.imwrite(crop_image_path, crop)
            
            # Ajustar los labels para esta subimagen
            new_labels = []
            for label in labels:
                cls, x_center, y_center, width, height = map(float, label.split())
                
                # Convertir las coordenadas normalizadas a píxeles absolutos
                x_center = x_center * w
                y_center = y_center * h
                width = width * w
                height = height * h
                
                # Calcular las esquinas del Bbox
                x1 = x_center - width / 2
                y1 = y_center - height / 2
                x2 = x_center + width / 2
                y2 = y_center + height / 2

                # Ajustar el Bbox a los límites de la subimagen
                x1_new = max(x1, x)
                y1_new = max(y1, y)
                x2_new = min(x2, x + image_size)
                y2_new = min(y2, y + image_size)

                # Verificar si el Bbox ajustado sigue siendo válido
                if x1_new < x2_new and y1_new < y2_new:
                    # Calcular el nuevo centro y tamaño del Bbox ajustado
                    x_center_new = (x1_new + x2_new) / 2 - x
                    y_center_new = (y1_new + y2_new) / 2 - y
                    width_new = x2_new - x1_new
                    height_new = y2_new - y1_new

                    # Normalizar las coordenadas para la subimagen
                    x_center_crop = x_center_new / image_size
                    y_center_crop = y_center_new / image_size
                    width_crop = width_new / image_size
                    height_crop = height_new / image_size

                    new_labels.append(f'{int(cls)} {x_center_crop:.6f} {y_center_crop:.6f} {width_crop:.6f} {height_crop:.6f}\n')
            
            # Guardar los nuevos labels solo si hay al menos uno válido
            if new_labels:
                with open(crop_label_path, 'w') as f:
                    f.writelines(new_labels)

# Procesar todas las imágenes en la carpeta de entrada
image_dir = os.path.join(input_dir, 'images/train')
label_dir = os.path.join(input_dir, 'labels/train')

for image_name in os.listdir(image_dir):
    if image_name.endswith('.png'):
        image_path = os.path.join(image_dir, image_name)
        label_path = os.path.join(label_dir, image_name.replace('.png', '.txt'))
        process_image(image_path, label_path, os.path.join(output_dir, 'images/train'), os.path.join(output_dir, 'labels/train'))

