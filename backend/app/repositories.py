"""Capa de repositorios: único lugar donde vive el SQL (RNF-08)."""


def _all(c, sql, a=()):
    return [dict(r) for r in c.execute(sql, a).fetchall()]


def _one(c, sql, a=()):
    r = c.execute(sql, a).fetchone()
    return dict(r) if r else None


def insertar(c, tabla, datos):
    cols, ph = ",".join(datos), ",".join("?" * len(datos))
    return c.execute(f"INSERT INTO {tabla}({cols}) VALUES({ph})", tuple(datos.values())).lastrowid


def actualizar(c, tabla, id_, datos):
    if datos:
        sets = ",".join(f"{k}=?" for k in datos)
        c.execute(f"UPDATE {tabla} SET {sets} WHERE id=?", (*datos.values(), id_))


# ---------- roles y permisos ----------
def roles_listar(c):
    roles = _all(c, "SELECT * FROM rol ORDER BY id")
    for r in roles:
        r["permisos"] = permisos_de_rol(c, r["id"])
        r["usuarios"] = _one(c, "SELECT COUNT(*) n FROM usuario WHERE rol_id=?", (r["id"],))["n"]
    return roles


def rol_por_id(c, id_):
    return _one(c, "SELECT * FROM rol WHERE id=?", (id_,))


def permisos_listar(c):
    return _all(c, "SELECT * FROM permiso ORDER BY modulo, codigo")


def permisos_de_rol(c, rol_id):
    return [r["codigo"] for r in c.execute(
        "SELECT p.codigo FROM permiso p JOIN rol_permiso rp ON rp.permiso_id=p.id "
        "WHERE rp.rol_id=? ORDER BY p.codigo", (rol_id,))]


def asignar_permisos(c, rol_id, codigos):
    c.execute("DELETE FROM rol_permiso WHERE rol_id=?", (rol_id,))
    for cod in codigos:
        c.execute("INSERT INTO rol_permiso(rol_id,permiso_id) SELECT ?, id FROM permiso WHERE codigo=?", (rol_id, cod))


# ---------- cuentas de usuario (personal) ----------
_USR = ("SELECT u.id,u.nombre,u.documento,u.telefono,u.estado_cuenta,u.ultimo_acceso,u.rol_id,"
        "r.nombre AS rol FROM usuario u JOIN rol r ON r.id=u.rol_id")


def usuario_auth_por_documento(c, doc):
    return _one(c, "SELECT u.*, r.nombre AS rol FROM usuario u JOIN rol r ON r.id=u.rol_id WHERE u.documento=?", (doc,))


def usuario_por_id(c, id_):
    return _one(c, _USR + " WHERE u.id=?", (id_,))


def usuario_por_documento(c, doc):
    return _one(c, _USR + " WHERE u.documento=?", (doc,))


def usuarios_listar(c, estado=None, rol_id=None, q=None):
    sql, a = _USR + " WHERE 1=1", []
    if estado: sql += " AND u.estado_cuenta=?"; a.append(estado)
    if rol_id: sql += " AND u.rol_id=?"; a.append(rol_id)
    if q: sql += " AND (u.nombre LIKE ? OR u.documento LIKE ?)"; a += [f"%{q}%"] * 2
    return _all(c, sql + " ORDER BY u.nombre", a)


def contar_admins_activos(c):
    return _one(c, "SELECT COUNT(*) n FROM usuario u JOIN rol r ON r.id=u.rol_id "
                   "WHERE r.nombre='ADMINISTRADOR' AND u.estado_cuenta='ACTIVO'")["n"]


# ---------- titulares y vehículos ----------
def titular_por_id(c, id_):
    return _one(c, "SELECT * FROM titular WHERE id=?", (id_,))


def titular_por_documento(c, doc):
    return _one(c, "SELECT * FROM titular WHERE documento=?", (doc,))


def titulares_listar(c, estado=None, q=None):
    sql, a = "SELECT * FROM titular WHERE 1=1", []
    if estado: sql += " AND estado=?"; a.append(estado)
    if q: sql += " AND (nombres||' '||apellidos LIKE ? OR documento LIKE ?)"; a += [f"%{q}%"] * 2
    rows = _all(c, sql + " ORDER BY apellidos, nombres", a)
    for r in rows:
        r["vehiculos"] = _all(c, "SELECT id,placa,tipo,estado FROM vehiculo WHERE titular_id=?", (r["id"],))
    return rows


_VEH = ("SELECT v.*, t.estado AS titular_estado, t.nombres||' '||t.apellidos AS titular, t.documento AS titular_documento "
        "FROM vehiculo v JOIN titular t ON t.id=v.titular_id")


def vehiculo_por_placa(c, placa):
    return _one(c, _VEH + " WHERE v.placa=?", (placa,))


def vehiculo_por_id(c, id_):
    return _one(c, _VEH + " WHERE v.id=?", (id_,))


def vehiculos_listar(c, titular_id=None):
    if titular_id:
        return _all(c, _VEH + " WHERE v.titular_id=? ORDER BY v.placa", (titular_id,))
    return _all(c, _VEH + " ORDER BY v.placa")


