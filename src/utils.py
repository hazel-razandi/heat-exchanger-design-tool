"""
Utility Functions Module
Helper functions for unit conversions, validations, and formatting.
"""

import numpy as np
from datetime import datetime


# ============================================================================
# UNIT CONVERSIONS
# ============================================================================

def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9/5) + 32


def fahrenheit_to_celsius(fahrenheit):
    """Convert Fahrenheit to Celsius."""
    return (fahrenheit - 32) * 5/9


def celsius_to_kelvin(celsius):
    """Convert Celsius to Kelvin."""
    return celsius + 273.15


def kelvin_to_celsius(kelvin):
    """Convert Kelvin to Celsius."""
    return kelvin - 273.15


def kw_to_btu_per_hour(kw):
    """Convert kW to BTU/hr."""
    return kw * 3412.14


def btu_per_hour_to_kw(btu_hr):
    """Convert BTU/hr to kW."""
    return btu_hr / 3412.14


def square_meters_to_square_feet(m2):
    """Convert m² to ft²."""
    return m2 * 10.7639


def square_feet_to_square_meters(ft2):
    """Convert ft² to m²."""
    return ft2 / 10.7639


def kg_per_s_to_lb_per_hr(kg_s):
    """Convert kg/s to lb/hr."""
    return kg_s * 7936.64


def lb_per_hr_to_kg_per_s(lb_hr):
    """Convert lb/hr to kg/s."""
    return lb_hr / 7936.64


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_temperatures(T_hot_in, T_hot_out, T_cold_in, T_cold_out, flow_type='Counter Flow'):
    """
    Validate heat exchanger temperatures for thermodynamic feasibility.
    
    Args:
        T_hot_in (float): Hot fluid inlet temperature (°C)
        T_hot_out (float): Hot fluid outlet temperature (°C)
        T_cold_in (float): Cold fluid inlet temperature (°C)
        T_cold_out (float): Cold fluid outlet temperature (°C)
        flow_type (str): 'Counter Flow' or 'Parallel Flow'
        
    Returns:
        tuple: (is_valid, error_message)
    """
    errors = []
    
    # Check that hot fluid cools down
    if T_hot_in <= T_hot_out:
        errors.append("Hot fluid inlet temperature must be greater than outlet temperature")
    
    # Check that cold fluid heats up
    if T_cold_out <= T_cold_in:
        errors.append("Cold fluid outlet temperature must be greater than inlet temperature")
    
    # Check Second Law of Thermodynamics
    if T_hot_out < T_cold_in:
        errors.append("Hot fluid outlet cannot be colder than cold fluid inlet (violates 2nd Law)")
    
    if T_cold_out > T_hot_in:
        errors.append("Cold fluid outlet cannot be hotter than hot fluid inlet (violates 2nd Law)")
    
    # Counter flow specific check
    if flow_type == 'Counter Flow':
        # In counter flow, temperatures can cross but must maintain proper relationship
        if T_hot_out < T_cold_in:
            errors.append("Temperature crossover violation in counter flow")
    
    # Parallel flow specific check
    if flow_type == 'Parallel Flow':
        # In parallel flow, hot outlet must be > cold outlet
        if T_hot_out < T_cold_out:
            errors.append("In parallel flow, hot outlet must be warmer than cold outlet")
    
    is_valid = len(errors) == 0
    error_message = "; ".join(errors) if errors else "Valid"
    
    return is_valid, error_message


def validate_positive(value, name):
    """
    Validate that a value is positive.
    
    Args:
        value (float): Value to check
        name (str): Name of the parameter
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if value <= 0:
        return False, f"{name} must be positive (got {value})"
    return True, "Valid"


def validate_range(value, name, min_val, max_val):
    """
    Validate that a value is within a range.
    
    Args:
        value (float): Value to check
        name (str): Name of the parameter
        min_val (float): Minimum allowed value
        max_val (float): Maximum allowed value
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if value < min_val or value > max_val:
        return False, f"{name} must be between {min_val} and {max_val} (got {value})"
    return True, "Valid"


