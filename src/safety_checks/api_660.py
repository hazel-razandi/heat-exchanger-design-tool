import numpy as np

class API660Validator:
    def __init__(self, inputs, results):
        self.inputs = inputs
        self.res = results

    def check_rho_v2(self):
        rho_shell = 950.0 
        v_shell = self.res.get('v_shell', 0)
        rho_v2 = rho_shell * (v_shell ** 2)
        
        m_flow = self.inputs.get('m_cold', 15.0)
        target_dia_in = np.sqrt((m_flow/rho_shell/1.5) * 4 / np.pi) * 39.37
        
        audit = {
            "Shell rho-v2": round(rho_v2, 0),
            "Limit rho-v2": 6000,
            "Rec. Nozzle (in)": round(target_dia_in, 1),
            "Actual Velocity": round(v_shell, 2)
        }
        
        warnings = []
        if rho_v2 > 6000: warnings.append(f"❌ EROSION RISK: Momentum {rho_v2:.0f} > 6000.")
        if v_shell > 3.0: warnings.append(f"⚠️ HIGH VELOCITY: {v_shell:.2f} m/s.")
            
        if not warnings:
            return {"status": "PASS", "msg": "Hydraulics Safe.", "items": [], "data": audit}
            
        return {"status": "WARNING", "msg": "Hydraulic Issues", "items": warnings, "data": audit}

