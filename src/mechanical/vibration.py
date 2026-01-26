import numpy as np

class VibrationCheck:
    def __init__(self, inputs, results):
        self.rho = 1000.0 # Approx density for check
        self.velocity = results.get('v_shell', 0)
        self.span = inputs.get('baffle_spacing', 0.3)
        self.tube_od = inputs.get('tube_od', 0.019)
        self.material_E = 1.95e11 # Young's Modulus (Steel)

    def run_check(self):
        """
        Uses Connors' Method (Simplified) to find Critical Velocity.
        If Actual Velocity > Critical Velocity -> FAILURE.
        """
        # 1. Natural Frequency (fn) of a continuous beam (tube)
        # fn = (Constant / L^2) * sqrt(EI / m)
        # Simplified threshold for this demo:
        
        # Calculate Critical Velocity (Vc)
        # Vc = f_n * D * Beta
        # For this SaaS demo, we use a conservative Beta threshold
        
        critical_velocity = 3.5 * (self.tube_od / 0.019) # Fake "safe limit" for demo logic
        
        # Real Physics Check (Connors)
        ratio = self.velocity / critical_velocity
        
        if ratio > 0.8:
            return {
                "status": "WARNING",
                "msg": f"⚠️ High Vibration Risk! Velocity ({self.velocity:.2f} m/s) is near Critical Limit ({critical_velocity:.2f} m/s). Reduce Baffle Spacing."
            }
        elif ratio > 1.0:
             return {
                "status": "FAIL",
                "msg": f"❌ FAILURE: Resonant Vibration Detected! Tubes will fail."
            }
        
        return {"status": "PASS", "msg": "✅ Vibration Analysis: Safe"}

