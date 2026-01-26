import numpy as np

class GeometryEngine:
    def __init__(self, inputs):
        self.Ds = inputs['shell_id']
        self.do = inputs['tube_od']
        self.Pt = inputs['tube_od'] * inputs['pitch_ratio']
        self.Lc = inputs['baffle_spacing']
        self.nt = inputs['n_tubes']
        self.passes = inputs['n_passes']

    def get_tube_area(self):
        """Flow area inside tubes (per pass)"""
        di = self.do - 0.002 # Assume 1mm wall
        total_area = (np.pi * di**2 / 4) * self.nt
        return total_area / self.passes

    def get_shell_area(self):
        """Crossflow area at shell center (Kern)"""
        clearance = self.Pt - self.do
        return (self.Ds * clearance * self.Lc) / self.Pt

    def get_hydraulic_diam(self):
        """Equivalent diameter for shell side"""
        num = 1.10 * (self.Pt**2) - 0.917 * (self.do**2)
        return (4 * num) / (np.pi * self.do)

