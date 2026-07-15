import asyncio
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

os.environ["PYTEST_CURRENT_TEST"] = "1"

from sistema_gestion_trabajo_grado.estado.estado_mantenimiento import (  # noqa: E402
    EstadoMantenimiento,
)


class FakeCursor:
    def __init__(self, fetchone_responses=None, fetchall_responses=None):
        self.fetchone_responses = fetchone_responses or []
        self.fetchall_responses = fetchall_responses or []
        self.executed = []

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        return self.fetchone_responses.pop(0) if self.fetchone_responses else (False,)

    def fetchall(self):
        return self.fetchall_responses.pop(0) if self.fetchall_responses else []

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


class FakeAuthState:
    def __init__(self, usuario_id=1, rol_usuario="administrador", cedula="12345678"):
        self.usuario = type("U", (), {"id": usuario_id, "cedula": cedula})
        self.rol_usuario = rol_usuario


class TestEstadoMantenimiento(unittest.TestCase):

    def test_abrir_cerrar_confirmacion_rol(self):
        estado = EstadoMantenimiento()
        estado.abrir_confirmacion_rol(8)
        self.assertTrue(estado.modal_confirmar_rol_abierto)
        self.assertEqual(estado.id_rol_eliminar, 8)
        self.assertEqual(estado.password_confirmacion, "")

        estado.cerrar_confirmacion_rol()
        self.assertFalse(estado.modal_confirmar_rol_abierto)

    def test_eliminar_rol_con_usuarios_asignados_devuelve_error(self):
        estado = EstadoMantenimiento()
        conn = FakeConn(FakeCursor(fetchone_responses=[(True,)]))
        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_mantenimiento.obtener_conexion",
            return_value=conn,
        ):
            with patch(
                "sistema_gestion_trabajo_grado.estado.estado_mantenimiento.rx.toast.error",
                return_value="error_has_users",
            ):
                resultado = estado.eliminar_rol(5)
        self.assertEqual(resultado, "error_has_users")
        self.assertTrue(conn.committed)

    def test_eliminar_rol_sin_usuarios_elimina_rol(self):
        estado = EstadoMantenimiento()
        conn = FakeConn(FakeCursor(fetchone_responses=[(False,)]))
        with patch(
            "sistema_gestion_trabajo_grado.estado.estado_mantenimiento.obtener_conexion",
            return_value=conn,
        ):
            with patch.object(EstadoMantenimiento, "cargar_datos", return_value=None):
                resultado = estado.eliminar_rol(5)
        self.assertIsNone(resultado)
        self.assertTrue(conn.committed)

    def test_confirmar_eliminar_rol_sin_sesion(self):
        estado = EstadoMantenimiento()

        async def fake_get_state(_):
            return type("Auth", (), {"usuario": None})

        with patch.object(EstadoMantenimiento, "get_state", side_effect=fake_get_state):
            with patch(
                "sistema_gestion_trabajo_grado.estado.estado_mantenimiento.rx.redirect",
                return_value="redirect:/login",
            ):
                resultado = asyncio.run(estado.confirmar_eliminar_rol())
        self.assertEqual(resultado, "redirect:/login")

    def test_confirmar_eliminar_rol_con_contrasena_incorrecta(self):
        estado = EstadoMantenimiento()
        estado.password_confirmacion = "bad"
        estado.id_rol_eliminar = 2
        fake_auth = FakeAuthState(usuario_id=1)

        async def fake_get_state(_):
            return fake_auth

        with patch.object(
            EstadoMantenimiento, "get_state", new=AsyncMock(return_value=fake_auth)
        ):
            conn = FakeConn(FakeCursor(fetchone_responses=[("hash",)]))
            with patch(
                "sistema_gestion_trabajo_grado.estado.estado_mantenimiento.obtener_conexion",
                return_value=conn,
            ):
                with patch(
                    "sistema_gestion_trabajo_grado.estado.estado_autenticacion.EncriptadorContrasena.verificar",
                    return_value=False,
                ):
                    with patch(
                        "sistema_gestion_trabajo_grado.estado.estado_mantenimiento.rx.toast.error",
                        return_value="error_bad_password",
                    ):
                        resultado = asyncio.run(estado.confirmar_eliminar_rol())
        self.assertEqual(resultado, "error_bad_password")

    def test_confirmar_eliminar_rol_exitoso(self):
        estado = EstadoMantenimiento()
        estado.password_confirmacion = "good"
        estado.id_rol_eliminar = 2
        fake_auth = FakeAuthState(usuario_id=1)

        async def fake_get_state(_):
            return fake_auth

        with patch.object(
            EstadoMantenimiento, "get_state", new=AsyncMock(return_value=fake_auth)
        ):
            conn = FakeConn(FakeCursor(fetchone_responses=[("hash",)]))
            with patch(
                "sistema_gestion_trabajo_grado.estado.estado_mantenimiento.obtener_conexion",
                return_value=conn,
            ):
                with patch(
                    "sistema_gestion_trabajo_grado.estado.estado_autenticacion.EncriptadorContrasena.verificar",
                    return_value=True,
                ):
                    with patch.object(
                        EstadoMantenimiento, "eliminar_rol", return_value=None
                    ):
                        with patch(
                            "sistema_gestion_trabajo_grado.estado.estado_mantenimiento.rx.toast.success",
                            return_value="success",
                        ):
                            resultado = asyncio.run(estado.confirmar_eliminar_rol())
        self.assertEqual(resultado, "success")
        self.assertFalse(estado.modal_confirmar_rol_abierto)


if __name__ == "__main__":
    unittest.main()
