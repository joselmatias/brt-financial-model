# Flujo de Caja BRT – Panel Ejecutivo

Aplicación web interactiva para el análisis financiero de la **Troncal 1** del sistema BRT (Bus Rapid Transit). Construida con **Streamlit**, permite modificar parámetros en tiempo real y visualizar el impacto en los indicadores financieros del proyecto a 12 años.

---

## Características principales

| Funcionalidad | Detalle |
|---|---|
| **Panel de parámetros** | Sidebar con controles para todos los inputs del modelo |
| **Escenarios** | Conservador, Base y Optimista pre-configurados |
| **KPIs ejecutivos** | VAN, TIR, Flujo Año 12, Payback y semáforo de viabilidad |
| **Pestañas** | Resumen · Demanda · Ingresos · Costos · Flujo de Caja · Exportar |
| **Gráficos Plotly** | Ingresos vs Costos · Flujo anual · Flujo acumulado · Composición de costos |
| **Exportar a Excel** | Multi-hoja con formato financiero (openpyxl) |
| **Multi-troncal** | Arquitectura lista para añadir Troncal 2, 3, etc. |

---

## Estructura de archivos

```
Flujos de caja AM/
├── app.py            # Aplicación principal Streamlit (UI)
├── funciones.py      # Lógica de cálculo del modelo financiero
├── parametros.py     # Valores por defecto, escenarios, tooltips
├── requirements.txt  # Dependencias Python
└── README.md         # Este archivo
```

---

## Instalación local

### Requisitos previos
- Python 3.10 o superior
- pip

### Pasos

```bash
# 1. Clonar o descargar el proyecto
cd "Flujos de caja AM"

# 2. Crear entorno virtual (recomendado)
python -m venv .venv

# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Correr la aplicación
streamlit run app.py
```

La app abrirá automáticamente en `http://localhost:8501`.

---

## Despliegue en Streamlit Cloud

1. Subir el proyecto a un repositorio **GitHub** (público o privado).
2. Ir a [share.streamlit.io](https://share.streamlit.io) e iniciar sesión.
3. Hacer clic en **"New app"**.
4. Seleccionar el repositorio, rama `main` y archivo `app.py`.
5. Hacer clic en **"Deploy"**.

> El archivo `requirements.txt` es detectado automáticamente por Streamlit Cloud.

---

## Flujo de uso

```
Abrir app
    │
    ├─► Seleccionar Troncal (sidebar)
    ├─► Seleccionar Escenario (Base / Conservador / Optimista)
    ├─► Ajustar parámetros (tarifas, demanda, combustible, etc.)
    │
    └─► El modelo recalcula automáticamente
            │
            ├─► Tab "Resumen Ejecutivo": KPIs + 4 gráficos
            ├─► Tab "Demanda":           Tablas de proyección de pasajeros
            ├─► Tab "Ingresos":          Tablas de ingresos por categoría
            ├─► Tab "Costos":            CV, CF y costos totales detallados
            ├─► Tab "Flujo de Caja":     Utilidad, impuesto, flujo, acumulado
            └─► Tab "Exportar":          Descarga Excel + resumen de parámetros
```

---

## Cómo agregar una nueva Troncal

1. En `parametros.py`, crear un nuevo dict siguiendo la estructura de `TRONCAL_1_DEFAULT`:

```python
TRONCAL_2_DEFAULT = {
    "nombre": "Troncal 2",
    "anios": 12,
    "base_demanda": { ... },
    # ... todos los demás campos
}
```

2. Añadirlo al catálogo `TRONCALES`:

```python
TRONCALES = {
    "Troncal 1": TRONCAL_1_DEFAULT,
    "Troncal 2": TRONCAL_2_DEFAULT,   # <-- nueva línea
}
```

3. La app detectará automáticamente la nueva troncal en el selector del sidebar.

---

## Modelo financiero

### Variables de entrada
- Demanda base por categoría (Estudiantes, Adultos Mayores, Cap. Especiales, General)
- Tarifas diferenciadas por categoría (USD)
- Tasas de crecimiento anual de demanda (11 valores para 12 años)
- Costos de mantenimiento por km (troncal y alimentación)
- Precio de combustible y rendimiento (km/galón)
- Costos de neumáticos
- Parámetros de financiamiento (tasa, plazo, % financiado)
- Sueldos de conductores
- Gastos administrativos detallados
- Costos ITOR (operación, transporte de valores, fideicomiso)
- Fee Metrovía por pasajero
- Inflación anual y tasa de descuento

### Indicadores calculados
| Indicador | Descripción |
|---|---|
| **VAN** | Valor Actual Neto descontado a la tasa configurada |
| **TIR** | Tasa Interna de Retorno (bisección numérica) |
| **Payback** | Primer año en que el flujo acumulado es positivo |
| **Flujo Año N** | Flujo de caja del último año del horizonte |

### Lógica de costos de mantenimiento
Los costos de mantenimiento aplican un prorrateo temporal:
- Años 1–6: `base_anual / 2.0` (flota parcialmente en operación)
- Años 7–12: `base_anual / 1.5` (operación plena)

### Impuesto a la renta
Se aplica 25% únicamente sobre utilidades positivas. Los años con pérdida no generan impuesto.

---

## Dependencias

| Librería | Versión mínima | Uso |
|---|---|---|
| streamlit | 1.35.0 | Framework web |
| pandas | 2.0.0 | Manipulación de datos |
| numpy | 1.26.0 | Cálculos numéricos |
| plotly | 5.20.0 | Gráficos interactivos |
| openpyxl | 3.1.0 | Exportación a Excel |
