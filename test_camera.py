import cv2

# Intentar abrir la cámara
cap = cv2.VideoCapture(0)

# Verificar si la cámara se abrió correctamente
if not cap.isOpened():
    print("Error: No se puede abrir la cámara.")
else:
    print("Cámara abierta correctamente.")

    # Leer y mostrar frames de la cámara
    while True:
        ret, frame = cap.read()

        # Verificar si el frame se leyó correctamente
        if not ret:
            print("Error al leer el frame.")
            break

        # Mostrar el frame en una ventana
        cv2.imshow('Transmisión de la cámara', frame)

        # Romper el bucle si se presiona la tecla 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Liberar la cámara y cerrar la ventana
    cap.release()
    cv2.destroyAllWindows()
