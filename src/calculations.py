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
        """
        Initialize heat exchanger.
        
        Args:
            flow_arrangement (str): 'Counter Flow' or 'Parallel Flow'
        """
        self.flow_arrangement = flow_arrangement
        self.results = {}
    
    def calculate_lmtd(self, T_hot_in, T_hot_out, T_cold_in, T_cold_out, 
                       m_hot, m_cold, fluid_hot, fluid_cold, U_value):
        """
        Calculate heat exchanger using LMTD method (Design mode).
        
        Args:
            T_hot_in (float): Hot fluid inlet temperature (°C)
            T_hot_out (float): Hot fluid outlet temperature (°C)
            T_cold_in (float): Cold fluid inlet temperature (°C)
            T_cold_out (float): Cold fluid outlet temperature (°C)
            m_hot (float): Hot fluid mass flow rate (kg/s)
            m_cold (float): Cold fluid mass flow rate (kg/s)
            fluid_hot (str): Hot fluid name
            fluid_cold (str): Cold fluid name
            U_value (float): Overall heat transfer coefficient (W/m²·K)
            
        Returns:
            dict: Results including Q, Area, LMTD, effectiveness, NTU
        """
        # Get fluid properties
        hot_fluid = FluidProperties(fluid_hot)
        cold_fluid = FluidProperties(fluid_cold)
        
        # Average temperatures for property evaluation
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
        C_ratio = C_min / C_max
        
        # Calculate heat transfer rates
        Q_hot = m_hot * Cp_hot * (T_hot_in - T_hot_out) / 1000  # kW
        Q_cold = m_cold * Cp_cold * (T_cold_out - T_cold_in) / 1000  # kW
        Q_avg = (Q_hot + Q_cold) / 2
        
        # Energy balance check
        energy_balance_error = abs(Q_hot - Q_cold) / Q_hot * 100
        
        # Calculate LMTD
        if self.flow_arrangement == 'Counter Flow':
            delta_T1 = T_hot_in - T_cold_out
            delta_T2 = T_hot_out - T_cold_in
        else:  # Parallel Flow
            delta_T1 = T_hot_in - T_cold_in
            delta_T2 = T_hot_out - T_cold_out
        
        # Check for zero or negative temperature differences
        if delta_T1 <= 0 or delta_T2 <= 0:
            raise ValueError("Invalid temperature profile - check inputs")
        
        # LMTD calculation
        if abs(delta_T1 - delta_T2) < 0.01:
            LMTD = delta_T1
        else:
            LMTD = (delta_T1 - delta_T2) / np.log(delta_T1 / delta_T2)
        
        # Required heat transfer area
        Q_watts = Q_avg * 1000  # Convert kW to W
        Area = Q_watts / (U_value * LMTD)
        
        # Calculate NTU and effectiveness
        NTU = (U_value * Area) / C_min
        
        # Maximum possible heat transfer
        Q_max = C_min * (T_hot_in - T_cold_in) / 1000  # kW
        
        # Effectiveness
        effectiveness = Q_avg / Q_max if Q_max > 0 else 0
        
        # Store results
        self.results = {
            'method': 'LMTD',
            'flow_type': self.flow_arrangement,
            'T_hot_in': T_hot_in,
            'T_hot_out': T_hot_out,
            'T_cold_in': T_cold_in,
            'T_cold_out': T_cold_out,
            'Q': Q_avg,
            'Q_hot': Q_hot,
            'Q_cold': Q_cold,
            'energy_balance_error': energy_balance_error,
            'LMTD': LMTD,
            'area': Area,
            'U_value': U_value,
            'NTU': NTU,
            'effectiveness': effectiveness,
            'C_hot': C_hot,
            'C_cold': C_cold,
            'C_min': C_min,
            'C_max': C_max,
            'C_ratio': C_ratio,
            'delta_T1': delta_T1,
            'delta_T2': delta_T2
        }
        
        return self.results
    
    def calculate_ntu(self, T_hot_in, T_cold_in, m_hot, m_cold, 
                     fluid_hot, fluid_cold, U_value, Area, T_hot_out=None):
        """
        Calculate heat exchanger using NTU-Effectiveness method (Rating mode).
        
        Args:
            T_hot_in (float): Hot fluid inlet temperature (°C)
            T_cold_in (float): Cold fluid inlet temperature (°C)
            m_hot (float): Hot fluid mass flow rate (kg/s)
            m_cold (float): Cold fluid mass flow rate (kg/s)
            fluid_hot (str): Hot fluid name
            fluid_cold (str): Cold fluid name
            U_value (float): Overall heat transfer coefficient (W/m²·K)
            Area (float): Heat exchanger area (m²)
            T_hot_out (float, optional): Hot outlet temp for better property estimation
            
        Returns:
            dict: Results including Q, outlet temperatures, effectiveness, NTU
        """
        # Get fluid properties
        hot_fluid = FluidProperties(fluid_hot)
        cold_fluid = FluidProperties(fluid_cold)
        
        # Initial temperature estimates for properties
        T_hot_avg = T_hot_in - 20 if T_hot_out is None else (T_hot_in + T_hot_out) / 2
        T_cold_avg = T_cold_in + 20
        
        # Get specific heats
        Cp_hot = hot_fluid.get_specific_heat(T_hot_avg)
        Cp_cold = cold_fluid.get_specific_heat(T_cold_avg)
        
        # Heat capacity rates
        C_hot = m_hot * Cp_hot
        C_cold = m_cold * Cp_cold
        C_min = min(C_hot, C_cold)
        C_max = max(C_hot, C_cold)
        C_ratio = C_min / C_max
        
        # Calculate NTU
        NTU = (U_value * Area) / C_min
        
        # Calculate effectiveness based on flow arrangement
        if self.flow_arrangement == 'Counter Flow':
            if C_ratio < 1.0:
                effectiveness = (1 - np.exp(-NTU * (1 - C_ratio))) / \
                               (1 - C_ratio * np.exp(-NTU * (1 - C_ratio)))
            else:  # C_ratio = 1
                effectiveness = NTU / (1 + NTU)
        else:  # Parallel Flow
            effectiveness = (1 - np.exp(-NTU * (1 + C_ratio))) / (1 + C_ratio)
        
        # Maximum possible heat transfer
        Q_max = C_min * (T_hot_in - T_cold_in) / 1000  # kW
        
        # Actual heat transfer
        Q = effectiveness * Q_max
        
        # Calculate outlet temperatures
        Q_watts = Q * 1000
        T_hot_out_calc = T_hot_in - Q_watts / C_hot
        T_cold_out_calc = T_cold_in + Q_watts / C_cold
        
        # Recalculate with better property estimates
        T_hot_avg_new = (T_hot_in + T_hot_out_calc) / 2
        T_cold_avg_new = (T_cold_in + T_cold_out_calc) / 2
        
        Cp_hot = hot_fluid.get_specific_heat(T_hot_avg_new)
        Cp_cold = cold_fluid.get_specific_heat(T_cold_avg_new)
        
        C_hot = m_hot * Cp_hot
        C_cold = m_cold * Cp_cold
        
        Q_hot = m_hot * Cp_hot * (T_hot_in - T_hot_out_calc) / 1000
        Q_cold = m_cold * Cp_cold * (T_cold_out_calc - T_cold_in) / 1000
        
        # Energy balance check
        energy_balance_error = abs(Q_hot - Q_cold) / Q_hot * 100 if Q_hot > 0 else 0
        
        # Calculate LMTD for reference
        if self.flow_arrangement == 'Counter Flow':
            delta_T1 = T_hot_in - T_cold_out_calc
            delta_T2 = T_hot_out_calc - T_cold_in
        else:
            delta_T1 = T_hot_in - T_cold_in
            delta_T2 = T_hot_out_calc - T_cold_out_calc
        
        if delta_T1 > 0 and delta_T2 > 0:
            if abs(delta_T1 - delta_T2) < 0.01:
                LMTD = delta_T1
            else:
                LMTD = (delta_T1 - delta_T2) / np.log(delta_T1 / delta_T2)
        else:
            LMTD = 0
        
        # Store results
        self.results = {
            'method': 'NTU',
            'flow_type': self.flow_arrangement,
            'T_hot_in': T_hot_in,
            'T_hot_out': T_hot_out_calc,
            'T_cold_in': T_cold_in,
            'T_cold_out': T_cold_out_calc,
            'Q': Q,
            'Q_hot': Q_hot,
            'Q_cold': Q_cold,
            'energy_balance_error': energy_balance_error,
            'LMTD': LMTD,
            'area': Area,
            'U_value': U_value,
            'NTU': NTU,
            'effectiveness': effectiveness,
            'C_hot': C_hot,
            'C_cold': C_cold,
            'C_min': C_min,
            'C_max': C_max,
            'C_ratio': C_ratio,
            'Q_max': Q_max
        }
        
        return self.results
    
    def get_results(self):
        """Return calculation results."""
        return self.results


