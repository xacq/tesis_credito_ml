import os
import joblib
import json

# 1. Configurar rutas
# Asumimos que este script está en la carpeta raíz del proyecto (c:\tesis_credito_ml\)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'credit_risk', 'ml_models')
FEATURES_JSON_PATH = os.path.join(BASE_DIR, 'web_app', 'credit_risk', 'ml_models', 'features.json')
OUTPUT_PATH = os.path.join(MODEL_DIR, 'model_columns.pkl')

def main():
    print("--- Extractor de Columnas del Modelo (desde JSON) ---")
    print(f"Buscando archivo de features en: {FEATURES_JSON_PATH}")

    if not os.path.exists(FEATURES_JSON_PATH):
        print("ERROR: No se encontró el archivo 'features.json'. Verifica la ruta.")
        return

    try:
        # 2. Cargar las columnas desde JSON
        print("Cargando columnas desde JSON...")
        with open(FEATURES_JSON_PATH, 'r') as f:
            columns = json.load(f)

        print(f"¡Éxito! Se encontraron {len(columns)} columnas en el archivo JSON.")
        print(f"Ejemplo: {columns[:5]}...")

        # 3. Guardar la lista en el archivo pickle
        joblib.dump(columns, OUTPUT_PATH)
        print(f"\nArchivo generado en: {OUTPUT_PATH}")
        print("Ahora puedes ejecutar 'python manage.py runserver' nuevamente.")

    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    main()
