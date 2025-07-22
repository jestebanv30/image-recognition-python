import pandas as pd
import json

# Ruta al Excel que contiene los estudiantes  
EXCEL_PATH = r"C:/Users/valde/Desktop/image-recognition/estudiantes-elcarmelo2.xlsx"

# Nombre de la institución
INSTITUCION = "Institución Educativa El Carmelo"

# Número de preguntas a generar
TOTAL_PREGUNTAS = 58

def generar_estructura_estudiantes(df):
    estudiantes = []
    for _, row in df.iterrows():
        # Unir apellidos y nombres
        nombre_completo = f"{str(row['APELLIDOS']).strip()} {str(row['NOMBRES']).strip()}"

        # Obtener grado y curso directamente
        grado = str(row["GRADO"]).strip()
        curso = str(row["CURSO"]).strip()
        # Eliminar ceros a la izquierda del curso si es numérico
        try:
            curso = str(int(curso))
        except:
            curso = curso

        # Generar diccionario de respuestas vacías del 1 al TOTAL_PREGUNTAS
        respuestas_vacias = {str(i): "" for i in range(1, TOTAL_PREGUNTAS + 1)}
        
        estudiante = {
            "archivo": "",  # Puede ser asignado luego
            "nombre": nombre_completo,
            "identificacion": str(row["IDENTIFICACIÓN"]).strip(),
            "institucion": INSTITUCION,
            "grado": grado,
            "curso": curso,
            "respuestas": respuestas_vacias
        }
        estudiantes.append(estudiante)
    return estudiantes

def generar_json_desde_excel(excel_path, output_json="estudiantes_manual.json"):
    # Cargar todas las hojas del Excel
    all_dfs = pd.read_excel(excel_path, sheet_name=None)
    
    todos_los_estudiantes = []
    for sheet_name, df in all_dfs.items():
        columnas_esperadas = {"APELLIDOS", "NOMBRES", "GRADO", "CURSO", "IDENTIFICACIÓN"}
        if columnas_esperadas.issubset(df.columns):
            estudiantes = generar_estructura_estudiantes(df)
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
generar_json_desde_excel(EXCEL_PATH)
