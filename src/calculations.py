"""
Heat Exchanger Calculations Module
Updated by KAKAROTONCLOUD for robustness.
"""

import numpy as np
from src.fluid_properties import FluidProperties

class HeatExchanger:
    def __init__(self, flow_arrangement='Counter Flow'):
        self.flow_arrangement = flow_arrangement

    def calculate_lmtd(self, T_hot_in, T_hot_out, T_cold_in, T_cold_out, 
                       m_hot, m_cold, fluid_hot, fluid_cold, U_value):
        
        # 1. Properties
        hot_fluid = FluidProperties(fluid_hot)
        cold_fluid = FluidProperties(fluid_cold)
        
        T_hot_avg = (T_hot_in + T_hot_out) / 2
        T_cold_avg = (T_cold_in + T_cold_out) / 2
        
        Cp_hot = hot_fluid.get_specific_heat(T_hot_avg)
        Cp_cold = cold_fluid.get_specific_heat(T_cold_avg)
        
        # 2. Heat Loads
        Q_hot = m_hot * Cp_hot * (T_hot_in - T_hot_out) / 1000  # kW
        Q_cold = m_cold * Cp_cold * (T_cold_out - T_cold_in) / 1000  # kW
        Q_avg = (Q_hot + Q_cold) / 2
        
        # 3. LMTD with safeguards
        if self.flow_arrangement == 'Counter Flow':
            dT1 = T_hot_in - T_cold_out
            dT2 = T_hot_out - T_cold_in
        else:
            dT1 = T_hot_in - T_cold_in
            dT2 = T_hot_out - T_cold_out

        # Handle pinch points or zero difference
        if dT1 <= 0.1: dT1 = 0.1
        if dT2 <= 0.1: dT2 = 0.1
        
        if abs(dT1 - dT2) < 0.05:
            LMTD = dT1
        else:
            LMTD = (dT1 - dT2) / np.log(dT1 / dT2)

        # 4. Area
        if U_value <= 1: U_value = 1 # Prevent div by zero
        Area = (Q_avg * 1000) / (U_value * LMTD)

        # 5. NTU & Effectiveness
        C_hot = m_hot * Cp_hot
        C_cold = m_cold * Cp_cold
        C_min = min(C_hot, C_cold)
        NTU = (U_value * Area) / C_min if C_min > 0 else 0
        Q_max = C_min * (T_hot_in - T_cold_in) / 1000
        Effectiveness = Q_avg / Q_max if Q_max > 0 else 0

        return {
            'Q': Q_avg, 'area': Area, 'LMTD': LMTD, 'NTU': NTU, 
            'effectiveness': Effectiveness, 'energy_balance_error': abs(Q_hot-Q_cold)/Q_hot*100 if Q_hot>0 else 0,
            'T_hot_in': T_hot_in, 'T_hot_out': T_hot_out,
            'T_cold_in': T_cold_in, 'T_cold_out': T_cold_out,
            'flow_type': self.flow_arrangement, 'method': 'LMTD',
            'hx_type': 'Generic', 'hot_fluid': fluid_hot, 'cold_fluid': fluid_cold,
            'm_hot': m_hot, 'm_cold': m_cold, 'U_value': U_value
        }

    def calculate_ntu(self, T_hot_in, T_cold_in, m_hot, m_cold, 
                     fluid_hot, fluid_cold, U_value, Area):
        # 1. Properties
        hot_fluid = FluidProperties(fluid_hot)
        cold_fluid = FluidProperties(fluid_cold)
        
        Cp_hot = hot_fluid.get_specific_heat(T_hot_in) # Approx using inlet
        Cp_cold = cold_fluid.get_specific_heat(T_cold_in)

        # 2. Capacity Rates
        C_hot = m_hot * Cp_hot
        C_cold = m_cold * Cp_cold
        C_min = min(C_hot, C_cold)
        C_max = max(C_hot, C_cold)
        C_r = C_min / C_max if C_max > 0 else 0

        # 3. NTU
        NTU = (U_value * Area) / C_min if C_min > 0 else 0

        # 4. Effectiveness
        eff = 0
        if self.flow_arrangement == 'Counter Flow':
            if C_r < 1:
                arg = -NTU * (1 - C_r)
                eff = (1 - np.exp(arg)) / (1 - C_r * np.exp(arg))
            else:
                eff = NTU / (1 + NTU)
        else: # Parallel
            arg = -NTU * (1 + C_r)
            eff = (1 - np.exp(arg)) / (1 + C_r)

        # 5. Heat & Outlets
        Q_max = C_min * (T_hot_in - T_cold_in)
        Q_watts = eff * Q_max
        
        T_hot_out = T_hot_in - (Q_watts / C_hot)
        T_cold_out = T_cold_in + (Q_watts / C_cold)

        return {
            'Q': Q_watts/1000, 'area': Area, 'LMTD': 0, 'NTU': NTU, 
            'effectiveness': eff, 'energy_balance_error': 0,
            'T_hot_in': T_hot_in, 'T_hot_out': T_hot_out,
            'T_cold_in': T_cold_in, 'T_cold_out': T_cold_out,
            'flow_type': self.flow_arrangement, 'method': 'NTU',
            'hx_type': 'Generic', 'hot_fluid': fluid_hot, 'cold_fluid': fluid_cold,
            'm_hot': m_hot, 'm_cold': m_cold, 'U_value': U_value
        }
