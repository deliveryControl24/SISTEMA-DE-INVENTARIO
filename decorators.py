from flask import request

def log_request_info():
    print(f"Request URL: {request.url}")
    print(f"Request Method: {request.method}")
    # Puedes agregar más lógica aquí si es necesario
