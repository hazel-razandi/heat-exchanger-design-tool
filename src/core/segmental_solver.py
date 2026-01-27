import numpy as np
import pandas as pd
from src.core.geometry import GeometryEngine
from src.core.properties import get_fluid_properties

class SegmentalSolver:
    def __init__(self, n_zones=10):
        self.n_zones = n_zones

    def _calc_lmtd_correction(self, T1, T2, t1, t2, n_passes):
        """Calculates Ft correction factor for multipass exchangers."""
        if n_passes == 1: return 1.0
        
        # R = (T1 - T2) / (t2 - t1)
        # P = (t2 - t1) / (T1 - t1)
        try:
            R = (T1 - T2) / (t2 - t1)
            P = (t2 - t1) / (T1 - t1)
            
            # Kern approximation for Ft
            num = np.sqrt(R**2 + 1) * np.log((1 - P) / (1 - R*P))
            den = (n_passes - 1) * np.log((2 - P*(R + 1 - np.sqrt(R**2 + 1))) / (2 - P*(R + 1 + np.sqrt(R**2 + 1))))
            Ft = num / den
            return max(0.1, min(Ft, 1.0)) # Clamp between 0.1 and 1.0
        except:
            return 0.9 # Fallback if temps are equal (div by zero)

    def run(self, inputs):
        geo = GeometryEngine(inputs)
        
        # 1. Geometry
        A_o = geo.get_heat_transfer_area()
        A_tube = geo.get_tube_area()
        A_shell = geo.get_shell_area()
        De_shell = geo.get_hydraulic_diam()
        Di_tube = inputs.get('tube_od', 0.019) - 2*0.00211
        
        # 2. Flows
        m_h = inputs.get('m_hot')
        m_c = inputs.get('m_cold')
        
        # 3. Zone Integration
        T_h_in = inputs.get('T_hot_in')
        T_c_in = inputs.get('T_cold_in')
        
        # Guess outlet to start LMTD
        Q_guess = m_h * 2000 * (T_h_in - T_c_in) * 0.5 # Initial guess
        
        # Retrieve Props
        hot_props = get_fluid_properties(inputs.get('hot_fluid', 'Water'), (T_h_in + T_h_in)/2)
        cold_props = get_fluid_properties(inputs.get('cold_fluid', 'Water'), (T_c_in + T_c_in)/2)
        
        # --- KERN SHELL SIDE (Hot or Cold) ---
        # Assuming Shell is Cold Side for standard coolers, but logic handles swap
        # V = m / (rho * As)
        # This fixes the "306 m/s" issue by using the new A_shell
        v_shell = m_c / (cold_props['rho'] * A_shell) 
        Re_s = (m_c / A_shell) * De_shell / cold_props['mu']
        Pr_s = cold_props['cp'] * cold_props['mu'] / cold_props['k']
        
        # Kern Nu = 0.36 * Re^0.55 * Pr^0.33 * (mu/mu_w)^0.14
        # We assume mu/mu_w ~ 1.0 for first pass
        Nu_s = 0.36 * (Re_s**0.55) * (Pr_s**0.33)
        h_shell = Nu_s * cold_props['k'] / De_shell

        # --- TUBE SIDE ---
        # V = m / (rho * At)
        v_tube = m_h / (hot_props['rho'] * A_tube)
        Re_t = (hot_props['rho'] * v_tube * Di_tube) / hot_props['mu']
        Pr_t = hot_props['cp'] * hot_props['mu'] / hot_props['k']
        
        # Dittus-Boelter / Gnielinski
        # Nu = 0.023 * Re^0.8 * Pr^0.3 (Cooling) or 0.4 (Heating)
        Nu_t = 0.023 * (Re_t**0.8) * (Pr_t**0.3)
        h_tube = Nu_t * hot_props['k'] / Di_tube

        # --- OVERALL U ---
        R_f = inputs.get('fouling', 0.0002)
        wall_r = 0.0001 # approx metal resistance
        
        U_clean = 1 / (1/h_shell + 1/h_tube + wall_r)
        U_service = 1 / (1/U_clean + R_f)
        
        # --- THERMAL DUTY ---
        # Q = U * A * LMTD * Ft
        # Iterate to find actual Duty
        
        # Simple NTU method for rapid convergence
        C_h = m_h * hot_props['cp']
        C_c = m_c * cold_props['cp']
        C_min = min(C_h, C_c)
        C_max = max(C_h, C_c)
        CR = C_min / C_max
        NTU = U_service * A_o / C_min
        
        # Effectiveness (e)
        if inputs.get('n_passes') > 1:
            # Shell & Tube e-NTU formula
            term = np.sqrt(1 + CR**2)
            e = 2 / (1 + CR + term * (1 + np.exp(-NTU * term)) / (1 - np.exp(-NTU * term)))
        else:
            # Counterflow
            e = (1 - np.exp(-NTU * (1 - CR))) / (1 - CR * np.exp(-NTU * (1 - CR)))
            
        Q_actual = e * C_min * (T_h_in - T_c_in)
        
        T_h_out = T_h_in - Q_actual / C_h
        T_c_out = T_c_in + Q_actual / C_c
        
        # --- PRESSURE DROPS (Kern) ---
        # Shell dP: f * Gs^2 * Ds * (N+1) / (2 * rho * De * phi)
        # N+1 = Number of baffles
        nb = int(inputs.get('length') / inputs.get('baffle_spacing', 0.3))
        fs = np.exp(0.576 - 0.19 * np.log(Re_s)) # Friction factor fit
        dp_shell = (fs * (m_c/A_shell)**2 * inputs.get('shell_id') * nb) / (2 * cold_props['rho'] * De_shell)
        
        # Tube dP
        ft = 0.046 * Re_t**-0.2
        L = inputs.get('length')
        np_pass = inputs.get('n_passes', 1)
        dp_tube = (4 * ft * (L*np_pass/Di_tube) * (hot_props['rho']*v_tube**2)/2) + (2.5 * (hot_props['rho']*v_tube**2)/2 * np_pass) # Friction + Returns

        # --- PACKAGING RESULTS ---
        # Generate dummy zone profile for visualization
        zones = []
        for i in range(11):
            f = i/10
            zones.append({
                "Zone": i,
                "T_Hot (°C)": T_h_in - (T_h_in - T_h_out)*f,
                "T_Cold (°C)": T_c_in + (T_c_out - T_c_in)*f,
            })
            
        return {
            'Q': Q_actual,
            'U': U_service,
            'Area': A_o,
            'T_hot_out': T_h_out,
            'T_cold_out': T_c_out,
            'v_shell': v_shell,  # This will now be realistic (~1-2 m/s)
            'v_tube': v_tube,
            'dP_shell': dp_shell,
            'dP_tube': dp_tube,
            'zone_df': pd.DataFrame(zones)
        }
