from fpdf import FPDF
import datetime

class PDFQuote(FPDF):
    def header(self):
        # --- PROFESSIONAL HEADER (KEPT) ---
        # Dark Gray Background
        self.set_fill_color(50, 60, 70) 
        self.rect(0, 0, 210, 40, 'F')
        
        # Company Title
        self.set_font('Arial', 'B', 20)
        self.set_text_color(255, 255, 255)
        self.cell(0, 15, 'ExchangerAI Solutions', 0, 1, 'L')
        
        # Subtitles
        self.set_font('Arial', '', 10)
        self.cell(0, 5, 'Advanced Thermal Engineering & Fabrication', 0, 1, 'L')
        self.cell(0, 5, 'License: ASME U-Stamp | ISO 9001:2015', 0, 1, 'L')
        self.ln(20)

    def footer(self):
        # --- PROFESSIONAL FOOTER (KEPT) ---
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f'Page {self.page_no()} | Confidential Commercial Proposal', 0, 0, 'C')

def create_pdf_quote(project_name, inputs, results, price):
    pdf = PDFQuote()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # --- DOCUMENT CONTROL BLOCK (KEPT) ---
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(0, 0, 0)
    
    # Row 1
    pdf.cell(120, 6, f"To: Client Engineering Team", 0, 0)
    pdf.cell(70, 6, f"Ref No: Q-{datetime.date.today().strftime('%Y%m%d')}-001", 0, 1, 'R')
    
    # Row 2
    pdf.cell(120, 6, f"Project: {project_name}", 0, 0)
    pdf.cell(70, 6, f"Date: {datetime.date.today().strftime('%d-%b-%Y')}", 0, 1, 'R')
    
    # Row 3
    pdf.cell(120, 6, f"Subject: Budgetary Offer for {inputs.get('tema_type')} Exchanger", 0, 0)
    pdf.cell(70, 6, "Validity: 30 Days", 0, 1, 'R')
    
    pdf.ln(10)
    
    # --- 1. EXECUTIVE SUMMARY (KEPT) ---
    pdf.set_font("Arial", 'B', 12)
    pdf.set_fill_color(230, 230, 230) # Light Gray Section Header
    pdf.cell(190, 8, "  1. EXECUTIVE SUMMARY", 0, 1, 'L', 1)
    pdf.ln(2)
    
    pdf.set_font("Arial", '', 10)
    pdf.multi_cell(190, 5, 
        f"We are pleased to submit our offer for the design, fabrication, and supply of 1 No. Shell & Tube Heat Exchanger "
        f"({inputs.get('tema_type')} Type) in accordance with ASME Sec VIII Div 1 and TEMA Class R standards. "
        "The unit is thermally guaranteed to meet the specified process duty."
    )
    pdf.ln(5)

    # --- 2. TECHNICAL SPECIFICATIONS (UPGRADED: Expanded Table) ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 8, "  2. TECHNICAL BASIS OF DESIGN", 0, 1, 'L', 1)
    pdf.ln(2)
    
    pdf.set_font("Arial", '', 9)
    
    # Custom Table Function for cleaner code
    def add_tech_row(label, value):
        pdf.cell(60, 6, label, 1)
        pdf.cell(130, 6, value, 1, 1)

    add_tech_row("TEMA Type", f"{inputs.get('tema_type')} (Class R)")
    add_tech_row("Total Heat Duty", f"{results['Q']/1000:.1f} kW")
    add_tech_row("Heat Transfer Area", f"{results['Area']:.1f} m2")
    add_tech_row("Design Pressure (Shell/Tube)", f"{inputs.get('des_press_shell')} bar / {inputs.get('des_press_tube')} bar")
    add_tech_row("Design Temperature (Shell/Tube)", f"{inputs.get('des_temp_shell')} C / {inputs.get('des_temp_tube')} C")
    add_tech_row("Materials (Shell/Tube)", f"{inputs.get('mat_shell')} / {inputs.get('mat_tube')}")
    add_tech_row("Corrosion Allowance", f"{inputs.get('corr_allow')} mm")
    
    # --- NEW ADDITION: Disclaimer ---
    pdf.ln(2)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(190, 4, "*Performance is guaranteed at specified design conditions. Fouling factors are assumed as per standard service requirements.")
    pdf.ln(5)

    # --- 3. COMMERCIAL PRICE SCHEDULE (KEPT) ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 8, "  3. PRICE SCHEDULE (Currency: USD)", 0, 1, 'L', 1)
    pdf.ln(2)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 8, "Description of Supply", 1, 0, 'C')
    pdf.cell(50, 8, "Total Price", 1, 1, 'C')
    
    pdf.set_font("Arial", '', 10)
    # Item 1
    pdf.cell(140, 8, f"1. Supply of {inputs.get('tema_type')} Heat Exchanger (Complete Unit)", 1)
    pdf.cell(50, 8, f"${price:,.2f}", 1, 1, 'R')
    
    # Item 2
    pdf.cell(140, 8, "2. Mechanical Design, Drawings & TEMA Datasheet", 1)
    pdf.cell(50, 8, "$1,800.00", 1, 1, 'R')
    
    # Item 3
    pdf.cell(140, 8, "3. Third Party Inspection (TPI) Charges", 1)
    pdf.cell(50, 8, "$1,200.00", 1, 1, 'R')
    
    # Total
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(140, 8, "TOTAL EX-WORKS VALUE", 1, 0, 'R')
    pdf.set_text_color(200, 0, 0)
    pdf.cell(50, 8, f"${price + 3000:,.2f}", 1, 1, 'R')
    pdf.set_text_color(0, 0, 0)
    
    pdf.ln(8)
    
    # --- 4. SCOPE & EXCLUSIONS (KEPT) ---
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, "4. SCOPE OF SUPPLY:", 0, 1)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, "- Complete vessel with shell, tubes, baffles, and channels.\n- Counter flanges with fasteners and gaskets.\n- Saddle supports welded to shell.\n- Primer painting (1 coat).")
    
    pdf.ln(5)
    
    # Page Break Logic
    if pdf.get_y() > 230: pdf.add_page()
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, "5. EXCLUSIONS:", 0, 1)
    pdf.set_font("Arial", '', 9)
    pdf.multi_cell(0, 5, "- Civil foundations and anchor bolts.\n- External piping, valves, and instruments.\n- Thermal insulation and cladding.\n- Site erection and commissioning.")

    pdf.ln(8)

    # --- 5. COMMERCIAL TERMS (UPGRADED: Expanded Legal Text) ---
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

    pdf.ln(10)

    # --- 6. SIGNATURE BLOCK (NEW ADDITION) ---
    # Ensure this block stays together
    if pdf.get_y() > 240: pdf.add_page()

    pdf.set_font("Arial", 'B', 10)
    pdf.cell(0, 6, "7. AUTHORIZATION:", 0, 1)
    pdf.ln(10)
    
    y = pdf.get_y()
    
    # Signature Lines
    pdf.line(10, y, 90, y) # Left Line
    pdf.line(120, y, 200, y) # Right Line
    
    pdf.ln(2)
    
    # Left Side
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(110, 5, "Authorized Signatory", 0, 0)
    # Right Side
    pdf.cell(80, 5, "Accepted By (Client)", 0, 1)
    
    pdf.set_font("Arial", '', 8)
    pdf.cell(110, 5, "ExchangerAI Solutions", 0, 0)
    pdf.cell(80, 5, "Name & Stamp", 0, 1)

    return pdf.output(dest='S').encode('latin-1')
