import os
import numpy as np
import tifffile

# Define the source and target directories
source_base_dir = "/home/enrique/Desktop/VARIOS/TFM/data/tree_images"
target_base_dir = "./other2channels_png"

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
    
    print(f"\nProcessing directory: {subdir}")
    
    # Process each .tif file in the source directory
    for filename in os.listdir(source_dir):
        if filename.startswith("P28") and filename.endswith(".tif"):
            tiff_path = os.path.join(source_dir, filename)
            new_tiff_path = os.path.join(target_dir, filename.replace(".tif", ".png"))
            
            try:
                # Read the image
                img = tifffile.imread(tiff_path)
                
                if subdir == "1cm_density":
                    # Set the desired min and max range for scaling
                    desired_min = 0
                    desired_max = 2
                    
                    # Clip the values to be within the desired range
                    img_clipped = np.clip(img, desired_min, desired_max)
                    
                    # Scale the clipped values to the range 0-255
                    img_scaled = ((img_clipped - desired_min) / (desired_max - desired_min)) * 255.0
                    
                    # Convert to uint8
                    img_scaled = img_scaled.astype(np.uint8)
                    
                    # Save the processed image as PNG
                    tifffile.imwrite(new_tiff_path, img_scaled)
                    print(f"Processed and saved {new_tiff_path}")
                
                else:
                    # Convert directly to uint8 for non-density images
                    img = img.astype(np.uint8)
                    
                    # Save the processed image as PNG
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

