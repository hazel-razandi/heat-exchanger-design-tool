"""
Pressure Drop Calculation Module
Calculates pressure drop and pumping power requirements for heat exchangers.
"""

import numpy as np


class PressureDropCalculator:
    """
    Calculate pressure drop for various heat exchanger configurations.
    """
    
    def __init__(self, hx_type='Shell-and-Tube'):
        """
        Initialize pressure drop calculator.
        
        Args:
            hx_type (str): Type of heat exchanger
        """
        self.hx_type = hx_type
    
    def calculate_reynolds_number(self, velocity, diameter, density, viscosity):
        """
        Calculate Reynolds number.
        
        Args:
            velocity (float): Fluid velocity (m/s)
            diameter (float): Hydraulic diameter (m)
            density (float): Fluid density (kg/m³)
            viscosity (float): Dynamic viscosity (Pa·s)
            
        Returns:
            float: Reynolds number
        """
        Re = (density * velocity * diameter) / viscosity
        return Re
    
    def calculate_friction_factor(self, reynolds_number, roughness=0.000045, diameter=0.025):
        """
        Calculate Darcy friction factor.
        
        Args:
            reynolds_number (float): Reynolds number
            roughness (float): Surface roughness (m), default for commercial steel
            diameter (float): Pipe diameter (m)
            
        Returns:
            float: Darcy friction factor
        """
        # Relative roughness
        epsilon = roughness / diameter
        
        if reynolds_number < 2300:
            # Laminar flow
            f = 64 / reynolds_number
        elif reynolds_number < 4000:
            # Transitional - interpolate
            f_lam = 64 / 2300
            f_turb = self._colebrook_white(4000, epsilon)
            # Linear interpolation
            f = f_lam + (f_turb - f_lam) * (reynolds_number - 2300) / (4000 - 2300)
        else:
            # Turbulent flow - Colebrook-White equation
            f = self._colebrook_white(reynolds_number, epsilon)
        
        return f
    
    def _colebrook_white(self, Re, epsilon, max_iter=50):
        """
        Solve Colebrook-White equation iteratively.
        
        Args:
            Re (float): Reynolds number
            epsilon (float): Relative roughness (epsilon/D)
            max_iter (int): Maximum iterations
            
        Returns:
            float: Friction factor
        """
        # Initial guess using Swamee-Jain approximation
        f = 0.25 / (np.log10(epsilon/3.7 + 5.74/Re**0.9))**2
        
        # Iterative solution
        for _ in range(max_iter):
            f_new = 1 / (-2 * np.log10(epsilon/3.7 + 2.51/(Re * np.sqrt(f))))**2
            if abs(f_new - f) < 1e-6:
                break
            f = f_new
        
        return f
    
    def calculate_tube_side_pressure_drop(self, mass_flow, density, viscosity, 
                                         tube_diameter, tube_length, n_tubes, n_passes):
        """
        Calculate tube-side pressure drop for shell-and-tube exchanger.
        
        Args:
            mass_flow (float): Mass flow rate (kg/s)
            density (float): Fluid density (kg/m³)
            viscosity (float): Dynamic viscosity (Pa·s)
            tube_diameter (float): Inner tube diameter (m)
            tube_length (float): Tube length (m)
            n_tubes (int): Number of tubes
            n_passes (int): Number of tube passes
            
        Returns:
            dict: Pressure drop results
        """
        # Flow area per pass
        tubes_per_pass = n_tubes / n_passes
        flow_area = tubes_per_pass * np.pi * (tube_diameter/2)**2
        
        # Velocity
        velocity = mass_flow / (density * flow_area)
        
        # Reynolds number
        Re = self.calculate_reynolds_number(velocity, tube_diameter, density, viscosity)
        
        # Friction factor
        f = self.calculate_friction_factor(Re, diameter=tube_diameter)
        
        # Pressure drop due to friction (Darcy-Weisbach)
        dP_friction = f * (tube_length * n_passes / tube_diameter) * (density * velocity**2 / 2)
        
        # Entrance/exit losses (4 velocity heads per pass)
        dP_minor = 4 * n_passes * (density * velocity**2 / 2)
        
        # Total pressure drop
        dP_total = dP_friction + dP_minor
        
        # Convert to kPa
        dP_total_kPa = dP_total / 1000
        
        return {
            'pressure_drop_Pa': dP_total,
            'pressure_drop_kPa': dP_total_kPa,
            'pressure_drop_psi': dP_total_kPa * 0.145,
            'velocity_m_s': velocity,
            'reynolds_number': Re,
            'friction_factor': f,
            'flow_regime': self._get_flow_regime(Re)
        }
    
    def calculate_shell_side_pressure_drop(self, mass_flow, density, viscosity,
                                          shell_diameter, tube_diameter, n_tubes, 
                                          baffle_spacing, n_baffles):
        """
        Calculate shell-side pressure drop (simplified).
        
        Args:
            mass_flow (float): Mass flow rate (kg/s)
            density (float): Fluid density (kg/m³)
            viscosity (float): Dynamic viscosity (Pa·s)
            shell_diameter (float): Shell inner diameter (m)
            tube_diameter (float): Outer tube diameter (m)
            n_tubes (int): Number of tubes
            baffle_spacing (float): Distance between baffles (m)
            n_baffles (int): Number of baffles
            
        Returns:
            dict: Pressure drop results
        """
        # Flow area (simplified - shell area minus tube area)
        shell_area = np.pi * (shell_diameter/2)**2
        tube_area = n_tubes * np.pi * (tube_diameter/2)**2
        flow_area = shell_area - tube_area
        
        # Equivalent diameter
        D_eq = 4 * flow_area / (n_tubes * np.pi * tube_diameter)
        
        # Velocity
        velocity = mass_flow / (density * flow_area)
        
        # Reynolds number
        Re = self.calculate_reynolds_number(velocity, D_eq, density, viscosity)
        
        # Friction factor (higher for shell side due to baffles)
        f = self.calculate_friction_factor(Re, diameter=D_eq) * 1.5
        
        # Total flow length
        flow_length = baffle_spacing * n_baffles
        
        # Pressure drop
        dP_total = f * (flow_length / D_eq) * (density * velocity**2 / 2)
        
        # Convert to kPa
        dP_total_kPa = dP_total / 1000
        
        return {
            'pressure_drop_Pa': dP_total,
            'pressure_drop_kPa': dP_total_kPa,
            'pressure_drop_psi': dP_total_kPa * 0.145,
            'velocity_m_s': velocity,
            'reynolds_number': Re,
            'friction_factor': f,
            'flow_regime': self._get_flow_regime(Re)
        }
    
    def calculate_pumping_power(self, mass_flow, pressure_drop_Pa, density, efficiency=0.7):
        """
        Calculate required pumping power.
        
        Args:
            mass_flow (float): Mass flow rate (kg/s)
            pressure_drop_Pa (float): Pressure drop (Pa)
            density (float): Fluid density (kg/m³)
            efficiency (float): Pump efficiency (0-1), default 0.7
            
        Returns:
            dict: Pumping power results
        """
        # Volume flow rate
        volume_flow = mass_flow / density  # m³/s
        
        # Hydraulic power
        power_hydraulic = volume_flow * pressure_drop_Pa / 1000  # kW
        
        # Actual power (accounting for efficiency)
        power_actual = power_hydraulic / efficiency  # kW
        
        # Convert to HP
        power_hp = power_actual * 1.341
        
        return {
            'hydraulic_power_kW': power_hydraulic,
            'actual_power_kW': power_actual,
            'actual_power_HP': power_hp,
            'volume_flow_m3_s': volume_flow,
            'volume_flow_GPM': volume_flow * 15850.3,
            'pump_efficiency': efficiency
        }
    
    def calculate_annual_pumping_cost(self, power_kW, hours_per_year=8760, 
                                     electricity_rate=0.10):
        """
        Calculate annual cost of pumping.
        
        Args:
            power_kW (float): Pump power (kW)
            hours_per_year (float): Operating hours per year
            electricity_rate (float): Electricity cost ($/kWh)
            
        Returns:
            dict: Cost results
        """
        # Annual energy consumption
        energy_kWh = power_kW * hours_per_year
        
        # Annual cost
        annual_cost = energy_kWh * electricity_rate
        
        return {
            'annual_energy_kWh': energy_kWh,
            'annual_cost_USD': annual_cost,
            'monthly_cost_USD': annual_cost / 12,
            'electricity_rate': electricity_rate,
            'operating_hours': hours_per_year
        }
    
    def _get_flow_regime(self, reynolds_number):
        """
        Determine flow regime from Reynolds number.
        
        Args:
            reynolds_number (float): Reynolds number
            
        Returns:
            str: Flow regime
        """
        if reynolds_number < 2300:
            return 'Laminar'
        elif reynolds_number < 4000:
            return 'Transitional'
        else:
            return 'Turbulent'
    
    def estimate_geometry_from_area(self, area, hx_type='Shell-and-Tube'):
        """
        Estimate heat exchanger geometry from total area.
        
        Args:
            area (float): Total heat transfer area (m²)
            hx_type (str): Type of heat exchanger
            
        Returns:
            dict: Estimated geometry
        """
        if hx_type == 'Shell-and-Tube':
            # Typical values for shell-and-tube
            tube_diameter = 0.025  # 25mm (1 inch) outer diameter
            tube_length = 4.0  # 4 meters typical
            
            # Area per tube
            area_per_tube = np.pi * tube_diameter * tube_length
            
            # Number of tubes
            n_tubes = int(area / area_per_tube)
            
            # Shell diameter (rule of thumb)
            shell_diameter = tube_diameter * np.sqrt(n_tubes) * 1.3
            
            # Number of passes (typically 2 or 4)
            n_passes = 2 if n_tubes < 200 else 4
            
            # Baffles (one every 0.5m typically)
            baffle_spacing = 0.5
            n_baffles = int(tube_length / baffle_spacing) - 1
            
            return {
                'tube_diameter_inner': 0.022,  # m (22mm ID)
                'tube_diameter_outer': tube_diameter,  # m
                'tube_length': tube_length,  # m
                'n_tubes': n_tubes,
                'n_passes': n_passes,
                'shell_diameter': shell_diameter,  # m
                'baffle_spacing': baffle_spacing,  # m
                'n_baffles': n_baffles
            }
        
        elif hx_type == 'Plate':
            # Typical values for plate heat exchanger
            plate_area = 0.3  # m² per plate (typical)
            n_plates = int(area / plate_area)
            
            # Channel spacing
            channel_spacing = 0.003  # 3mm typical
            
            return {
                'n_plates': n_plates,
                'plate_area': plate_area,
                'channel_spacing': channel_spacing,
                'plate_width': 0.5,  # m
                'plate_height': 0.6  # m
            }
        
        else:
            return {}


