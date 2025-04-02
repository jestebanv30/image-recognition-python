
import sys
import os

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.graphics.barcode import code128
from models.formatos_models import obtener_formato_por_grado

def draw_reference_markers(c, x, y, width, height):
    marker_size = 20
    margin = 10
    c.setFillColorRGB(0, 0, 0)
    c.rect(x - marker_size - margin, y, marker_size, marker_size, stroke=0, fill=1)
    c.rect(x - marker_size - margin, y + height/2 - marker_size/2, marker_size, marker_size, stroke=0, fill=1)
    c.rect(x - marker_size - margin, y + height - marker_size, marker_size, marker_size, stroke=0, fill=1)
    c.rect(x + width + margin, y, marker_size, marker_size, stroke=0, fill=1)
    c.rect(x + width + margin, y + height/2 - marker_size/2, marker_size, marker_size, stroke=0, fill=1)
    c.rect(x + width + margin, y + height - marker_size, marker_size, marker_size, stroke=0, fill=1)

def draw_barcode_markers(c, x, y, width, height):
    marker_size = 15
    margin = 5
    c.setFillColorRGB(0, 0, 0)
    c.rect(x - marker_size - margin, y - marker_size - margin, marker_size, marker_size, stroke=0, fill=1)
    c.rect(x + width + margin, y - marker_size - margin, marker_size, marker_size, stroke=0, fill=1)
    c.rect(x - marker_size - margin, y + height + margin, marker_size, marker_size, stroke=0, fill=1)
    c.rect(x + width + margin, y + height + margin, marker_size, marker_size, stroke=0, fill=1)

def generate_exam_pdf(student_name, identification, grado, curso, institution, output_pdf, logo_img):
    formato_info = obtener_formato_por_grado(grado)
    answer_sheet_img = formato_info["imagen"]
    ancho_img = formato_info["dimensiones"]["ancho"]
    alto_img = formato_info["dimensiones"]["alto"]

    if logo_img and not os.path.exists(os.path.dirname(logo_img)):
        print(f"El directorio {os.path.dirname(logo_img)} no existe")
        logo_img = None

    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter

    header_height = 100
    c.rect(50, height - header_height - 20, width - 100, header_height, stroke=1, fill=0)

    if logo_img and os.path.exists(logo_img):
        try:
            logo = ImageReader(logo_img)
            logo_width = 90
            logo_height = logo_width * (500/500)
            c.drawImage(logo, 60, height - 115, width=logo_width, height=logo_height, mask='auto')
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")

    c.setFont("Helvetica-Bold", 14)
    text_x = width / 2
    c.drawCentredString(text_x, height - 50, "INSTITUCIÓN EDUCATIVA")
    c.setFont("Helvetica", 12)
    c.drawCentredString(text_x, height - 65, institution)
    c.setFont("Helvetica", 10)
    c.drawCentredString(text_x, height - 80, f"Simulacro Saber {grado}° Curso {curso}")
    c.drawCentredString(text_x, height - 95, "Abril 2 de 2025")

    c.setFont("Helvetica", 12)
    c.drawString(60, height - 150, "NOMBRE Y APELLIDO:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, height - 150, student_name.upper())

    c.setFont("Helvetica", 12)
    c.drawString(60, height - 170, "IDENTIFICACIÓN:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, height - 170, str(identification).upper() if identification else "NO PROPORCIONADA")

    if os.path.exists(answer_sheet_img):
        try:
            answer_sheet = ImageReader(answer_sheet_img)
            sheet_width = 520
            sheet_height = sheet_width * (alto_img / ancho_img)
            espacio_disponible_vertical = height - 200
            y_centered = ((espacio_disponible_vertical - sheet_height) / 2) + 50
            x_centered = (width - sheet_width) / 2
            c.drawImage(answer_sheet, x_centered, y_centered, width=sheet_width, height=sheet_height)
            draw_reference_markers(c, x_centered, y_centered, sheet_width, sheet_height)
        except Exception as e:
            print(f"No se pudo cargar la hoja de respuestas: {e}")
    else:
        print(f"No se encontró el archivo de hoja de respuestas: {answer_sheet_img}")

    barcode_data = student_name.upper()
    barcode_obj = code128.Code128(barcode_data, barHeight=60, barWidth=1.2)
    barcode_width = 400
    barcode_height = 80
    barcode_x = (width - barcode_width) / 2
    barcode_y = 35
    barcode_obj.drawOn(c, barcode_x, barcode_y)
    draw_barcode_markers(c, barcode_x, barcode_y, barcode_width, barcode_height)

    c.save()
    print(f"PDF generado: {output_pdf}")

estudiantes = [
    ("ACOSTA FUENTES ALAN DAVID", "1122418713", 2, 1),
]

for nombre, identificacion, grado, curso in estudiantes:
    generate_exam_pdf(
        nombre,
        identificacion,
        grado,
        curso,
        "Institución Educativa El Carmelo",
        f"prueba-grado-{grado}-curso-{curso}-{identificacion}.pdf",
        "C:/Users/valde/Desktop/image-recognition/assets/logo-carmelita.png"
    )
