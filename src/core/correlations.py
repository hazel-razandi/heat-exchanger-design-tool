import numpy as np

class Correlations:
    @staticmethod
    def friction_factor(Re, rel_roughness):
        """Haaland Equation for Turbulent Friction"""
        if Re < 2300: return 64.0 / max(Re, 1)
        term = (rel_roughness/3.7)**1.11 + 6.9/Re
        return (-1.8 * np.log10(term))**-2

    @staticmethod
    def nusselt_gnielinski(Re, Pr, f):
        """Gnielinski Correlation (Valid for Re > 3000)"""
        if Re < 2300: return 3.66
        num = (f/8) * (Re - 1000) * Pr
        den = 1 + 12.7 * (f/8)**0.5 * (Pr**(2/3) - 1)
        return num / den

    @staticmethod
    def kern_shell_side(Re_s, Pr, baffle_cut):
        """Kern Method for Shell-Side Heat Transfer"""
        jH = 0.2 * (Re_s ** -0.4) 
        return jH * Re_s * (Pr ** 0.33)

