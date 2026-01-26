"""
Physics Correlations Library (Kern / Gnielinski)
"""
import numpy as np

class Correlations:
    
    @staticmethod
    def friction_factor_turbulent(Re, rel_roughness):
        """Haaland Equation for Friction Factor"""
        if Re < 2300: return 64.0 / max(Re, 1)
        term = (rel_roughness/3.7)**1.11 + 6.9/Re
        return (-1.8 * np.log10(term))**-2

    @staticmethod
    def nusselt_gnielinski(Re, Pr, f):
        """Gnielinski Correlation (Accurate for Tube Side)"""
        if Re < 2300: return 3.66 # Laminar approx
        num = (f/8) * (Re - 1000) * Pr
        den = 1 + 12.7 * (f/8)**0.5 * (Pr**(2/3) - 1)
        return num / den

    @staticmethod
    def kern_shell_side_Nu(Re_s, Pr, baffle_cut_pct):
        """Kern Method for Shell-Side Heat Transfer"""
        # Simplified jH factor for standard baffles
        jH = 0.2 * (Re_s ** -0.4) # Valid for 2k < Re < 1M
        return jH * Re_s * (Pr ** 0.33)

    @staticmethod
    def kern_shell_pressure(Re_s, Ds, De, N_baff, pitch):
        """Kern Method for Shell-Side Friction"""
        # Friction factor fit
        f_s = np.exp(0.576 - 0.19 * np.log(Re_s))
        return f_s
