from procesamiento.convert_tiff_to_png import convert_tiff_to_png
from procesamiento.combine_channels_to_rgb import combine_channels_to_rgb
from procesamiento.crop_images import crop_image

# Paso 1: Convertir TIFF a PNG
convert_tiff_to_png("data/1cm_meanint", "data/png_channels/meanint")
convert_tiff_to_png("data/1cm_maxint", "data/png_channels/maxint")

# Paso 2: Combinar los canales en una imagen RGB
combine_channels_to_rgb("data/png_channels/meanint/image1.png", 
                        "data/png_channels/maxint/image1.png", 
                        "data/density_black.png", 
                        "data/rgb_images/image1_rgb.png")

# Paso 3: Realizar crops de la imagen RGB
crop_image("data/rgb_images/image1_rgb.png", "data/crops/image1/")
