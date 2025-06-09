from flask import Flask, request, send_file
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color, red
import io, os

app = Flask(__name__)

def create_watermark(watermark_text):
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica-Bold", 40)

    # Rouge transparent (40 % d’opacité)
    semi_transparent_red = Color(1, 0, 0, alpha=0.4)
    can.setFillColor(semi_transparent_red)

    width, height = letter
    text_width = can.stringWidth(watermark_text, "Helvetica-Bold", 40)

    # ✅ Position ajustée : bas droite mais plus haut
    x = width - text_width - 40
    y = 120  # << ici, on le remonte plus haut qu’avant (anciennement 40)

    # Rotation autour du coin inférieur droit
    can.saveState()
    can.translate(x, y)
    can.rotate(30)  # inclinaison douce
    can.drawString(0, 0, watermark_text)
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
