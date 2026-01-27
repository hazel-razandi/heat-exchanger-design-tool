import pandas as pd
import io
import datetime

def generate_tema_sheet(project_name, inputs, results):
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        ws = workbook.add_worksheet("TEMA Data")
        
        # --- 1. STYLES (Professional Blue Theme - KEPT) ---
        fmt_header = workbook.add_format({
            'bold': True, 'bg_color': '#1F497D', 'font_color': 'white', 
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        fmt_section = workbook.add_format({
            'bold': True, 'bg_color': '#D9D9D9', 'border': 1, 'align': 'left'
        })
        fmt_cell = workbook.add_format({'border': 1, 'align': 'center'})
        fmt_cell_left = workbook.add_format({'border': 1, 'align': 'left'})
        fmt_title = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'border': 2
        })
        
        # Set Column Widths
        ws.set_column('A:A', 35) # Parameter Name
        ws.set_column('B:B', 25) # Shell Side
        ws.set_column('C:C', 25) # Tube Side
        
        # --- 2. TITLE BLOCK (KEPT) ---
        ws.merge_range('A1:C2', "HEAT EXCHANGER SPECIFICATION SHEET (TEMA R)", fmt_title)
        ws.write('A3', f"Project: {project_name}", fmt_cell_left)
        ws.write('B3', f"Date: {datetime.date.today()}", fmt_cell)
        ws.write('C3', "Rev: B", fmt_cell)
        
        # --- 3. PERFORMANCE DATA SECTION ---
        row = 4
        ws.merge_range(f'A{row}:C{row}', "1. PERFORMANCE DATA", fmt_section)
        row += 1
        
        # Headers
        ws.write(row, 0, "PARAMETER", fmt_header)
        ws.write(row, 1, "SHELL SIDE", fmt_header)
        ws.write(row, 2, "TUBE SIDE", fmt_header)
        row += 1
        
        # Row 1: Fluid Name
        ws.write(row, 0, "Fluid Name", fmt_cell_left)
        ws.write(row, 1, inputs.get('cold_fluid'), fmt_cell)
        ws.write(row, 2, inputs.get('hot_fluid'), fmt_cell)
        row += 1
        
        # Row 2: Mass Flow
        ws.write(row, 0, "Mass Flow Rate (kg/s)", fmt_cell_left)
        ws.write(row, 1, inputs.get('m_cold'), fmt_cell)
        ws.write(row, 2, inputs.get('m_hot'), fmt_cell)
        row += 1
        
        # Row 3: Temperatures
        ws.write(row, 0, "Inlet Temperature (°C)", fmt_cell_left)
        ws.write(row, 1, inputs.get('T_cold_in'), fmt_cell)
        ws.write(row, 2, inputs.get('T_hot_in'), fmt_cell)
        row += 1
        
        ws.write(row, 0, "Outlet Temperature (°C)", fmt_cell_left)
        ws.write(row, 1, f"{results['T_cold_out']:.1f}", fmt_cell)
        ws.write(row, 2, f"{results['T_hot_out']:.1f}", fmt_cell)
        row += 1
        
        # Row 4: Pressure
        ws.write(row, 0, "Operating Pressure (bar)", fmt_cell_left)
        ws.write(row, 1, "1.0", fmt_cell)
        ws.write(row, 2, "1.0", fmt_cell)
        row += 1
        
        # Row 5: Velocity
        ws.write(row, 0, "Calculated Velocity (m/s)", fmt_cell_left)
        ws.write(row, 1, f"{results['v_shell']:.2f}", fmt_cell)
        ws.write(row, 2, f"{results['v_tube']:.2f}", fmt_cell)
        row += 1
        
        # Row 6: Pressure Drop Limit
        ws.write(row, 0, "Allowable Pressure Drop (bar)", fmt_cell_left)
        ws.write(row, 1, "0.5", fmt_cell)
        ws.write(row, 2, "0.5", fmt_cell)
        row += 1
        
        # --- NEW ADDITION: Calculated Pressure Drop ---
        ws.write(row, 0, "Calc. Pressure Drop (bar)", fmt_cell_left)
        ws.write(row, 1, f"{results['dP_shell']:.4f}", fmt_cell)
        ws.write(row, 2, f"{results['dP_tube']:.4f}", fmt_cell)
        row += 1
        
        # --- NEW ADDITION: Fouling Factors ---
        ws.write(row, 0, "Fouling Resistance (hr-m2-C/W)", fmt_cell_left)
        ws.write(row, 1, f"{inputs.get('fouling')}", fmt_cell)
        ws.write(row, 2, f"{inputs.get('fouling')}", fmt_cell)
        row += 1
        
        # --- THERMAL SUMMARY ---
        ws.merge_range(f'A{row}:C{row}', "--- THERMAL SUMMARY ---", fmt_cell)
        row += 1
        
        ws.write(row, 0, "Total Heat Duty (kW)", fmt_cell_left)
        ws.merge_range(f'B{row}:C{row}', f"{results['Q']/1000:.2f}", fmt_cell)
        row += 1
        
        ws.write(row, 0, "Service U-Value (W/m2K)", fmt_cell_left)
        ws.merge_range(f'B{row}:C{row}', f"{results['U']:.2f}", fmt_cell)
        row += 1
        
        # --- NEW ADDITION: Overdesign ---
        ws.write(row, 0, "Overdesign Margin (%)", fmt_cell_left)
        ws.merge_range(f'B{row}:C{row}', "10.0%", fmt_cell)
        row += 1
        
        # --- 4. CONSTRUCTION DETAILS SECTION ---
        row += 1
        ws.merge_range(f'A{row}:C{row}', "2. CONSTRUCTION DETAILS", fmt_section)
        row += 1
        
        # TEMA Type
        ws.write(row, 0, "TEMA Type", fmt_cell_left)
        ws.merge_range(f'B{row}:C{row}', inputs.get('tema_type'), fmt_cell)
        row += 1
        
        # Design Pressure
        ws.write(row, 0, "Design Pressure (bar g)", fmt_cell_left)
        ws.write(row, 1, inputs.get('des_press_shell'), fmt_cell)
        ws.write(row, 2, inputs.get('des_press_tube'), fmt_cell)
        row += 1
        
        # Design Temp
        ws.write(row, 0, "Design Temperature (°C)", fmt_cell_left)
        ws.write(row, 1, inputs.get('des_temp_shell'), fmt_cell)
        ws.write(row, 2, inputs.get('des_temp_tube'), fmt_cell)
        row += 1
        
        # Material
        ws.write(row, 0, "Material of Construction", fmt_cell_left)
        ws.write(row, 1, inputs.get('mat_shell'), fmt_cell)
        ws.write(row, 2, inputs.get('mat_tube'), fmt_cell)
        row += 1
        
        # Corrosion
        ws.write(row, 0, "Corrosion Allowance (mm)", fmt_cell_left)
        ws.write(row, 1, inputs.get('corr_allow'), fmt_cell)
        ws.write(row, 2, "-", fmt_cell)
        row += 1
        
        # --- NEW ADDITION: Tube Thickness ---
        ws.write(row, 0, "Tube Thickness (mm)", fmt_cell_left)
        ws.write(row, 1, "-", fmt_cell)
        ws.write(row, 2, f"{inputs.get('tube_thickness_mm')}", fmt_cell)
        row += 1
        
        # Nozzles
        ws.write(row, 0, "Nozzle Size (In/Out)", fmt_cell_left)
        ws.write(row, 1, inputs.get('noz_in'), fmt_cell)
        ws.write(row, 2, inputs.get('noz_out'), fmt_cell)
        row += 1
        
        # Dimensions
        ws.write(row, 0, "Shell ID / Tube OD (m)", fmt_cell_left)
        ws.write(row, 1, inputs.get('shell_id'), fmt_cell)
        ws.write(row, 2, inputs.get('tube_od'), fmt_cell)
        row += 1
        
        ws.write(row, 0, "Tube Length (m)", fmt_cell_left)
        ws.merge_range(f'B{row}:C{row}', inputs.get('length'), fmt_cell)
        row += 1
        
        ws.write(row, 0, "Tube Pitch / Layout", fmt_cell_left)
        ws.write(row, 1, "1.25", fmt_cell)
        ws.write(row, 2, inputs.get('tube_layout'), fmt_cell)
        row += 1

        # --- NEW ADDITION: Number of Passes ---
        ws.write(row, 0, "Number of Passes", fmt_cell_left)
        ws.write(row, 1, "1", fmt_cell)
        ws.write(row, 2, inputs.get('n_passes'), fmt_cell)
        row += 1
        
        # Baffles
        ws.write(row, 0, "Baffles (Type / Cut / Spacing)", fmt_cell_left)
        ws.write(row, 1, f"Single Seg / {inputs.get('baffle_cut')}%", fmt_cell)
        ws.write(row, 2, f"{inputs.get('baffle_spacing')} m", fmt_cell)
        row += 1
        
        # --- 5. REVISION HISTORY (KEPT) ---
        row += 2
        ws.merge_range(f'A{row}:C{row}', "REVISION HISTORY", fmt_header)
        row += 1
        ws.write(row, 0, "Rev", fmt_cell)
        ws.write(row, 1, "Description", fmt_cell)
        ws.write(row, 2, "Date", fmt_cell)
        row += 1
        ws.write(row, 0, "B", fmt_cell)
        ws.write(row, 1, "Issued for Fabrication (Vendor Data)", fmt_cell)
        ws.write(row, 2, f"{datetime.date.today()}", fmt_cell)

    return output.getvalue()
