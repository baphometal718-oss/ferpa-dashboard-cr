import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from ferpa_logic import SimuladorFerpaV3

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="FERPA: Suite Financiera", layout="wide", initial_sidebar_state="expanded")

# --- 2. ESTILOS CSS CORPORATIVOS (HIGH-TECH) ---
def corporate_css():
    st.markdown("""
    <style>
    /* FUENTES & COLORES GLOBALES */
    .stApp {
        background-color: #0E1117; /* Negro Profundo */
        color: #E0E0E0; /* Blanco Humo para lectura */
        font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* SIDEBAR */
    section[data-testid="stSidebar"] {
        background-color: #0E1117;
        border-right: 1px solid #1E2329;
    }
    
    /* TITULOS Y TEXTOS NEÓN */
    h1, h2, h3 {
        color: #FFFFFF !important;
        font-weight: 700;
    }
    .neon-text {
        color: #00FFAA;
        text-shadow: 0 0 10px rgba(0, 255, 170, 0.6);
        font-weight: bold;
    }
    
    /* KPI CARDS (GLASSMORPHISM PRO) */
    .metric-card {
        background: rgba(22, 27, 34, 0.6);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0, 255, 170, 0.2);
        border-radius: 8px;
        padding: 24px 16px;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    .metric-card:hover {
        border-color: #00FFAA;
        box-shadow: 0 0 15px rgba(0, 255, 170, 0.15);
        transform: translateY(-2px);
    }
    
    .metric-icon {
        width: 32px;
        height: 32px;
        margin-bottom: 12px;
        fill: #00FFAA;
    }
    
    .metric-value {
        font-size: 32px;
        font-weight: 700;
        color: #FFFFFF;
        margin: 8px 0;
        letter-spacing: -0.5px;
    }
    .metric-value.neon {
        color: #00FFAA;
        text-shadow: 0 0 12px rgba(0, 255, 170, 0.5);
    }
    
    .metric-label {
        font-size: 13px;
        color: #A0AAB5;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 600;
    }
    
    /* SLIDERS CUSTOM */
    .stSlider > div > div > div > div {
        background-color: #00FFAA !important;
    }
    .stSlider > div > div > div > div > div {
        color: #00FFAA !important;
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        border-bottom-color: #1E2329;
    }
    .stTabs [data-baseweb="tab"] {
        color: #A0AAB5;
    }
    .stTabs [aria-selected="true"] {
        color: #00FFAA !important;
        border-bottom-color: #00FFAA !important;
    }
    
    /* DATAFRAMES */
    [data-testid="stDataFrame"] {
        border: 1px solid #30363D;
        border-radius: 5px;
    }
    
    </style>
    """, unsafe_allow_html=True)

corporate_css()

# --- ICONOS SVG ---
ICON_DOLLAR = """<svg class="metric-icon" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.31-8.86c-1.77-.45-2.34-.94-2.34-1.67 0-.84.79-1.43 2.1-1.43 1.38 0 1.9.66 1.94 1.64h1.71c-.05-1.34-.87-2.57-2.49-2.97V5H10.9v1.69c-1.51.32-2.72 1.3-2.72 2.81 0 1.79 1.49 2.69 3.66 3.21 1.95.46 2.34 1.15 2.34 1.87 0 .53-.39 1.39-2.1 1.39-1.6 0-2.23-.72-2.32-1.64H8.04c.1 1.7 1.36 2.66 2.86 2.97V19h2.34v-1.67c1.52-.29 2.72-1.16 2.73-2.77-.01-2.2-1.9-2.96-3.66-3.42z"/></svg>"""
ICON_FACTORY = """<svg class="metric-icon" viewBox="0 0 24 24"><path d="M22 22H2V10l7-3v2l5-2v3h3l1-8h3l1 8v12zM12 9.95l-5 2V10l-3 1.32V20h16v-8h-8V9.95z"/></svg>"""
ICON_LEAF = """<svg class="metric-icon" viewBox="0 0 24 24"><path d="M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17 1.01.29 1.57.33l1.61-3.18c.63.13 1.25.12 1.89-.04l2.16 2.93 1.66-2.93c1.76-.75 3.01-2.26 3.45-5.81zM7 21l-.95-2.28c.19-.55.45-1.1.77-1.65.31-.54.67-1.07 1.09-1.59l1.63 3.19c-.83.67-1.72 1.42-2.54 2.33zm11-13c-3.31 0-6 2.69-6 6 0 1.66.67 3.15 1.76 4.24l-3.33-5.86c.32-.46.7-.89 1.15-1.28l3.33 5.86c1.09-1.09 1.76-2.58 1.76-4.24 0-3.31-2.69-6-6-6z"/></svg>"""
ICON_CHART = """<svg class="metric-icon" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>"""

