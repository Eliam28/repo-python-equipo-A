import xmlrpc.client
import json
import os
from dotenv import load_dotenv
load_dotenv()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

def autenticar(url, db, username, password):
    common = xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/common", allow_none=True)
    uid = common.authenticate(db, username, password, {})
    if not uid:
        raise Exception("No se pudo autenticar.")
    return uid


def obtener_modelos(url):
    return xmlrpc.client.ServerProxy(f"{url}/xmlrpc/2/object", allow_none=True)


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
            
            existing_product = models.execute_kw(
                ODOO_DB,uid,ODOO_PASSWORD,
                "product.template",
                "search",
                [[["default_code", "=",product_data["default_code"]]]]
            )

            if existing_product:
                print(f"Producto existente: {product_data['name']}")
                continue
            
            product_id = models.execute_kw(
                ODOO_DB, uid, ODOO_PASSWORD,
                "product.template",
                "create",
                [product_data]
            )
            print(f"Producto creado: {producto['name']}")

            product_variant = models.execute_kw(
                ODOO_DB,uid,ODOO_PASSWORD,
                "product.product",
                "search",
                [[["product_tmpl_id", "=", product_id]]]
            )

            if not product_variant:
                print("No se encontro variante")
                continue

            variant_id = product_variant[0]

            cantidad = producto.get("qty_available", 0)

            if cantidad >0 and product_data["type"] == "product":
                location_id = 16

                quant_id = models.execute_kw(
                    ODOO_DB,uid,ODOO_PASSWORD,
                    "stock.quant",
                    "create",
                    [{
                        "product_id": variant_id,
                        "location_id": location_id,
                        "inventory_quantity": cantidad
                    }]
                )

                print(f"Stock agregado: {cantidad}")

                try:
                    models.execute_kw(
                    ODOO_DB,uid,ODOO_PASSWORD,
                    "stock.quant",
                    "action_apply_inventory",
                    [[quant_id]]
                    )
                except Exception as stock_error:
                    if "cannot marshal None" in str(stock_error):
                        pass
                    else:
                        raise

        except Exception as e:
            print(f"Error al crear {producto['name']}: {e}")


PRODUCTS_FILE = "productos_2.json"

uid = autenticar(ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD)
print(f"Autenticado como UID: {uid}")

models = obtener_modelos(ODOO_URL)
productos = cargar_productos(PRODUCTS_FILE)
crear_productos(models, uid, productos)

print("Todos los productos creados")