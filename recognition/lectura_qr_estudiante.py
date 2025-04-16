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

        # Probar con diferentes factores de escala
        factores_escala = [0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9, 2.0, 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8, 2.9, 3.0, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 4.0]
        for factor in factores_escala:
            roi_redimensionada = cv2.resize(roi_estandarizada, None, fx=factor, fy=factor, interpolation=cv2.INTER_CUBIC)

            # INTENTO 1: Decodificación con pyzbar
            decoded_objs = decode(roi_redimensionada)
            if decoded_objs:
                for obj in decoded_objs:
                    return obj.data.decode("utf-8")

            # INTENTO 2: Decodificación con QRCodeDetector
            detector = cv2.QRCodeDetector()
            data, _, _ = detector.detectAndDecode(roi_redimensionada)
            if data:
                return data

            # INTENTO 3: Binarización y decodificación
            gray = cv2.cvtColor(roi_redimensionada, cv2.COLOR_BGR2GRAY)
            gray = cv2.equalizeHist(gray)
            _, binarizada = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            decoded_objs = decode(binarizada)
            if decoded_objs:
                for obj in decoded_objs:
                    return obj.data.decode("utf-8")

        print("No se pudo decodificar el código QR.")
        return None

    except Exception as e:
        print(f"Error al procesar la imagen: {str(e)}")
        return None


if __name__ == "__main__":
    ruta_imagen = "C:/Users/valde/Desktop/image-recognition/assets/image.png"
    data = leer_qr_desde_imagen(ruta_imagen)
    if data:
        print("Contenido del QR:", data)
    else:
        print("No se extrajo información del QR.")
