import pandas as pd
import numpy_financial as npf
import numpy as np

# Default Parameters for V3
PARAMS_V3 = {
    "INFLACION_ANUAL": 0.03,
    "CRECIMIENTO_PRODUCCION": 0.0, # Flat growth for now
    "DIAS_OPERATIVOS_ANUAL": 312,
}

# Advanced Logic Defaults
LOGICA_AMBIENTAL = {
    "FACTOR_CO2_TON_RSU": 1.5,      # Tons of CO2 avoided per Ton of waste diverted
    "FACTOR_LIXIVIADOS_M3_TON": 0.4, # m3 of Leachate avoided per Ton of waste
    "ARBOL_EQUIVALENTE_CO2": 0.02,   # 20kg CO2 per tree/year approx
}

class SimuladorFerpaV3:
    def __init__(self, t_dia, p_bloque, p_tipping, p_bono_co2, p_bono_agua, tasa_cambio):
        self.t_dia = t_dia # Toneladas Diarias
        self.p_bloque = p_bloque
        self.p_tipping = p_tipping
        self.p_bono_co2 = p_bono_co2
        self.p_bono_agua = p_bono_agua
        self.tasa_cambio = tasa_cambio
        
        # Fixed Assumptions
        self.capex = 10000000 # $10M
        self.opex_ratio = 0.45 # "Regla del 45%" from user prompt Tab D hint
        self.tax_rate = 0.30
        self.tasa_descuento = 0.12
        
        # Mass Balance
        self.pct_reciclable = 0.15
        self.pct_bloque = 0.60
        self.pct_merma = 0.25 # Remaining
        self.peso_bloque = 1.7 # Lightweight
        
        self.params = PARAMS_V3
        self.env = LOGICA_AMBIENTAL

    def run_simulation(self, years=10):
        # 1. Physics & Production
        ton_anual_input = self.t_dia * self.params["DIAS_OPERATIVOS_ANUAL"]
        
        ton_reciclable = ton_anual_input * self.pct_reciclable
        ton_bloque_masa = ton_anual_input * self.pct_bloque
        ton_merma = ton_anual_input * self.pct_merma
        
        num_bloques = (ton_bloque_masa * 1000) / self.peso_bloque
        
        # 2. Environmental Impact
        co2_evitado = ton_anual_input * self.env["FACTOR_CO2_TON_RSU"]
        lixiviados_evitados = ton_anual_input * self.env["FACTOR_LIXIVIADOS_M3_TON"]
        arboles_equiv = co2_evitado / self.env["ARBOL_EQUIVALENTE_CO2"]
        
        # 3. Financial Loop
        flujos = []
        
        for i in range(1, years + 1):
            year = 2025 + i
            inf = (1 + self.params["INFLACION_ANUAL"]) ** (i - 1)
            
            # Revenues
            rev_tipping = ton_anual_input * self.p_tipping * inf
            rev_bloques = num_bloques * self.p_bloque * inf
            rev_reciclables = ton_reciclable * 185.0 * inf # Fixed price for recyclables
            
            # Environmental Revenues
            rev_bonos_co2 = co2_evitado * self.p_bono_co2 * inf
            rev_bonos_agua = lixiviados_evitados * self.p_bono_agua * inf
            
            total_rev = rev_tipping + rev_bloques + rev_reciclables + rev_bonos_co2 + rev_bonos_agua
            
            # Costs
            opex = total_rev * self.opex_ratio
            ebitda = total_rev - opex
            
            # Taxes
            taxes = ebitda * self.tax_rate
            net_income = ebitda - taxes
            
            flujos.append({
                "Año": year,
                "Ingresos_Totales": total_rev,
                "Ingresos_Tipping": rev_tipping,
                "Ingresos_Bloques": rev_bloques,
                "Ingresos_Reciclables": rev_reciclables,
                "Ingresos_CO2": rev_bonos_co2,
                "Ingresos_Agua": rev_bonos_agua,
                "Ingresos_Ambientales": rev_bonos_co2 + rev_bonos_agua,
                "OPEX": opex,
                "EBITDA": ebitda,
                "Impuestos": taxes,
                "Utilidad_Neta": net_income,
                "Flujo_Caja": net_income # Simplified
            })
            
        df = pd.DataFrame(flujos)
        
        # Metrics
        df["Flujo_Acumulado"] = df["Flujo_Caja"].cumsum() - self.capex
        
        cf_array = [-self.capex] + df["Flujo_Caja"].tolist()
        van = npf.npv(self.tasa_descuento, cf_array)
        tir = npf.irr(cf_array)
        
        # Physics DataFrame (same every year essentially, but for display)
        metrics_fisicos = {
            "ton_input": ton_anual_input,
            "ton_reciclable": ton_reciclable,
            "ton_bloque": ton_bloque_masa,
            "num_bloques": num_bloques,
            "co2_total": co2_evitado,
            "lixiviados_total": lixiviados_evitados,
            "arboles": arboles_equiv
        }
        
        return df, metrics_fisicos, {"VAN": van, "TIR": tir}

    def get_sensitivity(self):
        # Quick sensitivity analysis for graph 14 and 20
        # Varying Tipping Fee
        sens_tipping = []
        for p in range(5, 50, 5):
            # manual calc for speed
            rev = (self.t_dia*312) * p + (self.t_dia*312*0.6*1000/1.7)*self.p_bloque # simplified
            # This is too simple, better to run simulation? 
            # Let's just run lightweight sims
            sim = SimuladorFerpaV3(self.t_dia, self.p_bloque, p, self.p_bono_co2, self.p_bono_agua, self.tasa_cambio)
            df, _, _ = sim.run_simulation(1) # 1 year
            sens_tipping.append({"Tipping_Fee": p, "EBITDA": df.iloc[0]["EBITDA"]})
            
        # Varying Toneladas
        sens_ton = []
        for t in range(100, 600, 50):
            sim = SimuladorFerpaV3(t, self.p_bloque, self.p_tipping, self.p_bono_co2, self.p_bono_agua, self.tasa_cambio)
            df, _, _ = sim.run_simulation(1)
            sens_ton.append({"Toneladas": t, "Ventas_Totales": df.iloc[0]["Ingresos_Totales"]})
            
        return pd.DataFrame(sens_tipping), pd.DataFrame(sens_ton)

    def get_3d_matrix(self):
        # Generate meshgrid data for 3D Surface Plot
        # X = Tipping Fee ($5 to $40)
        # Y = Block Price ($0.30 to $1.20)
        # Z = Utilidad Neta (Year 1)
        
        x_vals = np.linspace(5, 40, 15) # Tipping Fee
        y_vals = np.linspace(0.3, 1.2, 15) # Block Price
        z_matrix = []
        
        for y in y_vals:
            z_row = []
            for x in x_vals:
                # Quick calc for speed
                # Rev = (Input) + (Bloques) + (Recic) + (Amb)
                # Input = T_dia * 312 * x
                # Bloques = Blocks * y
                # Amb & Recic = Fixed in this sensitivity
                
                # Full sim instance for accuracy
                sim = SimuladorFerpaV3(self.t_dia, y, x, self.p_bono_co2, self.p_bono_agua, self.tasa_cambio)
                df, _, _ = sim.run_simulation(1)
                z_row.append(df.iloc[0]["Utilidad_Neta"])
            z_matrix.append(z_row)
            
        return x_vals, y_vals, z_matrix
