import pandas as pd
import numpy as np
from src.core.segmental_solver import SegmentalSolver
# CHANGED IMPORT:
from src.safety_checks.vibration import VibrationCheck
from src.safety_checks.api_660 import API660Validator

class DesignOptimizer:
    def __init__(self):
        self.solver = SegmentalSolver()

    def generate_guesses(self, base_inputs):
        guesses = []
        for shell in [0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2]:
            est_tubes = int(0.25 * (shell / 0.019)**2)
            for b_ratio in [0.2, 0.4, 0.6]:
                case = base_inputs.copy()
                case['shell_id'] = shell
                case['n_tubes'] = est_tubes
                case['baffle_spacing'] = round(shell * b_ratio, 2)
                guesses.append(case)
        return guesses

    def run_optimization(self, base_inputs):
        candidates = self.generate_guesses(base_inputs)
        results = []
        for case in candidates:
            try:
                res = self.solver.run(case)
                # CHANGED CALLS:
                vib = VibrationCheck(case, res).run_check()
                hyd = API660Validator(case, res).check_rho_v2()
                if (vib['status'] == 'PASS') and (hyd['status'] == 'PASS'):
                    results.append({
                        "Shell (m)": case['shell_id'],
                        "Baffle (m)": case['baffle_spacing'],
                        "Tubes": case['n_tubes'],
                        "Duty (kW)": round(res['Q']/1000, 1),
                        "Area (m2)": round(res['Area'], 1),
                        "U-Value": round(res['U'], 1),
                        "Status": "✅ Optimal"
                    })
            except: continue
        
        df = pd.DataFrame(results)
        if not df.empty: df = df.sort_values('U-Value', ascending=False).head(3)
        return df
