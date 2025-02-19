from flask import Flask, render_template, request, redirect, url_for, flash, session, send_file, jsonify
import qrcode
import random
import string
import json
import os
import cv2
import numpy as np
from pyzbar.pyzbar import decode
from PIL import Image, ImageDraw, ImageFont
from werkzeug.utils import secure_filename
import re

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['QR_FOLDER'] = 'static/qrcodes'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Asegúrate de que las carpetas de subidas existan
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

if not os.path.exists(app.config['QR_FOLDER']):
    os.makedirs(app.config['QR_FOLDER'])

# Ruta del archivo JSON para almacenar el inventario y usuarios
INVENTORY_FILE = 'inventario.json'
USERS_FILE = 'usuarios.json'

# Cargar usuarios e inventario desde el archivo JSON
if os.path.exists(INVENTORY_FILE):
    with open(INVENTORY_FILE, 'r') as file:
        inventarios = json.load(file)
else:
    inventarios = {}

if os.path.exists(USERS_FILE):
    with open(USERS_FILE, 'r') as file:
        usuarios = json.load(file)
else:
    usuarios = {}

# Guardar el inventario en el archivo JSON
def save_inventory():
    with open(INVENTORY_FILE, 'w') as file:
        json.dump(inventarios, file)

# Guardar los usuarios en el archivo JSON
def save_users():
    with open(USERS_FILE, 'w') as file:
        json.dump(usuarios, file)

# Generar un código de 16 dígitos
def generate_unique_code():
    return ''.join(random.choices(string.digits, k=16))

# Ruta principal para mostrar el inventario
@app.route('/', methods=['GET'])
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    busqueda = request.args.get('busqueda')
    resultados = {}
    if busqueda:
        for nombre, inventario in inventarios.items():
            if busqueda.lower() in inventario.get('item_name', '').lower():
                inventario['image_url'] = url_for('static', filename=f'uploads/{nombre}')
                resultados[nombre] = inventario
    else:
        for nombre in inventarios:
            inventarios[nombre]['image_url'] = url_for('static', filename=f'uploads/{nombre}')
    return render_template('inventario.html', inventarios=resultados if busqueda else inventarios, usuarios=usuarios)

# Ruta para el login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        if user_id in usuarios:
            session['user_id'] = user_id
            flash('Login exitoso')
            return redirect(url_for('home'))
        else:
            flash('ID de usuario inválido')
    return render_template('login.html')

# Ruta para el registro
@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if len(usuarios) >= 10:
        flash('Se ha alcanzado el límite máximo de usuarios')
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = request.form['user_id']
        if len(user_id) != 4 or not user_id.isdigit():
            flash('El ID de usuario debe ser de 4 dígitos')
        elif user_id in usuarios:
            flash('El ID de usuario ya existe')
        else:
            usuarios[user_id] = {'id': user_id}
            save_users()
            flash('Registro exitoso')
            return redirect(url_for('login'))
    return render_template('registro.html')

# Ruta para subir imágenes
@app.route('/subir', methods=['GET', 'POST'])
def subir():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No se ha seleccionado ningún archivo')
            return redirect(url_for('subir'))
        file = request.files['file']
        if file.filename == '':
            flash('Nombre de archivo no válido')
            return redirect(url_for('subir'))
        if file:
            item_name = request.form['item_name']
            description = request.form['description']
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            unique_code = generate_unique_code()

            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(f'Item: {item_name}\nCode: {unique_code}\nDesc: {description}')
            qr.make(fit=True)
            img = qr.make_image(fill='black', back_color='white')

            draw = ImageDraw.Draw(img)
            font = ImageFont.load_default()
            text = f"Código: {unique_code}"
            textwidth, textheight = draw.textbbox((0, 0), text, font=font)[2:4]
            width, height = img.size
            x = (width - textwidth) / 2
            y = height + 10
            draw.text((x, y), text, font=font, fill='black')

            qr_filename = f"{os.path.splitext(filename)[0]}.jpg"
            qr_path = os.path.join(app.config['QR_FOLDER'], qr_filename)
            img.save(qr_path, format='JPEG')

            inventarios[filename] = {
                'file_path': file_path,
                'qr_path': qr_path,
                'item_name': item_name,
                'description': description,
                'unique_code': unique_code
            }
            save_inventory()

            flash('Imagen y código QR subidos exitosamente')
            return redirect(url_for('home'))
    return render_template('subir.html')

# Ruta para descargar el código QR
@app.route('/descargar_qr/<filename>')
def descargar_qr(filename):
    if filename in inventarios and 'qr_path' in inventarios[filename]:
        qr_path = inventarios[filename]['qr_path']
        return send_file(qr_path, as_attachment=True)
    flash('Código QR no encontrado')
    return redirect(url_for('home'))

# Ruta para imprimir códigos QR
@app.route('/imprimir_qr/<filename>')
def imprimir_qr(filename):
    if filename in inventarios and 'qr_path' in inventarios[filename]:
        qr_path = inventarios[filename]['qr_path']
        return send_file(qr_path)
    flash('Código QR no encontrado')
    return redirect(url_for('home'))

# Ruta para escanear códigos QR desde la cámara
@app.route('/escanear_qr_camara')
def escanear_qr_camara():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se puede abrir la cámara.")
        flash("Error: No se puede abrir la cámara.")
        return redirect(url_for('home'))
    else:
        print("Cámara abierta correctamente.")

    ret, frame = cap.read()
    if not ret:
        print("Error al leer el frame.")
        flash("Error al leer el frame.")
        cap.release()
        return redirect(url_for('home'))

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)

    decoded_objects = decode(img)
    for obj in decoded_objects:
        data = obj.data.decode('utf-8')
        unique_code_match = re.search(r'Code:\s*(\d{16})', data)
        if unique_code_match:
            unique_code = unique_code_match.group(1)
            for nombre, inventario in inventarios.items():
                if inventario.get('unique_code') == unique_code:
                    flash(f'Elemento encontrado: {inventario["item_name"]}')
                    return render_template('inventario.html', inventarios={nombre: inventario}, usuarios=usuarios)

    cap.release()
    flash('No se encontró ningún código QR o el elemento no está en el inventario.')
    return redirect(url_for('home'))

# Ruta para agregar elementos manualmente
@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        item_name = request.form['item_name']
        cantidad = request.form['cantidad']
        inventarios[item_name] = {'cantidad': cantidad}
        save_inventory()
        flash('Elemento agregado exitosamente')
        return redirect(url_for('home'))
    return render_template('agregar.html')

# Ruta para modificar un elemento
@app.route('/modificar/<item_name>', methods=['GET', 'POST'])
def modificar(item_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        nueva_cantidad = request.form['cantidad']
        inventarios[item_name]['cantidad'] = nueva_cantidad
        save_inventory()
        flash('Elemento modificado exitosamente')
        return redirect(url_for('home'))
    return render_template('modificar.html', item_name=item_name, cantidad=inventarios[item_name].get('cantidad', ''))

# Ruta para eliminar un elemento
@app.route('/eliminar/<item_name>', methods=['POST'])
def eliminar(item_name):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if item_name in inventarios:
        del inventarios[item_name]
        save_inventory()
        flash('Elemento eliminado exitosamente')
    else:
        flash('Elemento no encontrado')
    return redirect(url_for('home'))

# Ruta para cerrar sesión
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Sesión cerrada exitosamente')
    return redirect(url_for('login'))

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
