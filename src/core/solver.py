import numpy as np
from src.core.properties import FluidProperties
from src.core.correlations import Correlations
from src.core.geometry import GeometryEngine

class SegmentalSolver:
    def run(self, inputs):
        # 1. Setup
        geo = GeometryEngine(inputs)
        hot_f = FluidProperties(inputs['hot_fluid'])
        cold_f = FluidProperties(inputs['cold_fluid'])
        
        m_h, m_c = inputs['m_hot'], inputs['m_cold']
        Thi, Tci = inputs['T_hot_in'], inputs['T_cold_in']
        
        # 2. Energy Balance Guess
        Q_total = 0.5 * min(m_h*2000, m_c*4000) * (Thi - Tci)
        Tho = Thi - Q_total / (m_h * 2000)
        Tco = Tci + Q_total / (m_c * 4000)
        
        # 3. Iteration Loop (Simple LMTD for stability first)
        for _ in range(10):
            # Properties at Avg Temp
            Th_avg, Tc_avg = (Thi+Tho)/2, (Tci+Tco)/2
            rho_h, cp_h, mu_h, k_h, pr_h = hot_f.get_props(Th_avg)
            rho_c, cp_c, mu_c, k_c, pr_c = cold_f.get_props(Tc_avg)
            
            # Tube Side Physics
            At = geo.get_tube_area()
            vt = m_h / (rho_h * At)
            Re_t = (rho_h * vt * (inputs['tube_od']-0.002)) / mu_h
            ft = Correlations.friction_factor(Re_t, 0.000045/(inputs['tube_od']-0.002))
            Nu_t = Correlations.nusselt_gnielinski(Re_t, pr_h, ft)
            ht = Nu_t * k_h / (inputs['tube_od']-0.002)
            
            # Shell Side Physics
            As = geo.get_shell_area()
            De = geo.get_hydraulic_diam()
            vs = m_c / (rho_c * As)
            Re_s = (rho_c * vs * De) / mu_c
            Nu_s = Correlations.kern_shell_side(Re_s, pr_c, inputs['baffle_cut'])
            hs = Nu_s * k_c / De
            
            # Overall U
            U_clean = 1 / (1/hs + 1/ht + 0.0001) # Wall neglected for speed
            U_dirty = 1 / (1/U_clean + inputs['fouling'])
            
            # New Q
            LMTD = ((Thi-Tco)-(Tho-Tci))/np.log((Thi-Tco)/(Tho-Tci)) if abs((Thi-Tco)-(Tho-Tci))>0.1 else (Thi-Tco)
            Area = np.pi * inputs['tube_od'] * inputs['length'] * inputs['n_tubes']
            Q_new = U_dirty * Area * LMTD
            
            # Update Temps
            Tho = Thi - Q_new / (m_h * cp_h)
            Tco = Tci + Q_new / (m_c * cp_c)
            
            if abs(Q_new - Q_total) < 100: break
            Q_total = (Q_total + Q_new)/2
            
        return {
            'Q': Q_new, 'U': U_dirty, 'Area': Area, 
            'T_hot_out': Tho, 'T_cold_out': Tco,
            'v_tube': vt, 'v_shell': vs,
            'Re_tube': Re_t, 'Re_shell': Re_s
        }

