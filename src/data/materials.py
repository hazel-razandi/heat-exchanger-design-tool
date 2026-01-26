class MaterialDB:
    DATA = {
        'Carbon Steel (A516)': {'k': 54.0, 'cost_factor': 1.0},
        'Stainless Steel 304': {'k': 16.2, 'cost_factor': 2.8},
        'Stainless Steel 316L': {'k': 16.3, 'cost_factor': 3.5},
        'Titanium (Gr.2)': {'k': 21.9, 'cost_factor': 8.5},
        'Copper-Nickel (90/10)': {'k': 50.0, 'cost_factor': 3.2}
    }
    @staticmethod
    def get_names(): return list(MaterialDB.DATA.keys())
    @staticmethod
    def get_props(name): return MaterialDB.DATA.get(name, MaterialDB.DATA['Carbon Steel (A516)'])

