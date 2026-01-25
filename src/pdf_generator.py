"""
PDF Report Generator Module
Generates professional PDF reports for heat exchanger designs.
"""

from datetime import datetime
from io import BytesIO


def generate_text_report(results, pressure_drop_results=None, cost_results=None, 
                        project_info=None):
    """
    Generate a text-based report (fallback for PDF).
    
    Args:
        results (dict): Calculation results
        pressure_drop_results (dict): Pressure drop calculations
        cost_results (dict): Cost estimation results
        project_info (dict): Project details
        
    Returns:
        str: Formatted text report
    """
    report_lines = []
    
    # Header
    report_lines.append("="*80)
    report_lines.append("HEAT EXCHANGER DESIGN REPORT".center(80))
    report_lines.append("="*80)
    report_lines.append("")
    
    # Project Information
    if project_info:
        report_lines.append("PROJECT INFORMATION")
        report_lines.append("-"*80)
        report_lines.append(f"Project Name: {project_info.get('project_name', 'N/A')}")
        report_lines.append(f"Engineer: {project_info.get('engineer_name', 'N/A')}")
        report_lines.append(f"Company: {project_info.get('company', 'N/A')}")
        report_lines.append(f"Date: {project_info.get('date', datetime.now().strftime('%Y-%m-%d'))}")
        report_lines.append(f"Location: {project_info.get('location', 'N/A')}")
        report_lines.append("")
    else:
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
    
    # Design Configuration
    report_lines.append("DESIGN CONFIGURATION")
    report_lines.append("-"*80)
    report_lines.append(f"Flow Arrangement: {results.get('flow_type', 'N/A')}")
    report_lines.append(f"Calculation Method: {results.get('method', 'N/A')}")
    report_lines.append(f"Heat Exchanger Type: {results.get('hx_type', 'Shell-and-Tube')}")
    report_lines.append("")
    
    # Operating Conditions
    report_lines.append("OPERATING CONDITIONS")
    report_lines.append("-"*80)
    
    report_lines.append("Hot Fluid:")
    report_lines.append(f"  Type: {results.get('hot_fluid', 'N/A')}")
    report_lines.append(f"  Inlet Temperature: {results.get('T_hot_in', 0):.1f} °C")
    report_lines.append(f"  Outlet Temperature: {results.get('T_hot_out', 0):.1f} °C")
    report_lines.append(f"  Mass Flow Rate: {results.get('m_hot', 0):.2f} kg/s")
    report_lines.append("")
    
    report_lines.append("Cold Fluid:")
    report_lines.append(f"  Type: {results.get('cold_fluid', 'N/A')}")
    report_lines.append(f"  Inlet Temperature: {results.get('T_cold_in', 0):.1f} °C")
    report_lines.append(f"  Outlet Temperature: {results.get('T_cold_out', 0):.1f} °C")
    report_lines.append(f"  Mass Flow Rate: {results.get('m_cold', 0):.2f} kg/s")
    report_lines.append("")
    
    # Thermal Performance
    report_lines.append("THERMAL PERFORMANCE")
    report_lines.append("-"*80)
    report_lines.append(f"Heat Transfer Rate: {results.get('Q', 0):.2f} kW")
    report_lines.append(f"Required Heat Transfer Area: {results.get('area', 0):.2f} m²")
    report_lines.append(f"Overall Heat Transfer Coefficient (U): {results.get('U_value', 0):.1f} W/(m²·K)")
    report_lines.append(f"Effectiveness: {results.get('effectiveness', 0)*100:.1f}%")
    report_lines.append(f"NTU: {results.get('NTU', 0):.2f}")
    
    if 'LMTD' in results:
        report_lines.append(f"Log Mean Temperature Difference: {results.get('LMTD', 0):.2f} °C")
    
    report_lines.append(f"Heat Capacity Rate Ratio (C*): {results.get('C_ratio', 0):.3f}")
    report_lines.append("")
    
    # Energy Balance
    report_lines.append("ENERGY BALANCE VERIFICATION")
    report_lines.append("-"*80)
    report_lines.append(f"Heat Removed from Hot Fluid: {results.get('Q_hot', 0):.2f} kW")
    report_lines.append(f"Heat Added to Cold Fluid: {results.get('Q_cold', 0):.2f} kW")
    report_lines.append(f"Energy Balance Error: {results.get('energy_balance_error', 0):.2f}%")
    
    if results.get('energy_balance_error', 0) < 1.0:
        report_lines.append("Status: ✓ PASS - Energy balance satisfied")
    else:
        report_lines.append("Status: ⚠ WARNING - Review energy balance")
    report_lines.append("")
    
    # Pressure Drop Results
    if pressure_drop_results:
        report_lines.append("PRESSURE DROP ANALYSIS")
        report_lines.append("-"*80)
        
        if 'hot_side' in pressure_drop_results:
            hot_dp = pressure_drop_results['hot_side']
            report_lines.append("Hot Side:")
            report_lines.append(f"  Pressure Drop: {hot_dp.get('pressure_drop_kPa', 0):.2f} kPa ({hot_dp.get('pressure_drop_psi', 0):.2f} psi)")
            report_lines.append(f"  Velocity: {hot_dp.get('velocity_m_s', 0):.2f} m/s")
            report_lines.append(f"  Reynolds Number: {hot_dp.get('reynolds_number', 0):.0f} ({hot_dp.get('flow_regime', 'N/A')})")
            report_lines.append("")
        
        if 'cold_side' in pressure_drop_results:
            cold_dp = pressure_drop_results['cold_side']
            report_lines.append("Cold Side:")
            report_lines.append(f"  Pressure Drop: {cold_dp.get('pressure_drop_kPa', 0):.2f} kPa ({cold_dp.get('pressure_drop_psi', 0):.2f} psi)")
            report_lines.append(f"  Velocity: {cold_dp.get('velocity_m_s', 0):.2f} m/s")
            report_lines.append(f"  Reynolds Number: {cold_dp.get('reynolds_number', 0):.0f} ({cold_dp.get('flow_regime', 'N/A')})")
            report_lines.append("")
        
        if 'pumping' in pressure_drop_results:
            pump = pressure_drop_results['pumping']
            report_lines.append("Pumping Requirements:")
            report_lines.append(f"  Total Power Required: {pump.get('total_power_kW', 0):.3f} kW ({pump.get('total_power_HP', 0):.2f} HP)")
            report_lines.append(f"  Annual Energy: {pump.get('annual_energy_kWh', 0):.0f} kWh/year")
            report_lines.append(f"  Annual Energy Cost: ${pump.get('annual_cost', 0):.2f}/year")
            report_lines.append("")
    
    # Cost Analysis
    if cost_results:
        report_lines.append("COST ANALYSIS")
        report_lines.append("-"*80)
        
        if 'equipment' in cost_results:
            equip = cost_results['equipment']
            report_lines.append("Equipment Costs:")
            report_lines.append(f"  Heat Exchanger Equipment: ${equip.get('equipment_cost', 0):,.0f}")
            report_lines.append(f"  Installation: ${equip.get('installation_cost', 0):,.0f}")
            report_lines.append(f"  Piping & Valves: ${equip.get('piping_cost', 0):,.0f}")
            report_lines.append(f"  Instrumentation: ${equip.get('instrumentation_cost', 0):,.0f}")
            report_lines.append(f"  Contingency (10%): ${equip.get('contingency', 0):,.0f}")
            report_lines.append(f"  TOTAL PROJECT COST: ${equip.get('total_project_cost', 0):,.0f}")
            report_lines.append("")
        
        if 'operating' in cost_results:
            oper = cost_results['operating']
            report_lines.append("Annual Operating Costs:")
            report_lines.append(f"  Energy Cost: ${oper.get('annual_energy_cost', 0):,.0f}/year")
            report_lines.append(f"  Maintenance Cost: ${oper.get('annual_maintenance_cost', 0):,.0f}/year")
            report_lines.append(f"  TOTAL ANNUAL: ${oper.get('total_annual', 0):,.0f}/year")
            report_lines.append("")
        
        if 'lifecycle' in cost_results:
            lc = cost_results['lifecycle']
            report_lines.append("Lifecycle Cost Analysis (20 years):")
            report_lines.append(f"  Initial Investment: ${lc.get('initial_investment', 0):,.0f}")
            report_lines.append(f"  NPV of Operating Costs: ${lc.get('npv_operating_costs', 0):,.0f}")
            report_lines.append(f"  TOTAL LIFECYCLE COST: ${lc.get('total_lifecycle_cost', 0):,.0f}")
            report_lines.append(f"  Annualized Cost: ${lc.get('annualized_cost', 0):,.0f}/year")
            report_lines.append("")
    
    # Recommendations
    report_lines.append("RECOMMENDATIONS")
    report_lines.append("-"*80)
    
    # Add automatic recommendations based on results
    recommendations = []
    
    if results.get('effectiveness', 0) < 0.5:
        recommendations.append("• Consider increasing heat exchanger area to improve effectiveness")
    
    if results.get('effectiveness', 0) > 0.9:
        recommendations.append("• Excellent effectiveness achieved - design is well optimized")
    
    if pressure_drop_results and 'hot_side' in pressure_drop_results:
        if pressure_drop_results['hot_side'].get('pressure_drop_kPa', 0) > 100:
            recommendations.append("• High pressure drop on hot side - consider larger flow area or multiple passes")
    
    if pressure_drop_results and 'cold_side' in pressure_drop_results:
        if pressure_drop_results['cold_side'].get('pressure_drop_kPa', 0) > 100:
            recommendations.append("• High pressure drop on cold side - consider design modifications")
    
    if results.get('flow_type') == 'Parallel Flow':
        recommendations.append("• Consider counter flow arrangement for better thermal efficiency")
    
    if results.get('energy_balance_error', 0) > 5:
        recommendations.append("⚠ WARNING: Large energy balance error - verify input parameters")
    
    if recommendations:
        for rec in recommendations:
            report_lines.append(rec)
    else:
        report_lines.append("• Design meets all requirements")
        report_lines.append("• No critical issues identified")
    
    report_lines.append("")
    
    # Footer
    report_lines.append("="*80)
    report_lines.append("END OF REPORT".center(80))
    report_lines.append("="*80)
    report_lines.append("")
    report_lines.append("This report was generated by Heat Exchanger Design Tool")
    report_lines.append("For questions or support, visit: https://github.com/yourusername/heat-exchanger-design-tool")
    report_lines.append("")
    
    # Disclaimer
    report_lines.append("DISCLAIMER:")
    report_lines.append("This report is for preliminary design purposes only. Final design should be")
    report_lines.append("verified by a qualified engineer and comply with applicable codes and standards.")
    
    return "\n".join(report_lines)


