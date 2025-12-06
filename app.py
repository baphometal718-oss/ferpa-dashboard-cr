
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from ferpa_logic import SimuladorFerpaV5

# --- 1. PAGE CONFIG & THEME ---
st.set_page_config(page_title="FERPA FINANCIAL SUITE", page_icon="💎", layout="wide", initial_sidebar_state="expanded")

# CSS: Glassmorphism & Neon
st.markdown("""
<style>
    /* MAIN BACKGROUND */
    .stApp { background-color: #0E1117; color: #FAFAFA; }
    
    /* GLASS CARDS */
    .glass-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    
    /* NEON TEXT */
    .neon-green { color: #00FFAA; text-shadow: 0 0 10px rgba(0, 255, 170, 0.5); font-weight: bold; }
    .neon-red { color: #FF0055; text-shadow: 0 0 10px rgba(255, 0, 85, 0.5); font-weight: bold; }
    .neon-blue { color: #00AAFF; text-shadow: 0 0 10px rgba(0, 170, 255, 0.5); font-weight: bold; }
    
    /* METRICS */
    .metric-label { font-size: 12px; letter-spacing: 1px; color: #BBB; text-transform: uppercase; }
    .metric-val { font-size: 32px; font-weight: 600; color: #FFF; }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { background-color: #161B22; border-radius: 5px; border: 1px solid #333; color: #BBB; }
    .stTabs [aria-selected="true"] { background-color: #00FFAA !important; color: black !important; font-weight: bold; }

    /* EXPANDER */
    .streamlit-expanderHeader { background-color: #161B22; color: white; border: 1px solid #333; }
</style>
""", unsafe_allow_html=True)

# --- 2. SIDEBAR CONTROLS ---
with st.sidebar:
    st.image("logo.png", use_container_width=True)
    st.markdown("### ⚙️ PARÁMETROS DE CONTROL")
    
    with st.expander("🏭 1. OPERACIÓN", expanded=True):
        ton_dia = st.slider("Toneladas / Día", 100, 500, 300)
    
    with st.expander("💰 2. MERCADO Y PRECIOS", expanded=False):
        p_bloque = st.slider("Precio Base Bloque ($)", 0.35, 1.00, 0.55)
        p_tip = st.number_input("Tipping Fee ($/Ton)", 5.0, 30.0, 15.0)
        p_rec = st.number_input("Precio Reciclables ($/Ton)", 50.0, 300.0, 120.0)
    
    with st.expander("🌿 3. BONOS AMBIENTALES", expanded=False):
        p_co2 = st.slider("Precio Ton CO2 ($)", 5.0, 50.0, 15.0)
        p_agua = st.slider("Precio m³ Lixiviado ($)", 5.0, 30.0, 10.0)
        
    with st.expander("🏦 4. INVERSIÓN Y MACRO", expanded=False):
        capex = st.number_input("CAPEX Inicial ($)", 5000000, 20000000, 10000000, 500000)
        roi_target = st.slider("Meta ROI (Años)", 1, 5, 3)
        tax = st.slider("Impuesto Renta (%)", 0, 30, 30)
        inf = st.number_input("Inflación Anual (%)", 0.0, 10.0, 3.0) / 100.0

    st.markdown("---")
    st.caption("FERPA SUITE v5.0")
    st.markdown("<div style='margin-top: 20px; font-size: 11px; color: #666;'>Desarrollado por:<br><strong style='color: #00FFAA;'>Juan Gabriel Ortiz</strong><br>Director de Proyectos</div>", unsafe_allow_html=True)

# --- 3. LOGIC EXECUTION ---
sim = SimuladorFerpaV5(
    t_dia=ton_dia, p_base_bloque=p_bloque, p_tipping=p_tip, p_recic=p_rec,
    p_bono_co2=p_co2, p_bono_agua=p_agua, capex=capex, interest_rate=0.0,
    tax_rate=tax/100.0, inflation=inf, roi_target=roi_target
)
res = sim.run_simulation()
df = res["df"]
m = res["metrics"]

def fmt(x): return f"${x:,.0f}"

# --- 4. MAIN INTERFACE ---
st.markdown("<h1 style='text-align:center;'>💎 FERPA FINANCIAL SUITE <span class='neon-green'>V5</span></h1>", unsafe_allow_html=True)
st.markdown("---")

# TABS
t1, t2, t3, t4, t5 = st.tabs([
    "🏢 DASHBOARD GERENCIAL", "🏭 INGENIERÍA Y VENTAS", "💸 ESTRUCTURA DE COSTOS", 
    "🤝 EL INVERSIONISTA", "📚 BÓVEDA DE DATOS"
])

