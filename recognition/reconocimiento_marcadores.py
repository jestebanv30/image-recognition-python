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
            
        # Reducir escala de la imagen para mejor procesamiento
        height, width = img.shape[:2]
        if width > 1500:
            scale = 1500 / width
            new_width = 1500
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height))
            
        return img
    except Exception as e:
        print(f"Error al cargar la imagen: {str(e)}")
        return None

def detectar_qr_con_marcadores(img):
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plot_image(gray, "1. Imagen en escala de grises")
    
    # Umbralización adaptativa para mejorar detección de cuadrados pequeños
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                 cv2.THRESH_BINARY_INV, 11, 2)
    plot_image(thresh, "2. Umbralización adaptativa")
    
    # Aplicar operaciones morfológicas para limpiar ruido
    kernel = np.ones((3,3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    plot_image(thresh, "3. Operaciones morfológicas")
    
    # Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # Dibujar contornos encontrados
    img_contours = img.copy()
    cv2.drawContours(img_contours, contours, -1, (0,255,0), 2)
    plot_image(img_contours, "4. Contornos detectados", False)
    
    # Filtrar contornos cuadrados pequeños
    marcadores = []
    img_squares = img.copy()
    
    # Obtener dimensiones de la imagen
    height, width = img.shape[:2]
    area_imagen = height * width
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Ajustar el rango de área para detectar marcadores más pequeños
        if area > area_imagen * 0.00005 and area < area_imagen * 0.005:  # Reducidos los umbrales
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w)/h
            # Verificar si es aproximadamente cuadrado
            if 0.8 <= aspect_ratio <= 1.2:
                # Verificar si es negro (promedio de intensidad bajo)
                roi = gray[y:y+h, x:x+w]
                if np.mean(roi) < 100:
                    marcadores.append((x, y, w, h))
                    cv2.rectangle(img_squares, (x,y), (x+w,y+h), (0,0,255), 2)
    
    plot_image(img_squares, "5. Marcadores del QR detectados", False)
    
    # Encontrar los 4 marcadores que forman un cuadrado
    marcadores_validos = []
    if len(marcadores) >= 4:
        for i in range(len(marcadores)-3):
            for j in range(i+1, len(marcadores)-2):
                for k in range(j+1, len(marcadores)-1):
                    for l in range(k+1, len(marcadores)):
                        m1, m2, m3, m4 = marcadores[i], marcadores[j], marcadores[k], marcadores[l]
                        
                        # Calcular las distancias entre los marcadores
                        distancias = []
                        puntos = [(m1[0], m1[1]), (m2[0], m2[1]), (m3[0], m3[1]), (m4[0], m4[1])]
                        
                        for p1_idx in range(len(puntos)):
                            for p2_idx in range(p1_idx + 1, len(puntos)):
                                p1 = puntos[p1_idx]
                                p2 = puntos[p2_idx]
                                dist = np.sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
                                distancias.append(dist)
                        
                        # Si las distancias son similares (tolerancia del 10%)
                        distancias.sort()
                        if len(set([round(d, -1) for d in distancias[:4]])) == 1 and \
                           abs(distancias[4] - distancias[5]) < distancias[4] * 0.1:
                            marcadores_validos = [m1, m2, m3, m4]
                            break
                    if marcadores_validos:
                        break
                if marcadores_validos:
                    break
            if marcadores_validos:
                break
    
    if marcadores_validos:
        # Ordenar marcadores por posición
        marcadores_validos.sort(key=lambda x: (x[1], x[0]))  # Ordenar primero por y, luego por x
        
        # Obtener límites del QR
        x_min = min(m[0] for m in marcadores_validos)
        x_max = max(m[0] + m[2] for m in marcadores_validos)
        y_min = min(m[1] for m in marcadores_validos)
        y_max = max(m[1] + m[3] for m in marcadores_validos)
        
        return (x_min, y_min, x_max - x_min, y_max - y_min)
    else:
        print("No se encontraron 4 marcadores que formen un cuadrado")
        return None

def procesar_qr_con_marcadores(ruta_imagen, mostrar_resultados=True):
    img = cargar_imagen(ruta_imagen)
    
    if img is not None:
        plot_image(img, "0. Imagen original", False)
        # Detectar región del QR
        region = detectar_qr_con_marcadores(img)
        
        if region:
            x, y, w, h = region
            # Extraer región de interés
            roi = img[y:y+h, x:x+w]
            
            # Dimensiones estándar deseadas - aumentadas para mejor resolución
            ancho_estandar = 400  # Aumentado de 150 a 400 para mejor resolución
            # Mantener la relación de aspecto
            relacion_aspecto = h / w
            alto_estandar = int(ancho_estandar * relacion_aspecto)
            
            # Redimensionar usando INTER_CUBIC para mejor calidad
            roi_estandarizada = cv2.resize(roi, (ancho_estandar, alto_estandar), 
                                         interpolation=cv2.INTER_CUBIC)
            
            # Aplicar mejora de nitidez
            kernel_sharpening = np.array([[-1,-1,-1], 
                                        [-1, 9,-1],
                                        [-1,-1,-1]])
            roi_estandarizada = cv2.filter2D(roi_estandarizada, -1, kernel_sharpening)
            
            if mostrar_resultados:
                # Mostrar resultados
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
                plot_image(img, "6. Imagen con región QR detectada", False)
                plot_image(roi_estandarizada, "7. Región QR estandarizada", False)
            
            return roi_estandarizada
        else:
            print("No se detectaron suficientes marcadores para el QR")
            return None
    else:
        print("Error: No se pudo cargar la imagen")
        return None

def detectar_marcadores(img):
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    plot_image(gray, "1. Imagen en escala de grises")
    
    # Umbralización adaptativa para mejorar detección de cuadrados pequeños
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                 cv2.THRESH_BINARY_INV, 11, 2)
    plot_image(thresh, "2. Umbralización adaptativa")
    
    # Aplicar operaciones morfológicas para limpiar ruido
    kernel = np.ones((3,3), np.uint8)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    
    # Dibujar contornos encontrados
    img_contours = img.copy()
    cv2.drawContours(img_contours, contours, -1, (0,255,0), 2)
    plot_image(img_contours, "3. Contornos detectados", False)
    
    # Filtrar contornos cuadrados pequeños
    marcadores = []
    img_squares = img.copy()
    
    # Obtener dimensiones de la imagen
    height, width = img.shape[:2]
    area_imagen = height * width
    
    for cnt in contours:
        area = cv2.contourArea(cnt)
        # Filtrar por área relativa al tamaño de la imagen (ajustar según necesidad)
        if area > area_imagen * 0.0001 and area < area_imagen * 0.01:
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w)/h
            # Verificar si es aproximadamente cuadrado
            if 0.8 <= aspect_ratio <= 1.2:
                # Verificar si es negro (promedio de intensidad bajo)
                roi = gray[y:y+h, x:x+w]
                if np.mean(roi) < 100:  # Ajustar umbral según necesidad
                    marcadores.append((x, y, w, h))
                    cv2.rectangle(img_squares, (x,y), (x+w,y+h), (0,0,255), 2)
    
    plot_image(img_squares, "4. Cuadrados detectados", False)
    
    # Separar marcadores izquierdos y derechos
    marcadores.sort(key=lambda x: x[0])  # Ordenar por coordenada x
    if len(marcadores) >= 6:  # Verificar que hay al menos 6 marcadores
        marcadores_izq = sorted(marcadores[:3], key=lambda x: x[1])  # Ordenar por coordenada y
        marcadores_der = sorted(marcadores[-3:], key=lambda x: x[1])  # Ordenar por coordenada y
        
        # Verificar que los marcadores tienen distancias similares en y
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
        cv2.rectangle(img_region, (x_min,y_min), (x_max,y_max), (255,0,0), 2)
        plot_image(img_region, "5. Región detectada", False)
        
        return (x_min, y_min, x_max - x_min, y_max - y_min)
    else:
        print(f"No hay suficientes marcadores: {len(marcadores)} detectados")
    
    return None

def procesar_imagen_con_marcadores(ruta_imagen, mostrar_resultados=True):
    img = cargar_imagen(ruta_imagen)
    
    if img is not None:
        plot_image(img, "0. Imagen original", False)
        # Detectar región entre marcadores
        region = detectar_marcadores(img)
        
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
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
                plot_image(img, "6. Imagen con región detectada", False)
                plot_image(roi_estandarizada, "7. Región de interés estandarizada", False)
            
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
