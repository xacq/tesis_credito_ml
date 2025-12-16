from django.shortcuts import render

# Create your views here.
import os
import joblib
import pandas as pd
import numpy as np
from django.shortcuts import render
from django.conf import settings
from .forms import CreditForm

# 1. Cargar modelo y scaler al iniciar el servidor (para eficiencia)
MODEL_PATH = os.path.join(settings.BASE_DIR, 'credit_risk/ml_models/modelo_riesgo_v1.pkl')
SCALER_PATH = os.path.join(settings.BASE_DIR, 'credit_risk/ml_models/scaler.pkl')
COLUMNS_PATH = os.path.join(settings.BASE_DIR, 'credit_risk/ml_models/model_columns.pkl')

modelo = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
model_columns = joblib.load(COLUMNS_PATH)

def predict_view(request):
    resultado = None
    probabilidad = None
    
    if request.method == 'POST':
        form = CreditForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            
            # --- PREPROCESAMIENTO (Igual que en Notebook 01) ---
            
            # 1. Crear DataFrame base con una sola fila
            # Nota: Debemos inicializar TODAS las columnas que el modelo espera (One-Hot Encoding)
            # Para simplificar, creamos un diccionario con valores por defecto en 0
            
            # Mapa de Score
            mapa_score = {'AAA': 5, 'AA': 4, 'A': 3, 'Analista': 2, 'Rechazado': 1}
            score_num = mapa_score[data['score_interno']]
            
            # Estructura de entrada cruda para procesar
            input_dict = {
                'dias_mora_prom': data['dias_mora_prom'],
                'edad': data['edad'],
                'ingreso_mensual': data['ingreso_mensual'],
                'ventas_anuales': data['ventas_anuales'],
                'monto_solicitado': data['monto_solicitado'],
                'plazo_meses': data['plazo_meses'],
                'score_interno_num': score_num,
                'ventas_anuales': data['ventas_anuales'],
                # Variables booleanas directas
                'tiene_garante': 1 if data['tiene_garante'] else 0,
                'propiedad_completa': 1 if data['propiedad_completa'] else 0,
                'estado_legal': 1 if data['estado_legal'] else 0,
                'rastreo_instalado': 0 # Asumimos 0 o lo agregas al form si deseas
            }
            
            # --- ONE HOT ENCODING MANUAL ---
            # El modelo espera columnas específicas como 'segmento_credito_Microcrédito'
            # Aquí definimos las que salieron del entrenamiento (revisar X_train.columns)

            # Crear DataFrame lleno de ceros
            df_input = pd.DataFrame(0, index=[0], columns=model_columns)
            
            # Llenar numéricas
            cols_num = ['dias_mora_prom', 'edad', 'ingreso_mensual', 'ventas_anuales', 'monto_solicitado', 'plazo_meses']
            for col in cols_num:
                df_input[col] = input_dict[col]
            
            df_input['score_interno_num'] = score_num
            df_input['tiene_garante'] = input_dict['tiene_garante']
            df_input['propiedad_completa'] = input_dict['propiedad_completa']
            df_input['estado_legal'] = input_dict['estado_legal']

            # Activar Dummies según selección
            seg = f"segmento_credito_{data['segmento_credito']}"
            if seg in df_input.columns:
                df_input[seg] = 1
                
            gar = f"garantia_{data['garantia']}"
            if gar in df_input.columns:
                df_input[gar] = 1

            # Manejo genérico para estado_civil (causante del error original)
            if 'estado_civil' in data:
                ec = f"estado_civil_{data['estado_civil']}"
                if ec in df_input.columns:
                    df_input[ec] = 1

            # --- ESCALADO ---
            df_input[cols_num] = scaler.transform(df_input[cols_num])
            
            # --- PREDICCIÓN ---
            pred = modelo.predict(df_input)[0]
            prob = modelo.predict_proba(df_input)[0][1]
            
            resultado = "RIESGO ALTO (Rechazar)" if pred == 1 else "RIESGO BAJO (Aprobar)"
            probabilidad = round(prob * 100, 2)
            
    else:
        form = CreditForm()

    return render(request, 'credit_risk/home.html', {
        'form': form, 
        'resultado': resultado, 
        'probabilidad': probabilidad
    })

