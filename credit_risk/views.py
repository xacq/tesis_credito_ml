import os
import json
import joblib
import pandas as pd
import numpy as np

from django.conf import settings
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy

from .forms import CreditForm, FileUploadForm
from .models import CreditEvaluation


# =========================
# CARGA DE MODELO AL INICIAR
# =========================
MODEL_PATH = os.path.join(settings.BASE_DIR, 'credit_risk', 'ml_models', 'modelo_riesgo.pkl')
SCALER_PATH = os.path.join(settings.BASE_DIR, 'credit_risk', 'ml_models', 'scaler.pkl')
FEATURES_PATH = os.path.join(settings.BASE_DIR, 'credit_risk', 'ml_models', 'features.json')

modelo = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH) if os.path.exists(SCALER_PATH) else None

with open(FEATURES_PATH, 'r', encoding='utf-8') as f:
    model_columns = json.load(f)


# =========================
# LOGIN VIEW
# =========================
class CustomLoginView(LoginView):
    template_name = 'core/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')


# =========================
# UTIL: ARMAR INPUT DEL MODELO
# =========================
def build_model_input(data: dict) -> pd.DataFrame:
    df_input = pd.DataFrame(0, index=[0], columns=model_columns)

    # Numéricas
    cols_num = ['dias_mora_prom', 'edad', 'ingreso_mensual', 'ventas_anuales', 'monto_solicitado', 'plazo_meses']
    for col in cols_num:
        if col in df_input.columns:
            df_input[col] = float(data.get(col, 0) or 0)

    # Booleanas
    bool_map = {
        'tiene_garante': data.get('tiene_garante', False),
        'propiedad_completa': data.get('propiedad_completa', False),
        'estado_legal': data.get('estado_legal', False),
        'rastreo_instalado': data.get('rastreo_instalado', 0),
    }
    for col, val in bool_map.items():
        if col in df_input.columns:
            df_input[col] = 1 if val else 0

    # Estado civil (one-hot)
    estado_civil = data.get('estado_civil')
    if estado_civil:
        key_direct = f"estado_civil_{estado_civil}"
        if key_direct in df_input.columns:
            df_input[key_direct] = 1
        else:
            map_ec = {'UnionLibre': 'Unión Libre'}
            estado_civil_norm = map_ec.get(estado_civil, estado_civil)
            key_norm = f"estado_civil_{estado_civil_norm}"
            if key_norm in df_input.columns:
                df_input[key_norm] = 1

    # Garantía (one-hot)
    garantia = data.get('garantia')
    if garantia:
        key = f"garantia_{garantia}"
        if key in df_input.columns:
            df_input[key] = 1

    # Escalado (si aplica)
    if scaler is not None:
        df_scaled = scaler.transform(df_input)
        df_input = pd.DataFrame(df_scaled, index=df_input.index, columns=df_input.columns)

    return df_input


# =========================
# VISTA PRINCIPAL: PREDICCIÓN
# =========================
@login_required
def predict_view(request):
    resultado = None
    probabilidad = None

    if request.method == 'POST':
        form = CreditForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data

            df_input = build_model_input(data)

            pred = int(modelo.predict(df_input)[0])
            prob = float(modelo.predict_proba(df_input)[0][1])
            probabilidad = round(prob * 100, 2)

            if prob >= 0.70:
                recomendacion = "ALTO"
                resultado = "RIESGO ALTO (Rechazar / Revisar estrictamente)"
            elif prob >= 0.40:
                recomendacion = "MEDIO"
                resultado = "RIESGO MEDIO (Revisión manual)"
            else:
                recomendacion = "BAJO"
                resultado = "RIESGO BAJO (Aprobar)"

            # Guardar evaluación en BD
            CreditEvaluation.objects.create(
                user=request.user,
                edad=data['edad'],
                estado_civil=data['estado_civil'],
                ingreso_mensual=data['ingreso_mensual'],
                ventas_anuales=data.get('ventas_anuales', 0) or 0,
                monto_solicitado=data['monto_solicitado'],
                plazo_meses=data['plazo_meses'],
                dias_mora_prom=data['dias_mora_prom'],
                garantia=data['garantia'],
                tiene_garante=bool(data.get('tiene_garante', False)),
                propiedad_completa=bool(data.get('propiedad_completa', False)),
                estado_legal=bool(data.get('estado_legal', False)),
                prob_riesgo=prob,
                prediccion=pred,
                recomendacion=recomendacion
            )
        else:
            messages.error(request, "Formulario inválido. Revisa los datos ingresados.")
    else:
        form = CreditForm()

    return render(request, 'credit_risk/home.html', {
        'form': form,
        'resultado': resultado,
        'probabilidad': probabilidad
    })


