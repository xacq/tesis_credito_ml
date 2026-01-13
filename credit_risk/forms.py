from django import forms

class CreditForm(forms.Form):

    OPCIONES_GARANTIA = [
        ('Personal', 'Personal'),
        ('Prendaria', 'Prendaria'),
        ('Hipotecaria', 'Hipotecaria'),
        ('Autoliquidable', 'Autoliquidable')
    ]

    OPCIONES_ESTADO_CIVIL = [
        ('Soltero', 'Soltero'),
        ('Casado', 'Casado'),
        ('Divorciado', 'Divorciado'),
        ('Viudo', 'Viudo'),
        ('UnionLibre', 'Unión Libre')
    ]

    # Datos demográficos
    edad = forms.IntegerField(
        label="Edad",
        min_value=19,
        max_value=80
    )

    estado_civil = forms.ChoiceField(
        choices=OPCIONES_ESTADO_CIVIL,
        label="Estado Civil"
    )

    # Capacidad económica
    ingreso_mensual = forms.FloatField(
        label="Ingreso Mensual ($)"
    )

    ventas_anuales = forms.FloatField(
        label="Ventas Anuales ($)",
        required=False,
        initial=0
    )

    # Crédito solicitado
    monto_solicitado = forms.FloatField(
        label="Monto Solicitado ($)"
    )

    plazo_meses = forms.IntegerField(
        label="Plazo (Meses)"
    )

    # Riesgo y respaldo
    dias_mora_prom = forms.IntegerField(
        label="Días de Mora Promedio",
        min_value=0
    )

    garantia = forms.ChoiceField(
        choices=OPCIONES_GARANTIA,
        label="Tipo de Garantía"
    )

    tiene_garante = forms.BooleanField(
        label="¿Tiene Garante?",
        required=False
    )

    propiedad_completa = forms.BooleanField(
        label="¿Posee el 100% de un bien?",
        required=False
    )

    estado_legal = forms.BooleanField(
        label="¿Tiene juicios o insolvencia vigente?",
        required=False
    )


class FileUploadForm(forms.Form):
    file = forms.FileField(
        label='Selecciona un archivo (Excel .xlsx o CSV .csv)',
        help_text='El archivo debe contener las columnas requeridas por el modelo.'
    )

from django import forms
from .models import CreditEvaluation

class DecisionForm(forms.ModelForm):
    class Meta:
        model = CreditEvaluation
        fields = ['estado_caso', 'decision_final', 'comentario_analista']
