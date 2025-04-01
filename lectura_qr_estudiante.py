import cv2
import numpy as np
from pyzbar.pyzbar import decode
from reconocimiento_marcadores import procesar_imagen_con_marcadores, detectar_qr_con_marcadores

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
        # Procesar imagen usando los marcadores de referencia
        img = cv2.imread(ruta_imagen)
        if img is None:
            raise Exception("No se pudo cargar la imagen")

        plot_image(img, "0. Imagen original", False)

        # Detectar región del QR usando los marcadores
        region_qr = detectar_qr_con_marcadores(img)
        if region_qr is None:
            print("No se pudo detectar la región del QR.")
            return None
            
        x, y, w, h = region_qr
        qr_roi = img[y:y+h, x:x+w]
        plot_image(qr_roi, "5. Región del QR", False)

        # Decodificar QR
        codigos_qr = decode(qr_roi)
        
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
