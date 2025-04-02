import json
import os

def obtener_formato_por_grado(grado):
    ruta_actual = os.path.dirname(os.path.abspath(__file__))
    ruta_json = os.path.join(ruta_actual, "formatos_hojas_respuestas.json")
    
    with open(ruta_json, "r", encoding="utf-8") as f:
        formatos = json.load(f)
        for formato in formatos:
            if formato["grado"] == grado:
                return formato
        raise ValueError(f"No se encontró formato para grado {grado}")
