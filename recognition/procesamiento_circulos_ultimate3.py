# RECONOCIMIENTO DE CIRCULOS GRADO 10 y 11

import cv2
import numpy as np
from recognition.reconocimiento_marcadores2 import procesar_hoja_de_respuestas_con_marcadores

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

def agrupar_filas_y(columna, tolerancia_y=20, min_opciones=3):
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

def alinear_filas_con_referencia(filas_actual, filas_referencia, tolerancia_y=20):
    alineadas = []
    usadas = set()
    for ref in filas_referencia:
        y_ref = np.mean([pt[1] for pt in ref])
        candidata = None
        for idx, fila in enumerate(filas_actual):
            if idx in usadas:
                continue
            y_fila = np.mean([pt[1] for pt in fila])
            if abs(y_fila - y_ref) < tolerancia_y:
                candidata = fila
                usadas.add(idx)
                break
        alineadas.append(candidata if candidata else [])
    return alineadas

def detectar_respuestas_estudiante(ruta_imagen, formato_columnas, dp_values=[1.002, 1.003, 1.004, 1.35]):
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
        circulos = cv2.HoughCircles(roi_gray, cv2.HOUGH_GRADIENT, dp=dp, minDist=5,
                                    param1=40, param2=18, minRadius=5, maxRadius=8)
        if circulos is None:
            print(f"No se detectaron círculos con dp = {dp}.")
            continue

        circulos = np.uint16(np.around(circulos[0]))
        columnas = agrupar_columnas_por_x(circulos, num_columnas=len(formato_columnas))
        columnas = sorted(columnas, key=lambda col: np.mean([int(c[0]) for c in col]))
        numeracion_inicial_columnas = [1]
        for i in range(1, len(formato_columnas)):
            numeracion_inicial_columnas.append(numeracion_inicial_columnas[i - 1] + formato_columnas[i - 1])

        filas_columnas = [agrupar_filas_y(col, tolerancia_y=15) for col in columnas]
        filas_ref = max(filas_columnas, key=len)  # usar la columna con más filas como referencia

        respuestas_dp = {}
        for idx_col, filas in enumerate(filas_columnas):
            pregunta = numeracion_inicial_columnas[idx_col]
            alineadas = alinear_filas_con_referencia(filas, filas_ref, tolerancia_y=15)
            for fila in alineadas:
                if not fila:
                    respuestas_dp[f"{pregunta}"] = "No marcada"
                    pregunta += 1
                    continue

                opciones = [chr(65 + i) for i in range(len(fila))]
                densidades = []
                for i, (cx, cy, r) in enumerate(fila):
                    circle_roi = roi_gray[cy - r:cy + r, cx - r:cx + r]
                    total_pixels = circle_roi.size
                    dark_pixels = np.sum(circle_roi < 130)
                    density = dark_pixels / total_pixels
                    densidades.append((density, opciones[i], (cx, cy, r)))

                DENSIDAD_UMBRAL = 0.22
                marcadas_validas = [(dens, op, pos) for dens, op, pos in densidades if dens > DENSIDAD_UMBRAL]

                if not marcadas_validas:
                    respuestas_dp[f"{pregunta}"] = "No marcada"
                else:
                    densidad_maxima = max(marcadas_validas, key=lambda x: x[0])
                    marcada = densidad_maxima[1]
                    cx, cy, r = densidad_maxima[2]
                    respuestas_dp[f"{pregunta}"] = marcada
                    cv2.circle(roi_dp_color, (cx, cy), r, (0, 255, 0), 2)

                for dens, op, (cx, cy, r) in densidades:
                    color = (0, 255, 0) if dens > DENSIDAD_UMBRAL else (0, 0, 255)
                    cv2.circle(roi_dp_color, (cx, cy), r, color, 1)
                    cv2.putText(roi_dp_color, f"{pregunta}{op}", (cx - 10, cy - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 0), 1)

                pregunta += 1

        respuestas_por_dp.append(respuestas_dp)
        visualizaciones_por_dp.append(roi_dp_color)
        cantidad_por_dp.append(len(respuestas_dp))

    respuestas_combinadas = {}
    for respuestas in respuestas_por_dp:
        for pregunta, respuesta in respuestas.items():
            if pregunta not in respuestas_combinadas or respuestas_combinadas[pregunta] == "No marcada":
                respuestas_combinadas[pregunta] = respuesta

    print(f"\nTotal preguntas reconocidas en combinación: {len(respuestas_combinadas)}")

    if cantidad_por_dp:
        for idx, imagen in enumerate(visualizaciones_por_dp):
            dp_usado = dp_values[idx]
            #plot_image(imagen, f"Detección con dp = {dp_usado}", grayscale=False)

    return dict(sorted(respuestas_combinadas.items(), key=lambda x: int(x[0])))


# Prueba
if __name__ == "__main__":
    ruta = "C:/Users/valde/Desktop/image-recognition/assets/GRADO 1001/0.jpg"
    formato = [27, 27, 27, 27, 27]
    resultado = detectar_respuestas_estudiante(ruta, formato)
    print("\nRespuestas detectadas:")
    print(resultado)
