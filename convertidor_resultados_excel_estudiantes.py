import json
import pandas as pd
from openpyxl import load_workbook
import os

def cargar_respuestas_correctas(grado):
    with open('models/respuestas_correctas.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        if str(grado) not in data:
            raise ValueError(f"No hay configuración de respuestas para el grado {grado} en el archivo JSON models.")
        return data[str(grado)]['respuestas_correctas']

def materias_excel_respuestas(grado):
    with open('models/respuestas_correctas.json', 'r', encoding='utf-8') as file:
        data = json.load(file)
        if str(grado) not in data:
            raise ValueError(f"No hay configuración de respuestas para el grado {grado} en el archivo JSON models.")
        materias_data = data[str(grado)]['materias']
        materias_rangos = {}
        for materia, rango in materias_data.items():
            materias_rangos[materia] = range(rango[0], rango[1] + 1)
        return materias_rangos

def calcular_porcentaje(respuestas, rango, respuestas_correctas):
    correctas = 0
    incorrectas = 0
    no_marcadas = 0
    total_preguntas = 0
    for num in rango:
        str_num = str(num)
        if respuestas_correctas.get(str_num) != 'Anulada':
            if str_num in respuestas:
                total_preguntas += 1
                if respuestas[str_num] == 'No marcada':
                    incorrectas += 1
                    no_marcadas += 1
                elif respuestas[str_num] == respuestas_correctas[str_num]:
                    correctas += 1
                else:
                    incorrectas += 1
    return correctas, total_preguntas, no_marcadas

def process_data(json_file_path, respuestas_correctas, materias, umbral_no_marcadas):
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    grado_detectado = None
    curso_detectado = None
    institucion_detectada = None

    for estudiante in data['estudiantes']:
        if estudiante['grado'] != "No detectado":
            grado_detectado = int(estudiante['grado']) if str(estudiante['grado']).isdigit() else estudiante['grado']
        if estudiante['curso'] != "No detectado":
            curso_detectado = int(estudiante['curso']) if str(estudiante['curso']).isdigit() else estudiante['curso']
        if estudiante['institucion'] not in ["No detectado", "Desconocida", "", None]:
            institucion_detectada = estudiante['institucion']
        if grado_detectado and curso_detectado and institucion_detectada:
            break

    resultados = []
    for estudiante in data['estudiantes']:
        grado = estudiante['grado'] if estudiante['grado'] != "No detectado" else grado_detectado
        curso = estudiante['curso'] if estudiante['curso'] != "No detectado" else curso_detectado
        institucion = estudiante['institucion'] if estudiante['institucion'] not in ["No detectado", "Desconocida", "", None] else institucion_detectada

        resultado = {
            'ARCHIVO': estudiante['archivo'],
            'NOMBRE': estudiante['nombre'],
            'IDENTIFICACION': estudiante['identificacion'],
            'INSTITUCION': institucion,
            'GRADO': int(grado) if isinstance(grado, str) and grado.isdigit() else grado,
            'CURSO': int(curso) if isinstance(curso, str) and curso.isdigit() else curso
        }

        observaciones = []
        puntajes_materias = []

        for materia, rango in materias.items():
            correctas, total_preguntas, no_marcadas = calcular_porcentaje(estudiante['respuestas'], rango, respuestas_correctas)
            porcentaje = (correctas / total_preguntas * 100) if total_preguntas > 0 else 0
            porcentaje_final = round(max(porcentaje, 30.00), 2)
            resultado[materia] = porcentaje_final
            puntajes_materias.append(porcentaje_final)

            if no_marcadas >= umbral_no_marcadas:
                observaciones.append("Calificar manualmente, no marcadas supera el mínimo de 4")
            if estudiante['identificacion'] == 'No detectado':
                observaciones.append("QR no detectado, buscar credenciales con el nombre del archivo")

        # Calcular puntaje global
        if puntajes_materias:
            resultado["PUNTAJE_GLOBAL"] = round(sum(puntajes_materias) / len(puntajes_materias), 2)
        else:
            resultado["PUNTAJE_GLOBAL"] = 0.0

        resultado['OBSERVACIONES'] = observaciones[0] if observaciones else "No hay observaciones"
        resultados.append(resultado)

    return pd.DataFrame(resultados)

def highlight_observaciones(row):
    styles = [''] * len(row)
    if "QR no detectado" in row['OBSERVACIONES']:
        styles = ['background-color: yellow'] * len(row)
    if "Calificar manualmente" in row['OBSERVACIONES']:
        styles = ['background-color: red'] * len(row)
    return styles

def apply_borders(val):
    return 'border: 1px solid black'

def export_to_excel(dataframes_dict, file_name):
    with pd.ExcelWriter(f"{file_name}.xlsx", engine='openpyxl') as writer:
        for sheet_name, df in dataframes_dict.items():
            df_styled = df.style.apply(highlight_observaciones, axis=1).applymap(apply_borders)
            df_styled.to_excel(writer, sheet_name=sheet_name, index=False)

            worksheet = writer.sheets[sheet_name]
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).apply(len).max(), len(str(col)))
                worksheet.column_dimensions[chr(65 + idx)].width = max_length + 2

def main():
    json_dir = r"C:\\Users\\valde\\Desktop\\image-recognition\\resultados_estudiantes_json"
    dataframes_dict = {}

    for filename in os.listdir(json_dir):
        if filename.startswith("resultados_") and filename.endswith(".json"):
            grado = int(filename.split('_')[1])
            respuestas_correctas = cargar_respuestas_correctas(grado)
            materias = materias_excel_respuestas(grado)
            umbral_no_marcadas = 5

            sheet_name = f"CURSO_{filename.split('_')[2].replace('.json', '')}"
            json_path = os.path.join(json_dir, filename)
            df = process_data(json_path, respuestas_correctas, materias, umbral_no_marcadas)
            dataframes_dict[sheet_name] = df

    if dataframes_dict:
        export_to_excel(dataframes_dict, f"resultados_grado_{grado}")
        print("Archivo Excel generado con éxito")
    else:
        print("No se encontraron archivos JSON para procesar")

if __name__ == "__main__":
    main()
