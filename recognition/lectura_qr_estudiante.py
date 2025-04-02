import cv2
import numpy as np
from pyzbar.pyzbar import decode
from recognition.reconocimiento_marcadores import procesar_qr_con_marcadores

def plot_image(img, titulo="Imagen", grayscale=True):
    try:
        if grayscale and len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imshow(titulo, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error al mostrar la imagen: {str(e)}")

def leer_qr_desde_imagen(ruta_imagen):
    try:
        # Obtener la región de interés usando reconocimiento_marcadores
        roi_estandarizada = procesar_qr_con_marcadores(ruta_imagen, mostrar_resultados=False)

        if roi_estandarizada is None:
            print("No se pudo detectar la región del QR.")
            return None

        plot_image(roi_estandarizada, "Región del QR", False)

        # Decodificar QR
        codigos_qr = decode(roi_estandarizada)
        
        if not codigos_qr:
            print("No se encontró ningún código QR en la región detectada.")
            return None

        for qr in codigos_qr:
            data = qr.data.decode('utf-8')
            print("QR decodificado:", data)
            return data

        return None
    except Exception as e:
        print(f"Error al procesar la imagen: {str(e)}")
        return None

if __name__ == "__main__":
    ruta_imagen = "C:/Users/valde/Desktop/image-recognition/assets/image.png"
    leer_qr_desde_imagen(ruta_imagen)
