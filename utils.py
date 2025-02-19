import json
import re
from pyzbar.pyzbar import decode
from PIL import Image

# Función para guardar el resultado del escaneo en un archivo
def save_scan_result(data):
    with open('scan_result.json', 'w') as file:
        json.dump({'data': data}, file)

# Función para escanear códigos QR y guardar el resultado
def scan_qr(frame):
    decoded_objects = decode(frame)
    for obj in decoded_objects:
        data = obj.data.decode('utf-8')
        save_scan_result(data)  # Guardar el resultado en un archivo
        return data
    return None
