import cv2
import numpy as np

def plot_image(img, titulo="Imagen", grayscale=True):
    try:
        if grayscale and len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imshow(titulo, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error al mostrar la imagen: {str(e)}")

def cargar_imagen(ruta):
    try:
        img = cv2.imread(ruta)
        if img is None:
            raise Exception("No se pudo cargar la imagen")
        return img
    except Exception as e:
        print(f"Error al cargar la imagen: {str(e)}")
        return None

def detectar_qr_con_marcadores(img):
    # Crear copia redimensionada para detección de marcadores
    height, width = img.shape[:2]
    max_dimension = 800
    if width > max_dimension or height > max_dimension:
        scale = max_dimension / max(width, height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        img_small = cv2.resize(img, (new_width, new_height))
    else:
        img_small = img.copy()
        scale = 1.0

    # Trabajar con la parte superior de la imagen redimensionada
    height_small = img_small.shape[0]
    zona_superior = int(height_small * 0.4)
    img_superior_small = img_small[0:zona_superior, :]

    gray = cv2.cvtColor(img_superior_small, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV, 11, 2)
    kernel = np.ones((3, 3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    #plot_image(thresh, "Imagen procesada")

    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    marcadores = []
    area_imagen = zona_superior * img_superior_small.shape[1]
    img_marcadores = img_superior_small.copy()

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area_imagen * 0.00005 < area < area_imagen * 0.005:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            if 0.8 <= aspect_ratio <= 1.2 and w > 3 and h > 3:
                roi = gray[y:y + h, x:x + w]
                if np.mean(roi) < 150:
                    if x > img_superior_small.shape[1] * 0.7:
                        marcadores.append((x, y, w, h))
                        cv2.rectangle(img_marcadores, (x, y), (x + w, y + h), (0, 0, 255), 2)

    #plot_image(img_marcadores, "Marcadores detectados", False)

    if len(marcadores) >= 4:
        from itertools import combinations
        marcadores = sorted(marcadores, key=lambda m: (m[1], m[0]))
        for combo in combinations(marcadores, 4):
            combo = list(combo)
            combo.sort(key=lambda m: m[1])
            top = sorted(combo[:2], key=lambda m: m[0])
            bottom = sorted(combo[2:], key=lambda m: m[0])

            dv1 = abs(top[0][1] - bottom[0][1])
            dv2 = abs(top[1][1] - bottom[1][1])
            dh1 = abs(top[0][0] - top[1][0])
            dh2 = abs(bottom[0][0] - bottom[1][0])

            if abs(dv1 - dv2) / max(1, dv1) < 0.3 and abs(dh1 - dh2) / max(1, dh1) < 0.3:
                posibles = [top[0], top[1], bottom[0], bottom[1]]
                x1 = min(m[0] for m in posibles)
                y1 = min(m[1] for m in posibles)
                x2 = max(m[0] + m[2] for m in posibles)
                y2 = max(m[1] + m[3] for m in posibles)

                ancho = x2 - x1
                alto = y2 - y1
                margen_interno = int(min(ancho, alto) * 0.15)
                x1_interno = x1 + margen_interno
                y1_interno = y1 + margen_interno
                x2_interno = x2 - margen_interno
                y2_interno = y2 - margen_interno

                # Escalar coordenadas a imagen original
                x1_orig = int(x1_interno / scale)
                y1_orig = int(y1_interno / scale)
                x2_orig = int(x2_interno / scale)
                y2_orig = int(y2_interno / scale)

                # Extraer región de la imagen original en alta resolución
                zona_superior_orig = int(height * 0.4)
                img_superior_orig = img[0:zona_superior_orig, :]
                qr_region = img_superior_orig[y1_orig:y2_orig, x1_orig:x2_orig].copy()

                # Mostrar región detectada
                img_region = img_superior_small.copy()
                cv2.rectangle(img_region, (x1_interno, y1_interno), (x2_interno, y2_interno), (255, 0, 0), 2)
                #plot_image(img_region, "Región QR detectada", False)
                #plot_image(qr_region, "QR extraído", False)
                return qr_region

    print("No se encontraron 4 marcadores válidos que formen un rectángulo")
    return None

def procesar_qr_con_marcadores(ruta_imagen, mostrar_resultados=True):
    img = cargar_imagen(ruta_imagen)
    if img is None:
        print("Error al cargar la imagen")
        return None

    qr_region = detectar_qr_con_marcadores(img)
    if qr_region is None:
        print("No se pudo detectar la región del QR")
        return None

    if mostrar_resultados:
        plot_image(qr_region, "QR extraído en alta resolución", False)

    return qr_region

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
        
        # Verificar que las distancias entre los marcadores son consistentes
        dist_izq1 = abs(marcadores_izq[1][1] - marcadores_izq[0][1])
        dist_izq2 = abs(marcadores_izq[2][1] - marcadores_izq[1][1])
        
        if abs(dist_izq1 - dist_izq2) > 20:  # Si las distancias son muy diferentes
            print("Las distancias entre marcadores no son consistentes")
            return None
        
        # Obtener límites de la región de interés
        x_min = min(m[0] + m[2] for m in marcadores_izq)
        x_max = max(m[0] for m in marcadores_der)
        y_min = min(min(m[1] for m in marcadores_izq), min(m[1] for m in marcadores_der))
        y_max = max(max(m[1] + m[3] for m in marcadores_izq), max(m[1] + m[3] for m in marcadores_der))
        
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
            
            if mostrar_resultados:
                # Mostrar resultados
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.imshow("Región de interés detectada", roi_estandarizada)
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            
            return roi_estandarizada
        else:
            print("No se detectaron suficientes marcadores")
            return None
    else:
        print("Error: No se pudo cargar la imagen")
        return None

def detectar_marcadores_codigo_barras(img, mostrar=True):
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plot_image(gray, "1. Imagen en escala de grises")
    
    # Umbralización adaptativa
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY_INV, 11, 2)
    plot_image(thresh, "2. Umbralización adaptativa")
    
    # Limpiar ruido
    kernel = np.ones((3,3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    plot_image(thresh, "3. Limpieza de ruido")

    # Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    height, width = img.shape[:2]
    area_imagen = height * width
    marcadores = []

    # Detectar marcadores cuadrados
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area_imagen * 0.0001 < area < area_imagen * 0.01:  # Ajustado el rango de área
            x, y, w, h = cv2.boundingRect(cnt)
            ratio = w / h
            if 0.8 <= ratio <= 1.2:  # Debe ser aproximadamente cuadrado
                roi = gray[y:y+h, x:x+w]
                if np.mean(roi) < 100:  # Debe ser oscuro
                    marcadores.append((x, y, w, h))

    if mostrar:
        img_debug = img.copy()
        for m in marcadores:
            cv2.rectangle(img_debug, (m[0], m[1]), (m[0]+m[2], m[1]+m[3]), (0,0,255), 2)
        plot_image(img_debug, "4. Marcadores detectados", False)

    # Filtrar marcadores en la parte inferior de la imagen (último 25% de la altura)
    altura_imagen = img.shape[0]
    umbral_y = altura_imagen * 0.75  # Solo considerar marcadores en el último 25%
    marcadores_inferiores = [m for m in marcadores if m[1] > umbral_y]

    if len(marcadores_inferiores) < 4:
        print(f"No se encontraron suficientes marcadores en la región inferior: {len(marcadores_inferiores)}")
        return None

    # Ordenar marcadores por coordenada x
    marcadores_inferiores.sort(key=lambda m: m[0])
    
    # Identificar los 4 marcadores que forman un rectángulo
    marcadores_izq = sorted(marcadores_inferiores[:2], key=lambda x: x[1])  # Los 2 marcadores más a la izquierda
    marcadores_der = sorted(marcadores_inferiores[-2:], key=lambda x: x[1])  # Los 2 marcadores más a la derecha
    
    # Calcular región del código de barras
    x_min = min(m[0] + m[2] for m in marcadores_izq)  # Después del marcador izquierdo
    x_max = max(m[0] for m in marcadores_der)  # Antes del marcador derecho
    y_min = min(min(m[1] for m in marcadores_izq), min(m[1] for m in marcadores_der))  # El más alto
    y_max = max(max(m[1] + m[3] for m in marcadores_izq), max(m[1] + m[3] for m in marcadores_der))  # El más bajo

    if mostrar:
        img_region = img.copy()
        cv2.rectangle(img_region, (x_min, y_min), (x_max, y_max), (0,255,0), 2)
        plot_image(img_region, "5. Región del código de barras", False)

    return (x_min, y_min, x_max - x_min, y_max - y_min)

def procesar_codigo_barras_con_marcadores(ruta_imagen, mostrar_resultados=True):
    img = cargar_imagen(ruta_imagen)
    if img is None:
        print("Error al cargar la imagen.")
        return None

    if mostrar_resultados:
        plot_image(img, "0. Imagen original", False)

    region = detectar_marcadores_codigo_barras(img, mostrar=mostrar_resultados)
    if region is None:
        return None

    x, y, w, h = region
    roi = img[y:y+h, x:x+w]

    # Mejora de contraste y calidad
    # Convertir a escala de grises
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    # Redimensionar para mejor lectura (2x más grande)
    height, width = gray.shape[:2]
    roi_resized = cv2.resize(gray, (width*2, height*2), 
                           interpolation=cv2.INTER_CUBIC)
    
    # Mejorar contraste
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(16,16))
    roi_final = clahe.apply(roi_resized)
    
    # Convertir de nuevo a BGR para mantener consistencia
    roi_final = cv2.cvtColor(roi_final, cv2.COLOR_GRAY2BGR)

    if mostrar_resultados:
        plot_image(roi_final, "6. Código de barras procesado y mejorado", False)

    return roi_final

if __name__ == "__main__":
    # Ejemplo de uso
    ruta_imagen = "C:/Users/valde/Desktop/image-recognition/assets/image.png"
    #procesar_imagen_con_marcadores(ruta_imagen)

    procesar_qr_con_marcadores(ruta_imagen)

    #procesar_codigo_barras_con_marcadores(ruta_imagen)
