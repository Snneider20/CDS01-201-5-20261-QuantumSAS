"""
test_api.py – Pruebas unitarias para la API REST de QuantumSAS
Empresa ficticia: QUANTUM SAS – Tecnología y soluciones digitales
Ejecutar con:  pytest test_api.py -v
"""
import pytest
from app import app, clientes, productos, pedidos

# ── Datos ficticios QuantumSAS ────────────────────────────────────────────────
CLIENTES_FICTICIOS = [
    {"nombre": "Santiago Herrera Rios",   "email": "s.herrera@quantumsas.co"},
    {"nombre": "Valentina Ospina Casta",  "email": "v.ospina@quantumsas.co"},
    {"nombre": "Andres Felipe Mora",      "email": "a.mora@quantumsas.co"},
]

PRODUCTOS_FICTICIOS = [
    {"nombre": "Laptop Dell Inspiron 15",  "precio": 3200000.0, "stock": 15},
    {"nombre": "Monitor LG UltraWide 27",  "precio": 1450000.0, "stock": 30},
    {"nombre": "Teclado Mecanico Redragon","precio":  280000.0, "stock": 50},
]

# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture(autouse=True)
def limpiar_datos():
    clientes.clear()
    productos.clear()
    pedidos.clear()
    yield

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

@pytest.fixture
def base_datos(client):
    """Crea un cliente y un producto listos para pruebas de pedidos."""
    client.post("/clientes",  json=CLIENTES_FICTICIOS[0])
    client.post("/productos", json=PRODUCTOS_FICTICIOS[0])

# ── Endpoint raíz ─────────────────────────────────────────────────────────────
def test_raiz(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "QUANTUM SAS" in r.get_json()["message"]

# ── Clientes ──────────────────────────────────────────────────────────────────
def test_get_clientes_vacio(client):
    r = client.get("/clientes")
    assert r.status_code == 200
    assert r.get_json()["total"] == 0

def test_crear_cliente_santiago(client):
    r = client.post("/clientes", json=CLIENTES_FICTICIOS[0])
    assert r.status_code == 201
    data = r.get_json()
    assert data["nombre"] == "Santiago Herrera Rios"
    assert data["email"]  == "s.herrera@quantumsas.co"
    assert data["id"]     == 1

def test_crear_cliente_valentina(client):
    r = client.post("/clientes", json=CLIENTES_FICTICIOS[1])
    assert r.status_code == 201
    assert r.get_json()["nombre"] == "Valentina Ospina Casta"

def test_crear_cliente_sin_email(client):
    r = client.post("/clientes", json={"nombre": "Andres Felipe Mora"})
    assert r.status_code == 400

def test_get_cliente_por_id(client):
    client.post("/clientes", json=CLIENTES_FICTICIOS[2])
    r = client.get("/clientes/1")
    assert r.status_code == 200
    assert r.get_json()["nombre"] == "Andres Felipe Mora"

def test_get_cliente_no_existe(client):
    r = client.get("/clientes/99")
    assert r.status_code == 404

def test_eliminar_cliente(client):
    client.post("/clientes", json=CLIENTES_FICTICIOS[0])
    assert client.delete("/clientes/1").status_code == 200
    assert client.get("/clientes/1").status_code    == 404

def test_listar_tres_clientes(client):
    for c in CLIENTES_FICTICIOS:
        client.post("/clientes", json=c)
    r = client.get("/clientes")
    assert r.get_json()["total"] == 3

# ── Productos ─────────────────────────────────────────────────────────────────
def test_crear_producto_laptop(client):
    r = client.post("/productos", json=PRODUCTOS_FICTICIOS[0])
    assert r.status_code == 201
    data = r.get_json()
    assert data["nombre"] == "Laptop Dell Inspiron 15"
    assert data["precio"] == 3200000.0
    assert data["stock"]  == 15

def test_crear_producto_monitor(client):
    r = client.post("/productos", json=PRODUCTOS_FICTICIOS[1])
    assert r.status_code == 201
    assert r.get_json()["nombre"] == "Monitor LG UltraWide 27"

def test_crear_producto_sin_precio(client):
    r = client.post("/productos", json={"nombre": "Teclado sin precio"})
    assert r.status_code == 400

def test_get_producto_por_id(client):
    client.post("/productos", json=PRODUCTOS_FICTICIOS[2])
    r = client.get("/productos/1")
    assert r.status_code == 200
    assert r.get_json()["nombre"] == "Teclado Mecanico Redragon"

def test_get_producto_no_existe(client):
    r = client.get("/productos/999")
    assert r.status_code == 404

def test_eliminar_producto(client):
    client.post("/productos", json=PRODUCTOS_FICTICIOS[0])
    assert client.delete("/productos/1").status_code == 200
    assert client.get("/productos/1").status_code    == 404

def test_listar_tres_productos(client):
    for p in PRODUCTOS_FICTICIOS:
        client.post("/productos", json=p)
    r = client.get("/productos")
    assert r.get_json()["total"] == 3

# ── Pedidos ───────────────────────────────────────────────────────────────────
def test_crear_pedido_laptop(client, base_datos):
    r = client.post("/pedidos", json={"cliente_id": 1, "producto_id": 1, "cantidad": 2})
    assert r.status_code == 201
    data = r.get_json()
    assert data["cantidad"] == 2
    assert data["total"]    == 6400000.0

def test_crear_pedido_cantidad_default(client, base_datos):
    r = client.post("/pedidos", json={"cliente_id": 1, "producto_id": 1})
    assert r.status_code == 201
    assert r.get_json()["cantidad"] == 1
    assert r.get_json()["total"]    == 3200000.0

def test_pedido_cliente_inexistente(client):
    client.post("/productos", json=PRODUCTOS_FICTICIOS[1])
    r = client.post("/pedidos", json={"cliente_id": 99, "producto_id": 1})
    assert r.status_code == 404

def test_pedido_producto_inexistente(client):
    client.post("/clientes", json=CLIENTES_FICTICIOS[0])
    r = client.post("/pedidos", json={"cliente_id": 1, "producto_id": 99})
    assert r.status_code == 404

def test_get_pedido_por_id(client, base_datos):
    client.post("/pedidos", json={"cliente_id": 1, "producto_id": 1, "cantidad": 3})
    r = client.get("/pedidos/1")
    assert r.status_code == 200
    assert r.get_json()["total"] == 9600000.0

def test_get_pedido_no_existe(client):
    r = client.get("/pedidos/50")
    assert r.status_code == 404

def test_listar_pedidos(client, base_datos):
    client.post("/pedidos", json={"cliente_id": 1, "producto_id": 1, "cantidad": 1})
    client.post("/pedidos", json={"cliente_id": 1, "producto_id": 1, "cantidad": 2})
    r = client.get("/pedidos")
    assert r.get_json()["total"] == 2