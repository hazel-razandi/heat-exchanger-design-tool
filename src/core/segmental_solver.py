import numpy as np
import pandas as pd
from src.core.properties import FluidProperties
from src.core.correlations import Correlations
from src.core.geometry import GeometryEngine

class SegmentalSolver:
    def __init__(self, n_zones=10):
        self.n_zones = n_zones

    def run(self, inputs):
        # 1. Setup Geometry & Fluids
        geo = GeometryEngine(inputs)
        hot_f = FluidProperties(inputs['hot_fluid'])
        cold_f = FluidProperties(inputs['cold_fluid'])
        
        # 2. Initial Conditions
        m_h, m_c = inputs['m_hot'], inputs['m_cold']
        Thi = inputs['T_hot_in']
        Tci = inputs['T_cold_in']
        
        # 3. Geometric Slicing
        # We divide the exchanger into 10 virtual slices
        total_area = np.pi * inputs['tube_od'] * inputs['length'] * inputs['n_tubes']
        area_per_zone = total_area / self.n_zones
        
        # Guess outlet temps to start the counter-flow iteration
        # Assume 60% efficiency as a starting guess
        Q_guess = 0.6 * min(m_h*2000, m_c*4000) * (Thi - Tci)
        Tho_guess = Thi - Q_guess / (m_h * 2000)
        Tco_guess = Tci + Q_guess / (m_c * 4000)
        
        # Storage for the 10 zones
        zone_results = []
        
        # We iterate backwards from Hot Inlet / Cold Outlet (Counter-flow approximation)
        current_Th = Thi
        current_Tc = Tco_guess 
        
        total_Q = 0
        
        # 4. The Segmental Loop
        for i in range(self.n_zones):
            # A. Local Bulk Temperatures for this slice
            Th_local = current_Th
            Tc_local = current_Tc
            
            # B. Get Properties AT THIS EXACT TEMP (The "Real Physics")
            rho_h, cp_h, mu_h, k_h, pr_h = hot_f.get_props(Th_local)
            rho_c, cp_c, mu_c, k_c, pr_c = cold_f.get_props(Tc_local)
            
            # C. Tube Side Physics (Local)
            At_flow = geo.get_tube_area()
            vt = m_h / (rho_h * At_flow)
            Re_t = (rho_h * vt * (inputs['tube_od']-0.002)) / mu_h
            ft = Correlations.friction_factor(Re_t, 0.000045/(inputs['tube_od']-0.002))
            Nu_t = Correlations.nusselt_gnielinski(Re_t, pr_h, ft)
            ht = Nu_t * k_h / (inputs['tube_od']-0.002)
            
            # D. Shell Side Physics (Local)
            As_flow = geo.get_shell_area()
            De = geo.get_hydraulic_diam()
            vs = m_c / (rho_c * As_flow)
            Re_s = (rho_c * vs * De) / mu_c
            Nu_s = Correlations.kern_shell_side(Re_s, pr_c, inputs['baffle_cut'])
            hs = Nu_s * k_c / De
            
            # E. Local Overall Heat Transfer Coefficient (U)
            U_clean = 1 / (1/hs + 1/ht + 0.0001)
            U_dirty = 1 / (1/U_clean + inputs['fouling'])
            
            # F. Calculate Heat Transfer for this Slice
            delta_T = Th_local - Tc_local
            Q_zone = U_dirty * area_per_zone * delta_T
            
            # G. Update Temperatures for the next slice
            dTh = Q_zone / (m_h * cp_h)
            dTc = Q_zone / (m_c * cp_c)
            
            # Store Data
            zone_results.append({
                "Zone": i+1,
                "T_Hot (°C)": round(Th_local, 1),
                "T_Cold (°C)": round(Tc_local, 1),
                "U_Local": round(U_dirty, 1),
                "Re_Shell": round(Re_s, 0),
                "Re_Tube": round(Re_t, 0),
                "Duty (kW)": round(Q_zone/1000, 2)
            })
            
            # Step temperatures
            current_Th -= dTh
            current_Tc -= dTc
            total_Q += Q_zone

        # 5. Compile Final Results
        return {
            "Q": total_Q,
            "U": np.mean([z['U_Local'] for z in zone_results]),
            "Area": total_area,
            "T_hot_out": current_Th,
            "T_cold_out": inputs['T_cold_in'], 
            "v_shell": vs,
            "v_tube": vt,
            "zone_df": pd.DataFrame(zone_results) # The Table Data
        }

