"""
Iterative Design Solver (V4.0)
"""
import numpy as np
from src.fluid_properties import FluidProperties
from src.correlations import Correlations
from src.geometry_models import ShellGeometry
from src.materials import MaterialDB

class DesignSolver:
    def solve_rating(self, inputs):
        # 1. Setup
        m_h, m_c = inputs['m_hot'], inputs['m_cold']
        Thi, Tci = inputs['T_hot_in'], inputs['T_cold_in']
        hot_f = FluidProperties(inputs['hot_fluid'])
        cold_f = FluidProperties(inputs['cold_fluid'])
        mat = MaterialDB.get_properties(inputs['material'])
        
        # Geometry
        geom = ShellGeometry(inputs['shell_id'], inputs['n_tubes'], inputs['tube_od'], 
                             inputs['pitch_ratio'], inputs['baffle_spacing'])
        
        # 2. Iteration Loop (Energy Balance)
        Q = 0.5 * min(m_h*2000, m_c*4000) * (Thi - Tci) # Initial Guess
        
        for _ in range(15):
            # Calculate Outlets based on Guess Q
            Tho = Thi - Q / (m_h * hot_f.get_specific_heat((Thi+Thi)/2))
            Tco = Tci + Q / (m_c * cold_f.get_specific_heat((Tci+Tci)/2))
            
            # Avg Properties
            Th_avg, Tc_avg = (Thi+Tho)/2, (Tci+Tco)/2
            
            # --- Tube Side Physics ---
            At = (np.pi*(inputs['tube_od']-0.002)**2/4) * (inputs['n_tubes']/2)
            vt = m_h / (hot_f.get_density(Th_avg) * At)
            Ret = (hot_f.get_density(Th_avg)*vt*(inputs['tube_od']-0.002)) / hot_f.get_viscosity(Th_avg)
            ft = Correlations.friction_factor_turbulent(Ret, 0.000045/(inputs['tube_od']-0.002))
            Nut = Correlations.nusselt_gnielinski(Ret, hot_f.get_prandtl(Th_avg), ft)
            ht = Nut * hot_f.get_conductivity(Th_avg) / (inputs['tube_od']-0.002)
            
            # --- Shell Side Physics (Kern) ---
            As = geom.get_shell_side_area()
            Des = geom.get_equiv_diameter()
            vs = m_c / (cold_f.get_density(Tc_avg) * As)
            Res = (cold_f.get_density(Tc_avg)*vs*Des) / cold_f.get_viscosity(Tc_avg)
            Nus = Correlations.kern_shell_side_Nu(Res, cold_f.get_prandtl(Tc_avg), 25)
            hs = Nus * cold_f.get_conductivity(Tc_avg) / Des
            
            # --- Overall U ---
            k_w = mat['k']
            Rw = 0.002 / k_w # Wall resistance
            U_clean = 1 / (1/hs + 1/ht + Rw)
            U_dirty = 1 / (1/U_clean + inputs['fouling'])
            
            # New Q
            LMTD = ((Thi-Tco) - (Tho-Tci)) / np.log((Thi-Tco)/(Tho-Tci)) if abs((Thi-Tco)-(Tho-Tci)) > 0.1 else (Thi-Tco)
            Area = np.pi * inputs['tube_od'] * inputs['length'] * inputs['n_tubes']
            Q_new = U_dirty * Area * LMTD
            
            if abs(Q_new - Q) < 500: break # Converged
            Q = (Q + Q_new) / 2
            
        return {
            'Q': Q_new/1000, 'U': U_dirty, 'Area': Area, 
            'T_hot_out': Tho, 'T_cold_out': Tco,
            'v_tube': vt, 'v_shell': vs, 'Re_shell': Res, 'Re_tube': Ret
        }

