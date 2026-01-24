"""
Heat Exchanger Types Module
Defines different heat exchanger configurations and their typical properties.
"""


class HeatExchangerType:
    """
    Class representing different types of heat exchangers with their characteristics.
    """
    
    TYPES = {
        'Shell-and-Tube': {
            'description': 'Most common industrial heat exchanger. Robust and versatile.',
            'typical_U_range': {
                'Water-Water': (800, 1500),
                'Water-Oil': (100, 400),
                'Water-Air': (10, 50),
                'Steam-Water': (1500, 4000),
                'Gas-Gas': (10, 40)
            },
            'advantages': [
                'Handles high pressures and temperatures',
                'Easy to clean and maintain',
                'Wide range of sizes available',
                'Well-established design methods'
            ],
            'disadvantages': [
                'Larger footprint',
                'Higher weight',
                'More expensive than plate types'
            ],
            'applications': [
                'Refineries',
                'Chemical plants',
                'Power generation',
                'Oil and gas processing'
            ]
        },
        
        'Plate': {
            'description': 'Compact design with high efficiency. Thin metal plates create flow channels.',
            'typical_U_range': {
                'Water-Water': (3000, 7000),
                'Water-Oil': (300, 900),
                'Water-Glycol': (1500, 4000),
                'Refrigerant-Water': (800, 1500)
            },
            'advantages': [
                'Very compact - high surface area to volume ratio',
                'High thermal efficiency',
                'Easy to expand (add plates)',
                'Lower fouling tendency'
            ],
            'disadvantages': [
                'Limited pressure rating',
                'Not suitable for high temperatures',
                'Gasket maintenance required'
            ],
            'applications': [
                'HVAC systems',
                'Food processing',
                'Pharmaceutical',
                'District heating'
            ]
        },
        
        'Finned Tube': {
            'description': 'Extended surface on one side. Used when one fluid has poor heat transfer.',
            'typical_U_range': {
                'Air-Water': (25, 100),
                'Air-Steam': (30, 150),
                'Air-Refrigerant': (40, 200),
                'Gas-Water': (20, 80)
            },
            'advantages': [
                'Compensates for poor gas-side heat transfer',
                'Compact for gas applications',
                'Lower air-side pressure drop'
            ],
            'disadvantages': [
                'Susceptible to fouling on fin side',
                'Difficult to clean',
                'Higher manufacturing cost'
            ],
            'applications': [
                'Air conditioning coils',
                'Radiators',
                'Air-cooled condensers',
                'Heat recovery from flue gas'
            ]
        },
        
        'Double Pipe': {
            'description': 'Simple design - one pipe inside another. Easy to manufacture.',
            'typical_U_range': {
                'Water-Water': (500, 1200),
                'Water-Oil': (150, 350),
                'Steam-Water': (1200, 2500)
            },
            'advantages': [
                'Simple design and construction',
                'True counter-flow possible',
                'Suitable for small capacities',
                'Low cost'
            ],
            'disadvantages': [
                'Limited to small heat duties',
                'Large space requirement for high capacity',
                'Limited surface area per unit'
            ],
            'applications': [
                'Small industrial processes',
                'Laboratory equipment',
                'Heating/cooling small flows'
            ]
        },
        
        'Spiral': {
            'description': 'Two concentric spiral channels. Good for viscous fluids and slurries.',
            'typical_U_range': {
                'Water-Water': (1000, 3000),
                'Slurry-Water': (200, 600),
                'Viscous-Water': (150, 500)
            },
            'advantages': [
                'Self-cleaning due to flow pattern',
                'Handles viscous and fouling fluids',
                'Compact design',
                'True counter-flow'
            ],
            'disadvantages': [
                'Difficult to repair',
                'Limited to moderate pressures',
                'Higher cost than shell-and-tube'
            ],
            'applications': [
                'Pulp and paper',
                'Wastewater treatment',
                'Food processing with particles',
                'Chemical processing'
            ]
        }
    }
    
    @staticmethod
    def get_type_info(hx_type):
        """
        Get information about a specific heat exchanger type.
        
        Args:
            hx_type (str): Type of heat exchanger
            
        Returns:
            dict: Information about the heat exchanger type
        """
        if hx_type not in HeatExchangerType.TYPES:
            raise ValueError(f"Unknown heat exchanger type: {hx_type}")
        return HeatExchangerType.TYPES[hx_type]
    
    @staticmethod
    def get_typical_U_value(hx_type, fluid_combination):
        """
        Get typical U-value for a heat exchanger type and fluid combination.
        
        Args:
            hx_type (str): Type of heat exchanger
            fluid_combination (str): Fluid combination (e.g., 'Water-Water')
            
        Returns:
            tuple: (min_U, max_U) in W/(m²·K)
        """
        info = HeatExchangerType.get_type_info(hx_type)
        U_range = info['typical_U_range'].get(fluid_combination, None)
        
        if U_range is None:
            # Return a default range if specific combination not found
            return (100, 500)
        
        return U_range
    
    @staticmethod
    def get_average_U_value(hx_type, fluid_combination):
        """
        Get average typical U-value.
        
        Args:
            hx_type (str): Type of heat exchanger
            fluid_combination (str): Fluid combination
            
        Returns:
            float: Average U-value in W/(m²·K)
        """
        min_U, max_U = HeatExchangerType.get_typical_U_value(hx_type, fluid_combination)
        return (min_U + max_U) / 2
    
    @staticmethod
    def list_all_types():
        """
        List all available heat exchanger types.
        
        Returns:
            list: List of heat exchanger type names
        """
        return list(HeatExchangerType.TYPES.keys())
    
    @staticmethod
    def get_fluid_combinations(hx_type):
        """
        Get available fluid combinations for a heat exchanger type.
        
        Args:
            hx_type (str): Type of heat exchanger
            
        Returns:
            list: List of fluid combinations
        """
        info = HeatExchangerType.get_type_info(hx_type)
        return list(info['typical_U_range'].keys())


