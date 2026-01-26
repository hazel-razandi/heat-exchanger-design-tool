import CoolProp.CoolProp as CP
from functools import lru_cache

class FluidProperties:
    FLUID_MAP = {'Water': 'Water', 'Air': 'Air', 'Engine Oil': 'INCOMP::T66', 'Ethanol': 'Ethanol'}
    
    def __init__(self, name):
        self.code = self.FLUID_MAP.get(name, 'Water')

    @lru_cache(maxsize=128)
    def get_props(self, temp_c, pressure_pa=101325):
        """Returns (rho, cp, mu, k, pr) at given Temp (C)"""
        t_k = temp_c + 273.15
        try:
            rho = CP.PropsSI('D', 'T', t_k, 'P', pressure_pa, self.code)
            cp = CP.PropsSI('C', 'T', t_k, 'P', pressure_pa, self.code)
            mu = CP.PropsSI('V', 'T', t_k, 'P', pressure_pa, self.code)
            k = CP.PropsSI('L', 'T', t_k, 'P', pressure_pa, self.code)
            pr = CP.PropsSI('Prandtl', 'T', t_k, 'P', pressure_pa, self.code)
            return rho, cp, mu, k, pr
        except:
            return 1000.0, 4180.0, 0.001, 0.6, 7.0 # Fallback (Water)

# --- THIS FUNCTION MUST BE HERE ---
def get_available_fluids():
    return list(FluidProperties.FLUID_MAP.keys())