# === TAB 1: DASHBOARD GERENCIAL ===
with t1:
    # KPIs
    k1, k2, k3, k4 = st.columns(4)
    k1.markdown(f"""<div class="glass-card"><div class="metric-label">VAN (10 AÑOS)</div><div class="metric-val neon-green">{fmt(m['npv'])}</div></div>""", unsafe_allow_html=True)
    k2.markdown(f"""<div class="glass-card"><div class="metric-label">TIR PROYECTO</div><div class="metric-val neon-blue">{m['irr']*100:.1f}%</div></div>""", unsafe_allow_html=True)
    k3.markdown(f"""<div class="glass-card"><div class="metric-label">EBITDA PROMEDIO</div><div class="metric-val">{fmt(df['EBITDA'].mean())}</div></div>""", unsafe_allow_html=True)
    k4.markdown(f"""<div class="glass-card"><div class="metric-label">PROD. TOTAL</div><div class="metric-val">{m['total_prod']/1000000:.1f} M</div><div style="font-size:10px;color:#888">Bloques/Año</div></div>""", unsafe_allow_html=True)
    
    # SANKEY
    st.markdown("### 🌊 FLUJO DE CAJA INTELIGENTE (AÑO 1)")
    y1 = df.iloc[0]
    
    # Sankey Data
    # Nodes: 0:Bloques, 1:Recic, 2:Tipping, 3:Bonos, 4:TOTAL_REV, 
    #        5:OPEX, 6:Impuestos, 7:RetornoCap, 8:Dividendo, 9:CajaFerpa
    labels = ["Venta Bloques", "Venta Recic.", "Tipping Fee", "Bonos Verdes", "INGRESOS TOTALES",
              "OPEX (45%)", "Impuestos", "Retorno Capital", "Dividendos", "Caja Ferpa"]
    s_source = [0, 1, 2, 3, 4, 4, 4, 4, 4]
    s_target = [4, 4, 4, 4, 5, 6, 7, 8, 9]
    s_values = [y1["Rev_Bloques"], y1["Rev_Recic"], y1["Rev_Tipping"], y1["Rev_Bonos"],
                y1["OPEX_Total"], y1["Impuestos"], y1["Pago_Retorno_Capital"], y1["Pago_Dividendos"], y1["Caja_Ferpa"]]
    colors = ["#3498DB", "#F1C40F", "#9B59B6", "#2ECC71", "#FFFFFF", "#E74C3C", "#95A5A6", "#00FFAA", "#00FFAA", "#34495E"]
    
    fig_san = go.Figure(go.Sankey(
        node=dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=labels, color=colors),
        link=dict(source=s_source, target=s_target, value=s_values, color=['rgba(100,100,100,0.3)']*9)
    ))
    fig_san.update_layout(height=500, font_size=12, paper_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig_san, use_container_width=True)

