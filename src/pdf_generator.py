"""
Report Generator
Author: KAKAROTONCLOUD
"""
from datetime import datetime

def generate_text_report(results, pd, costs, project_info):
    lines = [
        "==========================================",
        "   HEAT EXCHANGER DESIGN REPORT",
        "   Author: KAKAROTONCLOUD",
        "==========================================",
        f"Date: {datetime.now().strftime('%Y-%m-%d')}",
        f"Project: {project_info.get('project_name')}",
        "",
        "--- THERMAL DESIGN ---",
        f"Heat Load (Q): {results.get('Q'):.2f} kW",
        f"Area Required: {results.get('area'):.2f} m2",
        f"Effectiveness: {results.get('effectiveness')*100:.1f} %",
        f"LMTD:          {results.get('LMTD'):.2f} C",
        "",
        "--- FLUID DATA ---",
        f"Hot Fluid:  {results.get('hot_fluid')} ({results.get('T_hot_in')} -> {results.get('T_hot_out')} C)",
        f"Cold Fluid: {results.get('cold_fluid')} ({results.get('T_cold_in')} -> {results.get('T_cold_out')} C)",
        "",
        "--- ECONOMICS (Est) ---"
    ]
    if costs:
        lines.append(f"Capital Cost: ${costs['equipment']['total_project_cost']:,.2f}")
    
    return "\n".join(lines)
