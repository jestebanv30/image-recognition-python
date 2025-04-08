import cv2
import numpy as np
from pyzbar.pyzbar import decode
from recognition.reconocimiento_marcadores import procesar_qr_con_marcadores

def leer_qr_desde_imagen(ruta_imagen):
    try:
        # Obtener la región de interés usando reconocimiento_marcadores
        roi_estandarizada = procesar_qr_con_marcadores(ruta_imagen, mostrar_resultados=False)

        if roi_estandarizada is None:
            print("No se pudo detectar la región del QR.")
            return None

        # Convertir a escala de grises
        gray = cv2.cvtColor(roi_estandarizada, cv2.COLOR_BGR2GRAY)

        # Aplicar umbral adaptativo para mejorar contraste del QR
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, 
                                     cv2.THRESH_BINARY, 11, 3)

        # Intentar decodificar con pyzbar
        decoded_objs = decode(thresh)
        if decoded_objs:
            for obj in decoded_objs:
                return obj.data.decode("utf-8")

        # Si falla pyzbar, intentar con OpenCV
        detector = cv2.QRCodeDetector()
        data, _, _ = detector.detectAndDecode(thresh)
        if data:
            return data

        return None

    except Exception as e:
        print(f"Error al procesar la imagen: {str(e)}")
        return None

if __name__ == "__main__":
    ruta_imagen = "C:/Users/valde/Desktop/image-recognition/assets/image.png"
    data = leer_qr_desde_imagen(ruta_imagen)
    if data:
        print(data)