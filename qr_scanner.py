import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from utils import scan_qr

# Inicializar la cámara
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: No se puede abrir la cámara.")
else:
    print("Cámara abierta correctamente.")

# Función para actualizar la transmisión de la cámara
def update_frame():
    ret, frame = cap.read()
    if ret:
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(img)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        data = scan_qr(frame)
        if data:
            messagebox.showinfo("Código QR detectado", f"Datos: {data}")
    lmain.after(10, update_frame)

# Crear la ventana principal
root = tk.Tk()
root.title("Escáner de Códigos QR")

# Crear un label para mostrar la transmisión de la cámara
lmain = tk.Label(root)
lmain.pack()

# Iniciar la actualización de la transmisión de la cámara
update_frame()

# Ejecutar la aplicación
root.mainloop()

# Liberar la cámara al cerrar la aplicación
cap.release()
cv2.destroyAllWindows()
