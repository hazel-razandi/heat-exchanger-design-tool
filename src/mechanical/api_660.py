class API660Validator:
    def __init__(self, inputs, results):
        self.res = results
        self.inputs = inputs

    def check_rho_v2(self):
        """
        API 660 Limit: Rho * v^2 should not exceed 6000 kg/m-s2 for shell side
        to prevent erosion of the bundle.
        """
        # We need density. In full app, pass density from Solver. 
        # For now, approximate or retrieve from context if available.
        rho_shell = 980.0 # Approx water/oil
        v_shell = self.res.get('v_shell', 0)
        
        rho_v2 = rho_shell * (v_shell ** 2)
        
        warnings = []
        
        # 1. Shell Side Erosion
        if rho_v2 > 6000:
            warnings.append(f"❌ API 660 FAIL: Shell momentum ({rho_v2:.0f}) exceeds 6000. Erosion risk.")
        
        # 2. Tube Side Velocity Limits
        v_tube = self.res.get('v_tube', 0)
        if v_tube > 3.5:
             warnings.append(f"⚠️ HIGH VELOCITY: Tube velocity {v_tube:.2f} m/s exceeds recommended 3.0 m/s.")
        elif v_tube < 0.8:
             warnings.append(f"⚠️ LOW VELOCITY: Tube velocity {v_tube:.2f} m/s allows fouling (sediment buildup).")

        if not warnings:
            return {"status": "PASS", "msg": "✅ API 660 Hydraulics: Safe"}
        
        return {"status": "WARNING", "items": warnings}