def mensualidad_vigente(c, vehiculo_id, hoy):
    return _one(c, "SELECT * FROM mensualidad WHERE vehiculo_id=? AND fecha_inicio<=? AND fecha_fin>=? "
                   "ORDER BY fecha_fin DESC LIMIT 1", (vehiculo_id, hoy, hoy))


def mensualidades_de(c, vehiculo_id):
    return _all(c, "SELECT * FROM mensualidad WHERE vehiculo_id=? ORDER BY fecha_fin DESC", (vehiculo_id,))


# ---------- celdas y configuración ----------
def celda_por_id(c, id_):
    return _one(c, "SELECT * FROM celda WHERE id=?", (id_,))


def celda_por_codigo(c, codigo):
    return _one(c, "SELECT * FROM celda WHERE codigo=?", (codigo,))


def celdas_listar(c, categoria=None, estado=None, activa=None):
    sql, a = ("SELECT ce.*, v.placa FROM celda ce LEFT JOIN movimiento m ON m.celda_id=ce.id AND m.estado='ABIERTO' "
              "LEFT JOIN vehiculo v ON v.id=m.vehiculo_id WHERE 1=1"), []
    if categoria: sql += " AND ce.categoria=?"; a.append(categoria)
    if estado: sql += " AND ce.estado_ocupacion=?"; a.append(estado)
    if activa is not None: sql += " AND ce.activa=?"; a.append(1 if activa else 0)
    return _all(c, sql + " ORDER BY ce.categoria, ce.codigo", a)


def celda_libre(c, categoria):
    return _one(c, "SELECT * FROM celda WHERE categoria=? AND activa=1 AND estado_ocupacion='LIBRE' "
                   "ORDER BY codigo LIMIT 1", (categoria,))


def config_get(c, clave):
    r = _one(c, "SELECT valor FROM configuracion WHERE clave=?", (clave,))
    return r["valor"] if r else 0


def config_set(c, clave, valor):
    c.execute("INSERT INTO configuracion(clave,valor) VALUES(?,?) ON CONFLICT(clave) DO UPDATE SET valor=excluded.valor",
              (clave, valor))


# ---------- movimientos, novedades y pagos ----------
def contar_abiertos(c, categoria):
    return _one(c, "SELECT COUNT(*) n FROM movimiento m JOIN vehiculo v ON v.id=m.vehiculo_id "
                   "WHERE m.estado='ABIERTO' AND v.tipo=?", (categoria,))["n"]


def mov_abierto_por_vehiculo(c, vehiculo_id):
    return _one(c, "SELECT * FROM movimiento WHERE vehiculo_id=? AND estado='ABIERTO'", (vehiculo_id,))


_MOV = ("SELECT m.id, v.placa, v.tipo, ce.codigo AS celda, ce.id AS celda_id, m.fecha_entrada, m.fecha_salida, m.estado, "
        "m.operario_id, uo.nombre AS operario_ingreso, m.operario_cierre_id, uc.nombre AS operario_cierre, "
        "m.observacion_entrada, m.observacion_salida, t.nombres||' '||t.apellidos AS titular, "
        "(SELECT group_concat(n.descripcion,' | ') FROM novedad n WHERE n.movimiento_id=m.id) AS novedades "
        "FROM movimiento m JOIN vehiculo v ON v.id=m.vehiculo_id JOIN celda ce ON ce.id=m.celda_id "
        "JOIN usuario uo ON uo.id=m.operario_id LEFT JOIN usuario uc ON uc.id=m.operario_cierre_id "
        "JOIN titular t ON t.id=v.titular_id")


def mov_por_id(c, id_):
    return _one(c, _MOV + " WHERE m.id=?", (id_,))


def mov_abierto_por_placa(c, placa):
    return _one(c, _MOV + " WHERE v.placa=? AND m.estado='ABIERTO'", (placa,))


def mov_historial(c, placa=None, desde=None, hasta=None, estado=None, limite=500):
    sql, a = _MOV + " WHERE 1=1", []
    if placa: sql += " AND v.placa LIKE ?"; a.append(f"%{placa}%")
    if desde: sql += " AND date(m.fecha_entrada)>=?"; a.append(desde)
    if hasta: sql += " AND date(m.fecha_entrada)<=?"; a.append(hasta)
    if estado: sql += " AND m.estado=?"; a.append(estado)
    return _all(c, sql + " ORDER BY m.id DESC LIMIT ?", (*a, limite))


def mov_abiertos(c):
    return _all(c, _MOV + " WHERE m.estado='ABIERTO' ORDER BY m.fecha_entrada DESC")


def novedades_de(c, mov_id):
    return _all(c, "SELECT n.*, u.nombre AS usuario FROM novedad n JOIN usuario u ON u.id=n.usuario_id "
                   "WHERE movimiento_id=? ORDER BY n.id", (mov_id,))


def pagos_listar(c):
    return _all(c, "SELECT p.*, v.placa, u.nombre AS registrado_por FROM pago p JOIN movimiento m ON m.id=p.movimiento_id "
                   "JOIN vehiculo v ON v.id=m.vehiculo_id JOIN usuario u ON u.id=p.usuario_id ORDER BY p.id DESC")
