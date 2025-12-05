import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from streamlit_lottie import st_lottie
import requests
import os

# ==========================================
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO NEÓN
# ==========================================
st.set_page_config(
    page_title="FERPA Financial Suite",
    page_icon="♻️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Función para cargar animaciones Lottie
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# CSS Personalizado (Dark Mode + Neon Glow + Glassmorphism)
st.markdown("""
<style>
    /* Fondo General */
    .stApp {
        background-color: #0E1117;
        color: #FAFAFA;
    }
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161B22;
        border-right: 1px solid #30363D;
    }
    /* Tarjetas de Métricas (Glassmorphism) */
    div[data-testid="metric-container"] {
        background: rgba(22, 27, 34, 0.7);
        border: 1px solid #30363D;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        border-color: #00FFAA;
        box-shadow: 0 0 15px rgba(0, 255, 170, 0.3);
    }
    /* Texto Neón para valores clave */
    div[data-testid="metric-container"] label {
        color: #8B949E !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        color: #00FFAA !important;
        text-shadow: 0 0 10px rgba(0, 255, 170, 0.4);
        font-weight: bold;
    }
    /* Títulos Principales */
    h1, h2, h3 {
        color: #FAFAFA !important;
    }
    .neon-text {
        color: #00FFAA;
        font-weight: bold;
        text-shadow: 0 0 10px rgba(0, 255, 170, 0.8);
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. LÓGICA MATEMÁTICA (EL CEREBRO V3)
# ==========================================
# Esta clase está PEGADA AQUÍ para evitar errores de importación
class SimuladorFerpaV3:
    def __init__(self, params):
        self.p = params

    def calcular_impacto_ambiental(self):
        """Calcula los volúmenes para Bonos Verdes y Créditos de Agua"""
        ton_anual = self.p["TONELADAS_DIA"] * self.p["DIAS_OPERACION"]
        # Factor CO2: 1.8 Ton evitadas por Ton RSU (Landfill Diversion)
        ton_co2_evitado = ton_anual * 1.8 
        # Factor Lixiviados: 0.25 m3 por Ton RSU
        m3_lixiviado_evitado = ton_anual * 0.25
        return ton_co2_evitado, m3_lixiviado_evitado

    def calcular_produccion_bloques(self):
        """Lógica de expansión química de Ferpa"""
        ton_entrada = self.p["TONELADAS_DIA"]
        # Retiro reciclables (13%)
        ton_procesable = ton_entrada * (1 - 0.13) 
        
        # Ingeniería inversa: Expansión de masa (químicos + lixiviados)
        # Factor 1.17 de expansión. Peso bloque aprox 3.8kg
        bloques_dia = (ton_procesable * 1000 * 1.17) / 3.8
        
        bloques_anuales = bloques_dia * self.p["DIAS_OPERACION"]
        return bloques_anuales

    def ejecutar_proyeccion(self):
        flujos = []
        acumulado = -self.p["CAPEX"]
        co2, lixiviados = self.calcular_impacto_ambiental()
        bloques_anuales = self.calcular_produccion_bloques()
        
        # Año 0
        flujos.append({
            "Año": 2025, "Tipo": "Inversión", "Ingresos_Totales": 0, 
            "EBITDA": -self.p["CAPEX"], "Flujo_Acumulado": acumulado
        })

        for i in range(1, 11): # 10 años
            inf = (1 + self.p["INFLACION"])**(i-1)
            
            # --- INGRESOS ---
            # 1. Tipping Fee
            ing_tipping = (self.p["TONELADAS_DIA"] * 365) * self.p["PRECIO_TIPPING_FEE"] * inf
            # 2. Resiblock
            ing_bloques = bloques_anuales * self.p["PRECIO_BLOQUE"] * inf
            # 3. Reciclables (13% fijo)
            ing_reciclables = (self.p["TONELADAS_DIA"] * 365 * 0.13) * 185.0 * inf
            # 4. Bonos Verdes
            ing_bonos_co2 = co2 * self.p["PRECIO_BONO_CO2"] * inf
            ing_bonos_agua = lixiviados * self.p["PRECIO_CREDITO_AGUA"] * inf
            total_ambiental = ing_bonos_co2 + ing_bonos_agua
            
            total_ingresos = ing_tipping + ing_bloques + ing_reciclables + total_ambiental
            
            # --- EGRESOS (OPEX 45% Regla) ---
            # Costo industrial (45% venta bloque) + Costo operativo patio (15% tipping)
            opex = (ing_bloques * 0.45) + (ing_tipping * 0.15)
            
            ebitda = total_ingresos - opex
            neto = ebitda - (ebitda * 0.30) # Impuesto 30%
            acumulado += neto
            
            flujos.append({
                "Año": 2025 + i,
                "Tipo": "Operación",
                "Ingresos_Totales": total_ingresos,
                "Ingresos_Bloques": ing_bloques,
                "Ingresos_Ambientales": total_ambiental,
                "Ingresos_Tipping": ing_tipping,
                "OPEX": opex,
                "EBITDA": ebitda,
                "Utilidad_Neta": neto,
                "Flujo_Acumulado": acumulado
            })
            
        return pd.DataFrame(flujos)

# ==========================================
# 3. INTERFAZ GRÁFICA (SIDEBAR & MAIN)
# ==========================================

# --- SIDEBAR: CONTROLES ---
with st.sidebar:
    # Logo Corporativo
    if os.path.exists("logo.png"):
        st.image("logo.png", use_column_width=True)
    else:
        st.markdown("<h2 class='neon-text'>FERPA CR</h2>", unsafe_allow_html=True)
        st.warning("⚠️ Sube 'logo.png' a GitHub")

    st.markdown("### 🎛️ Centro de Control")
    
    # Inputs conectados al Cerebro
    toneladas = st.slider("♻️ Toneladas Diarias (RSU)", 100, 500, 200)
    precio_bloque = st.slider("🧱 Precio Resiblock (USD)", 0.35, 1.00, 0.50)
    tipping_fee = st.slider("🚛 Tipping Fee / Entrada (USD)", 5.0, 30.0, 15.0)
    
    st.markdown("---")
    st.markdown("### 🌱 Mercado Ambiental")
    precio_co2 = st.slider("💨 Precio Bono CO2", 5.0, 50.0, 20.0)
    precio_agua = st.slider("💧 Precio Crédito Agua", 5.0, 40.0, 12.0)

    st.markdown("---")
    roi_meta = st.slider("🎯 Meta ROI (Años)", 1, 5, 2)
    tasa_cambio = st.number_input("💱 Tasa Cambio (CRC)", value=515.0)

# --- EJECUCIÓN DE SIMULACIÓN ---
PARAMS = {
    "TONELADAS_DIA": toneladas,
    "PRECIO_TIPPING_FEE": tipping_fee,
    "PRECIO_BLOQUE": precio_bloque,
    "PRECIO_BONO_CO2": precio_co2,
    "PRECIO_CREDITO_AGUA": precio_agua,
    "DIAS_OPERACION": 365,
    "INFLACION": 0.03,
    "CAPEX": 10000000.0
}

sim = SimuladorFerpaV3(PARAMS)
df = sim.ejecutar_proyeccion()

# --- HEADER ANIMADO ---
col_head1, col_head2 = st.columns([1, 3])
with col_head1:
    lottie_eco = load_lottieurl("https://assets5.lottiefiles.com/packages/lf20_zPrHZK.json")
    if lottie_eco:
        st_lottie(lottie_eco, height=120, key="eco")
with col_head2:
    st.markdown("<h1 style='padding-top:20px;'>FERPA <span class='neon-text'>COSTA RICA</span></h1>", unsafe_allow_html=True)
    st.markdown("##### Financial Intelligence Dashboard 2025-2035")

# --- KPI CARDS SUPERIORES ---
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
roi_year = df[df["Flujo_Acumulado"] >= 0]["Año"].min()
van_estimado = df["Flujo_Neto"].sum() - 10000000

kpi1.metric("VAN Estimado (10 Años)", f"${van_estimado/1e6:,.1f} M", "+High Growth")
kpi2.metric("Punto de Equilibrio", f"Año {roi_year}" if not pd.isna(roi_year) else "> 10 Años", "Target: Año 2027")
kpi3.metric("EBITDA Promedio", f"${df[df['Tipo']=='Operación']['EBITDA'].mean()/1e6:,.1f} M", "Margen Saludable")
kpi4.metric("Ingreso Ambiental", f"${df['Ingresos_Ambientales'].sum()/1e6:,.1f} M", "Bonos Verdes")

# --- PESTAÑAS PRINCIPALES ---
tab1, tab2, tab3 = st.tabs(["📈 Dashboard Ejecutivo", "🌍 Impacto Ambiental", "📊 Ingeniería 3D"])

# TAB 1: DASHBOARD
with tab1:
    st.markdown("### 🌊 Curva de Retorno de Inversión (Waterfall)")
    
    # Gráfico de Línea con área de Inversión
    fig_roi = go.Figure()
    fig_roi.add_trace(go.Scatter(x=df["Año"], y=df["Flujo_Acumulado"], fill='tozeroy', 
                                mode='lines+markers', name='Flujo Acumulado',
                                line=dict(color='#00FFAA', width=4)))
    
    fig_roi.add_hline(y=0, line_dash="dash", line_color="white", annotation_text="Break Even Point")
    
    fig_roi.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=400)
    st.plotly_chart(fig_roi, use_container_width=True)
    
    col_g1, col_g2 = st.columns(2)
    
    with col_g1:
        st.markdown("### 💰 Mix de Ingresos")
        # Gráfico de Dona
        total_sources = df[df["Tipo"]=="Operación"][["Ingresos_Bloques", "Ingresos_Tipping", "Ingresos_Ambientales"]].sum()
        fig_don = px.pie(names=["Resiblock", "Tipping Fee", "Bonos Verdes"], 
                         values=[total_sources["Ingresos_Bloques"], total_sources["Ingresos_Tipping"], total_sources["Ingresos_Ambientales"]],
                         hole=0.6, color_discrete_sequence=["#00FFAA", "#00B4D8", "#7209B7"])
        fig_don.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_don, use_container_width=True)
        
    with col_g2:
        st.markdown("### 📉 Estado de Resultados (Tabla)")
        st.dataframe(df[["Año", "Ingresos_Totales", "OPEX", "EBITDA", "Utilidad_Neta"]].style.format("${:,.0f}"))

# TAB 2: AMBIENTAL
with tab2:
    col_amb1, col_amb2 = st.columns(2)
    ton_co2, m3_lix = sim.calcular_impacto_ambiental()
    
    with col_amb1:
        st.markdown("### ☁️ Huella de Carbono Positiva")
        st.metric("CO2e Evitado Anual", f"{ton_co2:,.0f} Toneladas", "Créditos VCC")
        st.info(f"Equivale a sacar de circulación {int(ton_co2/4.6)} autos al año.")
        
    with col_amb2:
        st.markdown("### 💧 Protección de Mantos Acuíferos")
        st.metric("Lixiviados Evitados", f"{m3_lix:,.0f} m³", "Líquido Tóxico")
        st.info("Volumen crítico de lixiviados desviados de suelos de Santa Ana.")

# TAB 3: 3D ENGINEERING
with tab3:
    st.markdown("### 🧊 Análisis de Sensibilidad 3D")
    st.markdown("Gira el gráfico para ver cómo cambia la Utilidad Neta según Tipping Fee y Precio Bloque.")
    
    # Generar matriz para 3D
    x_tip = np.linspace(5, 30, 20)
    y_bloque = np.linspace(0.3, 1.0, 20)
    X, Y = np.meshgrid(x_tip, y_bloque)
    
    # Simulación simplificada para la superficie Z
    # Z = Utilidad Aprox Año 2
    bloques_anual = sim.calcular_produccion_bloques()
    Z = ((X * 200 * 365) + (bloques_anual * Y) + 1000000) * 0.5 # Margen 50% aprox
    
    fig_3d = go.Figure(data=[go.Surface(z=Z, x=X, y=Y, colorscale='Viridis')])
    fig_3d.update_layout(title='Utilidad Operativa vs Precios', autosize=True,
                         scene=dict(xaxis_title='Tipping Fee ($)', yaxis_title='Precio Bloque ($)', zaxis_title='Utilidad ($)'),
                         template="plotly_dark", margin=dict(l=0, r=0, b=0, t=30))
    st.plotly_chart(fig_3d, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("<div style='text-align: center; color: #555;'>FERPA Technology © 2025 | Sistema de Simulación Financiera v3.0</div>", unsafe_allow_html=True)
