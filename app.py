import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
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
        border: 1px solid rgba(0, 255, 170, 0.2); /* Borde sutil verde marca */
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
    
    </style>
    """, unsafe_allow_html=True)

corporate_css()

# --- ICONOS SVG (MODERNOS & LIMPIOS) ---
ICON_DOLLAR = """<svg class="metric-icon" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm.31-8.86c-1.77-.45-2.34-.94-2.34-1.67 0-.84.79-1.43 2.1-1.43 1.38 0 1.9.66 1.94 1.64h1.71c-.05-1.34-.87-2.57-2.49-2.97V5H10.9v1.69c-1.51.32-2.72 1.3-2.72 2.81 0 1.79 1.49 2.69 3.66 3.21 1.95.46 2.34 1.15 2.34 1.87 0 .53-.39 1.39-2.1 1.39-1.6 0-2.23-.72-2.32-1.64H8.04c.1 1.7 1.36 2.66 2.86 2.97V19h2.34v-1.67c1.52-.29 2.72-1.16 2.73-2.77-.01-2.2-1.9-2.96-3.66-3.42z"/></svg>"""
ICON_FACTORY = """<svg class="metric-icon" viewBox="0 0 24 24"><path d="M22 22H2V10l7-3v2l5-2v3h3l1-8h3l1 8v12zM12 9.95l-5 2V10l-3 1.32V20h16v-8h-8V9.95z"/></svg>"""
ICON_LEAF = """<svg class="metric-icon" viewBox="0 0 24 24"><path d="M17 8C8 10 5.9 16.17 3.82 21.34l1.89.66.95-2.3c.48.17 1.01.29 1.57.33l1.61-3.18c.63.13 1.25.12 1.89-.04l2.16 2.93 1.66-2.93c1.76-.75 3.01-2.26 3.45-5.81zM7 21l-.95-2.28c.19-.55.45-1.1.77-1.65.31-.54.67-1.07 1.09-1.59l1.63 3.19c-.83.67-1.72 1.42-2.54 2.33zm11-13c-3.31 0-6 2.69-6 6 0 1.66.67 3.15 1.76 4.24l-3.33-5.86c.32-.46.7-.89 1.15-1.28l3.33 5.86c1.09-1.09 1.76-2.58 1.76-4.24 0-3.31-2.69-6-6-6z"/></svg>"""
ICON_CHART = """<svg class="metric-icon" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/></svg>"""

# --- SIDEBAR: BRANDING & CONTROL ---
with st.sidebar:
    # 1. LOGO CORPORATIVO
    try:
        st.image("logo.png", width=220) # Centered automatically by Streamlit usually, width helps
    except:
        st.title("FERPA") # Fallback
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ⚙️ PARAMETRIZACIÓN")
    
    # CONTROLES AGRUPADOS
    with st.expander("🏭 PRODUCCIÓN & CAPACIDAD", expanded=True):
        toneladas_dia = st.slider("Input Diario (Ton)", 100, 500, 250, 10, format="%d t")

    with st.expander("🧱 ECONOMÍA DEL BLOQUE"):
        precio_bloque = st.slider("Precio Venta ($)", 0.35, 1.00, 0.65, 0.05, format="$%.2f")
    
    with st.expander("🏗️ GESTIÓN DE RESIDUOS"):
        precio_tipping = st.slider("Tipping Fee ($/Ton)", 7.0, 30.0, 15.0, 1.0, format="$%d")
        
    with st.expander("🌿 CRÉDITOS AMBIENTALES"):
        precio_bono_co2 = st.slider("Bono CO2 ($/Ton)", 10.0, 30.0, 15.0, 1.0, format="$%d")
        precio_bono_agua = st.slider("Crédito Agua ($/m3)", 5.0, 25.0, 10.0, 1.0, format="$%d")

    st.markdown("---")
    st.markdown("##### 💵 VARIABLES MACRO")
    col_mac1, col_mac2 = st.columns(2)
    with col_mac1:
        tasa_cambio = st.number_input("CRC/USD", 500.0, 600.0, 520.0)
    with col_mac2:
        meta_roi = st.number_input("Meta ROI (Años)", 1, 5, 2)

# --- SIMULATION ENGINE ---
sim = SimuladorFerpaV3(toneladas_dia, precio_bloque, precio_tipping, precio_bono_co2, precio_bono_agua, tasa_cambio)
df, fisicos, kpis = sim.run_simulation()
df_sens_tip, df_sens_ton = sim.get_sensitivity()

# --- PLOTLY THEME CONFIG ---
def apply_corporate_theme(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(
            family="Segoe UI, sans-serif",
            size=14, # Legibilidad aumentada
            color="#E0E0E0"
        ),
        title_font=dict(
            size=20,
            color="#00FFAA" # Neon Brand Title
        ),
        hoverlabel=dict(
            bgcolor="#161B22",
            font_size=14
        ),
        margin=dict(l=40, r=40, t=60, b=40)
    )
    # Update axes visibility
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.1)')
    return fig

# --- MAIN CONTENT ---
st.markdown("<h1 style='text-align: left; margin-bottom: 5px;'>SUITE FINANCIERA CORPORATIVA</h1>", unsafe_allow_html=True)
st.markdown(f"<span class='neon-text' style='font-size: 1.2rem; display: block; margin-bottom: 30px;'>PROYECCIÓN FINANCIERA 2025-2035 | ESCENARIO {toneladas_dia} TPD</span>", unsafe_allow_html=True)

# TABS
tab_a, tab_b, tab_c, tab_d = st.tabs(["RESUMEN EJECUTIVO", "SUSTENTABILIDAD", "INGENIERÍA", "ANÁLISIS FINANCIERO"])

