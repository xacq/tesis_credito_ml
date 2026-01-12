'''
Explicación del proceso de generación del dataset simulado

Con el objetivo de entrenar y evaluar un modelo de aprendizaje automático orientado a la gestión del riesgo crediticio, se desarrolló un script en Python que permite la generación de un conjunto de datos sintético, estructurado conforme a las políticas crediticias vigentes de la Cooperativa de Ahorro y Crédito Tulcán.
El uso de datos simulados responde a la necesidad de preservar la confidencialidad de la información real de los socios, sin perder coherencia técnica ni lógica institucional en la toma de decisiones crediticias.

Estructura general del código
El script está organizado en bloques funcionales que replican las principales dimensiones consideradas en el análisis crediticio de la cooperativa: información personal, variables económicas, características del crédito, evaluación de riesgo y resultado final de la operación.
En primer lugar, se definen parámetros globales como el número de registros a generar y una semilla aleatoria, lo que garantiza la reproducibilidad de los resultados, aspecto fundamental en trabajos académicos y procesos de validación.
Posteriormente, se establecen los catálogos de valores permitidos para variables categóricas, tales como el segmento de crédito, el estado civil, el tipo de garantía y el score interno. En este punto se destaca que el score se limita exclusivamente a las categorías AAA, AA, A y Rechazado, eliminando estados intermedios que no representan una decisión crediticia final.

Generación de variables personales y económicas
Para cada registro, se simulan variables demográficas básicas, como la edad y el estado civil del solicitante. La edad se genera respetando el mínimo establecido por la política institucional (19 años), utilizando una distribución triangular que concentra la mayor probabilidad en edades económicamente activas.
Los ingresos mensuales se simulan mediante una distribución lognormal, técnica comúnmente utilizada para representar ingresos en contextos reales, dado que permite reflejar la asimetría típica del ingreso económico. En el caso del microcrédito, se calcula adicionalmente el nivel de ventas anuales, alineándolo con la naturaleza productiva del segmento.

Definición del tipo de crédito y sus características
El tipo de segmento crediticio se asigna de manera aleatoria entre consumo, microcrédito, inmobiliario y ahorros suficientes. A partir de esta segmentación, el código establece automáticamente el producto específico, el monto solicitado y el plazo del crédito, respetando rangos coherentes con las prácticas habituales del sistema financiero cooperativo.
Este enfoque permite que cada registro tenga consistencia interna, evitando combinaciones irreales, como montos elevados en productos de bajo riesgo o garantías incompatibles con el tipo de crédito.

Asignación del score interno
El score interno del socio se asigna en función del comportamiento histórico simulado, representado principalmente por los días promedio de mora. Esta lógica replica el criterio institucional de priorizar el historial de pago como indicador clave de riesgo.
Los solicitantes sin mora son clasificados como AAA o AA, aquellos con mora leve como A, y los casos con mora superior a los umbrales definidos por la política son clasificados directamente como Rechazados. De esta manera, el score refleja una decisión crediticia final, adecuada para el entrenamiento de modelos supervisados.

Incorporación de políticas de riesgo y garantías
El script incluye variables críticas desde el punto de vista normativo y legal, como la existencia de procesos judiciales, la propiedad completa del bien ofrecido como respaldo, la presencia de garante y la instalación de dispositivos de rastreo en créditos vehiculares.
La asignación del tipo de garantía se realiza conforme al segmento crediticio, asegurando que, por ejemplo, los créditos inmobiliarios cuenten con garantía hipotecaria y los créditos respaldados por ahorros sean autoliquidables.

Construcción de la variable objetivo
La variable objetivo del modelo, denominada riesgo_real, se genera a partir de una probabilidad base de incumplimiento, la cual se ajusta dinámicamente según las condiciones de riesgo definidas en el manual de crédito.
Factores como mora elevada, score rechazado, problemas legales, incumplimiento de límites por edad y monto, debilidad de la garantía o riesgos legales sobre la propiedad incrementan la probabilidad de impago. Finalmente, se clasifica cada registro como buen o mal pagador, permitiendo contar con una variable dependiente adecuada para el entrenamiento y validación de modelos predictivos.

Resultado y utilidad del dataset
El resultado del proceso es un archivo en formato CSV que contiene un conjunto de datos estructurado, coherente y alineado con las políticas institucionales, apto para ser utilizado en experimentos de aprendizaje automático orientados a la predicción de riesgo crediticio.
Este enfoque permite evaluar el comportamiento del modelo bajo reglas realistas, facilitando el análisis de variables relevantes, la interpretación de resultados y la justificación técnica de las decisiones automatizadas, sin comprometer información sensible de la cooperativa.
'''

import pandas as pd
import numpy as np
import random
import os

# =========================
# CONFIGURACIÓN GENERAL
# =========================
NUM_REGISTROS = 1000
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

