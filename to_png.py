import os
from PIL import Image

def convert_images_to_png(source_folder, dest_folder):
    # Ensure the destination folder exists
    os.makedirs(dest_folder, exist_ok=True)

    # List all files in the source folder
    for file_name in os.listdir(source_folder):
        if file_name.lower().endswith('.tif') or file_name.lower().endswith('.tiff'):
            source_file_path = os.path.join(source_folder, file_name)
            try:
                # Open the TIFF file
                with Image.open(source_file_path) as tif_image:
                    # Create file name for PNG in the destination folder
                    base_name = os.path.splitext(file_name)[0]
                    png_path = os.path.join(dest_folder, f'{base_name}.png')

                    # Convert and save as PNG
                    tif_image.save(png_path, "PNG")

                    print(f'Successfully converted {file_name} to PNG')
            except Exception as e:
                print(f'Error converting {file_name}: {e}')

# Replace 'source_folder_path' with the actual path to your folder containing .tif images
# Replace 'dest_folder_path' with the actual path to your destination folder
source_folder_path = '1cm_meanint'
dest_folder_path = 'penege'
convert_images_to_png(source_folder_path, dest_folder_path)
