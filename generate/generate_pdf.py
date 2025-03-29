from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import qrcode
import os

def generate_exam_pdf(student_name, identification, institution, output_pdf, answer_sheet_img, logo_img):
    # Verificar si existe el directorio assets
    if logo_img and not os.path.exists(os.path.dirname(logo_img)):
        print(f"El directorio {os.path.dirname(logo_img)} no existe")
        logo_img = None
    
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter
    
    # Crear un recuadro para el encabezado
    header_height = 100
    c.rect(50, height - header_height - 20, width - 100, header_height, stroke=1, fill=0)
    
    # Agregar logo si está disponible y el archivo existe
    if logo_img and os.path.exists(logo_img):
        try:
            logo = ImageReader(logo_img)
            # Ajustamos el tamaño manteniendo la proporción original
            logo_width = 120  # Reducimos el ancho para que sea más compacto
            logo_height = logo_width * (207/607)  # Mantenemos la proporción original
            c.drawImage(logo, 60, height - 80, width=logo_width, height=logo_height, mask='auto')
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")
    
    # Agregar el texto centrado en el encabezado
    c.setFont("Helvetica-Bold", 14)
    text_x = width / 2
    c.drawCentredString(text_x, height - 50, "INSTITUCIÓN EDUCATIVA")
    c.setFont("Helvetica", 12)
    c.drawCentredString(text_x, height - 65, institution)
    c.setFont("Helvetica", 10)
    c.drawCentredString(text_x, height - 80, "Simulacro Saber 11")
    c.drawCentredString(text_x, height - 95, "Marzo 26 de 2025")

    # Agregar nombre e identificación del estudiante
    c.setFont("Helvetica", 12)
    c.drawString(60, height - 150, "NOMBRE Y APELLIDO:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, height - 150, student_name.upper())
    
    c.setFont("Helvetica", 12)
    c.drawString(60, height - 170, "IDENTIFICACIÓN:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, height - 170, str(identification).upper() if identification else "NO PROPORCIONADA")
    
    # Generar código QR
    qr_data = f"Nombre: {student_name}, Institución: {institution}, Identificación: {identification}"
    qr = qrcode.make(qr_data)
    temp_qr = "temp_qr.png"
    qr.save(temp_qr)
    qr_img = ImageReader(temp_qr)
    c.drawImage(qr_img, width - 140, height - 110, width=80, height=80)
    
    # Agregar imagen de la hoja de respuestas si existe
    if os.path.exists(answer_sheet_img):
        try:
            answer_sheet = ImageReader(answer_sheet_img)
            # Ajustamos el tamaño manteniendo la proporción original
            sheet_width = 520  # Ancho base
            sheet_height = sheet_width * (632/722)  # Altura proporcional
            x_centered = (width - sheet_width) / 2
            c.drawImage(answer_sheet, x_centered, 80, width=sheet_width, height=sheet_height)
        except Exception as e:
            print(f"No se pudo cargar la hoja de respuestas: {e}")
    else:
        print(f"No se encontró el archivo de hoja de respuestas: {answer_sheet_img}")
    
    # Guardar el PDF
    c.save()
    
    # Eliminar archivo temporal del QR si existe
    if os.path.exists(temp_qr):
        os.remove(temp_qr)
    
    print(f"PDF generado: {output_pdf}")

# Uso del script
generate_exam_pdf(
    "Juan Esteban Valdes",
    "1065847562",
    "Universidad Popular del Cesar", 
    "examen_mejorado.pdf",
    "C:/Users/valde/Desktop/image-recognition/assets/formato-preguntas2.jpg",
    "C:/Users/valde/Desktop/image-recognition/assets/LOGO-UPC-VERDE-2.png",
)
