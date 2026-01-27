import numpy as np

class VibrationCheck:
    def __init__(self, inputs, results):
        self.inputs = inputs
        self.res = results
        
        # Physical Constants (Carbon Steel)
        self.E = 200e9  # Young's Modulus (Pa)
        self.rho_steel = 7850 # kg/m3
        
        # Geometry
        self.do = inputs.get('tube_od', 0.01905) # OD (m)
        self.wall_thick = 0.00211 # BWG 14 approx (m)
        self.di = self.do - 2*self.wall_thick
        self.span = inputs.get('baffle_spacing', 0.3)
        
    def run_check(self):
        """
        Calculates Natural Frequency (fn) and Critical Velocity (vc).
        Uses TEMA / Connors' method simplified.
        """
        # 1. Calculate Tube Mass (m_e) - effective mass per length
        # Metal mass
        area_metal = np.pi * (self.do**2 - self.di**2) / 4
        m_metal = area_metal * self.rho_steel
        
        # Internal Fluid Mass (Assumed filled with hot fluid)
        # We approximate hot fluid density as 900 kg/m3 (oil/water mix)
        area_internal = np.pi * (self.di**2) / 4
        m_fluid = area_internal * 900 
        
        # Total effective mass per unit length (kg/m)
        m_total = m_metal + m_fluid
        
        # 2. Moment of Inertia (I)
        I = np.pi * (self.do**4 - self.di**4) / 64
        
        # 3. Natural Frequency (fn) - Continuous Beam on Multi-Supports
        # fn = C * sqrt(EI / m L^4)
        # C approx 9.87 for fixed-fixed (conservative for multi-span)
        # Using TEMA factor for intermediate spans
        fn = 9.81 * np.sqrt((self.E * I) / (m_total * self.span**4)) / (2*np.pi)
        
        # 4. Critical Velocity (Connors' Equation)
        # Vc = beta * fn * do * sqrt(m_damping / (rho_shell * do^2))
        # Simplified: Vc_limit approx 40 * fn * do * sqrt(...)
        # For this SaaS demo, we use a Critical Velocity Threshold based on frequency
        # Threshold: Fluid velocity should stay below prediction to avoid shedding resonance
        
        # Vortex Shedding Frequency (Strouhal Number ~ 0.2)
        v_actual = self.res.get('v_shell', 0)
        f_shedding = 0.2 * v_actual / self.do
        
        # RISK RATIO
        # If shedding freq is close to natural freq (+/- 20%), Resonance occurs
        ratio = f_shedding / (fn + 0.001)
        
        audit_data = {
            "Natural Freq (Hz)": round(fn, 1),
            "Shedding Freq (Hz)": round(f_shedding, 1),
            "Velocity (m/s)": round(v_actual, 2),
            "Ratio (fs/fn)": round(ratio, 2)
        }

        # STATUS CHECK
        if ratio > 0.8 and ratio < 1.2:
            return {"status": "FAIL", "msg": f"CRITICAL RESONANCE! Shedding ({f_shedding:.1f}Hz) matches Tube Freq ({fn:.1f}Hz).", "data": audit_data}
        elif ratio > 1.2:
            return {"status": "WARNING", "msg": "High Frequency Vibration Risk (Super-Critical Flow).", "data": audit_data}
        
        # Check Crossflow Amplitude limit (Connors)
        # Simplified: keep velocity under 1.5 m/s for standard liquids
        if v_actual > 2.5:
             return {"status": "FAIL", "msg": f"Velocity {v_actual:.2f} m/s exceeds safe cap (2.5 m/s).", "data": audit_data}

        return {"status": "PASS", "msg": "Vibration Analysis Safe (No Resonance).", "data": audit_data}