def calculate_effectiveness_from_ntu(NTU, C_ratio, flow_type='Counter Flow'):
    """
    Calculate effectiveness from NTU.
    
    Args:
        NTU (float): Number of Transfer Units
        C_ratio (float): Heat capacity ratio (C_min/C_max)
        flow_type (str): Flow arrangement
        
    Returns:
        float: Effectiveness
    """
    if flow_type == 'Counter Flow':
        if C_ratio < 1.0:
            eff = (1 - np.exp(-NTU * (1 - C_ratio))) / \
                  (1 - C_ratio * np.exp(-NTU * (1 - C_ratio)))
        else:
            eff = NTU / (1 + NTU)
    else:  # Parallel Flow
        eff = (1 - np.exp(-NTU * (1 + C_ratio))) / (1 + C_ratio)
    
    return eff


def calculate_ntu_from_effectiveness(effectiveness, C_ratio, flow_type='Counter Flow'):
    """
    Calculate NTU from effectiveness (inverse relationship).
    
    Args:
        effectiveness (float): Effectiveness (0-1)
        C_ratio (float): Heat capacity ratio
        flow_type (str): Flow arrangement
        
    Returns:
        float: NTU
    """
    if flow_type == 'Counter Flow':
        if C_ratio < 1.0:
            NTU = np.log((1 - effectiveness * C_ratio) / (1 - effectiveness)) / (C_ratio - 1)
        else:
            NTU = effectiveness / (1 - effectiveness)
    else:  # Parallel Flow
        NTU = -np.log(1 - effectiveness * (1 + C_ratio)) / (1 + C_ratio)
    
    return NTU