def batch_predict_view(request):
    """Vista para procesamiento de predicciones en lote desde archivos CSV/Excel"""
    from .forms import FileUploadForm
    from django.contrib import messages
    
    results = None
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            try:
                # 1. Leer archivo según extensión
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(file)
                else:
                    messages.error(request, "Formato no soportado. Use CSV (.csv) o Excel (.xlsx)")
                    return render(request, 'credit_risk/batch_predict.html', {'form': form})

                # 2. Validar columnas requeridas
                required_columns = [
                    'score_interno', 'dias_mora_prom', 'edad', 'ingreso_mensual', 
                    'ventas_anuales', 'monto_solicitado', 'plazo_meses', 
                    'segmento_credito', 'garantia', 'tiene_garante', 
                    'propiedad_completa', 'estado_legal'
                ]
                
                missing_cols = [col for col in required_columns if col not in df.columns]
                if missing_cols:
                    messages.error(request, f"Faltan las siguientes columnas: {', '.join(missing_cols)}")
                    return render(request, 'credit_risk/batch_predict.html', {'form': form})

                # 3. Procesar cada fila y hacer predicciones
                predictions = []
                probabilities = []
                
                mapa_score = {'AAA': 5, 'AA': 4, 'A': 3, 'Analista': 2, 'Rechazado': 1}
                
                
                cols_num = ['dias_mora_prom', 'edad', 'ingreso_mensual', 'ventas_anuales', 'monto_solicitado', 'plazo_meses']
                
                for idx, row in df.iterrows():
                    # Convertir score a numérico
                    score_num = mapa_score.get(row['score_interno'], 2)
                    
                    # Crear DataFrame con estructura del modelo
                    df_input = pd.DataFrame(0, index=[0], columns=model_columns)
                    
                    # Llenar valores numéricos
                    for col in cols_num:
                        df_input[col] = row[col]
                    
                    df_input['score_interno_num'] = score_num
                    df_input['tiene_garante'] = 1 if row['tiene_garante'] else 0
                    df_input['propiedad_completa'] = 1 if row['propiedad_completa'] else 0
                    df_input['estado_legal'] = 1 if row['estado_legal'] else 0
                    df_input['rastreo_instalado'] = 0
                    
                    # Activar columnas dummy según valores
                    seg = f"segmento_credito_{row['segmento_credito']}"
                    if seg in df_input.columns:
                        df_input[seg] = 1
                    
                    gar = f"garantia_{row['garantia']}"
                    if gar in df_input.columns:
                        df_input[gar] = 1
                    
                    # Manejo genérico para estado_civil en carga masiva
                    if 'estado_civil' in row:
                        ec = f"estado_civil_{row['estado_civil']}"
                        if ec in df_input.columns:
                            df_input[ec] = 1

                    # Escalar variables numéricas
                    df_input[cols_num] = scaler.transform(df_input[cols_num])
                    
                    # Realizar predicción
                    pred = modelo.predict(df_input)[0]
                    prob = modelo.predict_proba(df_input)[0][1]
                    
                    predictions.append("RIESGO ALTO" if pred == 1 else "RIESGO BAJO")
                    probabilities.append(round(prob * 100, 2))
                
                # 4. Agregar resultados al DataFrame original
                df['Prediccion_Riesgo'] = predictions
                df['Probabilidad_Impago_%'] = probabilities
                
                # Convertir a lista de diccionarios para la plantilla
                results = df.to_dict(orient='records')
                messages.success(request, f"✅ Se procesaron {len(df)} registros exitosamente.")
                
            except Exception as e:
                messages.error(request, f"❌ Error procesando el archivo: {str(e)}")
    else:
        form = FileUploadForm()
    
    return render(request, 'credit_risk/batch_predict.html', {'form': form, 'results': results})