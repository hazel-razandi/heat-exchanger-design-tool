"""
Engineering Database Module (TEMA/API Standards)
Author: KAKAROTONCLOUD
Version: 3.0.0 Enterprise
"""

class EngineeringDB:
    """
    Central database for standardized engineering data.
    Source: TEMA 10th Edition, API 660, and Perry's Chemical Engineers' Handbook.
    """
    
    # --- 1. MATERIAL LIBRARY ---
    # Properties: 
    #   'k': Thermal Conductivity (W/m-K) at 25°C
    #   'cost_factor': Relative cost multiplier vs Carbon Steel (A516)
    #   'max_temp': Maximum service temperature (°C)
    MATERIALS = {
        'Carbon Steel (A516)':      {'k': 54.0, 'cost_factor': 1.0, 'max_temp': 500, 'roughness': 0.045},
        'Stainless Steel 304':      {'k': 16.2, 'cost_factor': 2.6, 'max_temp': 800, 'roughness': 0.015},
        'Stainless Steel 316L':     {'k': 16.3, 'cost_factor': 3.4, 'max_temp': 850, 'roughness': 0.015},
        'Duplex SS (2205)':         {'k': 19.0, 'cost_factor': 4.2, 'max_temp': 300, 'roughness': 0.015},
        'Titanium (Gr.2)':          {'k': 21.9, 'cost_factor': 7.5, 'max_temp': 600, 'roughness': 0.005},
        'Copper-Nickel (90/10)':    {'k': 50.0, 'cost_factor': 3.1, 'max_temp': 300, 'roughness': 0.002},
        'Hastelloy C-276':          {'k': 10.2, 'cost_factor': 14.5,'max_temp': 1000,'roughness': 0.020}
    }

    # --- 2. TEMA FOULING FACTORS (R_f) ---
    # Units: m²-K/W
    # These are safety margins added to the design to account for dirt accumulation.
    FOULING_SERVICES = {
        'Clean Water / Distilled':  0.0001,
        'River Water (Filtered)':   0.0004,
        'Sea Water (Below 50C)':    0.0005,
        'Sea Water (Above 50C)':    0.0009,
        'Engine Oil':               0.0010,
        'Fuel Oil (Heavy)':         0.0015,
        'Compressed Air':           0.0002,
        'Refrigerant Liquids':      0.0001,
        'Chemical Process Stream':  0.0005
    }

    # --- 3. CONFIGURATION TYPES ---
    # Defines the physical limits and base performance of HX types.
    HX_CONFIGS = {
        'Shell-and-Tube (BEM)': {
            'desc': 'Fixed Tubesheet (Standard)', 
            'base_u': 800, 
            'max_pressure': 150, # bar
            'area_density': 100  # m2/m3
        },
        'Shell-and-Tube (AES)': {
            'desc': 'Floating Head (High Temp Diff)', 
            'base_u': 750, 
            'max_pressure': 200, 
            'area_density': 90
        },
        'Plate & Frame (Gasketed)': {
            'desc': 'Compact, High Efficiency, Low Temp', 
            'base_u': 4000, 
            'max_pressure': 25, 
            'area_density': 300
        },
        'Double Pipe (Hairpin)': {
            'desc': 'Counter-flow, High Pressure, Low Area', 
            'base_u': 900, 
            'max_pressure': 300, 
            'area_density': 50
        }
    }

    @staticmethod
    def get_material_list():
        return list(EngineeringDB.MATERIALS.keys())

    @staticmethod
    def get_fouling_services():
        return list(EngineeringDB.FOULING_SERVICES.keys())

    @staticmethod
    def get_configs():
        return list(EngineeringDB.HX_CONFIGS.keys())

    @staticmethod
    def get_properties(material_name):
        return EngineeringDB.MATERIALS.get(material_name, EngineeringDB.MATERIALS['Carbon Steel (A516)'])
