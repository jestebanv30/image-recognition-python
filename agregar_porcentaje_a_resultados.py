import os
import pandas as pd
from openpyxl.utils import get_column_letter

# === CONFIGURACIÓN ===
CARPETA_ENTRADA = r"C:\Users\valde\Desktop\image-recognition\porcentaje_para_grados"
CARPETA_SALIDA = r"C:\Users\valde\Desktop\image-recognition\porcentaje_para_grados_ajustados"
PORCENTAJE_AUMENTO = 15
NOTA_MAXIMA = 100.0

COLUMNAS_EXCLUIR = ['ARCHIVO', 'NOMBRE', 'IDENTIFICACION', 'INSTITUCION', 'GRADO', 'CURSO', 'OBSERVACIONES']

# === FUNCIONES ===

def highlight_observaciones(row):
    styles = [''] * len(row)
    if "QR no detectado" in row.get('OBSERVACIONES', ''):
        styles = ['background-color: yellow'] * len(row)
    if "Calificar manualmente" in row.get('OBSERVACIONES', ''):
        styles = ['background-color: red'] * len(row)
    return styles

def apply_borders(val):
    return 'border: 1px solid black'

def aumentar_notas(df, porcentaje):
    df_modificado = df.copy()
    columnas_materias = [col for col in df.columns if col not in COLUMNAS_EXCLUIR]
    for col in columnas_materias:
        df_modificado[col] = df_modificado[col].apply(
            lambda x: round(min(x * (1 + porcentaje / 100), NOTA_MAXIMA), 2)
            if pd.notnull(x) and isinstance(x, (int, float)) else x
        )
    return df_modificado

def exportar_excel_estilo(dataframes_dict, nombre_salida):
    with pd.ExcelWriter(nombre_salida, engine='openpyxl') as writer:
        for hoja, df in dataframes_dict.items():
            df_styled = df.style.apply(highlight_observaciones, axis=1).applymap(apply_borders)
            df_styled.to_excel(writer, sheet_name=hoja, index=False)

            # Ajuste automático del ancho de las columnas
            worksheet = writer.sheets[hoja]
            for idx, col in enumerate(df.columns, 1):  # openpyxl usa índices desde 1
                max_length = max(
                    df[col].astype(str).map(len).max(),
                    len(str(col))
                )
                worksheet.column_dimensions[get_column_letter(idx)].width = max_length + 2

# === FLUJO PRINCIPAL ===

def procesar_todos_los_excel():
    if not os.path.exists(CARPETA_SALIDA):
        os.makedirs(CARPETA_SALIDA)

    archivos = [f for f in os.listdir(CARPETA_ENTRADA) if f.endswith('.xlsx') and f.startswith('resultados_grado_')]

    for archivo in archivos:
        ruta_archivo = os.path.join(CARPETA_ENTRADA, archivo)
        nombre_salida = os.path.join(CARPETA_SALIDA, f"ajustado_{archivo}")

        excel = pd.ExcelFile(ruta_archivo)
        dataframes_dict = {}

        for hoja in excel.sheet_names:
            df = excel.parse(hoja)
            df_ajustada = aumentar_notas(df, PORCENTAJE_AUMENTO)
            dataframes_dict[hoja] = df_ajustada

        exportar_excel_estilo(dataframes_dict, nombre_salida)
        print(f"✅ Archivo generado: {nombre_salida}")

# === EJECUCIÓN ===
if __name__ == "__main__":
    procesar_todos_los_excel()
