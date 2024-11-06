### Introducción 
En este repositorio se encuentra el trabajo realizado para el Trabajo de Fin de Máster de Enrique García Iglesias, dirigido por el Dr. Pablo Crespo Peremarch y de título 'Identificación de troncos en nubes de puntos mediante Deep Learning'.

El script principal `main.py` contiene todos los pasos de ejecución para el procesamiento de rasterizaciones obtenidas a partir de una nube de puntos de una finca forestal, devolviendo un archivo JSON con la posición XY de los árboles detectados. Solamente hay que ubicar en la carpeta `data/` una subcarpeta con el nombre de una finca, EJ `P28/` según la nomenclatura utilizada, conteniendo las carpetas `1cm_maxint/` y `1cm_meanint/` con los archivos TIFF de las rasterizaciones de la finca según estas variables. El resto es indicar la finca a procesar en el `main.py` y ejecutar.

Hay que crear un entorno de Anaconda y dentro instalar los paquetes necesarios mediante `pip install requirements.txt` para que pueda funcionar el procesamiento.

### Explicación de los diferentes directorios:
- En la carpeta `data/` se deben ubicar los archivos de input y se ubicarán los archivos de pasos intermedios y output.
- En la carpeta `pruebas/` se ubican algunos notebooks interesantes para conocer experimentos hechos durante el desarollo.
- En la carpeta `procesamiento/` se ubican métodos utilizados durante el procesamiento y en la carpeta `visualizacion/` se encuentran métodos utilizados para visualizar resultados de detección de objetos en formato mapa de calor, resumiendo en un mapa las detecciones a todas las alturas.
- En la carpeta `entrenamiento/` se incluye una versión del pipeline de procesamiento que sirve para configurar un dataset formato YOLO para el entrenamiento del modelo de detección de objetos.
- En la carpeta `evaluacion/` se ubican scripts para la reutilización de etiquetados formato shapefile de ground truth, tanto para evaluación del método general como para evaluación del método de detección de objetos. También se ubican métodos para la identificación final de instancias de troncos, paso final del pipeline. Finalmente se tiene en esta carpeta el script `evaluate.py` que, en caso de tener ground truth de ubicación de los árboles, calcula las métricas de Precision, Recall y RMSE en la identificación y ubicación de árboles en la finca de estudio.

### Especificaciones Técnicas
El trabajo presentado ha sido desarrollado en un equipo con las siguientes especificaciones técnicas:
- Procesador (CPU): Intel(R) Core(TM) i7-10750H CPU @ 2.60GHz
- Memoria RAM: 15 GB
- Tarjeta Gráfica (GPU): NVIDIA GeForce RTX 3070 con 8 GB de VRAM
- Versión de CUDA: 12.4
- Sistema Operativo: Ubuntu 22.04 LTS