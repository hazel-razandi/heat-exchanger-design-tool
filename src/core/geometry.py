import numpy as np

class GeometryEngine:
    def __init__(self, inputs):
        self.inputs = inputs
        self.shell_id = inputs.get('shell_id', 0.6)
        self.tube_od = inputs.get('tube_od', 0.019)
        self.length = inputs.get('length', 3.0)
        self.pitch_ratio = inputs.get('pitch_ratio', 1.25)
        self.layout = inputs.get('tube_layout', 'Triangular')
        self.tema_type = inputs.get('tema_type', 'BEM')
        self.baffle_spacing = inputs.get('baffle_spacing', 0.3)
        self.baffle_cut = inputs.get('baffle_cut', 25) / 100.0 # Convert % to decimal

    def get_tube_count_correction(self):
        """
        Adjusts tube count based on TEMA type.
        Floating heads (AES/AET) lose space compared to Fixed (BEM).
        """
        base_tubes = self.inputs.get('n_tubes', 100)
        
        if self.tema_type in ['AES', 'AET', 'BET']:
            return int(base_tubes * 0.85) # Penalty for floating head clearance
        elif self.tema_type == 'U-Tube':
            return int(base_tubes * 0.90) # Penalty for bend radius
        
        return base_tubes # BEM (Fixed)

    def get_tube_area(self):
        """Calculates total flow area inside tubes per pass."""
        di = self.tube_od - 2*0.00211 # approx wall thickness (Average BWG 14)
        area_one = np.pi * di**2 / 4
        
        n_passes = int(self.inputs.get('n_passes', 1))
        real_tubes = self.get_tube_count_correction()
        
        return (real_tubes / n_passes) * area_one

    def get_shell_area(self):
        """
        Calculates Shell Side Crossflow Area (As) using Kern's Method.
        As = (ID * C * B) / Pt
        This fixes the '306 m/s' velocity error by using real clearance.
        """
        pt = self.tube_od * self.pitch_ratio
        clearance = pt - self.tube_od
        
        # Area = (Shell_ID * Clearance * Baffle_Spacing) / Pitch
        area_shell = (self.shell_id * clearance * self.baffle_spacing) / pt
        
        # Safety clamp: prevent division by zero or microscopic areas
        return max(area_shell, 0.001)

    def get_hydraulic_diam(self):
        """Calculates Equivalent Diameter (De) for Shell Side."""
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

    def get_heat_transfer_area(self):
        """Total external surface area for heat transfer."""
        real_tubes = self.get_tube_count_correction()
        return real_tubes * np.pi * self.tube_od * self.length