def create_downloadable_report(results, pressure_drop_results=None, cost_results=None,
                               project_info=None, format='txt'):
    """
    Create a downloadable report file.
    
    Args:
        results (dict): Calculation results
        pressure_drop_results (dict): Pressure drop data
        cost_results (dict): Cost data
        project_info (dict): Project information
        format (str): 'txt' or 'pdf' (pdf requires additional libraries)
        
    Returns:
        tuple: (file_content, filename, mime_type)
    """
    # Generate text report
    report_text = generate_text_report(results, pressure_drop_results, cost_results, project_info)
    
    if format == 'txt':
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        project_name = project_info.get('project_name', 'HeatExchanger') if project_info else 'HeatExchanger'
        # Clean project name for filename
        project_name = "".join(c for c in project_name if c.isalnum() or c in (' ', '-', '_')).strip()
        project_name = project_name.replace(' ', '_')
        
        filename = f"{project_name}_Report_{timestamp}.txt"
        
        return report_text, filename, 'text/plain'
    
    elif format == 'csv':
        # Generate CSV summary
        csv_lines = []
        csv_lines.append("Parameter,Value,Unit")
        csv_lines.append(f"Heat Transfer Rate,{results.get('Q', 0):.2f},kW")
        csv_lines.append(f"Required Area,{results.get('area', 0):.2f},m²")
        csv_lines.append(f"Effectiveness,{results.get('effectiveness', 0)*100:.1f},%")
        csv_lines.append(f"NTU,{results.get('NTU', 0):.2f},-")
        csv_lines.append(f"Hot Inlet,{results.get('T_hot_in', 0):.1f},°C")
        csv_lines.append(f"Hot Outlet,{results.get('T_hot_out', 0):.1f},°C")
        csv_lines.append(f"Cold Inlet,{results.get('T_cold_in', 0):.1f},°C")
        csv_lines.append(f"Cold Outlet,{results.get('T_cold_out', 0):.1f},°C")
        
        csv_text = "\n".join(csv_lines)
        filename = f"HeatExchanger_Summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        return csv_text, filename, 'text/csv'
    
    else:
        # Default to text
        return report_text, f"HeatExchanger_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt", 'text/plain'


# Testing
if __name__ == "__main__":
    print("Testing PDF/Report Generator\n")
    print("="*80)
    
    # Sample results
    sample_results = {
        'flow_type': 'Counter Flow',
        'method': 'LMTD',
        'hx_type': 'Shell-and-Tube',
        'hot_fluid': 'Water',
        'cold_fluid': 'Water',
        'T_hot_in': 90,
        'T_hot_out': 50,
        'T_cold_in': 25,
        'T_cold_out': 45,
        'm_hot': 2.0,
        'm_cold': 3.0,
        'Q': 335.2,
        'Q_hot': 334.4,
        'Q_cold': 336.0,
        'area': 12.4,
        'U_value': 500,
        'effectiveness': 0.615,
        'NTU': 2.07,
        'LMTD': 34.0,
        'C_ratio': 0.667,
        'energy_balance_error': 0.5
    }
    
    sample_project = {
        'project_name': 'Office Building HVAC',
        'engineer_name': 'John Smith',
        'company': 'ABC Engineering',
        'location': 'New York, NY'
    }
    
    # Generate report
    report = generate_text_report(sample_results, project_info=sample_project)
    
    print(report)
    print("\n" + "="*80)
    print("Report generated successfully!")
    print("="*80)
