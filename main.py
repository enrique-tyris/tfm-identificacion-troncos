# Importaciones de los módulos
from procesamiento.initial_checks import check_same_image_sizes
from procesamiento.convert_tiff_to_png import convert_tiff_to_png
from procesamiento.create_blank_density_image import create_blank_density_image
from procesamiento.combine_channels_to_rgb import combine_channels_to_rgb_batch
from procesamiento.crop_images import crop_images
from procesamiento.apply_yolo import apply_yolo_to_crops
from procesamiento.postprocess_detections import split_detections_by_level, remap_detections_to_original
from visualizacion.visualize_detections import draw_all_detections
from visualizacion.heatmap_visualization import draw_coverage_heatmap

# Definir el identificador de la finca
finca = "P28"

# Paso 0: Comprobar que todas las imágenes tienen el mismo tamaño
check_same_image_sizes(f"data/{finca}/1cm_meanint", f"data/{finca}/1cm_maxint")

# Paso 1: Convertir TIFF a PNG
convert_tiff_to_png(f"data/{finca}/1cm_meanint", f"data/{finca}/png_channels/meanint")
convert_tiff_to_png(f"data/{finca}/1cm_maxint", f"data/{finca}/png_channels/maxint")
create_blank_density_image(f"data/{finca}/1cm_maxint", f"data/{finca}/png_channels/density/density_blank.png")

# Paso 2: Combinar los canales en una imagen RGB
combine_channels_to_rgb_batch(f"data/{finca}/png_channels/meanint", 
                              f"data/{finca}/png_channels/maxint", 
                              f"data/{finca}/png_channels/density/", 
                              f"data/{finca}/rgb_images/")

# Paso 3: Realizar crops de la imagen RGB
crop_images(f"data/{finca}/rgb_images/", f"data/{finca}/crops/")

# Paso 4: Detectar las secciones con YOLO
model = "entrenamiento/runs/detect/train2/weights/best.pt"
apply_yolo_to_crops(f"data/{finca}/crops", f"data/{finca}/detections/detections.json", model)

# Paso 5.1: Mapear detecciones a dimensiones de la finca
split_detections_by_level(f"data/{finca}/detections/detections.json", f"data/{finca}/detections/level_detections")
remap_detections_to_original(f"data/{finca}/detections/level_detections", f"data/{finca}/detections/remapped_detections")

# Paso 5.2: Visualización de detecciones
draw_all_detections(f"data/{finca}/rgb_images", f"data/{finca}/detections/remapped_detections", f"data/{finca}/visualization/detections_output")
draw_coverage_heatmap(f"data/{finca}/detections/remapped_detections", f"data/{finca}/rgb_images", f"data/{finca}/visualization/", min_level=100, max_level=250)

# Paso 6: Identificación de árboles (EJ: agrupacion dirección Z o plano XY)

# Paso 7: Visualización de resultados de árboles (EJ: visualización 3D)