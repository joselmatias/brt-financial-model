# =========================================================
#  parametros.py – Valores por defecto y configuración
#  Troncal 1 – Flujo de Caja BRT
# =========================================================
# Diseñado para escalar a múltiples troncales:
#   - Cada troncal es un dict con la misma estructura.
#   - TRONCALES["Troncal 1"] contiene los parámetros base.

# ---------- TRONCAL 1 – Parámetros por defecto ----------
TRONCAL_1_DEFAULT = {
    # --- Identificación ---
    "nombre": "Troncal 1",

    # --- Horizonte temporal ---
    "anios": 12,

    # --- Demanda base (Año 1) ---
    "base_demanda": {
        "ESTUDIANTES":           478_548,
        "ADULTOS MAYORES":     1_755_826,
        "CAPACIDADES ESPECIALES": 572_796,
        "GENERAL":            21_308_057,
    },

    # --- Tarifas (USD por pasajero) ---
    "tarifas": {
        "ESTUDIANTES":              0.15,
        "ADULTOS MAYORES":          0.15,
        "CAPACIDADES ESPECIALES":   0.10,
        "GENERAL":                  0.45,
    },

    # --- Tasas de crecimiento anuales (11 valores para 12 años) ---
    "tasas_por_anio": [
        0.0091, 0.0091, 0.0090, 0.0089, 0.0088,
        0.0087, 0.0087, 0.0086, 0.0085, 0.0084, 0.0084
    ],

    # --- Equivalencia (divisor por categoría) ---
    "divisores_equivalencia": {
        "ESTUDIANTES":              2,
        "ADULTOS MAYORES":          2,
        "CAPACIDADES ESPECIALES":   3,
        "GENERAL":                  1,
    },

    # --- Modo de redondeo para proyección de demanda ---
    "modo_redondeo": "floor",   # "floor" o "round"

    # --- Costos Variables: Mantenimiento ---
    "divisor_meses":  12,
    "div_pre_7":       2.0,   # divisor años 1–6
    "div_post_7":      1.5,   # divisor años 7–12

    # Troncal (buses 18 m)
    "km_totales_troncal": 1_092_343.46,
    "costo_km_troncal":           0.33,
    "unidades_troncal":             40,   # 36 operación + 4 reserva

    # Alimentación (buses 12 m)
    "km_totales_alim_12y": 869_963,
    "costo_km_alim":              0.22,
    "unidades_alim":                31,

    # --- Costos Variables: Combustible ---
    "precio_galon":            2.80,
    "rend_km_gal_alim":        7.90,   # km/gal buses 12 m
    "rend_km_gal_troncal":     5.76,   # km/gal buses 18 m
    "combustible_aplica_prorrateo": False,

    # --- Costos Variables: Neumáticos ---
    "costo_llanta":                   450.0,
    "llantas_por_bus_troncal":           10,
    "llantas_por_bus_alim":               6,
    "renovaciones_llantas_por_anio":      1,

    # --- Costos Fijos: Financiamiento ---
    "precio_bus_troncal":       350_000.0,
    "precio_bus_alimentador":   156_848.0,
    "tasa_interes_anual":          0.0948,
    "plazo_anios_financ":               7,
    "porcentaje_financiado":         0.80,
    "porcentaje_equity":             0.20,

    # --- Costos Fijos: Sueldos ---
    "salario_mensual":             900.0,
    "choferes_por_bus_troncal":      2.4,
    "choferes_por_bus_alim":         2.4,

    # --- Costos Fijos: Gastos Administrativos (mensuales) ---
    "gastos_adm_items": [
        {"rubro": "Gerente",                 "cantidad": 1, "precio": 2500},
        {"rubro": "Presidente",              "cantidad": 1, "precio": 1800},
        {"rubro": "Asistente (Adm.)",        "cantidad": 1, "precio":  700},
        {"rubro": "Jefe de talento humano",  "cantidad": 1, "precio": 1200},
        {"rubro": "Asistente TH",            "cantidad": 1, "precio":  700},
        {"rubro": "Jefe de contabilidad",    "cantidad": 1, "precio": 1200},
        {"rubro": "Asistente contable",      "cantidad": 1, "precio":  700},
        {"rubro": "Operaciones",             "cantidad": 5, "precio":  500},
        {"rubro": "Jefe de infraestructura", "cantidad": 1, "precio": 1200},
        {"rubro": "Asistente (Infraest.)",   "cantidad": 1, "precio":  700},
        {"rubro": "Bodega",                  "cantidad": 3, "precio":  650},
        {"rubro": "Compras",                 "cantidad": 1, "precio":  500},
        {"rubro": "Salud Ocupacional",       "cantidad": 1, "precio":  800},
        {"rubro": "Jurídico",                "cantidad": 1, "precio": 1200},
    ],

    # --- Costos Fijos: Seguros ---
    "seguro_fiel_cumpl":           7_500.0,
    "seguro_todo_riesgo_unidades": 70_000.0,

    # --- Costos Fijos: Servicios básicos ---
    "serv_basicos_mensual": 1_400.0,

    # --- Costos Fijos: Matrícula e impuestos ---
    "matricula_precio":         250.00,
    "iva_compras":           11_500.00,
    "seg_unid_precio_mensual":  144.59,

    # --- Costos Fijos: Otros administrativos ---
    "otros_adm_anual": 14_000.00,

    # --- Otros Costos: ITOR ---
    "itor_porcentaje_oper_recaudo":  0.0995,
    "itor_transporte_valores_anual": 104_430.27,
    "itor_fideicomiso_admin_anual":   15_600.00,

    # --- Fee Metrovía ---
    "fee_metrovia_por_pasajero": 0.02,

    # --- Parámetros macroeconómicos ---
    "inflacion_anual":  0.0155,   # 1.55%
    "tasa_descuento":   0.12,     # 12% para VAN

    # --- Impuesto ---
    "tasa_impuesto_renta": 0.25,  # 25%
}

