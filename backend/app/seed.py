"""Datos iniciales: roles, permisos, cuentas de demostración, celdas, titulares y movimientos de ejemplo."""
from datetime import timedelta
from . import repositories as repo, security
from .config import ahora

PERMISOS = [
    ("tablero.ver", "Ver tablero de ocupación", "Operación"),
    ("movimientos.registrar", "Registrar ingreso y salida", "Operación"),
    ("novedades.registrar", "Registrar novedades", "Operación"),
    ("vehiculos.consultar", "Consultar vehículos por placa", "Operación"),
    ("celdas.consultar", "Consultar celdas", "Celdas"),
    ("celdas.gestionar", "Crear, modificar e inactivar celdas", "Celdas"),
    ("celdas.configurar", "Configurar aforo máximo", "Celdas"),
    ("historial.consultar", "Consultar historial de auditoría", "Auditoría"),
    ("titulares.gestionar", "Gestionar titulares y vehículos", "Usuarios"),
    ("usuarios.administrar", "Administrar cuentas del personal", "Usuarios"),
    ("roles.administrar", "Asignar roles y permisos", "Usuarios"),
    ("pagos.registrar", "Registrar pagos", "Pagos"),
]
OPERARIO = {"tablero.ver", "movimientos.registrar", "novedades.registrar", "vehiculos.consultar", "celdas.consultar"}


def seed(conn):
    if repo._one(conn, "SELECT id FROM rol LIMIT 1"):
        return
    conn.execute("BEGIN")
    conn.execute("INSERT INTO rol(id,nombre,descripcion) VALUES (1,'ADMINISTRADOR','Control total de la sede'),(2,'OPERARIO','Operación diaria del parqueadero')")
    for cod, desc, mod in PERMISOS:
        repo.insertar(conn, "permiso", {"codigo": cod, "descripcion": desc, "modulo": mod})
    repo.asignar_permisos(conn, 1, [p[0] for p in PERMISOS])
    repo.asignar_permisos(conn, 2, sorted(OPERARIO))
    cuentas = [(101, "Héctor Niño", "80123456", "3001112233", "Admin2026*", 1),
               (102, "Laura Jaramillo", "1032987654", "3002223344", "Operario2026*", 2),
               (103, "Arley Franco", "52741963", "3003334455", "Operario2026*", 2)]
    for id_, nom, doc, tel, pw, rol in cuentas:
        repo.insertar(conn, "usuario", {"id": id_, "nombre": nom, "documento": doc, "telefono": tel,
                                        "password_hash": security.hash_password(pw), "rol_id": rol})
    repo.config_set(conn, "capacidad_carros", 70)
    repo.config_set(conn, "capacidad_motos", 10)
    for i in range(1, 71):
        repo.insertar(conn, "celda", {"codigo": f"C-{i:02d}", "categoria": "CARRO"})
    for i in range(1, 11):
        repo.insertar(conn, "celda", {"codigo": f"M-{i:02d}", "categoria": "MOTO"})
    hoy = ahora().date()
    vig_i, vig_f = (hoy - timedelta(days=10)).isoformat(), (hoy + timedelta(days=20)).isoformat()
    venc_i, venc_f = (hoy - timedelta(days=60)).isoformat(), (hoy - timedelta(days=5)).isoformat()
    titulares = [("Carlos Andrés", "Mendoza", "1020456789", "ACTIVO", [("ABC123", "CARRO", "Mazda 3", "Gris", 1)]),
                 ("Diana Marcela", "Torres", "52890123", "ACTIVO", [("MOT45G", "MOTO", "Yamaha", "Negro", 1)]),
                 ("Jorge Enrique", "Ramírez", "80456123", "ACTIVO", [("KLM890", "CARRO", "Renault Logan", "Blanco", 1)]),
                 ("Andrés Felipe", "Gómez", "1098765432", "ACTIVO", [("XYZ789", "CARRO", "Chevrolet Spark", "Rojo", 1),
                                                                      ("MOT88A", "MOTO", "Honda", "Azul", 1)]),
                 ("Roberto", "Gómez Bolaños", "79456123", "INACTIVO", [("INA404", "CARRO", "Kia Rio", "Plata", 1)]),
                 ("Sandra Milena", "Pérez", "51987654", "ACTIVO", [("VEN999", "CARRO", "Mazda 2", "Negro", 0)])]
    for nom, ape, doc, est, vehs in titulares:
        tid = repo.insertar(conn, "titular", {"nombres": nom, "apellidos": ape, "documento": doc, "estado": est})
        for placa, tipo, marca, color, vigente in vehs:
            vid = repo.insertar(conn, "vehiculo", {"placa": placa, "tipo": tipo, "marca": marca, "color": color, "titular_id": tid})
            ini, fin = (vig_i, vig_f) if vigente else (venc_i, venc_f)
            repo.insertar(conn, "mensualidad", {"vehiculo_id": vid, "fecha_inicio": ini, "fecha_fin": fin,
                                                "valor": 250000 if tipo == "CARRO" else 100000})
    d = hoy.isoformat()

    def mov(placa, celda, entrada, op, cierre=None, salida=None, oe=None, os_=None):
        v, c = repo.vehiculo_por_placa(conn, placa), repo.celda_por_codigo(conn, celda)
        repo.insertar(conn, "movimiento", {
            "vehiculo_id": v["id"], "celda_id": c["id"], "fecha_entrada": f"{d}T{entrada}", "operario_id": op,
            "operario_cierre_id": cierre, "fecha_salida": f"{d}T{salida}" if salida else None,
            "observacion_entrada": oe, "observacion_salida": os_, "estado": "CERRADO" if cierre else "ABIERTO"})
        if not cierre:
            conn.execute("UPDATE celda SET estado_ocupacion='OCUPADA' WHERE id=?", (c["id"],))
    mov("ABC123", "C-01", "07:45:12", 102, oe="Sin novedades")
    mov("MOT45G", "M-01", "08:15:40", 103, oe="Casco guardado en baúl")
    mov("KLM890", "C-02", "09:10:05", 101, oe="Sin observaciones")
    mov("XYZ789", "C-03", "06:50:11", 103, 101, "17:12:04", "Entrada: OK", "Entrega sin novedad")
    conn.execute("COMMIT")
