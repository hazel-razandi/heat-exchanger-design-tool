import pandas as pd
import io

def generate_tema_sheet(project_name, inputs, results):
    """
    Generates a TEMA-style datasheet with Mechanical Specs.
    """
    # Create dictionary mapping TEMA fields to values
    data = {
        "Parameter": [
            "Project Reference", "TEMA Type", "Shell ID (m)", "Tube Length (m)", 
            "Tube Count", "Number of Passes", "Tube Pattern", 
            "--- PERFORMANCE ---",
            "Duty (kW)", "U-Value (W/m2K)", "Area (m2)",
            "Hot Fluid", "Cold Fluid",
            "--- MECHANICAL DESIGN ---",
            "Design Pressure (Shell/Tube)", "Design Temp (Shell/Tube)",
            "Shell Material", "Tube Material",
            "Corrosion Allowance (mm)", "Nozzles (In/Out)"
        ],
        "Value": [
            project_name, inputs.get('tema_type'), inputs.get('shell_id'), inputs.get('length'),
            inputs.get('n_tubes'), inputs.get('n_passes'), inputs.get('tube_layout'),
            "", # Spacer
            f"{results['Q']/1000:.2f}", f"{results['U']:.2f}", f"{results['Area']:.2f}",
            inputs.get('hot_fluid'), inputs.get('cold_fluid'),
            "", # Spacer
            f"{inputs.get('des_press_shell')} / {inputs.get('des_press_tube')} bar",
            f"{inputs.get('des_temp_shell')} / {inputs.get('des_temp_tube')} °C",
            inputs.get('mat_shell'), inputs.get('mat_tube'),
            f"{inputs.get('corr_allow')} mm",
            f"{inputs.get('noz_in')} / {inputs.get('noz_out')}"
        ]
    }
    
    df = pd.read_json(json.dumps(data)) # Quick dataframe creation
    
    # Save to Excel buffer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='TEMA Data')
        
        # Auto-adjust column width
        worksheet = writer.sheets['TEMA Data']
        worksheet.set_column('A:A', 30)
        worksheet.set_column('B:B', 20)
        
    return output.getvalue()
import json
