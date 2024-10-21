# Importar de scripts de la carpeta
from config_dataset import config_dataset

# Agrega el directorio raíz del proyecto al sys.path para importar
import sys
from pathlib import Path
directorio_raiz = Path(__file__).resolve().parent.parent
sys.path.append(str(directorio_raiz))

# Importar los módulos
from procesamiento.convert_tiff_to_png import convert_tiff_to_png
from procesamiento.combine_channels_to_rgb import combine_channels_to_rgb_batch
from procesamiento.crop_images import crop_images_with_labels
from pruebas.convert_density_tiff_to_png import convert_density_tiff_to_png

# Paso 1: utilizar una carpeta de las 3, pasemos de .tiff a .png
convert_tiff_to_png()

# Paso 2: etiquetar con el .png y descargar carpeta con .txt de bboxes

# Paso 3: Combinar los 3 canales en una imagen RGB
convert_tiff_to_png()
convert_density_tiff_to_png()
combine_channels_to_rgb_batch()

# Paso 4: hacer el crop modificando .txt también
crop_images_with_labels("images", "labels", "output_images", "output_labels")

# Paso 5: train/val split, añadir .yaml
config_dataset('carpeta_solotrain_imagesylabels', './final_dataset', val_percentage=0.2)

# Paso 6: Entrenar YOLO
# Utilizar script yolotrain.py