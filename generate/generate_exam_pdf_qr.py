import sys
import os
import json

# Agregar el directorio raíz al path de Python
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import qrcode
from models.formatos_models import obtener_formato_por_grado

def draw_reference_markers(c, x, y, width, height):
    
    # Dibuja marcadores cuadrados en los bordes de la hoja
    
    marker_size = 20  # Tamaño del cuadrado aumentado a 30
    margin = 10  # Margen aumentado para separar más los marcadores
    
    # Dibuja los cuadrados negros en los bordes
    c.setFillColorRGB(0, 0, 0)
    
    # Borde izquierdo
    c.rect(x - marker_size - margin, y, marker_size, marker_size, stroke=0, fill=1)  # Inferior
    c.rect(x - marker_size - margin, y + height/2 - marker_size/2, marker_size, marker_size, stroke=0, fill=1)  # Medio
    c.rect(x - marker_size - margin, y + height - marker_size, marker_size, marker_size, stroke=0, fill=1)  # Superior
        
    # Borde derecho
    c.rect(x + width + margin, y, marker_size, marker_size, stroke=0, fill=1)  # Inferior
    c.rect(x + width + margin, y + height/2 - marker_size/2, marker_size, marker_size, stroke=0, fill=1)  # Medio
    c.rect(x + width + margin, y + height - marker_size, marker_size, marker_size, stroke=0, fill=1)  # Superior

def draw_qr_markers(c, x, y, width, height):
    # Dibuja marcadores cuadrados en las esquinas del QR
    marker_size = 15
    margin = 5
    
    c.setFillColorRGB(0, 0, 0)
    
    # Esquinas
    c.rect(x - marker_size - margin, y - marker_size - margin, marker_size, marker_size, stroke=0, fill=1)  # Inferior izquierda
    c.rect(x + width + margin, y - marker_size - margin, marker_size, marker_size, stroke=0, fill=1)  # Inferior derecha
    c.rect(x - marker_size - margin, y + height + margin, marker_size, marker_size, stroke=0, fill=1)  # Superior izquierda
    c.rect(x + width + margin, y + height + margin, marker_size, marker_size, stroke=0, fill=1)  # Superior derecha

