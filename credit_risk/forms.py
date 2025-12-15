from django import forms

class CreditForm(forms.Form):
    # Opciones basadas en tu tesis y dataset simulado
    OPCIONES_SCORE = [('AAA', 'AAA'), ('AA', 'AA'), ('A', 'A'), ('Analista', 'Analista'), ('Rechazado', 'Rechazado')]
    OPCIONES_SEGMENTO = [('Consumo', 'Consumo'), ('Microcrédito', 'Microcrédito'), ('Inmobiliario', 'Inmobiliario'), ('Ahorros Suficientes', 'Ahorros Suficientes')]
    OPCIONES_GARANTIA = [('Personal', 'Personal'), ('Prendaria', 'Prendaria'), ('Hipotecaria', 'Hipotecaria'), ('Autoliquidable', 'Autoliquidable')]
    
    # Campos del formulario
    score_interno = forms.ChoiceField(choices=OPCIONES_SCORE, label="Calificación Interna")
    dias_mora_prom = forms.IntegerField(label="Días de Mora Promedio", min_value=0)
    edad = forms.IntegerField(label="Edad", min_value=19, max_value=80)
    ingreso_mensual = forms.FloatField(label="Ingreso Mensual ($)")
    ventas_anuales = forms.FloatField(label="Ventas Anuales (Si aplica)", required=False, initial=0)
    monto_solicitado = forms.FloatField(label="Monto Solicitado ($)")
    plazo_meses = forms.IntegerField(label="Plazo (Meses)")
    
    segmento_credito = forms.ChoiceField(choices=OPCIONES_SEGMENTO, label="Segmento")
    garantia = forms.ChoiceField(choices=OPCIONES_GARANTIA, label="Tipo de Garantía")
    tiene_garante = forms.BooleanField(label="¿Tiene Garante?", required=False)
    propiedad_completa = forms.BooleanField(label="¿Posee 100% Bienes?", required=False)
    estado_legal = forms.BooleanField(label="¿Tiene Juicios/Insolvencia?", required=False)

class FileUploadForm(forms.Form):
    file = forms.FileField(
        label='Selecciona un archivo (Excel .xlsx o CSV .csv)',
        help_text='El archivo debe contener las columnas requeridas por el modelo.'
    )
