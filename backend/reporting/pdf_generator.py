from fpdf import FPDF # fpdf2 also uses 'from fpdf import FPDF' but is more modern
import os

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'Traffic Violation Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_violation_report(violation_data, image_path, output_path, plate_image_path=None):
    pdf = PDFReport()
    pdf.add_page()
    
    # Metadata
    pdf.set_font("Arial", size=12)
    
    # Define line height
    lh = 10 
    
    pdf.cell(200, lh, txt=f"Date: {violation_data.get('date', 'Unknown')}", ln=1, align='L')
    pdf.cell(200, lh, txt=f"Time: {violation_data.get('time', 'Unknown')}", ln=1, align='L')
    pdf.cell(200, lh, txt=f"Vehicle ID: {violation_data.get('vehicle_id', 'Unknown')}", ln=1, align='L')
    pdf.cell(200, lh, txt=f"Violation Type: {violation_data.get('type', 'Unknown')}", ln=1, align='L')
    
    # Add Main Image
    if os.path.exists(image_path):
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(200, 10, txt="Violation Context:", ln=1, align='L')
        # Center image, approx 160mm width
        pdf.image(image_path, x=25, w=160)
        pdf.ln(5)
    else:
        pdf.cell(200, lh, txt="[Main Image Not Available]", ln=1, align='C')
        
    # Add Plate Image (Crop)
    if plate_image_path and os.path.exists(plate_image_path):
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(200, 10, txt="Vehicle/Plate Crop:", ln=1, align='L')
        # Smaller image for plate, centered
        pdf.image(plate_image_path, x=60, w=90)
        pdf.ln(10)
        
    pdf.output(output_path)
    return output_path
