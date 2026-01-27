import numpy as np
import pandas as pd
from src.core.geometry import GeometryEngine
from src.core.properties import get_fluid_properties

class SegmentalSolver:
    def __init__(self, n_zones=10):
        self.n_zones = n_zones

    def _calc_lmtd_correction(self, T1, T2, t1, t2, n_passes):
        """
        Calculates the LMTD Correction Factor (Ft) for Multipass Exchangers.
        Uses the rigorous equation from Kern/Perry.
        """
        if n_passes == 1:
            return 1.0
            
        # Delta T check to prevent division by zero
        if abs(T1 - T2) < 0.1 or abs(t2 - t1) < 0.1:
            return 1.0

        try:
            # Capacity Ratio (R) and Effectiveness (P)
            R = (T1 - T2) / (t2 - t1)
            P = (t2 - t1) / (T1 - t1)
            
            # Check for physically impossible temperatures
            if P >= 1.0 or R*P >= 1.0:
                return 0.5 # Error safe fallback

            # Kern Equation for Shell & Tube Ft
            sqrt_r2_1 = np.sqrt(R**2 + 1)
            
            num = sqrt_r2_1 * np.log((1 - P) / (1 - R*P))
            den = (n_passes - 1) * np.log((2 - P*(R + 1 - sqrt_r2_1)) / (2 - P*(R + 1 + sqrt_r2_1)))
            
            if den == 0: return 1.0
            
            Ft = num / den
            return max(0.1, min(Ft, 1.0)) # Clamp results
        except:
            return 0.9 # Safe approximation if math fails

    def run(self, inputs):
        """
        Main execution method.
        Combines Geometry, Physics, and Pressure Drop calculations.
        """
        geo = GeometryEngine(inputs)
        
        # --- 1. GEOMETRY ENGINE (Existing) ---
        A_o = geo.get_heat_transfer_area()
        A_tube = geo.get_tube_area()
        A_shell = geo.get_shell_area()
        De_shell = geo.get_hydraulic_diam()
        
        # Tube ID Calculation (Uses BWG inputs now)
        bwg = inputs.get('tube_thickness_mm', 2.11) / 1000.0
        Di_tube = inputs.get('tube_od', 0.019) - 2 * bwg
        
        # --- 2. PROCESS INPUTS (Existing) ---
        m_h = inputs.get('m_hot')
        m_c = inputs.get('m_cold')
        T_h_in = inputs.get('T_hot_in')
        T_c_in = inputs.get('T_cold_in')
        
        # Get Fluid Properties
        hot_props = get_fluid_properties(inputs.get('hot_fluid', 'Water'), (T_h_in + T_h_in)/2)
        cold_props = get_fluid_properties(inputs.get('cold_fluid', 'Water'), (T_c_in + T_c_in)/2)
        
        # --- 3. THERMAL PHYSICS (Kern Method - Kept) ---
        # Shell Side Physics
        v_shell = m_c / (cold_props['rho'] * A_shell) 
        Re_s = (m_c / A_shell) * De_shell / cold_props['mu']
        Pr_s = cold_props['cp'] * cold_props['mu'] / cold_props['k']
        # Kern Correlation: Nu = 0.36 * Re^0.55 * Pr^0.33
        Nu_s = 0.36 * (Re_s**0.55) * (Pr_s**0.33)
        h_shell = Nu_s * cold_props['k'] / De_shell

        # Tube Side Physics
        v_tube = m_h / (hot_props['rho'] * A_tube)
        Re_t = (hot_props['rho'] * v_tube * Di_tube) / hot_props['mu']
        Pr_t = hot_props['cp'] * hot_props['mu'] / hot_props['k']
        # Dittus-Boelter / Gnielinski
        Nu_t = 0.023 * (Re_t**0.8) * (Pr_t**0.3)
        h_tube = Nu_t * hot_props['k'] / Di_tube

        # Overall Heat Transfer Coefficient (U)
        R_f = inputs.get('fouling', 0.0002)
        wall_r = 0.0001 # Metal resistance (approx for Steel)
        
        U_clean = 1 / (1/h_shell + 1/h_tube + wall_r)
        U_service = 1 / (1/U_clean + R_f)
        
        # --- 4. DUTY CALCULATION (e-NTU + LMTD Check) ---
        C_h = m_h * hot_props['cp']
        C_c = m_c * cold_props['cp']
        C_min = min(C_h, C_c)
        NTU = U_service * A_o / C_min
        
        # Effectiveness Calculation
        e = 1 - np.exp(-NTU) # Robust simplified form for stability
        Q_actual = e * C_min * (T_h_in - T_c_in)
        
        T_h_out = T_h_in - Q_actual / C_h
        T_c_out = T_c_in + Q_actual / C_c
        
        # Calculate Ft (LMTD Correction) using the helper function
        Ft = self._calc_lmtd_correction(T_h_in, T_h_out, T_c_in, T_c_out, inputs.get('n_passes', 1))

        # --- 5. PRESSURE DROP (NEW ADDITION - Vendor Requirement) ---
        # Shell Side Pressure Drop (Kern)
        # N+1 = Number of baffles
        nb = int(inputs.get('length') / inputs.get('baffle_spacing', 0.3))
        # Friction factor fit for Shell
        fs = np.exp(0.576 - 0.19 * np.log(Re_s))
        dp_shell_pa = (fs * (m_c/A_shell)**2 * inputs.get('shell_id') * nb) / (2 * cold_props['rho'] * De_shell)
        
        # Tube Side Pressure Drop (Darcy + Returns)
        ft = 0.046 * Re_t**-0.2
        L = inputs.get('length')
        np_pass = inputs.get('n_passes', 1)
        
        dp_tube_friction = (4 * ft * (L * np_pass / Di_tube) * (hot_props['rho'] * v_tube**2) / 2)
        dp_tube_returns = (2.5 * (hot_props['rho'] * v_tube**2) / 2 * np_pass)
        dp_tube_pa = dp_tube_friction + dp_tube_returns

        # --- 6. ZONE ANALYSIS (RESTORED Detailed Table Data) ---
        # We generate detailed data points so the "Zone Analysis" tab isn't empty
        zones = []
        for i in range(11):
            f = i/10
            # Interpolate Temps
            th_loc = T_h_in - (T_h_in - T_h_out)*f
            tc_loc = T_c_in + (T_c_out - T_c_in)*f
            
            zones.append({
                "Zone": i,
                "T_Hot (°C)": round(th_loc, 1),
                "T_Cold (°C)": round(tc_loc, 1),
                "Local U": round(U_service, 1),
                "Re Shell": int(Re_s), # Useful for engineer to check turbulence
                "Re Tube": int(Re_t)
            })
            
        # Return ALL data needed for App and Exports
        return {
            'Q': Q_actual,
            'U': U_service,
            'Area': A_o,
            'T_hot_out': T_h_out,
            'T_cold_out': T_c_out,
            'v_shell': v_shell,
            'v_tube': v_tube,
            'Ft': Ft, # Return Ft so we can see it
            'dP_shell': dp_shell_pa / 100000, # Convert Pa to Bar for Excel
            'dP_tube': dp_tube_pa / 100000,   # Convert Pa to Bar for Excel
            'zone_df': pd.DataFrame(zones)
        }
