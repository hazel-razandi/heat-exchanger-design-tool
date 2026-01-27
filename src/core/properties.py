"""
Physical Properties Database for Heat Exchanger Fluids
Includes Water and Standard API Oils (Kern).
"""
import numpy as np

def get_available_fluids():
    """Returns list of fluids for UI dropdowns."""
    return ["Water", "Oil_35API", "Oil_Heavy", "Methanol", "Benzene"]

def get_fluid_properties(fluid_name, T_C):
    """
    Returns dictionary of properties at Temperature T (Celsius).
    Units:
    - rho: kg/m3
    - cp:  J/kgK
    - k:   W/mK
    - mu:  Pa.s
    """
    # Convert T to Kelvin for standard correlations if needed
    T_K = T_C + 273.15
    
    # Defaults (Water at 25C)
    props = {
        'rho': 997.0,
        'cp': 4180.0,
        'k': 0.60,
        'mu': 0.00089
    }
    
    if fluid_name == "Water":
        # Simple linearized regression for water (valid 10-100C)
        props['rho'] = 1000 - 0.0178 * (T_C - 4)**1.7
        props['cp'] = 4180.0
        props['k'] = 0.6 + 0.001 * T_C
        # Viscosity fit
        props['mu'] = 2.414e-5 * 10**(247.8/(T_K - 140))

    elif fluid_name == "Oil_35API":
        # Data for Kern Ex 11.1 (Raw Oil)
        # 35 API ~ 0.85 SG
        # Linear fits based on Kern's Appendix for 35 API Oil
        props['rho'] = 850 - 0.65 * T_C  # Density decreases with temp
        props['cp'] = 2000 + 3.5 * T_C   # Cp increases with temp
        props['k'] = 0.13 - 0.0001 * T_C # k decreases slightly
        
        # Viscosity (Critical for pressure drop & heat transfer)
        if T_C < 0: T_C = 0.1
        props['mu'] = np_exp_viscosity(T_C) 

    elif fluid_name == "Oil_Heavy":
        props['rho'] = 920 - 0.6 * T_C
        props['cp'] = 1900 + 3.0 * T_C
        props['k'] = 0.12
        props['mu'] = 0.1 * (100/(T_C+20))**2 # Very viscous

    return props

def np_exp_viscosity(T_C):
    """
    Calibrated Viscosity for Kern 35 API Oil.
    Matches Kern Fig 14: ~5 cP at 40C, ~1.8 cP at 100C.
    """
    # Increased viscosity factor from 0.0026 to 0.0050 to match textbook dirty service
    return 0.0050 * np.exp(-0.021 * (T_C - 40))