# === TAB 2: INGENIERÍA Y VENTAS ===
with t2:
    c2a, c2b = st.columns([2, 1])
    
    with c2a:
        st.markdown("#### MIX DE INGRESOS (SUNBURST)")
        # Calculate totals for year 1 mix
        mix_data = df[["Bloque #5", "Adoquín Pesado", "Ladrillo Decorativo"]].iloc[0]
        fig_sun = px.sunburst(
            names=["Bloques", "Adoquines", "Ladrillos"],
            parents=["Mix", "Mix", "Mix"],
            values=[mix_data["Bloque #5"], mix_data["Adoquín Pesado"], mix_data["Ladrillo Decorativo"]],
            color_discrete_sequence=px.colors.sequential.Teal
        )
        fig_sun.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_sun, use_container_width=True)
        
    with c2b:
        st.markdown("#### PERFORMANCE")
        # Gauge 1 Capacity
        cap_util = min(100, (m['total_prod'] / 35000000)*100) # Assuming 35M max
        fig_g1 = go.Figure(go.Indicator(mode="gauge+number", value=cap_util, title={'text':"Uso Planta %"}, gauge={'axis':{'range':[0,100]}, 'bar':{'color':"#00FFAA"}}))
        fig_g1.update_layout(height=200, margin=dict(t=30,b=10,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_g1, use_container_width=True)
        
        # Gauge 2 Sales Target
        sales_target = 10000000 # Example target
        sales_pct = min(100, (y1["Ingresos"] / sales_target)*100)
        fig_g2 = go.Figure(go.Indicator(mode="gauge+number", value=sales_pct, title={'text':"Meta Ventas %"}, gauge={'axis':{'range':[0,100]}, 'bar':{'color':"#FF0055"}}))
        fig_g2.update_layout(height=200, margin=dict(t=30,b=10,l=20,r=20), paper_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig_g2, use_container_width=True)

    with st.expander("📋 PLAN DE PRODUCCIÓN DETALLADO", expanded=True):
        prod_df = df[["Año", "Unidades_Total"]].copy()
        prod_df["Bloques #5 (70%)"] = prod_df["Unidades_Total"] * 0.7
        prod_df["Adoquines (20%)"] = prod_df["Unidades_Total"] * 0.2
        prod_df["Ladrillos (10%)"] = prod_df["Unidades_Total"] * 0.1
        st.dataframe(prod_df.style.format("{:,.0f}"), use_container_width=True)

# === TAB 3: ESTRUCTURA DE COSTOS ===
with t3:
    st.markdown("#### MAPA DE CALOR DE COSTOS (TREEMAP)")
    # Treemap Data
    y1 = df.iloc[0]
    labels_tree = ["OPEX TOTAL", "Insumos/Variable", "Nómina", "ENERGÍA ($500k)"]
    parents_tree = ["", "OPEX TOTAL", "OPEX TOTAL", "OPEX TOTAL"]
    values_tree = [0, y1["Cost_Variable"], y1["Cost_Payroll"], y1["Cost_Energy"]] # Root value ignored by Plotly usually or calc sum
    
    fig_tree = go.Figure(go.Treemap(
        labels = labels_tree,
        parents = parents_tree,
        values =  [y1["OPEX_Total"], y1["Cost_Variable"], y1["Cost_Payroll"], y1["Cost_Energy"]],
        textinfo = "label+value+percent parent",
        marker_colors = ["#333", "#2E86C1", "#1ABC9C", "#FF0055"]
    ))
    fig_tree.update_layout(height=400, paper_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig_tree, use_container_width=True)
    
    st.markdown("#### 📉 REGLA DEL 45%: CÁLCULO")
    opex_check = df[["Año", "Rev_Bloques", "OPEX_Total", "Cost_Energy"]].copy()
    opex_check["% Real"] = (opex_check["OPEX_Total"] / opex_check["Rev_Bloques"]) * 100
    st.dataframe(opex_check.style.format({"Rev_Bloques": "${:,.0f}", "OPEX_Total": "${:,.0f}", "Cost_Energy": "${:,.0f}", "% Real": "{:.1f}%"}), use_container_width=True)

# === TAB 4: EL INVERSIONISTA ===
with t4:
    st.markdown("### 🧬 ADN DE RETORNO Y GANANCIA")
    
    # Combo Chart
    fig_combo = go.Figure()
    # Bars: Payments
    fig_combo.add_trace(go.Bar(x=df["Año"], y=df["Pago_Retorno_Capital"], name="Retorno Capital", marker_color="#00FFAA"))
    fig_combo.add_trace(go.Bar(x=df["Año"], y=df["Pago_Dividendos"], name="Dividendos", marker_color="#3498DB"))
    # Line: Remaining Investment
    fig_combo.add_trace(go.Scatter(x=df["Año"], y=df["Saldo_Inversion"], name="Saldo Inversión", mode='lines+markers', line=dict(color='#FF0055', width=3)))
    
    fig_combo.update_layout(barmode='stack', title="Flujo al Socio vs Saldo Pendiente", 
                            height=450, paper_bgcolor='rgba(0,0,0,0)', font_color="white",
                            yaxis=dict(title="Flujo ($)"), yaxis2=dict(title="Saldo", overlaying="y", side="right"))
    st.plotly_chart(fig_combo, use_container_width=True)
    
    with st.expander("🧾 CRONOGRAMA DE PAGOS EXACTO (Recortar para Contrato)", expanded=True):
        pay_df = df[["Año", "Pago_Retorno_Capital", "Pago_Dividendos", "Flujo_Investor_Total", "Saldo_Inversion"]]
        st.dataframe(pay_df.style.format(fmt), use_container_width=True)

# === TAB 5: BÓVEDA DE DATOS ===
with t5:
    vault = {
        "📊 Detalle de Producción Física": df[["Año", "Unidades_Total"]],
        "💰 Proyección de Precios e Ingresos": df[["Año", "Ingresos", "Rev_Bloques", "Rev_Recic", "Rev_Tipping", "Rev_Bonos"]],
        "🛠️ Nómina y OPEX Detallado": df[["Año", "OPEX_Total", "Cost_Energy", "Cost_Payroll", "Cost_Variable"]],
        "📈 Estado de Resultados (P&L) Completo": df[["Año", "EBITDA", "Deprec", "Impuestos", "Utilidad_Neta"]],
        "🌍 Impacto Ambiental": df[["Año", "Rev_Bonos"]] # Proxy
    }
    
    for name, data in vault.items():
        with st.expander(name):
            st.dataframe(data.style.format(fmt) if "Año" in data.columns else data, use_container_width=True)

st.caption("FERPA FINANCIAL SUITE v5 | POWERED BY PYTHON CORTEX ENGINE")