# ---------- ESCENARIOS PRE-CONFIGURADOS ----------
def _aplicar_escenario(base: dict, delta: dict) -> dict:
    """Crea una copia profunda del dict base y aplica las diferencias del escenario."""
    import copy
    p = copy.deepcopy(base)
    for k, v in delta.items():
        if isinstance(v, dict) and isinstance(p.get(k), dict):
            p[k].update(v)
        else:
            p[k] = v
    return p


ESCENARIO_CONSERVADOR = _aplicar_escenario(
    TRONCAL_1_DEFAULT,
    {
        "base_demanda": {
            "ESTUDIANTES":           430_000,
            "ADULTOS MAYORES":     1_580_000,
            "CAPACIDADES ESPECIALES": 515_000,
            "GENERAL":            19_177_000,
        },
        "tarifas": {
            "ESTUDIANTES":              0.13,
            "ADULTOS MAYORES":          0.13,
            "CAPACIDADES ESPECIALES":   0.09,
            "GENERAL":                  0.40,
        },
        "precio_galon": 3.10,
        "inflacion_anual": 0.025,
    }
)

ESCENARIO_BASE = TRONCAL_1_DEFAULT  # Sin cambios

ESCENARIO_OPTIMISTA = _aplicar_escenario(
    TRONCAL_1_DEFAULT,
    {
        "base_demanda": {
            "ESTUDIANTES":           527_000,
            "ADULTOS MAYORES":     1_932_000,
            "CAPACIDADES ESPECIALES": 630_000,
            "GENERAL":            23_439_000,
        },
        "tarifas": {
            "ESTUDIANTES":              0.17,
            "ADULTOS MAYORES":          0.17,
            "CAPACIDADES ESPECIALES":   0.11,
            "GENERAL":                  0.50,
        },
        "precio_galon": 2.50,
        "inflacion_anual": 0.010,
    }
)

ESCENARIOS = {
    "Base":         ESCENARIO_BASE,
    "Conservador":  ESCENARIO_CONSERVADOR,
    "Optimista":    ESCENARIO_OPTIMISTA,
}

# ---------- CATÁLOGO DE TRONCALES (para escalar) ----------
# Agregar aquí nuevas troncales cuando estén disponibles.
TRONCALES = {
    "Troncal 1": TRONCAL_1_DEFAULT,
    # "Troncal 2": TRONCAL_2_DEFAULT,  # Habilitar cuando esté listo
}

# ---------- TOOLTIPS PARA LA UI ----------
TOOLTIPS = {
    "base_demanda":              "Número de pasajeros anuales del Año 1 por categoría.",
    "tarifas":                   "Precio del pasaje en USD por tipo de pasajero.",
    "tasas_por_anio":            "Tasa de crecimiento de la demanda para cada año (11 valores).",
    "km_totales_troncal":        "Kilómetros totales recorridos por la flota troncal durante el período de análisis.",
    "costo_km_troncal":          "Costo de mantenimiento por kilómetro para buses de 18 m.",
    "unidades_troncal":          "Número total de buses troncales (operativos + reserva).",
    "km_totales_alim_12y":       "Kilómetros totales de la flota alimentadora en 12 años.",
    "costo_km_alim":             "Costo de mantenimiento por kilómetro para buses de 12 m.",
    "unidades_alim":             "Número total de buses alimentadores.",
    "precio_galon":              "Precio del galón de combustible en USD.",
    "rend_km_gal_troncal":       "Rendimiento de combustible (km/gal) de buses troncales.",
    "rend_km_gal_alim":          "Rendimiento de combustible (km/gal) de buses alimentadores.",
    "costo_llanta":              "Precio por llanta en USD.",
    "precio_bus_troncal":        "Precio de compra de un bus troncal de 18 m (USD).",
    "precio_bus_alimentador":    "Precio de compra de un bus alimentador de 12 m (USD).",
    "tasa_interes_anual":        "Tasa de interés anual del préstamo bancario.",
    "plazo_anios_financ":        "Número de años del financiamiento bancario.",
    "porcentaje_financiado":     "Porcentaje del costo de los buses financiado con deuda (80% = 0.80).",
    "salario_mensual":           "Salario mensual base por chofer en USD.",
    "inflacion_anual":           "Tasa de inflación anual aplicada a sueldos, neumáticos y gastos administrativos.",
    "tasa_descuento":            "Tasa de descuento para el cálculo del VAN (Valor Actual Neto).",
    "itor_porcentaje_oper_recaudo": "Porcentaje de los ingresos totales que corresponde al costo de operación y recaudo ITOR.",
    "fee_metrovia_por_pasajero": "Fee fijo pagado a Metrovía por cada pasajero transportado (USD).",
}