# Testing
if __name__ == "__main__":
    print("Testing Heat Exchanger Calculations\n")
    print("="*70)
    
    # Test LMTD method
    print("\nTest 1: LMTD Method (Counter Flow)")
    print("-"*70)
    
    hx = HeatExchanger(flow_arrangement='Counter Flow')
    results = hx.calculate_lmtd(
        T_hot_in=90,
        T_hot_out=50,
        T_cold_in=25,
        T_cold_out=45,
        m_hot=2.0,
        m_cold=3.0,
        fluid_hot='Water',
        fluid_cold='Water',
        U_value=500
    )
    
    print(f"Heat Transfer Rate: {results['Q']:.2f} kW")
    print(f"Required Area: {results['area']:.2f} m²")
    print(f"LMTD: {results['LMTD']:.2f} °C")
    print(f"Effectiveness: {results['effectiveness']*100:.1f}%")
    print(f"NTU: {results['NTU']:.2f}")
    print(f"Energy Balance Error: {results['energy_balance_error']:.2f}%")
    
    # Test NTU method
    print("\n" + "="*70)
    print("\nTest 2: NTU Method (Counter Flow)")
    print("-"*70)
    
    hx2 = HeatExchanger(flow_arrangement='Counter Flow')
    results2 = hx2.calculate_ntu(
        T_hot_in=90,
        T_cold_in=25,
        m_hot=2.0,
        m_cold=3.0,
        fluid_hot='Water',
        fluid_cold='Water',
        U_value=500,
        Area=12.4
    )
    
    print(f"Heat Transfer Rate: {results2['Q']:.2f} kW")
    print(f"Hot Outlet Temperature: {results2['T_hot_out']:.2f} °C")
    print(f"Cold Outlet Temperature: {results2['T_cold_out']:.2f} °C")
    print(f"Effectiveness: {results2['effectiveness']*100:.1f}%")
    print(f"NTU: {results2['NTU']:.2f}")
    print(f"Energy Balance Error: {results2['energy_balance_error']:.2f}%")
