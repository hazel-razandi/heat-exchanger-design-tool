"""
Report Generator
Author: KAKAROTONCLOUD
"""
from datetime import datetime

def generate_text_report(results, pd, costs, project_info):
    # Ensure project_info is not None to prevent errors
    if project_info is None: project_info = {}
    
    lines = [
        "==========================================",
        "   HEAT EXCHANGER DESIGN REPORT",
        "   Author: KAKAROTONCLOUD",
        "==========================================",
        f"Date: {datetime.now().strftime('%Y-%m-%d')}",
        f"Project: {project_info.get('project_name', 'New Design')}",
        "",
        "--- THERMAL DESIGN ---",
        f"Heat Load (Q): {results.get('Q', 0):.2f} kW",
        f"Area Required: {results.get('area', 0):.2f} m2",
        f"Effectiveness: {results.get('effectiveness', 0)*100:.1f} %",
        f"LMTD:          {results.get('LMTD', 0):.2f} C",
        "",
        "--- FLUID DATA ---",
        f"Hot Fluid:  {results.get('hot_fluid', 'N/A')} ({results.get('T_hot_in')} -> {results.get('T_hot_out')} C)",
        f"Cold Fluid: {results.get('cold_fluid', 'N/A')} ({results.get('T_cold_in')} -> {results.get('T_cold_out')} C)",
        "",
        "--- ECONOMICS (Est) ---"
    ]
    
    if costs:
        # FIXED: Check for direct key access first (Flat structure)
        total_cost = costs.get('total_project_cost')
        
        # Fallback: Check for nested 'equipment' key (Old structure)
        if total_cost is None and 'equipment' in costs:
            total_cost = costs['equipment'].get('total_project_cost')
            
        if total_cost:
            lines.append(f"Capital Cost: ${total_cost:,.2f}")
        else:
            lines.append("Capital Cost: Not Available")
    
    return "\n".join(lines)
