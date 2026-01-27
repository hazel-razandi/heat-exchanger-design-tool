import pandas as pd
import numpy as np
from src.core.segmental_solver import SegmentalSolver
from src.mechanical.vibration import VibrationCheck
from src.mechanical.api_660 import API660Validator

class DesignOptimizer:
    def __init__(self):
        self.solver = SegmentalSolver()

    def generate_guesses(self, base_inputs):
        """
        Generates smart geometric combinations to test.
        """
        guesses = []
        
        # Standard Shell Diameters (TEMA Sizes)
        std_shells = [0.3, 0.4, 0.5, 0.6, 0.8, 1.0, 1.2]
        
        for shell in std_shells:
            # Heuristic: Estimate Max Tubes that fit in this shell
            # N = K * (Ds / do)^2
            # K approx 0.25 for conservative pitch
            est_tubes = int(0.25 * (shell / 0.019)**2)
            
            # Test 3 Baffle Spacings for each shell (20%, 40%, 60% of shell ID)
            for b_ratio in [0.2, 0.4, 0.6]:
                case = base_inputs.copy()
                case['shell_id'] = shell
                case['n_tubes'] = est_tubes
                case['baffle_spacing'] = round(shell * b_ratio, 2)
                guesses.append(case)
                
        return guesses

    def run_optimization(self, base_inputs):
        """
        Runs the solver on 20+ variations and ranks them.
        """
        candidates = self.generate_guesses(base_inputs)
        results = []
        
        for case in candidates:
            try:
                # 1. Run Physics
                res = self.solver.run(case)
                
                # 2. Run Safety
                vib = VibrationCheck(case, res).run_check()
                hyd = API660Validator(case, res).check_rho_v2()
                
                # 3. Calculate "Score"
                # Safety is binary (Must Pass)
                is_safe = (vib['status'] == 'PASS') and (hyd['status'] == 'PASS')
                
                if is_safe:
                    results.append({
                        "Shell (m)": case['shell_id'],
                        "Baffle (m)": case['baffle_spacing'],
                        "Tubes": case['n_tubes'],
                        "Duty (kW)": round(res['Q']/1000, 1),
                        "Area (m2)": round(res['Area'], 1),
                        "U-Value": round(res['U'], 1),
                        "Pressure Drop": "Low" if res['v_shell'] < 1.0 else "Med",
                        "Status": "✅ Optimal"
                    })
            except:
                continue # Skip failed math cases
        
        # Convert to DataFrame
        df = pd.DataFrame(results)
        
        if not df.empty:
            # Sort by Efficiency (U-Value) for now
            df = df.sort_values('U-Value', ascending=False).head(3)
            
        return df