# --- SIDEBAR: BRANDING & CONTROL ---
with st.sidebar:
    # 1. LOGO CORPORATIVO
    try:
        st.image("logo.png", width=220)
    except:
        st.title("FERPA")
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ⚙️ PARAMETRIZACIÓN")
    
    # CONTROLES MODULADOS
    with st.expander("🏭 PRODUCCIÓN", expanded=True):
        toneladas_dia = st.slider("Input Diario (Ton)", 100, 500, 200, 10, format="%d t")

    with st.expander("🧱 PRECIOS"):
        precio_bloque = st.slider("Precio Venta Bloque ($)", 0.35, 1.20, 0.65, 0.05, format="$%.2f")
    
    with st.expander("🏗️ GESTIÓN RESIDUOS"):
        precio_tipping = st.slider("Tipping Fee ($/Ton)", 7.0, 30.0, 15.0, 1.0, format="$%d")
        
    with st.expander("🌿 CRÉDITOS AMBIENTALES"):
        precio_bono_co2 = st.slider("Bono CO2 ($/Ton)", 5.0, 50.0, 15.0, 1.0, format="$%d")
        precio_bono_agua = st.slider("Crédito Agua ($/m3)", 5.0, 25.0, 10.0, 1.0, format="$%d")

    # NUEVO: CONTROL DE IMPUESTOS
    with st.expander("🏛️ FISCALIDAD", expanded=True):
        tax_rate_percent = st.slider("Tasa Impuesto Renta (%)", 0, 30, 0, 1, format="%d%%")
        tax_rate_decimal = tax_rate_percent / 100.0

    st.markdown("---")
    st.markdown("##### 💵 MACRO")
    tasa_cambio = st.number_input("CRC/USD", 500.0, 600.0, 520.0)

# --- ENGINE ---
sim = SimuladorFerpaV3(toneladas_dia, precio_bloque, precio_tipping, precio_bono_co2, precio_bono_agua, tasa_cambio, tax_rate_decimal)
df, fisicos, kpis = sim.run_simulation()

