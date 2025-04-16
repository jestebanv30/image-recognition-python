# RECONOCIMIENTO DE CIRCULOS GRADO 4 Y 5

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

def agrupar_columnas_por_x(circulos, num_columnas):
    circulos_ordenados = sorted(circulos, key=lambda c: c[0])
    x_vals = [c[0] for c in circulos_ordenados]
    x_min = min(x_vals)
    x_max = max(x_vals)
    ancho_total = x_max - x_min
    separacion = ancho_total / (num_columnas - 1)

    columnas = [[] for _ in range(num_columnas)]

    for c in circulos_ordenados:
        index = int((c[0] - x_min + separacion / 2) // separacion)
        index = max(0, min(index, num_columnas - 1))
        columnas[index].append(c)

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

def detectar_respuestas_estudiante(ruta_imagen, formato_columnas, dp_values=[1.002, 1.003, 1.004, 1.35, 1.36, 1.37, 1.38, 1.39]):
    roi = procesar_hoja_de_respuestas_con_marcadores(ruta_imagen, mostrar_resultados=False)
    if roi is None:
        print("No se pudo detectar la región de la hoja.")
        return

    roi_gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    respuestas_por_dp = []
    visualizaciones_por_dp = []
    cantidad_por_dp = []

    for dp in dp_values:
        print(f"Probando con dp = {dp}")
        roi_dp_color = roi.copy()

        circulos = cv2.HoughCircles(
            roi_gray,
            cv2.HOUGH_GRADIENT,
            dp=dp,
            minDist=8,
            param1=40,
            param2=17,
            minRadius=8,
            maxRadius=10
        )

        if circulos is None:
            print(f"No se detectaron círculos con dp = {dp}.")
            continue

        circulos = np.uint16(np.around(circulos[0]))
        columnas = agrupar_columnas_por_x(circulos, num_columnas=len(formato_columnas))
        columnas = sorted(columnas, key=lambda col: np.mean([int(c[0]) for c in col]))

        numeracion_inicial_columnas = [1]
        for i in range(1, len(formato_columnas)):
            numeracion_inicial_columnas.append(numeracion_inicial_columnas[i - 1] + formato_columnas[i - 1])

        respuestas_dp = {}

        for idx_col, col in enumerate(columnas):
            if idx_col >= len(numeracion_inicial_columnas):
                break

            pregunta = numeracion_inicial_columnas[idx_col]
            filas = agrupar_filas_horizontales(col, tolerancia_y=15)
            limite = formato_columnas[idx_col] if idx_col < len(formato_columnas) else len(filas)

            for fila in filas[:limite]:
                opciones = [chr(65 + i) for i in range(len(fila))]
                densidades = []

                for i, (cx, cy, r) in enumerate(fila):
                    circle_roi = roi_gray[cy - r:cy + r, cx - r:cx + r]
                    total_pixels = circle_roi.size
                    dark_pixels = np.sum(circle_roi < 130)
                    density = dark_pixels / total_pixels
                    densidades.append((density, opciones[i], (cx, cy, r)))

                DENSIDAD_UMBRAL = 0.22 # 0.22 para 501,502,503,504 - 0.17 para 401 - 0.24 para 402 y 403
                marcadas_validas = [(dens, op, pos) for dens, op, pos in densidades if dens > DENSIDAD_UMBRAL]

                if not marcadas_validas:
                    respuestas_dp[f"{pregunta}"] = "No marcada"
                else:
                    densidad_maxima = max(marcadas_validas, key=lambda x: x[0])
                    marcada = densidad_maxima[1]
                    cx, cy, r = densidad_maxima[2]
                    respuestas_dp[f"{pregunta}"] = marcada
                    cv2.circle(roi_dp_color, (cx, cy), r, (0, 255, 0), 2)

                # Dibujar todos los círculos con etiquetas
                for dens, op, (cx, cy, r) in densidades:
                    color = (0, 255, 0) if dens > DENSIDAD_UMBRAL else (0, 0, 255)
                    cv2.circle(roi_dp_color, (cx, cy), r, color, 1)
                    cv2.putText(roi_dp_color, f"{pregunta}{op}", (cx - 10, cy - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

                pregunta += 1

        print(f"dp = {dp} detectó {len(respuestas_dp)} preguntas.")
        respuestas_por_dp.append(respuestas_dp)
        visualizaciones_por_dp.append(roi_dp_color)
        cantidad_por_dp.append(len(respuestas_dp))

    # Combinar respuestas detectadas por todos los dp
    respuestas_combinadas = {}
    for respuestas in respuestas_por_dp:
        for pregunta, respuesta in respuestas.items():
            if pregunta not in respuestas_combinadas or respuestas_combinadas[pregunta] == "No marcada":
                respuestas_combinadas[pregunta] = respuesta

    print(f"\nTotal preguntas únicas combinadas: {len(respuestas_combinadas)}")

    # Mostrar la imagen del dp que detectó más respuestas
    if cantidad_por_dp:
        indice_mejor_dp = cantidad_por_dp.index(max(cantidad_por_dp))
        imagen_mejor = visualizaciones_por_dp[indice_mejor_dp]
        plot_image(imagen_mejor, "Detección de Respuestas", grayscale=False)

    return dict(sorted(respuestas_combinadas.items(), key=lambda x: int(x[0])))

# Prueba
if __name__ == "__main__":
    ruta = "C:/Users/valde/Desktop/image-recognition/assets/GRADO 501/1.jpg"
    formato = [24, 24, 24, 24, 24] # Formato para cuarto y quinto grado 
    resultado = detectar_respuestas_estudiante(ruta, formato)
    print("\nRespuestas detectadas:")
    print(resultado)
