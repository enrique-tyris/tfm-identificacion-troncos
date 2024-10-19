import os
import shutil
import random
from tqdm import tqdm

# Path to the dataset
merged_path = './310596_tfm_rgb_cropped'
output_path = './dataset'

# Percentage of images to move from train to val
val_percentage = 0.2

# Function to move a subset of files from train to val
def move_files_to_val(image_dir, label_dir, val_image_dir, val_label_dir, val_percentage):
    # Crear las carpetas de destino si no existen
    os.makedirs(val_image_dir, exist_ok=True)
    os.makedirs(val_label_dir, exist_ok=True)
    
    # List all files in the train directory
    images = [f for f in os.listdir(image_dir) if os.path.isfile(os.path.join(image_dir, f))]

    # Calculate the number of files to move
    num_val_images = int(len(images) * val_percentage)

    # Randomly select files to move
    val_images = random.sample(images, num_val_images)

    not_found_count = 0

    for image in tqdm(val_images, desc=f"Moving {val_percentage * 100}% of images from {image_dir} to {val_image_dir}"):
        # Move image
        shutil.move(os.path.join(image_dir, image), os.path.join(val_image_dir, image))
        
        # Move corresponding label
        label = image.replace('.jpg', '.txt').replace('.png', '.txt')  # Handle both jpg and png extensions
        label_path = os.path.join(label_dir, label)
        
        # Check if the label file exists before moving
        if os.path.exists(label_path):
            shutil.move(label_path, os.path.join(val_label_dir, label))
        else:
            not_found_count += 1
            print(f"Warning: Label file {label_path} not found. Skipping.")

    print(f"\nTotal warnings: {not_found_count} files not found.")

# Paths to train and val directories for images and labels
image_train_dir = os.path.join(merged_path, 'images/train')
label_train_dir = os.path.join(merged_path, 'labels/train')
image_val_dir = os.path.join(output_path, 'images/val')
label_val_dir = os.path.join(output_path, 'labels/val')

# Create output directory structure
os.makedirs(output_path, exist_ok=True)
os.makedirs(os.path.join(output_path, 'images/train'), exist_ok=True)
os.makedirs(os.path.join(output_path, 'labels/train'), exist_ok=True)

# Copy train images and labels to the new directory
shutil.copytree(image_train_dir, os.path.join(output_path, 'images/train'), dirs_exist_ok=True)
shutil.copytree(label_train_dir, os.path.join(output_path, 'labels/train'), dirs_exist_ok=True)

# Move files from train to val
move_files_to_val(os.path.join(output_path, 'images/train'), 
                  os.path.join(output_path, 'labels/train'), 
                  image_val_dir, label_val_dir, val_percentage)

print("20% of the images and labels have been moved from train to val.")

# Create YOLO data_config.yaml file
data_config = """
train: dataset/images/train
val: dataset/images/val

nc: 1  # Number of classes
names: ['class_name']  # Replace 'class_name' with your class names
"""

with open(os.path.join(output_path, 'data_config.yaml'), 'w') as f:
    f.write(data_config)

print("YOLO data_config.yaml file created.")

