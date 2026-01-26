from fpdf import FPDF
from datetime import datetime

class PDFQuote(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'ExchangerAI - Commercial Proposal', 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf_quote(project_name, inputs, results, cost_est):
    pdf = PDFQuote()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # 1. Project Header
    pdf.cell(200, 10, txt=f"Project Ref: {project_name}", ln=1)
    pdf.cell(200, 10, txt=f"Date: {datetime.now().strftime('%Y-%m-%d')}", ln=1)
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    # 2. Executive Summary
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="1. Technical Summary", ln=1)
    pdf.set_font("Arial", size=10)
    
    summary = [
        f"Duty: {results['Q']/1000:.1f} kW",
        f"Surface Area: {results['Area']:.1f} m2",
        f"Shell Diameter: {inputs['shell_id']} m",
        f"Tube Length: {inputs['length']} m",
        f"Design Pressure: 10 Bar (g)"
    ]
    
    for line in summary:
        pdf.cell(200, 8, txt=f"- {line}", ln=1)
    
    pdf.ln(5)
    
    # 3. Commercials
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="2. Investment", ln=1)
    pdf.set_font("Arial", size=10)
    
    # Simple Cost Logic for Demo
    base_cost = cost_est if cost_est else 15000 
    
    pdf.cell(100, 10, "Equipment Cost (FOB):", border=1)
    pdf.cell(50, 10, f"${base_cost:,.2f}", border=1, ln=1)
    
    pdf.cell(100, 10, "Engineering & Design:", border=1)
    pdf.cell(50, 10, f"${base_cost*0.15:,.2f}", border=1, ln=1)
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(100, 10, "TOTAL PRICE:", border=1)
    pdf.cell(50, 10, f"${base_cost*1.15:,.2f}", border=1, ln=1)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 8)
    pdf.multi_cell(0, 5, "Terms: Valid for 30 days. 50% Advance, 50% prior to dispatch. Lead time: 8-10 Weeks.")
    
    return pdf.output(dest='S').encode('latin-1')

