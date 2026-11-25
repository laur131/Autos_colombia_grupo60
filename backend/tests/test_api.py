"""Pruebas de extremo a extremo de la API (requieren fastapi + httpx). Ejecutar: pytest"""
import os, tempfile, unittest
os.environ["AUTOS_DB"] = os.path.join(tempfile.mkdtemp(), "test.db")
try:
    from fastapi.testclient import TestClient
    from app.main import app
except ImportError:  # entorno sin dependencias
    app = None


@unittest.skipIf(app is None, "fastapi no instalado")
class TestApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cm = TestClient(app)
        cls.client = cls.cm.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.cm.__exit__(None, None, None)

    def token(self, doc, pw):
        r = self.client.post("/api/v1/auth/login", json={"documento": doc, "password": pw})
        return {"Authorization": f"Bearer {r.json()['access_token']}"}

    def test_login_fallido_no_entrega_token(self):
        r = self.client.post("/api/v1/auth/login", json={"documento": "80123456", "password": "x"})
        self.assertEqual(r.status_code, 401)
        self.assertNotIn("access_token", r.text)

    def test_sin_token_401(self):
        self.assertEqual(self.client.get("/api/v1/celdas").status_code, 401)

    def test_operario_no_puede_funciones_de_admin(self):
        h = self.token("1032987654", "Operario2026*")
        self.assertEqual(self.client.get("/api/v1/celdas", headers=h).status_code, 200)
        self.assertEqual(self.client.post("/api/v1/celdas", json={"codigo": "X-1", "categoria": "CARRO"}, headers=h).status_code, 403)
        self.assertEqual(self.client.get("/api/v1/usuarios", headers=h).status_code, 403)
        self.assertEqual(self.client.put("/api/v1/celdas/configuracion", json={"capacidad_carros": 5, "capacidad_motos": 5}, headers=h).status_code, 403)

    def test_flujo_ingreso_salida(self):
        h = self.token("1032987654", "Operario2026*")
        r = self.client.post("/api/v1/movimientos/ingresos", json={"placa": "MOT88A"}, headers=h)
        self.assertEqual(r.status_code, 201)
        r = self.client.post("/api/v1/movimientos/ingresos", json={"placa": "MOT88A"}, headers=h)
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (409, "MOVIMIENTO_DUPLICADO"))
        r = self.client.post("/api/v1/movimientos/salidas", json={"placa": "MOT88A", "observacion": "OK"}, headers=h)
        self.assertEqual(r.json()["estado"], "CERRADO")

    def test_admin_aforo_409(self):
        h = self.token("80123456", "Admin2026*")
        r = self.client.put("/api/v1/celdas/configuracion", json={"capacidad_carros": 1, "capacidad_motos": 10}, headers=h)
        self.assertEqual((r.status_code, r.json()["detail"]["codigo"]), (409, "CAPACIDAD_MENOR_OCUPACION"))
