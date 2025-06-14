from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color
from datetime import datetime
import io, os

app = Flask(__name__)

def create_watermark(watermark_text):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    width, height = letter

    # Lignes de texte
    line1 = watermark_text
    line2 = datetime.today().strftime("le %d/%m/%y")

    # Styles
    size_main = 36
    size_secondary = 10
    rotation_angle = 15
    font_main = "Helvetica-Bold"
    font_secondary = "Helvetica"

    # Couleurs semi-transparentes
    red_transparent = Color(1, 0, 0, alpha=0.5)
    black_transparent = Color(0, 0, 0, alpha=0.5)

    # Mesures des textes
    text_width_1 = can.stringWidth(line1, font_main, size_main)
    text_width_2 = can.stringWidth(line2, font_secondary, size_secondary)

    max_width = max(text_width_1, text_width_2)
    x_align = width - max_width - 40
    y_base = height * 0.4

    # PAYÉ
    can.saveState()
    can.translate(x_align, y_base)
    can.rotate(rotation_angle)
    can.setFillColor(red_transparent)
    can.setFont(font_main, size_main)
    can.drawString(max_width - text_width_1, 0, line1)

    # Date
    can.setFillColor(black_transparent)
    can.setFont(font_secondary, size_secondary)
    can.drawString(max_width - text_width_2, -24, line2)
    can.restoreState()

    can.save()
    packet.seek(0)
    return PdfReader(packet)

@app.route('/filigrane', methods=['POST'])
def watermark_pdf():
    if 'file' not in request.files:
        return {"error": "PDF file required"}, 400

    pdf_file = request.files['file']
    watermark_text = request.form.get('text', 'PAYÉ')

    pdf_reader = PdfReader(pdf_file)
    pdf_writer = PdfWriter()
    watermark = create_watermark(watermark_text).pages[0]

    for page in pdf_reader.pages:
        page.merge_page(watermark)
        pdf_writer.add_page(page)

    output_pdf = io.BytesIO()
    pdf_writer.write(output_pdf)
    output_pdf.seek(0)

    return send_file(output_pdf, download_name="watermarked.pdf", as_attachment=True)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)
