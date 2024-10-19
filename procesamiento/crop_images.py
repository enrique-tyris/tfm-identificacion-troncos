import os
from PIL import Image

def crop_image(input_image_path, output_dir, crop_size=640):
    """
    Corta una imagen grande en múltiples crops de tamaño crop_size x crop_size.
    
    Parameters:
    input_image_path (str): Ruta de la imagen de entrada.
    output_dir (str): Directorio de salida donde se guardarán los crops.
    crop_size (int): Tamaño de los crops (ancho y alto). Default: 640.
    """
    img = Image.open(input_image_path)
    img_width, img_height = img.size
    
    # Crear el directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Contador para los nombres de los crops
    crop_count = 0
    
    # Iterar sobre la imagen y generar crops
    for top in range(0, img_height, crop_size):
        for left in range(0, img_width, crop_size):
            right = min(left + crop_size, img_width)
            bottom = min(top + crop_size, img_height)
            crop = img.crop((left, top, right, bottom))
            
            # Guardar el crop
            crop_file_name = f"crop_{crop_count}.png"
            crop_output_path = os.path.join(output_dir, crop_file_name)
            crop.save(crop_output_path)
            crop_count += 1
            print(f"Guardado crop: {crop_output_path}")

# Ejemplo de uso en el main o en un notebook
# crop_image("data/rgb_images/image1_rgb.png", "data/crops/image1/")
