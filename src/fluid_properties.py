"""
Fluid Properties Engine
Author: KAKAROTONCLOUD
Version: 3.0.0 Enterprise
"""

import CoolProp.CoolProp as CP
from functools import lru_cache

class FluidProperties:
    """
    High-performance fluid property engine with caching and failover.
    """
    
    # Mapping friendly names to CoolProp internal codes
    FLUID_MAP = {
        'Water': 'Water',
        'Air': 'Air',
        'Sea Water': 'INCOMP::MAS',
        'Ethylene Glycol (30%)': 'INCOMP::MEG-30%',
        'Ethylene Glycol (50%)': 'INCOMP::MEG-50%',
        'Propylene Glycol (30%)': 'INCOMP::MPG-30%',
        'Engine Oil': 'INCOMP::T66',
        'Lube Oil': 'INCOMP::DowJ',
        'Ammonia': 'Ammonia',
        'R-134a': 'R134a',
        'R-410A': 'R410A'
    }
    
    def __init__(self, fluid_name):
        self.friendly_name = fluid_name
        self.cp_code = self.FLUID_MAP.get(fluid_name, 'Water')

    @lru_cache(maxsize=128)
    def _get_prop_secure(self, prop_code, temp_c, pressure_pa=101325):
        """
        Internal protected method to fetch properties with caching.
        """
        try:
            # Convert C to K (Absolute Temp)
            tk = temp_c + 273.15
            
            # Physics Safety: Prevent absolute zero or negative Kelvin
            if tk <= 0.1: tk = 273.15
            
            # CoolProp Call
            return CP.PropsSI(prop_code, 'T', tk, 'P', pressure_pa, self.cp_code)
        except Exception:
            return None

    def get_density(self, temp_c):
        """Returns Density (kg/m3)"""
        val = self._get_prop_secure('D', temp_c)
        return val if val else self._fallback('D')

    def get_specific_heat(self, temp_c):
        """Returns Specific Heat Cp (J/kg-K)"""
        val = self._get_prop_secure('C', temp_c)
        return val if val else self._fallback('C')

    def get_viscosity(self, temp_c):
        """Returns Dynamic Viscosity (Pa-s)"""
        val = self._get_prop_secure('V', temp_c)
        return val if val else self._fallback('V')

    def get_conductivity(self, temp_c):
        """Returns Thermal Conductivity (W/m-K)"""
        val = self._get_prop_secure('L', temp_c)
        return val if val else self._fallback('L')

    def get_prandtl(self, temp_c):
        """Returns Prandtl Number (Dimensionless)"""
        cp = self.get_specific_heat(temp_c)
        mu = self.get_viscosity(temp_c)
        k = self.get_conductivity(temp_c)
        return (cp * mu) / k if k > 0 else 1.0

    def _fallback(self, prop_code):
        """
        Safety net: Returns approximate values if CoolProp fails.
        Prevents 'Red Screen of Death' in the app.
        """
        is_gas = 'Air' in self.friendly_name
        is_oil = 'Oil' in self.friendly_name
        
        defaults = {
            'D': 1.2 if is_gas else (880 if is_oil else 995),     # Density
            'C': 1005 if is_gas else (2000 if is_oil else 4180),  # Cp
            'V': 1.8e-5 if is_gas else (0.05 if is_oil else 0.001), # Viscosity
            'L': 0.026 if is_gas else (0.15 if is_oil else 0.6)   # Conductivity
        }
        return defaults.get(prop_code, 1.0)

def get_available_fluids():
    return list(FluidProperties.FLUID_MAP.keys())
