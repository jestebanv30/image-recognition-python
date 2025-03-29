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

ruta_imagen = "C:/Users/valde/Desktop/image-recognition/assets/prueba-tipo-ifces.jpg"
img = cargar_imagen(ruta_imagen)

# PROCESAMIENTO DE IMAGEN
if img is not None:
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Aplicar umbralización para detectar mejor los bordes
    _, thresh = cv2.threshold(gray, 170, 255, cv2.THRESH_BINARY)
    
    # Detectar bordes
    edges = cv2.Canny(thresh, 50, 150)
    
    # Encontrar contornos para detectar la hoja de respuestas
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Encontrar el contorno más grande (que debería ser la hoja de respuestas)
    hoja_respuestas = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(hoja_respuestas)
    
    # Recortar la región de la hoja de respuestas
    roi = gray[y:y+h, x:x+w]
    
    # Convertir roi a imagen BGR para poder dibujar círculos y números en color
    roi_color = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
    
    # Aplicar detección de círculos usando HoughCircles
    circles = cv2.HoughCircles(
        roi,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=15,  # Distancia mínima entre círculos
        param1=50, # BORDES: Reducir para detectar más con más ruido, aumentar para detectar bordes más fuertes 
        param2=20, # CÍRCULOS: Reducir para detectar más círculos con bordes débiles, aumentar para detectar más claros y definidos 
        minRadius=8,
        maxRadius=12 
    )
    
    NUM_COLUMNAS = 3  # número de columnas de respuestas
    respuestas_por_columna = {}  # Diccionario para agrupar respuestas por columna
    
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
            # Si la diferencia en Y es pequeña, es parte de la misma fila
            if abs(y_actual - y_anterior) < 15:  # Umbral de 15 píxeles
                fila_actual.append(circle)
            else:
                if len(fila_actual) >= 4:  # Solo guardar filas con al menos 4 círculos
                    filas.append(sorted(fila_actual, key=lambda x: x[0]))  # Ordenar por X
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
            # Agrupar círculos de 4 en 4 dentro de cada fila
            for j in range(0, len(fila), 4):
                grupo = fila[j:j+4]
                if len(grupo) == 4:  # Solo procesar grupos completos de 4
                    pregunta = num_fila + 1
                    columna_actual = (j // 4) + 1  # Determinar a qué columna pertenece
                    
                    # Procesar cada círculo en el grupo
                    for i, (cx, cy, r) in enumerate(grupo):
                        # Extraer región del círculo
                        circle_roi = roi[cy-r:cy+r, cx-r:cx+r]
                        
                        # Calcular densidad de píxeles oscuros
                        total_pixels = circle_roi.size
                        dark_pixels = np.sum(circle_roi < 130)
                        density = dark_pixels / total_pixels
                        
                        # Si el círculo está marcado
                        if density > 0.30:
                            opcion = chr(65 + i)  # A, B, C, D
                            respuestas_por_columna[columna_actual].append(f"Círculo {pregunta}{opcion} está rellenado")
                            cv2.circle(roi_color, (cx, cy), r, (0, 255, 0), 2)
                        else:
                            cv2.circle(roi_color, (cx, cy), r, (0, 0, 255), 1)
                        
                        # Agregar etiqueta con número de pregunta y opción
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