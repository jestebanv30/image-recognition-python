import json
import os
from recognition.lectura_qr_estudiante import leer_qr_desde_imagen
from recognition.procesamiento_circulos_ultimate2 import detectar_respuestas_estudiante

def extraer_info_dict(info_qr):
    partes = [parte.strip() for parte in info_qr.split(',')]
    datos = {}
    for parte in partes:
        if ':' in parte:
            clave, valor = parte.split(':', 1)
            datos[clave.strip().lower()] = valor.strip()
    return datos

def completar_datos_estudiantes(estudiantes):
    grado_valido = None
    curso_valido = None
    institucion_valida = None

    for est in estudiantes:
        if est["grado"] not in [None, "", "No detectado"] and not grado_valido:
            grado_valido = est["grado"]
        if est["curso"] not in [None, "", "No detectado"] and not curso_valido:
            curso_valido = est["curso"]
        if est["institucion"] not in [None, "", "No detectado", "Desconocida"] and not institucion_valida:
            institucion_valida = est["institucion"]
        if grado_valido and curso_valido and institucion_valida:
            break

    for est in estudiantes:
        if est["grado"] in [None, "", "No detectado"]:
            est["grado"] = grado_valido
        if est["curso"] in [None, "", "No detectado"]:
            est["curso"] = curso_valido
        if est["institucion"] in [None, "", "No detectado", "Desconocida"]:
            est["institucion"] = institucion_valida

    return estudiantes

def main():
    directorio_imagenes = "C:/Users/valde/Desktop/image-recognition/assets/NUEVO"
    extensiones_validas = ('.png', '.jpg', '.jpeg', '.tiff', '.bmp')
    rutas_imagenes = [
        os.path.join(directorio_imagenes, archivo)
        for archivo in os.listdir(directorio_imagenes)
        if archivo.lower().endswith(extensiones_validas)
    ]

    resultados = []
    estudiantes_detectados = 0
    estudiantes_sin_qr = 0
    estudiantes_con_preguntas_invalidas = []

    for ruta in rutas_imagenes:
        print(f"Procesando archivo: {ruta}")
        nombre_archivo = os.path.basename(ruta)

        info_qr = leer_qr_desde_imagen(ruta)
        if not info_qr:
            print(f"No se pudo leer el QR en: {nombre_archivo}")
            datos_estudiante = {
                "nombre": "No detectado",
                "identificación": "No detectado",
                "institución": "No detectado",
                "grado": "No detectado",
                "curso": "No detectado"
            }
            estudiantes_sin_qr += 1
        else:
            datos_estudiante = extraer_info_dict(info_qr)
            if "nombre" not in datos_estudiante:
                datos_estudiante["nombre"] = "No detectado"

        respuestas = detectar_respuestas_estudiante(ruta, formato_columnas=[24, 24, 24, 24, 24])
        if respuestas is None:
            print(f"No se pudieron detectar respuestas en: {nombre_archivo}")
            respuestas = {}
        else:
            estudiantes_detectados += 1

        if len(respuestas) != 120:
            estudiantes_con_preguntas_invalidas.append(nombre_archivo)

        resultado = {
            "archivo": nombre_archivo,
            "nombre": datos_estudiante.get("nombre", "No detectado"),
            "identificacion": datos_estudiante.get("identificación", "No detectado"),
            "institucion": datos_estudiante.get("institución", "No detectado"),
            "grado": datos_estudiante.get("grado", "No detectado"),
            "curso": datos_estudiante.get("curso", "No detectado"),
            "respuestas": respuestas
        }

        resultados.append(resultado)

    # 🔧 Completar datos faltantes
    resultados = completar_datos_estudiantes(resultados)

    resultado_final = {
        "total_estudiantes_detectados": estudiantes_detectados,
        "total_estudiantes_sin_qr": estudiantes_sin_qr,
        "estudiantes": resultados
    }

    directorio_salida = "C:/Users/valde/Desktop/image-recognition/resultados_estudiantes_json"
    os.makedirs(directorio_salida, exist_ok=True)

    grado_curso = None
    for estudiante in resultados:
        if estudiante["grado"] and estudiante["grado"] != "No detectado" and estudiante["curso"]:
            grado_curso = (estudiante["grado"], estudiante["curso"])
            break

    if grado_curso:
        nombre_archivo_json = f"resultados_{grado_curso[0]}_{grado_curso[1]}.json"
    else:
        nombre_archivo_json = "resultados_NONE.json"

    ruta_completa = os.path.join(directorio_salida, nombre_archivo_json)

    with open(ruta_completa, "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, indent=4, ensure_ascii=False)

    print(f"\n✅ Archivo JSON generado: {ruta_completa}")
    print(f"📌 Total de estudiantes detectados: {estudiantes_detectados}")
    print(f"📌 Total de estudiantes sin QR detectado: {estudiantes_sin_qr}")

    if estudiantes_con_preguntas_invalidas:
        print("\n⚠️ Estudiantes con menos o más de 120 preguntas respondidas:")
        for estudiante in estudiantes_con_preguntas_invalidas:
            print(f" - {estudiante}")

if __name__ == "__main__":
    main()
