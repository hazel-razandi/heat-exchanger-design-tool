"""
Fluid Properties Module
Provides thermophysical properties for various fluids using CoolProp library.
Robust error handling added by KAKAROTONCLOUD.
"""

import CoolProp.CoolProp as CP
import numpy as np

class FluidProperties:
    """
    Class to retrieve thermophysical properties of fluids.
    Includes safeguards against calculation errors.
    """
    
    # Fluid mapping to CoolProp names
    FLUID_MAP = {
        'Water': 'Water',
        'Air': 'Air',
        'Ethylene Glycol (20%)': 'INCOMP::MEG-20%',
        'Ethylene Glycol (40%)': 'INCOMP::MEG-40%',
        'Ethylene Glycol (60%)': 'INCOMP::MEG-60%',
        'Engine Oil': 'INCOMP::T66',
        'R-134a': 'R134a'
    }
    
    def __init__(self, fluid_name):
        self.fluid_name = fluid_name
        # Default to Water if fluid not found (Safety feature)
        self.coolprop_name = self.FLUID_MAP.get(fluid_name, 'Water')
    
    def _safe_prop_lookup(self, prop_code, temperature_c):
        """
        Internal helper to safely lookup properties without crashing.
        """
        try:
            T_kelvin = temperature_c + 273.15
            # Safety clamp: Ensure temp is positive Kelvin
            if T_kelvin <= 0: T_kelvin = 298.15 
            
            # Standard pressure: 1 atm (101325 Pa)
            return CP.PropsSI(prop_code, 'T', T_kelvin, 'P', 101325, self.coolprop_name)
        except:
            # If CoolProp fails (e.g., out of range), return fallback
            return None

    def get_specific_heat(self, temperature):
        val = self._safe_prop_lookup('C', temperature)
        if val is None: return self._get_fallback_specific_heat()
        return val

    def get_density(self, temperature):
        val = self._safe_prop_lookup('D', temperature)
        if val is None: return self._get_fallback_density()
        return val

    def get_dynamic_viscosity(self, temperature):
        val = self._safe_prop_lookup('V', temperature)
        if val is None: return self._get_fallback_viscosity()
        return val

    def get_thermal_conductivity(self, temperature):
        val = self._safe_prop_lookup('L', temperature)
        if val is None: return self._get_fallback_conductivity()
        return val

    # --- FALLBACK VALUES (To prevent app crashes) ---
    def _get_fallback_specific_heat(self):
        # Approximate J/kg-K
        if 'Air' in self.fluid_name: return 1005
        if 'Oil' in self.fluid_name: return 2000
        if 'Glycol' in self.fluid_name: return 3500
        return 4180 # Water default

    def _get_fallback_density(self):
        # Approximate kg/m3
        if 'Air' in self.fluid_name: return 1.2
        if 'Oil' in self.fluid_name: return 880
        if 'Glycol' in self.fluid_name: return 1050
        return 997 # Water default
        
    def _get_fallback_viscosity(self):
        # Approximate Pa-s
        if 'Air' in self.fluid_name: return 0.000018
        if 'Oil' in self.fluid_name: return 0.05
        return 0.00089 # Water default

    def _get_fallback_conductivity(self):
        # Approximate W/m-K
        if 'Air' in self.fluid_name: return 0.026
        if 'Oil' in self.fluid_name: return 0.145
        return 0.6 # Water default

def get_available_fluids():
    return list(FluidProperties.FLUID_MAP.keys())
