import sys
import unittest
import asyncio
import os
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["PYTEST_CURRENT_TEST"] = "1"

from sistema_tesis.estado.estado_autenticacion import EstadoAutenticacion, EncriptadorContrasena, Usuario


class FakeCursor:
    def __init__(self, responses=None):
        self.responses = list(responses or [])
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        return self.responses.pop(0) if self.responses else None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class FakeConn:
    def __init__(self, cursor):
        self.cursor_obj = cursor
        self.committed = False
        self.closed = False

    def cursor(self):
        return self.cursor_obj

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.commit()
        return False

    def commit(self):
        self.committed = True

    def close(self):
        self.closed = True


class TestEstadoAutenticacionExtended(unittest.TestCase):

    def test_encriptador_contrasena_rechaza_muy_larga(self):
        largo = "a" * 100
        with self.assertRaises(ValueError):
            EncriptadorContrasena.encriptar(largo)

    def test_iniciar_sesion_sin_conexion(self):
        estado = EstadoAutenticacion()
        estado.entrada_usuario = "user@example.com"
        estado.entrada_contrasena = "secret"

        with patch("sistema_tesis.estado.estado_autenticacion.obtener_conexion", return_value=None):
            with patch("sistema_tesis.estado.estado_autenticacion.rx.toast.error", return_value="error_conn"):
                result = estado.iniciar_sesion()

        self.assertEqual(result, "error_conn")
        self.assertEqual(estado.intentos_fallidos, 0)

    def test_iniciar_sesion_credenciales_invalidas_incrementa_intentos(self):
        estado = EstadoAutenticacion()
        estado.entrada_usuario = "usuario@test.com"
        estado.entrada_contrasena = "wrongpass"

        cursor = FakeCursor(responses=[(1, "123456", "Juan", "Perez", "usuario@test.com", "hash", True, "Admin")])
        conn = FakeConn(cursor)

        with patch("sistema_tesis.estado.estado_autenticacion.obtener_conexion", return_value=conn):
            with patch.object(EncriptadorContrasena, "verificar", return_value=False):
                with patch("sistema_tesis.estado.estado_autenticacion.rx.toast.error", return_value="error_invalid"):
                    result = estado.iniciar_sesion()

        self.assertEqual(result, "error_invalid")
        self.assertEqual(estado.intentos_fallidos, 1)
        self.assertTrue(conn.closed)

    def test_iniciar_sesion_usuario_inactivo(self):
        estado = EstadoAutenticacion()
        estado.entrada_usuario = "usuario@test.com"
        estado.entrada_contrasena = "secret"

        cursor = FakeCursor(responses=[(1, "123456", "Juan", "Perez", "usuario@test.com", "hash", False, "Admin")])
        conn = FakeConn(cursor)

        with patch("sistema_tesis.estado.estado_autenticacion.obtener_conexion", return_value=conn):
            with patch.object(EncriptadorContrasena, "verificar", return_value=True):
                with patch("sistema_tesis.estado.estado_autenticacion.rx.toast.error", return_value="error_inactive"):
                    result = estado.iniciar_sesion()

        self.assertEqual(result, "error_inactive")
        self.assertEqual(estado.intentos_fallidos, 0)
        self.assertTrue(conn.closed)

    def test_iniciar_sesion_exitoso_crea_usuario_y_sesion(self):
        estado = EstadoAutenticacion()
        estado.entrada_usuario = "usuario@test.com"
        estado.entrada_contrasena = "secret"

        cursor = FakeCursor(responses=[(1, "123456", "Juan", "Perez", "usuario@test.com", "hash", True, "Admin")])
        conn = FakeConn(cursor)

        with patch("sistema_tesis.estado.estado_autenticacion.obtener_conexion", return_value=conn):
            with patch.object(EncriptadorContrasena, "verificar", return_value=True):
                with patch("sistema_tesis.estado.estado_autenticacion.secrets.token_urlsafe", return_value="fixed-token"):
                    with patch("sistema_tesis.estado.estado_autenticacion.rx.redirect", return_value="redirect_home"):
                        result = estado.iniciar_sesion()

        self.assertEqual(result, "redirect_home")
        self.assertIsNotNone(estado.usuario)
        self.assertEqual(estado.usuario.token_sesion, "fixed-token")
        self.assertEqual(estado.usuario.correo, "usuario@test.com")
        self.assertEqual(estado.intentos_fallidos, 0)
        self.assertEqual(estado.bloqueado_hasta, "")
        self.assertTrue(conn.committed)

    def test_iniciar_sesion_bloquea_despues_de_cinco_intentos(self):
        estado = EstadoAutenticacion()
        estado.entrada_usuario = "usuario@test.com"
        estado.entrada_contrasena = "wrong"

        cursor = FakeCursor(responses=[(1, "123456", "Juan", "Perez", "usuario@test.com", "hash", True, "Admin")])
        conn = FakeConn(cursor)

        with patch("sistema_tesis.estado.estado_autenticacion.obtener_conexion", return_value=conn):
            with patch.object(EncriptadorContrasena, "verificar", return_value=False):
                with patch("sistema_tesis.estado.estado_autenticacion.rx.toast.error", return_value="error_invalid"):
                    for _ in range(4):
                        estado.iniciar_sesion()
                    resultado = estado.iniciar_sesion()

        self.assertEqual(resultado, "error_invalid")
        self.assertTrue(estado.bloqueado_hasta)
        self.assertGreaterEqual(estado.intentos_fallidos, 5)

    def test_cerrar_sesion_limpia_usuario_y_actualiza_bd(self):
        estado = EstadoAutenticacion()
        estado.usuario = Usuario(id=1, correo="usuario@test.com", token_sesion="abc123")

        cursor = FakeCursor(responses=[])
        conn = FakeConn(cursor)

        async def run_close():
            with patch("sistema_tesis.estado.estado_autenticacion.obtener_conexion", return_value=conn):
                with patch("sistema_tesis.estado.estado_autenticacion.rx.redirect", return_value="redirect_login"):
                    return await estado.cerrar_sesion()

        resultado = asyncio.run(run_close())

        self.assertEqual(resultado, "redirect_login")
        self.assertIsNone(estado.usuario)
        self.assertTrue(conn.closed)


if __name__ == "__main__":
    unittest.main()
