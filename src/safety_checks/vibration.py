import numpy as np

class VibrationCheck:
    def __init__(self, inputs, results):
        self.inputs = inputs
        self.res = results
        self.E = 200e9  # Young's Modulus (Pa)
        self.rho_steel = 7850 # kg/m3
        self.do = inputs.get('tube_od', 0.01905)
        self.wall_thick = 0.00211
        self.di = self.do - 2*self.wall_thick
        self.span = inputs.get('baffle_spacing', 0.3)
        
    def run_check(self):
        # 1. Effective Mass
        area_metal = np.pi * (self.do**2 - self.di**2) / 4
        m_metal = area_metal * self.rho_steel
        m_fluid = (np.pi * self.di**2 / 4) * 900 
        m_total = m_metal + m_fluid
        
        # 2. Natural Frequency
        I = np.pi * (self.do**4 - self.di**4) / 64
        fn = 9.81 * np.sqrt((self.E * I) / (m_total * self.span**4)) / (2*np.pi)
        
        # 3. Vortex Shedding
        v_actual = self.res.get('v_shell', 0)
        f_shedding = 0.2 * v_actual / self.do
        
        ratio = f_shedding / (fn + 0.001)
        
        audit = {
            "Natural Freq (Hz)": round(fn, 1),
            "Shedding Freq (Hz)": round(f_shedding, 1),
            "Velocity (m/s)": round(v_actual, 2),
            "Ratio (fs/fn)": round(ratio, 2)
        }

        if ratio > 0.8 and ratio < 1.2:
            return {"status": "FAIL", "msg": f"CRITICAL RESONANCE! Shedding ({f_shedding:.1f}Hz) matches Tube Freq ({fn:.1f}Hz).", "data": audit}
        elif ratio > 1.2:
            return {"status": "WARNING", "msg": "High Frequency Vibration Risk.", "data": audit}
        if v_actual > 2.5:
             return {"status": "FAIL", "msg": f"Velocity {v_actual:.2f} m/s exceeds safe cap.", "data": audit}

        return {"status": "PASS", "msg": "Vibration Analysis Safe.", "data": audit}

