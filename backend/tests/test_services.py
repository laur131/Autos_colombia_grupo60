"""Pruebas de la lógica de negocio (sin servidor). Ejecutar:  python -m unittest -v   o   pytest"""
import sqlite3, unittest
from app import repositories as repo
from app.db import connect, init_db
from app.errors import DomainError
from app.seed import seed
from app.services import auth, celdas, movimientos as mov, pagos, titulares, usuarios


class Base(unittest.TestCase):
    def setUp(self):
        self.c = connect(":memory:")
        init_db(self.c)
        seed(self.c)
        self.op, self.admin = 102, 101

    def err(self, codigo, fn, *a, **k):
        with self.assertRaises(DomainError) as cm:
            fn(*a, **k)
        self.assertEqual(cm.exception.codigo, codigo)
        return cm.exception


class TestAuth(Base):  # CP: RF-23, RN-01
    def test_login_ok_y_permisos_por_rol(self):
        r = auth.login(self.c, "80123456", "Admin2026*")
        self.assertIn("access_token", r)
        self.assertIn("celdas.gestionar", r["permisos"])
        r2 = auth.login(self.c, "1032987654", "Operario2026*")
        self.assertNotIn("celdas.gestionar", r2["permisos"])
        self.assertNotIn("usuarios.administrar", r2["permisos"])

    def test_password_no_en_texto_plano(self):
        h = repo.usuario_auth_por_documento(self.c, "80123456")["password_hash"]
        self.assertNotIn("Admin2026*", h)
        self.assertTrue(h.startswith("pbkdf2_sha256$"))

    def test_credenciales_incorrectas_y_bloqueo_a_los_5_intentos(self):
        for _ in range(5):
            self.err("CREDENCIALES_INVALIDAS", auth.login, self.c, "52741963", "mala")
        self.err("CUENTA_BLOQUEADA", auth.login, self.c, "52741963", "Operario2026*")

    def test_cuenta_inactiva_se_deniega_sin_token(self):
        usuarios.cambiar_estado(self.c, 103, "INACTIVO", self.admin)
        self.err("CUENTA_INACTIVA", auth.login, self.c, "52741963", "Operario2026*")


class TestUsuarios(Base):  # RF-16, RF-24, RF-25, RN-02
    def test_crear_actualizar_inactivar_reactivar(self):
        u = usuarios.crear(self.c, {"nombre": "Nuevo Operario", "documento": "99887766", "password": "Clave2026*", "rol_id": 2})
        self.assertEqual(u["rol"], "OPERARIO")
        self.err("DOCUMENTO_DUPLICADO", usuarios.crear, self.c,
                 {"nombre": "Otro", "documento": "99887766", "password": "Clave2026*", "rol_id": 2})
        usuarios.actualizar(self.c, u["id"], {"nombre": "Nombre Nuevo"}, self.admin)
        self.assertEqual(usuarios.cambiar_estado(self.c, u["id"], "INACTIVO", self.admin)["estado_cuenta"], "INACTIVO")
        self.assertEqual(usuarios.cambiar_estado(self.c, u["id"], "ACTIVO", self.admin)["estado_cuenta"], "ACTIVO")

    def test_no_autoinactivar_ni_dejar_sin_admin(self):
        self.err("AUTO_INACTIVACION", usuarios.cambiar_estado, self.c, 101, "INACTIVO", 101)
        self.err("ULTIMO_ADMIN", usuarios.cambiar_estado, self.c, 101, "INACTIVO", 102)

    def test_asignar_permisos(self):
        r = usuarios.asignar_permisos(self.c, 2, ["tablero.ver", "celdas.consultar"])
        self.assertEqual(sorted(r["permisos"]), ["celdas.consultar", "tablero.ver"])
        self.err("PERMISO_DESCONOCIDO", usuarios.asignar_permisos, self.c, 2, ["inventado"])
        self.err("ADMIN_SIN_ACCESO", usuarios.asignar_permisos, self.c, 1, ["tablero.ver"])


