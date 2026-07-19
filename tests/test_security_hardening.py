import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from cryptography.fernet import InvalidToken

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sistema_gestion_trabajo_grado.database_manager import ConnectionProxy  # noqa: E402
from sistema_gestion_trabajo_grado.estado.estado_autenticacion import (  # noqa: E402
    COOKIE_MAX_AGE_SECONDS,
    SESSION_TTL_HOURS,
    EstadoAutenticacion,
)
from sistema_gestion_trabajo_grado import sistema_gestion_trabajo_grado as app_module  # noqa: E402
from sistema_gestion_trabajo_grado.seguridad import (  # noqa: E402
    configurar_logging_seguridad,
    crear_token_acceso_archivo,
    decrypt_bytes,
    encrypt_bytes,
)


class DummyRequest:
    def __init__(self, path_params=None, cookies=None, headers=None, method="GET", query_params=None):
        self.path_params = path_params or {}
        self.cookies = cookies or {}
        self.headers = headers or {}
        self.method = method
        self.query_params = query_params or {}
        self.url = "http://testserver/"


class TestSecurityHardening(unittest.TestCase):
    def test_servir_pdf_publico_rechaza_acceso_publico(self):
        ruta_dir = ROOT / "almacen_privado" / "documentos"
        ruta_dir.mkdir(parents=True, exist_ok=True)
        ruta_archivo = ruta_dir / "test_security.pdf"
        ruta_archivo.write_bytes(b"%PDF-1.4")
        try:
            request = DummyRequest(
                path_params={"categoria": "documentos", "archivo": "test_security.pdf"},
                cookies={},
                headers={},
            )
            response = app_module.servir_pdf_publico(request)
            self.assertEqual(response.status_code, 403)
        finally:
            if ruta_archivo.exists():
                ruta_archivo.unlink()

    def test_cookie_de_sesion_usa_politica_lax_en_localhost(self):
        estado = object.__new__(EstadoAutenticacion)
        cookie = EstadoAutenticacion._crear_cookie_sesion(estado, "abc123", 60)
        self.assertEqual(cookie.same_site, "lax")
        self.assertTrue(getattr(cookie, "http_only", False))

    def test_cookie_de_sesion_no_requiere_secure_en_localhost(self):
        estado = object.__new__(EstadoAutenticacion)
        cookie = EstadoAutenticacion._crear_cookie_sesion(estado, "abc123", 60)
        self.assertFalse(cookie.secure)

    def test_ttl_y_cookie_max_age_son_compatibles_con_sesion_larga(self):
        self.assertGreaterEqual(COOKIE_MAX_AGE_SECONDS, int(SESSION_TTL_HOURS * 3600))

    def test_servir_archivo_privado_acepta_token_de_acceso_firmado(self):
        ruta_dir = ROOT / "almacen_privado" / "documentos"
        ruta_dir.mkdir(parents=True, exist_ok=True)
        ruta_archivo = ruta_dir / "query_param.pdf"
        ruta_archivo.write_bytes(encrypt_bytes(b"%PDF-1.4\nsecret"))
        try:
            token = crear_token_acceso_archivo("documentos/query_param.pdf", usuario_id=7)
            request = DummyRequest(
                path_params={"categoria": "documentos", "archivo": "query_param.pdf"},
                cookies={},
                headers={},
                query_params={"token": token},
            )
            with patch.object(app_module, "verificar_token_acceso", return_value=False):
                response = app_module.servir_archivo_privado(request)
            self.assertEqual(response.status_code, 200)
            self.assertIn(b"%PDF", response.body)
        finally:
            if ruta_archivo.exists():
                ruta_archivo.unlink()

    def test_cifrado_pdf_round_trip(self):
        datos = b"%PDF-1.4\nsecret"
        texto_cifrado = encrypt_bytes(datos, key=b"0123456789abcdef0123456789abcdef")
        self.assertNotEqual(texto_cifrado, datos)
        self.assertEqual(decrypt_bytes(texto_cifrado, key=b"0123456789abcdef0123456789abcdef"), datos)

    def test_transaccion_rolls_back_en_error(self):
        class FakeConnection:
            def __init__(self):
                self.commited = 0
                self.rolled_back = 0
                self.started = 0

            def begin(self):
                self.started += 1

            def commit(self):
                self.commited += 1

            def rollback(self):
                self.rolled_back += 1

        fake_conn = FakeConnection()
        proxy = ConnectionProxy(fake_conn)
        with self.assertRaises(RuntimeError):
            with proxy.transaction():
                raise RuntimeError("boom")
        self.assertEqual(fake_conn.started, 1)
        self.assertEqual(fake_conn.rolled_back, 1)
        self.assertEqual(fake_conn.commited, 0)

    def test_logging_seguridad_escribe_en_archivo(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as handle:
            path = handle.name
        try:
            logger = configurar_logging_seguridad(path)
            logger.warning("acceso denegado para ruta /secret")
            logger.handlers[0].flush()
            with open(path, "r", encoding="utf-8") as fh:
                contenido = fh.read()
            self.assertIn("acceso denegado", contenido)
        finally:
            Path(path).unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
