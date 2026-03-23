from fpdf import FPDF
from datetime import datetime

class ExecutiveReport(FPDF):
    def header(self):
        # Branded Header
        self.set_font('Arial', 'B', 15)
        self.set_text_color(173, 20, 87) # HDFC-ish Crimson
        self.cell(0, 10, 'GenAI Equity Research Command Center - EXECUTIVE BRIEFING', 0, 1, 'C')
        self.set_font('Arial', 'I', 8)
        self.set_text_color(128)
        self.cell(0, 10, f'Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'R')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()} | Confidential - Internal Use Only', 0, 0, 'C')

def generate_pdf_report(result, ticker):
    pdf = ExecutiveReport()
    pdf.add_page()
    
    # Summary Section
    ui = result.get('ui_payload', {})
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, f"Ticker Analysis: {ticker}", 0, 1)
    
    # Recommendation Box
    rec = ui.get('recommendation', 'HOLD')
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 15, f"OFFICIAL VERDICT: {rec}", 1, 1, 'C', 1)
    pdf.ln(5)

    # Key Metrics Table
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 10, "Key Quantitative Metrics:", 0, 1)
    pdf.set_font('Arial', '', 10)
    for m in ui.get('key_metrics', []):
        pdf.cell(0, 8, f"- {m['label']}: {m['value']}", 0, 1)
    
    pdf.ln(10)
    
    # Thesis Section
    pdf.set_font('Arial', 'B', 12)
    pdf.cell(0, 10, "Agentic Investment Thesis:", 0, 1)
    pdf.set_font('Arial', '', 11)
    # Multi-cell handles long text wrapping
    pdf.multi_cell(0, 8, result.get('analysis', 'No analysis provided.'))
    
    return pdf.output(dest='S').encode('latin-1') # Return as bytes for Streamlit