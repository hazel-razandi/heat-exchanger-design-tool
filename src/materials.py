"""
Material Database (V4.0 Physics)
"""
class MaterialDB:
    # k: Thermal Conductivity (W/m-K) -> Crucial for Wall Resistance
    # rho: Density (kg/m3) -> Crucial for Weight/Cost
    # cost: Multiplier vs Carbon Steel
    DATA = {
        'Carbon Steel (A516)':      {'k': 54.0, 'rho': 7850, 'cost': 1.0,  'max_t': 500},
        'Stainless Steel 304':      {'k': 16.2, 'rho': 7900, 'cost': 2.8,  'max_t': 800},
        'Stainless Steel 316L':     {'k': 16.3, 'rho': 7980, 'cost': 3.5,  'max_t': 850},
        'Titanium (Gr.2)':          {'k': 21.9, 'rho': 4500, 'cost': 8.5,  'max_t': 600},
        'Hastelloy C-276':          {'k': 10.2, 'rho': 8890, 'cost': 15.0, 'max_t': 1000},
        'Copper-Nickel (90/10)':    {'k': 50.0, 'rho': 8900, 'cost': 3.2,  'max_t': 300}
    }

    @staticmethod
    def get_properties(name):
        return MaterialDB.DATA.get(name, MaterialDB.DATA['Carbon Steel (A516)'])

    @staticmethod
    def get_names():
        return list(MaterialDB.DATA.keys())
￼Enter