# Testing
if __name__ == "__main__":
    print("Testing Pressure Drop Calculator\n")
    print("="*70)
    
    calc = PressureDropCalculator()
    
    # Test case: Water through shell-and-tube
    print("\nTest: Water through 12.4 m² shell-and-tube heat exchanger")
    print("-"*70)
    
    # Estimate geometry
    geometry = calc.estimate_geometry_from_area(12.4)
    print(f"\nEstimated Geometry:")
    print(f"  Tubes: {geometry['n_tubes']}")
    print(f"  Tube length: {geometry['tube_length']} m")
    print(f"  Shell diameter: {geometry['shell_diameter']:.3f} m")
    
    # Tube side pressure drop
    tube_results = calc.calculate_tube_side_pressure_drop(
        mass_flow=2.0,  # kg/s
        density=997,  # kg/m³ (water)
        viscosity=0.00089,  # Pa·s (water at 25°C)
        tube_diameter=geometry['tube_diameter_inner'],
        tube_length=geometry['tube_length'],
        n_tubes=geometry['n_tubes'],
        n_passes=geometry['n_passes']
    )
    
    print(f"\nTube Side Results:")
    print(f"  Pressure drop: {tube_results['pressure_drop_kPa']:.2f} kPa ({tube_results['pressure_drop_psi']:.2f} psi)")
    print(f"  Velocity: {tube_results['velocity_m_s']:.2f} m/s")
    print(f"  Reynolds: {tube_results['reynolds_number']:.0f} ({tube_results['flow_regime']})")
    
    # Pumping power
    pump_results = calc.calculate_pumping_power(
        mass_flow=2.0,
        pressure_drop_Pa=tube_results['pressure_drop_Pa'],
        density=997
    )
    
    print(f"\nPumping Power:")
    print(f"  Required: {pump_results['actual_power_kW']:.3f} kW ({pump_results['actual_power_HP']:.2f} HP)")
    
    # Annual cost
    cost_results = calc.calculate_annual_pumping_cost(
        power_kW=pump_results['actual_power_kW']
    )
    
    print(f"\nAnnual Operating Cost:")
    print(f"  Energy: {cost_results['annual_energy_kWh']:.0f} kWh/year")
    print(f"  Cost: ${cost_results['annual_cost_USD']:.2f}/year (${cost_results['monthly_cost_USD']:.2f}/month)")
    print("\n" + "="*70)