# ============================================================================
# HEAT TRANSFER CALCULATIONS
# ============================================================================

def calculate_reynolds_number(velocity, diameter, density, viscosity):
    """
    Calculate Reynolds number.
    
    Args:
        velocity (float): Fluid velocity (m/s)
        diameter (float): Characteristic diameter (m)
        density (float): Fluid density (kg/m³)
        viscosity (float): Dynamic viscosity (Pa·s)
        
    Returns:
        float: Reynolds number (dimensionless)
    """
    Re = (density * velocity * diameter) / viscosity
    return Re


def determine_flow_regime(reynolds_number):
    """
    Determine flow regime based on Reynolds number.
    
    Args:
        reynolds_number (float): Reynolds number
        
    Returns:
        str: Flow regime ('Laminar', 'Transitional', or 'Turbulent')
    """
    if reynolds_number < 2300:
        return 'Laminar'
    elif reynolds_number < 4000:
        return 'Transitional'
    else:
        return 'Turbulent'


# ============================================================================
# TEMPERATURE PROFILE GENERATION
# ============================================================================

def generate_temperature_profile(T_hot_in, T_hot_out, T_cold_in, T_cold_out, 
                                 flow_type='Counter Flow', num_points=100):
    """
    Generate temperature profile data for visualization.
    
    Args:
        T_hot_in (float): Hot fluid inlet temperature
        T_hot_out (float): Hot fluid outlet temperature
        T_cold_in (float): Cold fluid inlet temperature
        T_cold_out (float): Cold fluid outlet temperature
        flow_type (str): 'Counter Flow' or 'Parallel Flow'
        num_points (int): Number of points to generate
        
    Returns:
        tuple: (x_positions, hot_temps, cold_temps)
    """
    x = np.linspace(0, 1, num_points)
    
    # Hot fluid temperature (always decreases from inlet to outlet)
    T_hot = T_hot_in - (T_hot_in - T_hot_out) * x
    
    if flow_type == 'Counter Flow':
        # Cold fluid flows opposite direction
        T_cold = T_cold_out - (T_cold_out - T_cold_in) * x
    else:  # Parallel Flow
        # Cold fluid flows same direction
        T_cold = T_cold_in + (T_cold_out - T_cold_in) * x
    
    return x, T_hot, T_cold


# ============================================================================
# FORMATTING AND OUTPUT
# ============================================================================

def format_result_string(results, units='metric'):
    """
    Format results dictionary into readable string.
    
    Args:
        results (dict): Dictionary of calculation results
        units (str): 'metric' or 'imperial'
        
    Returns:
        str: Formatted results string
    """
    output = []
    output.append("="*60)
    output.append("HEAT EXCHANGER DESIGN RESULTS")
    output.append("="*60)
    output.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")
    
    # Configuration
    output.append("CONFIGURATION:")
    output.append(f"  Flow Type: {results.get('flow_type', 'N/A')}")
    output.append(f"  Method: {results.get('method', 'N/A')}")
    output.append("")
    
    # Temperatures
    output.append("TEMPERATURES:")
    if units == 'metric':
        output.append(f"  Hot Inlet:     {results.get('T_hot_in', 0):.1f} °C")
        output.append(f"  Hot Outlet:    {results.get('T_hot_out', 0):.1f} °C")
        output.append(f"  Cold Inlet:    {results.get('T_cold_in', 0):.1f} °C")
        output.append(f"  Cold Outlet:   {results.get('T_cold_out', 0):.1f} °C")
    else:
        output.append(f"  Hot Inlet:     {celsius_to_fahrenheit(results.get('T_hot_in', 0)):.1f} °F")
        output.append(f"  Hot Outlet:    {celsius_to_fahrenheit(results.get('T_hot_out', 0)):.1f} °F")
        output.append(f"  Cold Inlet:    {celsius_to_fahrenheit(results.get('T_cold_in', 0)):.1f} °F")
        output.append(f"  Cold Outlet:   {celsius_to_fahrenheit(results.get('T_cold_out', 0)):.1f} °F")
    output.append("")
    
    # Performance
    output.append("PERFORMANCE:")
    if units == 'metric':
        output.append(f"  Heat Transfer Rate: {results.get('Q', 0):.2f} kW")
        output.append(f"  Required Area:      {results.get('area', 0):.2f} m²")
    else:
        output.append(f"  Heat Transfer Rate: {kw_to_btu_per_hour(results.get('Q', 0)):.0f} BTU/hr")
        output.append(f"  Required Area:      {square_meters_to_square_feet(results.get('area', 0)):.2f} ft²")
    
    output.append(f"  Effectiveness:      {results.get('effectiveness', 0)*100:.1f} %")
    output.append(f"  NTU:                {results.get('NTU', 0):.2f}")
    
    if 'LMTD' in results:
        if units == 'metric':
            output.append(f"  LMTD:               {results.get('LMTD', 0):.2f} °C")
        else:
            output.append(f"  LMTD:               {results.get('LMTD', 0)*9/5:.2f} °F")
    
    output.append("")
    output.append("="*60)
    
    return "\n".join(output)


