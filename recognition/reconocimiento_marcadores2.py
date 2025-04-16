import cv2
import numpy as np

def cargar_imagen(ruta):
    """ Cargar imagen desde el archivo """
    try:
        img = cv2.imread(ruta)
        if img is None:
            raise Exception("No se pudo cargar la imagen")
        return img
    except Exception as e:
        print(f"Error al cargar la imagen: {str(e)}")
        return None

def detectar_marcadores_hoja_de_respuestas(img):
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Umbralización adaptativa para mejorar detección de cuadrados pequeños
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                 cv2.THRESH_BINARY_INV, 11, 2)
    
    # Aplicar operaciones morfológicas para limpiar ruido
    kernel = np.ones((3,3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filtrar contornos cuadrados pequeños
    marcadores = []
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Filtrar por área relativa al tamaño de la imagen (ajustar según necesidad)
        if area > 500 and area < 5000:  # Ajustado el rango de área
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w)/h
            # Verificar si es aproximadamente cuadrado
            if 0.8 <= aspect_ratio <= 1.2:
                # Verificar si es oscuro (promedio de intensidad bajo)
                roi = gray[y:y+h, x:x+w]
                if np.mean(roi) < 150:  # Ajustar umbral según necesidad
                    marcadores.append((x, y, w, h))
    
    # Si se detectan al menos 6 marcadores, los ordenamos
    if len(marcadores) >= 6:
        marcadores.sort(key=lambda m: m[0])  # Ordenar por coordenada x
        marcadores_izq = sorted(marcadores[:3], key=lambda x: x[1])  # Los 3 de la izquierda
        marcadores_der = sorted(marcadores[-3:], key=lambda x: x[1])  # Los 3 de la derecha
        
        # Obtener límites de la región de interés
        x_min = min(m[0] + m[2] for m in marcadores_izq)
        x_max = max(m[0] for m in marcadores_der)
        y_min = min(min(m[1] for m in marcadores_izq), min(m[1] for m in marcadores_der))
        y_max = max(max(m[1] + m[3] for m in marcadores_izq), max(m[1] + m[3] for m in marcadores_der))
        
        # Expansión de la región de recorte para tomar desde afuera de los marcadores
        margen_extra = 30  # Margen adicional fuera de los marcadores
        x_min = max(x_min - margen_extra, 0)
        x_max = min(x_max + margen_extra, img.shape[1])
        y_min = max(y_min - margen_extra, 0)
        y_max = min(y_max + margen_extra, img.shape[0])
        
        # Dibujar región detectada
        img_region = img.copy()
        cv2.rectangle(img_region, (x_min, y_min), (x_max, y_max), (255, 0, 0), 2)
        
        return (x_min, y_min, x_max - x_min, y_max - y_min)
    else:
        print(f"No hay suficientes marcadores: {len(marcadores)} detectados")
    
    return None

def procesar_hoja_de_respuestas_con_marcadores(ruta_imagen, mostrar_resultados=True):
    img = cargar_imagen(ruta_imagen)
    
    if img is not None:
        # Detectar región entre marcadores
        region = detectar_marcadores_hoja_de_respuestas(img)
        
        if region:
            x, y, w, h = region
            # Extraer región de interés
            roi = img[y:y+h, x:x+w]
            
            # Dimensiones estándar deseadas
            ancho_estandar = 800  # Ancho fijo deseado
            # Mantener la relación de aspecto
            relacion_aspecto = h / w
            alto_estandar = int(ancho_estandar * relacion_aspecto)
            
            # Redimensionar la región de interés a un tamaño estándar
            roi_estandarizada = cv2.resize(roi, (ancho_estandar, alto_estandar))
            
            #if mostrar_resultados:
                # Mostrar resultados
                #cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                #cv2.imshow("Región de interés detectada", roi_estandarizada)
                #cv2.waitKey(0)
                #cv2.destroyAllWindows()
            
            return roi_estandarizada
        else:
            print("No se detectaron suficientes marcadores")
            return None
    else:
        print("Error: No se pudo cargar la imagen")
        return None