# --- PLOTLY THEME ---
def apply_corporate_theme(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Segoe UI, sans-serif", size=14, color="#E0E0E0"),
        title_font=dict(size=20, color="#00FFAA"),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

# --- MAIN CONTENT ---
st.markdown("<h1 style='text-align: left; margin-bottom: 5px;'>SUITE FINANCIERA CORPORATIVA</h1>", unsafe_allow_html=True)
st.markdown(f"<span class='neon-text' style='font-size: 1.2rem; display: block; margin-bottom: 30px;'>PROYECCIÓN FINANCIERA 2025-2035 | ESCENARIO {toneladas_dia} TPD</span>", unsafe_allow_html=True)

# NEW TABS STRUCTURE
tab_resumen, tab_sustentabilidad, tab_reporte = st.tabs(["RESUMEN EJECUTIVO", "SUSTENTABILIDAD", "📑 REPORTE FINANCIERO (TABLAS)"])

# --- TAB A: RESUMEN EJECUTIVO ---
with tab_resumen:
    # 1. KPI MATRIX
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(f"""
        <div class="metric-card">
            {ICON_DOLLAR}
            <div class="metric-label">VALOR PRESENTE NETO (VAN)</div>
            <div class="metric-value neon">${kpis['VAN']/1000000:,.1f} M</div>
        </div>""", unsafe_allow_html=True)
    with k2:
        st.markdown(f"""
        <div class="metric-card">
            {ICON_CHART}
            <div class="metric-label">TASA INTERNA RETORNO (TIR)</div>
            <div class="metric-value neon">{kpis['TIR']*100:.1f}%</div>
        </div>""", unsafe_allow_html=True)
    with k3:
        st.markdown(f"""
        <div class="metric-card">
            {ICON_FACTORY}
            <div class="metric-label">EBITDA PROMEDIO</div>
            <div class="metric-value">${df['EBITDA'].mean():,.0f}</div>
        </div>""", unsafe_allow_html=True)
    with k4:
        st.markdown(f"""
        <div class="metric-card">
            {ICON_LEAF}
            <div class="metric-label">CO2 EVITADO / AÑO</div>
            <div class="metric-value">{fisicos['co2_total']:,.0f} T</div>
        </div>""", unsafe_allow_html=True)

    # 2. CHARTS - Waterfall & Payback
    st.markdown("<br>", unsafe_allow_html=True)
    r1_c1, r1_c2 = st.columns([2, 1])
    
    with r1_c1:
        st.markdown("<h3 class='neon-text'>RECUPERACIÓN DE CAPITAL</h3>", unsafe_allow_html=True)
        # Waterfall Logic Update
        x_wf = ["CAPEX"] + [str(y) for y in df["Año"]]
        y_wf = [-sim.capex] + df["Flujo_Caja"].tolist()
        fig_wf = go.Figure(go.Waterfall(
            name="Flujo", orientation="v", measure=["relative"] * len(y_wf),
            x=x_wf, y=y_wf,
            connector={"line": {"color": "#444"}},
            decreasing={"marker": {"color": "#EF5350", "line": {"width":0}}},
            increasing={"marker": {"color": "#00FFAA", "line": {"width":0}}},
        ))
        fig_wf.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
        st.plotly_chart(apply_corporate_theme(fig_wf), use_container_width=True)

    with r1_c2:
        st.markdown("<h3 class='neon-text'>TIEMPO DE RETORNO</h3>", unsafe_allow_html=True)
        payback = next((i for i, v in enumerate(df["Flujo_Acumulado"]) if v >= 0), 10) + 1
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = payback,
            number = {'suffix': " Años", 'font': {'size': 40, 'color': '#00FFAA'}},
            gauge = {'axis': {'range': [0, 10], 'tickcolor': "#A0AAB5"}, 'bar': {'color': "#00FFAA"}, 'bgcolor': "#161B22"}
        ))
        st.plotly_chart(apply_corporate_theme(fig_gauge), use_container_width=True)

    # 3. PRODUCTION DISTRIBUTION (DONUT) - UPDATED 0 MERMA
    st.markdown("### DISTRIBUCIÓN DE INPUT FABRIL")
    col_d1, col_d2 = st.columns([1, 2])
    with col_d1:
        # DONUT CHART: Reciclable vs Bloque ONLY
        fig_donut = px.pie(
            values=[fisicos['ton_reciclable'], fisicos['ton_bloque']], 
            names=["Recuperación Reciclable", "Transformación a Bloque"],
            color_discrete_sequence=["#F4D03F", "#00FFAA"], # Gold, Neon Green
            hole=0.6
        )
        fig_donut.update_traces(textinfo='percent+label', textfont_size=14)
        st.plotly_chart(apply_corporate_theme(fig_donut), use_container_width=True)
    with col_d2:
         st.info("ℹ️ **NUEVA LÓGICA DE PRODUCCIÓN:** El 100% de la entrada se valoriza. 13% se recupera como reciclable de alto valor y el 87% restante se transforma integralmente en Bloques de Construcción, eliminando el concepto de merma por vertedero.")

