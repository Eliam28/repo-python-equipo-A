import xmlrpc.client
import json
import os

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

def autenticar(url, db, username, password):
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common")
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise Exception("No se pudo autenticar.")
    return uid


def obtener_modelos(url):
    return xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object")


def construir_producto(producto):
    return {
        "name": producto["name"],
        "type": producto["type"],
        "list_price": float(producto["list_price"]),
        "default_code": producto["default_code"],
        "barcode": producto["barcode"],
        "categ_id": int(producto["categ_id"]),
    }


def cargar_productos(ruta):
    with open(ruta, encoding="utf-8") as f:
        return json.load(f)


def crear_productos(models, uid, productos):
    for producto in productos:
        try:
            product_data = construir_producto(producto)
            models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                "product.template",
                "create",
                [product_data]
            )
            print(f"Producto creado: {producto['name']}")
        except Exception as e:
            print(f"Error al crear {producto['name']}")


PRODUCTS_FILE = "productos.json"

uid = autenticar(ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD)
print(f"Autenticado como UID: {uid}")

models = obtener_modelos(ODOO_URL)
productos = cargar_productos(PRODUCTS_FILE)
crear_productos(models, uid, productos)

print("Todos los productos creados")