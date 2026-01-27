from fpdf import FPDF
import datetime

class PDFQuote(FPDF):
    def header(self):
        # Professional Header with Gray Background
        self.set_fill_color(50, 60, 70) # Dark Slate Gray
        self.rect(0, 0, 210, 40, 'F')
        
        self.set_font('Arial', 'B', 20)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'ExchangerAI Solutions', 0, 1, 'L')
        
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Advanced Thermal Engineering & Fabrication', 0, 1, 'L')
        self.cell(0, 5, 'License: ASME U-Stamp | ISO 9001:2015', 0, 1, 'L')
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Confidential Commercial Proposal', 0, 0, 'C')

def create_pdf_quote(project_name, inputs, results, price):
    pdf = PDFQuote()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # DOCUMENT CONTROL BLOCK
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(120, 6, f"To: Client Engineering Team", 0, 0)
    pdf.cell(70, 6, f"Ref No: Q-{datetime.date.today().strftime('%Y%m%d')}-001", 0, 1, 'R')
    pdf.cell(120, 6, f"Project: {project_name}", 0, 0)
    pdf.cell(70, 6, f"Date: {datetime.date.today().strftime('%d-%b-%Y')}", 0, 1, 'R')
    pdf.cell(120, 6, f"Subject: Budgetary Offer for {inputs.get('tema_type')} Exchanger", 0, 0)
    pdf.cell(70, 6, "Validity: 30 Days", 0, 1, 'R')
    
    pdf.ln(10)
    
    # 1. EXECUTIVE SUMMARY
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(190, 8, "  1. EXECUTIVE SUMMARY", 0, 1, 'L', 1)
    pdf.ln(2)
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(190, 5, 
        f"We are pleased to submit our offer for the design, fabrication, and supply of 1 No. Shell & Tube Heat Exchanger "
        f"({inputs.get('tema_type')} Type) in accordance with ASME Sec VIII Div 1 and TEMA Class R standards. "
        "The unit is thermally guaranteed to meet the specified process duty."
    )
    pdf.ln(5)

    # 2. TECHNICAL SPECIFICATIONS
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 8, "  2. TECHNICAL BASIS OF DESIGN", 0, 1, 'L', 1)
    pdf.ln(2)
    
    # Table Header
    pdf.set_font("Arial", 'B', 9)
    pdf.set_fill_color(245, 245, 245)
    pdf.cell(95, 6, "Process Parameters", 1, 0, 'C', 1)
    pdf.cell(95, 6, "Mechanical Construction", 1, 1, 'C', 1)
    
    # Table Content
    pdf.set_font("Arial", '', 9)
    # Row 1
    pdf.cell(45, 6, "Fluid (Shell/Tube):", 1); pdf.cell(50, 6, f"{inputs.get('cold_fluid')} / {inputs.get('hot_fluid')}", 1)
    pdf.cell(45, 6, "TEMA Type:", 1); pdf.cell(50, 6, f"{inputs.get('tema_type')} (Class R)", 1, 1)
    # Row 2
    pdf.cell(45, 6, "Heat Duty:", 1); pdf.cell(50, 6, f"{results['Q']/1000:.1f} kW", 1)
    pdf.cell(45, 6, "Design Pressure:", 1); pdf.cell(50, 6, f"{inputs.get('des_press_shell')} / {inputs.get('des_press_tube')} bar", 1, 1)
    # Row 3
    pdf.cell(45, 6, "Surface Area:", 1); pdf.cell(50, 6, f"{results['Area']:.1f} m2", 1)
    pdf.cell(45, 6, "Design Temp:", 1); pdf.cell(50, 6, f"{inputs.get('des_temp_shell')} / {inputs.get('des_temp_tube')} C", 1, 1)
    # Row 4
    pdf.cell(45, 6, "Calculated U-Value:", 1); pdf.cell(50, 6, f"{results['U']:.1f} W/m2K", 1)
    pdf.cell(45, 6, "MOC (Shell/Tube):", 1); pdf.cell(50, 6, f"{inputs.get('mat_shell')} / {inputs.get('mat_tube')}", 1, 1)
    # Row 5
    pdf.cell(45, 6, "Fouling Factor:", 1); pdf.cell(50, 6, "0.0002 hr-m2-K/W", 1)
    pdf.cell(45, 6, "Corrosion Allow:", 1); pdf.cell(50, 6, f"{inputs.get('corr_allow')} mm", 1, 1)

    pdf.ln(5)

    # 3. COMMERCIAL PRICE SCHEDULE
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 8, "  3. PRICE SCHEDULE (Currency: USD)", 0, 1, 'L', 1)
    pdf.ln(2)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 8, "Description of Supply", 1, 0, 'C')
    pdf.cell(50, 8, "Total Price", 1, 1, 'C')
    
    pdf.set_font("Arial", '', 10)
    pdf.cell(140, 8, f"1. Supply of {inputs.get('tema_type')} Heat Exchanger (Complete Unit)", 1)
    pdf.cell(50, 8, f"${price:,.2f}", 1, 1, 'R')
    
    pdf.cell(140, 8, "2. Mechanical Design, Drawings & TEMA Datasheet", 1)
    pdf.cell(50, 8, "$1,800.00", 1, 1, 'R')
    
    pdf.cell(140, 8, "3. Third Party Inspection (TPI) Charges", 1)
    pdf.cell(50, 8, "$1,200.00", 1, 1, 'R')
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 8, "TOTAL EX-WORKS VALUE", 1, 0, 'R')
    pdf.set_text_color(200, 0, 0)
    pdf.cell(50, 8, f"${price + 3000:,.2f}", 1, 1, 'R')
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(10)
    
    # 4. SCOPE & EXCLUSIONS
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, "4. SCOPE OF SUPPLY:", 0, 1)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, "- Complete vessel with shell, tubes, baffles, and channels.\n- Counter flanges with fasteners and gaskets.\n- Saddle supports welded to shell.\n- Primer painting (1 coat).")
    
    pdf.ln(5)
    
    # Check for page break space before Exclusions
    if pdf.get_y() > 240: pdf.add_page()
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, "5. EXCLUSIONS:", 0, 1)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, "- Civil foundations and anchor bolts.\n- External piping, valves, and instruments.\n- Thermal insulation and cladding.\n- Site erection and commissioning.")

    pdf.ln(8)

    # 5. COMMERCIAL TERMS
    # Check for page break space before Terms
    if pdf.get_y() > 220: pdf.add_page()

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, "6. COMMERCIAL TERMS & CONDITIONS:", 0, 1)
    pdf.set_font("Arial", '', 8)
    pdf.multi_cell(0, 5, 
        "1. DELIVERY: 14-16 Weeks from drawing approval.\n"
        "2. PAYMENT: 30% Advance, 60% Against Proforma Invoice, 10% against Performance Bank Guarantee (PBG).\n"
        "3. WARRANTY: 12 months from commissioning or 18 months from dispatch.\n"
        "4. FORCE MAJEURE: Standard clauses apply as per ICC 2020.\n"
        "5. VALIDITY: This offer is valid for 30 days."
    )

    return pdf.output(dest='S').encode('latin-1')
