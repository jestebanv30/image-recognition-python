import cv2
from pyzbar.pyzbar import decode
from reconocimiento_marcadores import procesar_codigo_barras_con_marcadores

def plot_image(img, titulo="Imagen", grayscale=True):
    try:
        if grayscale and len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imshow(titulo, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error al mostrar la imagen: {str(e)}")

def leer_barcode_dual(ruta_imagen):
    try:
        roi_estandarizada = procesar_codigo_barras_con_marcadores(ruta_imagen, mostrar_resultados=False)

        if roi_estandarizada is None:
            print("No se pudo detectar la región del código de barras.")
            return None

        plot_image(roi_estandarizada, "Región del código de barras", False)

        # Convertir a escala de grises para mejorar detección
        gray = cv2.cvtColor(roi_estandarizada, cv2.COLOR_BGR2GRAY)
        
        # Aplicar umbralización adaptativa
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                     cv2.THRESH_BINARY, 11, 2)

        # === PRIMER INTENTO: PYZBAR con imagen procesada ===
        decoded_objs = decode(thresh)
        if decoded_objs:
            data = decoded_objs[0].data.decode('utf-8')
            print("Código de barras decodificado con pyzbar:", data)
            return data
        else:
            print("pyzbar no detectó nada, intentando con imagen original...")
            # Intentar con imagen original
            decoded_objs = decode(roi_estandarizada)
            if decoded_objs:
                data = decoded_objs[0].data.decode('utf-8')
                print("Código de barras decodificado con pyzbar (imagen original):", data)
                return data
            print("pyzbar no detectó nada, probando con OpenCV...")

        # === SEGUNDO INTENTO: OpenCV ===
        detector = cv2.barcode_BarcodeDetector()
        try:
            ok, decoded_info, _, _ = detector.detectAndDecode(thresh)
        except ValueError:
            ok, decoded_info, _ = detector.detectAndDecode(thresh)

        if ok and decoded_info:
            print("✅ Código de barras decodificado con OpenCV:", decoded_info[0])
            return decoded_info[0]
        else:
            print("❌ No se pudo decodificar el código de barras con OpenCV tampoco.")
            return None

    except Exception as e:
        print(f"Error al procesar la imagen: {str(e)}")
        return None

if __name__ == "__main__":
    ruta_imagen = "C:/Users/valde/Desktop/image-recognition/assets/image.png"
    leer_barcode_dual(ruta_imagen)