def create_comparison_table(results_list, labels):
    """
    Create comparison table for multiple designs.
    
    Args:
        results_list (list): List of result dictionaries
        labels (list): List of labels for each design
        
    Returns:
        str: Formatted comparison table
    """
    output = []
    output.append("="*80)
    output.append("DESIGN COMPARISON")
    output.append("="*80)
    
    # Header
    header = f"{'Parameter':<25}"
    for label in labels:
        header += f"{label:<15}"
    output.append(header)
    output.append("-"*80)
    
    # Data rows
    params = [
        ('Heat Transfer (kW)', 'Q'),
        ('Area (m²)', 'area'),
        ('Effectiveness (%)', 'effectiveness'),
        ('NTU', 'NTU'),
        ('LMTD (°C)', 'LMTD')
    ]
    
    for param_name, param_key in params:
        row = f"{param_name:<25}"
        for results in results_list:
            value = results.get(param_key, 0)
            if param_key == 'effectiveness':
                row += f"{value*100:<15.1f}"
            else:
                row += f"{value:<15.2f}"
        output.append(row)
    
    output.append("="*80)
    return "\n".join(output)


# ============================================================================
# ENERGY BALANCE CHECK
# ============================================================================

def check_energy_balance(Q_hot, Q_cold, tolerance=0.05):
    """
    Check if energy balance is satisfied.
    
    Args:
        Q_hot (float): Heat removed from hot fluid (kW)
        Q_cold (float): Heat added to cold fluid (kW)
        tolerance (float): Acceptable relative difference (default 5%)
        
    Returns:
        tuple: (is_balanced, relative_error)
    """
    if Q_hot == 0:
        return False, float('inf')
    
    relative_error = abs(Q_hot - Q_cold) / Q_hot
    is_balanced = relative_error <= tolerance
    
    return is_balanced, relative_error


# Testing
if __name__ == "__main__":
    print("Testing Utility Functions\n")
    print("="*60)
    
    # Test unit conversions
    print("Unit Conversions:")
    print(f"  25°C = {celsius_to_fahrenheit(25):.1f}°F")
    print(f"  100 kW = {kw_to_btu_per_hour(100):.0f} BTU/hr")
    print(f"  10 m² = {square_meters_to_square_feet(10):.2f} ft²")
    
    # Test temperature validation
    print("\n" + "="*60)
    print("Temperature Validation:")
    valid, msg = validate_temperatures(90, 50, 25, 45, 'Counter Flow')
    print(f"  Valid: {valid}, Message: {msg}")
    
    # Test temperature profile
    print("\n" + "="*60)
    print("Temperature Profile Generation:")
    x, T_hot, T_cold = generate_temperature_profile(90, 50, 25, 45)
    print(f"  Generated {len(x)} points")
    print(f"  Hot: {T_hot[0]:.1f}°C → {T_hot[-1]:.1f}°C")
    print(f"  Cold: {T_cold[0]:.1f}°C → {T_cold[-1]:.1f}°C")
