import base64
import hashlib
import json
import logging
import os
import time
from pathlib import Path
from typing import Optional

from cryptography.fernet import Fernet

from .database_manager import obtener_conexion

DEFAULT_KEY_ENV = "SGTG_PDF_ENCRYPTION_KEY"
DEFAULT_LOG_PATH_ENV = "SGTG_SECURITY_LOG"


def _resolve_key(key: Optional[bytes | str] = None) -> bytes:
    if key is None:
        key = os.getenv(DEFAULT_KEY_ENV)
    if key is None:
        key = os.getenv("SECRET_KEY", "sistema-gestion-trabajo-grado")
    if isinstance(key, str):
        key_bytes = key.encode("utf-8")
    else:
        key_bytes = key
    if len(key_bytes) == 32:
        return base64.urlsafe_b64encode(key_bytes)
    digest = hashlib.sha256(key_bytes).digest()
    return base64.urlsafe_b64encode(digest)


def encrypt_bytes(data: bytes, key: Optional[bytes | str] = None) -> bytes:
    fernet = Fernet(_resolve_key(key))
    return fernet.encrypt(data)


def decrypt_bytes(data: bytes, key: Optional[bytes | str] = None) -> bytes:
    fernet = Fernet(_resolve_key(key))
    return fernet.decrypt(data)


def crear_token_acceso_archivo(ruta_archivo: str, usuario_id: Optional[int] = None, ttl_seconds: int = 900) -> str:
    payload = {
        "ruta": ruta_archivo,
        "usuario_id": usuario_id,
        "exp": int(time.time()) + ttl_seconds,
    }
    payload_json = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    token_bytes = Fernet(_resolve_key()).encrypt(payload_json)
    return base64.urlsafe_b64encode(token_bytes).decode("utf-8").rstrip("=")


def verificar_token_acceso_archivo(token: str, ruta_archivo: Optional[str] = None, usuario_id: Optional[int] = None) -> bool:
    if not token:
        return False
    try:
        padding = "=" * (-len(token) % 4)
        token_bytes = base64.urlsafe_b64decode(token.encode("utf-8") + padding.encode("utf-8"))
        payload_json = Fernet(_resolve_key()).decrypt(token_bytes)
        payload = json.loads(payload_json.decode("utf-8"))
        if int(payload.get("exp", 0)) < int(time.time()):
            return False
        if ruta_archivo and payload.get("ruta") != ruta_archivo:
            return False
        if usuario_id is not None and payload.get("usuario_id") is not None and payload.get("usuario_id") != usuario_id:
            return False
        return True
    except Exception:
        return False


def configurar_logging_seguridad(ruta: str | os.PathLike[str] | None = None) -> logging.Logger:
    ruta_log = Path(ruta or os.getenv(DEFAULT_LOG_PATH_ENV, "security.log")).expanduser()
    ruta_log.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("sgtg.security")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    for handler in list(logger.handlers):
        if isinstance(handler, logging.FileHandler) and Path(handler.baseFilename) == ruta_log.resolve():
            logger.removeHandler(handler)
            handler.close()

    handler = logging.FileHandler(ruta_log, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    return logger


def registrar_evento_seguridad(nivel: str, mensaje: str, ruta: str | None = None, usuario: str | None = None) -> None:
    logger = SECURITY_LOGGER
    logger.log(getattr(logging, nivel.upper(), logging.INFO), "%s", mensaje)

    conn = obtener_conexion()
    if conn is None:
        return
    try:
        with conn.transaction():
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO seguridad_evento (nivel, mensaje, ruta, usuario)
                    VALUES (%s, %s, %s, %s)
                    """,
                    (nivel.upper(), mensaje, ruta, usuario),
                )
    except Exception:
        logger.exception("No se pudo persistir el evento de seguridad en la base de datos")
    finally:
        try:
            conn.close()
        except Exception:
            pass


SECURITY_LOGGER = configurar_logging_seguridad()
