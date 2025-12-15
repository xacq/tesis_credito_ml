import pandas as pd
import numpy as np
import random
import os

# Configuración
NUM_REGISTROS = 1000
SEED = 42
np.random.seed(SEED)
random.seed(SEED)

# Definición de opciones basadas en Tabla 6 y Apéndice A
OPCIONES_SCORE = ['AAA', 'AA', 'A', 'Analista', 'Rechazado']
OPCIONES_SEGMENTO = ['Consumo', 'Microcrédito', 'Inmobiliario', 'Ahorros Suficientes']
OPCIONES_CIVIL = ['Soltero', 'Casado', 'Divorciado', 'Viudo', 'Unión Libre']
OPCIONES_GARANTIA = ['Personal', 'Prendaria', 'Hipotecaria', 'Autoliquidable']

def generar_dataset_simulado():
    data = []

    for _ in range(NUM_REGISTROS):
        # 1. Variables Demográficas y Personales
        edad = int(np.random.triangular(19, 35, 75)) # Min 19 años [cite: 511]
        estado_civil = random.choice(OPCIONES_CIVIL)
        
        # 2. Variables Económicas
        # Ingresos: Distribución log-normal para simular realidad económica
        ingreso_mensual = round(np.random.lognormal(mean=6.5, sigma=0.5), 2) 
        
        # Ventas anuales (solo relevante para microcrédito, otros 0)
        ventas_anuales = 0
        
        # 3. Variables del Crédito
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
        
        # 4. Variables de Riesgo (Políticas Institucionales)
        dias_mora_prom = int(np.random.exponential(scale=5)) # La mayoría paga bien (cerca de 0)
        
        # Asignar Score basado en mora (Lógica simulada)
        if dias_mora_prom == 0:
            score = np.random.choice(['AAA', 'AA'], p=[0.6, 0.4])
        elif dias_mora_prom <= 5:
            score = 'A'
        elif dias_mora_prom <= 15:
            score = 'Analista'
        else:
            score = 'Rechazado'

        # Reglas específicas del Manual [Apéndice A]
        estado_legal = np.random.choice([0, 1], p=[0.95, 0.05]) # 1 = Tiene Juicios 
        propiedad_completa = np.random.choice([0, 1], p=[0.2, 0.8]) # 0 = Derechos y Acciones (Riesgo) 
        tiene_garante = np.random.choice([0, 1])
        
        # Garantía
        if segmento == 'Inmobiliario':
            garantia = 'Hipotecaria'
        elif segmento == 'Ahorros Suficientes':
            garantia = 'Autoliquidable'
        else:
            garantia = random.choice(['Personal', 'Prendaria'])
            
        rastreo = 0
        if 'Vehicular' in producto:
            rastreo = np.random.choice([0, 1], p=[0.1, 0.9]) # [cite: 531]

        # 5. Generación de la Variable Objetivo (Target) "riesgo_real"
        # Aquí inyectamos patrones para que el ML tenga qué aprender
        probabilidad_impago = 0.1 # Base
        
        # Penalizaciones por políticas
        if dias_mora_prom > 10: probabilidad_impago += 0.4
        if score == 'Rechazado': probabilidad_impago += 0.5
        if estado_legal == 1: probabilidad_impago += 0.8 # Política estricta 
        if edad < 21 and monto > 3000: probabilidad_impago += 0.3 # Riesgo alto por edad/monto 
        if garantia == 'Personal' and monto > 10000: probabilidad_impago += 0.2
        if segmento == 'Inmobiliario' and propiedad_completa == 0: probabilidad_impago += 0.3 # Riesgo legal 
        
        # Definir clase final (0 = Buen Pagador, 1 = Mal Pagador/Alto Riesgo)
        riesgo_real = 1 if random.random() < probabilidad_impago else 0

        # Agregar fila
        data.append([
            score, dias_mora_prom, edad, ingreso_mensual, ventas_anuales,
            segmento, producto, monto, plazo, garantia,
            propiedad_completa, estado_civil, estado_legal, tiene_garante,
            rastreo, riesgo_real
        ])

    # Crear DataFrame con nombres de columnas de Tabla 6 [cite: 455]
    cols = [
        'score_interno', 'dias_mora_prom', 'edad', 'ingreso_mensual', 'ventas_anuales',
        'segmento_credito', 'producto', 'monto_solicitado', 'plazo_meses', 'garantia',
        'propiedad_completa', 'estado_civil', 'estado_legal', 'tiene_garante',
        'rastreo_instalado', 'riesgo_real'
    ]
    
    df = pd.DataFrame(data, columns=cols)
    return df

# Ejecutar y guardar
df_simulado = generar_dataset_simulado()
output_path = os.path.join(os.path.dirname(__file__), 'datos_credito_simulados.csv')
df_simulado.to_csv(output_path, index=False)
print(f"Dataset generado exitosamente: {output_path}")
print(df_simulado.head())