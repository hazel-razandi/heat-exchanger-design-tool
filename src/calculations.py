"""
Thermal Calculation Engine (LMTD & NTU)
Author: KAKAROTONCLOUD
Version: 3.0.0 Enterprise
"""
import numpy as np
from src.fluid_properties import FluidProperties

class HeatExchanger:
    def __init__(self, flow_arrangement='Counter Flow'):
        self.flow_arrangement = flow_arrangement

    def calculate_lmtd(self, Thi, Tho, Tci, Tco, mh, mc, hot_fluid, cold_fluid, U):
        """
        Design Mode: Calculates Required Area based on Temps.
        """
        warnings = []
        
        # 1. Fluid Properties (Cached)
        hf = FluidProperties(hot_fluid)
        cf = FluidProperties(cold_fluid)
        
        # Avg Temps
        Th_avg = (Thi + Tho) / 2
        Tc_avg = (Tci + Tco) / 2
        
        Cph = hf.get_specific_heat(Th_avg)
        Cpc = cf.get_specific_heat(Tc_avg)
        
        # 2. Duty Calculation
        Q_hot = mh * Cph * (Thi - Tho) / 1000  # kW
        Q_cold = mc * Cpc * (Tco - Tci) / 1000 # kW
        Q_duty = (Q_hot + Q_cold) / 2
        
        # 3. LMTD & Correction Factor (Ft)
        if self.flow_arrangement == 'Counter Flow':
            dt1 = Thi - Tco
            dt2 = Tho - Tci
        else:
            dt1 = Thi - Tci
            dt2 = Tho - Tco
            
        # Physics Safety: Prevent log(0)
        if dt1 <= 0.1: dt1 = 0.1
        if dt2 <= 0.1: dt2 = 0.1
        
        if abs(dt1 - dt2) < 0.05:
            LMTD = dt1
        else:
            LMTD = (dt1 - dt2) / np.log(dt1 / dt2)

        # TEMA Alert: Temperature Cross check
        if self.flow_arrangement == 'Counter Flow' and Tho < Tco:
            warnings.append("Temperature Cross Detected (Th_out < Tc_out). Requires Multi-Shell TEMA F or G type.")

        # 4. Area Calculation
        if U <= 1: U = 1.0
        Area = (Q_duty * 1000) / (U * LMTD)

        # 5. Effectiveness & NTU (Back-calculation)
        Ch = mh * Cph
        Cc = mc * Cpc
        Cmin = min(Ch, Cc)
        NTU = (U * Area) / Cmin if Cmin > 0 else 0
        Q_max = Cmin * (Thi - Tci) / 1000
        Eff = Q_duty / Q_max if Q_max > 0 else 0

        return {
            'Q': Q_duty, 'area': Area, 'LMTD': LMTD, 'NTU': NTU, 
            'effectiveness': Eff, 
            'T_hot_in': Thi, 'T_hot_out': Tho, 'T_cold_in': Tci, 'T_cold_out': Tco,
            'm_hot': mh, 'm_cold': mc, 'hot_fluid': hot_fluid, 'cold_fluid': cold_fluid,
            'flow_type': self.flow_arrangement, 'U_value': U,
            'warnings': warnings
        }

    def calculate_ntu(self, Thi, Tci, mh, mc, hot_fluid, cold_fluid, U, Area):
        """
        Rating Mode: Calculates Outlet Temps based on Area.
        """
        warnings = []
        
        # 1. Properties
        hf = FluidProperties(hot_fluid)
        cf = FluidProperties(cold_fluid)
        
        Cph = hf.get_specific_heat(Thi)
        Cpc = cf.get_specific_heat(Tci)
        
        # 2. NTU Parameters
        Ch = mh * Cph
        Cc = mc * Cpc
        Cmin = min(Ch, Cc)
        Cmax = max(Ch, Cc)
        Cr = Cmin / Cmax if Cmax > 0 else 0
        
        NTU = (U * Area) / Cmin if Cmin > 0 else 0
        
        # 3. Effectiveness-NTU Relations
        if self.flow_arrangement == 'Counter Flow':
            if Cr < 1.0:
                arg = -NTU * (1 - Cr)
                Eff = (1 - np.exp(arg)) / (1 - Cr * np.exp(arg))
            else:
                Eff = NTU / (1 + NTU)
        else: # Parallel
            arg = -NTU * (1 + Cr)
            Eff = (1 - np.exp(arg)) / (1 + Cr)

        # 4. Outlets
        Q_max = Cmin * (Thi - Tci)
        Q_actual = Eff * Q_max # Watts
        
        Tho = Thi - (Q_actual / Ch)
        Tco = Tci + (Q_actual / Cc)
        
        # 5. LMTD for reporting
        # Recalculate LMTD based on new temps for report consistency
        dt1 = Thi - Tco
        dt2 = Tho - Tci
        if dt1 <= 0.1: dt1 = 0.1
        if dt2 <= 0.1: dt2 = 0.1
        LMTD = (dt1 - dt2) / np.log(dt1 / dt2) if abs(dt1-dt2) > 0.05 else dt1

        return {
            'Q': Q_actual/1000, 'area': Area, 'LMTD': LMTD, 'NTU': NTU, 
            'effectiveness': Eff, 
            'T_hot_in': Thi, 'T_hot_out': Tho, 'T_cold_in': Tci, 'T_cold_out': Tco,
            'm_hot': mh, 'm_cold': mc, 'hot_fluid': hot_fluid, 'cold_fluid': cold_fluid,
            'flow_type': self.flow_arrangement, 'U_value': U,
            'warnings': warnings
        }
