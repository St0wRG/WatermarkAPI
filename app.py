from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import red, black
from datetime import datetime
import io, os

app = Flask(__name__)

def create_watermark(watermark_text):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    width, height = letter

    # Ligne 1 : texte principal ("PAYÉ")
    line1 = watermark_text
    # Ligne 2 : date du jour automatiquement générée
    line2 = datetime.today().strftime("le %d/%m/%y")

    # Tailles des polices
    size_main = 36
    size_secondary = 18

    # Largeur des deux lignes pour alignement à droite
    text_width_1 = can.stringWidth(line1, "Helvetica-Bold", size_main)
    text_width_2 = can.stringWidth(line2, "Helvetica", size_secondary)

    # Coordonnées de placement bas droite (remonté pour visibilité)
    y_base = 120
    x1 = width - text_width_1 - 40
    x2 = width - text_width_2 - 40

    # Dessin "PAYÉ" en rouge
    can.setFillColor(red)
    can.setFont("Helvetica-Bold", size_main)
    can.drawString(x1, y_base, line1)

    # Dessin date en noir, plus petit
    can.setFillColor(black)
    can.setFont("Helvetica", size_secondary)
    can.drawString(x2, y_base - 24, line2)

    can.save()
    packet.seek(0)
    return PdfReader(packet)

@app.route('/filigrane', methods=['POST'])
def watermark_pdf():
    if 'file' not in request.files:
        return {"error": "PDF file required"}, 400

    pdf_file = request.files['file']
    watermark_text = request.form.get('text', 'PAYÉ')  # Défaut = PAYÉ

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