def generate_exam_pdf(student_name, identification, grado, curso, institution, output_pdf, logo_img):
    # Obtener información del formato según el grado
    formato_info = obtener_formato_por_grado(grado)
    answer_sheet_img = formato_info["imagen"]
    ancho_img = formato_info["dimensiones"]["ancho"]
    alto_img = formato_info["dimensiones"]["alto"]

    # Verificar si existe el directorio assets
    if logo_img and not os.path.exists(os.path.dirname(logo_img)):
        print(f"El directorio {os.path.dirname(logo_img)} no existe")
        logo_img = None
    
    c = canvas.Canvas(output_pdf, pagesize=letter)
    width, height = letter
    
    # Crear un recuadro para el encabezado
    header_height = 100
    c.rect(50, height - header_height - 20, width - 100, header_height, stroke=1, fill=0)
    
    # Generar código QR primero para ubicarlo en el encabezado
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr_data = f"Nombre: {student_name}, Institución: {institution}, Identificación: {identification}, Grado: {grado}, Curso: {curso}"
    qr.add_data(qr_data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white")
    temp_qr = "temp_qr.png"
    qr_img.save(temp_qr)
    qr_img = ImageReader(temp_qr)
    
    # Ubicar QR en la esquina derecha del encabezado
    qr_width = 80  # Tamaño reducido para el encabezado
    qr_height = 80
    qr_x = width - 150  # Posición desde la derecha
    qr_y = height - 110  # Posición desde arriba
    c.drawImage(qr_img, qr_x, qr_y, width=qr_width, height=qr_height)
    
    # Agregar marcadores alrededor del QR
    draw_qr_markers(c, qr_x, qr_y, qr_width, qr_height)
    
    # Agregar logo si está disponible y el archivo existe
    if logo_img and os.path.exists(logo_img):
        try:
            logo = ImageReader(logo_img)
            # Ajustamos el tamaño manteniendo la proporción original
            logo_width = 90  # Reducimos el ancho para que sea más compacto
            logo_height = logo_width * (500/500)  # Mantenemos la proporción original
            c.drawImage(logo, 60, height - 115, width=logo_width, height=logo_height, mask='auto')
        except Exception as e:
            print(f"No se pudo cargar el logo: {e}")
    
    # Agregar el texto centrado en el encabezado
    c.setFont("Helvetica-Bold", 14)
    text_x = width / 2
    c.drawCentredString(text_x, height - 50, "INSTITUCIÓN EDUCATIVA")
    c.setFont("Helvetica", 12)
    c.drawCentredString(text_x, height - 65, institution)
    c.setFont("Helvetica", 10)
    c.drawCentredString(text_x, height - 80, f"Prueba de Mejoramiento Institucional Por Periodo")
    c.setFont("Helvetica", 10)
    c.drawCentredString(text_x, height - 95, f"Grado {grado}° Curso {curso}")
    c.setFont("Helvetica", 8)
    c.drawCentredString(text_x, height - 110, f"Abril 4 de 2025")

    # Agregar nombre e identificación del estudiante
    c.setFont("Helvetica", 12)
    c.drawString(60, height - 150, "NOMBRE Y APELLIDO:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, height - 150, student_name.upper())
    
    c.setFont("Helvetica", 12)
    c.drawString(60, height - 170, "IDENTIFICACIÓN:")
    c.setFont("Helvetica-Bold", 12)
    c.drawString(200, height - 170, str(identification).upper() if identification else "NO PROPORCIONADA")
    
    # Agregar imagen de tipo de marcaciones
    try:
        tipo_marcaciones = ImageReader("C:/Users/valde/Desktop/image-recognition/assets/formato-grados/tipo_marcaciones.png")
        # Ajustar dimensiones manteniendo proporción
        marcaciones_width = 300  # Ancho reducido para que quede bien
        marcaciones_height = marcaciones_width * (166/696)  # Mantener proporción
        
        # Centrar horizontalmente
        x_marcaciones = (width - marcaciones_width) / 2
        c.drawImage(tipo_marcaciones, x_marcaciones, height - 280, 
                   width=marcaciones_width, height=marcaciones_height)
    except Exception as e:
        print(f"No se pudo cargar la imagen de tipo de marcaciones: {e}")
    
    # Agregar imagen de la hoja de respuestas si existe
    if os.path.exists(answer_sheet_img):
        try:
            answer_sheet = ImageReader(answer_sheet_img)
            # Ajustamos el tamaño manteniendo la proporción original
            sheet_width = 520  # Ancho de la hoja de respuestas
            sheet_height = sheet_width * (alto_img / ancho_img)  # Altura proporcional usando dimensiones del formato
            
            # Calcular coordenadas para centrar la hoja más abajo
            espacio_disponible_vertical = height - 300  # Aumentado más el espacio superior
            y_centered = ((espacio_disponible_vertical - sheet_height) / 2) - 20  # Ajustado para bajar más
            x_centered = (width - sheet_width) / 2  # Centrado horizontal
            
            # Dibujar la hoja de respuestas centrada
            c.drawImage(answer_sheet, x_centered, y_centered, width=sheet_width, height=sheet_height)
            
            # Dibujar marcadores de referencia por fuera de la imagen
            draw_reference_markers(c, x_centered, y_centered, sheet_width, sheet_height)
            
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

# Cargar datos de estudiantes desde el archivo JSON
json_path = "C:/Users/valde/Desktop/image-recognition/generate/estudiantes.json"
with open(json_path, 'r', encoding='utf-8') as f:
    data = json.load(f)

# Crear directorio para los exámenes si no existe
output_dir = "C:/Users/valde/Desktop/image-recognition/generate/nuevas_pruebas"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Generar PDF para cada estudiante
for estudiante in data['estudiantes']:
    output_pdf = os.path.join(output_dir, f"prueba-grado-{estudiante['grado']}-curso-{estudiante['curso']}-{estudiante['identificacion']}.pdf")
    generate_exam_pdf(
        estudiante['nombre_completo'],
        estudiante['identificacion'],
        estudiante['grado'],
        estudiante['curso'],
        "Institución Educativa El Carmelo",
        output_pdf,
        "C:/Users/valde/Desktop/image-recognition/assets/logo-carmelita.png"
    )
