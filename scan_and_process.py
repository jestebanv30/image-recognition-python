import cv2
import numpy as np
import os
from image_recognition_v1 import procesar_hoja_respuestas

def detectar_marcadores_referencia(imagen):
    """
    Detecta los marcadores de referencia en la imagen escaneada
    """
    gris = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    _, umbralizada = cv2.threshold(gris, 170, 255, cv2.THRESH_BINARY)
    
    # Encontrar contornos
    contornos, _ = cv2.findContours(umbralizada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    marcadores = []
    for contorno in contornos:
        x, y, w, h = cv2.boundingRect(contorno)
        # Filtrar por tamaño aproximado de los marcadores
        if 15 < w < 25 and 15 < h < 25:
            marcadores.append((x, y, w, h))
    
    return marcadores

def corregir_perspectiva(imagen, marcadores):
    """
    Corrige la perspectiva de la imagen usando los marcadores de referencia
    """
    if len(marcadores) < 4:
        print("No se detectaron suficientes marcadores para corregir la perspectiva")
        return imagen
    
    # Ordenar marcadores: [superior_izquierdo, superior_derecho, inferior_derecho, inferior_izquierdo]
    marcadores_ordenados = sorted(marcadores, key=lambda m: (m[1], m[0]))
    
    # Obtener dimensiones de la hoja
    width = int(np.linalg.norm(np.array(marcadores_ordenados[1][:2]) - np.array(marcadores_ordenados[0][:2])))
    height = int(np.linalg.norm(np.array(marcadores_ordenados[2][:2]) - np.array(marcadores_ordenados[1][:2])))
    
    # Puntos de origen y destino para la transformación
    src_points = np.float32([
        [marcadores_ordenados[0][0], marcadores_ordenados[0][1]],
        [marcadores_ordenados[1][0], marcadores_ordenados[1][1]],
        [marcadores_ordenados[2][0], marcadores_ordenados[2][1]],
        [marcadores_ordenados[3][0], marcadores_ordenados[3][1]]
    ])
    
    dst_points = np.float32([
        [0, 0],
        [width, 0],
        [width, height],
        [0, height]
    ])
    
    # Calcular matriz de transformación
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    
    # Aplicar transformación
    imagen_corregida = cv2.warpPerspective(imagen, matrix, (width, height))
    
    return imagen_corregida

def capturar_y_procesar():
    """
    Captura una imagen de la cámara y procesa la hoja de respuestas
    """
    # Crear directorio si no existe
    output_dir = r"C:\Users\valde\Desktop\image-recognition\scan"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    # Inicializar cámara
    cap = cv2.VideoCapture(2)
    
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara")
        return
    
    print("Presiona 'ESPACIO' para capturar la imagen o 'ESC' para salir")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: No se pudo leer el frame")
            break
            
        # Mostrar frame
        cv2.imshow('Captura de Hoja de Respuestas', frame)
        
        # Esperar tecla
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            break
        elif key == 32:  # ESPACIO
            # Guardar imagen
            imagen_escaneada = os.path.join(output_dir, 'hoja_escaneada.jpg')
            cv2.imwrite(imagen_escaneada, frame)
            print(f"Imagen capturada y guardada como '{imagen_escaneada}'")
            break
    
    # Liberar recursos
    cap.release()
    cv2.destroyAllWindows()
    
    # Procesar imagen
    imagen = cv2.imread(imagen_escaneada)
    if imagen is None:
        print("Error: No se pudo cargar la imagen capturada")
        return
    
    # Detectar marcadores
    marcadores = detectar_marcadores_referencia(imagen)
    print(f"Marcadores detectados: {len(marcadores)}")
    
    # Corregir perspectiva
    imagen_corregida = corregir_perspectiva(imagen, marcadores)
    imagen_corregida_path = os.path.join(output_dir, 'hoja_corregida.jpg')
    cv2.imwrite(imagen_corregida_path, imagen_corregida)
    
    # Procesar respuestas
    respuestas = procesar_hoja_respuestas(imagen_corregida_path)
    
    # Mostrar resultados
    print("\nRespuestas detectadas:")
    for pregunta, respuesta in sorted(respuestas.items()):
        print(f"Pregunta {pregunta}: {respuesta}")

if __name__ == "__main__":
    capturar_y_procesar() 