import pandas as pd
import json
import os

def leer_estudiantes(ruta_archivo):
    try:
        # Leer el archivo Excel
        df = pd.read_excel(ruta_archivo)
        
        # Procesar los datos
        estudiantes = []
        
        for _, row in df.iterrows():
            # Obtener nombre completo en mayúsculas
            nombre_completo = str(row['NOMBRE COMPLETO']).upper()
            
            # Obtener identificación como string
            identificacion = str(row['IDENTIFICACIÓN']) if pd.notna(row['IDENTIFICACIÓN']) else ''
            
            # Procesar curso (ej: '601' -> grado 6, curso 1 o '1001' -> grado 10, curso 1)
            curso_completo = str(row['CURSO'])
            if len(curso_completo) == 3:  # Para grados 1-9
                grado = int(curso_completo[0])
                curso = int(curso_completo[1:])
            else:  # Para grados 10 y 11
                grado = int(curso_completo[:2])  # Dos primeros dígitos son el grado
                curso = int(curso_completo[2:])  # Resto de dígitos es el curso
            
            estudiante = {
                'nombre_completo': nombre_completo,
                'grado': grado,
                'curso': curso,
                'identificacion': identificacion
            }
            estudiantes.append(estudiante)
            
        return estudiantes
        
    except Exception as e:
        print(f"Error al leer el archivo: {str(e)}")
        return None
    
def main(ruta_excel):
    # Obtener los datos de estudiantes
    estudiantes = leer_estudiantes(ruta_excel)
    
    if estudiantes:
        total_estudiantes = len(estudiantes)
        print(f"\nTotal de estudiantes procesados: {total_estudiantes}")
        
        # Crear diccionario con la información
        datos = {
            "total_estudiantes": total_estudiantes,
            "estudiantes": estudiantes
        }
        
        # Guardar JSON en la ruta raíz
        ruta_json = "estudiantes.json"
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
            
        print(f"\nArchivo JSON generado en: {os.path.abspath(ruta_json)}")

if __name__ == "__main__":
    ruta_excel = "C:/Users/valde/Desktop/image-recognition/estudiantes.xlsx"
    main(ruta_excel)
