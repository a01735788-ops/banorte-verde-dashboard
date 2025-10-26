# --------------------------------------------
# BANORTE VERDE IoT – Dashboard Web (UI Kit)
# --------------------------------------------
# Colores / tokens (UI Kit Banorte)
BANORTE_RED = "#EB0029"
BANORTE_RED_HOVER = "#DB0026"
BANORTE_GREY_DARK = "#323E48"
BANORTE_GREY_TEXT = "#5B6670"
BANORTE_GREY_BG = "#F6F6F6"

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="Banorte Verde IoT", layout="wide", page_icon="💳")

# ---------- Estilos UI (fuente, colores, botones) ----------
st.markdown(f"""
<style>
:root {{
  --banorte-red: {BANORTE_RED};
  --banorte-red-hover: {BANORTE_RED_HOVER};
  --banorte-grey-dark: {BANORTE_GREY_DARK};
  --banorte-grey-text: {BANORTE_GREY_TEXT};
  --banorte-grey-bg: {BANORTE_GREY_BG};
}}
html, body, [class*="css"] {{
  background: var(--banorte-grey-bg);
  color: var(--banorte-grey-dark);
  font-family: "Gotham", "Montserrat", Arial, sans-serif;
}}
h1, h2, h3, h4 {{
  color: var(--banorte-grey-dark);
  font-weight: 600;
}}
div[data-testid="metric-container"] {{
  background: white;
  border: 1px solid #e6e6e6;
  border-radius: 10px;
  padding: 14px 16px;
}}
.stButton>button {{
  background: var(--banorte-red);
  color: #fff;
  border: 0;
  border-radius: 8px;
  padding: 10px 18px;
  font-weight: 600;
}}
.stButton>button:hover {{
  background: var(--banorte-red-hover);
}}
section[data-testid="stSidebar"] {{
  background: #ffffff;
  border-right: 1px solid #eee;
}}
</style>
""", unsafe_allow_html=True)

# ---------- Sidebar (parámetros) ----------
st.sidebar.title("⚙️ Parámetros")
clientes = st.sidebar.slider("Número de clientes Banorte", 1, 10000, 1000, step=100)
tarifa_mxn = st.sidebar.number_input("Tarifa eléctrica (MXN/kWh)", value=2.50, step=0.10, min_value=0.0)
factor_co2 = st.sidebar.number_input("Factor CO₂ (kg/kWh)", value=0.45, step=0.01, min_value=0.0)
st.sidebar.caption("Ajusta para CDMX / MTY / Puebla según tarifa local y factor de emisión.")

# ---------- Simulación IoT (7 días, cada hora) ----------
fechas = pd.date_range(start="2025-10-01", periods=7*24, freq="H")
np.random.seed(42)
consumo_watts = np.clip(np.random.normal(800, 150, len(fechas)), 400, 1500)
produccion_solar = np.maximum(0, 900 * np.sin((fechas.hour - 6)/12 * np.pi))
consumo_red = np.maximum(consumo_watts - produccion_solar, 0)

df = pd.DataFrame({
    "timestamp": fechas,
    "consumo_watts": consumo_watts,
    "produccion_solar": produccion_solar,
    "consumo_red": consumo_red
})

# ---------- Cálculos energéticos ----------
df["consumo_red_kwh"] = df["consumo_red"] / 1000
df["consumo_base_kwh"] = df["consumo_red_kwh"] * 1.10
df["ahorro_kwh"] = df["consumo_base_kwh"] - df["consumo_red_kwh"]
df["ahorro_mxn"] = df["ahorro_kwh"] * tarifa_mxn
df["co2_ev_kg"] = df["ahorro_kwh"] * factor_co2
df_dia = df.resample("D", on="timestamp").sum()

# ---------- KPIs individuales ----------
energia_base = df_dia["consumo_base_kwh"].sum()
energia_real = df_dia["consumo_red_kwh"].sum()
ahorro_kwh = df_dia["ahorro_kwh"].sum()
ahorro_mxn = df_dia["ahorro_mxn"].sum()
co2_ev = df_dia["co2_ev_kg"].sum()

# ---------- Escalamiento por # de clientes ----------
ahorro_kwh_total = ahorro_kwh * clientes
ahorro_mxn_total = ahorro_mxn * clientes
co2_ev_total = co2_ev * clientes
proyeccion_4_anios = ahorro_mxn_total * 52 * 4

# ---------- Header ----------
st.title("💳 Tarjeta Banorte Verde — IoT Dashboard")
st.subheader("Transformamos cada transacción y dato energético en **valor financiero y ambiental.**")

# ---------- KPIs (por cliente) ----------
st.markdown("### 📊 KPIs por cliente (7 días)")
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("⚡ Energía Base", f"{energia_base:.2f} kWh")
c2.metric("💡 Energía Optimizada", f"{energia_real:.2f} kWh")
c3.metric("💚 Ahorro Energético", f"{ahorro_kwh:.2f} kWh")
c4.metric("🌎 CO₂ Evitado", f"{co2_ev:.2f} kg")
c5.metric("💰 Ahorro Financiero", f"${ahorro_mxn:,.2f}")

# ---------- KPIs (agregados) ----------
st.markdown("### 🌍 Impacto agregado (todos los clientes)")
a1, a2, a3 = st.columns(3)
a1.metric("💚 Ahorro total (kWh)", f"{ahorro_kwh_total:,.0f}")
a2.metric("🌎 CO₂ evitado (kg)", f"{co2_ev_total:,.0f}")
a3.metric("📈 Proyección 4 años (MXN)", f"${proyeccion_4_anios:,.0f}")

# ---------- Gráfica Plotly ----------
fig = px.line(
    df_dia,
    x=df_dia.index,
    y=["consumo_base_kwh", "consumo_red_kwh", "ahorro_kwh"],
    labels={"value": "kWh", "timestamp": "Día"},
    title="Consumo y Ahorro Energético (kWh) — Banorte Verde IoT",
)
fig.update_layout(
    template="plotly_dark",
    paper_bgcolor=BANORTE_GREY_BG,
    plot_bgcolor=BANORTE_GREY_BG,
    font=dict(color=BANORTE_GREY_DARK),
    legend_title_text="Indicadores"
)
fig.update_traces(selector=0, line=dict(color=BANORTE_RED))
fig.update_traces(selector=1, line=dict(color=BANORTE_GREY_DARK))
fig.update_traces(selector=2, line=dict(color="#1BAA5A"))
st.plotly_chart(fig, use_container_width=True)

# ---------- Pie de página ----------
st.caption("Datos simulados para demostración del modelo financiero sostenible de Banorte Verde. Ajusta parámetros en el panel izquierdo.")
