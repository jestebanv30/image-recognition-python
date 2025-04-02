import json
from recognition.lectura_qr_estudiante import leer_qr_desde_imagen
from recognition.procesamiento_circulos import procesar_circulos

def extraer_info_dict(info_qr):
    # Convierte el texto del QR a un diccionario
    partes = [parte.strip() for parte in info_qr.split(',')]
    datos = {}
    for parte in partes:
        if ':' in parte:
            clave, valor = parte.split(':', 1)
            datos[clave.strip().lower()] = valor.strip()
    return datos

def main():
    # Lista de imágenes a procesar (una por estudiante)
    rutas_imagenes = [
        "C:/Users/valde/Desktop/image-recognition/assets/image.png",
        # Puedes agregar más rutas de imágenes aquí
    ]

    resultados = []

    for ruta in rutas_imagenes:
        print(f"Procesando archivo: {ruta}")

        info_qr = leer_qr_desde_imagen(ruta)
        if not info_qr:
            print("No se pudo leer el QR.")
            continue

        datos_estudiante = extraer_info_dict(info_qr)

        respuestas = procesar_circulos(ruta)
        if respuestas is None:
            respuestas = {}

        resultado = {
            "nombre": datos_estudiante.get("nombre", "Desconocido"),
            "identificacion": datos_estudiante.get("identificación", "Desconocido"),
            "institucion": datos_estudiante.get("institución", "Desconocida"),
            "grado": datos_estudiante.get("grado", ""),
            "curso": datos_estudiante.get("curso", ""),
            "respuestas": {
                f"columna_{col}": respuestas_columna
                for col, respuestas_columna in respuestas.items()
            }
        }

        resultados.append(resultado)

    # Guardar resultados en archivo JSON
    with open("resultados_estudiantes.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)

    print("Archivo JSON generado: resultados_estudiantes.json")

if __name__ == "__main__":
    main()