# --- TAB A: EXECUTIVE ---
with tab_a:
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

    # 2. CHARTS ROW 1
    st.markdown("<br>", unsafe_allow_html=True)
    r1_c1, r1_c2 = st.columns([2, 1])
    
    with r1_c1:
        st.markdown("<h3 class='neon-text'>RECUPERACIÓN DE CAPITAL (ROI)</h3>", unsafe_allow_html=True)
        # Waterfall
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
            gauge = {
                'axis': {'range': [0, 10], 'tickcolor': "#A0AAB5"},
                'bar': {'color': "#00FFAA"},
                'bgcolor': "#161B22",
                'bordercolor': "#30363D"
            }
        ))
        st.plotly_chart(apply_corporate_theme(fig_gauge), use_container_width=True)

    # 3. CHARTS ROW 2
    r2_c1, r2_c2 = st.columns(2)
    with r2_c1:
        st.markdown("### COMPOSICIÓN DE INGRESOS")
        fig_stack = px.bar(df, x="Año", y=["Ingresos_Tipping", "Ingresos_Bloques", "Ingresos_Reciclables", "Ingresos_Ambientales"],
                           color_discrete_sequence=["#2E86C1", "#00FFAA", "#F4D03F", "#27AE60"])
        st.plotly_chart(apply_corporate_theme(fig_stack), use_container_width=True)
    
    with r2_c2:
        st.markdown("### EBITDA vs UTILIDAD NETA")
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=df["Año"], y=df["EBITDA"], name="EBITDA", 
                                      line=dict(width=4, color='#00FFAA'), mode='lines+markers'))
        fig_line.add_trace(go.Scatter(x=df["Año"], y=df["Utilidad_Neta"], name="Net Income", 
                                      line=dict(dash='dot', width=2, color='#E0E0E0')))
        st.plotly_chart(apply_corporate_theme(fig_line), use_container_width=True)

# --- TAB B: ENVIRONMENTAL ---
with tab_b:
    b1, b2 = st.columns(2)
    with b1:
        st.markdown("<h3 class='neon-text'>IMPACTO DE CARBONO ACUMULADO</h3>", unsafe_allow_html=True)
        co2_acum = [fisicos['co2_total'] * i for i in range(1, 11)]
        fig_area = px.area(x=df["Año"], y=co2_acum)
        fig_area.update_traces(line_color='#00FFAA', fillcolor='rgba(0, 255, 170, 0.2)')
        st.plotly_chart(apply_corporate_theme(fig_area), use_container_width=True)
        
    with b2:
        st.markdown("<h3 class='neon-text'>EQUIVALENCIA ECOLÓGICA</h3>", unsafe_allow_html=True)
        # Visual Metric Card for Trees
        st.markdown(f"""
        <div class="metric-card" style="margin-top: 20px;">
            {ICON_LEAF}
            <div class="metric-label">BOSQUE EQUIVALENTE</div>
            <div class="metric-value neon">{fisicos['arboles']:,.0f}</div>
            <div class="metric-label">ÁRBOLES PLANTADOS / AÑO</div>
        </div>""", unsafe_allow_html=True)

# --- TAB C: ENGINEERING ---
with tab_c:
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### BALANCE DE MASA (INPUT vs OUTPUT)")
        fig_io = go.Figure(data=[
            go.Bar(name='Input RSU', x=['Masa Total'], y=[fisicos['ton_input']], marker_color='#E0E0E0'),
            go.Bar(name='Output Bloques', x=['Masa Total'], y=[fisicos['ton_bloque']], marker_color='#00FFAA')
        ])
        st.plotly_chart(apply_corporate_theme(fig_io), use_container_width=True)
        
    with c2:
        st.markdown("### DETALLE DE TRANSFORMACIÓN")
        fig_mass = px.pie(values=[fisicos['ton_reciclable'], fisicos['ton_bloque'], fisicos['ton_input']*0.25], 
                          names=["Reciclables", "Bloques", "Merma"], 
                          color_discrete_sequence=["#F4D03F", "#00FFAA", "#EF5350"], hole=0.6)
        st.plotly_chart(apply_corporate_theme(fig_mass), use_container_width=True)

    st.markdown("### HOJA DE PRODUCCIÓN ANUAL")
    df_fisicos = pd.DataFrame([fisicos]).T.rename(columns={0: "Valor Anual"})
    st.markdown(df_fisicos.to_html(classes='table table-dark'), unsafe_allow_html=True)

# --- TAB D: FINANCE ---
with tab_d:
    d1, d2 = st.columns([3, 1])
    with d1:
        st.markdown("<h3 class='neon-text'>SUPERFICIE DE RENTABILIDAD (SENSIBILIDAD)</h3>", unsafe_allow_html=True)
        x_3d, y_3d, z_3d = sim.get_3d_matrix()
        fig_3d = go.Figure(data=[go.Surface(z=z_3d, x=x_3d, y=y_3d, colorscale='Viridis')])
        fig_3d.update_layout(scene = dict(
            xaxis_title='Tipping Fee', yaxis_title='Precio Bloque', zaxis_title='Utilidad'),
            margin=dict(l=0, r=0, b=0, t=0), height=600)
        st.plotly_chart(apply_corporate_theme(fig_3d), use_container_width=True)
        
    with d2:
        st.markdown("### KPI DE EFICIENCIA")
        st.markdown(f"""
        <div class="metric-card">
            {ICON_FACTORY}
            <div class="metric-label">MARGEN EBITDA</div>
            <div class="metric-value neon">{(df['EBITDA'].sum() / df['Ingresos_Totales'].sum())*100:.1f}%</div>
        </div>""", unsafe_allow_html=True)
        
    st.markdown("### ESTADO DE RESULTADOS DETALLADO")
    st.markdown(df.style.format("${:,.0f}").to_html(), unsafe_allow_html=True)
