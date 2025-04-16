import cv2
import numpy as np
from reconocimiento_marcadores2 import procesar_hoja_de_respuestas_con_marcadores

def plot_image(img, titulo="Imagen", grayscale=True):
    try:
        if grayscale and len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imshow(titulo, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error al mostrar la imagen: {str(e)}")

def agrupar_columnas_por_x(circulos, distancia_x=65):
    columnas = []
    for c in circulos:
        x = int(c[0])
        agregado = False
        for columna in columnas:
            if abs(int(np.mean([p[0] for p in columna])) - x) < distancia_x:
                columna.append(c)
                agregado = True
                break
        if not agregado:
            columnas.append([c])
    return columnas

def agrupar_filas_horizontales(columna, tolerancia_y=20, min_opciones=3):
    filas = []
    columna = sorted(columna, key=lambda c: int(c[1]))
    actual = [columna[0]]
    for c in columna[1:]:
        if abs(int(c[1]) - int(actual[-1][1])) < tolerancia_y:
            actual.append(c)
        else:
            if len(actual) >= min_opciones:
                filas.append(sorted(actual, key=lambda x: int(x[0])))
            actual = [c]
    if len(actual) >= min_opciones:
        filas.append(sorted(actual, key=lambda x: int(x[0])))
    return filas

def detectar_respuestas_estudiante(ruta_imagen, formato_columnas, dp_values=[1.001, 1.002, 1.003, 1.004]):
    roi = procesar_hoja_de_respuestas_con_marcadores(ruta_imagen, mostrar_resultados=False)
    if roi is None:
        print("No se pudo detectar la región de la hoja.")
        return

    roi_color = roi.copy()
    
    # Convertir a escala de grises para HoughCircles
    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    
    respuestas = {}
    
    # Probar diferentes valores de dp
    for dp in dp_values:
        print(f"Probando con dp = {dp}")
        
        circulos = cv2.HoughCircles(
            roi_gray,
            cv2.HOUGH_GRADIENT,
            dp=dp,  # Probar con diferentes dp
            minDist=8, #6
            param1=40, #40
            param2=17, #20
            minRadius=8, #6
            maxRadius=16 #15
        )

        if circulos is None:
            print(f"No se detectaron círculos con dp = {dp}. Probando otro valor.")
            continue

        circulos = np.uint16(np.around(circulos[0]))
        columnas = agrupar_columnas_por_x(circulos)
        columnas = sorted(columnas, key=lambda col: np.mean([int(c[0]) for c in col]))

        pregunta = 1
        for idx_col, col in enumerate(columnas):
            filas = agrupar_filas_horizontales(col)
            limite = formato_columnas[idx_col] if idx_col < len(formato_columnas) else len(filas)
            for fila in filas[:limite]:
                opciones = [chr(65 + i) for i in range(len(fila))]
                marcada = None
                no_marcada = True  # Flag para verificar si hay opciones marcadas
                for i, (cx, cy, r) in enumerate(fila):
                    circle_roi = roi_gray[cy-r:cy+r, cx-r:cx+r]
                    total_pixels = circle_roi.size
                    dark_pixels = np.sum(circle_roi < 130)
                    density = dark_pixels / total_pixels
                    if density > 0.30:
                        marcada = opciones[i]
                        no_marcada = False  # Al menos una opción fue marcada
                        cv2.circle(roi_color, (cx, cy), r, (0, 255, 0), 2)
                    else:
                        cv2.circle(roi_color, (cx, cy), r, (0, 0, 255), 1)
                    cv2.putText(roi_color, f"{pregunta}{opciones[i]}", (cx - 10, cy - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

                if no_marcada:  # Si no se ha marcado ninguna opción, asignamos "No marcada"
                    respuestas[f"{pregunta}"] = "No marcada"
                elif marcada:
                    respuestas[f"{pregunta}"] = marcada
                pregunta += 1

        # Verificar si detectó 58 preguntas
        if len(respuestas) == 58:
            print(f"Detectado 58 preguntas con dp = {dp}. Usando esta configuración.")
            break
    else:
        print("No se detectaron 58 preguntas con los valores de dp probados.")
    
    # Mostrar la imagen con las detecciones
    plot_image(roi_color, "Detección de Respuestas", grayscale=False)
    
    return respuestas

# Prueba
if __name__ == "__main__":
    ruta = "C:/Users/valde/Desktop/image-recognition/assets/GRADO 301/202504081559_00001.jpg"
    formato = [17, 17, 17, 17, 15]
    resultado = detectar_respuestas_estudiante(ruta, formato)
    print("\nRespuestas detectadas:")
    print(resultado)
