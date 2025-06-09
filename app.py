from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black
from datetime import datetime
import io, os

app = Flask(__name__)

def create_watermark(watermark_text):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # Couleur noire
    can.setFillColor(black)

    width, height = letter

    # Ligne 1 : texte principal ("PAYÉ")
    line1 = watermark_text
    # Ligne 2 : date formatée automatiquement
    line2 = datetime.today().strftime("le %d/%m/%y")

    # Polices et tailles
    font_main = "Helvetica-Bold"
    font_secondary = "Helvetica"
    size_main = 36
    size_secondary = 24

    # Calcul des largeurs de texte
    text_width_1 = can.stringWidth(line1, font_main, size_main)
    text_width_2 = can.stringWidth(line2, font_secondary, size_secondary)

    # Position bas droite mais visible (marge de 40 px + hauteur personnalisée)
    y_base = 120
    x1 = width - text_width_1 - 40
    x2 = width - text_width_2 - 40

    # Dessin des deux lignes
    can.setFont(font_main, size_main)
    can.drawString(x1, y_base, line1)

    can.setFont(font_secondary, size_secondary)
    can.drawString(x2, y_base - 28, line2)

    can.save()
    packet.seek(0)
    return PdfReader(packet)

@app.route('/filigrane', methods=['POST'])
def watermark_pdf():
    if 'file' not in request.files:
        return {"error": "PDF file required"}, 400

    pdf_file = request.files['file']
    watermark_text = request.form.get('text', 'PAYÉ')  # par défaut : PAYÉ

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
