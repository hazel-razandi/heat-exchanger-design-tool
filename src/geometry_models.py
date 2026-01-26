"""
Geometric Modeling Engine
"""
import numpy as np

class ShellGeometry:
    def __init__(self, shell_id, n_tubes, tube_od, pitch_ratio, baffle_spacing):
        self.Ds = shell_id
        self.do = tube_od
        self.Pt = tube_od * pitch_ratio
        self.Lc = baffle_spacing

    def get_shell_side_area(self):
        """Calculates Crossflow Area (As)"""
        clearance = self.Pt - self.do
        return (self.Ds * clearance * self.Lc) / self.Pt

    def get_equiv_diameter(self):
        """Hydraulic Diameter (De) for Triangular Pitch"""
        num = 1.10 * (self.Pt**2) - 0.917 * (self.do**2)
        return (4 * num) / (np.pi * self.do)

