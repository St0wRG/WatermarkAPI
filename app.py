from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color, black
from datetime import datetime
import io, os

app = Flask(__name__)

def create_watermark(watermark_text):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    width, height = letter

    # Texte principal ("PAYÉ")
    line1 = watermark_text
    # Ligne 2 : date automatique
    line2 = datetime.today().strftime("le %d/%m/%y")

    # Styles
    size_main = 36
    size_secondary = 18
    font_main = "Helvetica-Bold"
    font_secondary = "Helvetica"

    # Couleur rouge semi-transparente (alpha ≈ 50 %)
    semi_transparent_red = Color(1, 0, 0, alpha=0.5)
    can.setFillColor(semi_transparent_red)
    can.setFont(font_main, size_main)

    # Mesure largeur du texte pour alignement à droite
    text_width_1 = can.stringWidth(line1, font_main, size_main)
    x1 = width - text_width_1 - 40

    # Position verticale : ~⅖ de la page
    y_base = height * 0.4  # ~320 sur 792 (page letter)

    # Appliquer rotation pour "PAYÉ"
    can.saveState()
    can.translate(x1, y_base)
    can.rotate(15)  # Rotation légère
    can.drawString(0, 0, line1)
    can.restoreState()

    # Date en dessous, en noir, non inclinée
    can.setFont(font_secondary, size_secondary)
    can.setFillColor(black)

    text_width_2 = can.stringWidth(line2, font_secondary, size_secondary)
    x2 = width - text_width_2 - 40
    y2 = y_base - 30  # Position de la date, plus bas que "PAYÉ"

    can.drawString(x2, y2, line2)

    can.save()
    packet.seek(0)
    return PdfReader(packet)

@app.route('/filigrane', methods=['POST'])
def watermark_pdf():
    if 'file' not in request.files:
        return {"error": "PDF file required"}, 400

    pdf_file = request.files['file']
    watermark_text = request.form.get('text', 'PAYÉ')  # Par défaut : PAYÉ

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
