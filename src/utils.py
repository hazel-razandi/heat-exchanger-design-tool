"""
Utility Helpers
Author: KAKAROTONCLOUD
Version: 3.0.0 Enterprise
"""
import numpy as np

def generate_temperature_profile(Thi, Tho, Tci, Tco, flow_type):
    """
    Generates datapoints for T-Q Diagram.
    """
    x = np.linspace(0, 1, 50)
    
    # Hot fluid always cools
    Th = Thi - (Thi - Tho) * x
    
    # Cold fluid heats up
    if flow_type == 'Counter Flow':
        # Cold inlet is at x=1 (Right side)
        Tc = Tco - (Tco - Tci) * x
    else:
        # Cold inlet is at x=0 (Left side)
        Tc = Tci + (Tco - Tci) * x
        
    return x, Th, Tc

def validate_temperatures(Thi, Tho, Tci, Tco, flow_type):
    """
    Validates thermodynamic feasibility.
    """
    # 1. Direction Check
    if Thi is not None and Tho is not None:
        if Thi <= Tho: 
            return False, "Hot Fluid Error: Inlet Temp must be > Outlet Temp."
            
    if Tci is not None and Tco is not None:
        if Tco <= Tci: 
            return False, "Cold Fluid Error: Outlet Temp must be > Inlet Temp."

    # 2. Second Law Check (Design Mode)
    if Tho is not None and Tco is not None:
        if flow_type == 'Parallel Flow':
            if Tho < Tco:
                return False, "Physics Violation: Hot outlet cannot be colder than Cold outlet in Parallel Flow."
        
        # Heat Balance Check
        # Cannot cool hot fluid below cold inlet (Infinite Area)
        if Tho < Tci:
            return False, "Physics Violation: Hot outlet cannot be colder than Cold inlet."

    return True, "Valid"