class TestTitularesVehiculos(Base):  # RF-15, RF-18, RF-19, HU-06, HU-08
    def test_documento_unico_y_baja_logica(self):
        self.err("DOCUMENTO_DUPLICADO", titulares.crear_titular, self.c,
                 {"nombres": "X", "apellidos": "Y", "documento": "1020456789"})
        t = titulares.cambiar_estado_titular(self.c, 1, "INACTIVO")
        self.assertEqual(t["estado"], "INACTIVO")
        self.err("TITULAR_INACTIVO", titulares.crear_vehiculo, self.c,
                 {"placa": "AAA111", "tipo": "CARRO", "titular_id": 1})

    def test_vehiculo_fk_y_formato_placa(self):
        t = titulares.crear_titular(self.c, {"nombres": "Ana", "apellidos": "Ruiz", "documento": "11223344"})
        v = titulares.crear_vehiculo(self.c, {"placa": "aaa-111", "tipo": "CARRO", "titular_id": t["id"]})
        self.assertEqual(v["placa"], "AAA111")
        self.err("PLACA_INVALIDA", titulares.crear_vehiculo, self.c, {"placa": "AAA111", "tipo": "MOTO", "titular_id": t["id"]})
        self.err("PLACA_DUPLICADA", titulares.crear_vehiculo, self.c, {"placa": "AAA111", "tipo": "CARRO", "titular_id": t["id"]})
        with self.assertRaises(sqlite3.IntegrityError):  # PRAGMA foreign_keys = ON (RNF-05)
            self.c.execute("INSERT INTO vehiculo(placa,tipo,titular_id) VALUES('ZZZ999','CARRO',9999)")


