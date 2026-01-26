"""
Heat Exchanger Calculations Module
Core engineering calculations for heat exchanger design and analysis.
"""

import numpy as np
from src.fluid_properties import FluidProperties

class HeatExchanger:
    """
    Main class for heat exchanger calculations using LMTD and NTU methods.
    """
    
    def __init__(self, flow_arrangement='Counter Flow'):
        self.flow_arrangement = flow_arrangement
        self.results = {}
    
    def calculate_lmtd(self, T_hot_in, T_hot_out, T_cold_in, T_cold_out, 
                       m_hot, m_cold, fluid_hot, fluid_cold, U_value):
        # Get fluid properties
        hot_fluid = FluidProperties(fluid_hot)
        cold_fluid = FluidProperties(fluid_cold)
        
        # Average temperatures
        T_hot_avg = (T_hot_in + T_hot_out) / 2
        T_cold_avg = (T_cold_in + T_cold_out) / 2
        
        # Get specific heats
        Cp_hot = hot_fluid.get_specific_heat(T_hot_avg)
        Cp_cold = cold_fluid.get_specific_heat(T_cold_avg)
        
        # Heat capacity rates (W/K)
        C_hot = m_hot * Cp_hot
        C_cold = m_cold * Cp_cold
        C_min = min(C_hot, C_cold)
        C_max = max(C_hot, C_cold)
        C_ratio = C_min / C_max if C_max > 0 else 0
        
        # Calculate heat transfer rates
        Q_hot = m_hot * Cp_hot * (T_hot_in - T_hot_out) / 1000  # kW
        Q_cold = m_cold * Cp_cold * (T_cold_out - T_cold_in) / 1000  # kW
        Q_avg = (Q_hot + Q_cold) / 2
        
        # Energy balance check
        energy_balance_error = abs(Q_hot - Q_cold) / Q_hot * 100 if Q_hot > 0 else 0
        
        # Calculate LMTD
        if self.flow_arrangement == 'Counter Flow':
            delta_T1 = T_hot_in - T_cold_out
            delta_T2 = T_hot_out - T_cold_in
        else:  # Parallel Flow
            delta_T1 = T_hot_in - T_cold_in
            delta_T2 = T_hot_out - T_cold_out
        
        # SAFETY CHECK: Prevent log of zero or negative numbers
        if delta_T1 <= 1e-4 or delta_T2 <= 1e-4:
            raise ValueError("Temperature approach is too small (near zero) or negative. Check design temperatures.")
        
        # LMTD calculation with L'Hopital rule check
        if abs(delta_T1 - delta_T2) < 0.01:
            LMTD = delta_T1
        else:
            LMTD = (delta_T1 - delta_T2) / np.log(delta_T1 / delta_T2)
        
        # Required heat transfer area
        Q_watts = Q_avg * 1000
        
        if U_value <= 0 or LMTD <= 0:
             raise ValueError("Invalid U-value or LMTD resulted in calculation error.")
             
        Area = Q_watts / (U_value * LMTD)
        
        # Calculate NTU and effectiveness
        NTU = (U_value * Area) / C_min if C_min > 0 else 0
        
        # Maximum possible heat transfer
        Q_max = C_min * (T_hot_in - T_cold_in) / 1000  # kW
        
        # Effectiveness
        effectiveness = Q_avg / Q_max if Q_max > 0 else 0
        
        self.results = {
            'method': 'LMTD',
            'flow_type': self.flow_arrangement,
            'T_hot_in': T_hot_in, 'T_hot_out': T_hot_out,
            'T_cold_in': T_cold_in, 'T_cold_out': T_cold_out,
            'Q': Q_avg, 'Q_hot': Q_hot, 'Q_cold': Q_cold,
            'energy_balance_error': energy_balance_error,
            'LMTD': LMTD,
            'area': Area,
            'U_value': U_value,
            'NTU': NTU,
            'effectiveness': effectiveness,
            'C_hot': C_hot, 'C_cold': C_cold,
            'C_min': C_min, 'C_max': C_max, 'C_ratio': C_ratio,
            'delta_T1': delta_T1, 'delta_T2': delta_T2
        }
        
        return self.results
    
    def calculate_ntu(self, T_hot_in, T_cold_in, m_hot, m_cold, 
                     fluid_hot, fluid_cold, U_value, Area, T_hot_out=None):
        # Get fluid properties
        hot_fluid = FluidProperties(fluid_hot)
        cold_fluid = FluidProperties(fluid_cold)
        
        # Initial estimates
        T_hot_avg = T_hot_in - 20 if T_hot_out is None else (T_hot_in + T_hot_out) / 2
        T_cold_avg = T_cold_in + 20
        
        Cp_hot = hot_fluid.get_specific_heat(T_hot_avg)
        Cp_cold = cold_fluid.get_specific_heat(T_cold_avg)
        
        C_hot = m_hot * Cp_hot
        C_cold = m_cold * Cp_cold
        C_min = min(C_hot, C_cold)
        C_max = max(C_hot, C_cold)
        C_ratio = C_min / C_max if C_max > 0 else 0
        
        NTU = (U_value * Area) / C_min if C_min > 0 else 0
        
        # Effectiveness formulas
        if self.flow_arrangement == 'Counter Flow':
            if C_ratio < 1.0:
                # Prevent overflow in exp
                exp_val = np.exp(-NTU * (1 - C_ratio))
                effectiveness = (1 - exp_val) / (1 - C_ratio * exp_val)
            else:
                effectiveness = NTU / (1 + NTU)
        else:  # Parallel Flow
            exp_val = np.exp(-NTU * (1 + C_ratio))
            effectiveness = (1 - exp_val) / (1 + C_ratio)
        
        Q_max = C_min * (T_hot_in - T_cold_in) / 1000  # kW
        Q = effectiveness * Q_max
        
        # Calculate outlet temperatures
        Q_watts = Q * 1000
        T_hot_out_calc = T_hot_in - Q_watts / C_hot
        T_cold_out_calc = T_cold_in + Q_watts / C_cold
        
        # Recalculate with new averages
        T_hot_avg_new = (T_hot_in + T_hot_out_calc) / 2
        T_cold_avg_new = (T_cold_in + T_cold_out_calc) / 2
        
        Cp_hot = hot_fluid.get_specific_heat(T_hot_avg_new)
        Cp_cold = cold_fluid.get_specific_heat(T_cold_avg_new)
        
        C_hot = m_hot * Cp_hot
        C_cold = m_cold * Cp_cold
        
        Q_hot = m_hot * Cp_hot * (T_hot_in - T_hot_out_calc) / 1000
        Q_cold = m_cold * Cp_cold * (T_cold_out_calc - T_cold_in) / 1000
        
        energy_balance_error = abs(Q_hot - Q_cold) / Q_hot * 100 if Q_hot > 0 else 0
        
        # Calculate LMTD for reference
        if self.flow_arrangement == 'Counter Flow':
            delta_T1 = T_hot_in - T_cold_out_calc
            delta_T2 = T_hot_out_calc - T_cold_in
        else:
            delta_T1 = T_hot_in - T_cold_in
            delta_T2 = T_hot_out_calc - T_cold_out_calc
            
        if delta_T1 > 1e-4 and delta_T2 > 1e-4:
            if abs(delta_T1 - delta_T2) < 0.01:
                LMTD = delta_T1
            else:
                LMTD = (delta_T1 - delta_T2) / np.log(delta_T1 / delta_T2)
        else:
            LMTD = 0
            
        self.results = {
            'method': 'NTU',
            'flow_type': self.flow_arrangement,
            'T_hot_in': T_hot_in, 'T_hot_out': T_hot_out_calc,
            'T_cold_in': T_cold_in, 'T_cold_out': T_cold_out_calc,
            'Q': Q, 'Q_hot': Q_hot, 'Q_cold': Q_cold,
            'energy_balance_error': energy_balance_error,
            'LMTD': LMTD,
            'area': Area,
            'U_value': U_value,
            'NTU': NTU,
            'effectiveness': effectiveness,
            'C_hot': C_hot, 'C_cold': C_cold,
            'C_min': C_min, 'C_max': C_max, 'C_ratio': C_ratio,
            'Q_max': Q_max
        }
        return self.results
