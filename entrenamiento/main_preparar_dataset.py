# Importar de scripts de la carpeta
from config_dataset import move_files_to_val #configurar adecuadamente

# Agrega el directorio raíz del proyecto al sys.path para importar
import sys
from pathlib import Path
directorio_raiz = Path(__file__).resolve().parent.parent
sys.path.append(str(directorio_raiz))

# Importar los módulos
from procesamiento.convert_tiff_to_png import convert_tiff_to_png
from procesamiento.combine_channels_to_rgb import combine_channels_to_rgb_batch
from procesamiento.crop_images import crop_images
from pruebas.convert_density_tiff_to_png import convert_density_tiff_to_png

# Paso 1: utilizar una carpeta de las 3, pasemos de .tiff a .png
convert_tiff_to_png()

# Paso 2: etiquetar con el .png y descargar carpeta con .txt de bboxes

# Paso 3: Combinar los 3 canales en una imagen RGB
convert_tiff_to_png()
convert_density_tiff_to_png()
combine_channels_to_rgb_batch()

# Paso 4: hacer el crop modificando .txt también
crop_images() #hay que adaptar para los txt

# Paso 5: train/val split, añadir .yaml
# ((config_dataset.py))

# Paso 6: Entrenar YOLO
# (yolotrain.py)