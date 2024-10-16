import os
import numpy as np
import tifffile

# Define the source and target directories
source_base_dir = "./tree_images"
target_base_dir = "./tree_images_supervisely"

# Define the subdirectories to process
subdirs = ["1cm_maxint", "1cm_meanint", "1cm_density"]

# List to store the names of files that failed to convert
failed_conversions = []

for subdir in subdirs:
    source_dir = os.path.join(source_base_dir, subdir)
    target_dir = os.path.join(target_base_dir, subdir)

    # Create target directory if it doesn't exist
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Process each .tif file in the source directory
    for filename in os.listdir(source_dir):
        if filename.endswith(".tif"):
            tiff_path = os.path.join(source_dir, filename)
            new_tiff_path = os.path.join(target_dir, filename)
            
            try:
                # Read, process, and save the image
                img = tifffile.imread(tiff_path).astype(np.uint8)
                tifffile.imwrite(new_tiff_path, img)
                print(f"Processed and saved {new_tiff_path}")
            except Exception as e:
                print(f"Failed to process {tiff_path}: {e}")
                failed_conversions.append(tiff_path)

# Print the names of files that failed to convert
if failed_conversions:
    print("\nFailed to convert the following files:")
    for failed_file in failed_conversions:
        print(failed_file)
else:
    print("\nAll files processed successfully.")

