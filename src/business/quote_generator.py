"""
Professional PDF Quote Generator
"""
from fpdf import FPDF
from datetime import datetime

class PDFQuote(FPDF):
    def header(self):
        # Company Logo Area (Text for now)
        self.set_font('Arial', 'B', 16)
        self.set_text_color(30, 58, 138) # Dark Blue
        self.cell(0, 10, 'ExchangerAI Solutions', 0, 1, 'L')
        self.set_font('Arial', '', 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, 'Industrial Thermal Engineering', 0, 1, 'L')
        self.ln(5)
        self.line(10, 25, 200, 25) # Horizontal Line
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Page {self.page_no()} | Generated via ExchangerAI Enterprise SaaS', 0, 0, 'C')

def create_pdf_quote(project_name, inputs, results, cost_est):
    pdf = PDFQuote()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # 1. Client Info Block
    pdf.set_font("Arial", 'B', 12)
    pdf.set_text_color(0)
    pdf.cell(100, 8, f"Project Reference: {project_name}", 0, 0)
    pdf.cell(90, 8, f"Date: {datetime.now().strftime('%Y-%m-%d')}", 0, 1, 'R')
    pdf.ln(5)
    
    # 2. Executive Summary (Boxed)
    pdf.set_fill_color(240, 240, 240) # Light Grey
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "  1. TECHNICAL SUMMARY", 0, 1, 'L', fill=True)
    pdf.ln(2)
    
    pdf.set_font("Arial", size=10)
    specs = [
        ("Design Duty", f"{results['Q']/1000:.1f} kW"),
        ("Heat Transfer Area", f"{results['Area']:.1f} m2"),
        ("Overall U-Value", f"{results['U']:.1f} W/m2K"),
        ("Shell Diameter", f"{inputs['shell_id']} m"),
        ("Tube Material", "Carbon Steel (A516)"),
        ("Design Pressure", "10.0 Bar(g)")
    ]
    
    for label, val in specs:
        pdf.cell(50, 7, label + ":", 0, 0)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(50, 7, val, 0, 1)
        pdf.set_font("Arial", size=10)
        
    pdf.ln(5)

    # 3. Commercial Investment (Table Look)
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 8, "  2. COMMERCIAL PROPOSAL", 0, 1, 'L', fill=True)
    pdf.ln(4)
    
    # Cost Logic (Mock)
    base_cost = cost_est if cost_est else 15000.00
    engineering = base_cost * 0.15
    shipping = 1200.00
    total = base_cost + engineering + shipping
    
    # Table Header
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(120, 8, "Description", 1, 0, 'L')
    pdf.cell(70, 8, "Amount (USD)", 1, 1, 'R')
    
    # Table Rows
    pdf.set_font("Arial", '', 10)
    pdf.cell(120, 8, "Heat Exchanger Fabrication (FOB Factory)", 1, 0, 'L')
    pdf.cell(70, 8, f"${base_cost:,.2f}", 1, 1, 'R')
    
    pdf.cell(120, 8, "Mechanical Design & TEMA Drawings", 1, 0, 'L')
    pdf.cell(70, 8, f"${engineering:,.2f}", 1, 1, 'R')
    
    pdf.cell(120, 8, "Packaging & Handling", 1, 0, 'L')
    pdf.cell(70, 8, f"${shipping:,.2f}", 1, 1, 'R')
    
    # Total Row
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(120, 10, "TOTAL PROJECT VALUE", 1, 0, 'R')
    pdf.set_text_color(30, 58, 138) # Blue
    pdf.cell(70, 10, f"${total:,.2f}", 1, 1, 'R')
    pdf.set_text_color(0)
    
    pdf.ln(10)
    
    # 4. Terms & Conditions (Fine Print)
    pdf.set_font("Arial", 'B', 9)
    pdf.cell(0, 6, "Standard Terms & Conditions:", 0, 1)
    pdf.set_font("Arial", '', 8)
    terms = [
        "1. Validity: This proposal is valid for 30 days from the date of issue.",
        "2. Payment: 50% Advance with Purchase Order, 50% Prior to Dispatch.",
        "3. Delivery: Estimated 8-10 weeks ex-works.",
        "4. Exclusions: Site installation, civil works, and external piping are not included."
    ]
    for t in terms:
        pdf.cell(0, 5, t, 0, 1)

    return pdf.output(dest='S').encode('latin-1')
