from flask_pymongo import ObjectId
from bson import json_util

def parse_json(data):
    return json_util.dumps(data, default=json_util.default)

class Inventario:
    def __init__(self, mongo):
        self.mongo = mongo

    def agregar_articulo(self, nombre, cantidad, qrCode):
        articulo = {
            'nombre': nombre,
            'cantidad': cantidad,
            'qrCode': qrCode
        }
        self.mongo.db.inventario.insert_one(articulo)
        return articulo

    def obtener_articulos(self):
        articulos = self.mongo.db.inventario.find()
        return parse_json(articulos)
