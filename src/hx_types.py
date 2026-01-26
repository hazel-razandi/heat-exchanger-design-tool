"""
Heat Exchanger Types Data
Author: KAKAROTONCLOUD
"""

class HeatExchangerType:
    TYPES = {
        'Shell-and-Tube': {'min_u': 800, 'max_u': 1500, 'desc': 'Standard industrial choice'},
        'Plate': {'min_u': 3000, 'max_u': 7000, 'desc': 'Compact, high efficiency'},
        'Finned Tube': {'min_u': 25, 'max_u': 100, 'desc': 'For air/gas cooling'},
        'Double Pipe': {'min_u': 500, 'max_u': 1200, 'desc': 'Simple, low surface area'},
        'Spiral': {'min_u': 1000, 'max_u': 3000, 'desc': 'For viscous fluids'}
    }

    @staticmethod
    def list_all_types():
        return list(HeatExchangerType.TYPES.keys())

    @staticmethod
    def get_typical_U_value(hx_type, fluid_combo=None):
        data = HeatExchangerType.TYPES.get(hx_type, {'min_u': 100, 'max_u': 500})
        return data['min_u'], data['max_u']

    @staticmethod
    def get_fluid_combinations(hx_type):
        # Simplified for robustness
        return ["Water-Water", "Water-Oil", "Water-Air", "Steam-Water"]
