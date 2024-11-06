import json
import numpy as np
from scipy.spatial import KDTree
from tqdm import tqdm
import matplotlib.pyplot as plt

def load_coordinates_from_json(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return [(coord[0], coord[1]) for coord in data]

def associate_detections_with_ground_truth(detection_json, ground_truth_json, max_distance=20):
    detections = load_coordinates_from_json(detection_json)
    ground_truth = load_coordinates_from_json(ground_truth_json)

    # KDTree for efficient nearest neighbor search
    gt_tree = KDTree(ground_truth)

    matches = []
    false_positives = []
    false_negatives = list(ground_truth)  # Start with all ground truth as unmatched

    for detection in detections:
        distance, index = gt_tree.query(detection, distance_upper_bound=max_distance)
        if distance < max_distance:
            match = ground_truth[index]
            matches.append((detection, match))
            if match in false_negatives:
                false_negatives.remove(match)
        else:
            false_positives.append(detection)

    return {
    'matches': matches,
    'false_positives': false_positives,
    'false_negatives': false_negatives
    }


def calculate_metrics(association_data):
    matches = association_data['matches']
    false_positives = association_data['false_positives']
    false_negatives = association_data['false_negatives']

    # Precision and Recall
    true_positives = len(matches)
    precision = true_positives / (true_positives + len(false_positives)) if true_positives + len(false_positives) > 0 else 0
    recall = true_positives / (true_positives + len(false_negatives)) if true_positives + len(false_negatives) > 0 else 0

    # RMSE Calculation for matched pairs
    if len(matches) > 0:
        detection_points = np.array([match[0] for match in matches])
        ground_truth_points = np.array([match[1] for match in matches])
        
        # Calculate RMSE manually
        rmse = np.sqrt(np.mean((detection_points - ground_truth_points) ** 2))
    else:
        rmse = None  # No matches, cannot calculate RMSE

    return {
        'precision': precision,
        'recall': recall,
        'rmse': rmse
    }


def plot_detections_and_ground_truth(association_data):
    """
    Visualiza los puntos de detección y ground truth en el mismo gráfico, mostrando las asociaciones.

    Parameters:
    association_data (dict): Datos de asociación que contienen 'matches', 'false_positives' y 'false_negatives'.
    """
    # Extraer las coordenadas de detecciones y ground truth desde los datos de asociación
    detection_coords = [match[0] for match in association_data['matches']] + association_data['false_positives']
    ground_truth_coords = [match[1] for match in association_data['matches']] + association_data['false_negatives']
    
    # Crear una figura
    plt.figure(figsize=(10, 8))
    
    # Graficar todos los puntos de detección y ground truth
    plt.scatter(*zip(*detection_coords), c='blue', marker='o', label='Detecciones', alpha=0.6)
    plt.scatter(*zip(*ground_truth_coords), c='green', marker='x', label='Ground Truth', alpha=0.6)

    # Dibujar líneas entre detecciones y ground truth asociados
    for match in association_data['matches']:
        det_point, gt_point = match
        plt.plot([det_point[0], gt_point[0]], [det_point[1], gt_point[1]], 'r--', linewidth=0.8)

    # Marcar falsos positivos y negativos
    for fp in association_data['false_positives']:
        plt.scatter(fp[0], fp[1], c='red', edgecolor='black', marker='o', s=100, label='Falso Positivo')
    
    for fn in association_data['false_negatives']:
        plt.scatter(fn[0], fn[1], c='purple', edgecolor='black', marker='x', s=100, label='Falso Negativo')
    
    # Configurar la visualización
    plt.legend()
    plt.xlabel("X")
    plt.ylabel("Y")
    plt.title("Detecciones vs Ground Truth con Asociaciones")
    plt.gca().invert_yaxis()  # Invertir eje Y para que coincida con la representación de la imagen
    plt.show()


if __name__ == "__main__":
    finca = 'P9'
    detection_json = f"data/{finca}/results/tree_centers.json"
    ground_truth_json = f"data/{finca}/results/tree_centers_ground_truth.json"

    # Asociar detecciones con ground truth y visualizar
    association_data = associate_detections_with_ground_truth(detection_json, ground_truth_json, max_distance=25)
    
    # Visualizar asociaciones
    # plot_detections_and_ground_truth(association_data)

    # Calcular métricas
    metrics = calculate_metrics(association_data)
    print("Precision:", metrics['precision'])
    print("Recall:", metrics['recall'])
    print("RMSE:", metrics['rmse'])