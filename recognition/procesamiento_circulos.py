import cv2
import numpy as np
#from recognition.reconocimiento_marcadores import procesar_imagen_con_marcadores
from reconocimiento_marcadores import procesar_imagen_con_marcadores

def plot_image(img, titulo="Imagen", grayscale=True):
    try:
        if grayscale and len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imshow(titulo, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error al mostrar la imagen: {str(e)}")

def procesar_circulos(ruta_imagen):
    # Obtener la región de interés usando reconocimiento_marcadores
    roi_estandarizada = procesar_imagen_con_marcadores(ruta_imagen, mostrar_resultados=False)

    if roi_estandarizada is not None:
        # Convertir a escala de grises
        roi = cv2.cvtColor(roi_estandarizada, cv2.COLOR_BGR2GRAY)
        
        # Convertir roi a imagen BGR para poder dibujar círculos y números en color
        roi_color = cv2.cvtColor(roi, cv2.COLOR_GRAY2BGR)
        
        # Aplicar detección de círculos usando HoughCircles con parámetros ajustados
        circles = cv2.HoughCircles(
            roi,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=10,  # Aumentada distancia mínima
            param1=45,
            param2=28,  # Reducido para detectar más círculos
            minRadius=7,  # Reducido radio mínimo
            maxRadius=14  # Aumentado radio máximo
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
        return respuestas_por_columna

    else:
        print("Error: No se pudo procesar la imagen")
        return None
    
if __name__ == "__main__":
    ruta_imagen = "C:/Users/valde/Desktop/image-recognition/assets/image.png"
    procesar_circulos(ruta_imagen)