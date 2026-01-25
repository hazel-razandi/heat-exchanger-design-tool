"""
Cost Estimation Module
Estimates equipment costs, operating costs, and lifecycle costs for heat exchangers.
"""

import numpy as np


class CostEstimator:
    """
    Estimate costs for heat exchanger projects.
    """
    
    # Base costs per m² for different types (2024 USD)
    BASE_COSTS = {
        'Shell-and-Tube': {
            'Carbon Steel': 850,
            'Stainless Steel 304': 1500,
            'Stainless Steel 316': 1800,
            'Titanium': 4500
        },
        'Plate': {
            'Stainless Steel 304': 600,
            'Stainless Steel 316': 750,
            'Titanium': 2200
        },
        'Finned Tube': {
            'Carbon Steel': 450,
            'Stainless Steel': 800,
            'Aluminum': 350
        },
        'Double Pipe': {
            'Carbon Steel': 400,
            'Stainless Steel 304': 700
        },
        'Spiral': {
            'Stainless Steel 304': 1200,
            'Stainless Steel 316': 1500
        }
    }
    
    def __init__(self):
        """Initialize cost estimator."""
        pass
    
    def estimate_equipment_cost(self, area, hx_type='Shell-and-Tube', 
                               material='Stainless Steel 304', 
                               pressure_rating='Low'):
        """
        Estimate heat exchanger equipment cost.
        
        Args:
            area (float): Heat transfer area (m²)
            hx_type (str): Type of heat exchanger
            material (str): Construction material
            pressure_rating (str): 'Low' (<10 bar), 'Medium' (10-40 bar), 'High' (>40 bar)
            
        Returns:
            dict: Cost breakdown
        """
        # Get base cost per m²
        if hx_type not in self.BASE_COSTS:
            hx_type = 'Shell-and-Tube'
        
        type_costs = self.BASE_COSTS[hx_type]
        
        if material not in type_costs:
            material = list(type_costs.keys())[0]
        
        base_cost_per_m2 = type_costs[material]
        
        # Base equipment cost
        base_cost = area * base_cost_per_m2
        
        # Pressure rating multiplier
        pressure_multipliers = {
            'Low': 1.0,
            'Medium': 1.3,
            'High': 1.6
        }
        pressure_mult = pressure_multipliers.get(pressure_rating, 1.0)
        
        # Size factor (economies of scale)
        if area < 5:
            size_factor = 1.3  # Small units cost more per m²
        elif area < 20:
            size_factor = 1.0
        elif area < 100:
            size_factor = 0.9
        else:
            size_factor = 0.8  # Large units cost less per m²
        
        # Total equipment cost
        equipment_cost = base_cost * pressure_mult * size_factor
        
        # Installation cost (typically 30-50% of equipment)
        installation_cost = equipment_cost * 0.4
        
        # Piping and valves (10-15% of equipment)
        piping_cost = equipment_cost * 0.12
        
        # Instrumentation (5-10% of equipment)
        instrumentation_cost = equipment_cost * 0.07
        
        # Total installed cost
        total_installed = equipment_cost + installation_cost + piping_cost + instrumentation_cost
        
        # Contingency (10%)
        contingency = total_installed * 0.1
        
        # Project total
        project_total = total_installed + contingency
        
        return {
            'equipment_cost': equipment_cost,
            'installation_cost': installation_cost,
            'piping_cost': piping_cost,
            'instrumentation_cost': instrumentation_cost,
            'subtotal': total_installed,
            'contingency': contingency,
            'total_project_cost': project_total,
            'cost_per_m2': equipment_cost / area,
            'assumptions': {
                'hx_type': hx_type,
                'material': material,
                'pressure_rating': pressure_rating,
                'area_m2': area
            }
        }
    
    def estimate_annual_operating_cost(self, pumping_power_kW, 
                                      electricity_rate=0.10,
                                      operating_hours=8760,
                                      maintenance_factor=0.03):
        """
        Estimate annual operating costs.
        
        Args:
            pumping_power_kW (float): Total pumping power (kW)
            electricity_rate (float): Electricity cost ($/kWh)
            operating_hours (float): Hours per year
            maintenance_factor (float): Maintenance as fraction of equipment cost
            
        Returns:
            dict: Annual operating costs
        """
        # Energy cost
        annual_energy_kWh = pumping_power_kW * operating_hours
        annual_energy_cost = annual_energy_kWh * electricity_rate
        
        return {
            'annual_energy_kWh': annual_energy_kWh,
            'annual_energy_cost': annual_energy_cost,
            'monthly_energy_cost': annual_energy_cost / 12,
            'electricity_rate': electricity_rate,
            'operating_hours': operating_hours
        }
    
    def estimate_maintenance_cost(self, equipment_cost, maintenance_type='Standard'):
        """
        Estimate annual maintenance costs.
        
        Args:
            equipment_cost (float): Equipment cost ($)
            maintenance_type (str): 'Minimal', 'Standard', 'Intensive'
            
        Returns:
            dict: Maintenance cost breakdown
        """
        # Maintenance as percentage of equipment cost
        maintenance_factors = {
            'Minimal': 0.02,  # 2% per year (clean fluids, low duty)
            'Standard': 0.04,  # 4% per year (typical)
            'Intensive': 0.08  # 8% per year (fouling fluids, harsh conditions)
        }
        
        factor = maintenance_factors.get(maintenance_type, 0.04)
        annual_maintenance = equipment_cost * factor
        
        # Breakdown
        routine_maintenance = annual_maintenance * 0.6  # Regular inspections, minor repairs
        cleaning = annual_maintenance * 0.3  # Cleaning, descaling
        parts_replacement = annual_maintenance * 0.1  # Gaskets, seals, etc.
        
        return {
            'annual_maintenance_total': annual_maintenance,
            'routine_maintenance': routine_maintenance,
            'cleaning': cleaning,
            'parts_replacement': parts_replacement,
            'maintenance_type': maintenance_type,
            'monthly_cost': annual_maintenance / 12
        }
    
    def calculate_lifecycle_cost(self, equipment_cost, annual_operating_cost,
                                 annual_maintenance_cost, lifetime_years=20,
                                 discount_rate=0.05, salvage_value_factor=0.1):
        """
        Calculate total lifecycle cost (Net Present Value).
        
        Args:
            equipment_cost (float): Initial equipment cost ($)
            annual_operating_cost (float): Annual operating cost ($)
            annual_maintenance_cost (float): Annual maintenance cost ($)
            lifetime_years (int): Expected lifetime (years)
            discount_rate (float): Discount rate for NPV calculation
            salvage_value_factor (float): Salvage value as fraction of initial cost
            
        Returns:
            dict: Lifecycle cost analysis
        """
        # Initial investment
        initial_cost = equipment_cost
        
        # Annual costs
        annual_cost = annual_operating_cost + annual_maintenance_cost
        
        # Calculate NPV of annual costs
        npv_annual = 0
        yearly_costs = []
        
        for year in range(1, lifetime_years + 1):
            # Discount factor
            discount_factor = 1 / (1 + discount_rate) ** year
            
            # Present value of this year's cost
            pv_year = annual_cost * discount_factor
            npv_annual += pv_year
            
            yearly_costs.append({
                'year': year,
                'annual_cost': annual_cost,
                'discount_factor': discount_factor,
                'present_value': pv_year,
                'cumulative_pv': npv_annual
            })
        
        # Salvage value
        salvage_value = equipment_cost * salvage_value_factor
        salvage_pv = salvage_value / (1 + discount_rate) ** lifetime_years
        
        # Total lifecycle cost
        total_lifecycle_cost = initial_cost + npv_annual - salvage_pv
        
        # Average annual equivalent cost
        annualized_cost = total_lifecycle_cost * (discount_rate * (1 + discount_rate) ** lifetime_years) / ((1 + discount_rate) ** lifetime_years - 1)
        
        return {
            'initial_investment': initial_cost,
            'npv_operating_costs': npv_annual,
            'salvage_value': salvage_value,
            'salvage_present_value': salvage_pv,
            'total_lifecycle_cost': total_lifecycle_cost,
            'annualized_cost': annualized_cost,
            'lifetime_years': lifetime_years,
            'discount_rate': discount_rate,
            'total_undiscounted': initial_cost + (annual_cost * lifetime_years),
            'yearly_breakdown': yearly_costs
        }
    
    def compare_designs(self, designs_list):
        """
        Compare multiple designs economically.
        
        Args:
            designs_list (list): List of design dictionaries with lifecycle costs
            
        Returns:
            dict: Comparison results
        """
        if not designs_list:
            return {}
        
        # Find best design by lifecycle cost
        sorted_designs = sorted(designs_list, key=lambda x: x.get('total_lifecycle_cost', float('inf')))
        
        best_design = sorted_designs[0]
        
        # Calculate savings vs others
        comparisons = []
        for design in sorted_designs[1:]:
            savings = design['total_lifecycle_cost'] - best_design['total_lifecycle_cost']
            savings_percent = (savings / design['total_lifecycle_cost']) * 100
            
            comparisons.append({
                'design_name': design.get('name', 'Design'),
                'lifecycle_cost': design['total_lifecycle_cost'],
                'cost_vs_best': savings,
                'percent_more_expensive': savings_percent
            })
        
        return {
            'best_design': best_design.get('name', 'Best Design'),
            'best_lifecycle_cost': best_design['total_lifecycle_cost'],
            'comparisons': comparisons,
            'potential_savings': sum([c['cost_vs_best'] for c in comparisons])
        }
    
    def estimate_payback_period(self, additional_investment, annual_savings):
        """
        Calculate simple payback period.
        
        Args:
            additional_investment (float): Extra cost for better design ($)
            annual_savings (float): Annual savings from better design ($/year)
            
        Returns:
            dict: Payback analysis
        """
        if annual_savings <= 0:
            return {
                'payback_years': float('inf'),
                'payback_months': float('inf'),
                'is_viable': False,
                'message': 'No savings - investment not recommended'
            }
        
        payback_years = additional_investment / annual_savings
        payback_months = payback_years * 12
        
        # Typical acceptable payback: 2-5 years
        is_viable = payback_years <= 5
        
        if payback_years < 2:
            message = 'Excellent investment - payback under 2 years!'
        elif payback_years < 5:
            message = 'Good investment - acceptable payback period'
        elif payback_years < 10:
            message = 'Marginal investment - long payback period'
        else:
            message = 'Poor investment - payback too long'
        
        return {
            'payback_years': payback_years,
            'payback_months': payback_months,
            'is_viable': is_viable,
            'message': message,
            'roi_percent': (annual_savings / additional_investment) * 100
        }


