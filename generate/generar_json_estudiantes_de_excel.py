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
            # Combinar nombres y apellidos
            nombre_completo = f"{row['NOMBRES']} {row['APELLIDOS']}".upper()
            
            # Convertir a entero manejando valores NaN
            grado = int(row['GRADO']) if pd.notna(row['GRADO']) else 0
            curso = int(row['CURSO']) if pd.notna(row['CURSO']) else 0
            identificacion = int(row['IDENTIFICACIÓN']) if pd.notna(row['IDENTIFICACIÓN']) else 0
            
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
