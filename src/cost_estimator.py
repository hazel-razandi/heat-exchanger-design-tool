"""
AACE Class 4 Cost Estimator
Author: KAKAROTONCLOUD
Version: 3.0.0 Enterprise
"""
from src.hx_types import EngineeringDB

class CostEstimator:
    """
    Generates preliminary capital cost estimates (+/- 30% accuracy).
    Based on AACE International standards for process equipment.
    """
    
    def estimate_project_budget(self, area, hx_config, material_name):
        # 1. Base Equipment Cost (Carbon Steel Reference)
        # Using a power-law sizing model: Cost = Base * (Area)^0.65
        # Calibrated to 2024 Market Rates (approx $12,000 for a small unit)
        if area < 1: area = 1.0
        base_fob = 12500 * (area ** 0.65)
        
        # 2. Material Multiplier
        mat_data = EngineeringDB.get_properties(material_name)
        mat_factor = mat_data.get('cost_factor', 1.0)
        
        # 3. Pressure/Type Multiplier
        type_factor = 1.0
        if "Plate" in hx_config: type_factor = 0.75 # Plates typically cheaper per m2
        if "Double Pipe" in hx_config: type_factor = 1.4 # Heavy wall thickness
        
        # Calculate Equipment FOB (Free on Board)
        equipment_cost = base_fob * mat_factor * type_factor
        
        # 4. Lang Factors (Total Installed Cost Breakdown)
        # Standard factors for fluid processing plants
        installation_labor = equipment_cost * 0.45
        piping_valves      = equipment_cost * 0.35
        electrical_instr   = equipment_cost * 0.15
        engineering_admin  = equipment_cost * 0.25
        contingency        = equipment_cost * 0.20 # Risk buffer
        
        total_capex = (equipment_cost + installation_labor + 
                      piping_valves + electrical_instr + 
                      engineering_admin + contingency)

        return {
            'equipment_fob': equipment_cost,
            'installation': installation_labor,
            'piping': piping_valves,
            'electrical': electrical_instr,
            'indirects': engineering_admin,
            'contingency': contingency,
            'total_capex': total_capex,
            'currency': 'USD'
        }

    def estimate_opex(self, pump_power_kW, hours_per_year=8000, energy_cost_kwh=0.12):
        """
        Annual Operating Expenditure (OPEX)
        """
        energy_cost = pump_power_kW * hours_per_year * energy_cost_kwh
        # Maintenance typically 3% of CAPEX annually
        return {
            'energy_annual': energy_cost,
            'maintenance_annual': 0 # Calculated in main app usually
        }
