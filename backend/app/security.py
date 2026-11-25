import hashlib, hmac, os
from datetime import datetime, timedelta, timezone
import jwt
from .config import SECRET, TOKEN_HORAS, PBKDF2_ITER
from .errors import DomainError


def hash_password(password: str) -> str:  # RN-01
    salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, PBKDF2_ITER)
    return f"pbkdf2_sha256${PBKDF2_ITER}${salt.hex()}${h.hex()}"


def verificar(password: str, guardado: str) -> bool:
    try:
        _, it, salt, h = guardado.split("$")
        calc = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(it))
        return hmac.compare_digest(calc.hex(), h)
    except Exception:
        return False


def crear_token(usuario_id: int, rol: str) -> str:
    exp = datetime.now(timezone.utc) + timedelta(hours=TOKEN_HORAS)
    return jwt.encode({"sub": str(usuario_id), "rol": rol, "exp": exp}, SECRET, algorithm="HS256")


def leer_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise DomainError(401, "TOKEN_INVALIDO", "Sesión inválida o expirada")
