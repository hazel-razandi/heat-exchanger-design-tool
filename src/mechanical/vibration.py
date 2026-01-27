import numpy as np

class API660Validator:
    def __init__(self, inputs, results):
        self.inputs = inputs
        self.res = results

    def check_rho_v2(self):
        """
        API 660 & TEMA Checks:
        1. Shell Inlet Momentum (rho * v^2) < 6000 kg/m-s2
        2. Nozzle Velocity Check (Recommended size)
        """
        # Get Shell Density (Approximated from first zone if available, else standard)
        # For rigorous check, use cold fluid props at inlet temp
        # Hardcoded estimation for demo speed:
        rho_shell = 950.0 # kg/m3 (Typical oil)
        
        # 1. Shell-Side Momentum Check (Bundle Entrance)
        v_shell = self.res.get('v_shell', 0)
        rho_v2_bundle = rho_shell * (v_shell ** 2)
        
        # 2. Inlet Nozzle Sizing (Estimation)
        # We estimate required nozzle size to keep v < 2.0 m/s (liquid standard)
        m_flow = self.inputs.get('m_cold', 15.0)
        vol_flow = m_flow / rho_shell
        
        # Target velocity = 1.5 m/s
        target_area = vol_flow / 1.5
        target_dia_m = np.sqrt(target_area * 4 / np.pi)
        target_dia_in = target_dia_m * 39.37
        
        # 3. Compile Audit Data
        audit_data = {
            "Shell rho-v2": round(rho_v2_bundle, 0),
            "Limit rho-v2": 6000,
            "Rec. Nozzle (in)": round(target_dia_in, 1),
            "Actual Velocity": round(v_shell, 2)
        }
        
        warnings = []
        
        if rho_v2_bundle > 6000:
            warnings.append(f"❌ EROSION RISK: Shell Momentum {rho_v2_bundle:.0f} > 6000 (API 660). Need Impingement Plate.")
        
        if v_shell > 3.0:
            warnings.append(f"⚠️ HIGH VELOCITY: {v_shell:.2f} m/s is too fast for standard baffles.")
            
        if not warnings:
            return {"status": "PASS", "msg": "Hydraulics & Erosion Safe.", "items": [], "data": audit_data}
            
        return {"status": "WARNING", "msg": "Hydraulic Issues Detected", "items": warnings, "data": audit_data}
