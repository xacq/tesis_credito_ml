# Tesis Crédito ML

Este proyecto implementa un modelo de Machine Learning para la evaluación de riesgo crediticio, incluyendo la generación de datos sintéticos, análisis exploratorio y una interfaz web desarrollada en Django.

## Estructura del Proyecto

* `data/`: Scripts de generación de datos y archivos CSV resultantes.
* `notebooks/`: Jupyter Notebooks para el análisis y modelado.
* `web/`: Aplicación Django (vistas, modelos, templates).
* `manage.py`: Script de gestión de Django.
* `venv/`: Entorno virtual de Python (no se sube al repositorio).
* `requirements.txt`: Lista de dependencias del proyecto.

## Instalación y Configuración

### 1. Prerrequisitos

Asegúrate de tener Python 3.10 instalado (según tu configuración actual).

### 2. Crear y Activar Entorno Virtual

Es fundamental trabajar dentro del entorno virtual para evitar conflictos de versiones.

```bash
# Estando en la carpeta raíz (c:\tesis_credito_ml)

# Crear entorno (si no existe)
python -m venv venv

# Activar entorno (Windows)
.\venv\Scripts\activate
```

### 3. Instalar Dependencias

Una vez activado el entorno (verás `(venv)` en tu terminal), instala las librerías:

```bash
pip install -r requirements.txt
```

*Nota: Si tienes problemas con las versiones específicas del archivo requirements, puedes instalar las librerías base manualmente:*

```bash
pip install pandas numpy matplotlib seaborn scikit-learn jupyter notebook django
```

## Ejecución

### Generar Dataset Simulado

Para crear el archivo `datos_credito_simulados.csv`:

```bash
python data/generar_dataset.py
```

### Iniciar Jupyter Notebook

Para abrir los cuadernos de análisis:

```bash
jupyter notebook
```

## Solución de Problemas Comunes

**Error al iniciar Jupyter (`TypeError: field() ... 'alias'`)**
Si encuentras este error al ejecutar `jupyter notebook`, se debe a una versión desactualizada de `attrs`. Ejecuta:

```bash
pip install --upgrade attrs referencing jsonschema
```
