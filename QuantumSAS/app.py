from flask import Flask, jsonify
from flask_restful import Api, Resource, reqparse
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
api = Api(app)

# ── Swagger UI ────────────────────────────────────────────────────────────────
SWAGGER_URL  = "/docs"
API_URL      = "/static/swagger.json"
swagger_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL)
app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)

# ── Datos en memoria ──────────────────────────────────────────────────────────
clientes  = []
productos = []
pedidos   = []

# ── Parsers ───────────────────────────────────────────────────────────────────
cliente_parser = reqparse.RequestParser()
cliente_parser.add_argument("nombre", type=str, required=True, help="El nombre es obligatorio")
cliente_parser.add_argument("email",  type=str, required=True, help="El email es obligatorio")

producto_parser = reqparse.RequestParser()
producto_parser.add_argument("nombre", type=str,   required=True, help="El nombre es obligatorio")
producto_parser.add_argument("precio", type=float, required=True, help="El precio es obligatorio")
producto_parser.add_argument("stock",  type=int,   default=0)

pedido_parser = reqparse.RequestParser()
pedido_parser.add_argument("cliente_id",  type=int, required=True, help="El cliente_id es obligatorio")
pedido_parser.add_argument("producto_id", type=int, required=True, help="El producto_id es obligatorio")
pedido_parser.add_argument("cantidad",    type=int, default=1)

# ── Recursos ──────────────────────────────────────────────────────────────────
class HelloWorld(Resource):
    def get(self):
        return {
            "message": "Bienvenidos a la empresa QUANTUM SAS",
            "docs": "/docs",
            "endpoints": {
                "clientes":  "/clientes",
                "productos": "/productos",
                "pedidos":   "/pedidos",
            }
        }

class ClienteList(Resource):
    def get(self):
        return {"clientes": clientes, "total": len(clientes)}, 200
    def post(self):
        args = cliente_parser.parse_args()
        nuevo = {"id": len(clientes)+1, "nombre": args["nombre"], "email": args["email"]}
        clientes.append(nuevo)
        return nuevo, 201

class ClienteDetalle(Resource):
    def get(self, cliente_id):
        cliente = next((c for c in clientes if c["id"] == cliente_id), None)
        if not cliente:
            return {"error": f"Cliente {cliente_id} no encontrado"}, 404
        return cliente, 200
    def delete(self, cliente_id):
        global clientes
        original = len(clientes)
        clientes = [c for c in clientes if c["id"] != cliente_id]
        if len(clientes) == original:
            return {"error": f"Cliente {cliente_id} no encontrado"}, 404
        return {"message": f"Cliente {cliente_id} eliminado"}, 200

class ProductoList(Resource):
    def get(self):
        return {"productos": productos, "total": len(productos)}, 200
    def post(self):
        args = producto_parser.parse_args()
        nuevo = {"id": len(productos)+1, "nombre": args["nombre"], "precio": args["precio"], "stock": args["stock"]}
        productos.append(nuevo)
        return nuevo, 201

class ProductoDetalle(Resource):
    def get(self, producto_id):
        producto = next((p for p in productos if p["id"] == producto_id), None)
        if not producto:
            return {"error": f"Producto {producto_id} no encontrado"}, 404
        return producto, 200
    def delete(self, producto_id):
        global productos
        original = len(productos)
        productos = [p for p in productos if p["id"] != producto_id]
        if len(productos) == original:
            return {"error": f"Producto {producto_id} no encontrado"}, 404
        return {"message": f"Producto {producto_id} eliminado"}, 200

class PedidoList(Resource):
    def get(self):
        return {"pedidos": pedidos, "total": len(pedidos)}, 200
    def post(self):
        args = pedido_parser.parse_args()
        cliente = next((c for c in clientes if c["id"] == args["cliente_id"]), None)
        if not cliente:
            return {"error": f"Cliente {args['cliente_id']} no existe"}, 404
        producto = next((p for p in productos if p["id"] == args["producto_id"]), None)
        if not producto:
            return {"error": f"Producto {args['producto_id']} no existe"}, 404
        nuevo = {
            "id":          len(pedidos)+1,
            "cliente_id":  args["cliente_id"],
            "producto_id": args["producto_id"],
            "cantidad":    args["cantidad"],
            "total":       round(producto["precio"] * args["cantidad"], 2),
        }
        pedidos.append(nuevo)
        return nuevo, 201

class PedidoDetalle(Resource):
    def get(self, pedido_id):
        pedido = next((p for p in pedidos if p["id"] == pedido_id), None)
        if not pedido:
            return {"error": f"Pedido {pedido_id} no encontrado"}, 404
        return pedido, 200

# ── Rutas ─────────────────────────────────────────────────────────────────────
api.add_resource(HelloWorld,      "/")
api.add_resource(ClienteList,     "/clientes")
api.add_resource(ClienteDetalle,  "/clientes/<int:cliente_id>")
api.add_resource(ProductoList,    "/productos")
api.add_resource(ProductoDetalle, "/productos/<int:producto_id>")
api.add_resource(PedidoList,      "/pedidos")
api.add_resource(PedidoDetalle,   "/pedidos/<int:pedido_id>")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
