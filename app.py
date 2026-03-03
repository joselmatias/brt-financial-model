# =========================================================
#  app.py – Aplicación Streamlit
#  Flujo de Caja BRT – Panel Ejecutivo
# =========================================================

import copy
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

from funciones import calcular_modelo, exportar_excel
from parametros import TOOLTIPS, TRONCALES

# ─────────────────────────────────────────────
#  CONFIGURACIÓN DE PÁGINA
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Flujo de Caja BRT",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  CSS PERSONALIZADO
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Encabezado principal ── */
.main-header {
    background: linear-gradient(135deg, #1F4E79 0%, #2E86AB 100%);
    padding: 1.2rem 1.8rem;
    border-radius: 10px;
    margin-bottom: 1.2rem;
    color: white;
}
.main-header h1 { margin: 0; font-size: 1.7rem; }
.main-header p  { margin: 0.2rem 0 0; opacity: 0.85; font-size: 0.9rem; }

/* ── Tarjetas KPI ── */
.kpi-card {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    text-align: center;
}
.kpi-label { font-size: 0.78rem; color: #6c757d; font-weight: 600;
             text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.3rem; }
.kpi-value { font-size: 1.6rem; font-weight: 700; color: #1F4E79; }
.kpi-sub   { font-size: 0.75rem; color: #6c757d; margin-top: 0.2rem; }

/* ── Semáforo ── */
.semaforo { font-size: 2rem; text-align: center; }
.semaforo-label { font-size: 0.85rem; font-weight: 700; text-align: center; }

/* ── Tablas ── */
.stDataFrame { font-size: 0.82rem; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background-color: #f0f4f8; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  HELPERS DE FORMATO
# ─────────────────────────────────────────────

def fmt_usd(val: float) -> str:
    """Formatea un número como moneda USD con signo."""
    if val >= 0:
        return f"${val:,.0f}"
    return f"-${abs(val):,.0f}"


def fmt_pct(val: float) -> str:
    return f"{val * 100:.2f}%"


def estilo_df(df: pd.DataFrame, entero: bool = False):
    """Aplica formato de moneda o entero a todas las columnas numéricas."""
    fmt = "{:,.0f}" if entero else "${:,.2f}"
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    return df.style.format({c: fmt for c in num_cols}, na_rep="—")


def color_filas_totales(styler):
    """Pinta las filas que comienzan con 'TOTAL' o 'SUBTOTAL'."""
    def resaltar(row):
        nombre = str(row.name)
        if nombre.startswith("TOTAL") or nombre.startswith("SUBTOTAL"):
            return ["background-color: #dbe9f7; font-weight: bold"] * len(row)
        return [""] * len(row)
    return styler.apply(resaltar, axis=1)


# ─────────────────────────────────────────────
#  SEMÁFORO DE VIABILIDAD
# ─────────────────────────────────────────────

def semaforo_viabilidad(van: float, tir: float, tasa_descuento: float):
    """Devuelve emoji, color y texto de viabilidad."""
    if np.isnan(tir):
        return "🔴", "red", "No viable (TIR indefinida)"
    if van > 0 and tir > tasa_descuento:
        return "🟢", "green", "Viable"
    if van > 0 or tir > tasa_descuento:
        return "🟡", "orange", "Viable con reservas"
    return "🔴", "red", "No viable"


# ─────────────────────────────────────────────
#  SIDEBAR – PARÁMETROS
# ─────────────────────────────────────────────

def render_sidebar() -> dict:
    """Construye el sidebar y retorna el dict de parámetros activos."""
    with st.sidebar:
        st.markdown("## ⚙️ Parámetros del Modelo")

        # ── Selector de troncal ──────────────────────────────────
        troncal_sel = st.selectbox(
            "Troncal",
            options=list(TRONCALES.keys()),
            help="Selecciona la troncal a analizar."
        )

        # Cargamos los parámetros de la troncal seleccionada
        p = copy.deepcopy(TRONCALES[troncal_sel])

        if st.button("↺ Restablecer valores", use_container_width=True):
            p = copy.deepcopy(TRONCALES[troncal_sel])
            st.rerun()

        st.divider()

        # ── DEMANDA ──────────────────────────────────────────────
        with st.expander("📊 Demanda base (Año 1)", expanded=False):
            st.caption(TOOLTIPS["base_demanda"])
            for cat in list(p["base_demanda"].keys()):
                p["base_demanda"][cat] = st.number_input(
                    cat, min_value=0, value=int(p["base_demanda"][cat]),
                    step=1_000, format="%d", key=f"dem_{cat}"
                )

        # ── TARIFAS ──────────────────────────────────────────────
        with st.expander("💵 Tarifas (USD)", expanded=False):
            st.caption(TOOLTIPS["tarifas"])
            for cat in list(p["tarifas"].keys()):
                p["tarifas"][cat] = st.number_input(
                    cat, min_value=0.01, max_value=10.0,
                    value=float(p["tarifas"][cat]),
                    step=0.01, format="%.2f", key=f"tar_{cat}"
                )

        # ── TASAS DE CRECIMIENTO ─────────────────────────────────
        with st.expander("📈 Tasas de crecimiento anuales", expanded=False):
            st.caption(TOOLTIPS["tasas_por_anio"])
            anios = p["anios"]
            nuevas_tasas = []
            for i, tasa in enumerate(p["tasas_por_anio"]):
                val = st.number_input(
                    f"Año {i+1} → Año {i+2}",
                    min_value=-0.5, max_value=0.5,
                    value=float(tasa), step=0.0001,
                    format="%.4f", key=f"tasa_{i}"
                )
                nuevas_tasas.append(val)
            p["tasas_por_anio"] = nuevas_tasas

        # ── COMBUSTIBLE ──────────────────────────────────────────
        with st.expander("⛽ Combustible", expanded=False):
            p["precio_galon"] = st.number_input(
                "Precio galón (USD)", min_value=0.01,
                value=float(p["precio_galon"]), step=0.05, format="%.2f",
                help=TOOLTIPS["precio_galon"]
            )
            p["rend_km_gal_troncal"] = st.number_input(
                "Rendimiento troncal (km/gal)", min_value=0.1,
                value=float(p["rend_km_gal_troncal"]), step=0.1, format="%.2f",
                help=TOOLTIPS["rend_km_gal_troncal"]
            )
            p["rend_km_gal_alim"] = st.number_input(
                "Rendimiento alimentación (km/gal)", min_value=0.1,
                value=float(p["rend_km_gal_alim"]), step=0.1, format="%.2f",
                help=TOOLTIPS["rend_km_gal_alim"]
            )

        # ── MANTENIMIENTO ────────────────────────────────────────
        with st.expander("🔧 Mantenimiento", expanded=False):
            p["costo_km_troncal"] = st.number_input(
                "Costo/km troncal (USD)", min_value=0.01,
                value=float(p["costo_km_troncal"]), step=0.01, format="%.2f",
                help=TOOLTIPS["costo_km_troncal"]
            )
            p["costo_km_alim"] = st.number_input(
                "Costo/km alimentación (USD)", min_value=0.01,
                value=float(p["costo_km_alim"]), step=0.01, format="%.2f",
                help=TOOLTIPS["costo_km_alim"]
            )
            p["costo_llanta"] = st.number_input(
                "Costo por llanta (USD)", min_value=1.0,
                value=float(p["costo_llanta"]), step=10.0, format="%.0f"
            )

        # ── FLOTA ────────────────────────────────────────────────
        with st.expander("🚌 Flota", expanded=False):
            p["unidades_troncal"] = st.number_input(
                "Buses troncal (18 m)", min_value=1,
                value=int(p["unidades_troncal"]), step=1,
                help=TOOLTIPS["unidades_troncal"]
            )
            p["unidades_alim"] = st.number_input(
                "Buses alimentación (12 m)", min_value=1,
                value=int(p["unidades_alim"]), step=1,
                help=TOOLTIPS["unidades_alim"]
            )

        # ── FINANCIAMIENTO ───────────────────────────────────────
        with st.expander("🏦 Financiamiento", expanded=False):
            p["tasa_interes_anual"] = st.number_input(
                "Tasa interés anual", min_value=0.001, max_value=0.5,
                value=float(p["tasa_interes_anual"]),
                step=0.001, format="%.4f",
                help=TOOLTIPS["tasa_interes_anual"]
            )
            p["plazo_anios_financ"] = st.number_input(
                "Plazo (años)", min_value=1, max_value=30,
                value=int(p["plazo_anios_financ"]), step=1,
                help=TOOLTIPS["plazo_anios_financ"]
            )
            p["porcentaje_financiado"] = st.slider(
                "% Financiado con deuda", min_value=0.0, max_value=1.0,
                value=float(p["porcentaje_financiado"]), step=0.05,
                format="%.0f%%",
                help=TOOLTIPS["porcentaje_financiado"]
            )
            p["porcentaje_equity"] = 1.0 - p["porcentaje_financiado"]

        # ── SUELDOS Y ADMIN ──────────────────────────────────────
        with st.expander("👥 Sueldos y Administración", expanded=False):
            p["salario_mensual"] = st.number_input(
                "Salario mensual chofer (USD)", min_value=100.0,
                value=float(p["salario_mensual"]), step=50.0, format="%.0f",
                help=TOOLTIPS["salario_mensual"]
            )

        # ── MACROECONOMÍA ────────────────────────────────────────
        with st.expander("🌐 Macroeconomía", expanded=False):
            p["inflacion_anual"] = st.number_input(
                "Inflación anual", min_value=0.0, max_value=0.5,
                value=float(p["inflacion_anual"]),
                step=0.001, format="%.4f",
                help=TOOLTIPS["inflacion_anual"]
            )
            p["tasa_descuento"] = st.number_input(
                "Tasa de descuento (VAN)", min_value=0.001, max_value=0.5,
                value=float(p["tasa_descuento"]),
                step=0.005, format="%.3f",
                help=TOOLTIPS["tasa_descuento"]
            )
            p["itor_porcentaje_oper_recaudo"] = st.number_input(
                "ITOR – % ingresos (recaudo)", min_value=0.0, max_value=0.5,
                value=float(p["itor_porcentaje_oper_recaudo"]),
                step=0.001, format="%.4f",
                help=TOOLTIPS["itor_porcentaje_oper_recaudo"]
            )
            p["fee_metrovia_por_pasajero"] = st.number_input(
                "Fee Metrovía (USD/pasajero)", min_value=0.0,
                value=float(p["fee_metrovia_por_pasajero"]),
                step=0.005, format="%.3f",
                help=TOOLTIPS["fee_metrovia_por_pasajero"]
            )

        return p, troncal_sel


# ─────────────────────────────────────────────
#  PANEL KPIs
# ─────────────────────────────────────────────

def render_kpis(res: dict, p: dict):
    van  = res["van"]
    tir  = res["tir"]
    anios = p["anios"]

    emoji, color_sem, texto_sem = semaforo_viabilidad(van, tir, p["tasa_descuento"])

    c1, c2, c3, c4, c5 = st.columns([1, 1.2, 1.2, 1.2, 1])

    with c1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="semaforo">{emoji}</div>
            <div class="semaforo-label" style="color:{color_sem}">{texto_sem}</div>
        </div>""", unsafe_allow_html=True)

    with c2:
        van_fmt = fmt_usd(van)
        color_van = "#1a7a4a" if van > 0 else "#c0392b"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">VAN ({p['tasa_descuento']*100:.0f}%)</div>
            <div class="kpi-value" style="color:{color_van}">{van_fmt}</div>
            <div class="kpi-sub">Valor Actual Neto</div>
        </div>""", unsafe_allow_html=True)

    with c3:
        tir_fmt = "N/A" if np.isnan(tir) else fmt_pct(tir)
        color_tir = "#1a7a4a" if (not np.isnan(tir) and tir > p["tasa_descuento"]) else "#c0392b"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">TIR</div>
            <div class="kpi-value" style="color:{color_tir}">{tir_fmt}</div>
            <div class="kpi-sub">Tasa Interna de Retorno</div>
        </div>""", unsafe_allow_html=True)

    with c4:
        ultimo = res["flujo_ultimo"]
        color_u = "#1a7a4a" if ultimo > 0 else "#c0392b"
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Flujo Año {anios}</div>
            <div class="kpi-value" style="color:{color_u}">{fmt_usd(ultimo)}</div>
            <div class="kpi-sub">Último año del horizonte</div>
        </div>""", unsafe_allow_html=True)

    with c5:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-label">Payback</div>
            <div class="kpi-value">{res['payback']}</div>
            <div class="kpi-sub">Recuperación inversión</div>
        </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  GRÁFICOS
# ─────────────────────────────────────────────

PALETA = {
    "azul_oscuro":  "#1F4E79",
    "azul_claro":   "#2E86AB",
    "verde":        "#27AE60",
    "rojo":         "#E74C3C",
    "naranja":      "#F39C12",
    "gris":         "#95A5A6",
}


def fig_ingresos_vs_costos(res: dict) -> go.Figure:
    """Líneas: Ingresos totales vs Costos totales por año."""
    cols = res["cols_anios"]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=cols, y=res["serie_ingresos"],
        name="Ingresos totales",
        mode="lines+markers",
        line=dict(color=PALETA["verde"], width=2.5),
        marker=dict(size=6),
        hovertemplate="<b>%{x}</b><br>Ingresos: $%{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=cols, y=res["serie_costos"],
        name="Costos totales",
        mode="lines+markers",
        line=dict(color=PALETA["rojo"], width=2.5),
        marker=dict(size=6),
        hovertemplate="<b>%{x}</b><br>Costos: $%{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(
        title="Ingresos vs Costos totales",
        xaxis_title="Año", yaxis_title="USD",
        yaxis_tickformat="$,.0f",
        legend=dict(orientation="h", y=1.12),
        template="plotly_white", height=360,
        margin=dict(t=60, b=40, l=60, r=20)
    )
    return fig


def fig_flujo_barras(res: dict) -> go.Figure:
    """Barras coloreadas de flujo de caja anual (verde=positivo, rojo=negativo)."""
    cols  = res["cols_0aN"]
    vals  = res["flujos_0aN"]
    colores = [PALETA["verde"] if v >= 0 else PALETA["rojo"] for v in vals]
    fig = go.Figure(go.Bar(
        x=cols, y=vals,
        marker_color=colores,
        text=[fmt_usd(v) for v in vals],
        textposition="outside",
        textfont=dict(size=10),
        hovertemplate="<b>%{x}</b><br>Flujo: $%{y:,.0f}<extra></extra>"
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
    fig.update_layout(
        title="Flujo de Caja Anual",
        xaxis_title="Año", yaxis_title="USD",
        yaxis_tickformat="$,.0f",
        template="plotly_white", height=360,
        margin=dict(t=60, b=40, l=60, r=20)
    )
    return fig


def fig_flujo_acumulado(res: dict) -> go.Figure:
    """Área del flujo de caja acumulado."""
    cols  = res["cols_0aN"]
    acum  = np.cumsum(res["flujos_0aN"])
    if acum[-1] >= 0:
        line_color = PALETA["verde"]
        fill_color = "rgba(39, 174, 96, 0.15)"
    else:
        line_color = PALETA["rojo"]
        fill_color = "rgba(231, 76, 60, 0.15)"
    fig = go.Figure(go.Scatter(
        x=cols, y=acum,
        fill="tozeroy",
        line=dict(color=line_color, width=2.5),
        fillcolor=fill_color,
        hovertemplate="<b>%{x}</b><br>Acumulado: $%{y:,.0f}<extra></extra>",
        name="Flujo acumulado"
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
    fig.update_layout(
        title="Flujo de Caja Acumulado",
        xaxis_title="Año", yaxis_title="USD",
        yaxis_tickformat="$,.0f",
        template="plotly_white", height=360,
        margin=dict(t=60, b=40, l=60, r=20)
    )
    return fig


def fig_composicion_costos(res: dict) -> go.Figure:
    """Stacked bar: costos variables vs costos fijos por año."""
    cols = res["cols_anios"]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=cols, y=res["serie_cv"],
        name="Costos Variables",
        marker_color=PALETA["naranja"],
        hovertemplate="<b>%{x}</b><br>CV: $%{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        x=cols, y=res["serie_cf"],
        name="Costos Fijos",
        marker_color=PALETA["azul_claro"],
        hovertemplate="<b>%{x}</b><br>CF: $%{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(
        barmode="stack",
        title="Composición de Costos",
        xaxis_title="Año", yaxis_title="USD",
        yaxis_tickformat="$,.0f",
        legend=dict(orientation="h", y=1.12),
        template="plotly_white", height=360,
        margin=dict(t=60, b=40, l=60, r=20)
    )
    return fig


# ─────────────────────────────────────────────
#  RENDER DE TABLAS
# ─────────────────────────────────────────────

def render_tabla(df: pd.DataFrame, entero: bool = False, titulo: str = ""):
    """Muestra una tabla estilizada con totales resaltados."""
    if titulo:
        st.markdown(f"**{titulo}**")
    styled = color_filas_totales(estilo_df(df, entero=entero))
    st.dataframe(styled, use_container_width=True)


# ─────────────────────────────────────────────
#  PESTAÑAS PRINCIPALES
# ─────────────────────────────────────────────

def render_tab_resumen(res: dict, p: dict):
    """Tab: Resumen Ejecutivo con KPIs y todos los gráficos."""
    render_kpis(res, p)
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(fig_ingresos_vs_costos(res), use_container_width=True)
        st.plotly_chart(fig_flujo_acumulado(res),    use_container_width=True)
    with col2:
        st.plotly_chart(fig_flujo_barras(res),        use_container_width=True)
        st.plotly_chart(fig_composicion_costos(res),  use_container_width=True)


def render_tab_demanda(res: dict):
    st.subheader("Demanda de pasajeros proyectada")
    render_tabla(res["demanda"],             entero=True, titulo="Demanda por categoría (pasajeros)")
    st.divider()
    render_tabla(res["demanda_equivalente"], entero=True, titulo="Demanda equivalente (ajustada por tarifa reducida)")


def render_tab_ingresos(res: dict):
    st.subheader("Ingresos proyectados (USD)")
    render_tabla(res["ingresos"],             titulo="Ingresos por categoría de pasajero")
    st.divider()
    render_tabla(res["ingresos_equivalentes"], titulo="Ingresos equivalentes")


def render_tab_costos(res: dict):
    st.subheader("Costos Variables (USD)")
    render_tabla(res["costos_variables_op"], titulo="Mantenimiento y Combustible")
    st.divider()
    render_tabla(res["df_itor"],             titulo="Otros Costos – ITOR")
    st.divider()
    render_tabla(res["df_fee"],              titulo="Fee Metrovía")
    st.divider()
    render_tabla(res["df_total_cv"],         titulo="TOTAL Costos Variables")

    st.subheader("Costos Fijos (USD)")
    render_tabla(res["costos_fijos"],        titulo="Financiamiento, Sueldos y Gastos Administrativos")
    st.divider()
    render_tabla(res["df_costos_totales"],   titulo="TOTAL Costos (Variables + Fijos)")


def render_tab_flujo(res: dict):
    st.subheader("Estado de Resultados y Flujo de Caja (USD)")
    render_tabla(res["df_utilidad_bruta"],   titulo="Utilidad Bruta")
    st.divider()
    render_tabla(res["df_imp_renta"],        titulo="Impuesto a la Renta (25%)")
    st.divider()
    render_tabla(res["df_flujo"],            titulo="Flujo de Caja (Año 0 = aporte equity)")
    st.divider()
    render_tabla(res["df_flujo_acum"],       titulo="Flujo de Caja Acumulado")

    # Mini-tabla de indicadores financieros
    st.divider()
    st.subheader("Indicadores Financieros")
    van = res["van"]
    tir = res["tir"]
    df_ind = pd.DataFrame({
        "Indicador": ["VAN", "TIR", "Payback"],
        "Valor":     [
            fmt_usd(van),
            "N/A" if np.isnan(tir) else fmt_pct(tir),
            res["payback"],
        ]
    }).set_index("Indicador")
    st.table(df_ind)


def render_tab_exportar(res: dict, p: dict, troncal_sel: str):
    st.subheader("Exportar resultados")
    st.markdown("""
    Descarga todos los resultados en un archivo Excel multi-hoja con formato financiero.
    Incluye: Demanda, Ingresos, Costos Variables, Costos Fijos, Flujo de Caja, KPIs.
    """)

    try:
        excel_bytes = exportar_excel(res, nombre_troncal=troncal_sel)
        st.download_button(
            label="📥 Descargar Excel",
            data=excel_bytes,
            file_name=f"FlujoCaja_{troncal_sel.replace(' ', '_')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except ImportError:
        st.error("openpyxl no está instalado. Ejecuta: pip install openpyxl")
    except Exception as e:
        st.error(f"Error generando Excel: {e}")

    st.divider()
    st.subheader("Resumen de parámetros activos")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Demanda base (Año 1)**")
        for cat, val in p["base_demanda"].items():
            st.markdown(f"- {cat}: **{val:,}** pasajeros")
        st.markdown("**Tarifas**")
        for cat, val in p["tarifas"].items():
            st.markdown(f"- {cat}: **${val:.2f}**")
    with col2:
        st.markdown("**Parámetros financieros**")
        st.markdown(f"- Tasa descuento: **{p['tasa_descuento']*100:.1f}%**")
        st.markdown(f"- Tasa interés:   **{p['tasa_interes_anual']*100:.2f}%**")
        st.markdown(f"- Plazo financ.:  **{p['plazo_anios_financ']} años**")
        st.markdown(f"- Inflación:      **{p['inflacion_anual']*100:.2f}%**")
        st.markdown(f"- Precio galón:   **${p['precio_galon']:.2f}**")
        st.markdown(f"- Salario chofer: **${p['salario_mensual']:.0f}/mes**")


# ─────────────────────────────────────────────
#  APLICACIÓN PRINCIPAL
# ─────────────────────────────────────────────

def main():
    # ── Encabezado ───────────────────────────────────────────────
    st.markdown("""
    <div class="main-header">
        <h1>🚌 Flujo de Caja BRT – Panel Ejecutivo</h1>
        <p>Sistema de Transporte Rápido de Pasajeros | Modelo financiero a 12 años</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Sidebar ──────────────────────────────────────────────────
    p, troncal_sel = render_sidebar()

    # ── Cálculo (con caché basado en parámetros) ─────────────────
    @st.cache_data(show_spinner="Calculando modelo financiero…")
    def _calcular(p_frozen: str) -> dict:
        import json
        params = json.loads(p_frozen)
        return calcular_modelo(params)

    import json

    try:
        p_frozen = json.dumps(p, sort_keys=True, default=str)
        resultado = _calcular(p_frozen)
    except ValueError as e:
        st.error(f"⚠️ Parámetro inválido: {e}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error en el cálculo: {e}")
        st.stop()

    # ── Pestañas ─────────────────────────────────────────────────
    tab_res, tab_dem, tab_ing, tab_cos, tab_flu, tab_exp = st.tabs([
        "📊 Resumen Ejecutivo",
        "👥 Demanda",
        "💵 Ingresos",
        "📦 Costos",
        "💰 Flujo de Caja",
        "📥 Exportar",
    ])

    with tab_res:
        render_tab_resumen(resultado, p)
    with tab_dem:
        render_tab_demanda(resultado)
    with tab_ing:
        render_tab_ingresos(resultado)
    with tab_cos:
        render_tab_costos(resultado)
    with tab_flu:
        render_tab_flujo(resultado)
    with tab_exp:
        render_tab_exportar(resultado, p, troncal_sel)


if __name__ == "__main__":
    main()
