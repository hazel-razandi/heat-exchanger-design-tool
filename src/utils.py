"""
Utilities & Visualization
Author: KAKAROTONCLOUD
"""
import numpy as np

def generate_temperature_profile(T_hot_in, T_hot_out, T_cold_in, T_cold_out, flow_type='Counter Flow'):
    """Generates X, Y coordinates for temperature charts"""
    x = np.linspace(0, 1, 100)
    
    # Linear approximation for visualization
    T_hot = T_hot_in - (T_hot_in - T_hot_out) * x
    
    if flow_type == 'Counter Flow':
        T_cold = T_cold_out - (T_cold_out - T_cold_in) * x
    else:
        T_cold = T_cold_in + (T_cold_out - T_cold_in) * x
        
    return x, T_hot, T_cold

def validate_temperatures(Thi, Tho, Tci, Tco, flow_type):
    """Basic physics check"""
    if Thi <= Tho: return False, "Hot fluid must cool down (Inlet > Outlet)"
    if Tco <= Tci: return False, "Cold fluid must heat up (Outlet > Inlet)"
    
    if flow_type == 'Counter Flow':
        if Tho < Tci: return False, "Temperature cross error: Hot Out < Cold In"
    else: # Parallel
        if Tho < Tco: return False, "Parallel Flow Violation: Hot Out < Cold Out"
        
    return True, "Valid"
