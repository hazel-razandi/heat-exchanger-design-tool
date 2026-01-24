"""
Fluid Properties Module
Provides thermophysical properties for various fluids using CoolProp library.
"""

import CoolProp.CoolProp as CP
import numpy as np


class FluidProperties:
    """
    Class to retrieve thermophysical properties of fluids.
    
    Supports: Water, Air, Ethylene Glycol solutions, Engine Oil, R-134a
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
        """
        Initialize fluid properties object.
        
        Args:
            fluid_name (str): Name of the fluid (e.g., 'Water', 'Air')
        """
        if fluid_name not in self.FLUID_MAP:
            raise ValueError(f"Fluid '{fluid_name}' not supported. Available: {list(self.FLUID_MAP.keys())}")
        
        self.fluid_name = fluid_name
        self.coolprop_name = self.FLUID_MAP[fluid_name]
    
    def get_density(self, temperature):
        """
        Get density at given temperature.
        
        Args:
            temperature (float): Temperature in Celsius
            
        Returns:
            float: Density in kg/m³
        """
        T_kelvin = temperature + 273.15
        try:
            if 'INCOMP' in self.coolprop_name:
                rho = CP.PropsSI('D', 'T', T_kelvin, 'P', 101325, self.coolprop_name)
            else:
                rho = CP.PropsSI('D', 'T', T_kelvin, 'P', 101325, self.coolprop_name)
            return rho
        except Exception as e:
            return self._get_fallback_density(temperature)
    
    def get_specific_heat(self, temperature):
        """
        Get specific heat capacity at given temperature.
        
        Args:
            temperature (float): Temperature in Celsius
            
        Returns:
            float: Specific heat in J/(kg·K)
        """
        T_kelvin = temperature + 273.15
        try:
            if 'INCOMP' in self.coolprop_name:
                cp = CP.PropsSI('C', 'T', T_kelvin, 'P', 101325, self.coolprop_name)
            else:
                cp = CP.PropsSI('C', 'T', T_kelvin, 'P', 101325, self.coolprop_name)
            return cp
        except Exception as e:
            return self._get_fallback_specific_heat(temperature)
    
    def get_thermal_conductivity(self, temperature):
        """
        Get thermal conductivity at given temperature.
        
        Args:
            temperature (float): Temperature in Celsius
            
        Returns:
            float: Thermal conductivity in W/(m·K)
        """
        T_kelvin = temperature + 273.15
        try:
            if 'INCOMP' in self.coolprop_name:
                k = CP.PropsSI('L', 'T', T_kelvin, 'P', 101325, self.coolprop_name)
            else:
                k = CP.PropsSI('L', 'T', T_kelvin, 'P', 101325, self.coolprop_name)
            return k
        except Exception as e:
            return self._get_fallback_thermal_conductivity(temperature)
    
    def get_dynamic_viscosity(self, temperature):
        """
        Get dynamic viscosity at given temperature.
        
        Args:
            temperature (float): Temperature in Celsius
            
        Returns:
            float: Dynamic viscosity in Pa·s
        """
        T_kelvin = temperature + 273.15
        try:
            if 'INCOMP' in self.coolprop_name:
                mu = CP.PropsSI('V', 'T', T_kelvin, 'P', 101325, self.coolprop_name)
            else:
                mu = CP.PropsSI('V', 'T', T_kelvin, 'P', 101325, self.coolprop_name)
            return mu
        except Exception as e:
            return self._get_fallback_viscosity(temperature)
    
    def get_prandtl(self, temperature):
        """
        Get Prandtl number at given temperature.
        
        Args:
            temperature (float): Temperature in Celsius
            
        Returns:
            float: Prandtl number (dimensionless)
        """
        cp = self.get_specific_heat(temperature)
        mu = self.get_dynamic_viscosity(temperature)
        k = self.get_thermal_conductivity(temperature)
        
        Pr = (cp * mu) / k
        return Pr
    
    def get_all_properties(self, temperature):
        """
        Get all properties at once.
        
        Args:
            temperature (float): Temperature in Celsius
            
        Returns:
            dict: Dictionary with all properties
        """
        return {
            'density': self.get_density(temperature),
            'specific_heat': self.get_specific_heat(temperature),
            'thermal_conductivity': self.get_thermal_conductivity(temperature),
            'dynamic_viscosity': self.get_dynamic_viscosity(temperature),
            'prandtl': self.get_prandtl(temperature),
            'temperature': temperature
        }
    
    # Fallback values (approximate, used if CoolProp fails)
    def _get_fallback_density(self, temp):
        fallback = {
            'Water': 1000,
            'Air': 1.2,
            'Ethylene Glycol (20%)': 1020,
            'Ethylene Glycol (40%)': 1050,
            'Ethylene Glycol (60%)': 1080,
            'Engine Oil': 880,
            'R-134a': 1200
        }
        return fallback.get(self.fluid_name, 1000)
    
    def _get_fallback_specific_heat(self, temp):
        fallback = {
            'Water': 4180,
            'Air': 1005,
            'Ethylene Glycol (20%)': 3900,
            'Ethylene Glycol (40%)': 3500,
            'Ethylene Glycol (60%)': 3100,
            'Engine Oil': 2000,
            'R-134a': 1400
        }
        return fallback.get(self.fluid_name, 4180)
    
    def _get_fallback_thermal_conductivity(self, temp):
        fallback = {
            'Water': 0.6,
            'Air': 0.026,
            'Ethylene Glycol (20%)': 0.5,
            'Ethylene Glycol (40%)': 0.45,
            'Ethylene Glycol (60%)': 0.4,
            'Engine Oil': 0.145,
            'R-134a': 0.08
        }
        return fallback.get(self.fluid_name, 0.6)
    
    def _get_fallback_viscosity(self, temp):
        fallback = {
            'Water': 0.001,
            'Air': 0.000018,
            'Ethylene Glycol (20%)': 0.0015,
            'Ethylene Glycol (40%)': 0.003,
            'Ethylene Glycol (60%)': 0.008,
            'Engine Oil': 0.05,
            'R-134a': 0.0002
        }
        return fallback.get(self.fluid_name, 0.001)


def get_available_fluids():
    """
    Returns list of available fluids.
    
    Returns:
        list: List of fluid names
    """
    return list(FluidProperties.FLUID_MAP.keys())


# Testing function
if __name__ == "__main__":
    print("Testing Fluid Properties Module\n")
    print("="*50)
    
    # Test water at 25°C
    water = FluidProperties('Water')
    props = water.get_all_properties(25)
    
    print(f"Water at 25°C:")
    print(f"  Density: {props['density']:.2f} kg/m³")
    print(f"  Specific Heat: {props['specific_heat']:.2f} J/(kg·K)")
    print(f"  Thermal Conductivity: {props['thermal_conductivity']:.4f} W/(m·K)")
    print(f"  Dynamic Viscosity: {props['dynamic_viscosity']:.6f} Pa·s")
    print(f"  Prandtl Number: {props['prandtl']:.2f}")
    print("\n" + "="*50)
    
    print("\nAvailable fluids:")
    for fluid in get_available_fluids():
        print(f"  - {fluid}")
