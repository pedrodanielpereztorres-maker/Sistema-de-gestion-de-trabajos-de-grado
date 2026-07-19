import logging
from typing import Any

import reflex as rx
from sqlalchemy import create_engine

logger = logging.getLogger(__name__)


ESQUEMA_SQL = """
CREATE TABLE IF NOT EXISTS permiso (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS carrera (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    esta_activa BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS rol (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion TEXT,
    esta_activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS empresa (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    direccion TEXT,
    correo VARCHAR(150),
    telefono VARCHAR(20),
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS rol_permiso (
    rol_id INTEGER REFERENCES rol(id) ON DELETE CASCADE,
    permiso_id INTEGER REFERENCES permiso(id) ON DELETE CASCADE,
    PRIMARY KEY (rol_id, permiso_id)
);

CREATE TABLE IF NOT EXISTS usuario (
    id SERIAL PRIMARY KEY,
    cedula VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    correo VARCHAR(150) UNIQUE NOT NULL,
    contrasena_hash TEXT NOT NULL,
    rol_id INTEGER REFERENCES rol(id),
    esta_activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS tutor_empresarial (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(150) UNIQUE,
    telefono VARCHAR(20),
    empresa_id INTEGER REFERENCES empresa(id)
);

CREATE TABLE IF NOT EXISTS tutor_academico (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE REFERENCES usuario(id),
    cedula VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    correo VARCHAR(150),
    telefono VARCHAR(20),
    carrera_id INTEGER REFERENCES carrera(id),
    especialidad VARCHAR(150),
    esta_activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS estudiante (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER UNIQUE REFERENCES usuario(id),
    cedula VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    carrera_id INTEGER REFERENCES carrera(id),
    tutor_academico_id INTEGER REFERENCES tutor_academico(id),
    tutor_empresarial_id INTEGER REFERENCES tutor_empresarial(id),
    periodo_inicio DATE,
    periodo_cierre DATE,
    celular VARCHAR(20),
    esta_activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS trabajo_de_grado (
    id SERIAL PRIMARY KEY,
    titulo TEXT NOT NULL,
    fecha_registro DATE DEFAULT CURRENT_DATE,
    es_publica BOOLEAN DEFAULT FALSE,
    ruta_archivo TEXT,
    estudiante_id INTEGER UNIQUE REFERENCES estudiante(id)
);

CREATE TABLE IF NOT EXISTS documento (
    id SERIAL PRIMARY KEY,
    trabajo_de_grado_id INTEGER REFERENCES trabajo_de_grado(id) ON DELETE CASCADE,
    titulo VARCHAR(255) NOT NULL,
    descripcion TEXT,
    fecha_subida DATE DEFAULT CURRENT_DATE,
    tipo VARCHAR(50),
    tamano_kb INTEGER,
    ruta_archivo TEXT
);

CREATE TABLE IF NOT EXISTS sesion (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER REFERENCES usuario(id),
    token TEXT UNIQUE NOT NULL,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expira_en TIMESTAMP NOT NULL,
    esta_activa BOOLEAN DEFAULT TRUE
);

-- Índices recomendados para consultas frecuentes
CREATE INDEX IF NOT EXISTS idx_usuario_correo ON usuario(LOWER(correo));
CREATE INDEX IF NOT EXISTS idx_usuario_cedula ON usuario(cedula);
CREATE INDEX IF NOT EXISTS idx_estudiante_cedula ON estudiante(cedula);
CREATE INDEX IF NOT EXISTS idx_estudiante_carrera ON estudiante(carrera_id);
CREATE INDEX IF NOT EXISTS idx_estudiante_activo ON estudiante(esta_activo);
CREATE INDEX IF NOT EXISTS idx_trabajo_de_grado_estudiante ON trabajo_de_grado(estudiante_id);
CREATE INDEX IF NOT EXISTS idx_sesion_token ON sesion(token);
CREATE INDEX IF NOT EXISTS idx_sesion_activa ON sesion(esta_activa, expira_en);
"""

# Creamos el motor de forma global para reutilizar el pool de conexiones.
# Esto mejora drásticamente el rendimiento y evita errores de "Too many clients".
_motor = None


class ConnectionProxy:
    """Proxy para que los objetos de raw_connection sean usados como context managers."""

    def __init__(self, conn: Any):
        self._conn = getattr(conn, "connection", conn)
        self._closed = False

    def __enter__(self):
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is None:
                self._conn.commit()
            else:
                self._conn.rollback()
        except Exception:
            pass
        finally:
            try:
                self._conn.close()
            except Exception:
                pass
            self._closed = True
        return False

    def transaction(self):
        """Context manager explícito con BEGIN/COMMIT/ROLLBACK."""
        return _TransactionContext(self)

    def cursor(self, *args, **kwargs):
        return self._conn.cursor(*args, **kwargs)

    def commit(self):
        return self._conn.commit()

    def rollback(self):
        return self._conn.rollback()

    def close(self):
        if self._closed:
            return
        try:
            self._conn.close()
        except Exception:
            pass
        self._closed = True

    def __getattr__(self, name: str):
        return getattr(self._conn, name)


class _TransactionContext:
    def __init__(self, proxy: ConnectionProxy):
        self._proxy = proxy
        self._conn = getattr(proxy, "_conn", proxy)

    def __enter__(self):
        self._conn.begin()
        return self._conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self._conn.commit()
        else:
            self._conn.rollback()
        return False


def obtener_conexion() -> Any:
    """
    Establece y retorna una conexión a la base de datos PostgreSQL.
    Retorna la conexión cruda compatible con el uso de cursores.
    """
    global _motor
    if _motor is None:
        configuracion = rx.config.get_config()
        if not configuracion.db_url:
            return None
        _motor = create_engine(
            configuracion.db_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=10,
            max_overflow=20,
        )
    try:
        raw_conn = _motor.raw_connection()
        driver_conn = getattr(raw_conn, "driver_connection", None)
        if driver_conn is not None:
            raw_conn = driver_conn
        else:
            raw_conn = getattr(raw_conn, "connection", raw_conn)
        return ConnectionProxy(raw_conn)
    except Exception as e:
        logger.critical(
            "--- ERROR CRÍTICO DE CONEXIÓN A POSTGRES --- %s", e, exc_info=True
        )
        return None


def inicializar_infraestructura() -> None:
    """Crea la estructura de la base de datos si no existe."""
    conexion = obtener_conexion()
    if conexion is None:
        logger.critical("No se pudo establecer la conexión para crear las tablas.")
        return
    try:
        with conexion:
            with conexion.cursor() as cursor:
                cursor.execute(ESQUEMA_SQL)
            conexion.commit()
        logger.info(
            "Éxito: infraestructura verificada en %s",
            rx.config.get_config().db_url.split("@")[-1],
        )
    except Exception as e:
        logger.error("Error al inicializar las tablas: %s", e, exc_info=True)
    finally:
        if conexion:
            conexion.close()
