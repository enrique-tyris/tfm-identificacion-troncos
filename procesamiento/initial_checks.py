from PIL import Image
import os
import sys

def check_same_image_sizes(*input_dirs):
    """
    Verifica si todas las imágenes en los directorios de entrada tienen el mismo tamaño.
    Detiene la ejecución si se encuentran imágenes con tamaños diferentes.
    
    Parameters:
    *input_dirs (str): Lista de rutas de directorios a comprobar.
    
    Raises:
    SystemExit: Si se encuentran imágenes con tamaños diferentes.
    """
    reference_size = None
    for input_dir in input_dirs:
        # Listar todas las imágenes en el directorio
        image_files = [f for f in os.listdir(input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tif', '.tiff'))]
        
        for image_file in image_files:
            image_path = os.path.join(input_dir, image_file)
            with Image.open(image_path) as img:
                current_size = img.size  # (width, height)
                
                if reference_size is None:
                    reference_size = current_size
                    print(f"Tamaño de referencia establecido: {reference_size}")
                elif current_size != reference_size:
                    print(f"ERROR: Tamaño inconsistente encontrado en {image_path}. "
                          f"Esperado: {reference_size}, Encontrado: {current_size}")
                    sys.exit(1)  # Detener la ejecución con código de error 1
    
    print("Todas las imágenes tienen el mismo tamaño.")