# Testing
if __name__ == "__main__":
    print("Testing Cost Estimator\n")
    print("="*70)
    
    estimator = CostEstimator()
    
    # Test equipment cost
    print("\nTest: 12.4 m² Stainless Steel Shell-and-Tube Heat Exchanger")
    print("-"*70)
    
    equipment = estimator.estimate_equipment_cost(
        area=12.4,
        hx_type='Shell-and-Tube',
        material='Stainless Steel 304',
        pressure_rating='Low'
    )
    
    print(f"\nEquipment Cost Breakdown:")
    print(f"  Equipment: ${equipment['equipment_cost']:,.0f}")
    print(f"  Installation: ${equipment['installation_cost']:,.0f}")
    print(f"  Piping: ${equipment['piping_cost']:,.0f}")
    print(f"  Instrumentation: ${equipment['instrumentation_cost']:,.0f}")
    print(f"  Contingency: ${equipment['contingency']:,.0f}")
    print(f"  Total Project Cost: ${equipment['total_project_cost']:,.0f}")
    
    # Operating costs
    operating = estimator.estimate_annual_operating_cost(
        pumping_power_kW=0.5,
        electricity_rate=0.10
    )
    
    print(f"\nAnnual Operating Costs:")
    print(f"  Energy: ${operating['annual_energy_cost']:,.0f}/year")
    print(f"  Monthly: ${operating['monthly_energy_cost']:,.0f}/month")
    
    # Maintenance
    maintenance = estimator.estimate_maintenance_cost(
        equipment_cost=equipment['equipment_cost'],
        maintenance_type='Standard'
    )
    
    print(f"\nAnnual Maintenance Costs:")
    print(f"  Total: ${maintenance['annual_maintenance_total']:,.0f}/year")
    print(f"  Monthly: ${maintenance['monthly_cost']:,.0f}/month")
    
    # Lifecycle
    lifecycle = estimator.calculate_lifecycle_cost(
        equipment_cost=equipment['total_project_cost'],
        annual_operating_cost=operating['annual_energy_cost'],
        annual_maintenance_cost=maintenance['annual_maintenance_total'],
        lifetime_years=20
    )
    
    print(f"\n20-Year Lifecycle Cost:")
    print(f"  Initial Investment: ${lifecycle['initial_investment']:,.0f}")
    print(f"  NPV Operating Costs: ${lifecycle['npv_operating_costs']:,.0f}")
    print(f"  Total Lifecycle Cost: ${lifecycle['total_lifecycle_cost']:,.0f}")
    print(f"  Annualized Cost: ${lifecycle['annualized_cost']:,.0f}/year")
    
    print("\n" + "="*70)
