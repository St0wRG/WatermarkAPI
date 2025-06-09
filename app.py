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

    # Tailles de police
    size_main = 36
    size_secondary = 10
    rotation_angle = 15

    # Polices
    font_main = "Helvetica-Bold"
    font_secondary = "Helvetica"

    # Couleurs semi-transparentes
    red_transparent = Color(1, 0, 0, alpha=0.5)
    black_transparent = Color(0, 0, 0, alpha=0.5)

    # Largeurs des textes
    text_width_1 = can.stringWidth(line1, font_main, size_main)
    text_width_2 = can.stringWidth(line2, font_secondary, size_secondary)

    # Aligné à droite sur la largeur la plus grande
    max_width = max(text_width_1, text_width_2)
    x_align = width - max_width - 40
    y_base = height * 0.4

    # "PAYÉ"
    can.saveState()
    can.setFillColor(red_transparent)
    can.setFont(font_main, size_main)
    can.translate(x_align, y_base)
    can.rotate(rotation_angle)
    can.drawString(max_width - tex_
