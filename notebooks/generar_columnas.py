import os
import joblib
import pandas as pd

# 1. Configurar rutas
# Asumimos que este script está en la carpeta raíz del proyecto (c:\tesis_credito_ml\)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'credit_risk', 'ml_models')
MODEL_PATH = os.path.join(MODEL_DIR, 'modelo_riesgo_v1.pkl')
OUTPUT_PATH = os.path.join(MODEL_DIR, 'model_columns.pkl')

def main():
    print("--- Extractor de Columnas del Modelo ---")
    print(f"Buscando modelo en: {MODEL_PATH}")

    if not os.path.exists(MODEL_PATH):
        print("ERROR: No se encontró el archivo del modelo. Verifica la ruta.")
        return

    try:
        # 2. Cargar el modelo existente
        print("Cargando modelo...")
        model = joblib.load(MODEL_PATH)
        
        # 3. Extraer nombres de características (features)
        # Scikit-learn guarda esto en el atributo 'feature_names_in_'
        if hasattr(model, 'feature_names_in_'):
            columns = list(model.feature_names_in_)
            print(f"¡Éxito! Se encontraron {len(columns)} columnas en el modelo.")
            print(f"Ejemplo: {columns[:5]}...")
            
            # 4. Guardar la lista en el archivo pickle
            joblib.dump(columns, OUTPUT_PATH)
            print(f"\nArchivo generado en: {OUTPUT_PATH}")
            print("Ahora puedes ejecutar 'python manage.py runserver' nuevamente.")
        else:
            print("ERROR: El modelo no contiene el atributo 'feature_names_in_'.")
            print("Esto sucede si se entrenó con una versión antigua de scikit-learn o usando arrays de Numpy en vez de Pandas.")

    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    main()