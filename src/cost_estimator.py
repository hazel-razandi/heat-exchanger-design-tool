"""
Cost Estimator
Author: KAKAROTONCLOUD
"""

class CostEstimator:
    def estimate_equipment_cost(self, area, hx_type, material, pressure):
        base_rate = 1500 if hx_type == 'Shell-and-Tube' else 800
        cost = area * base_rate * 1.5 # installation factor
        return {
            'equipment_cost': cost,
            'total_project_cost': cost * 1.3 # piping/controls
        }

    def estimate_annual_operating_cost(self, power_kW):
        return {'annual_energy_cost': power_kW * 8760 * 0.12}

    def estimate_maintenance_cost(self, eq_cost, type):
        return {'annual_maintenance_total': eq_cost * 0.03}

    def calculate_lifecycle_cost(self, capital, opex, maintenance):
        return {'total_lifecycle_cost': capital + (opex + maintenance) * 10} # 10 year simple