# Flow arrangement types
FLOW_ARRANGEMENTS = {
    'Counter Flow': {
        'description': 'Fluids flow in opposite directions. Maximum efficiency.',
        'efficiency': 'Highest',
        'LMTD_correction': 1.0,
        'suitable_for': 'Close temperature approach applications'
    },
    'Parallel Flow': {
        'description': 'Fluids flow in same direction. Lower efficiency.',
        'efficiency': 'Lower',
        'LMTD_correction': 1.0,
        'suitable_for': 'Temperature-sensitive materials'
    },
    'Cross Flow': {
        'description': 'Fluids flow perpendicular to each other.',
        'efficiency': 'Medium',
        'LMTD_correction': 0.9,  # Approximate
        'suitable_for': 'Gas-liquid applications, air conditioning'
    }
}


def get_flow_arrangement_info(arrangement):
    """
    Get information about a flow arrangement.
    
    Args:
        arrangement (str): Flow arrangement type
        
    Returns:
        dict: Information about the flow arrangement
    """
    if arrangement not in FLOW_ARRANGEMENTS:
        raise ValueError(f"Unknown flow arrangement: {arrangement}")
    return FLOW_ARRANGEMENTS[arrangement]


# Testing
if __name__ == "__main__":
    print("Heat Exchanger Types Information\n")
    print("="*70)
    
    # List all types
    print("\nAvailable Heat Exchanger Types:")
    for hx_type in HeatExchangerType.list_all_types():
        print(f"  - {hx_type}")
    
    # Example: Shell-and-Tube info
    print("\n" + "="*70)
    print("\nShell-and-Tube Heat Exchanger:")
    info = HeatExchangerType.get_type_info('Shell-and-Tube')
    print(f"\nDescription: {info['description']}")
    print(f"\nTypical U-values:")
    for combo, (min_u, max_u) in info['typical_U_range'].items():
        avg_u = (min_u + max_u) / 2
        print(f"  {combo:20s}: {min_u:5.0f} - {max_u:5.0f} W/(m²·K)  (avg: {avg_u:.0f})")
    
    print(f"\nAdvantages:")
    for adv in info['advantages']:
        print(f"  + {adv}")
    
    print(f"\nApplications:")
    for app in info['applications']:
        print(f"  • {app}")
    
    # Flow arrangements
    print("\n" + "="*70)
    print("\nFlow Arrangements:")
    for arrangement, details in FLOW_ARRANGEMENTS.items():
        print(f"\n{arrangement}:")
        print(f"  Description: {details['description']}")
        print(f"  Efficiency: {details['efficiency']}")