# =========================
# OPCIONES DEFINIDAS SEGÚN POLÍTICA
# =========================
OPCIONES_SCORE = ['AAA', 'AA', 'A', 'Rechazado']
OPCIONES_SEGMENTO = ['Consumo', 'Microcrédito', 'Inmobiliario', 'Ahorros Suficientes']
OPCIONES_CIVIL = ['Soltero', 'Casado', 'Divorciado', 'Viudo', 'Unión Libre']
OPCIONES_GARANTIA = ['Personal', 'Prendaria', 'Hipotecaria', 'Autoliquidable']

# =========================
# FUNCIÓN GENERADORA
# =========================
def generar_dataset_simulado():
    data = []

    for _ in range(NUM_REGISTROS):

        # -------------------------
        # 1. VARIABLES PERSONALES
        # -------------------------
        edad = int(np.random.triangular(19, 35, 75))
        estado_civil = random.choice(OPCIONES_CIVIL)

        # -------------------------
        # 2. VARIABLES ECONÓMICAS
        # -------------------------
        ingreso_mensual = round(np.random.lognormal(mean=6.5, sigma=0.5), 2)
        ventas_anuales = 0

        # -------------------------
        # 3. VARIABLES DEL CRÉDITO
        # -------------------------
        segmento = random.choice(OPCIONES_SEGMENTO)

        if segmento == 'Microcrédito':
            ventas_anuales = round(ingreso_mensual * 12 * 1.5, 2)
            producto = random.choice(['Mi Negocio', 'Agrícola-Ganadero', 'Vehicular Trabajo'])
            monto = round(random.uniform(1000, 20000), 2)

        elif segmento == 'Consumo':
            producto = random.choice(['Consumo General', 'Sueldo', 'Digital'])
            monto = round(random.uniform(500, 15000), 2)

        elif segmento == 'Inmobiliario':
            producto = 'Vivienda'
            monto = round(random.uniform(15000, 80000), 2)

        else:
            producto = 'Back-to-back'
            monto = round(random.uniform(500, 50000), 2)

        plazo = random.choice([12, 24, 36, 48, 60, 84])

        # -------------------------
        # 4. VARIABLES DE RIESGO
        # -------------------------
        dias_mora_prom = int(np.random.exponential(scale=5))

        # LÓGICA DE SCORE AJUSTADA (SIN "ANALISTA")
        if dias_mora_prom == 0:
            score = np.random.choice(['AAA', 'AA'], p=[0.6, 0.4])
        elif dias_mora_prom <= 5:
            score = 'A'
        elif dias_mora_prom <= 10:
            score = 'A'
        else:
            score = 'Rechazado'

        estado_legal = np.random.choice([0, 1], p=[0.95, 0.05])  # 1 = Juicios
        propiedad_completa = np.random.choice([0, 1], p=[0.2, 0.8])
        tiene_garante = np.random.choice([0, 1])

        # -------------------------
        # 5. GARANTÍA
        # -------------------------
        if segmento == 'Inmobiliario':
            garantia = 'Hipotecaria'
        elif segmento == 'Ahorros Suficientes':
            garantia = 'Autoliquidable'
        else:
            garantia = random.choice(['Personal', 'Prendaria'])

        rastreo = 0
        if 'Vehicular' in producto:
            rastreo = np.random.choice([0, 1], p=[0.1, 0.9])

        # -------------------------
        # 6. VARIABLE OBJETIVO
        # -------------------------
        probabilidad_impago = 0.1

        if dias_mora_prom > 10:
            probabilidad_impago += 0.4

        if score == 'Rechazado':
            probabilidad_impago += 0.5

        if estado_legal == 1:
            probabilidad_impago += 0.8

        if edad < 21 and monto > 3000:
            probabilidad_impago += 0.3

        if garantia == 'Personal' and monto > 10000:
            probabilidad_impago += 0.2

        if segmento == 'Inmobiliario' and propiedad_completa == 0:
            probabilidad_impago += 0.3

        riesgo_real = 1 if random.random() < probabilidad_impago else 0

        # -------------------------
        # 7. REGISTRO FINAL
        # -------------------------
        data.append([
            score, dias_mora_prom, edad, ingreso_mensual, ventas_anuales,
            segmento, producto, monto, plazo, garantia,
            propiedad_completa, estado_civil, estado_legal, tiene_garante,
            rastreo, riesgo_real
        ])

    columnas = [
        'score_interno', 'dias_mora_prom', 'edad', 'ingreso_mensual', 'ventas_anuales',
        'segmento_credito', 'producto', 'monto_solicitado', 'plazo_meses', 'garantia',
        'propiedad_completa', 'estado_civil', 'estado_legal', 'tiene_garante',
        'rastreo_instalado', 'riesgo_real'
    ]

    return pd.DataFrame(data, columns=columnas)

# =========================
# EJECUCIÓN Y EXPORTACIÓN
# =========================
df_simulado = generar_dataset_simulado()
output_path = os.path.join(os.path.dirname(__file__), 'datos_credito_simulados.csv')
df_simulado.to_csv(output_path, index=False)

print(f"Dataset generado exitosamente: {output_path}")
print(df_simulado.head())
