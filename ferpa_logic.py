
import numpy as np
import pandas as pd
import numpy_financial as npf

class SimuladorFerpaV5:
    def __init__(self, t_dia, p_base_bloque, p_tipping, p_recic, p_bono_co2, p_bono_agua, capex, interest_rate, tax_rate, inflation, roi_target):
        self.t_dia = t_dia
        self.p_base_bloque = p_base_bloque
        self.p_tipping = p_tipping
        self.p_recic = p_recic
        self.p_bono_co2 = p_bono_co2
        self.p_bono_agua = p_bono_agua
        self.capex = capex
        self.tax_rate = tax_rate
        self.inflation = inflation
        self.roi_target = roi_target
        
        # Production Specs
        self.dias_anuales = 365
        self.pct_reciclable = 0.13
        self.pct_transformacion = 0.87
        self.factor_expansion = 1.4 # Masa expands due to additives/chemicals/water to achieve ~26M units
        self.unidades_por_ton_masa = 380 # Base calculation factor
        
        # Product Mix: [Share, PriceFactor, Name]
        self.mix = [
            {"name": "Bloque #5", "share": 0.70, "factor": 1.0},
            {"name": "Adoquín Pesado", "share": 0.20, "factor": 1.3},
            {"name": "Ladrillo Decorativo", "share": 0.10, "factor": 1.6}
        ]
        
    def run_simulation(self, years=10):
        rows = []
        
        # 1. PHYSICAL CALCULATIONS
        ton_input_anual = self.t_dia * self.dias_anuales
        ton_reciclable = ton_input_anual * self.pct_reciclable
        ton_masa_base = ton_input_anual * self.pct_transformacion
        ton_masa_expandida = ton_masa_base * self.factor_expansion
        
        total_units = ton_masa_expandida * self.unidades_por_ton_masa
        
        # Environment
        co2_total = ton_input_anual * 1.5 
        lix_total = ton_input_anual * 0.4
        
        # Investment Return Schedule
        # Rule: 50% of CAPEX returned in Y1 and Y2 respectively
        retorno_programado = {1: self.capex * 0.5, 2: self.capex * 0.5}
        
        saldo_inversion = self.capex
        
        for i in range(1, years + 1):
            inf_index = (1 + self.inflation) ** (i - 1)
            
            # --- REVENUES ---
            # 1. Blocks Mix
            # Weighted Price Calculation
            w_price = sum([m["share"] * m["factor"] for m in self.mix]) * self.p_base_bloque
            rev_bloques_mix = total_units * w_price * inf_index
            
            # Segmented Revenues for Sunburst
            rev_mix_detail = {
                m["name"]: total_units * m["share"] * (self.p_base_bloque * m["factor"] * inf_index)
                for m in self.mix
            }
            
            # 2. Recyclables
            rev_recic = ton_reciclable * self.p_recic * inf_index
            
            # 3. Tipping
            rev_tip = ton_input_anual * self.p_tipping * inf_index
            
            # 4. Bonds
            rev_green = (co2_total * self.p_bono_co2 * inf_index) + (lix_total * self.p_bono_agua * inf_index)
            
            total_revenue = rev_bloques_mix + rev_recic + rev_tip + rev_green
            
            # --- OPEX (RULE 45% of BLOCK SALES) ---
            opex_target = rev_bloques_mix * 0.45
            
            # Breakdown
            cost_energy = 500000 * inf_index # Fixed
            cost_payroll = 1500000 * inf_index # Approx fixed admin/ops structure
            cost_variable = opex_target - cost_energy - cost_payroll
            if cost_variable < 0: cost_variable = 0
            
            opex_real = cost_energy + cost_payroll + cost_variable
            
            # --- PROFITABILITY ---
            ebitda = total_revenue - opex_real
            deprec = self.capex / 10 # SL 10y
            ebit = ebitda - deprec
            taxes = max(0, ebit * self.tax_rate)
            net_income = ebit - taxes
            
            # --- CASH FLOW DISIMBURSEMENT (WATERFALL) ---
            # 1. Priority Return (Year 1 & 2)
            payment_return = retorno_programado.get(i, 0)
            
            # 2. Cash Available for Dividends
            # Simplified Operating Cash = Net Income + Deprec (add back non-cash)
            op_cash = net_income + deprec
            
            # Check availability
            remanente_post_retorno = op_cash - payment_return
            
            # 3. Dividend (30% of Remainder)
            dividend = 0
            if remanente_post_retorno > 0:
                dividend = remanente_post_retorno * 0.30
                
            # 4. Project Cash (Retained)
            project_cash = remanente_post_retorno - dividend
            
            # Investor Update
            saldo_inversion -= payment_return
            if saldo_inversion < 0: saldo_inversion = 0
            
            # Append Data
            rows.append({
                "Año": 2024 + i,
                "Ingresos": total_revenue,
                "Rev_Bloques": rev_bloques_mix,
                "Rev_Recic": rev_recic,
                "Rev_Tipping": rev_tip,
                "Rev_Bonos": rev_green,
                "OPEX_Total": opex_real,
                "Cost_Energy": cost_energy,
                "Cost_Payroll": cost_payroll,
                "Cost_Variable": cost_variable,
                "EBITDA": ebitda,
                "Deprec": deprec,
                "Impuestos": taxes,
                "Utilidad_Neta": net_income,
                "Flujo_Operativo": op_cash,
                "Pago_Retorno_Capital": payment_return,
                "Pago_Dividendos": dividend,
                "Caja_Ferpa": project_cash,
                "Saldo_Inversion": saldo_inversion,
                "Flujo_Investor_Total": payment_return + dividend,
                "Unidades_Total": total_units,
                **rev_mix_detail # Unpack mix revenues
            })
            
        df = pd.DataFrame(rows)
        
        # Financial Metrics
        flows = [-self.capex] + df["Flujo_Investor_Total"].tolist()
        irr = npf.irr(flows) or 0.0
        npv = npf.npv(0.12, flows)
        
        return {
            "df": df,
            "metrics": {
                "irr": irr,
                "npv": npv,
                "total_prod": total_units,
                "capex": self.capex
            }
        }