# --- TAB B: SUSTENTABILIDAD ---
with tab_sustentabilidad:
    b1, b2 = st.columns(2)
    with b1:
        st.markdown("<h3 class='neon-text'>HUELLA DE CARBONO EVITADA</h3>", unsafe_allow_html=True)
        co2_acum = [fisicos['co2_total'] * i for i in range(1, 11)]
        fig_area = px.area(x=df["Año"], y=co2_acum, labels={'y': 'Ton CO2 Acumuladas'})
        fig_area.update_traces(line_color='#00FFAA', fillcolor='rgba(0, 255, 170, 0.2)')
        st.plotly_chart(apply_corporate_theme(fig_area), use_container_width=True)
        
    with b2:
        st.markdown("<h3 class='neon-text'>EQUIVALENCIA ECOLÓGICA</h3>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="metric-card" style="margin-top: 20px;">
            {ICON_LEAF}
            <div class="metric-label">BOSQUE EQUIVALENTE</div>
            <div class="metric-value neon">{fisicos['arboles']:,.0f}</div>
            <div class="metric-label">ÁRBOLES ADULTOS CONSERVADOS / AÑO</div>
        </div>""", unsafe_allow_html=True)

# --- TAB C: REPORTING (10 TABLES) ---
with tab_reporte:
    st.markdown("### 📑 REPORTE FINANCIERO DETALLADO")
    st.markdown("Consolidado de tablas maestras para auditoría y revisión contable.")
    
    # helper for formatting
    def format_df(dataframe, format_dict=None):
        if format_dict:
            return dataframe.style.format(format_dict)
        return dataframe

    # TABLE 1: PRODUCCIÓN FÍSICA
    with st.expander("TABLA 1: PRODUCCIÓN FÍSICA", expanded=True):
        # Create year range
        years = df["Año"].tolist()
        t1_data = {
            "Año": years,
            "Ton Entrada": [fisicos['ton_input']] * 10,
            "Ton Reciclaje": [fisicos['ton_reciclable']] * 10,
            "Ton Transformación": [fisicos['ton_bloque']] * 10,
            "Cantidad Bloques": [fisicos['num_bloques']] * 10
        }
        df_t1 = pd.DataFrame(t1_data)
        st.dataframe(df_t1.style.format({"Ton Entrada": "{:,.0f}", "Ton Reciclaje": "{:,.0f}", "Ton Transformación": "{:,.0f}", "Cantidad Bloques": "{:,.0f}"}), use_container_width=True)

    # TABLE 2: PRECIOS UNITARIOS
    with st.expander("TABLA 2: PRECIOS UNITARIOS PROYECTADOS"):
        t2_cols = ["Año", "Precio_Bloque_Proy", "Precio_Tipping_Proy", "Precio_BonoCO2_Proy", "Precio_BonoAgua_Proy"]
        df_t2 = df[t2_cols].copy()
        df_t2.columns = ["Año", "Precio Bloque ($)", "Tipping Fee ($/Ton)", "Bono CO2 ($/Ton)", "Bono Agua ($/m3)"]
        st.dataframe(df_t2.style.format("${:,.2f}"), use_container_width=True)

    # TABLE 3: INGRESOS POR LÍNEA
    with st.expander("TABLA 3: INGRESOS POR LÍNEA DE NEGOCIO"):
        t3_cols = ["Año", "Ingresos_Tipping", "Ingresos_Bloques", "Ingresos_Reciclables", "Ingresos_Ambientales", "Ingresos_Totales"]
        df_t3 = df[t3_cols].copy()
        st.dataframe(df_t3.style.format("${:,.0f}"), use_container_width=True)

    # TABLE 4: ESTRUCTURA OPEX
    with st.expander("TABLA 4: ESTRUCTURA OPEX (Costos Operativos)"):
        # OPEX is 45% of Block Sales logic
        t4_data = {
            "Año": df["Año"],
            "Ingresos Bloques": df["Ingresos_Bloques"],
            "Factor OPEX": ["45%"] * 10,
            "OPEX Total": df["OPEX"]
        }
        df_t4 = pd.DataFrame(t4_data)
        st.dataframe(df_t4.style.format({"Ingresos Bloques": "${:,.0f}", "OPEX Total": "${:,.0f}"}), use_container_width=True)

    # TABLE 5: ESTADO DE RESULTADOS (P&L)
    with st.expander("TABLA 5: ESTADO DE RESULTADOS (P&L)", expanded=True):
        t5_cols = ["Año", "Ingresos_Totales", "OPEX", "EBITDA", "Depreciacion", "Impuestos", "Utilidad_Neta"]
        df_t5 = df[t5_cols].copy()
        st.dataframe(df_t5.style.format("${:,.0f}"), use_container_width=True)

    # TABLE 6: FLUJO DE CAJA
    with st.expander("TABLA 6: FLUJO DE CAJA LIBRE"):
        # FC = Net Income + Dep - CAPEX (if any in that year)
        # Year 0 not shown in these annual tables usually, but implicit.
        t6_cols = ["Año", "Utilidad_Neta", "Depreciacion", "Flujo_Caja"]
        df_t6 = df[t6_cols].copy()
        st.dataframe(df_t6.style.format("${:,.0f}"), use_container_width=True)

    # TABLE 7: RETORNO DE INVERSIÓN
    with st.expander("TABLA 7: RETORNO DE INVERSIÓN ACUMULADO"):
        t7_cols = ["Año", "Flujo_Caja", "Flujo_Acumulado"]
        df_t7 = df[t7_cols].copy()
        st.dataframe(df_t7.style.format("${:,.0f}"), use_container_width=True)

    # TABLE 8: IMPACTO AMBIENTAL DETALLADO
    with st.expander("TABLA 8: IMPACTO AMBIENTAL"):
        years = df["Año"]
        t8_data = {
            "Año": years,
            "CO2 Evitado (Ton)": [fisicos['co2_total']] * 10,
            "Lixiviados Evitados (m3)": [fisicos['lixiviados_total']] * 10,
            "Árboles Equivalentes": [fisicos['arboles']] * 10
        }
        df_t8 = pd.DataFrame(t8_data)
        st.dataframe(df_t8.style.format("{:,.0f}"), use_container_width=True)

    # TABLE 9: AHORRO AL MERCADO
    with st.expander("TABLA 9: COMPARATIVA DE MERCADO (AHORRO)"):
        # Assumption: Market Block Price is 25% higher than Ferpa Price for competitive edge
        market_price_base = precio_bloque * 1.25
        
        t9_data = []
        for i, year in enumerate(years):
            inf = (1 + 0.03) ** i
            p_ferpa = precio_bloque * inf
            p_market = market_price_base * inf
            num = fisicos['num_bloques']
            ahorro = (p_market - p_ferpa) * num
            t9_data.append({
                "Año": year,
                "Precio FERPA": p_ferpa,
                "Precio Mercado Est.": p_market,
                "Ahorro Cliente Total": ahorro
            })
        df_t9 = pd.DataFrame(t9_data)
        st.dataframe(df_t9.style.format({"Precio FERPA": "${:,.2f}", "Precio Mercado Est.": "${:,.2f}", "Ahorro Cliente Total": "${:,.0f}"}), use_container_width=True)

    # TABLE 10: RESUMEN EJECUTIVO (KPIs)
    with st.expander("TABLA 10: RESUMEN EJECUTIVO KPI"):
        t10_data = pd.DataFrame({
            "Año": df["Año"],
            "EBITDA": df["EBITDA"],
            "Margen EBITDA": (df["EBITDA"] / df["Ingresos_Totales"]) * 100,
            "Utilidad Neta": df["Utilidad_Neta"],
            "ROI Acumulado": df["Flujo_Acumulado"]
        })
        st.dataframe(t10_data.style.format({
            "EBITDA": "${:,.0f}", 
            "Margen EBITDA": "{:.1f}%", 
            "Utilidad Neta": "${:,.0f}",
            "ROI Acumulado": "${:,.0f}"
        }), use_container_width=True)

