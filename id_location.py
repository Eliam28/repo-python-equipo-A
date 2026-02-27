import xmlrpc.client
import json
import os
from dotenv import load_dotenv
load_dotenv()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

# Conexión common
common = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/common")
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_PASSWORD, {})

if not uid:
    raise Exception("Error de autenticación")

print(f"Autenticado con UID: {uid}")

models = xmlrpc.client.ServerProxy(f"{ODOO_URL}/xmlrpc/2/object")

locations = models.execute_kw(
  ODOO_DB, uid, ODOO_PASSWORD,
    "stock.location",
    "search_read",
    [[["usage", "=", "internal"]]],
    {"fields": ["id", "complete_name", "usage"]}
)

print("Ubicaciones internas encontradas:")
for loc in locations:
  print(loc)