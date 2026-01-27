import numpy as np

class GeometryEngine:
    def __init__(self, inputs):
        self.inputs = inputs
        self.shell_id = inputs.get('shell_id', 0.6)
        self.tube_od = inputs.get('tube_od', 0.019)
        self.pitch_ratio = inputs.get('pitch_ratio', 1.25)
        self.layout = inputs.get('tube_layout', 'Triangular') # New Input
        self.tema_type = inputs.get('tema_type', 'BEM')       # New Input

    def get_tube_count_correction(self):
        """
        Adjusts tube count based on TEMA type.
        Floating heads (AES/AET) lose space compared to Fixed (BEM).
        """
        base_tubes = self.inputs.get('n_tubes', 100)
        
        if self.tema_type in ['AES', 'AET', 'BET']:
            # Floating heads need massive clearance, reducing tube count capacity
            return int(base_tubes * 0.85) 
        elif self.tema_type == 'U-Tube':
            # U-Tubes lose the center rows
            return int(base_tubes * 0.90)
        
        return base_tubes # BEM / NEN (Fixed)

    def get_tube_area(self):
        # Flow area per tube
        di = self.tube_od - 2*0.002 # approx wall
        area_one = np.pi * di**2 / 4
        
        # Total flow area = (N_tubes / N_passes) * area_one
        n_passes = self.inputs.get('n_passes', 1)
        real_tubes = self.get_tube_count_correction()
        
        return (real_tubes / n_passes) * area_one

    def get_shell_area(self):
        # Kern Method for Shell Area
        # As = (ID * C * B) / Pt
        # C = Clearance between tubes
        pt = self.tube_od * self.pitch_ratio
        clearance = pt - self.tube_od
        b_space = self.inputs.get('baffle_spacing', 0.3)
        
        return (self.shell_id * clearance * b_space) / pt

    def get_hydraulic_diam(self):
        # Equivalent Diameter based on Layout
        do = self.tube_od
        pt = do * self.pitch_ratio
        
        if self.layout == 'Square' or self.layout == 'Rotated Square':
            # De = 4 * (Pt^2 - pi*do^2/4) / (pi*do)
            num = (pt**2) - (np.pi * do**2 / 4)
            den = np.pi * do
            return 4 * num / den
        else:
            # Triangular (Default)
            # De = 4 * (0.433*Pt^2 - 0.5*pi*do^2/4) / (0.5*pi*do)
            num = (0.433 * pt**2) - (0.5 * np.pi * do**2 / 4)
            den = 0.5 * np.pi * do
            return 4 * num / den
