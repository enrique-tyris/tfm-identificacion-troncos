from ultralytics import YOLO

# Load the YOLOv8 model for segmentation
model = YOLO('/home/enrique/Desktop/VARIOS/TFM/dataset_yolo/runs/detect/train2/weights/best.pt') 

# Set up training parameters
training_parameters = {
    'data': 'dataset/data_config.yaml',  	       # Path to your dataset YAML file
    'epochs': 10,                                      # Number of training epochs
    'imgsz': 640,                                      # Image size
    'batch': 16,                                       # Batch size, adjust according to your GPU memory
    'augment': True,                                   # Enable default augmentations
    'mosaic': 1,                                       # Disable mosaic augmentation
    'degrees': 20,                                     # Rotation augmentation (±10 degrees)
    'translate': 0.1,                                  # Translation augmentation (10% translation)
    'scale': 0.25,                                      # Scale augmentation (scales images by ±50%)
    'shear': 2.0,                                      # Shear augmentation (±2 degrees)
    'flipud': 0.5,                                     # Vertical flip augmentation with 50% probability
    'fliplr': 0.5,                                     # Horizontal flip augmentation with 50% probability
    'hsv_h': 0.015,                                    # Hue shift augmentation (±1.5%)
    'hsv_s': 0.2,                                      # Saturation augmentation (±70%)
    'hsv_v': 0.2,                                      # Value (brightness) augmentation (±40%)
    'patience': 15                                     # Early stopping patience (stop if no improvement for 10 epochs)
}

# Train the model
model.train(**training_parameters)
