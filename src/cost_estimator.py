"""
Advanced Cost Estimator (Class 4)
Author: KAKAROTONCLOUD
"""
from src.hx_types import EngineeringDB

class CostEstimator:
    def estimate_project_budget(self, area, hx_type, material_name):
        """
        Generates a Class 4 estimate (-30% / +50%)
        """
        # 1. Base Cost (Carbon Steel Reference)
        # Empirical correlation: Cost = a * Area^b
        base_cost = 12000 * (area ** 0.65) # Approximation for shell & tube
        
        # 2. Material Correction
        mat_data = EngineeringDB.MATERIALS.get(material_name, {'cost_factor': 1.0})
        mat_factor = mat_data['cost_factor']
        
        # 3. Type Correction
        type_factor = 1.0
        if "Plate" in hx_type: type_factor = 0.7 # Plates are cheaper
        if "Air" in hx_type: type_factor = 1.2
        
        # Equipment Cost (F.O.B)
        equipment_cost = base_cost * mat_factor * type_factor
        
        # 4. Lang Factors (Total Installed Cost)
        # Factor 3.0 is typical for fluid processing plants
        installation = equipment_cost * 0.50
        piping = equipment_cost * 0.40
        instrumentation = equipment_cost * 0.20
        electrical = equipment_cost * 0.10
        engineering = equipment_cost * 0.25
        contingency = equipment_cost * 0.25
        
        total_capex = equipment_cost + installation + piping + instrumentation + electrical + engineering + contingency

        return {
            'equipment_fob': equipment_cost,
            'installation_labor': installation,
            'bulk_materials': piping + instrumentation + electrical,
            'indirects': engineering + contingency,
            'total_capex': total_capex,
            'class': 'AACE Class 4 (Preliminary)'
        }
