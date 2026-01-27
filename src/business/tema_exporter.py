import pandas as pd
import io
import datetime

def generate_tema_sheet(project_name, inputs, results):
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        workbook = writer.book
        ws = workbook.add_worksheet("TEMA Data")
        
        # --- STYLES ---
        # Headers (Blue Background)
        fmt_header = workbook.add_format({
            'bold': True, 'bg_color': '#1F497D', 'font_color': 'white', 
            'border': 1, 'align': 'center', 'valign': 'vcenter'
        })
        # Section Titles (Grey)
        fmt_section = workbook.add_format({
            'bold': True, 'bg_color': '#D9D9D9', 'border': 1, 'align': 'left'
        })
        # Data Cells (Boxed)
        fmt_cell = workbook.add_format({'border': 1, 'align': 'center'})
        fmt_cell_left = workbook.add_format({'border': 1, 'align': 'left'})
        # Title Block
        fmt_title = workbook.add_format({
            'bold': True, 'font_size': 14, 'align': 'center', 'border': 2
        })
        
        # --- LAYOUT ---
        # Set Columns Widths
        ws.set_column('A:A', 30) # Parameter Name
        ws.set_column('B:B', 20) # Shell Side
        ws.set_column('C:C', 20) # Tube Side
        
        # 1. TITLE BLOCK
        ws.merge_range('A1:C2', "HEAT EXCHANGER SPECIFICATION SHEET (TEMA R)", fmt_title)
        ws.write('A3', f"Project: {project_name}", fmt_cell_left)
        ws.write('B3', f"Date: {datetime.date.today()}", fmt_cell)
        ws.write('C3', "Rev: A", fmt_cell)
        
        # 2. PERFORMANCE DATA SECTION
        row = 4
        ws.merge_range(f'A{row}:C{row}', "1. PERFORMANCE DATA", fmt_section)
        row += 1
        
        # Headers
        ws.write(row, 0, "PARAMETER", fmt_header)
        ws.write(row, 1, "SHELL SIDE", fmt_header)
        ws.write(row, 2, "TUBE SIDE", fmt_header)
        row += 1
        
        # Performance Rows
        perf_data = [
            ("Fluid Name", inputs.get('cold_fluid'), inputs.get('hot_fluid')),
            ("Mass Flow Rate (kg/s)", inputs.get('m_cold'), inputs.get('m_hot')),
            ("Inlet Temperature (°C)", inputs.get('T_cold_in'), inputs.get('T_hot_in')),
            ("Outlet Temperature (°C)", f"{results['T_cold_out']:.1f}", f"{results['T_hot_out']:.1f}"),
            ("Operating Pressure (bar)", "1.0", "1.0"),
            ("Allowable Pressure Drop (bar)", "0.5", "0.5"),
            ("Calculated Velocity (m/s)", f"{results['v_shell']:.2f}", f"{results['v_tube']:.2f}"),
            ("Fouling Resistance", "0.0002", "0.0002")
        ]
        
        for label, shell_val, tube_val in perf_data:
            ws.write(row, 0, label, fmt_cell_left)
            ws.write(row, 1, shell_val, fmt_cell)
            ws.write(row, 2, tube_val, fmt_cell)
            row += 1
            
        # Calculated Summary
        ws.merge_range(f'A{row}:C{row}', "--- THERMAL SUMMARY ---", fmt_cell)
        row += 1
        ws.write(row, 0, "Total Heat Duty (kW)", fmt_cell_left)
        ws.merge_range(f'B{row}:C{row}', f"{results['Q']/1000:.2f}", fmt_cell)
        row += 1
        ws.write(row, 0, "Service U-Value (W/m2K)", fmt_cell_left)
        ws.merge_range(f'B{row}:C{row}', f"{results['U']:.2f}", fmt_cell)
        row += 1
        
        # 3. MECHANICAL DATA SECTION (Merged Visuals + New Data)
        row += 1
        ws.merge_range(f'A{row}:C{row}', "2. CONSTRUCTION DETAILS", fmt_section)
        row += 1
        
        mech_data = [
            ("TEMA Type", inputs.get('tema_type'), ""),
            ("Design Pressure (bar g)", inputs.get('des_press_shell'), inputs.get('des_press_tube')),
            ("Design Temperature (°C)", inputs.get('des_temp_shell'), inputs.get('des_temp_tube')),
            ("Material of Construction", inputs.get('mat_shell'), inputs.get('mat_tube')),
            ("Corrosion Allowance (mm)", inputs.get('corr_allow'), "-"),
            ("Nozzle Size (In/Out)", inputs.get('noz_in'), inputs.get('noz_out')),
            ("Shell ID / Tube OD (m)", inputs.get('shell_id'), inputs.get('tube_od')),
            ("Tube Length (m)", inputs.get('length'), ""),
            ("Tube Pitch / Layout", "1.25", inputs.get('tube_layout')),
            ("Baffles", f"Type: Single Seg, Cut: {inputs.get('baffle_cut')}%", f"Spacing: {inputs.get('baffle_spacing')} m")
        ]
        
        for label, shell_val, tube_val in mech_data:
            ws.write(row, 0, label, fmt_cell_left)
            # Check if second value is empty (merge cells)
            if tube_val == "":
                ws.merge_range(f'B{row}:C{row}', shell_val, fmt_cell)
            else:
                ws.write(row, 1, shell_val, fmt_cell)
                ws.write(row, 2, tube_val, fmt_cell)
            row += 1

        # 4. REVISION BLOCK (The "Real Company" Touch)
        row += 2
        ws.merge_range(f'A{row}:C{row}', "REVISION HISTORY", fmt_header)
        row += 1
        ws.write(row, 0, "Rev", fmt_cell)
        ws.write(row, 1, "Description", fmt_cell)
        ws.write(row, 2, "Date", fmt_cell)
        row += 1
        ws.write(row, 0, "A", fmt_cell)
        ws.write(row, 1, "Issued for Approval", fmt_cell)
        ws.write(row, 2, f"{datetime.date.today()}", fmt_cell)

    return output.getvalue()
