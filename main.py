from procesamiento.convert_tiff_to_png import convert_tiff_to_png
from procesamiento.create_blank_density_image import create_blank_density_image
from procesamiento.combine_channels_to_rgb import combine_channels_to_rgb_batch
from procesamiento.crop_images import crop_images
from procesamiento.apply_yolo import apply_yolo_to_crops

# Paso 1: Convertir TIFF a PNG
convert_tiff_to_png("data/P28/1cm_meanint", "data/P28/png_channels/meanint")
convert_tiff_to_png("data/P28/1cm_maxint", "data/P28/png_channels/maxint")
create_blank_density_image("data/P28/1cm_maxint", "data/P28/png_channels/density/density_blank.png")

# Paso 2: Combinar los canales en una imagen RGB
combine_channels_to_rgb_batch("data/P28/png_channels/meanint", 
                              "data/P28/png_channels/maxint", 
                              "data/P28/png_channels/density/", 
                              "data/P28/rgb_images/")

# Paso 3: Realizar crops de la imagen RGB
crop_images("data/P28/rgb_images/", "data/P28/crops/")

# Paso 4: detectar las secciones con YOLO
model = "train/runs/detect/train2/weights/best.pt"
apply_yolo_to_crops("data/P28/crops", "data/P28/detections.json", model)

# Paso 5: mapear detecciones a dimensiones de la finca

# Paso 6: identificación de árboles