import asyncio
import importlib
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["PYTEST_CURRENT_TEST"] = "1"

estado_autenticacion = importlib.import_module(
    "sistema_gestion_trabajo_grado.estado.estado_autenticacion"
)
estado_estudiante = importlib.import_module(
    "sistema_gestion_trabajo_grado.estado.estado_estudiante"
)
EncriptadorContrasena = estado_autenticacion.EncriptadorContrasena
EstadoAutenticacion = estado_autenticacion.EstadoAutenticacion
EstadoEstudiante = estado_estudiante.EstadoEstudiante
Usuario = estado_autenticacion.Usuario


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

        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_autenticacion.obtener_conexion",
            return_value=None,
        ):
            with patch(
                "sistema_gestion_trabajo_grado.estado.estado_autenticacion.rx.toast.error",
                return_value="error_conn",
            ):
                result = estado.iniciar_sesion()

        self.assertEqual(result, "error_conn")
        self.assertEqual(estado.intentos_fallidos, 0)

    def test_iniciar_sesion_credenciales_invalidas_incrementa_intentos(self):
        estado = EstadoAutenticacion()
        estado.entrada_usuario = "usuario@test.com"
        estado.entrada_contrasena = "wrongpass"

        cursor = FakeCursor(
            responses=[
                (
                    1,
                    "123456",
                    "Juan",
                    "Perez",
                    "usuario@test.com",
                    "hash",
                    True,
                    "Admin",
                )
            ]
        )
        conn = FakeConn(cursor)

        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_autenticacion.obtener_conexion",
            return_value=conn,
        ):
            with patch.object(EncriptadorContrasena, "verificar", return_value=False):
                with patch(
                    "sistema_gestion_trabajo_grado.estado.estado_autenticacion.rx.toast.error",
                    return_value="error_invalid",
                ):
                    result = estado.iniciar_sesion()

        self.assertEqual(result, "error_invalid")
        self.assertEqual(estado.intentos_fallidos, 1)
        self.assertTrue(conn.closed)

    def test_iniciar_sesion_usuario_inactivo(self):
        estado = EstadoAutenticacion()
        estado.entrada_usuario = "usuario@test.com"
        estado.entrada_contrasena = "secret"

        cursor = FakeCursor(
            responses=[
                (
                    1,
                    "123456",
                    "Juan",
                    "Perez",
                    "usuario@test.com",
                    "hash",
                    False,
                    "Admin",
                )
            ]
        )
        conn = FakeConn(cursor)

        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_autenticacion.obtener_conexion",
            return_value=conn,
        ):
            with patch.object(EncriptadorContrasena, "verificar", return_value=True):
                with patch(
                    "sistema_gestion_trabajo_grado.estado.estado_autenticacion.rx.toast.error",
                    return_value="error_inactive",
                ):
                    result = estado.iniciar_sesion()

        self.assertEqual(result, "error_inactive")
        self.assertEqual(estado.intentos_fallidos, 0)
        self.assertTrue(conn.closed)

    def test_iniciar_sesion_exitoso_crea_usuario_y_sesion(self):
        estado = EstadoAutenticacion()
        estado.entrada_usuario = "usuario@test.com"
        estado.entrada_contrasena = "secret"

        cursor = FakeCursor(
            responses=[
                (
                    1,
                    "123456",
                    "Juan",
                    "Perez",
                    "usuario@test.com",
                    "hash",
                    True,
                    "Admin",
                )
            ]
        )
        conn = FakeConn(cursor)

        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_autenticacion.obtener_conexion",
            return_value=conn,
        ):
            with patch.object(EncriptadorContrasena, "verificar", return_value=True):
                with patch(
                    "sistema_gestion_trabajo_grado.estado.estado_autenticacion.secrets.token_urlsafe",
                    return_value="fixed-token",
                ):
                    with patch(
                        "sistema_gestion_trabajo_grado.estado.estado_autenticacion.rx.redirect",
                        return_value="redirect_home",
                    ):
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

        cursor = FakeCursor(
            responses=[
                (
                    1,
                    "123456",
                    "Juan",
                    "Perez",
                    "usuario@test.com",
                    "hash",
                    True,
                    "Admin",
                )
            ]
        )
        conn = FakeConn(cursor)

        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_autenticacion.obtener_conexion",
            return_value=conn,
        ):
            with patch.object(EncriptadorContrasena, "verificar", return_value=False):
                with patch(
                    "sistema_gestion_trabajo_grado.estado.estado_autenticacion.rx.toast.error",
                    return_value="error_invalid",
                ):
                    for _ in range(4):
                        estado.iniciar_sesion()
                    resultado = estado.iniciar_sesion()

        self.assertEqual(resultado, "error_invalid")
        self.assertTrue(estado.bloqueado_hasta)
        self.assertGreaterEqual(estado.intentos_fallidos, 5)

    def test_guardar_estudiante_crea_cuenta_acceso_automaticamente(self):
        estado = EstadoEstudiante()
        estado.cedula = "12345678"
        estado.nombre = "Ana"
        estado.apellido = "Pérez"
        estado.correo = "ana@example.com"
        estado.carrera = "Ingeniería"
        estado.telefono_personal = "04141234567"
        estado.periodo_inicio = "2024-01-01"
        estado.periodo_cierre = "2024-06-01"
        estado.haciendo_trabajo_de_grado = False
        estado.nombre_empresa = ""
        estado.direccion_empresa = ""
        estado.tutor_empresa = ""
        estado.correo_empresa = ""
        estado.telefono_empresa = ""
        estado.tutores_mapeo = []
        estado.tutores_disponibles = []

        cursor = FakeCursor(responses=[None, None, (1,), (42,), None, None])
        conn = FakeConn(cursor)

        async def run_save():
            with patch(
                "sistema_gestion_trabajo_grado.estado.estado_estudiante.obtener_conexion",
                return_value=conn,
            ):
                with patch(
                    "sistema_gestion_trabajo_grado.estado.estado_estudiante.rx.toast.success",
                    return_value="toast_ok",
                ):
                    return await estado.guardar_estudiante()

        resultado = asyncio.run(run_save())

        self.assertEqual(resultado, "toast_ok")
        self.assertTrue(
            any("INSERT INTO usuario" in query for query, _ in cursor.executed)
        )
        self.assertTrue(conn.committed)

    def test_cerrar_sesion_limpia_usuario_y_actualiza_bd(self):
        estado = EstadoAutenticacion()
        estado.usuario = Usuario(id=1, correo="usuario@test.com", token_sesion="abc123")

        cursor = FakeCursor(responses=[])
        conn = FakeConn(cursor)

        async def run_close():
            with patch(
                "sistema_gestion_trabajo_grado.estado.estado_autenticacion.obtener_conexion",
                return_value=conn,
            ):
                with patch(
                    "sistema_gestion_trabajo_grado.estado.estado_autenticacion.rx.redirect",
                    return_value="redirect_login",
                ):
                    return await estado.cerrar_sesion()

        resultado = asyncio.run(run_close())

        self.assertEqual(resultado, "redirect_login")
        self.assertIsNone(estado.usuario)
        self.assertTrue(conn.closed)


if __name__ == "__main__":
    unittest.main()
