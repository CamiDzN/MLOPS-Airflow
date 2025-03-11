from fastapi import FastAPI, HTTPException
import joblib
import numpy as np
from pydantic import BaseModel
import os

app = FastAPI()

MODEL_DIR = "/opt/airflow/models"

# Lista de nombres de modelos que esperamos encontrar
model_names = ["random_forest", "decision_tree", "svm", "logistic_regression"]

# Cargamos los modelos desde el directorio compartido (asegúrate de que la ruta coincide con el mapeo en Docker)
models = {}

def load_models():
    global models
    models = {}  # Reinicia el diccionario
    print("Cargando modelos desde:", MODEL_DIR)
    try:
        archivos = os.listdir(MODEL_DIR)
        print("Archivos en el directorio:", archivos)
    except Exception as e:
        print("Error al listar el directorio:", e)
    
    for name in model_names:
        file_path = os.path.join(MODEL_DIR, f"{name}.pkl")
        if os.path.exists(file_path):
            try:
                models[name] = joblib.load(file_path)
                print(f"Modelo {name} cargado exitosamente desde {file_path}")
            except Exception as e:
                print(f"Error al cargar el modelo {name}: {e}")
        else:
            print(f"Warning: El modelo {name} NO existe en {file_path}")
    print("Modelos actualmente cargados:", list(models.keys()))

# Cargar los modelos al iniciar la API
load_models()
# Modelo seleccionado por defecto
selected_model = "random_forest"

# Definición del esquema de entrada para la predicción
class PenguinFeatures(BaseModel):
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float
    island: int

@app.post("/predict/")
def predict(features: PenguinFeatures):
    global selected_model
    if selected_model not in models:
        raise HTTPException(status_code=400, detail=f"Modelo {selected_model} no encontrado.")
    
    model_data = models[selected_model]
    model = model_data["model"]
    scaler = model_data["scaler"]

    # Preparar los datos de entrada
    input_data = np.array([[features.culmen_length_mm,
                             features.culmen_depth_mm,
                             features.flipper_length_mm,
                             features.body_mass_g,
                             features.island]])
    input_scaled = scaler.transform(input_data)
    prediction = model.predict(input_scaled)
    sex = "MALE" if prediction[0] == 1 else "FEMALE"
    
    return {"selected_model": selected_model, "prediction": sex}

@app.put("/select_model/{model_name}")
def select_model(model_name: str):
    global selected_model
    if model_name not in models:
        raise HTTPException(status_code=400, detail="Modelo no encontrado.")
    selected_model = model_name
    return {"message": f"Modelo cambiado a {model_name}"}

@app.get("/")
def home():
    return {"message": "API de Predicción de Pingüinos con FastAPI"}

@app.post("/reload_models/")
def reload_models():
    load_models()
    return {"message": "Modelos recargados", "models": list(models.keys())}