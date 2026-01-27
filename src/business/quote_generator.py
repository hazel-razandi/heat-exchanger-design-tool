"""
Professional PDF Quote Generator
"""
from fpdf import FPDF
from datetime import datetime

class ProfessionalQuote(FPDF):
    def header(self):
        # Logo / Company Name
        self.set_font('Arial', 'B', 20)
        self.set_text_color(44, 62, 80) # Dark Navy
        self.cell(0, 10, 'ExchangerAI Solutions', 0, 1, 'L')
        
        # Subheader
        self.set_font('Arial', '', 10)
        self.set_text_color(127, 140, 141) # Grey
        self.cell(0, 5, 'Advanced Thermal Engineering Systems', 0, 1, 'L')
        
        # Line break
        self.ln(10)
        self.set_draw_color(189, 195, 199)
        self.line(10, 30, 200, 30) # Horizontal line

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()} | Quote Ref: EX-{datetime.now().strftime("%Y%m%d")}', 0, 0, 'C')

def create_pdf_quote(project_name, inputs, results, cost_est):
    pdf = ProfessionalQuote()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- CLIENT INFO ---
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(100, 8, f"Project: {project_name}", 0, 0)
    pdf.cell(90, 8, f"Date: {datetime.now().strftime('%d-%b-%Y')}", 0, 1, 'R')
    pdf.ln(5)

    # --- SECTION 1: TECHNICAL SUMMARY (Grey Box) ---
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "  1. TECHNICAL SPECIFICATIONS", 0, 1, 'L', fill=True)
    pdf.ln(2)

    # Specs List
    pdf.set_font("Arial", size=10)
    
    # FIXED LINE BELOW
    area_val = results.get('Area', 0)
    duty_val = results.get('Q', 0) / 1000
    
    specs = [
        ("Design Duty", f"{duty_val:.1f} kW"),
        ("Heat Transfer Area", f"{area_val:.1f} m2"),
        ("Shell Diameter", f"{inputs.get('shell_id', 0)} m"),
        ("Tube Material", "Carbon Steel A516"),
        ("Design Code", "ASME Sec VIII Div 1 / TEMA Class R")
    ]
    
    for label, val in specs:
        pdf.cell(60, 7, label, 0, 0)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(60, 7, f":  {val}", 0, 1)
        pdf.set_font("Arial", size=10)
    
    pdf.ln(8)

    # --- SECTION 2: COMMERCIAL OFFER (Table) ---
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "  2. COMMERCIAL PROPOSAL", 0, 1, 'L', fill=True)
    pdf.ln(4)

    # Table Header
    pdf.set_fill_color(52, 73, 94) # Dark Header
    pdf.set_text_color(255, 255, 255) # White Text
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(130, 8, "Description", 1, 0, 'L', fill=True)
    pdf.cell(60, 8, "Amount (USD)", 1, 1, 'R', fill=True)

    # Table Rows
    pdf.set_text_color(0) # Back to Black
    pdf.set_font("Arial", '', 10)
    
    # Cost Logic
    base = cost_est if cost_est else 12500.00
    eng_fee = base * 0.12
    doc_fee = 500.00
    total = base + eng_fee + doc_fee

    items = [
        ("Shell & Tube Heat Exchanger (Fabrication)", base),
        ("Mechanical Design & Engineering Drawings", eng_fee),
        ("TEMA Datasheet & Documentation", doc_fee)
    ]

    for desc, amt in items:
        pdf.cell(130, 8, desc, 1, 0, 'L')
        pdf.cell(60, 8, f"${amt:,.2f}", 1, 1, 'R')

    # Total
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(130, 10, "TOTAL INVESTMENT", 1, 0, 'R')
    pdf.set_text_color(192, 57, 43) # Red for money
    pdf.cell(60, 10, f"${total:,.2f}", 1, 1, 'R')
    
    pdf.ln(10)
    
    # --- SECTION 3: TERMS (Fine Print) ---
    pdf.set_text_color(0)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(0, 6, "Standard Terms & Conditions:", 0, 1)
    
    pdf.set_font("Arial", '', 8)
    terms = [
        "1. Validity: Proposal valid for 30 days.",
        "2. Payment Terms: 40% Advance, 60% Prior to Dispatch.",
        "3. Delivery: Ex-Works, 8-10 Weeks from Drawing Approval.",
        "4. Warranty: 12 months from commissioning or 18 months from supply."
    ]
    for term in terms:
        pdf.cell(0, 5, term, 0, 1)

    return pdf.output(dest='S').encode('latin-1')
