import io
import xlsxwriter
from datetime import datetime

def generate_tema_sheet(project_name, inputs, results):
    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    sheet = workbook.add_worksheet("TEMA Specification")

    # Styles
    header_fmt = workbook.add_format({'bold': True, 'bg_color': '#D9E1F2', 'border': 1})
    data_fmt = workbook.add_format({'border': 1})
    num_fmt = workbook.add_format({'border': 1, 'num_format': '0.00'})

    # 1. Header Info
    sheet.merge_range('A1:E1', f"HEAT EXCHANGER SPECIFICATION SHEET - {project_name}", header_fmt)
    sheet.write('A2', f"Date: {datetime.now().strftime('%Y-%m-%d')}", data_fmt)
    
    # 2. Process Conditions Table
    sheet.write('A4', "PERFORMANCE DATA", header_fmt)
    headers = ["Parameter", "Shell Side", "Tube Side"]
    for col, h in enumerate(headers):
        sheet.write(4, col, h, header_fmt)
        
    data = [
        ("Fluid", inputs['cold_fluid'], inputs['hot_fluid']),
        ("Flow Rate (kg/s)", inputs['m_cold'], inputs['m_hot']),
        ("Temperature In (°C)", inputs['T_cold_in'], inputs['T_hot_in']),
        ("Temperature Out (°C)", results['T_cold_out'], results['T_hot_out']),
        ("Velocity (m/s)", results['v_shell'], results['v_tube']),
        ("Pressure Drop (kPa)", 0.0, 0.0) # Placeholder for full dP calc
    ]
    
    row = 5
    for label, shell_val, tube_val in data:
        sheet.write(row, 0, label, data_fmt)
        # Handle mixed types (strings vs numbers)
        fmt_s = num_fmt if isinstance(shell_val, (int, float)) else data_fmt
        fmt_t = num_fmt if isinstance(tube_val, (int, float)) else data_fmt
        
        sheet.write(row, 1, shell_val, fmt_s)
        sheet.write(row, 2, tube_val, fmt_t)
        row += 1
        
    # 3. Mechanical Data
    row += 2
    sheet.write(row, 0, "CONSTRUCTION DETAILS", header_fmt)
    mech_data = [
        ("Shell Diameter", f"{inputs['shell_id']} m"),
        ("Tube Length", f"{inputs['length']} m"),
        ("Tube Count", inputs['n_tubes']),
        ("Tube OD", "19.05 mm"),
        ("Baffle Spacing", f"{inputs['baffle_spacing']} m"),
        ("Material", "Carbon Steel") # Simplified
    ]
    
    row += 1
    for label, val in mech_data:
        sheet.write(row, 0, label, data_fmt)
        sheet.write(row, 1, val, data_fmt)
        row += 1

    workbook.close()
    output.seek(0)
    return output

