"""
Hydraulic Analysis & Safety (API 660/661)
Author: KAKAROTONCLOUD
Version: 3.0.0 Enterprise
"""
import numpy as np

class PressureDropCalculator:
    def __init__(self, hx_config='Shell-and-Tube (BEM)'):
        self.config = hx_config

    def estimate_geometry_from_area(self, area, config):
        """
        Intelligent geometry estimation based on industrial norms.
        """
        if not area or area <= 0: area = 1.0
        
        # Standard Tubing: 3/4" OD (19.05mm), 14 BWG
        od = 0.01905 
        length = 6.0 # Standard 20ft tube
        
        # Surface area per tube
        surf_per_tube = np.pi * od * length
        n_tubes = int(np.ceil(area / surf_per_tube))
        
        return {
            'tube_od': od, 
            'tube_id': 0.01483, # 14 BWG wall
            'length': length, 
            'n_tubes': max(1, n_tubes)
        }

    def calculate_tube_side_pressure_drop(self, m_dot, rho, mu, d_id, length, n_tubes, passes=2):
        """
        Calculates DP and checks against API erosion limits.
        """
        alerts = []
        try:
            # Flow Area (Total tubes / passes)
            tubes_per_pass = max(1, n_tubes / passes)
            flow_area = tubes_per_pass * (np.pi * (d_id/2)**2)
            
            # Velocity Calculation
            velocity = m_dot / (rho * flow_area)
            
            # API 660/661 Safety Checks
            if velocity > 3.0:
                alerts.append(f"High Velocity ({velocity:.2f} m/s). Exceeds API erosion limit (3.0 m/s).")
            elif velocity < 0.9:
                alerts.append(f"Low Velocity ({velocity:.2f} m/s). Risk of fouling/sedimentation.")
            
            # Reynolds Number
            Re = (rho * velocity * d_id) / mu if mu > 0 else 1000
            
            # Darcy Friction Factor (Haaland Equation)
            # Assuming commercial steel roughness (epsilon = 4.5e-5)
            epsilon = 4.5e-5
            rel_rough = epsilon / d_id
            
            if Re < 2300:
                f = 64 / Re
                regime = "Laminar"
            else:
                # Turbulent approximation
                f = 0.316 * Re**(-0.25)
                regime = "Turbulent"

            # Pressure Drop (Friction + Returns)
            # 2.5 velocity heads per pass for return losses
            dp_fric = f * (length / d_id) * (rho * velocity**2) / 2
            dp_return = 2.5 * (rho * velocity**2) / 2
            
            total_dp = (dp_fric + dp_return) * passes
            
            return {
                'pressure_drop_kPa': total_dp / 1000,
                'velocity_m_s': velocity,
                'reynolds': Re,
                'regime': regime,
                'alerts': alerts
            }
        except Exception:
            return {'pressure_drop_kPa': 0, 'velocity_m_s': 0, 'reynolds': 0, 'regime': 'N/A', 'alerts': ['Calculation Failed']}
