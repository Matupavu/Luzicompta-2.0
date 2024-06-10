# test_fpdf2.py

from fpdf import FPDF
import os

def create_test_pdf():
    print("Current working directory:", os.getcwd())
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(40, 10, 'Hello World!')
        pdf.output('test.pdf')
        print("PDF generated successfully.")
    except Exception as e:
        print("Error during PDF generation:", e)

# Test the function
create_test_pdf()
