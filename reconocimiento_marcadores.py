import cv2
import numpy as np

def plot_image(img, titulo="Imagen", grayscale=True):
    try:
        if grayscale and len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        cv2.imshow(titulo, img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except Exception as e:
        print(f"Error al mostrar la imagen: {str(e)}")

def cargar_imagen(ruta):
    try:
        img = cv2.imread(ruta)
        if img is None:
            raise Exception("No se pudo cargar la imagen")
        return img
    except Exception as e:
        print(f"Error al cargar la imagen: {str(e)}")
        return None

def detectar_marcadores(img):
    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Umbralización para detectar cuadrados negros
    _, thresh = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)
    
    # Encontrar contornos
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filtrar contornos cuadrados
    marcadores = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > 100:  # Filtrar ruido
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w)/h
            # Verificar si es aproximadamente cuadrado
            if 0.8 <= aspect_ratio <= 1.2:
                marcadores.append((x, y, w, h))
    
    # Separar marcadores izquierdos y derechos
    marcadores.sort(key=lambda x: x[0])  # Ordenar por coordenada x
    if len(marcadores) >= 6:  # Verificar que hay al menos 6 marcadores
        marcadores_izq = marcadores[:3]
        marcadores_der = marcadores[-3:]
        
        # Obtener límites de la región de interés
        x_min = min(m[0] + m[2] for m in marcadores_izq)
        x_max = max(m[0] for m in marcadores_der)
        y_min = min(min(m[1] for m in marcadores_izq), min(m[1] for m in marcadores_der))
        y_max = max(max(m[1] + m[3] for m in marcadores_izq), max(m[1] + m[3] for m in marcadores_der))
        
        return (x_min, y_min, x_max - x_min, y_max - y_min)
    
    return None

def procesar_imagen_con_marcadores(ruta_imagen, mostrar_resultados=True):
    img = cargar_imagen(ruta_imagen)
    
    if img is not None:
        # Detectar región entre marcadores
        region = detectar_marcadores(img)
        
        if region:
            x, y, w, h = region
            # Extraer región de interés
            roi = img[y:y+h, x:x+w]
            
            # Dimensiones estándar deseadas
            ancho_estandar = 800  # Ancho fijo deseado
            # Mantener la relación de aspecto
            relacion_aspecto = h / w
            alto_estandar = int(ancho_estandar * relacion_aspecto)
            
            # Redimensionar la región de interés a un tamaño estándar
            roi_estandarizada = cv2.resize(roi, (ancho_estandar, alto_estandar))
            
            if mostrar_resultados:
                # Mostrar resultados
                cv2.rectangle(img, (x,y), (x+w,y+h), (0,255,0), 2)
                plot_image(img, "Imagen con región detectada", False)
                plot_image(roi_estandarizada, "Región de interés estandarizada", False)
            
            return roi_estandarizada
        else:
            print("No se detectaron suficientes marcadores")
            return None
    else:
        print("Error: No se pudo cargar la imagen")
        return None

if __name__ == "__main__":
    # Ejemplo de uso
    ruta_imagen = "C:/Users/valde/Desktop/image-recognition/assets/examen-marcadores.jpg"
    procesar_imagen_con_marcadores(ruta_imagen)