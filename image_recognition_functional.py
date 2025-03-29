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

# ruta_imagen = "C:/Users/valde/Desktop/image-recognition/assets/prueba-tipo-ifces.jpg"
ruta_imagen = "C:/Users/valde/Desktop/image-recognition/assets/prueba-saber2.jpg"
img = cargar_imagen(ruta_imagen)

# PROCESAMIENTO DE IMAGEN
if img is not None:
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Aplicar umbralización adaptativa para mejorar detección de bordes
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                 cv2.THRESH_BINARY, 11, 2)
    
    # Detectar bordes con parámetros ajustados
    edges = cv2.Canny(thresh, 30, 150)  # Aumentado umbral superior para mejor detección
    
    # Dilatación para conectar bordes cercanos
    kernel = np.ones((5,5), np.uint8)  # Kernel más grande
    edges = cv2.dilate(edges, kernel, iterations=2)  # Más iteraciones
    
    # Encontrar contornos con jerarquía
    contours, hierarchy = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filtrar contornos por área y proporción
    valid_contours = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100000:  # Aumentado el área mínima
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w)/h
            if 0.7 < aspect_ratio < 1.3:  # Ajustada la proporción para ser más cuadrada
                valid_contours.append(cnt)
    
    if valid_contours:
        # Tomar el contorno más grande
        hoja_respuestas = max(valid_contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(hoja_respuestas)
        print(f"Coordenadas de la hoja de respuestas: x={x}, y={y}, w={w}, h={h}")
        
        # Recortar la región de la hoja de respuestas
        roi = gray[y:y+h, x:x+w]
        
        # Convertir roi a imagen BGR para poder dibujar círculos y números en color
        roi_color = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
        
        # Aplicar detección de círculos usando HoughCircles con parámetros ajustados
        circles = cv2.HoughCircles(
            roi,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=10,  # Aumentada distancia mínima
            param1=50,
            param2=18,  # Reducido para detectar más círculos
            minRadius=5,  # Reducido radio mínimo
            maxRadius=12  # Aumentado radio máximo
        )
        
        NUM_COLUMNAS = 5
        respuestas_por_columna = {}
        
        if circles is not None:
            circles = np.uint16(np.around(circles))
            
            # Ordenar círculos primero por coordenada Y (filas)
            circles_sorted = sorted(circles[0], key=lambda x: x[1])
            
            # Agrupar círculos por filas basado en proximidad vertical
            filas = []
            fila_actual = [circles_sorted[0]]
            y_anterior = circles_sorted[0][1]
            
            for circle in circles_sorted[1:]:
                y_actual = circle[1]
                if abs(y_actual - y_anterior) < 20:  # Aumentada tolerancia vertical
                    fila_actual.append(circle)
                else:
                    if len(fila_actual) >= 4:
                        filas.append(sorted(fila_actual, key=lambda x: x[0]))
                    fila_actual = [circle]
                y_anterior = y_actual
                
            if len(fila_actual) >= 4:
                filas.append(sorted(fila_actual, key=lambda x: x[0]))
            
            # Inicializar diccionario para cada columna
            for i in range(NUM_COLUMNAS):
                respuestas_por_columna[i+1] = []
                
            print("\nCírculos rellenados detectados por columna:")
            # Procesar cada fila
            for num_fila, fila in enumerate(filas):
                for j in range(0, len(fila), 4):
                    grupo = fila[j:j+4]
                    if len(grupo) == 4:
                        pregunta = num_fila + 1
                        columna_actual = (j // 4) + 1
                        
                        for i, (cx, cy, r) in enumerate(grupo):
                            circle_roi = roi[cy-r:cy+r, cx-r:cx+r]
                            total_pixels = circle_roi.size
                            dark_pixels = np.sum(circle_roi < 130)
                            density = dark_pixels / total_pixels
                            
                            if density > 0.20:
                                opcion = chr(65 + i)
                                respuestas_por_columna[columna_actual].append(f"Círculo {pregunta}{opcion} está rellenado")
                                cv2.circle(roi_color, (cx, cy), r, (0, 255, 0), 2)
                            else:
                                cv2.circle(roi_color, (cx, cy), r, (0, 0, 255), 1)
                            
                            cv2.putText(roi_color, f"{pregunta}{chr(65 + i)}", 
                                      (cx-r, cy-r), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
            
            # Imprimir respuestas agrupadas por columna
            for columna, respuestas in respuestas_por_columna.items():
                print(f"\nColumna {columna}:")
                for respuesta in respuestas:
                    print(respuesta)
                    
        plot_image(roi_color, "Hoja de Respuestas Procesada", False)

else:
    print("Error: No se pudo procesar la imagen")