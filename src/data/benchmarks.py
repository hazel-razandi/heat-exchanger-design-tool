"""
Validation Cases from Standard Literature (Kern, API, HTRI)
"""

def get_benchmarks():
    return {
        "Kern_Ex_11_1": {
            "name": "Kern Example 11.1 (Oil Cooler)",
            "source": "Process Heat Transfer, D.Q. Kern, pg. 145",
            "description": "Cooling of 43,800 lb/hr of raw oil (35°API) using water.",
            "inputs": {
                'shell_id': 0.39,      # 15.25 inch ID
                'length': 4.88,        # 16 ft
                'n_tubes': 158,
                'tube_od': 0.019,      # 3/4 inch
                'baffle_spacing': 0.15, # 6 inch
                'baffle_cut': 25,       
                'pitch_ratio': 1.25,
                'n_passes': 2,
                'fouling': 0.0003,      # <--- ADDED THIS MISSING KEY
                'm_hot': 5.52,         # 43800 lb/hr approx
                'm_cold': 15.0,        # Water flow
                'T_hot_in': 121.0,     # 250 F
                'T_cold_in': 29.0,     # 85 F
                'hot_fluid': 'Oil_35API', 
                'cold_fluid': 'Water',
                # Add default geometry keys to prevent other errors
                'tema_type': 'BEM',
                'tube_layout': 'Triangular'
            },
            "targets": {
                "U_Service": 475.0,     # W/m2K
                "Duty_kW": 385.0,
                "Pressure_Shell_bar": 0.8,
                "Pressure_Tube_bar": 0.4
            }
        }
    }