# =========================
# PREDICCIÓN POR LOTES
# =========================
@login_required
def batch_predict_view(request):
    results = None

    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']

            try:
                if file.name.endswith('.csv'):
                    df = pd.read_csv(file)
                elif file.name.endswith(('.xls', '.xlsx')):
                    df = pd.read_excel(file)
                else:
                    messages.error(request, "Formato no soportado. Use CSV (.csv) o Excel (.xlsx)")
                    return render(request, 'credit_risk/batch_predict.html', {'form': form})

                required_columns = [
                    'dias_mora_prom', 'edad', 'ingreso_mensual', 'ventas_anuales',
                    'monto_solicitado', 'plazo_meses',
                    'garantia', 'tiene_garante', 'propiedad_completa', 'estado_legal',
                    'estado_civil'
                ]
                missing = [c for c in required_columns if c not in df.columns]
                if missing:
                    messages.error(request, f"Faltan columnas: {', '.join(missing)}")
                    return render(request, 'credit_risk/batch_predict.html', {'form': form})

                predictions = []
                probabilities = []
                recs = []

                for _, row in df.iterrows():
                    df_input = build_model_input(row.to_dict())
                    pred = int(modelo.predict(df_input)[0])
                    prob = float(modelo.predict_proba(df_input)[0][1])

                    predictions.append("RIESGO ALTO" if pred == 1 else "RIESGO BAJO")
                    probabilities.append(round(prob * 100, 2))

                    if prob >= 0.70:
                        recs.append("ALTO")
                    elif prob >= 0.40:
                        recs.append("MEDIO")
                    else:
                        recs.append("BAJO")

                df['Prediccion_Riesgo'] = predictions
                df['Probabilidad_Impago_%'] = probabilities
                df['Recomendacion'] = recs

                results = df.to_dict(orient='records')
                messages.success(request, f"✅ Se procesaron {len(df)} registros exitosamente.")

            except Exception as e:
                messages.error(request, f"❌ Error procesando el archivo: {str(e)}")
    else:
        form = FileUploadForm()

    return render(request, 'credit_risk/batch_predict.html', {'form': form, 'results': results})


# =========================
# HISTORIAL
# =========================
@login_required
def historial_view(request):
    evaluaciones = CreditEvaluation.objects.select_related('user').order_by('-created_at')[:200]
    return render(request, 'credit_risk/historial.html', {'evaluaciones': evaluaciones})


from django.shortcuts import get_object_or_404

@login_required
def evaluation_detail_view(request, pk):
    evaluacion = get_object_or_404(CreditEvaluation, pk=pk)
    return render(request, 'credit_risk/evaluacion_detalle.html', {'e': evaluacion})


from .forms import DecisionForm

@login_required
def evaluation_update_view(request, pk):
    evaluacion = get_object_or_404(CreditEvaluation, pk=pk)

    if request.method == 'POST':
        form = DecisionForm(request.POST, instance=evaluacion)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Caso actualizado.")
            return render(request, 'credit_risk/evaluacion_detalle.html', {'e': evaluacion})
    else:
        form = DecisionForm(instance=evaluacion)

    return render(request, 'credit_risk/evaluacion_editar.html', {'form': form, 'e': evaluacion})

