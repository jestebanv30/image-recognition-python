import pandas as pd
import json

# Ruta al archivo de respuestas correctas
RESPUESTAS_PATH = r"C:/Users/valde/Desktop/image-recognition/models/respuestas_correctas.json"

# Ruta al Excel que contiene los estudiantes  
EXCEL_PATH = r"C:/Users/valde/Desktop/image-recognition/estudiantes-remedios-solano.xlsx"

# Nombre de la institución
INSTITUCION = "Institución Remedios Solano"

def obtener_total_preguntas_por_grado(respuestas_dict):
    """Retorna un diccionario con el grado como clave y el total de preguntas como valor."""
    return {
        grado: len(info["respuestas_correctas"])
        for grado, info in respuestas_dict.items()
    }

def generar_estructura_estudiantes(df, total_por_grado):
    estudiantes = []
    for _, row in df.iterrows():
        salon = str(row["SALON"])
        
        if len(salon) == 4:  # ej. 1001 o 1101
            grado = salon[:2]
            curso = salon[2:]
        else:  # ej. 601 o 705
            grado = salon[0]
            curso = salon[1:]
        
        # Eliminar ceros a la izquierda del curso
        curso = str(int(curso))
        
        total_preguntas = total_por_grado.get(grado)
        if not total_preguntas:
            print(f"Grado {grado} no encontrado en respuestas_correctas.json, saltando...")
            continue

        respuestas_vacias = {str(i): "" for i in range(1, total_preguntas + 1)}
        
        estudiante = {
            "archivo": "",  # Puede ser asignado luego
            "nombre": str(row["NOMBRE"]).strip(),
            "identificacion": str(row["IDENTIFICACION"]).strip(),
            "institucion": INSTITUCION,
            "grado": grado,
            "curso": curso,
            "respuestas": respuestas_vacias
        }
        estudiantes.append(estudiante)
    return estudiantes

def generar_json_desde_excel(excel_path, respuestas_path, output_json="resultados_generados.json"):
    # Cargar respuestas correctas
    with open(respuestas_path, encoding="utf-8") as f:
        respuestas_data = json.load(f)
    
    total_por_grado = obtener_total_preguntas_por_grado(respuestas_data)

    # Cargar todas las hojas del Excel
    all_dfs = pd.read_excel(excel_path, sheet_name=None)
    
    todos_los_estudiantes = []
    for sheet_name, df in all_dfs.items():
        if {"NOMBRE", "SALON", "IDENTIFICACION"}.issubset(df.columns):
            estudiantes = generar_estructura_estudiantes(df, total_por_grado)
            todos_los_estudiantes.extend(estudiantes)
        else:
            print(f"Hoja '{sheet_name}' omitida, columnas esperadas no encontradas.")

    json_data = {
        "total_estudiantes_detectados": len(todos_los_estudiantes),
        "total_estudiantes_sin_qr": 0,  # Se puede actualizar si manejas QR después
        "estudiantes": todos_los_estudiantes
    }

    # Guardar JSON resultante
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    print(f"Archivo generado correctamente: {output_json}")

# Ejecución
generar_json_desde_excel(EXCEL_PATH, RESPUESTAS_PATH)
