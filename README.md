# Taller Airflow: Pipelines de datos para entrenamiento e inferencia de modelos

Este repositorio contiene una solución de ejemplo para explorar Apache Airflow usando Docker Compose. El objetivo del taller es construir un workflow que:

- **Limpie el contenido** de una base de datos MySQL.
- **Cargue datos crudos** (archivos CSV de pingüinos) en la base de datos.
- **Procese y preprocese dichos datos** para preparar el entrenamiento.
- **Entrene modelos de Machine Learning** (Random Forest, Decision Tree, SVM, Logistic Regression) utilizando los datos preprocesados.
- **Implemente una API** para realizar inferencias a partir del modelo entrenado.

Todos los servicios se ejecutan en un único Docker Compose, permitiendo tener una arquitectura completa en contenedores.

---

## Arquitectura

La solución se compone de los siguientes contenedores:

- **MySQL:** Una base de datos que almacena los datos crudos y preprocesados, además de servir como fuente para el entrenamiento.
- **Airflow:** Contenedor (con varios servicios: webserver, scheduler, worker, triggerer, init, cli) encargado de ejecutar los DAGs que orquestan el flujo de datos.
- **Redis y Postgres:** Requeridos para el funcionamiento interno de Airflow (Celery executor y metadatos, respectivamente).
- **Montajes de volúmenes:**
  - `./data`: Directorio local que contiene los archivos CSV (ej.: `penguins_lter.csv` y `penguins_size.csv`).
  - `./dags`: Definición de DAGs (incluyendo el workflow `penguins_workflow.py`).
  - `./logs` y `./plugins`: Para logs y plugins de Airflow.
  - `models_volume`: Volumen compartido para almacenar los modelos entrenados (usado tanto por Airflow como, en un posible futuro, la API de inferencia).

### Diagrama básico

```ascii
       +---------------------+
       |   docker-compose    |
       +---------------------+
                │
       ┌────────┴─────────┐
┌─────────────┐    ┌─────────────┐
|    MySQL    |    |    Airflow  |
| (model_db)  |    | (DAGs, etc) |
└─────────────┘    └─────────────┘
       │                  │
(CSVs en ./data)   (Modelos en models_volume)
```


### Estructura del repositorio

.
├── airflow/               # Dockerfile y configuración custom de Airflow


├── dags/                  # DAGs de Airflow (incluye penguins_workflow.py)


├── data/                  # Archivos CSV de origen (penguins_lter.csv, penguins_size.csv)


├── logs/                  # Directorio para almacenar logs de Airflow


├── mysql/                 # Dockerfile y configuración custom para el contenedor MySQL


├── plugins/               # Plugins de Airflow (si se requieren)


├── docker-compose.yml     # Composición de todos los contenedores


├── .env                   # Archivo de variables de entorno (ejemplo: AIRFLOW_UID)


└── README.md              # Este archivo


### Configuración y Ejecución

- **1. Clonar el Repositorio** Puedes usar GitHub Desktop o ejecutar en Git Bash/CMD:

bash


git clone https://github.com/tu-usuario/tu-repositorio.git


Navega al directorio clonado:

bash


cd tu-repositorio

- **2. Configurar las Variables de Entorno** Crea un archivo .env en la raíz del repositorio (si no lo tienes) y asigna el siguiente valor para definir el usuario de Airflow. En Linux o Git Bash en Windows:

bash


echo -e "AIRFLOW_UID=$(id -u)" > .env


En CMD o PowerShell, asigna manualmente:

cmd


echo AIRFLOW_UID=50000 > .env

- **3. Preparar los Datos de Entrada** Coloca los archivos CSV de los pingüinos en el directorio ./data. 

Ejemplo:

./data/penguins_lter.csv

./data/penguins_size.csv

- **5. Ejecutar el Entorno** Desde la raíz del repositorio, ejecuta:

bash


docker compose up airflow-init


docker compose up



Este comando construirá y levantará todos los contenedores (Airflow, MySQL, Redis, Postgres, etc.).


- **6. Acceder a Airflow**
Una vez que todos los contenedores estén en ejecución, abre tu navegador y dirígete a: http://localhost:8080

Desde la UI de Airflow podrás ver el DAG penguins_workflow y seguir su progreso.

#### Descripción de los DAGs
El DAG penguins_workflow realiza lo siguiente:

- **clear_penguins_tables**

Utiliza MySqlOperator con el conn_id="mysql_default" para eliminar las tablas penguins_raw y penguins_preprocessed de la base de datos MySQL.

- **load_data**

Función Python que:

Lee los archivos CSV (ubicados en /data dentro del contenedor). Realiza un procesamiento básico y carga los datos crudos en la tabla penguins_raw de MySQL.

- **preprocess_data**

Función Python que:

Recupera los datos de penguins_raw. Aplica un preprocesamiento (como codificación de variables) y guarda el resultado en la tabla penguins_preprocessed.

- **train_models**

Función Python que:

Lee los datos preprocesados. Divide los datos en conjuntos de entrenamiento y prueba. 
Entrena varios modelos de Machine Learning (Random Forest, Decision Tree, SVM y Logistic Regression).
Guarda los artefactos (modelos entrenados) en el directorio /opt/airflow/models (montado via models_volume).

- **notify_api_reload:**

 Envía una solicitud HTTP POST al endpoint /reload_models/ de FastAPI para actualizar la caché de modelos, garantizando que la API utilice siempre la versión más reciente sin necesidad de reiniciar el contenedor.


### API de Inferencia

Como parte del taller se implemento fastAPI para realizar inferencias a partir del modelo entrenado.





---

Este README proporciona una descripción completa de la arquitectura, cómo configurar y ejecutar el entorno, el funcionamiento de los DAGs y pautas de solución de problemas. Puedes adaptarlo o ampliarlo conforme a los cambios o a la integración de la API para la inferencia.