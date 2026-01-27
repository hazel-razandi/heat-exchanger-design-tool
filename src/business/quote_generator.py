from fpdf import FPDF

class PDFQuote(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'ExchangerAI - Commercial Proposal', 0, 1, 'C')
        self.ln(10)

def create_pdf_quote(project_name, inputs, results, price):
    pdf = PDFQuote()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Header Info
    pdf.cell(200, 10, txt=f"Project Ref: {project_name}", ln=True)
    pdf.cell(200, 10, txt=f"Configuration: {inputs.get('tema_type')} Heat Exchanger", ln=True)
    pdf.ln(5)
    
    # 1. Performance Summary
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="1. Performance Guarantee", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 6, txt=f"- Rated Duty: {results['Q']/1000:.1f} kW", ln=True)
    pdf.cell(200, 6, txt=f"- Service U-Value: {results['U']:.1f} W/m2K", ln=True)
    pdf.cell(200, 6, txt=f"- Surface Area: {results['Area']:.1f} m2", ln=True)
    pdf.ln(5)
    
    # 2. Mechanical Specs (NEW)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="2. Mechanical Specifications", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 6, txt=f"- Design Pressure: {inputs.get('des_press_shell')} bar (Shell) / {inputs.get('des_press_tube')} bar (Tube)", ln=True)
    pdf.cell(200, 6, txt=f"- Design Temperature: {inputs.get('des_temp_shell')} C (Shell) / {inputs.get('des_temp_tube')} C (Tube)", ln=True)
    pdf.cell(200, 6, txt=f"- Materials: {inputs.get('mat_shell')} (Shell) / {inputs.get('mat_tube')} (Tubes)", ln=True)
    pdf.cell(200, 6, txt=f"- Corrosion Allowance: {inputs.get('corr_allow')} mm", ln=True)
    pdf.ln(5)
    
    # 3. Commercial
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="3. Commercial Offer", ln=True)
    pdf.set_font("Arial", size=10)
    pdf.cell(200, 6, txt=f"Total Price (Ex Works): ${price:,.2f}", ln=True)
    pdf.cell(200, 6, txt="Delivery: 14-16 Weeks", ln=True)
    pdf.cell(200, 6, txt="Validity: 30 Days", ln=True)
    
    return pdf.output(dest='S').encode('latin-1')