class TestIngresoSalida(Base):  # HU-01, HU-02, RF-01..09, RN-06
    def test_ingreso_ok_asigna_celda_y_salida_la_libera(self):
        m = mov.registrar_ingreso(self.c, "xyz789", "Sin novedades", self.op)
        self.assertEqual(m["estado"], "ABIERTO")
        self.assertEqual(m["operario_id"], self.op)
        self.assertEqual(repo.celda_por_id(self.c, m["celda_id"])["estado_ocupacion"], "OCUPADA")
        self.err("OBSERVACION_REQUERIDA", mov.registrar_salida, self.c, "XYZ789", "  ", 101)
        s = mov.registrar_salida(self.c, "XYZ789", "Entrega conforme", 101)
        self.assertEqual((s["estado"], s["operario_cierre_id"], s["operario_id"]), ("CERRADO", 101, self.op))
        self.assertEqual(repo.celda_por_id(self.c, m["celda_id"])["estado_ocupacion"], "LIBRE")

    def test_rechazos(self):
        self.err("TITULAR_INACTIVO", mov.registrar_ingreso, self.c, "INA404", None, self.op)
        self.err("MENSUALIDAD_VENCIDA", mov.registrar_ingreso, self.c, "VEN999", None, self.op)
        self.err("MOVIMIENTO_DUPLICADO", mov.registrar_ingreso, self.c, "ABC123", None, self.op)
        self.err("VEHICULO_NO_ENCONTRADO", mov.registrar_ingreso, self.c, "QQQ000", None, self.op)
        self.err("SIN_ENTRADA_ABIERTA", mov.registrar_salida, self.c, "XYZ789", "ok", self.op)

    def test_sobrecupo_y_sin_celda(self):
        celdas.configurar_capacidad(self.c, 2, 10)  # ya hay 2 carros adentro
        self.err("SOBRECUPO", mov.registrar_ingreso, self.c, "XYZ789", None, self.op)
        celdas.configurar_capacidad(self.c, 70, 10)
        for cel in repo.celdas_listar(self.c, categoria="CARRO", estado="LIBRE"):
            celdas.cambiar_estado(self.c, cel["id"], "BLOQUEADA")
        self.err("SIN_CELDA_DISPONIBLE", mov.registrar_ingreso, self.c, "XYZ789", None, self.op)

    def test_celda_bloqueada_o_inactiva_no_se_asigna(self):
        for cod in ("C-03", "C-04"):
            celdas.cambiar_estado(self.c, repo.celda_por_codigo(self.c, cod)["id"], "BLOQUEADA")
        celdas.cambiar_activa(self.c, repo.celda_por_codigo(self.c, "C-05")["id"], False)
        m = mov.registrar_ingreso(self.c, "XYZ789", None, self.op)
        self.assertEqual(m["celda"], "C-06")

    def test_ocupacion_y_historial_con_doble_operario(self):
        o = mov.ocupacion(self.c)
        self.assertEqual((o["carros"]["ocupados"], o["carros"]["capacidad"], o["motos"]["ocupados"]), (2, 70, 1))
        h = mov.historial(self.c, estado="CERRADO")
        self.assertEqual(h[0]["operario_ingreso"], "Arley Franco")
        self.assertEqual(h[0]["operario_cierre"], "Héctor Niño")
        self.assertEqual(len(mov.historial(self.c, placa="ABC")), 1)

    def test_novedades(self):
        m = mov.registrar_ingreso(self.c, "XYZ789", None, self.op)
        mov.agregar_novedad(self.c, m["id"], "Rayón puerta izquierda", self.op)
        self.assertIn("Rayón", mov.historial(self.c, placa="XYZ789")[0]["novedades"])

    def test_auditoria_inmutable_rnf01(self):
        with self.assertRaises(sqlite3.DatabaseError):
            self.c.execute("UPDATE movimiento SET operario_id=103 WHERE id=1")
        with self.assertRaises(sqlite3.DatabaseError):
            self.c.execute("DELETE FROM movimiento WHERE id=1")
        with self.assertRaises(sqlite3.DatabaseError):
            self.c.execute("UPDATE movimiento SET operario_cierre_id=102 WHERE estado='CERRADO'")

    def test_indice_unico_parcial_evita_duplicados(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.c.execute("INSERT INTO movimiento(vehiculo_id,celda_id,fecha_entrada,operario_id) "
                           "SELECT vehiculo_id,70,'2026-01-01T00:00:00',101 FROM movimiento WHERE id=1")


class TestCeldas(Base):  # RF-22, RF-26..28, RN-04, RN-05
    def test_codigo_unico(self):
        self.err("CODIGO_DUPLICADO", celdas.crear, self.c, {"codigo": "c-01", "categoria": "CARRO"})
        c = celdas.crear(self.c, {"codigo": "c-71", "categoria": "CARRO"})
        self.assertEqual((c["codigo"], c["estado_ocupacion"], c["activa"]), ("C-71", "LIBRE", 1))

    def test_no_inactivar_ni_modificar_celda_ocupada(self):
        ocupada = repo.celda_por_codigo(self.c, "C-01")
        self.err("CELDA_OCUPADA", celdas.cambiar_activa, self.c, ocupada["id"], False)
        self.err("CELDA_OCUPADA", celdas.actualizar, self.c, ocupada["id"], {"codigo": "Z-99"})
        self.err("CELDA_OCUPADA", celdas.cambiar_estado, self.c, ocupada["id"], "BLOQUEADA")

    def test_inactivar_reactivar_libre_conserva_registro(self):
        libre = repo.celda_por_codigo(self.c, "C-10")
        self.assertEqual(celdas.cambiar_activa(self.c, libre["id"], False)["activa"], 0)
        self.assertEqual(celdas.cambiar_activa(self.c, libre["id"], True)["activa"], 1)

    def test_aforo_no_puede_bajar_de_la_ocupacion(self):
        e = self.err("CAPACIDAD_MENOR_OCUPACION", celdas.configurar_capacidad, self.c, 1, 10)
        self.assertEqual(e.status, 409)
        self.assertEqual(celdas.obtener_capacidad(self.c), {"capacidad_carros": 70, "capacidad_motos": 10})
        self.assertEqual(celdas.configurar_capacidad(self.c, 60, 5)["capacidad_carros"], 60)


class TestPagos(Base):
    def test_un_pago_por_movimiento(self):
        p = pagos.registrar(self.c, 4, 12000, self.admin)
        self.assertEqual(p["valor"], 12000)
        self.err("PAGO_DUPLICADO", pagos.registrar, self.c, 4, 5000, self.admin)
        self.err("MOVIMIENTO_NO_ENCONTRADO", pagos.registrar, self.c, 999, 5000, self.admin)


if __name__ == "__main__":
    unittest.main()
