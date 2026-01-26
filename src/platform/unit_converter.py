# Conversion Factors (to Metric)
FACTORS = {
    'len_in_m': 0.0254,      # Inches to Meters
    'len_ft_m': 0.3048,      # Feet to Meters
    'mass_lb_kg': 0.453592,  # lb to kg
    'temp_f_c': lambda f: (f - 32) * 5/9,
    'press_psi_pa': 6894.76
}

def to_metric(val, unit_type):
    if unit_type == 'in': return val * FACTORS['len_in_m']
    if unit_type == 'ft': return val * FACTORS['len_ft_m']
    if unit_type == 'lb': return val * FACTORS['mass_lb_kg']
    if unit_type == 'F': return FACTORS['temp_f_c'](val)
    return val

def format_metric(val, unit_name, is_metric=True):
    """Formats output for display based on selected unit system"""
    if is_metric:
        return val # Already metric
    
    # Convert Metric -> Imperial for Display
    if unit_name == 'mm': return val / 25.4 # mm to inch
    if unit_name == 'm': return val / 0.3048 # m to ft
    if unit_name == 'C': return (val * 9/5) + 32 # C to F
    if unit_name == 'kW': return val * 3412.14 # kW to Btu/hr
    
    return val

